from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import sympy as sp


MASKS = tuple(itertools.product((0, 1), repeat=2))
GAMMA = sp.Rational(99, 100)


def _matrix_strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(sp.factor(x)) for x in row] for row in matrix.tolist()]


def _positive_definite(matrix: sp.Matrix) -> dict[str, object]:
    matrix = sp.simplify(matrix)
    if matrix != matrix.T:
        raise ValueError("positive-definite certificate requires an exactly symmetric matrix")
    leading = [sp.factor(matrix[:i, :i].det()) for i in range(1, matrix.rows + 1)]
    return {"leading_minors": [str(x) for x in leading], "positive": all(x > 0 for x in leading)}


def exact_data() -> dict[str, sp.Matrix]:
    identity = sp.eye(2)
    q1 = 3 * identity
    n = sp.Matrix([
        [sp.Rational(27, 100), -sp.Rational(1, 4)],
        [-sp.Rational(1, 4), sp.Rational(13, 25)],
    ])
    q2 = sp.simplify(n.inv() - identity)
    return {
        "q1": q1,
        "q2": q2,
        "m": sp.simplify((q1 + identity).inv()),
        "n": n,
        "h": sp.diag(1, 1, sp.Rational(9, 4), sp.Rational(9, 4)),
    }


def selector(mask: tuple[int, int]) -> sp.Matrix:
    return sp.diag(*mask)


def signed_jacobian(mask: tuple[int, int]) -> sp.Matrix:
    data = exact_data()
    m, n = data["m"], data["n"]
    identity = sp.eye(2)
    d = selector(mask)
    sign = 2 * d - identity
    return sp.simplify(
        (n * m).row_join(-n * (identity - m) * sign)
        .col_join(
            ((identity - n) * m).row_join(
                d - (identity - n) * (identity - m) * sign
            )
        )
    )


def original_admm_signed_jacobian(mask: tuple[int, int]) -> sp.Matrix:
    """Eliminate one original ADMM step on a fixed source orthant."""

    data = exact_data()
    m, n = data["m"], data["n"]
    identity = sp.eye(2)
    d = selector(mask)
    sign = 2 * d - identity
    # Canonical source: z=Dq and lambda=(I-D)q.
    x_map = (-m).row_join(-m * sign)
    lambda_minus_z = sp.zeros(2).row_join(-sign)
    y_map = sp.simplify(n * (lambda_minus_z - x_map))
    lambda_map = sp.zeros(2).row_join(identity - d)
    q_map = sp.simplify(-x_map - y_map + lambda_map)
    return sp.simplify(y_map.col_join(q_map))


def reduced_edge(source: tuple[int, int], target: tuple[int, int]) -> sp.Matrix:
    data = exact_data()
    m, n = data["m"], data["n"]
    identity = sp.eye(2)
    d = selector(source)
    target_sign = 2 * selector(target) - identity
    return sp.simplify(
        (n * m).row_join(-n * (identity - m))
        .col_join(
            (target_sign * (identity - n) * m).row_join(
                target_sign * (d - (identity - n) * (identity - m))
            )
        )
    )


def signed_transform(mask: tuple[int, int]) -> sp.Matrix:
    return sp.diag(1, 1, *(2 * value - 1 for value in mask))


