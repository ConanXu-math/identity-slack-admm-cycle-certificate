from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


def _canonical_hash(values: list[sp.Expr]) -> str:
    payload = "\n".join(sp.sstr(value) for value in values).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def run(
    mu: sp.Rational = sp.Rational(8957, 10000),
    nu: sp.Rational = sp.Rational(999, 1000),
) -> dict[str, object]:
    identity = sp.eye(2)
    epsilon = sp.Rational(1, 1000)
    first_direction = sp.Matrix([-1, 20])
    second_direction = sp.Matrix([-1, 10])
    m_matrix = epsilon * identity + (mu - epsilon) * (
        first_direction * first_direction.T
    ) / 401
    n_matrix = epsilon * identity + (nu - epsilon) * (
        second_direction * second_direction.T
    ) / 101
    q1_matrix = m_matrix.inv() - identity
    q2_matrix = n_matrix.inv() - identity

    rhs = sp.Matrix([0, 1])
    c1 = sp.Matrix([-1, 0])
    c2 = sp.Matrix([-1, 0])
    recurrence_offset = (identity - m_matrix) * rhs + m_matrix * c1 - c2
    affine_offset = (n_matrix * recurrence_offset).col_join(
        (identity - n_matrix) * recurrence_offset + c2
    )

    branch_matrices: list[sp.Matrix] = []
    lifts: list[sp.Matrix] = []
    for bit in (0, 1):
        selector = sp.diag(0, bit)
        sign = 2 * selector - identity
        branch = sp.BlockMatrix(
            [
                [
                    n_matrix * m_matrix,
                    -n_matrix * (identity - m_matrix) * sign,
                ],
                [
                    (identity - n_matrix) * m_matrix,
                    selector
                    - (identity - n_matrix) * (identity - m_matrix) * sign,
                ],
            ]
        ).as_explicit()
        lift = branch.row_join(affine_offset).col_join(
            sp.zeros(1, 4).row_join(sp.ones(1, 1))
        )
        branch_matrices.append(branch)
        lifts.append(lift)

    word = (0, 0) + (1,) * 64
    period_lift = lifts[1] ** 64 * lifts[0] ** 2
    period_matrix = period_lift[:4, :4]
    period_offset = period_lift[:4, 4]
    fixed_system = sp.eye(4) - period_matrix
    signed_initial = fixed_system.inv() * period_offset

    signed_states = [signed_initial]
    margins: list[sp.Expr] = []
    branch_recurrence_checks: list[bool] = []
    for phase, bit in enumerate(word):
        state = signed_states[-1]
        margins.extend([-state[2], state[3] if bit else -state[3]])
        lifted_next = lifts[bit] * state.col_join(sp.ones(1, 1))
        next_state = lifted_next[:4, 0]
        branch_recurrence_checks.append(
            next_state == branch_matrices[bit] * state + affine_offset
        )
        if phase + 1 < len(word):
            signed_states.append(next_state)
    signed_return = (
        lifts[word[-1]] * signed_states[-1].col_join(sp.ones(1, 1))
    )[:4, 0]

    direct_step_checks: list[bool] = []
    x_states: list[sp.Matrix] = []
    for phase in range(len(word)):
        previous = signed_states[(phase - 1) % len(word)]
        previous_y = previous[:2, 0]
        previous_q = previous[2:, 0]
        previous_abs_q = previous_q.applyfunc(abs)
        x_state = m_matrix * (-previous_y - previous_abs_q + rhs - c1)
        x_states.append(x_state)

    for phase, bit in enumerate(word):
        next_phase = (phase + 1) % len(word)
        state = signed_states[phase]
        y_state = state[:2, 0]
        q_state = state[2:, 0]
        source_selector = sp.diag(0, bit)
        target_selector = sp.diag(0, word[next_phase])
        z_state = source_selector * q_state
        lambda_state = (identity - source_selector) * q_state

        x_next = m_matrix * (
            lambda_state - y_state - z_state + rhs - c1
        )
        y_next = n_matrix * (
            lambda_state - x_next - z_state + rhs - c2
        )
        q_next = rhs - x_next - y_next + lambda_state
        z_next = target_selector * q_next
        residual = x_next + y_next + z_next - rhs
        lambda_next = lambda_state - residual
        expected_next = signed_states[next_phase]
        direct_step_checks.append(
            x_next == x_states[next_phase]
            and y_next == expected_next[:2, 0]
            and q_next == expected_next[2:, 0]
            and z_next == target_selector * expected_next[2:, 0]
            and lambda_next
            == (identity - target_selector) * expected_next[2:, 0]
        )

    x_star = sp.zeros(2, 1)
    y_star = sp.zeros(2, 1)
    z_star = rhs
    lambda_star = c1
    x_shift = q1_matrix.inv() * c1
    y_shift = q2_matrix.inv() * c2
    zero_linear_rhs = rhs + x_shift + y_shift
    zero_linear_direct_step_checks: list[bool] = []
    for phase, bit in enumerate(word):
        next_phase = (phase + 1) % len(word)
        state = signed_states[phase]
        y_state = state[:2, 0] + y_shift
        q_state = state[2:, 0]
        source_selector = sp.diag(0, bit)
        target_selector = sp.diag(0, word[next_phase])
        z_state = source_selector * q_state
        lambda_state = (identity - source_selector) * q_state

        x_next = m_matrix * (
            lambda_state - y_state - z_state + zero_linear_rhs
        )
        y_next = n_matrix * (
            lambda_state - x_next - z_state + zero_linear_rhs
        )
        q_next = zero_linear_rhs - x_next - y_next + lambda_state
        z_next = target_selector * q_next
        residual = x_next + y_next + z_next - zero_linear_rhs
        lambda_next = lambda_state - residual
        expected_next = signed_states[next_phase]
        zero_linear_direct_step_checks.append(
            x_next == x_states[next_phase] + x_shift
            and y_next == expected_next[:2, 0] + y_shift
            and q_next == expected_next[2:, 0]
            and z_next == target_selector * expected_next[2:, 0]
            and lambda_next
            == (identity - target_selector) * expected_next[2:, 0]
        )
    proper_divisors = [divisor for divisor in range(1, 66) if 66 % divisor == 0]
    checks = {
        "M_spectrum": set(m_matrix.eigenvals()) == {epsilon, mu},
        "N_spectrum": set(n_matrix.eigenvals()) == {epsilon, nu},
        "Q1_positive_definite": q1_matrix[0, 0] > 0 and q1_matrix.det() > 0,
        "Q2_positive_definite": q2_matrix[0, 0] > 0 and q2_matrix.det() > 0,
        "kkt_primal_feasibility": x_star + y_star + z_star == rhs,
        "kkt_x_stationarity": q1_matrix * x_star + c1 == lambda_star,
        "kkt_y_stationarity": q2_matrix * y_star + c2 == lambda_star,
        "kkt_strict_complementarity": z_star[1] > 0 and lambda_star[0] < 0,
        "zero_linear_kkt_primal_feasibility": x_shift
        + y_shift
        + z_star
        == zero_linear_rhs,
        "zero_linear_kkt_x_stationarity": q1_matrix * x_shift
        == lambda_star,
        "zero_linear_kkt_y_stationarity": q2_matrix * y_shift
        == lambda_star,
        "period_system_invertible": fixed_system.det() != 0,
        "signed_period_closure": signed_return == signed_initial,
        "all_branch_recurrences_exact": all(branch_recurrence_checks),
        "all_strict_itinerary_margins": all(margin > 0 for margin in margins),
        "uniform_margin_gt_1_over_1000": all(
            margin > sp.Rational(1, 1000) for margin in margins
        ),
        "all_original_admm_steps_exact": all(direct_step_checks),
        "all_zero_linear_original_admm_steps_exact": all(
            zero_linear_direct_step_checks
        ),
        "non_kkt_cycle": signed_initial
        != y_star.col_join(z_star + lambda_star),
        "word_has_minimal_period_66": all(
            any(word[index] != word[index % divisor] for index in range(66))
            for divisor in proper_divisors
        ),
    }
    minimum_margin = min(margins)
    minimum_phase_coordinate = margins.index(minimum_margin)
    return {
        "status": "proof_grade_strict_rational_66_cycle_counterexample",
        "scope": "pure strongly convex rational A=B=I two-dimensional slack QP (zero linear terms after exact translation)",
        "period": 66,
        "word_run_length_encoding": [[0, 2], [1, 64]],
        "design_parameters": {
            "epsilon": sp.sstr(epsilon),
            "mu": sp.sstr(mu),
            "nu": sp.sstr(nu),
        },
        "checks": {key: bool(value) for key, value in checks.items()},
        "minimum_margin_decimal": str(sp.N(minimum_margin, 18)),
        "minimum_margin_phase": minimum_phase_coordinate // 2,
        "minimum_margin_coordinate": minimum_phase_coordinate % 2,
        "signed_initial_decimal": [str(sp.N(value, 18)) for value in signed_initial],
        "exact_hashes": {
            "M": _canonical_hash(list(m_matrix)),
            "N": _canonical_hash(list(n_matrix)),
            "signed_initial": _canonical_hash(list(signed_initial)),
            "minimum_margin": _canonical_hash([minimum_margin]),
        },
        "claim_boundary": "This is an exact bounded non-KKT 66-cycle of the original direct three-block slack ADMM. It refutes unconditional global convergence, but does not claim unbounded iterates.",
        "valid": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "outputs/breakthrough_attempts/stage44_strict_rational_66_cycle/certificate.json"
        ),
    )
    args = parser.parse_args()
    payload = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"valid": payload["valid"]}, sort_keys=True))


if __name__ == "__main__":
    main()
