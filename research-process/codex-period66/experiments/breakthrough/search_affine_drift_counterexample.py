from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.search_active_set_switching_cycle import load_problem  # noqa: E402
from experiments.search_switching_cone_certificate import (  # noqa: E402
    all_masks,
    compose_affine_cycle,
    iterate_affine_states,
    iterate_linear_states,
    q_affine_map,
    signed_margins,
)
from experiments.slack_admm_core import SlackQpProblem, slack_admm_step  # noqa: E402
from src.admm_identity.slack_projection import (  # noqa: E402
    active_mask_from_argument,
    active_region_margin,
    build_effective_fixed_active_set_map,
    effective_state_size,
    unpack_effective_state,
    z_projection_argument_for_step,
)


def mask_key(mask: np.ndarray) -> tuple[int, ...]:
    return tuple(mask.astype(int).tolist())


def parse_lengths(text: str) -> list[int]:
    return [int(item) for item in text.split(",") if item]


def matrix_rank(matrix: np.ndarray, tol: float) -> int:
    if matrix.size == 0:
        return 0
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    return int(np.sum(singular_values > tol))


def nullspace(matrix: np.ndarray, tol: float) -> np.ndarray:
    if matrix.size == 0:
        return np.eye(matrix.shape[1])
    _, singular_values, vh = np.linalg.svd(matrix, full_matrices=True)
    rank = int(np.sum(singular_values > tol))
    return vh[rank:].T.copy()


def solve_range_residual(system: np.ndarray, offset: np.ndarray) -> tuple[np.ndarray, float]:
    solution, _, _, _ = np.linalg.lstsq(system, offset, rcond=None)
    residual = system @ solution - offset
    return solution, float(np.linalg.norm(residual) / (1.0 + np.linalg.norm(offset)))


def projected_drift_direction(
    product: np.ndarray,
    offset: np.ndarray,
    singular_tol: float,
) -> tuple[np.ndarray | None, float]:
    system = np.eye(product.shape[0]) - product
    right = nullspace(system, singular_tol)
    left = nullspace(system.T, singular_tol)
    if right.size == 0 or left.size == 0:
        return None, 0.0
    obstruction = left.T @ offset
    coupling = left.T @ right
    coeffs, _, _, _ = np.linalg.lstsq(coupling, obstruction, rcond=None)
    drift = right @ coeffs
    norm = float(np.linalg.norm(drift))
    if norm <= singular_tol:
        return None, float(np.linalg.norm(obstruction) / (1.0 + np.linalg.norm(offset)))
    return drift / norm, float(np.linalg.norm(obstruction) / (1.0 + np.linalg.norm(offset)))


def best_cone_orientation(
    matrices: dict[tuple[int, ...], np.ndarray],
    q_matrix: np.ndarray,
    cycle: tuple[tuple[int, ...], ...],
    direction: np.ndarray,
) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    for sign in (1.0, -1.0):
        oriented = sign * direction
        states = iterate_linear_states(matrices, cycle, oriented)
        margins = signed_margins(q_matrix, np.zeros(q_matrix.shape[0]), cycle, states)
        min_margin = min(float(np.min(item)) for item in margins)
        record = {
            "orientation": int(sign),
            "min_linear_margin": min_margin,
            "linear_margins": [item.tolist() for item in margins],
        }
        if best is None or min_margin > best["min_linear_margin"]:
            best = record
    if best is None:
        raise RuntimeError("empty orientation check")
    return best


def best_unit_eigendirection_cone(
    product: np.ndarray,
    matrices: dict[tuple[int, ...], np.ndarray],
    q_matrix: np.ndarray,
    cycle: tuple[tuple[int, ...], ...],
    singular_tol: float,
) -> dict[str, Any] | None:
    basis = nullspace(product - np.eye(product.shape[0]), singular_tol)
    if basis.size == 0:
        return None
    best: dict[str, Any] | None = None
    for index in range(basis.shape[1]):
        direction = basis[:, index]
        norm = float(np.linalg.norm(direction))
        if norm <= singular_tol:
            continue
        record = best_cone_orientation(matrices, q_matrix, cycle, direction / norm)
        record["basis_index"] = index
        if best is None or record["min_linear_margin"] > best["min_linear_margin"]:
            best = record
    return best


