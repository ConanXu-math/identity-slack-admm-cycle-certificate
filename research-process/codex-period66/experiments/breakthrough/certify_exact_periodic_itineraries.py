from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import sympy as sp
from sympy.solvers.simplex import InfeasibleLPError, linprog


Mask = tuple[int, ...]


def rational_problem() -> dict[str, sp.Matrix | sp.Rational]:
    return {
        "q1": sp.Matrix([[sp.Rational(7, 5), sp.Rational(1, 5)], [sp.Rational(1, 5), sp.Rational(9, 5)]]),
        "q2": sp.Matrix([[sp.Rational(6, 5)]]),
        "a": sp.Matrix([[sp.Rational(2, 5), 1], [1, sp.Rational(-1, 5)]]),
        "b": sp.Matrix([[sp.Rational(4, 5)], [sp.Rational(-1, 2)]]),
        "rhs": sp.Matrix([sp.Rational(1, 5), sp.Rational(-7, 10)]),
        "beta": sp.Rational(9, 10),
    }


def singular_boundary_problem() -> dict[str, sp.Matrix | sp.Rational]:
    """Convex scalar boundary case with unique ADMM subproblem minimizers."""
    return {
        "q1": sp.zeros(1),
        "q2": sp.zeros(1),
        "a": sp.eye(1),
        "b": sp.eye(1),
        "rhs": sp.Matrix([1]),
        "beta": sp.Rational(1),
    }


def mask_matrices(mask: Mask, dim_y: int) -> tuple[sp.Matrix, sp.Matrix]:
    d_matrix = sp.diag(*mask)
    sign = sp.diag(*[1 if value else -1 for value in mask])
    g_matrix = sp.diag(*([1] * dim_y + [1 if value else -1 for value in mask]))
    return d_matrix, g_matrix


def affine_factors(problem: dict[str, sp.Matrix | sp.Rational], source: Mask) -> tuple[sp.Matrix, sp.Matrix]:
    q1 = problem["q1"]
    q2 = problem["q2"]
    a = problem["a"]
    bmat = problem["b"]
    rhs = problem["rhs"]
    beta = problem["beta"]
    assert isinstance(q1, sp.MatrixBase)
    assert isinstance(q2, sp.MatrixBase)
    assert isinstance(a, sp.MatrixBase)
    assert isinstance(bmat, sp.MatrixBase)
    assert isinstance(rhs, sp.MatrixBase)
    assert isinstance(beta, sp.Rational)

    h_x = q1 + beta * a.T * a
    h_y = q2 + beta * bmat.T * bmat
    m_x = beta * a * h_x.inv() * a.T
    n_y = beta * bmat * h_y.inv() * bmat.T
    y_solver = beta * h_y.inv() * bmat.T
    identity = sp.eye(rhs.rows)
    source_d, _ = mask_matrices(source, q2.rows)
    k_source = sp.Matrix.vstack(
        sp.Matrix.hstack(y_solver * m_x * bmat, -y_solver * (identity - m_x)),
        sp.Matrix.hstack(
            (identity - n_y) * m_x * bmat,
            n_y + (identity - n_y) * m_x - (identity - source_d),
        ),
    )
    offset = sp.Matrix.vstack(
        y_solver * (identity - m_x) * rhs,
        (identity - n_y) * (identity - m_x) * rhs,
    )
    return k_source, offset


def transition(problem: dict[str, sp.Matrix | sp.Rational], source: Mask, target: Mask) -> tuple[sp.Matrix, sp.Matrix]:
    q2 = problem["q2"]
    assert isinstance(q2, sp.MatrixBase)
    k_source, offset = affine_factors(problem, source)
    _, g_target = mask_matrices(target, q2.rows)
    return g_target * k_source, g_target * offset


def compose_word(problem: dict[str, sp.Matrix | sp.Rational], word: tuple[Mask, ...]) -> tuple[sp.Matrix, sp.Matrix]:
    q2 = problem["q2"]
    rhs = problem["rhs"]
    assert isinstance(q2, sp.MatrixBase)
    assert isinstance(rhs, sp.MatrixBase)
    size = q2.rows + rhs.rows
    product = sp.eye(size)
    offset = sp.zeros(size, 1)
    for step, source in enumerate(word):
        target = word[(step + 1) % len(word)]
        matrix, edge_offset = transition(problem, source, target)
        offset = matrix * offset + edge_offset
        product = matrix * product
    return product, offset


