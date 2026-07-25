from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import differential_evolution


DEFAULT_BASE_SEED = 20260714
DEFAULT_MU_BOUNDS = (0.85, 0.98)
DEFAULT_NU_BOUNDS = (0.995, 0.9999999)


def candidate_seed(
    zero_count: int,
    one_count: int,
    base_seed: int = DEFAULT_BASE_SEED,
) -> int:
    """Recover the deterministic seed used by the Stage 43-to-44 search."""
    return base_seed + 100 * zero_count + one_count


def evaluate_periodic_word(
    mu: float,
    nu: float,
    zero_count: int,
    one_count: int,
) -> dict[str, object] | None:
    """Evaluate the strict margin of ``(00)^a (01)^b`` in floating point.

    This function is a discovery screen.  It solves the affine period fixed-point
    equation for the prescribed word and then checks whether all branch signs
    are strict.  Proof-grade closure is delegated to the exact Stage 44 checker.
    """
    identity = np.eye(2)
    epsilon = 0.001
    first_direction = np.array([-1.0, 20.0])
    second_direction = np.array([-1.0, 10.0])
    first_projector = np.outer(first_direction, first_direction) / 401.0
    second_projector = np.outer(second_direction, second_direction) / 101.0
    m_matrix = epsilon * identity + (mu - epsilon) * first_projector
    n_matrix = epsilon * identity + (nu - epsilon) * second_projector

    rhs = np.array([0.0, 1.0])
    linear_term = np.array([-1.0, 0.0])
    recurrence_offset = (
        (identity - m_matrix) @ rhs
        + m_matrix @ linear_term
        - linear_term
    )
    affine_offset = np.concatenate(
        (
            n_matrix @ recurrence_offset,
            (identity - n_matrix) @ recurrence_offset + linear_term,
        )
    )

    branch_matrices: list[np.ndarray] = []
    for bit in (0, 1):
        selector = np.diag([0.0, float(bit)])
        sign = 2.0 * selector - identity
        branch_matrices.append(
            np.block(
                [
                    [
                        n_matrix @ m_matrix,
                        -n_matrix @ (identity - m_matrix) @ sign,
                    ],
                    [
                        (identity - n_matrix) @ m_matrix,
                        selector
                        - (identity - n_matrix)
                        @ (identity - m_matrix)
                        @ sign,
                    ],
                ]
            )
        )

    word = (0,) * zero_count + (1,) * one_count
    period_matrix = np.eye(4)
    period_offset = np.zeros(4)
    for bit in word:
        period_offset = branch_matrices[bit] @ period_offset + affine_offset
        period_matrix = branch_matrices[bit] @ period_matrix

    try:
        initial_state = np.linalg.solve(
            np.eye(4) - period_matrix,
            period_offset,
        )
    except np.linalg.LinAlgError:
        return None

    state = initial_state.copy()
    minimum_margin = float("inf")
    minimum_phase = -1
    minimum_coordinate = -1
    for phase, bit in enumerate(word):
        phase_margins = (-state[2], state[3] if bit else -state[3])
        for coordinate, value in enumerate(phase_margins):
            if value < minimum_margin:
                minimum_margin = float(value)
                minimum_phase = phase
                minimum_coordinate = coordinate
        state = branch_matrices[bit] @ state + affine_offset

    return {
        "mu": float(mu),
        "nu": float(nu),
        "zero_count": zero_count,
        "one_count": one_count,
        "word_run_length_encoding": [[0, zero_count], [1, one_count]],
        "minimum_margin": minimum_margin,
        "minimum_margin_phase": minimum_phase,
        "minimum_margin_coordinate": minimum_coordinate,
        "initial_state": initial_state.tolist(),
        "period_spectral_radius": float(
            np.max(np.abs(np.linalg.eigvals(period_matrix)))
        ),
        "floating_closure_error_inf": float(
            np.linalg.norm(state - initial_state, ord=np.inf)
        ),
    }


