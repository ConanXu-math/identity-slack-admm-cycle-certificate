from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution


Mask = tuple[int, int]


def canonical_margin(
    strict_values: list[float], weak_values: list[float]
) -> tuple[float, float, float]:
    """Return strict margin, weakest weak row, and a feasibility-aware score."""
    strict_margin = min(strict_values)
    weak_minimum = min(weak_values) if weak_values else float("inf")
    optimization_score = (
        strict_margin
        if weak_minimum >= 0.0
        else min(strict_margin, weak_minimum)
    )
    return strict_margin, weak_minimum, optimization_score


def rational_rotation(parameter: float) -> np.ndarray:
    denominator = 1.0 + parameter * parameter
    return np.array(
        [
            [1.0 - parameter * parameter, -2.0 * parameter],
            [2.0 * parameter, 1.0 - parameter * parameter],
        ]
    ) / denominator


def canonical_word(word: tuple[Mask, ...]) -> tuple[Mask, ...]:
    candidates = []
    for swap in (False, True):
        transformed = tuple((mask[1], mask[0]) if swap else mask for mask in word)
        candidates.extend(
            transformed[index:] + transformed[:index]
            for index in range(len(transformed))
        )
    return min(candidates)


def canonical_words(lengths: tuple[int, ...]) -> list[tuple[Mask, ...]]:
    masks = tuple(itertools.product((0, 1), repeat=2))
    return sorted(
        {
            canonical_word(word)
            for length in lengths
            for word in itertools.product(masks, repeat=length)
            if len(set(word)) > 1
        },
        key=lambda word: (len(word), word),
    )


def matrices_from_parameters(parameters: np.ndarray, rhs_chart: int) -> tuple[np.ndarray, ...]:
    mu1, mu2, rotation_m, nu1, nu2, rotation_n, rhs_parameter = parameters
    rot_m = rational_rotation(rotation_m)
    rot_n = rational_rotation(rotation_n)
    m_matrix = rot_m @ np.diag([mu1, mu2]) @ rot_m.T
    n_matrix = rot_n @ np.diag([nu1, nu2]) @ rot_n.T
    if rhs_chart == 0:
        rhs = np.array([1.0, rhs_parameter])
    else:
        rhs = np.array([rhs_parameter, 1.0])
    rhs /= 1.0 + abs(rhs_parameter)
    return m_matrix, n_matrix, rhs


def affine_factors(
    m_matrix: np.ndarray, n_matrix: np.ndarray, rhs: np.ndarray, source: Mask
) -> tuple[np.ndarray, np.ndarray]:
    identity = np.eye(2)
    selector = np.diag(source)
    matrix = np.block(
        [
            [n_matrix @ m_matrix, -n_matrix @ (identity - m_matrix)],
            [
                (identity - n_matrix) @ m_matrix,
                n_matrix
                + (identity - n_matrix) @ m_matrix
                - (identity - selector),
            ],
        ]
    )
    offset = np.concatenate(
        (
            n_matrix @ (identity - m_matrix) @ rhs,
            (identity - n_matrix) @ (identity - m_matrix) @ rhs,
        )
    )
    return matrix, offset


def periodic_margin(
    parameters: np.ndarray, word: tuple[Mask, ...], rhs_chart: int
) -> dict[str, object] | None:
    m_matrix, n_matrix, rhs = matrices_from_parameters(parameters, rhs_chart)
    matrices, offsets, source_factors = [], [], []
    for step, source in enumerate(word):
        target = word[(step + 1) % len(word)]
        source_matrix, source_offset = affine_factors(m_matrix, n_matrix, rhs, source)
        target_sign = np.diag(
            [1.0, 1.0, *(1.0 if bit else -1.0 for bit in target)]
        )
        matrices.append(target_sign @ source_matrix)
        offsets.append(target_sign @ source_offset)
        source_factors.append((source_matrix, source_offset))

    product = np.eye(4)
    period_offset = np.zeros(4)
    for matrix, offset in zip(matrices, offsets):
        period_offset = matrix @ period_offset + offset
        product = matrix @ product
    periodicity = np.eye(4) - product
    try:
        basepoint = np.linalg.solve(periodicity, period_offset)
    except np.linalg.LinAlgError:
        return None

    state = basepoint.copy()
    strict_values: list[float] = []
    weak_values: list[float] = []
    phase_states = []
    for step, source in enumerate(word):
        target = word[(step + 1) % len(word)]
        source_matrix, source_offset = source_factors[step]
        projection_argument = (source_matrix @ state + source_offset)[2:]
        phase_states.append(state.copy())
        for index in range(2):
            source_value = float(state[2 + index])
            target_value = float(
                projection_argument[index]
                if target[index]
                else -projection_argument[index]
            )
            (strict_values if source[index] else weak_values).append(source_value)
            (strict_values if target[index] else weak_values).append(target_value)
        state = matrices[step] @ state + offsets[step]

    strict_margin, weak_minimum, optimization_score = canonical_margin(
        strict_values, weak_values
    )

    return {
        "margin": optimization_score,
        "strict_margin": strict_margin,
        "weak_minimum": weak_minimum,
        "weak_feasible": weak_minimum >= 0.0,
        "strict_values": strict_values,
        "weak_values": weak_values,
        "periodicity_determinant": float(np.linalg.det(periodicity)),
        "periodicity_condition": float(np.linalg.cond(periodicity)),
        "basepoint": basepoint.tolist(),
        "phase_states": [phase.tolist() for phase in phase_states],
        "M": m_matrix.tolist(),
        "N": n_matrix.tolist(),
        "rhs": rhs.tolist(),
    }