def exact_edge_checks(
    problem: dict[str, sp.Matrix | sp.Rational],
    word: tuple[Mask, ...],
    basepoint: sp.Matrix,
) -> tuple[bool, list[dict[str, object]]]:
    q2 = problem["q2"]
    rhs = problem["rhs"]
    assert isinstance(q2, sp.MatrixBase)
    assert isinstance(rhs, sp.MatrixBase)
    dim_y = q2.rows
    dim_m = rhs.rows
    state = basepoint
    records: list[dict[str, object]] = []
    all_valid = True

    for step, source in enumerate(word):
        target = word[(step + 1) % len(word)]
        k_source, common_offset = affine_factors(problem, source)
        q_value = k_source[dim_y:, :] * state + common_offset[dim_y:, :]
        u_value = state[dim_y:, :]
        checks: list[dict[str, object]] = []
        for index in range(dim_m):
            source_value = sp.factor(u_value[index])
            source_valid = bool(source_value > 0) if source[index] else bool(source_value >= 0)
            checks.append(
                {
                    "label": f"source_u[{index}]",
                    "strict": bool(source[index]),
                    "value": str(source_value),
                    "valid": source_valid,
                }
            )
            target_value = sp.factor(q_value[index] if target[index] else -q_value[index])
            target_valid = bool(target_value > 0) if target[index] else bool(target_value >= 0)
            checks.append(
                {
                    "label": f"target_q[{index}]",
                    "strict": bool(target[index]),
                    "value": str(target_value),
                    "valid": target_valid,
                }
            )
        phase_valid = all(bool(item["valid"]) for item in checks)
        all_valid = all_valid and phase_valid
        records.append(
            {
                "step": step,
                "source": list(source),
                "target": list(target),
                "state": [str(sp.factor(value)) for value in state],
                "q": [str(sp.factor(value)) for value in q_value],
                "checks": checks,
                "valid": phase_valid,
            }
        )
        matrix, edge_offset = transition(problem, source, target)
        state = matrix * state + edge_offset
    return all_valid, records


def periodic_cell_rows(
    problem: dict[str, sp.Matrix | sp.Rational],
    word: tuple[Mask, ...],
) -> list[dict[str, object]]:
    """Pull every canonical half-space back to the initial reduced state."""
    q2 = problem["q2"]
    rhs = problem["rhs"]
    assert isinstance(q2, sp.MatrixBase)
    assert isinstance(rhs, sp.MatrixBase)
    dim_y, dim_m = q2.rows, rhs.rows
    size = dim_y + dim_m
    state_matrix = sp.eye(size)
    state_offset = sp.zeros(size, 1)
    rows: list[dict[str, object]] = []

    for step, source in enumerate(word):
        target = word[(step + 1) % len(word)]
        k_source, common_offset = affine_factors(problem, source)
        q_matrix = k_source[dim_y:, :] * state_matrix
        q_offset = k_source[dim_y:, :] * state_offset + common_offset[dim_y:, :]
        u_matrix = state_matrix[dim_y:, :]
        u_offset = state_offset[dim_y:, :]
        for index in range(dim_m):
            rows.append(
                {
                    "label": f"step_{step}_source_u_{index}",
                    "row": u_matrix[index, :],
                    "constant": u_offset[index],
                    "strict": bool(source[index]),
                }
            )
            target_sign = 1 if target[index] else -1
            rows.append(
                {
                    "label": f"step_{step}_target_q_{index}",
                    "row": target_sign * q_matrix[index, :],
                    "constant": target_sign * q_offset[index],
                    "strict": bool(target[index]),
                }
            )
        edge_matrix, edge_offset = transition(problem, source, target)
        state_offset = edge_matrix * state_offset + edge_offset
        state_matrix = edge_matrix * state_matrix
    return rows