def analyze_cycle(
    maps: dict[tuple[int, ...], tuple[np.ndarray, np.ndarray]],
    q_matrix: np.ndarray,
    q_offset: np.ndarray,
    cycle: tuple[tuple[int, ...], ...],
    unit_tol: float,
    near_unit_tol: float,
    singular_tol: float,
    range_tol: float,
    margin_tol: float,
) -> dict[str, Any]:
    matrices = {key: value[0] for key, value in maps.items()}
    product, offset = compose_affine_cycle(maps, cycle)
    eigenvalues = np.linalg.eigvals(product)
    spectral_radius = float(np.max(np.abs(eigenvalues))) if eigenvalues.size else 0.0
    unit_distances = [float(abs(value - 1.0)) for value in eigenvalues]
    min_unit_distance = min(unit_distances) if unit_distances else float("inf")
    unit_algebraic_count = sum(distance <= unit_tol for distance in unit_distances)
    near_unit_count = sum(distance <= near_unit_tol for distance in unit_distances)

    system = np.eye(product.shape[0]) - product
    rank = matrix_rank(system, singular_tol)
    geometric_multiplicity = product.shape[0] - rank
    singular_values = np.linalg.svd(system, compute_uv=False).tolist()
    basepoint, range_residual = solve_range_residual(system, offset)
    drift_direction, left_obstruction = projected_drift_direction(product, offset, singular_tol)
    nonsemisimple_unit = bool(unit_algebraic_count > geometric_multiplicity)
    range_obstruction = bool(range_residual > range_tol and left_obstruction > range_tol)

    drift_cone: dict[str, Any] | None = None
    if drift_direction is not None:
        drift_cone = best_cone_orientation(matrices, q_matrix, cycle, drift_direction)
        drift_cone["is_cone_compatible"] = bool(drift_cone["min_linear_margin"] >= margin_tol)

    unit_cone = best_unit_eigendirection_cone(product, matrices, q_matrix, cycle, singular_tol)
    if unit_cone is not None:
        unit_cone["is_cone_compatible"] = bool(unit_cone["min_linear_margin"] >= margin_tol)

    affine_states = iterate_affine_states(maps, cycle, basepoint)
    affine_margins = signed_margins(q_matrix, q_offset, cycle, affine_states)
    min_affine_margin = min(float(np.min(item)) for item in affine_margins)

    screen_hit = bool(
        nonsemisimple_unit
        or range_obstruction
        or (unit_algebraic_count > 0 and min_affine_margin >= margin_tol)
    )
    cone_hit = bool(
        screen_hit
        and (
            (drift_cone is not None and drift_cone["is_cone_compatible"])
            or (unit_cone is not None and unit_cone["is_cone_compatible"])
        )
    )

    return {
        "cycle": [list(item) for item in cycle],
        "length": len(cycle),
        "is_constant_cycle": len(set(cycle)) == 1,
        "spectral_radius": spectral_radius,
        "eigenvalues": [
            {"real": float(np.real(value)), "imag": float(np.imag(value)), "abs": float(abs(value))}
            for value in eigenvalues
        ],
        "min_unit_distance": min_unit_distance,
        "near_unit_count": int(near_unit_count),
        "unit_algebraic_count": int(unit_algebraic_count),
        "unit_geometric_multiplicity": int(geometric_multiplicity),
        "nonsemisimple_unit": nonsemisimple_unit,
        "singular_values_I_minus_P": singular_values,
        "range_residual": range_residual,
        "left_obstruction_norm": left_obstruction,
        "range_obstruction": range_obstruction,
        "min_affine_margin_at_lstsq_basepoint": min_affine_margin,
        "drift_cone": drift_cone,
        "unit_eigendirection_cone": unit_cone,
        "screen_hit": screen_hit,
        "cone_hit": cone_hit,
    }