def optimize_word(
    word: tuple[Mask, ...],
    seed: int,
    maxiter: int,
    popsize: int,
    rhs_bound: float,
) -> dict[str, object]:
    bounds = [
        (0.01, 0.99),
        (0.01, 0.99),
        (-4.0, 4.0),
        (0.01, 0.99),
        (0.01, 0.99),
        (-4.0, 4.0),
        (-rhs_bound, rhs_bound),
    ]
    best: dict[str, object] | None = None
    best_parameters: np.ndarray | None = None
    best_chart = 0
    for chart in (0, 1):

        def objective(parameters: np.ndarray) -> float:
            evaluation = periodic_margin(parameters, word, chart)
            return 1.0e6 if evaluation is None else -float(evaluation["margin"])

        result = differential_evolution(
            objective,
            bounds,
            seed=seed + chart,
            maxiter=maxiter,
            popsize=popsize,
            polish=True,
            tol=1.0e-8,
            workers=1,
            updating="immediate",
        )
        evaluation = periodic_margin(result.x, word, chart)
        if evaluation is not None and (
            best is None or float(evaluation["margin"]) > float(best["margin"])
        ):
            best = evaluation
            best_parameters = result.x
            best_chart = chart
    assert best is not None and best_parameters is not None
    best.update(
        {
            "word": [list(mask) for mask in word],
            "rhs_chart": best_chart,
            "parameters": best_parameters.tolist(),
            "seed": seed,
        }
    )
    return best


def run(
    lengths: tuple[int, ...],
    seed: int,
    maxiter: int,
    popsize: int,
    rhs_bound: float,
) -> dict[str, object]:
    words = canonical_words(lengths)
    records = [
        optimize_word(word, seed + 100 * index, maxiter, popsize, rhs_bound)
        for index, word in enumerate(words)
    ]
    records.sort(key=lambda record: float(record["margin"]), reverse=True)
    positive = [
        record
        for record in records
        if bool(record["weak_feasible"])
        and float(record["strict_margin"]) > 1.0e-7
    ]
    return {
        "status": "numerical_periodic_margin_optimization",
        "scope": "A=B=I2, beta=1, strongly convex quadratic Hessians represented by 0<M,N<I",
        "lengths": list(lengths),
        "canonical_word_count": len(words),
        "seed": seed,
        "maxiter": maxiter,
        "popsize": popsize,
        "best_margin": records[0]["margin"],
        "positive_candidate_count": len(positive),
        "records": records,
        "claim_boundary": [
            "Differential evolution is candidate optimization, not a proof of feasibility or infeasibility.",
            "Inactive source/target rows are weak constraints and do not limit the strict margin once feasible.",
            "A positive candidate must be rationalized and passed through the exact periodic-itinerary checker.",
            "A nonpositive optimum does not prove that the word is impossible.",
        ],
    }


def write_report(payload: dict[str, object], path: Path) -> None:
    lines = [
        "# 非恒定周期 Margin 优化",
        "",
        "状态：numerical_screen；目标直接是 canonical itinerary strict margin，不是谱半径。",
        "",
        f"- canonical words: {payload['canonical_word_count']}",
        f"- best margin: {payload['best_margin']}",
        f"- positive candidates: {payload['positive_candidate_count']}",
        "",
        "## Top Records",
        "",
    ]
    records = payload["records"]
    assert isinstance(records, list)
    for record in records[:10]:
        lines.append(
            f"- word {record['word']}: score {record['margin']}, "
            f"strict margin {record['strict_margin']}, "
            f"weak minimum {record['weak_minimum']}"
        )
    lines.extend(
        [
            "",
            "## 边界",
            "",
            "- 正 margin 只能进入有理化与 exact checker，不能直接称为反例。",
            "- 非正结果只是有限预算 failure map，不能证明不存在周期轨道。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lengths", default="2,3")
    parser.add_argument("--seed", type=int, default=20260712)
    parser.add_argument("--maxiter", type=int, default=120)
    parser.add_argument("--popsize", type=int, default=10)
    parser.add_argument("--rhs-bound", type=float, default=5.0)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/breakthrough_attempts/stage27_periodic_margin"),
    )
    args = parser.parse_args()
    lengths = tuple(int(value) for value in args.lengths.split(",") if value)
    payload = run(lengths, args.seed, args.maxiter, args.popsize, args.rhs_bound)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "periodic_margin_optimization.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(payload, args.output_dir / "periodic_margin_optimization.md")
    print(
        json.dumps(
            {
                "best_margin": payload["best_margin"],
                "positive_candidate_count": payload["positive_candidate_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
