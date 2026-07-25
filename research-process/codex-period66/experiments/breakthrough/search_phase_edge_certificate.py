#!/usr/bin/env python3
"""Numerically screen a phase-dependent edge Lyapunov certificate.

This script builds a DNN/S-procedure relaxation for one fixed rational
two-dimensional slack-ADMM QP.  A successful solve is numerical screening
evidence only; it is not an exact positivity or convergence proof.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.slack_admm_core import AdmmState, SlackQpProblem  # noqa: E402
from src.admm_identity.edge_energy import (
    EdgeEnergyQuadraticForm,
    build_edge_energy_quadratic_form,
)  # noqa: E402


Mask = tuple[int, int]
Edge = tuple[Mask, Mask]


@dataclass(frozen=True)
class PhaseEdgeData:
    """Pure NumPy data for the four-phase, sixteen-edge SDP."""

    masks: tuple[Mask, ...]
    core: dict[Mask, np.ndarray]
    edges: dict[Edge, EdgeEnergyQuadraticForm]

    @property
    def matrix_size(self) -> int:
        return next(iter(self.core.values())).shape[0]


def obstruction_problem() -> tuple[SlackQpProblem, AdmmState]:
    """Return the fixed rational QP and its zero KKT point."""

    problem = SlackQpProblem(
        q1=3.0 * np.eye(2),
        q2=np.array([[7.0, 4.0], [4.0, 3.0]]),
        a=np.eye(2),
        bmat=np.eye(2),
        rhs=np.zeros(2),
        beta=1.0,
    )
    zero = np.zeros(2)
    return problem, AdmmState(x=zero.copy(), y=zero.copy(), z=zero.copy(), lam=zero.copy())


def all_masks() -> tuple[Mask, ...]:
    return tuple(tuple(bits) for bits in product((0, 1), repeat=2))  # type: ignore[return-value]


def build_phase_edge_data() -> PhaseEdgeData:
    """Build all phase cores and all 16 source-target edge forms."""

    problem, kkt = obstruction_problem()
    masks = all_masks()
    edges: dict[Edge, EdgeEnergyQuadraticForm] = {}
    core: dict[Mask, np.ndarray] = {}
    for source in masks:
        source_array = np.asarray(source, dtype=bool)
        for target in masks:
            form = build_edge_energy_quadratic_form(
                problem, kkt, source_array, np.asarray(target, dtype=bool)
            )
            edges[(source, target)] = form
            core.setdefault(source, form.source_energy.copy())
    return PhaseEdgeData(masks=masks, core=core, edges=edges)


def _symmetric_min_eigenvalue(matrix: np.ndarray) -> float:
    return float(np.linalg.eigvalsh(0.5 * (matrix + matrix.T)).min())


def audit_candidate(
    data: PhaseEdgeData,
    epsilon: float,
    phase_matrices: Mapping[Mask, np.ndarray],
    multipliers: Mapping[Edge, np.ndarray],
    trace_budget: float,
) -> dict[str, Any]:
    """Audit a numerical candidate without importing or requiring cvxpy."""

    size = data.matrix_size
    phase_audits: dict[str, Any] = {}
    edge_audits: dict[str, Any] = {}
    correction_trace = 0.0
    for mask in data.masks:
        matrix = np.asarray(phase_matrices[mask], dtype=float)
        if matrix.shape != (size, size):
            raise ValueError(f"H[{mask}] has shape {matrix.shape}, expected {(size, size)}")
        correction = matrix - data.core[mask]
        correction_trace += float(np.trace(correction))
        phase_audits[_mask_key(mask)] = {
            "symmetry_residual": float(np.linalg.norm(matrix - matrix.T, ord=np.inf)),
            "homogeneous_last_row_residual": float(
                max(np.linalg.norm(correction[-1, :], ord=np.inf), np.linalg.norm(correction[:, -1], ord=np.inf))
            ),
            "min_core_dominance_eigenvalue": _symmetric_min_eigenvalue(correction),
        }

    for edge, form in data.edges.items():
        source, target = edge
        multiplier = np.asarray(multipliers[edge], dtype=float)
        rows = form.region_rows
        expected = (rows.shape[0], rows.shape[0])
        if multiplier.shape != expected:
            raise ValueError(f"Lambda[{edge}] has shape {multiplier.shape}, expected {expected}")
        residual = (
            phase_matrices[source]
            - form.transition_lift.T @ phase_matrices[target] @ form.transition_lift
            - epsilon * (form.dissipation_map.T @ form.dissipation_map)
            - rows.T @ multiplier @ rows
        )
        edge_audits[_edge_key(edge)] = {
            "min_residual_eigenvalue": _symmetric_min_eigenvalue(residual),
            "residual_symmetry": float(np.linalg.norm(residual - residual.T, ord=np.inf)),
            "multiplier_min_eigenvalue": _symmetric_min_eigenvalue(multiplier),
            "multiplier_min_entry": float(multiplier.min()),
            "multiplier_symmetry_residual": float(
                np.linalg.norm(multiplier - multiplier.T, ord=np.inf)
            ),
        }

    return {
        "epsilon": float(epsilon),
        "correction_trace": correction_trace,
        "trace_budget": float(trace_budget),
        "trace_budget_slack": float(trace_budget - correction_trace),
        "phases": phase_audits,
        "edges": edge_audits,
        "worst": {
            "min_core_dominance_eigenvalue": min(
                item["min_core_dominance_eigenvalue"] for item in phase_audits.values()
            ),
            "max_homogeneous_last_row_residual": max(
                item["homogeneous_last_row_residual"] for item in phase_audits.values()
            ),
            "min_edge_residual_eigenvalue": min(
                item["min_residual_eigenvalue"] for item in edge_audits.values()
            ),
            "min_multiplier_eigenvalue": min(
                item["multiplier_min_eigenvalue"] for item in edge_audits.values()
            ),
            "min_multiplier_entry": min(
                item["multiplier_min_entry"] for item in edge_audits.values()
            ),
        },
    }


def solve_phase_edge_sdp(
    data: PhaseEdgeData,
    *,
    solver: str | None = None,
    verbose: bool = False,
    trace_budget: float = 100.0,
) -> dict[str, Any]:
    """Solve the DNN relaxation, importing cvxpy only when requested."""

    try:
        import cvxpy as cp
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "cvxpy is required to solve the phase-edge SDP; install cvxpy or use "
            "build_phase_edge_data()/audit_candidate() for solver-free inspection"
        ) from exc
    if not np.isfinite(trace_budget) or trace_budget <= 0.0:
        raise ValueError("trace_budget must be finite and positive")

    size = data.matrix_size
    corrections = {mask: cp.Variable((size, size), symmetric=True) for mask in data.masks}
    phase = {mask: data.core[mask] + corrections[mask] for mask in data.masks}
    epsilon = cp.Variable(nonneg=True)
    multipliers: dict[Edge, Any] = {}
    constraints: list[Any] = []
    for correction in corrections.values():
        constraints.extend([correction >> 0, correction[-1, :] == 0, correction[:, -1] == 0])
    constraints.append(sum(cp.trace(item) for item in corrections.values()) <= trace_budget)

    for edge, form in data.edges.items():
        row_count = form.region_rows.shape[0]
        multiplier = cp.Variable((row_count, row_count), symmetric=True)
        multipliers[edge] = multiplier
        constraints.extend([multiplier >> 0, multiplier >= 0])
        source, target = edge
        residual = (
            phase[source]
            - form.transition_lift.T @ phase[target] @ form.transition_lift
            - epsilon * (form.dissipation_map.T @ form.dissipation_map)
            - form.region_rows.T @ multiplier @ form.region_rows
        )
        constraints.append(residual >> 0)

    problem = cp.Problem(cp.Maximize(epsilon), constraints)
    solve_kwargs: dict[str, Any] = {"verbose": verbose}
    if solver:
        solve_kwargs["solver"] = solver
    value = problem.solve(**solve_kwargs)
    status = str(problem.status)
    solved = status in {str(cp.OPTIMAL), str(cp.OPTIMAL_INACCURATE)}
    epsilon_value = float(epsilon.value) if epsilon.value is not None else float("nan")
    phase_values = {
        mask: np.asarray(phase[mask].value, dtype=float) for mask in data.masks
    } if solved else {}
    multiplier_values = {
        edge: np.asarray(variable.value, dtype=float) for edge, variable in multipliers.items()
    } if solved else {}
    audit = (
        audit_candidate(
            data, epsilon_value, phase_values, multiplier_values, trace_budget
        )
        if solved
        else None
    )
    return {
        "status": status,
        "objective": None if value is None or not np.isfinite(value) else float(value),
        "epsilon": None if not np.isfinite(epsilon_value) else epsilon_value,
        "H": {_mask_key(mask): matrix.tolist() for mask, matrix in phase_values.items()},
        "multipliers": {
            _edge_key(edge): matrix.tolist() for edge, matrix in multiplier_values.items()
        },
        "audit": audit,
    }


def _mask_key(mask: Mask) -> str:
    return "".join(str(bit) for bit in mask)


def _edge_key(edge: Edge) -> str:
    return f"{_mask_key(edge[0])}->{_mask_key(edge[1])}"


def build_report(
    result: Mapping[str, Any], solver: str | None, trace_budget: float
) -> dict[str, Any]:
    return {
        "status": result["status"],
        "evidence_kind": "numerical_screen",
        "claim_scope": (
            "Numerical DNN relaxation for one fixed two-dimensional rational QP; "
            "not an exact certificate, convergence proof, or counterexample."
        ),
        "model": {
            "masks": ["00", "01", "10", "11"],
            "edge_count": 16,
            "phase_condition": "H_b - core_b PSD; correction homogeneous last row/column zero",
            "trace_budget": trace_budget,
            "normalization": "sum_b trace(H_b - core_b) <= trace_budget",
            "multipliers": "doubly nonnegative (PSD and entrywise nonnegative)",
            "solver": solver,
        },
        **{key: result[key] for key in ("objective", "epsilon", "H", "multipliers", "audit")},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--solver", default=None)
    parser.add_argument("--trace-budget", type=float, default=100.0)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = build_phase_edge_data()
    result = solve_phase_edge_sdp(
        data,
        solver=args.solver,
        verbose=args.verbose,
        trace_budget=args.trace_budget,
    )
    report = build_report(result, args.solver, args.trace_budget)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