def optimize_word(
    zero_count: int,
    one_count: int,
    base_seed: int,
    maxiter: int,
    popsize: int,
) -> dict[str, object]:
    seed = candidate_seed(zero_count, one_count, base_seed)

    def objective(parameters: np.ndarray) -> float:
        evaluation = evaluate_periodic_word(
            float(parameters[0]),
            float(parameters[1]),
            zero_count,
            one_count,
        )
        return 1.0e6 if evaluation is None else -float(evaluation["minimum_margin"])

    result = differential_evolution(
        objective,
        [DEFAULT_MU_BOUNDS, DEFAULT_NU_BOUNDS],
        seed=seed,
        popsize=popsize,
        maxiter=maxiter,
        tol=1.0e-8,
        polish=True,
        workers=1,
    )
    evaluation = evaluate_periodic_word(
        float(result.x[0]),
        float(result.x[1]),
        zero_count,
        one_count,
    )
    assert evaluation is not None
    evaluation.update(
        {
            "seed": seed,
            "optimizer_success": bool(result.success),
            "optimizer_message": str(result.message),
            "optimizer_iterations": int(result.nit),
            "optimizer_evaluations": int(result.nfev),
        }
    )
    return evaluation


def run(
    base_seed: int = DEFAULT_BASE_SEED,
    maxiter: int = 35,
    popsize: int = 6,
    stop_margin: float = 1.0e-7,
) -> dict[str, object]:
    records: list[dict[str, object]] = []
    hit: dict[str, object] | None = None
    for zero_count in range(2, 7):
        for one_count in range(60, 67):
            record = optimize_word(
                zero_count,
                one_count,
                base_seed,
                maxiter,
                popsize,
            )
            records.append(record)
            if float(record["minimum_margin"]) > stop_margin:
                hit = record
                break
        if hit is not None:
            break

    return {
        "status": "numerical_screen_recovered_from_stage43_to_stage44_search",
        "stage43_mother_parameters": {
            "epsilon": 0.001,
            "mu": 0.9,
            "nu": 0.999,
            "first_direction": [-1, 20],
            "second_direction": [-1, 10],
        },
        "search_family": "(00)^zero_count (01)^one_count",
        "zero_count_range": [2, 6],
        "one_count_range": [60, 66],
        "mu_bounds": list(DEFAULT_MU_BOUNDS),
        "nu_bounds": list(DEFAULT_NU_BOUNDS),
        "base_seed": base_seed,
        "seed_formula": "base_seed + 100 * zero_count + one_count",
        "maxiter": maxiter,
        "popsize": popsize,
        "stop_margin": stop_margin,
        "software_versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "records": records,
        "hit": hit,
        "claim_boundary": [
            "This differential-evolution run is numerical discovery evidence only.",
            "A positive floating margin is not proof of exact closure or branch admissibility.",
            "The rounded parameters must be rebuilt and checked by the exact Stage 44 and Stage 45 certifiers.",
            "Failure to find a hit for a word is not a proof that the word is impossible.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-seed", type=int, default=DEFAULT_BASE_SEED)
    parser.add_argument("--maxiter", type=int, default=35)
    parser.add_argument("--popsize", type=int, default=6)
    parser.add_argument("--stop-margin", type=float, default=1.0e-7)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "outputs/breakthrough_attempts/"
            "stage43_to_stage44_discovery/search.json"
        ),
    )
    args = parser.parse_args()
    payload = run(
        base_seed=args.base_seed,
        maxiter=args.maxiter,
        popsize=args.popsize,
        stop_margin=args.stop_margin,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    hit = payload["hit"]
    print(
        json.dumps(
            {
                "hit": hit is not None,
                "word_run_length_encoding": None
                if hit is None
                else hit["word_run_length_encoding"],
                "minimum_margin": None
                if hit is None
                else hit["minimum_margin"],
                "mu": None if hit is None else hit["mu"],
                "nu": None if hit is None else hit["nu"],
                "seed": None if hit is None else hit["seed"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
