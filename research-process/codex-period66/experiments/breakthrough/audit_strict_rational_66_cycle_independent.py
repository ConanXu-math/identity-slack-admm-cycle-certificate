from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


def _canonical_hash(values: list[sp.Expr]) -> str:
    payload = "\n".join(sp.sstr(value) for value in values).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _matrix_strings(matrix: sp.Matrix) -> list[list[str]]:
    return [
        [sp.sstr(matrix[row, column]) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _positive_part(vector: sp.Matrix) -> sp.Matrix:
    """Project an exact rational vector onto the nonnegative orthant."""
    return sp.Matrix([value if value > 0 else sp.S.Zero for value in vector])


def _raw_step(
    state: sp.Matrix,
    q1_matrix: sp.Matrix,
    q2_matrix: sp.Matrix,
    rhs: sp.Matrix,
    c1: sp.Matrix,
    c2: sp.Matrix,
    target_selector: sp.Matrix | None,
) -> dict[str, sp.Matrix]:
    """Apply one full-state ADMM step.

    A selector is used only while constructing a fixed affine branch.  Passing
    ``None`` applies the genuine orthant projection from the exact signs of the
    newly computed projection argument.
    """
    identity = sp.eye(2)
    y_state = state[:2, 0]
    z_state = state[2:4, 0]
    lambda_state = state[4:6, 0]

    x_next = (q1_matrix + identity).inv() * (
        lambda_state - y_state - z_state + rhs - c1
    )
    y_next = (q2_matrix + identity).inv() * (
        lambda_state - x_next - z_state + rhs - c2
    )
    projection_argument = rhs - x_next - y_next + lambda_state
    z_next = (
        _positive_part(projection_argument)
        if target_selector is None
        else target_selector * projection_argument
    )
    residual = x_next + y_next + z_next - rhs
    lambda_next = lambda_state - residual
    next_state = y_next.col_join(z_next).col_join(lambda_next)
    return {
        "x_next": x_next,
        "y_next": y_next,
        "z_next": z_next,
        "lambda_next": lambda_next,
        "projection_argument": projection_argument,
        "residual": residual,
        "next_state": next_state,
    }


def _affine_lift(
    q1_matrix: sp.Matrix,
    q2_matrix: sp.Matrix,
    rhs: sp.Matrix,
    c1: sp.Matrix,
    c2: sp.Matrix,
    target_selector: sp.Matrix,
) -> sp.Matrix:
    """Build a raw-state affine lift by exact basis evaluation."""
    state_dimension = 6
    zero_state = sp.zeros(state_dimension, 1)
    offset = _raw_step(
        zero_state,
        q1_matrix,
        q2_matrix,
        rhs,
        c1,
        c2,
        target_selector,
    )["next_state"]
    columns: list[sp.Matrix] = []
    for column in range(state_dimension):
        basis_state = sp.zeros(state_dimension, 1)
        basis_state[column] = 1
        basis_image = _raw_step(
            basis_state,
            q1_matrix,
            q2_matrix,
            rhs,
            c1,
            c2,
            target_selector,
        )["next_state"]
        columns.append(basis_image - offset)
    linear_part = sp.Matrix.hstack(*columns)
    return linear_part.row_join(offset).col_join(
        sp.zeros(1, state_dimension).row_join(sp.ones(1, 1))
    )


def _periodic_initial(lifts: dict[int, sp.Matrix], word: tuple[int, ...]) -> tuple[sp.Matrix, sp.Expr]:
    """Solve the full raw-state period map using target-phase selectors."""
    period_lift = sp.eye(7)
    target_word = word[1:] + word[:1]
    for target_bit in target_word:
        period_lift = lifts[target_bit] * period_lift
    period_matrix = period_lift[:6, :6]
    period_offset = period_lift[:6, 6]
    fixed_system = sp.eye(6) - period_matrix
    return fixed_system.inv() * period_offset, fixed_system.det()


def _audit_cycle(
    initial: sp.Matrix,
    q1_matrix: sp.Matrix,
    q2_matrix: sp.Matrix,
    rhs: sp.Matrix,
    c1: sp.Matrix,
    c2: sp.Matrix,
    word: tuple[int, ...],
) -> dict[str, object]:
    identity = sp.eye(2)
    selectors = {0: sp.diag(0, 0), 1: sp.diag(0, 1)}
    states = [initial]
    x_updates: list[sp.Matrix] = []
    margins: list[sp.Expr] = []
    source_decomposition_checks: list[bool] = []
    x_optimality_checks: list[bool] = []
    y_optimality_checks: list[bool] = []
    projection_checks: list[bool] = []
    raw_itinerary_checks: list[bool] = []
    multiplier_checks: list[bool] = []

    current = initial
    closing_state = initial
    for phase, source_bit in enumerate(word):
        source_selector = selectors[source_bit]
        target_bit = word[(phase + 1) % len(word)]
        target_selector = selectors[target_bit]
        y_state = current[:2, 0]
        z_state = current[2:4, 0]
        lambda_state = current[4:6, 0]
        signed_projection_state = z_state + lambda_state

        source_decomposition_checks.append(
            z_state == source_selector * signed_projection_state
            and lambda_state
            == (identity - source_selector) * signed_projection_state
        )
        margins.extend(
            [
                -signed_projection_state[0],
                signed_projection_state[1]
                if source_bit
                else -signed_projection_state[1],
            ]
        )

        update = _raw_step(
            current,
            q1_matrix,
            q2_matrix,
            rhs,
            c1,
            c2,
            None,
        )
        x_next = update["x_next"]
        y_next = update["y_next"]
        z_next = update["z_next"]
        lambda_next = update["lambda_next"]
        projection_argument = update["projection_argument"]
        next_state = update["next_state"]
        x_updates.append(x_next)

        x_optimality_checks.append(
            (q1_matrix + identity) * x_next
            == lambda_state - y_state - z_state + rhs - c1
        )
        y_optimality_checks.append(
            (q2_matrix + identity) * y_next
            == lambda_state - x_next - z_state + rhs - c2
        )
        actual_target_mask = tuple(
            1 if value > 0 else 0 for value in projection_argument
        )
        raw_itinerary_checks.append(actual_target_mask == (0, target_bit))
        projection_checks.append(
            z_next == _positive_part(projection_argument)
            and all(value >= 0 for value in z_next)
            and lambda_next
            == projection_argument - _positive_part(projection_argument)
            and all(value <= 0 for value in lambda_next)
            and (z_next.T * lambda_next)[0] == 0
        )
        multiplier_checks.append(
            lambda_next
            == lambda_state - (x_next + y_next + z_next - rhs)
        )

        closing_state = next_state
        if phase + 1 < len(word):
            states.append(next_state)
        current = next_state

    return {
        "states": states,
        "x_updates": x_updates,
        "closing_state": closing_state,
        "margins": margins,
        "source_decomposition_checks": source_decomposition_checks,
        "x_optimality_checks": x_optimality_checks,
        "y_optimality_checks": y_optimality_checks,
        "projection_checks": projection_checks,
        "raw_itinerary_checks": raw_itinerary_checks,
        "multiplier_checks": multiplier_checks,
    }


def run(
    mu: sp.Rational = sp.Rational(8957, 10000),
    nu: sp.Rational = sp.Rational(999, 1000),
) -> dict[str, object]:
    identity = sp.eye(2)
    epsilon = sp.Rational(1, 1000)
    first_direction = sp.Matrix([-1, 20])
    second_direction = sp.Matrix([-1, 10])
    m_input = epsilon * identity + (mu - epsilon) * (
        first_direction * first_direction.T
    ) / 401
    n_input = epsilon * identity + (nu - epsilon) * (
        second_direction * second_direction.T
    ) / 101
    q1_matrix = m_input.inv() - identity
    q2_matrix = n_input.inv() - identity

    rhs = sp.Matrix([0, 1])
    c1 = sp.Matrix([-1, 0])
    c2 = sp.Matrix([-1, 0])
    zero = sp.zeros(2, 1)
    x_shift = q1_matrix.inv() * c1
    y_shift = q2_matrix.inv() * c2
    zero_linear_rhs = rhs + x_shift + y_shift
    word = (0, 0) + (1,) * 64
    selectors = {0: sp.diag(0, 0), 1: sp.diag(0, 1)}

    linear_lifts = {
        bit: _affine_lift(q1_matrix, q2_matrix, rhs, c1, c2, selector)
        for bit, selector in selectors.items()
    }
    zero_linear_lifts = {
        bit: _affine_lift(
            q1_matrix,
            q2_matrix,
            zero_linear_rhs,
            zero,
            zero,
            selector,
        )
        for bit, selector in selectors.items()
    }
    linear_initial, linear_fixed_determinant = _periodic_initial(
        linear_lifts, word
    )
    zero_linear_initial, zero_linear_fixed_determinant = _periodic_initial(
        zero_linear_lifts, word
    )
    linear_audit = _audit_cycle(
        linear_initial, q1_matrix, q2_matrix, rhs, c1, c2, word
    )
    zero_linear_audit = _audit_cycle(
        zero_linear_initial,
        q1_matrix,
        q2_matrix,
        zero_linear_rhs,
        zero,
        zero,
        word,
    )

    translated_initial = linear_initial.copy()
    translated_initial[:2, 0] += y_shift
    state_conjugacy_checks: list[bool] = []
    x_conjugacy_checks: list[bool] = []
    for phase in range(len(word)):
        translated_state = linear_audit["states"][phase].copy()
        translated_state[:2, 0] += y_shift
        state_conjugacy_checks.append(
            translated_state == zero_linear_audit["states"][phase]
        )
        x_conjugacy_checks.append(
            linear_audit["x_updates"][phase] + x_shift
            == zero_linear_audit["x_updates"][phase]
        )

    kkt_linear_state = zero.col_join(rhs).col_join(c1)
    kkt_zero_linear_state = y_shift.col_join(rhs).col_join(c1)
    linear_margins = linear_audit["margins"]
    zero_linear_margins = zero_linear_audit["margins"]
    minimum_margin = min(linear_margins)
    first_return_checks = [
        linear_audit["states"][phase] != linear_initial
        for phase in range(1, len(word))
    ]

    checks = {
        "Q1_positive_definite": q1_matrix[0, 0] > 0
        and q1_matrix.det() > 0,
        "Q2_positive_definite": q2_matrix[0, 0] > 0
        and q2_matrix.det() > 0,
        "subproblem_inverse_M_matches_input": (q1_matrix + identity).inv()
        == m_input,
        "subproblem_inverse_N_matches_input": (q2_matrix + identity).inv()
        == n_input,
        "linear_kkt_primal_feasibility": zero + zero + rhs == rhs,
        "linear_kkt_stationarity": q1_matrix * zero + c1 == c1
        and q2_matrix * zero + c2 == c1,
        "linear_kkt_complementarity": all(value >= 0 for value in rhs)
        and all(value <= 0 for value in c1)
        and (rhs.T * c1)[0] == 0,
        "zero_linear_kkt_primal_feasibility": x_shift
        + y_shift
        + rhs
        == zero_linear_rhs,
        "zero_linear_kkt_stationarity": q1_matrix * x_shift == c1
        and q2_matrix * y_shift == c1,
        "linear_period_system_invertible": linear_fixed_determinant != 0,
        "zero_linear_period_system_invertible": zero_linear_fixed_determinant
        != 0,
        "translated_initial_matches": translated_initial == zero_linear_initial,
        "all_state_conjugacies_exact": all(state_conjugacy_checks),
        "all_x_conjugacies_exact": all(x_conjugacy_checks),
        "linear_cycle_closes": linear_audit["closing_state"]
        == linear_initial,
        "zero_linear_cycle_closes": zero_linear_audit["closing_state"]
        == zero_linear_initial,
        "all_source_decompositions_exact": all(
            linear_audit["source_decomposition_checks"]
        )
        and all(zero_linear_audit["source_decomposition_checks"]),
        "all_x_subproblems_exact": all(linear_audit["x_optimality_checks"])
        and all(zero_linear_audit["x_optimality_checks"]),
        "all_y_subproblems_exact": all(linear_audit["y_optimality_checks"])
        and all(zero_linear_audit["y_optimality_checks"]),
        "all_projection_steps_exact": all(linear_audit["projection_checks"])
        and all(zero_linear_audit["projection_checks"]),
        "raw_projection_itinerary_matches_word": all(
            linear_audit["raw_itinerary_checks"]
        )
        and all(zero_linear_audit["raw_itinerary_checks"]),
        "all_multiplier_steps_exact": all(linear_audit["multiplier_checks"])
        and all(zero_linear_audit["multiplier_checks"]),
        "all_strict_itinerary_margins": all(
            margin > 0 for margin in linear_margins + zero_linear_margins
        ),
        "uniform_margin_gt_1_over_1000": all(
            margin > sp.Rational(1, 1000)
            for margin in linear_margins + zero_linear_margins
        ),
        "linear_and_zero_linear_margins_match": linear_margins
        == zero_linear_margins,
        "linear_cycle_is_non_kkt": linear_initial != kkt_linear_state,
        "zero_linear_cycle_is_non_kkt": zero_linear_initial
        != kkt_zero_linear_state,
        "no_earlier_return_before_66": all(first_return_checks),
    }

    minimum_margin_index = linear_margins.index(minimum_margin)
    valid = all(checks.values())
    return {
        "status": "independent_exact_raw_admm_audit_passed"
        if valid
        else "independent_exact_raw_admm_audit_failed",
        "scope": "full-state exact audit of the strict rational period-66 orbit in both linear and zero-linear formulations",
        "implementation_boundary": "This module does not import or call certify_strict_rational_66_cycle.py, does not use its signed-state recurrence, and applies the orthant projection from exact signs rather than a preset mask during the cycle audit.",
        "period": len(word),
        "word_run_length_encoding": [[0, 2], [1, 64]],
        "design_parameters": {
            "epsilon": sp.sstr(epsilon),
            "mu": sp.sstr(mu),
            "nu": sp.sstr(nu),
        },
        "checks": {name: bool(value) for name, value in checks.items()},
        "minimum_margin_decimal": str(sp.N(minimum_margin, 18)),
        "minimum_margin_phase": minimum_margin_index // 2,
        "minimum_margin_coordinate": minimum_margin_index % 2,
        "linear_initial_full_state_decimal": [
            str(sp.N(value, 18)) for value in linear_initial
        ],
        "zero_linear_initial_full_state_decimal": [
            str(sp.N(value, 18)) for value in zero_linear_initial
        ],
        "exact_problem_data": {
            "Q1": _matrix_strings(q1_matrix),
            "Q2": _matrix_strings(q2_matrix),
            "zero_linear_rhs": _matrix_strings(zero_linear_rhs),
            "zero_linear_kkt_x": _matrix_strings(x_shift),
            "zero_linear_kkt_y": _matrix_strings(y_shift),
            "zero_linear_kkt_z": _matrix_strings(rhs),
            "zero_linear_kkt_lambda": _matrix_strings(c1),
        },
        "exact_hashes": {
            "linear_initial_full_state": _canonical_hash(list(linear_initial)),
            "zero_linear_initial_full_state": _canonical_hash(
                list(zero_linear_initial)
            ),
            "minimum_margin": _canonical_hash([minimum_margin]),
        },
        "claim_boundary": "The exact bounded non-KKT orbit refutes unconditional global convergence. It is not a claim of unbounded divergence or external independent review.",
        "valid": valid,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "outputs/breakthrough_attempts/"
            "stage45_independent_raw_admm_audit/certificate.json"
        ),
    )
    args = parser.parse_args()
    payload = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"valid": payload["valid"]}, sort_keys=True))


if __name__ == "__main__":
    main()