def _farkas_infeasibility_certificate(
    inequality_matrix: sp.Matrix,
    inequality_rhs: sp.Matrix,
    equality_matrix: sp.Matrix,
    equality_rhs: sp.Matrix,
) -> dict[str, object]:
    inequality_count = inequality_matrix.rows
    equality_count = equality_matrix.rows
    stationarity = inequality_matrix.T.row_join(equality_matrix.T).row_join(-equality_matrix.T)
    gap_row = inequality_rhs.T.row_join(equality_rhs.T).row_join(-equality_rhs.T)
    certificate_matrix = stationarity.col_join(gap_row)
    certificate_rhs = sp.zeros(stationarity.rows, 1).col_join(sp.Matrix([-1]))
    dual_size = inequality_count + 2 * equality_count
    _, solution = linprog(
        sp.zeros(1, dual_size),
        A=sp.zeros(1, dual_size),
        b=sp.zeros(1, 1),
        A_eq=certificate_matrix,
        b_eq=certificate_rhs,
    )
    vector = sp.Matrix(solution)
    y = vector[:inequality_count, :]
    nu = (
        vector[inequality_count : inequality_count + equality_count, :]
        - vector[inequality_count + equality_count :, :]
    )
    stationarity_gap = sp.simplify(inequality_matrix.T * y + equality_matrix.T * nu)
    contradiction_gap = sp.factor((inequality_rhs.T * y + equality_rhs.T * nu)[0])
    valid = bool(
        all(value >= 0 for value in y)
        and stationarity_gap == sp.zeros(inequality_matrix.cols, 1)
        and contradiction_gap == -1
    )
    return {
        "inequality_weights": [str(sp.factor(value)) for value in y],
        "equality_weights": [str(sp.factor(value)) for value in nu],
        "stationarity_gap": [str(sp.factor(value)) for value in stationarity_gap],
        "contradiction_gap": str(contradiction_gap),
        "valid": valid,
    }


def _zero_margin_dual_certificate(
    inequality_matrix: sp.Matrix,
    inequality_rhs: sp.Matrix,
    equality_matrix: sp.Matrix,
    equality_rhs: sp.Matrix,
) -> dict[str, object]:
    inequality_count = inequality_matrix.rows
    equality_count = equality_matrix.rows
    target = sp.zeros(inequality_matrix.cols, 1)
    target[-1] = 1
    dual_equalities = (
        inequality_matrix.T.row_join(equality_matrix.T).row_join(-equality_matrix.T)
    )
    objective = inequality_rhs.T.row_join(equality_rhs.T).row_join(-equality_rhs.T)
    dual_size = inequality_count + 2 * equality_count
    optimum, solution = linprog(
        objective,
        A=sp.zeros(1, dual_size),
        b=sp.zeros(1, 1),
        A_eq=dual_equalities,
        b_eq=target,
    )
    vector = sp.Matrix(solution)
    y = vector[:inequality_count, :]
    nu = (
        vector[inequality_count : inequality_count + equality_count, :]
        - vector[inequality_count + equality_count :, :]
    )
    stationarity_gap = sp.simplify(inequality_matrix.T * y + equality_matrix.T * nu - target)
    upper_bound = sp.factor((inequality_rhs.T * y + equality_rhs.T * nu)[0])
    valid = bool(
        all(value >= 0 for value in y)
        and stationarity_gap == sp.zeros(inequality_matrix.cols, 1)
        and upper_bound == 0
        and optimum == 0
    )
    return {
        "inequality_weights": [str(sp.factor(value)) for value in y],
        "equality_weights": [str(sp.factor(value)) for value in nu],
        "stationarity_gap": [str(sp.factor(value)) for value in stationarity_gap],
        "strict_margin_upper_bound": str(upper_bound),
        "valid": valid,
    }