def build_certificate() -> dict[str, object]:
    data = exact_data()
    h = data["h"]
    jacobians = []
    for mask in MASKS:
        matrix = signed_jacobian(mask)
        original_matrix = original_admm_signed_jacobian(mask)
        residual = sp.simplify(GAMMA**2 * h - matrix.T * h * matrix)
        jacobians.append({
            "mask": "".join(map(str, mask)),
            "matrix": _matrix_strings(matrix),
            "original_admm_matrix": _matrix_strings(original_matrix),
            "matches_original_admm_elimination": matrix == original_matrix,
            "contraction_residual": _matrix_strings(residual),
            "contraction_check": _positive_definite(residual),
        })

    edge_relations = []
    for source, target in itertools.product(MASKS, repeat=2):
        transformed = sp.simplify(
            signed_transform(target) * reduced_edge(source, target) * signed_transform(source)
        )
        edge_relations.append({
            "source": "".join(map(str, source)),
            "target": "".join(map(str, target)),
            "equals_signed_jacobian": transformed == signed_jacobian(source),
        })

    y1, y2, q1, q2 = sp.symbols("y1 y2 q1 q2", real=True)
    state = sp.Matrix([y1, y2, q1, q2])
    facet_checks = []
    for left, right in itertools.combinations(MASKS, 2):
        differing = [i for i in range(2) if left[i] != right[i]]
        if len(differing) != 1:
            continue
        coordinate = differing[0]
        facet_state = state.subs(q1 if coordinate == 0 else q2, 0)
        gap = sp.simplify((signed_jacobian(left) - signed_jacobian(right)) * facet_state)
        facet_checks.append({
            "left": "".join(map(str, left)),
            "right": "".join(map(str, right)),
            "coordinate": coordinate,
            "gap": [str(x) for x in gap],
            "continuous": gap == sp.zeros(4, 1),
        })

    identity = sp.eye(2)
    a_block = data["n"] * data["m"]
    b_block = data["n"] * (identity - data["m"])
    old_a_residual = sp.simplify(sp.Rational(1, 6) ** 2 * identity - a_block.T * a_block)
    old_b_residual = sp.simplify(sp.Rational(1, 2) ** 2 * identity - b_block.T * b_block)
    gate_exterior = {
        "old_gate": "a<=1/6 and b<=1/2 from small_gain_common_metric_theorem",
        "a_gram_residual": _matrix_strings(old_a_residual),
        "a_residual_determinant": str(sp.factor(old_a_residual.det())),
        "a_bound_fails": bool(old_a_residual.det() < 0),
        "b_gram_residual": _matrix_strings(old_b_residual),
        "b_residual_determinant": str(sp.factor(old_b_residual.det())),
        "b_bound_fails": bool(old_b_residual.det() < 0),
    }

    q2_check = _positive_definite(data["q2"])

    valid = bool(
        q2_check["positive"]
        and gate_exterior["a_bound_fails"]
        and gate_exterior["b_bound_fails"]
        and all(item["matches_original_admm_elimination"] for item in jacobians)
        and all(item["contraction_check"]["positive"] for item in jacobians)
        and all(item["equals_signed_jacobian"] for item in edge_relations)
        and all(item["continuous"] for item in facet_checks)
    )
    return {
        "status": "exact_fixed_qp_signed_pwa_certificate" if valid else "certificate_failed",
        "review_status": "see_external_review_manifest",
        "evidence_kind": "exact_rational_recurrence_facet_and_contraction_certificate",
        "scope": "Q1=3I, Q2=[[4421,2500],[2500,1921]]/779, A=B=I, rhs=0, beta=1",
        "Q1": _matrix_strings(data["q1"]),
        "Q2": _matrix_strings(data["q2"]),
        "Q2_positive_check": q2_check,
        "M": _matrix_strings(data["m"]),
        "N": _matrix_strings(data["n"]),
        "H": _matrix_strings(h),
        "gamma": str(GAMMA),
        "jacobians": jacobians,
        "edge_relations": edge_relations,
        "facet_checks": facet_checks,
        "gate_exterior": gate_exterior,
        "theorem_bridge": {
            "continuous_pwa_plus_common_jacobian_contraction": "global_incremental_H_contraction",
            "fixed_point_equivalence": "proved_in_notes/fixed_qp_signed_pwa_contraction_theorem.md",
            "claim": "theorem bridge is documented in the theorem card; review provenance is external",
        },
        "valid": valid,
    }


def render_markdown(certificate: dict[str, object]) -> str:
    return "\n".join([
        "# 固定 QP Signed-State PWA exact 证书",
        "",
        f"状态：`{certificate['status']}`；复核：`{certificate['review_status']}`。",
        "",
        f"- gamma：`{certificate['gamma']}`",
        f"- 旧 (SG) gate 的 a/b bounds 均 exact 失败：`{certificate['gate_exterior']['a_bound_fails'] and certificate['gate_exterior']['b_bound_fails']}`",
        f"- 原 ADMM 消元与 signed recurrence 一致：`{all(x['matches_original_admm_elimination'] for x in certificate['jacobians'])}`",
        f"- 四个 Jacobians 严格收缩：`{all(x['contraction_check']['positive'] for x in certificate['jacobians'])}`",
        f"- 16 条 edge/signed 变换恒等式：`{all(x['equals_signed_jacobian'] for x in certificate['edge_relations'])}`",
        f"- 相邻 facet 连续性：`{all(x['continuous'] for x in certificate['facet_checks'])}`",
        "",
        "机器证书认证 exact 代数；全局增量与 KKT 桥见已完成独立复核的中文定理卡。",
        "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    certificate = build_certificate()
    if not certificate["valid"]:
        raise SystemExit(2)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(certificate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(certificate), encoding="utf-8")


if __name__ == "__main__":
    main()
