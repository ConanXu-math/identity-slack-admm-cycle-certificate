"""Numerically test dual-step relaxation on the strict 66-cycle witness.

Evidence status: numerical_screen.

The quadratic problem and initial state are rebuilt from the exact rational
verifier.  Only the multiplier update is changed:

    lambda_next = lambda - tau * (x_next + y_next + z_next - rhs).

For tau < 1 the identity ``lambda = q_-`` no longer holds, so every trajectory
is generated in the full state ``(y, z, lambda)``.  No reduced signed-state
formula from the tau=1 certificate is reused.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
EXACT_VERIFIER = (
    ROOT / "deliverables" / "strict_66_cycle_minimal" / "Python" / "verify_cycle.py"
)
DEFAULT_OUTPUT = ROOT / "outputs" / "tau_multiplier_relaxation_2026-07-15"
DEFAULT_TAUS = (
    1.0,
    0.9999,
    0.999,
    0.995,
    0.99,
    0.98,
    0.95,
    0.9,
    0.8,
    0.7,
    0.6,
    0.5,
    0.4,
    0.3,
    0.2,
    0.1,
    0.05,
    0.02,
    0.01,
)


@dataclass(frozen=True)
class Witness:
    M: np.ndarray
    N: np.ndarray
    rhs: np.ndarray
    initial: np.ndarray
    kkt_state: np.ndarray


def load_exact_verifier():
    """Load the checked-in rational verifier without making it a package dependency."""
    spec = importlib.util.spec_from_file_location("strict_66_cycle_exact", EXACT_VERIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load exact verifier: {EXACT_VERIFIER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_witness() -> Witness:
    """Rebuild the QP and the tau=1 periodic initial state from exact rationals."""
    verifier = load_exact_verifier()
    problem = verifier.build_problem()
    initial = verifier.construct_initial(problem)

    def array(matrix) -> np.ndarray:
        return np.asarray(matrix.evalf(), dtype=float).reshape(-1)

    return Witness(
        M=np.asarray(problem["M"].evalf(), dtype=float),
        N=np.asarray(problem["N"].evalf(), dtype=float),
        rhs=array(problem["rhs"]),
        initial=array(initial),
        kkt_state=np.concatenate(
            [
                array(problem["y_star"]),
                array(problem["z_star"]),
                array(problem["lambda_star"]),
            ]
        ),
    )


def relaxed_step(
    state: np.ndarray, witness: Witness, tau: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Apply one original ADMM sweep followed by a tau-scaled dual update."""
    y = state[:2]
    z = state[2:4]
    lam = state[4:6]
    x_next = witness.M @ (lam - y - z + witness.rhs)
    y_next = witness.N @ (lam - x_next - z + witness.rhs)
    q_next = witness.rhs - x_next - y_next + lam
    z_next = np.maximum(q_next, 0.0)
    residual = x_next + y_next + z_next - witness.rhs
    lambda_next = lam - tau * residual
    next_state = np.concatenate([y_next, z_next, lambda_next])
    return next_state, x_next, q_next, residual


def selected_relaxed_step(
    state: np.ndarray, witness: Witness, tau: float, selector: np.ndarray
) -> np.ndarray:
    """Apply the same relaxed update while forcing one projection branch."""
    y = state[:2]
    z = state[2:4]
    lam = state[4:6]
    x_next = witness.M @ (lam - y - z + witness.rhs)
    y_next = witness.N @ (lam - x_next - z + witness.rhs)
    q_next = witness.rhs - x_next - y_next + lam
    z_next = selector @ q_next
    residual = x_next + y_next + z_next - witness.rhs
    lambda_next = lam - tau * residual
    return np.concatenate([y_next, z_next, lambda_next])


def local_branch_matrix(witness: Witness, tau: float) -> np.ndarray:
    """Return the six-dimensional linear part of the strict KKT branch 01."""
    selector = np.diag([0.0, 1.0])
    zero = np.zeros(6)
    offset = selected_relaxed_step(zero, witness, tau, selector)
    columns = [
        selected_relaxed_step(np.eye(6)[column], witness, tau, selector) - offset
        for column in range(6)
    ]
    return np.column_stack(columns)


def local_spectral_radius(witness: Witness, tau: float) -> float:
    """Spectral radius governing local behavior near the strict KKT point."""
    eigenvalues = np.linalg.eigvals(local_branch_matrix(witness, tau))
    return float(np.max(np.abs(eigenvalues)))


def local_stability_threshold(
    witness: Witness, lower: float = 0.9, upper: float = 1.0
) -> float:
    """Bisect the observed rho=1 crossing on the KKT branch."""
    if local_spectral_radius(witness, lower) >= 1.0:
        raise ValueError("lower endpoint is not locally stable")
    if local_spectral_radius(witness, upper) <= 1.0:
        raise ValueError("upper endpoint is not locally unstable")
    for _ in range(80):
        midpoint = 0.5 * (lower + upper)
        if local_spectral_radius(witness, midpoint) < 1.0:
            lower = midpoint
        else:
            upper = midpoint
    return 0.5 * (lower + upper)