def certify_singular_periodic_cell(
    problem: dict[str, sp.Matrix | sp.Rational],
    word: tuple[Mask, ...],
    periodicity: sp.Matrix,
    offset: sp.Matrix,
) -> dict[str, object]:
    rows = periodic_cell_rows(problem, word)
    size = periodicity.cols
    strict_count = sum(bool(item["strict"]) for item in rows)
    weak_a = sp.Matrix.vstack(*[-sp.Matrix(item["row"]) for item in rows])
    weak_b = sp.Matrix([sp.factor(item["constant"]) for item in rows])

    margin_a_rows = []
    for item in rows:
        row = list(-sp.Matrix(item["row"])) + [1 if item["strict"] else 0]
        margin_a_rows.append(row)
    margin_a_rows.append([0] * size + [1])
    margin_a = sp.Matrix(margin_a_rows)
    margin_b = weak_b.col_join(sp.Matrix([1]))
    margin_eq = periodicity.row_join(sp.zeros(periodicity.rows, 1))
    margin_objective = sp.Matrix([[0] * size + [-1]])

    try:
        optimum, solution = linprog(
            margin_objective,
            A=margin_a,
            b=margin_b,
            A_eq=margin_eq,
            b_eq=offset,
            bounds=[(None, None)] * size + [(0, 1)],
        )
    except InfeasibleLPError:
        farkas = _farkas_infeasibility_certificate(
            weak_a, weak_b, periodicity, offset
        )
        return {
            "status": "exact_singular_periodic_cell_infeasible_by_farkas",
            "strict_row_count": strict_count,
            "farkas_certificate": farkas,
            "valid": farkas["valid"],
        }

    vector = sp.Matrix(solution)
    basepoint = vector[:size, :]
    margin = sp.factor(vector[-1])
    exact_valid, phases = exact_edge_checks(problem, word, basepoint)
    if strict_count == 0 or margin > 0:
        nonconstant_word = len(set(word)) > 1
        return {
            "status": (
                "exact_nonconstant_periodic_itinerary_witness"
                if nonconstant_word
                else "exact_rational_periodic_itinerary_witness"
            ),
            "nonconstant_word": nonconstant_word,
            "strict_row_count": strict_count,
            "strict_margin": str(margin),
            "basepoint": [str(sp.factor(value)) for value in basepoint],
            "phases": phases,
            "valid": bool(exact_valid and optimum == -margin),
        }

    dual = _zero_margin_dual_certificate(
        margin_a, margin_b, margin_eq, offset
    )
    return {
        "status": "exact_singular_periodic_cell_excluded_by_zero_margin_dual",
        "strict_row_count": strict_count,
        "weak_basepoint": [str(sp.factor(value)) for value in basepoint],
        "strict_margin": str(margin),
        "dual_certificate": dual,
        "valid": bool(margin == 0 and optimum == 0 and dual["valid"]),
    }


def certify_word(problem: dict[str, sp.Matrix | sp.Rational], word: tuple[Mask, ...]) -> dict[str, object]:
    product, offset = compose_word(problem, word)
    periodicity = sp.eye(product.rows) - product
    augmented = periodicity.row_join(offset)
    record: dict[str, object] = {
        "word": [list(mask) for mask in word],
        "periodicity_rank": periodicity.rank(),
        "augmented_rank": augmented.rank(),
        "det_i_minus_p": str(sp.factor(periodicity.det())),
    }
    if periodicity.rank() < augmented.rank():
        record["status"] = "exact_no_periodic_basepoint_by_rank"
        return record
    if periodicity.det() == 0:
        record.update(certify_singular_periodic_cell(problem, word, periodicity, offset))
        return record

    basepoint = periodicity.inv() * offset
    valid, phases = exact_edge_checks(problem, word, basepoint)
    nonconstant_word = len(set(word)) > 1
    record["basepoint"] = [str(sp.factor(value)) for value in basepoint]
    record["phases"] = phases
    record["nonconstant_word"] = nonconstant_word
    record["status"] = (
        (
            "exact_nonconstant_periodic_itinerary_witness"
            if nonconstant_word
            else "exact_rational_periodic_itinerary_witness"
        )
        if valid
        else "exact_unique_periodic_point_violates_edge_cell"
    )
    return record


def run(max_length: int) -> dict[str, object]:
    problem = rational_problem()
    masks = tuple(itertools.product([0, 1], repeat=2))
    records = [
        certify_word(problem, word)
        for length in range(1, max_length + 1)
        for word in itertools.product(masks, repeat=length)
    ]
    counts: dict[str, int] = {}
    for record in records:
        status = str(record["status"])
        counts[status] = counts.get(status, 0) + 1
    basepoints = {
        tuple(record["basepoint"])
        for record in records
        if "basepoint" in record
    }
    inadmissible_basepoints = {
        tuple(record["basepoint"])
        for record in records
        if record["status"] == "exact_unique_periodic_point_violates_edge_cell"
    }
    unit_root_records = [record for record in records if record["det_i_minus_p"] == "0"]
    singular_regression = run_singular_boundary_regression(max_length)
    return {
        "status_label": "exact_rational_periodic_itinerary_certificate",
        "scope": "one fixed rational SPD slack QP plus a scalar convex singular-periodicity regression",
        "max_length": max_length,
        "word_count": len(records),
        "distinct_basepoint_count": len(basepoints),
        "distinct_inadmissible_basepoint_count": len(inadmissible_basepoints),
        "unit_root_word_count": len(unit_root_records),
        "unit_root_words": [record["word"] for record in unit_root_records],
        "counts": counts,
        "records": records,
        "singular_boundary_regression": singular_regression,
        "claim_boundary": [
            "A constant-word periodic basepoint is only an ADMM fixed point, not a counterexample.",
            "A nonconstant exact periodic witness becomes a strict nonconvergence counterexample once convex-QP well-posedness and the canonical full-state lift are checked.",
            "Singular periodicity systems are decided by exact rational LP witnesses or dual certificates.",
            "The result covers only the explicitly recorded rational QP and word lengths.",
        ],
    }


