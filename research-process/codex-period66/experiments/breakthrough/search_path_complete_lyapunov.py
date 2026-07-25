from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.search_active_set_switching_cycle import load_problem  # noqa: E402
from src.admm_identity.slack_projection import complementarity_reduced_linear_matrix  # noqa: E402


def all_mask_keys(dim: int) -> list[tuple[int, ...]]:
    return [tuple((bits >> index) & 1 for index in range(dim)) for bits in range(2**dim)]


def parse_lengths(text: str) -> list[int]:
    return [int(item) for item in text.split(",") if item]


def cycle_product(
    matrices: dict[tuple[int, ...], np.ndarray],
    cycle: tuple[tuple[int, ...], ...],
) -> np.ndarray:
    product = None
    for mask_key in cycle:
        matrix = matrices[mask_key]
        product = matrix if product is None else matrix @ product
    if product is None:
        raise ValueError("cycle must not be empty")
    return product


def enumerate_cycles(
    masks: list[tuple[int, ...]],
    lengths: list[int],
    skip_constant: bool = True,
) -> list[tuple[tuple[int, ...], ...]]:
    cycles: list[tuple[tuple[int, ...], ...]] = []
    for length in lengths:
        for cycle in itertools.product(masks, repeat=length):
            if skip_constant and len(set(cycle)) == 1:
                continue
            cycles.append(cycle)
    return cycles


def spectral_radius(matrix: np.ndarray) -> float:
    if matrix.size == 0:
        return 0.0
    return float(np.max(np.abs(np.linalg.eigvals(matrix))))


def unpack_spd(params: np.ndarray, dim: int) -> np.ndarray:
    lower = np.zeros((dim, dim))
    cursor = 0
    for row in range(dim):
        for col in range(row + 1):
            value = params[cursor]
            lower[row, col] = np.exp(value) if row == col else value
            cursor += 1
    h_matrix = lower @ lower.T
    return h_matrix / np.trace(h_matrix)