def _period_66_diagnostic(history: deque[np.ndarray]) -> tuple[float, float]:
    """Return the worst 66-lag error and within-cycle oscillation on the tail."""
    if len(history) < 133:
        return float("inf"), 0.0
    states = list(history)
    lag_errors = [
        np.linalg.norm(states[-1 - j] - states[-67 - j]) for j in range(66)
    ]
    tail = np.asarray(states[-66:])
    center = np.mean(tail, axis=0)
    oscillation = float(np.max(np.linalg.norm(tail - center, axis=1)))
    return float(max(lag_errors)), oscillation


def simulate(
    witness: Witness,
    tau: float,
    max_steps: int,
    tolerance: float,
    tail_window: int,
    sample_every: int,
) -> tuple[dict[str, object], list[dict[str, float]]]:
    """Run one tau value and classify only behavior resolved within the budget."""
    state = witness.initial.copy()
    history: deque[np.ndarray] = deque([state.copy()], maxlen=max(133, tail_window + 1))
    recent_metrics: deque[tuple[float, float, float]] = deque(maxlen=tail_window)
    trace: list[dict[str, float]] = []
    max_state_norm = float(np.linalg.norm(state))
    classification = "not_resolved_within_budget"
    period_error = float("inf")
    oscillation = 0.0

    for iteration in range(1, max_steps + 1):
        next_state, _, _, residual = relaxed_step(state, witness, tau)
        state_step = float(np.linalg.norm(next_state - state))
        residual_norm = float(np.linalg.norm(residual))
        kkt_distance = float(np.linalg.norm(next_state - witness.kkt_state))
        state = next_state
        history.append(state.copy())
        recent_metrics.append((kkt_distance, residual_norm, state_step))
        max_state_norm = max(max_state_norm, float(np.linalg.norm(state)))

        if iteration == 1 or iteration % sample_every == 0:
            trace.append(
                {
                    "iteration": float(iteration),
                    "kkt_distance": kkt_distance,
                    "residual_norm": residual_norm,
                    "state_step": state_step,
                }
            )

        if not np.all(np.isfinite(state)) or max_state_norm > 1.0e12:
            classification = "diverged_within_budget"
            break

        if len(recent_metrics) == tail_window:
            tail_maxima = np.max(np.asarray(recent_metrics), axis=0)
            if bool(np.all(tail_maxima < tolerance)):
                classification = "converged_to_kkt_within_budget"
                break

        if iteration >= 132 and iteration % 66 == 0:
            period_error, oscillation = _period_66_diagnostic(history)
            if (
                period_error < tolerance
                and oscillation > 100.0 * tolerance
                and kkt_distance > 100.0 * tolerance
            ):
                classification = "period_66_detected"
                break

    if not trace or trace[-1]["iteration"] != float(iteration):
        trace.append(
            {
                "iteration": float(iteration),
                "kkt_distance": float(np.linalg.norm(state - witness.kkt_state)),
                "residual_norm": residual_norm,
                "state_step": state_step,
            }
        )

    if not np.isfinite(period_error):
        period_error, oscillation = _period_66_diagnostic(history)

    result = {
        "tau": tau,
        "local_01_spectral_radius": local_spectral_radius(witness, tau),
        "classification": classification,
        "iterations": iteration,
        "final_kkt_distance": float(np.linalg.norm(state - witness.kkt_state)),
        "final_residual_norm": residual_norm,
        "final_state_step": state_step,
        "max_state_norm": max_state_norm,
        "tail_period_66_error": period_error,
        "tail_66_oscillation": oscillation,
    }
    return result, trace


def write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    rows = list(rows)
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            rendered = {}
            for key, value in row.items():
                if isinstance(value, float):
                    rendered[key] = f"{value:.16f}"
                else:
                    rendered[key] = value
            writer.writerow(rendered)