def simulate_projected_itinerary(
    problem: SlackQpProblem,
    cycle: list[list[int]],
    initial_effective_state: np.ndarray,
    cycles_to_simulate: int,
) -> dict[str, Any]:
    state = unpack_effective_state(initial_effective_state, problem)
    expected = [np.array(item, dtype=bool) for item in cycle]
    total_steps = len(expected) * cycles_to_simulate
    min_expected_margin = float("inf")
    mismatch_count = 0
    first_mismatch: dict[str, Any] | None = None
    observed_masks: list[list[int]] = []

    for step in range(total_steps):
        _, _, argument = z_projection_argument_for_step(state, problem)
        expected_mask = expected[step % len(expected)]
        observed = active_mask_from_argument(argument)
        observed_masks.append(observed.astype(int).tolist())
        margin = active_region_margin(argument, expected_mask)
        min_expected_margin = min(min_expected_margin, float(margin))
        if not np.array_equal(observed, expected_mask):
            mismatch_count += 1
            if first_mismatch is None:
                first_mismatch = {
                    "step": step,
                    "expected": expected_mask.astype(int).tolist(),
                    "observed": observed.astype(int).tolist(),
                    "expected_margin": float(margin),
                    "q_argument": argument.tolist(),
                }
        state = slack_admm_step(state, problem)

    return {
        "cycles_to_simulate": cycles_to_simulate,
        "steps": total_steps,
        "mismatch_count": mismatch_count,
        "first_mismatch": first_mismatch,
        "min_expected_margin": min_expected_margin,
        "observed_prefix": observed_masks[: min(16, len(observed_masks))],
    }


def well_posedness(problem: SlackQpProblem) -> dict[str, Any]:
    beta = problem.beta
    x_matrix = problem.q1 + beta * (problem.a.T @ problem.a)
    y_matrix = problem.q2 + beta * (problem.bmat.T @ problem.bmat)
    x_eigs = np.linalg.eigvalsh(x_matrix)
    y_eigs = np.linalg.eigvalsh(y_matrix)
    return {
        "min_eig_q1_plus_beta_ata": float(np.min(x_eigs)),
        "min_eig_q2_plus_beta_btb": float(np.min(y_eigs)),
        "x_subproblem_positive_definite": bool(np.min(x_eigs) > 1.0e-10),
        "y_subproblem_positive_definite": bool(np.min(y_eigs) > 1.0e-10),
    }