def run_singular_boundary_regression(max_length: int) -> dict[str, object]:
    problem = singular_boundary_problem()
    masks = ((0,), (1,))
    records = [
        certify_word(problem, word)
        for length in range(1, max_length + 1)
        for word in itertools.product(masks, repeat=length)
    ]
    counts: dict[str, int] = {}
    for record in records:
        status = str(record["status"])
        counts[status] = counts.get(status, 0) + 1
    return {
        "scope": "q1=q2=0, A=B=1, rhs=1, beta=1; exact scalar closed words",
        "word_count": len(records),
        "counts": counts,
        "all_singular_words_decided": all(
            "requires_parametric_lp" not in str(record["status"])
            and bool(record.get("valid", True))
            for record in records
        ),
        "records": records,
    }


def write_report(payload: dict[str, object], path: Path) -> None:
    counts = payload["counts"]
    assert isinstance(counts, dict)
    records = payload["records"]
    assert isinstance(records, list)
    witnesses = [
        record
        for record in records
        if record["status"]
        in {
            "exact_rational_periodic_itinerary_witness",
            "exact_nonconstant_periodic_itinerary_witness",
        }
    ]
    lines = [
        "# Exact Rational Periodic Itinerary Certificates",
        "",
        "状态：`exact_certificate_for_fixed_qp_and_finite_words`",
        "",
        "本报告对一个固定有理 SPD slack QP 的 closed mask words 做 exact SymPy 消元；不是数值筛查，也不是严格反例。",
        "",
        f"- max length: `{payload['max_length']}`",
        f"- total words: `{payload['word_count']}`",
        f"- distinct basepoints: `{payload['distinct_basepoint_count']}`",
        f"- distinct inadmissible basepoints: `{payload['distinct_inadmissible_basepoint_count']}`",
        f"- exact unit-root words (det(I-P)=0): `{payload['unit_root_word_count']}`",
    ]
    lines.extend(f"- {key}: `{value}`" for key, value in sorted(counts.items()))
    singular = payload["singular_boundary_regression"]
    assert isinstance(singular, dict)
    lines.extend(
        [
            "",
            "## Singular Periodicity Regression",
            "",
            f"- scalar boundary words: `{singular['word_count']}`",
            f"- all singular words decided: `{singular['all_singular_words_decided']}`",
        ]
    )
    singular_counts = singular["counts"]
    assert isinstance(singular_counts, dict)
    lines.extend(f"- {key}: `{value}`" for key, value in sorted(singular_counts.items()))
    lines.extend(["", "## Exact Witnesses", ""])
    for record in witnesses[:20]:
        lines.append(f"- word `{record['word']}`: basepoint `{record['basepoint']}`")
    if len(witnesses) > 20:
        lines.append(f"- 其余 `{len(witnesses) - 20}` 个 witness 见 JSON。")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- 恒定 word witness 只是 ADMM fixed point，不是反例。",
            "- 非恒定 strict periodic witness 在补齐凸 QP well-posedness 与 full-state lift 后，会直接构成不收敛反例，无需额外谱扩张。",
            "- `inadmissible` 计数按标记 word 统计，不表示同样数量的彼此不同 basepoint。",
            "- 它不证明 expanding ray、Jordan drift、aperiodic stability 或全局收敛。",
            "- 本实例长度不超过上限的 words 若 `unit_root_word_count=0`，则 exact 排除这些 words 的 Jordan/affine-drift 入口；不外推到其他数据或更长 words。",
            "- 奇异周期等式由 exact rational margin LP 与可核查 dual/Farkas 证书处理。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-length", type=int, default=4)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/breakthrough_attempts/stage6_exact_admissibility"),
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = run(args.max_length)
    json_path = args.output_dir / "exact_periodic_itineraries.json"
    report_path = args.output_dir / "exact_periodic_itineraries.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(payload, report_path)
    print(json.dumps(payload["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