def write_plot(path: Path, traces: dict[float, list[dict[str, float]]]) -> None:
    """Plot representative KKT-distance histories as an SVG."""
    import matplotlib.pyplot as plt

    representative = (1.0, 0.94, 0.935, 0.93, 0.92, 0.9, 0.8, 0.5, 0.1)
    figure, axis = plt.subplots(figsize=(7.2, 4.5))
    for tau in representative:
        if tau not in traces:
            continue
        iterations = [row["iteration"] for row in traces[tau]]
        distances = [max(row["kkt_distance"], 1.0e-16) for row in traces[tau]]
        axis.semilogy(iterations, distances, label=fr"$\tau={tau:g}$")
    axis.set_xlabel("iteration")
    axis.set_ylabel("distance to the unique KKT state")
    axis.set_title("Relaxed multiplier update on the 66-cycle witness")
    axis.grid(True, which="both", alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(path, format="svg")
    plt.close(figure)


def write_spectral_radius_plot(
    path: Path, witness: Witness, threshold: float
) -> None:
    """Plot the local KKT-branch spectral radius and its unit-circle crossing."""
    import matplotlib.pyplot as plt

    taus = np.linspace(0.85, 1.0, 301)
    radius_gaps = [
        local_spectral_radius(witness, float(tau)) - 1.0 for tau in taus
    ]
    figure, axis = plt.subplots(figsize=(7.2, 4.2))
    axis.plot(taus, radius_gaps, color="#0b3a82", linewidth=2)
    axis.axhline(0.0, color="#a32626", linestyle="--", linewidth=1.2)
    axis.axvline(threshold, color="#126b35", linestyle=":", linewidth=1.4)
    axis.annotate(
        fr"$\tau_c\approx {threshold:.10f}$",
        xy=(threshold, 0.0),
        xytext=(0.895, 0.00012),
        arrowprops={"arrowstyle": "->", "color": "#126b35"},
    )
    axis.set_xlabel(r"multiplier step $\tau$")
    axis.set_ylabel(r"local stability gap $\rho(T_{01}(\tau))-1$")
    axis.set_title("Local stability of the unique KKT point")
    axis.grid(True, alpha=0.25)
    figure.tight_layout()
    figure.savefig(path, format="svg")
    plt.close(figure)


def parse_taus(text: str | None) -> tuple[float, ...]:
    if text is None:
        return DEFAULT_TAUS
    values = tuple(float(item.strip()) for item in text.split(",") if item.strip())
    if not values or any(not (0.0 < value <= 1.0) for value in values):
        raise ValueError("all tau values must lie in (0, 1]")
    return values


def run(
    output_dir: Path,
    taus: tuple[float, ...],
    max_steps: int,
    tolerance: float,
    tail_window: int,
    sample_every: int,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    results_dir = output_dir / "results"
    figures_dir = output_dir / "figures"
    results_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)

    witness = build_witness()
    threshold = local_stability_threshold(witness)
    results: list[dict[str, object]] = []
    traces: dict[float, list[dict[str, float]]] = {}
    for tau in taus:
        result, trace = simulate(
            witness=witness,
            tau=tau,
            max_steps=max_steps,
            tolerance=tolerance,
            tail_window=tail_window,
            sample_every=sample_every,
        )
        results.append(result)
        traces[tau] = trace
        print(
            f"tau={tau:.4f}  {result['classification']}  "
            f"steps={result['iterations']}  "
            f"kkt={result['final_kkt_distance']:.6g}  "
            f"residual={result['final_residual_norm']:.6g}"
        )

    write_csv(results_dir / "tau_sweep.csv", results)
    for tau, trace in traces.items():
        safe_tau = f"{tau:.6f}".replace(".", "_")
        write_csv(results_dir / f"trace_tau_{safe_tau}.csv", trace)
    write_plot(figures_dir / "tau_convergence.svg", traces)
    write_spectral_radius_plot(
        figures_dir / "local_01_spectral_radius.svg", witness, threshold
    )

    summary = {
        "evidence_status": "numerical_screen",
        "problem": "same exact rational QP and same tau=1 periodic initial state",
        "changed_update": "lambda_next = lambda - tau * primal_residual",
        "max_steps": max_steps,
        "tolerance": tolerance,
        "tail_window": tail_window,
        "local_kkt_branch": "01",
        "local_stability_threshold_tau": threshold,
        "local_stability_interpretation": (
            "rho(T_01(tau)) < 1 below the threshold and > 1 above it"
        ),
        "results": results,
        "limitations": [
            "finite trajectories do not prove global convergence",
            "classification applies only to the fixed witness and fixed initial state",
            "tau < 1 uses the full state because lambda = q_- no longer holds",
        ],
    }
    (results_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--taus", type=str)
    parser.add_argument("--max-steps", type=int, default=200_000)
    parser.add_argument("--tolerance", type=float, default=1.0e-10)
    parser.add_argument("--tail-window", type=int, default=100)
    parser.add_argument("--sample-every", type=int, default=10)
    args = parser.parse_args()
    if args.max_steps < 132:
        parser.error("--max-steps must be at least 132")
    if args.tail_window < 2:
        parser.error("--tail-window must be at least 2")
    if args.sample_every < 1:
        parser.error("--sample-every must be positive")
    run(
        output_dir=args.output_dir,
        taus=parse_taus(args.taus),
        max_steps=args.max_steps,
        tolerance=args.tolerance,
        tail_window=args.tail_window,
        sample_every=args.sample_every,
    )


if __name__ == "__main__":
    main()