def run_search(
    payload: dict[str, Any],
    cycle_lengths: list[int],
    unit_tol: float,
    near_unit_tol: float,
    singular_tol: float,
    range_tol: float,
    margin_tol: float,
    max_records: int,
    max_simulations: int,
    cycles_to_simulate: int,
) -> dict[str, Any]:
    problem = load_problem(payload)
    masks = [mask_key(mask) for mask in all_masks(problem.rhs.shape[0])]
    active_maps = {
        key: build_effective_fixed_active_set_map(problem, np.array(key, dtype=bool))
        for key in masks
    }
    maps = {key: (value.matrix, value.offset) for key, value in active_maps.items()}
    q_matrix, q_offset = q_affine_map(problem, effective_state_size(problem))

    records: list[dict[str, Any]] = []
    for length in cycle_lengths:
        for cycle in itertools.product(masks, repeat=length):
            if len(set(cycle)) == 1:
                continue
            records.append(
                analyze_cycle(
                    maps=maps,
                    q_matrix=q_matrix,
                    q_offset=q_offset,
                    cycle=cycle,
                    unit_tol=unit_tol,
                    near_unit_tol=near_unit_tol,
                    singular_tol=singular_tol,
                    range_tol=range_tol,
                    margin_tol=margin_tol,
                )
            )

    records.sort(
        key=lambda item: (
            item["cone_hit"],
            item["screen_hit"],
            item["range_obstruction"],
            item["nonsemisimple_unit"],
            item["near_unit_count"],
            -item["min_unit_distance"],
            item["spectral_radius"],
        ),
        reverse=True,
    )

    simulations = []
    matrices = {key: value[0] for key, value in maps.items()}
    for item in records[:max_simulations]:
        cycle = tuple(tuple(mask) for mask in item["cycle"])
        product, offset = compose_affine_cycle(maps, cycle)
        initial, _ = solve_range_residual(np.eye(product.shape[0]) - product, offset)
        simulation = simulate_projected_itinerary(
            problem=problem,
            cycle=item["cycle"],
            initial_effective_state=initial,
            cycles_to_simulate=cycles_to_simulate,
        )
        simulation["cycle"] = item["cycle"]
        simulation["range_residual"] = item["range_residual"]
        simulation["min_unit_distance"] = item["min_unit_distance"]
        simulations.append(simulation)
        item["projected_admm_simulation"] = simulation

    counterexample_candidates = [
        item
        for item in records
        if item["cone_hit"]
        and item.get("projected_admm_simulation", {}).get("mismatch_count", 1) == 0
        and well_posedness(problem)["x_subproblem_positive_definite"]
        and well_posedness(problem)["y_subproblem_positive_definite"]
    ]

    return {
        "status_label": "unit_root_jordan_affine_drift_search",
        "evidence_level": "counterexample_candidate" if counterexample_candidates else "failure_map",
        "claim_boundary": (
            "Stage 2 deterministic numerical screen over the selected QP and mask lengths; "
            "no proof-grade counterexample unless all candidate gates pass."
        ),
        "problem_source_status_label": payload.get("status_label"),
        "problem_claim_boundary": payload.get("claim_boundary"),
        "active_mask_from_source": payload.get("active_mask"),
        "well_posedness": well_posedness(problem),
        "config": {
            "cycle_lengths": cycle_lengths,
            "mask_count": len(masks),
            "cycle_evaluations": len(records),
            "unit_tol": unit_tol,
            "near_unit_tol": near_unit_tol,
            "singular_tol": singular_tol,
            "range_tol": range_tol,
            "margin_tol": margin_tol,
            "max_records": max_records,
            "max_simulations": max_simulations,
            "cycles_to_simulate": cycles_to_simulate,
        },
        "summary": {
            "screen_hit_count": sum(1 for item in records if item["screen_hit"]),
            "cone_hit_count": sum(1 for item in records if item["cone_hit"]),
            "counterexample_candidate_count": len(counterexample_candidates),
            "nonsemisimple_unit_count": sum(1 for item in records if item["nonsemisimple_unit"]),
            "range_obstruction_count": sum(1 for item in records if item["range_obstruction"]),
            "near_unit_count": sum(1 for item in records if item["near_unit_count"] > 0),
            "min_unit_distance": min((item["min_unit_distance"] for item in records), default=None),
            "max_range_residual": max((item["range_residual"] for item in records), default=0.0),
            "max_spectral_radius": max((item["spectral_radius"] for item in records), default=0.0),
        },
        "counterexample_candidates": counterexample_candidates[:max_records],
        "top_records": records[:max_records],
        "qp_embedding_checks": simulations,
    }