def zero_spd_params(dim: int) -> np.ndarray:
    return np.zeros(dim * (dim + 1) // 2)


def max_lyapunov_violation(h_matrix: np.ndarray, products: list[np.ndarray]) -> tuple[float, list[float]]:
    violations = []
    for product in products:
        sym = product.T @ h_matrix @ product - h_matrix
        sym = 0.5 * (sym + sym.T)
        violations.append(float(np.max(np.linalg.eigvalsh(sym))))
    return max(violations) if violations else -float("inf"), violations


def optimize_common_product_metric(
    products: list[np.ndarray],
    maxiter: int,
    restarts: int,
    seed: int,
) -> dict[str, Any]:
    dim = products[0].shape[0]
    rng = np.random.default_rng(seed)
    starts = [zero_spd_params(dim)]
    starts.extend(rng.normal(scale=0.2, size=dim * (dim + 1) // 2) for _ in range(max(0, restarts - 1)))
    best_result = None

    def objective(params: np.ndarray) -> float:
        h_matrix = unpack_spd(params, dim)
        violation, _ = max_lyapunov_violation(h_matrix, products)
        return violation

    for start in starts:
        result = minimize(
            objective,
            start,
            method="Powell",
            options={"maxiter": maxiter, "xtol": 1.0e-10, "ftol": 1.0e-12},
        )
        if best_result is None or result.fun < best_result.fun:
            best_result = result

    if best_result is None:
        raise RuntimeError("optimizer did not run")
    h_matrix = unpack_spd(best_result.x, dim)
    max_violation, violations = max_lyapunov_violation(h_matrix, products)
    eigs = np.linalg.eigvalsh(h_matrix)
    return {
        "status_label": "common_product_quadratic_metric_search",
        "optimizer_success": bool(best_result.success),
        "optimizer_message": str(best_result.message),
        "objective": float(best_result.fun),
        "max_violation": max_violation,
        "min_h_eigenvalue": float(np.min(eigs)),
        "max_h_eigenvalue": float(np.max(eigs)),
        "condition_number": float(np.max(eigs) / np.min(eigs)),
        "h_matrix": h_matrix.tolist(),
        "violation_summary": {
            "max": max_violation,
            "min": min(violations) if violations else None,
            "positive_count_1e_8": sum(value > 1.0e-8 for value in violations),
            "positive_count_1e_10": sum(value > 1.0e-10 for value in violations),
        },
    }


def unpack_node_metrics(params: np.ndarray, node_count: int, dim: int) -> list[np.ndarray]:
    block = dim * (dim + 1) // 2
    return [unpack_spd(params[index * block : (index + 1) * block], dim) for index in range(node_count)]


def optimize_nonconstant_transition_metrics(
    matrices: dict[tuple[int, ...], np.ndarray],
    masks: list[tuple[int, ...]],
    maxiter: int,
    seed: int,
) -> dict[str, Any]:
    dim = next(iter(matrices.values())).shape[0]
    block = dim * (dim + 1) // 2
    mask_to_index = {mask: index for index, mask in enumerate(masks)}
    rng = np.random.default_rng(seed)
    start = np.concatenate(
        [zero_spd_params(dim) + rng.normal(scale=0.05, size=block) for _ in masks]
    )
    transitions = [(left, right) for left in masks for right in masks if left != right]

    def objective(params: np.ndarray) -> float:
        h_list = unpack_node_metrics(params, len(masks), dim)
        max_value = -float("inf")
        for left, right in transitions:
            h_left = h_list[mask_to_index[left]]
            h_right = h_list[mask_to_index[right]]
            step = matrices[left]
            sym = step.T @ h_right @ step - h_left
            sym = 0.5 * (sym + sym.T)
            max_value = max(max_value, float(np.max(np.linalg.eigvalsh(sym))))
        return max_value

    result = minimize(
        objective,
        start,
        method="Powell",
        options={"maxiter": maxiter, "xtol": 1.0e-9, "ftol": 1.0e-11},
    )
    h_list = unpack_node_metrics(result.x, len(masks), dim)
    records = []
    max_violation = -float("inf")
    for left, right in transitions:
        h_left = h_list[mask_to_index[left]]
        h_right = h_list[mask_to_index[right]]
        step = matrices[left]
        sym = step.T @ h_right @ step - h_left
        sym = 0.5 * (sym + sym.T)
        violation = float(np.max(np.linalg.eigvalsh(sym)))
        max_violation = max(max_violation, violation)
        records.append(
            {
                "from": list(left),
                "to": list(right),
                "max_eigenvalue": violation,
            }
        )
    records.sort(key=lambda item: item["max_eigenvalue"], reverse=True)
    return {
        "status_label": "nonconstant_transition_path_complete_metric_search",
        "optimizer_success": bool(result.success),
        "optimizer_message": str(result.message),
        "objective": float(result.fun),
        "max_violation": max_violation,
        "node_metrics": {str(list(mask)): h_list[index].tolist() for index, mask in enumerate(masks)},
        "top_transition_violations": records[:20],
    }


def run_search(
    payload: dict[str, Any],
    cycle_lengths: list[int],
    maxiter_common: int,
    maxiter_node: int,
    restarts: int,
    seed: int,
    acceptance_tol: float,
) -> dict[str, Any]:
    problem = load_problem(payload)
    masks = all_mask_keys(problem.rhs.shape[0])
    matrices = {
        mask: complementarity_reduced_linear_matrix(problem, np.array(mask, dtype=bool))
        for mask in masks
    }
    fixed_mask_records = [
        {
            "mask": list(mask),
            "spectral_radius": spectral_radius(matrix),
        }
        for mask, matrix in matrices.items()
    ]
    fixed_mask_records.sort(key=lambda item: item["spectral_radius"], reverse=True)
    self_loop_obstruction = any(item["spectral_radius"] > 1.0 + acceptance_tol for item in fixed_mask_records)

    cycles = enumerate_cycles(masks, cycle_lengths, skip_constant=True)
    products = [cycle_product(matrices, cycle) for cycle in cycles]
    product_records = [
        {
            "cycle": [list(mask) for mask in cycle],
            "spectral_radius": spectral_radius(product),
        }
        for cycle, product in zip(cycles, products, strict=True)
    ]
    product_records.sort(key=lambda item: item["spectral_radius"], reverse=True)

    common_metric = optimize_common_product_metric(
        products=products,
        maxiter=maxiter_common,
        restarts=restarts,
        seed=seed,
    )
    transition_metric = optimize_nonconstant_transition_metrics(
        matrices=matrices,
        masks=masks,
        maxiter=maxiter_node,
        seed=seed + 1,
    )
    common_candidate = common_metric["max_violation"] <= acceptance_tol
    transition_candidate = transition_metric["max_violation"] <= acceptance_tol

    return {
        "status_label": "stage3_path_complete_lyapunov_gate",
        "evidence_level": "proof_attempt" if (common_candidate or transition_candidate) else "failure_map",
        "claim_boundary": (
            "Heuristic finite-dimensional quadratic Lyapunov search for the selected QP embedding; "
            "not a proof of original direct ADMM convergence and not a certificate without exact/interval verification."
        ),
        "problem_source_status_label": payload.get("status_label"),
        "problem_claim_boundary": payload.get("claim_boundary"),
        "config": {
            "cycle_lengths": cycle_lengths,
            "cycle_count": len(cycles),
            "state_dimension": products[0].shape[0] if products else None,
            "maxiter_common": maxiter_common,
            "maxiter_node": maxiter_node,
            "restarts": restarts,
            "seed": seed,
            "acceptance_tol": acceptance_tol,
        },
        "summary": {
            "self_loop_obstruction": self_loop_obstruction,
            "max_fixed_mask_spectral_radius": fixed_mask_records[0]["spectral_radius"],
            "max_product_spectral_radius": product_records[0]["spectral_radius"],
            "common_product_metric_candidate": common_candidate,
            "common_product_metric_max_violation": common_metric["max_violation"],
            "nonconstant_transition_metric_candidate": transition_candidate,
            "nonconstant_transition_metric_max_violation": transition_metric["max_violation"],
        },
        "fixed_mask_records": fixed_mask_records,
        "top_product_records": product_records[:40],
        "common_product_metric": common_metric,
        "nonconstant_transition_metric": transition_metric,
    }


def write_report(payload: dict[str, Any], output: Path) -> None:
    summary = payload["summary"]
    config = payload["config"]
    lines = [
        "# Stage 3A Path-Complete Lyapunov Gate",
        "",
        f"状态：`{payload['evidence_level']}`",
        "",
        "本报告尝试把 Stage 1/2 之后的路线转成 proof-first 的 common seminorm / path-complete Lyapunov gate。由于本地没有 SDP 求解器，本轮只使用 NumPy/SciPy 做有限 QP 嵌入上的启发式二次型搜索；结果不能作为严格证明。",
        "",
        "## Config",
        "",
        f"- cycle_lengths: `{config['cycle_lengths']}`",
        f"- cycle_count: `{config['cycle_count']}`",
        f"- state_dimension: `{config['state_dimension']}`",
        f"- acceptance_tol: `{config['acceptance_tol']}`",
        "",
        "## Necessary Obstruction",
        "",
        f"- max_fixed_mask_spectral_radius: `{summary['max_fixed_mask_spectral_radius']}`",
        f"- self_loop_obstruction: `{summary['self_loop_obstruction']}`",
        "",
        "若允许 self-loop transition，则任何 fixed mask 的 spectral radius 超过 1 都排除严格正定 path-complete quadratic metric。这个 obstruction 只针对未加 cone restriction 的矩阵模型。",
        "",
        "## Common Product Metric Search",
        "",
        f"- max_product_spectral_radius: `{summary['max_product_spectral_radius']}`",
        f"- common_product_metric_candidate: `{summary['common_product_metric_candidate']}`",
        f"- common_product_metric_max_violation: `{summary['common_product_metric_max_violation']}`",
        "",
        "## Nonconstant Transition Metric Search",
        "",
        f"- nonconstant_transition_metric_candidate: `{summary['nonconstant_transition_metric_candidate']}`",
        f"- nonconstant_transition_metric_max_violation: `{summary['nonconstant_transition_metric_max_violation']}`",
        "",
        "## Top Product Records",
        "",
        "| cycle | spectral radius |",
        "| --- | ---: |",
    ]
    for item in payload["top_product_records"][:20]:
        lines.append(f"| `{item['cycle']}` | `{item['spectral_radius']}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "若 metric candidate 为 `True`，下一步必须做 exact/interval verification，并明确该 metric 只覆盖当前 finite product family。若为 `False`，本轮只说明当前启发式搜索未找到二次型证书，不排除更复杂的 cone-restricted 或 higher-degree Lyapunov。",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--cycle-lengths", default="2,3")
    parser.add_argument("--maxiter-common", type=int, default=800)
    parser.add_argument("--maxiter-node", type=int, default=400)
    parser.add_argument("--restarts", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260707)
    parser.add_argument("--acceptance-tol", type=float, default=1.0e-8)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = run_search(
        payload=payload,
        cycle_lengths=parse_lengths(args.cycle_lengths),
        maxiter_common=args.maxiter_common,
        maxiter_node=args.maxiter_node,
        restarts=args.restarts,
        seed=args.seed,
        acceptance_tol=args.acceptance_tol,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_report(result, args.output)
    print("DONE Stage 3A path-complete Lyapunov gate.")
    print(f"Evidence level: {result['evidence_level']}")
    print(f"Common metric max violation: {result['summary']['common_product_metric_max_violation']}")
    print(f"Transition metric max violation: {result['summary']['nonconstant_transition_metric_max_violation']}")


if __name__ == "__main__":
    main()