def write_unit_root_report(payload: dict[str, Any], output: Path) -> None:
    summary = payload["summary"]
    config = payload["config"]
    lines = [
        "# Stage 2 Unit-Root Jordan / Affine Drift Search",
        "",
        f"状态：`{payload['evidence_level']}`",
        "",
        "本报告只检查固定 QP 嵌入和有限长度 mask itinerary 下的 unit-root / affine-drift 机制；没有通过全部 gate 时不能称为严格反例。",
        "",
        "## Config",
        "",
        f"- cycle_lengths: `{config['cycle_lengths']}`",
        f"- cycle_evaluations: `{config['cycle_evaluations']}`",
        f"- unit_tol: `{config['unit_tol']}`",
        f"- range_tol: `{config['range_tol']}`",
        "",
        "## Summary",
        "",
        f"- screen_hit_count: `{summary['screen_hit_count']}`",
        f"- cone_hit_count: `{summary['cone_hit_count']}`",
        f"- counterexample_candidate_count: `{summary['counterexample_candidate_count']}`",
        f"- nonsemisimple_unit_count: `{summary['nonsemisimple_unit_count']}`",
        f"- range_obstruction_count: `{summary['range_obstruction_count']}`",
        f"- near_unit_count: `{summary['near_unit_count']}`",
        f"- min_unit_distance: `{summary['min_unit_distance']}`",
        f"- max_spectral_radius: `{summary['max_spectral_radius']}`",
        "",
        "## Top Records",
        "",
        "| cycle | rho | dist(lambda,1) | range residual | Jordan | cone hit |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for item in payload["top_records"][:20]:
        lines.append(
            f"| `{item['cycle']}` | `{item['spectral_radius']}` | "
            f"`{item['min_unit_distance']}` | `{item['range_residual']}` | "
            f"`{item['nonsemisimple_unit']}` | `{item['cone_hit']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "若 `counterexample_candidate_count=0`，本轮没有找到同时满足 unit-root/Jordan 或 affine-drift、signed-q cone 和真实 projected ADMM itinerary 的候选。该结果是当前范围的 failure map，不证明原始 direct ADMM 收敛。",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")


def write_qp_embedding_report(payload: dict[str, Any], output: Path) -> None:
    lines = [
        "# Stage 2 QP Embedding Checks",
        "",
        "状态：`numerical_screen`",
        "",
        "这里对 top Stage 2 records 使用真实 projected ADMM 更新检查 mask itinerary 是否按局部 affine recurrence 运行。通过该检查也仍需 exact/interval 证书；失败则不能升级为 counterexample candidate。",
        "",
        "## Well-Posedness",
        "",
    ]
    for key, value in payload["well_posedness"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Simulations", ""])
    for item in payload["qp_embedding_checks"]:
        lines.extend(
            [
                f"### Cycle `{item['cycle']}`",
                "",
                f"- range_residual: `{item['range_residual']}`",
                f"- min_unit_distance: `{item['min_unit_distance']}`",
                f"- mismatch_count: `{item['mismatch_count']}`",
                f"- min_expected_margin: `{item['min_expected_margin']}`",
                f"- first_mismatch: `{item['first_mismatch']}`",
                "",
            ]
        )
    output.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--cycle-lengths", default="2,3,4,5,6,7,8")
    parser.add_argument("--unit-tol", type=float, default=1.0e-8)
    parser.add_argument("--near-unit-tol", type=float, default=1.0e-5)
    parser.add_argument("--singular-tol", type=float, default=1.0e-9)
    parser.add_argument("--range-tol", type=float, default=1.0e-8)
    parser.add_argument("--margin-tol", type=float, default=1.0e-10)
    parser.add_argument("--max-records", type=int, default=100)
    parser.add_argument("--max-simulations", type=int, default=12)
    parser.add_argument("--cycles-to-simulate", type=int, default=8)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = run_search(
        payload=payload,
        cycle_lengths=parse_lengths(args.cycle_lengths),
        unit_tol=args.unit_tol,
        near_unit_tol=args.near_unit_tol,
        singular_tol=args.singular_tol,
        range_tol=args.range_tol,
        margin_tol=args.margin_tol,
        max_records=args.max_records,
        max_simulations=args.max_simulations,
        cycles_to_simulate=args.cycles_to_simulate,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    candidates_path = args.output_dir / "affine_drift_candidates.json"
    cone_path = args.output_dir / "itinerary_cone_checks.json"
    unit_report_path = args.output_dir / "unit_root_jordan_candidates.md"
    qp_report_path = args.output_dir / "qp_embedding_checks.md"

    candidates_payload = {
        key: result[key]
        for key in (
            "status_label",
            "evidence_level",
            "claim_boundary",
            "problem_source_status_label",
            "problem_claim_boundary",
            "active_mask_from_source",
            "well_posedness",
            "config",
            "summary",
            "counterexample_candidates",
            "top_records",
        )
    }
    cone_payload = {
        "status_label": result["status_label"],
        "evidence_level": result["evidence_level"],
        "claim_boundary": result["claim_boundary"],
        "config": result["config"],
        "summary": result["summary"],
        "top_records": result["top_records"],
        "qp_embedding_checks": result["qp_embedding_checks"],
    }

    candidates_path.write_text(json.dumps(candidates_payload, indent=2), encoding="utf-8")
    cone_path.write_text(json.dumps(cone_payload, indent=2), encoding="utf-8")
    write_unit_root_report(result, unit_report_path)
    write_qp_embedding_report(result, qp_report_path)

    print("DONE Stage 2 affine drift search.")
    print(f"Evidence level: {result['evidence_level']}")
    print(f"Counterexample candidates: {result['summary']['counterexample_candidate_count']}")
    print(f"Files written: {candidates_path}, {cone_path}, {unit_report_path}, {qp_report_path}")


if __name__ == "__main__":
    main()
