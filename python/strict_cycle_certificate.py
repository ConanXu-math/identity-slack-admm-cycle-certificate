"""Independent exact raw-state certificate for the period-66 ADMM orbit.

This checker solves a six-dimensional affine period equation in the raw state
``(y, z, lambda)``.  The proposed word is used only to construct that equation.
Acceptance is decided afterwards by rerunning the original ADMM update with
the actual componentwise positive-part projection.  This module deliberately
does not import the signed-state checker.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

import sympy as sp


HERE = Path(__file__).resolve().parent
CERTIFICATE_DIR = HERE.parent / "certificates"
INSTANCE_ID = "identity_slack_p66_short_v1"
EPSILON = sp.Rational(1, 1000)
MU = sp.Rational(8957, 10000)
NU = sp.Rational(999, 1000)
PERIOD = 66
MARGIN_THRESHOLD = sp.Rational(1, 1000)


def _exact_strings(values: Iterable[sp.Expr]) -> list[str]:
    return [sp.sstr(value) for value in values]


def _decimal_strings(values: Iterable[sp.Expr]) -> list[str]:
    return [str(sp.N(value, 18)) for value in values]


def _canonical_hash(strings: Iterable[str]) -> str:
    payload = "\n".join(strings).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _word_labels(word: tuple[tuple[int, int], ...]) -> list[str]:
    return [f"{first}{second}" for first, second in word]


def _instance_hash(problem: dict[str, object]) -> str:
    strings = [
        INSTANCE_ID,
        sp.sstr(EPSILON),
        sp.sstr(MU),
        sp.sstr(NU),
        "beta=1",
        *_exact_strings(problem["Q1"]),
        *_exact_strings(problem["Q2"]),
        *_exact_strings(problem["rhs"]),
        *_word_labels(problem["word"]),
    ]
    return _canonical_hash(strings)


def positive_part(vector: sp.Matrix) -> sp.Matrix:
    """Project an exact vector onto the nonnegative orthant."""
    return sp.Matrix([value if value > 0 else sp.S.Zero for value in vector])


def strict_sign_mask(vector: sp.Matrix) -> tuple[int, ...] | None:
    """Return the strict sign mask, or ``None`` if any component is zero."""
    if any(value == 0 for value in vector):
        return None
    return tuple(1 if value > 0 else 0 for value in vector)


def build_problem() -> dict[str, object]:
    """Construct the frozen pure-quadratic rational instance."""
    identity = sp.eye(2)
    first_direction = sp.Matrix([-1, 20])
    second_direction = sp.Matrix([-1, 10])
    m_matrix = EPSILON * identity + (MU - EPSILON) * (
        first_direction * first_direction.T
    ) / (first_direction.T * first_direction)[0]
    n_matrix = EPSILON * identity + (NU - EPSILON) * (
        second_direction * second_direction.T
    ) / (second_direction.T * second_direction)[0]
    q1_matrix = m_matrix.inv() - identity
    q2_matrix = n_matrix.inv() - identity

    z_star = sp.Matrix([0, 1])
    lambda_star = sp.Matrix([-1, 0])
    x_star = q1_matrix.inv() * lambda_star
    y_star = q2_matrix.inv() * lambda_star
    rhs = x_star + y_star + z_star
    word = ((0, 0), (0, 0)) + ((0, 1),) * 64

    return {
        "I": identity,
        "M": m_matrix,
        "N": n_matrix,
        "Q1": q1_matrix,
        "Q2": q2_matrix,
        "rhs": rhs,
        "x_star": x_star,
        "y_star": y_star,
        "z_star": z_star,
        "lambda_star": lambda_star,
        "word": word,
    }


def raw_quantities(
    state: sp.Matrix, problem: dict[str, object]
) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    """Solve the x/y subproblems and form the next projection input."""
    y_state = state[:2, 0]
    z_state = state[2:4, 0]
    lambda_state = state[4:6, 0]
    x_next = problem["M"] * (
        lambda_state - y_state - z_state + problem["rhs"]
    )
    y_next = problem["N"] * (
        lambda_state - x_next - z_state + problem["rhs"]
    )
    q_next = problem["rhs"] - x_next - y_next + lambda_state
    return x_next, y_next, q_next


def selected_step(
    state: sp.Matrix, problem: dict[str, object], selector: sp.Matrix
) -> sp.Matrix:
    """Affine branch used only to solve the candidate period equation."""
    _, y_next, q_next = raw_quantities(state, problem)
    z_next = selector * q_next
    lambda_next = q_next - z_next
    return y_next.col_join(z_next).col_join(lambda_next)


def actual_step(
    state: sp.Matrix, problem: dict[str, object]
) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    """Apply one original ADMM step with the genuine orthant projection."""
    x_next, y_next, q_next = raw_quantities(state, problem)
    z_next = positive_part(q_next)
    lambda_next = q_next - z_next
    next_state = y_next.col_join(z_next).col_join(lambda_next)
    return x_next, q_next, next_state


def affine_lift(problem: dict[str, object], selector: sp.Matrix) -> sp.Matrix:
    """Recover a seven-dimensional affine lift by exact basis evaluation."""
    origin = sp.zeros(6, 1)
    offset = selected_step(origin, problem, selector)
    columns: list[sp.Matrix] = []
    for index in range(6):
        basis = sp.zeros(6, 1)
        basis[index] = 1
        columns.append(selected_step(basis, problem, selector) - offset)
    affine = sp.Matrix.hstack(*columns).row_join(offset)
    return affine.col_join(sp.zeros(1, 6).row_join(sp.ones(1, 1)))


def solve_period_equation(
    problem: dict[str, object],
) -> tuple[sp.Matrix, sp.Expr]:
    """Solve the exact unreduced essential-state fixed point.

    The prescribed source-mask word is ``(00)^2(01)^64``.
    """
    lifts = {
        (0, 0): affine_lift(problem, sp.diag(0, 0)),
        (0, 1): affine_lift(problem, sp.diag(0, 1)),
    }
    period_lift = sp.eye(7)
    word = problem["word"]
    for target_mask in word[1:] + word[:1]:
        period_lift = lifts[target_mask] * period_lift
    fixed_matrix = sp.eye(6) - period_lift[:6, :6]
    determinant = fixed_matrix.det()
    if determinant == 0:
        raise ValueError("the raw six-dimensional period system is singular")
    return fixed_matrix.inv() * period_lift[:6, 6], determinant


def _is_primitive_word(word: tuple[tuple[int, int], ...]) -> bool:
    proper_divisors = [value for value in range(1, len(word)) if len(word) % value == 0]
    return all(
        any(word[index] != word[index % divisor] for index in range(len(word)))
        for divisor in proper_divisors
    )


def build_certificate() -> dict[str, object]:
    """Close all raw-state proof obligations using exact arithmetic.

    The rich SymPy return value is retained for the manuscript figure builder.
    Use :func:`certificate_payload` for the stable JSON representation.
    """
    problem = build_problem()
    initial, fixed_determinant = solve_period_equation(problem)
    states = [initial]
    updates: list[dict[str, sp.Matrix]] = []
    signed_margins: list[sp.Expr] = []

    source_strict_checks: list[bool] = []
    source_word_checks: list[bool] = []
    x_optimality_checks: list[bool] = []
    y_optimality_checks: list[bool] = []
    q_definition_checks: list[bool] = []
    projection_checks: list[bool] = []
    step_complementarity_checks: list[bool] = []
    multiplier_checks: list[bool] = []

    for expected_mask in problem["word"]:
        state = states[-1]
        y_state = state[:2, 0]
        z_state = state[2:4, 0]
        lambda_state = state[4:6, 0]
        q_source = z_state + lambda_state
        actual_source_mask = strict_sign_mask(q_source)

        source_strict_checks.append(actual_source_mask is not None)
        source_word_checks.append(actual_source_mask == expected_mask)
        if actual_source_mask is None:
            signed_margins.extend([sp.S.Zero, sp.S.Zero])
        else:
            signed_margins.extend(
                value if bit else -value
                for value, bit in zip(q_source, actual_source_mask)
            )

        x_next, q_next, next_state = actual_step(state, problem)
        y_next = next_state[:2, 0]
        z_next = next_state[2:4, 0]
        lambda_next = next_state[4:6, 0]
        residual = x_next + y_next + z_next - problem["rhs"]

        x_optimality_checks.append(
            (problem["Q1"] + problem["I"]) * x_next
            == lambda_state - y_state - z_state + problem["rhs"]
        )
        y_optimality_checks.append(
            (problem["Q2"] + problem["I"]) * y_next
            == lambda_state - x_next - z_state + problem["rhs"]
        )
        q_definition_checks.append(
            q_next == problem["rhs"] - x_next - y_next + lambda_state
        )
        projection_checks.append(z_next == positive_part(q_next))
        step_complementarity_checks.append(
            all(value >= 0 for value in z_next)
            and all(value <= 0 for value in lambda_next)
            and (z_next.T * lambda_next)[0] == 0
        )
        multiplier_checks.append(lambda_next == lambda_state - residual)
        updates.append({"x": x_next, "q_next": q_next})
        states.append(next_state)

    kkt_state = (
        problem["y_star"]
        .col_join(problem["z_star"])
        .col_join(problem["lambda_star"])
    )
    q1_positive_definite = (
        problem["Q1"][0, 0] > 0 and problem["Q1"].det() > 0
    )
    q2_positive_definite = (
        problem["Q2"][0, 0] > 0 and problem["Q2"].det() > 0
    )
    kkt_primal = (
        problem["x_star"] + problem["y_star"] + problem["z_star"]
        == problem["rhs"]
    )
    kkt_x = problem["Q1"] * problem["x_star"] == problem["lambda_star"]
    kkt_y = problem["Q2"] * problem["y_star"] == problem["lambda_star"]
    kkt_z_nonnegative = all(value >= 0 for value in problem["z_star"])
    kkt_lambda_nonpositive = all(
        value <= 0 for value in problem["lambda_star"]
    )
    kkt_complementarity = (
        problem["z_star"].T * problem["lambda_star"]
    )[0] == 0

    checks = {
        "all_data_and_states_are_exact_rationals": all(
            value.is_Rational is True
            for matrix in [
                problem["Q1"],
                problem["Q2"],
                problem["rhs"],
                *states,
            ]
            for value in matrix
        ),
        "Q1_positive_definite": q1_positive_definite,
        "Q2_positive_definite": q2_positive_definite,
        "KKT_primal_feasibility": kkt_primal,
        "KKT_x_stationarity": kkt_x,
        "KKT_y_stationarity": kkt_y,
        "KKT_z_nonnegative": kkt_z_nonnegative,
        "KKT_lambda_nonpositive": kkt_lambda_nonpositive,
        "KKT_complementarity": kkt_complementarity,
        "unique_KKT_from_strong_convexity": (
            q1_positive_definite
            and q2_positive_definite
            and kkt_primal
            and kkt_x
            and kkt_y
            and kkt_z_nonnegative
            and kkt_lambda_nonpositive
            and kkt_complementarity
        ),
        "raw_period_system_invertible": fixed_determinant != 0,
        "all_source_projection_signs_strict": all(source_strict_checks),
        "raw_projection_itinerary_matches_word": all(source_word_checks),
        "all_x_subproblem_equalities_exact": all(x_optimality_checks),
        "all_y_subproblem_equalities_exact": all(y_optimality_checks),
        "all_projection_arguments_exact": all(q_definition_checks),
        "all_positive_part_updates_exact": all(projection_checks),
        "all_stepwise_complementarity_conditions": all(
            step_complementarity_checks
        ),
        "all_multiplier_updates_exact": all(multiplier_checks),
        "all_132_branch_margins_positive": all(
            margin > 0 for margin in signed_margins
        ),
        "uniform_margin_gt_1_over_1000": min(signed_margins)
        > MARGIN_THRESHOLD,
        "exact_return_at_phase_66": states[PERIOD] == states[0],
        "no_earlier_state_return": all(
            states[phase] != states[0] for phase in range(1, PERIOD)
        ),
        "mask_word_is_primitive": _is_primitive_word(problem["word"]),
        "all_66_source_states_are_non_KKT": all(
            state != kkt_state for state in states[:PERIOD]
        ),
    }
    return {
        "valid": all(bool(value) for value in checks.values()),
        "checks": checks,
        "fixed_determinant": fixed_determinant,
        "minimum_margin": min(signed_margins),
        "problem": problem,
        "states": states,
        "updates": updates,
        "signed_margins": signed_margins,
    }


def certificate_payload(certificate: dict[str, object] | None = None) -> dict[str, object]:
    """Return a stable, fully JSON-serializable certificate."""
    if certificate is None:
        certificate = build_certificate()
    problem = certificate["problem"]
    states = certificate["states"]
    initial = states[0]
    initial_y = initial[:2, 0]
    initial_q = initial[2:4, 0] + initial[4:6, 0]
    signed_states = [
        state[:2, 0].col_join(state[2:4, 0] + state[4:6, 0])
        for state in states[:PERIOD]
    ]
    minimum_margin = certificate["minimum_margin"]
    minimum_index = certificate["signed_margins"].index(minimum_margin)
    initial_signed = initial_y.col_join(initial_q)
    exact_hashes = {
        "instance": _instance_hash(problem),
        "word": _canonical_hash(_word_labels(problem["word"])),
        "orbit_y_q": _canonical_hash(
            sp.sstr(value) for state in signed_states for value in state
        ),
        "initial_y_q": _canonical_hash(_exact_strings(initial_signed)),
        "minimum_margin": _canonical_hash([sp.sstr(minimum_margin)]),
    }
    return {
        "schema_version": 1,
        "instance_id": INSTANCE_ID,
        "implementation": "independent_raw_6d_basis_evaluation",
        "implementation_boundary": (
            "Solves the affine period equation in (y,z,lambda), does not "
            "import the signed checker, and accepts the orbit only after "
            "rerunning the genuine positive-part ADMM projection."
        ),
        "status": "passed" if certificate["valid"] else "failed",
        "valid": bool(certificate["valid"]),
        "formulation": "pure_quadratic_zero_linear_terms",
        "parameters": {
            "beta": "1",
            "epsilon": sp.sstr(EPSILON),
            "mu": sp.sstr(MU),
            "nu": sp.sstr(NU),
        },
        "period": PERIOD,
        "word_run_length_encoding": [["00", 2], ["01", 64]],
        "minimum_margin": {
            "exact": sp.sstr(minimum_margin),
            "decimal": str(sp.N(minimum_margin, 20)),
            "phase_zero_based": minimum_index // 2,
            "coordinate_zero_based": minimum_index % 2,
            "threshold_exact": sp.sstr(MARGIN_THRESHOLD),
        },
        "initial_state": {
            "y0_exact": _exact_strings(initial_y),
            "y0_decimal": _decimal_strings(initial_y),
            "q0_exact": _exact_strings(initial_q),
            "q0_decimal": _decimal_strings(initial_q),
            "z0_exact": _exact_strings(initial[2:4, 0]),
            "lambda0_exact": _exact_strings(initial[4:6, 0]),
        },
        "kkt_point": {
            "x_exact": _exact_strings(problem["x_star"]),
            "y_exact": _exact_strings(problem["y_star"]),
            "z_exact": _exact_strings(problem["z_star"]),
            "lambda_exact": _exact_strings(problem["lambda_star"]),
        },
        "exact_hashes": exact_hashes,
        "checks": {
            name: bool(value) for name, value in certificate["checks"].items()
        },
        "claim_boundary": (
            "This exact bounded non-KKT period-66 orbit refutes "
            "unconditional global convergence; it does not claim unbounded "
            "iterates or external independent review."
        ),
    }


def write_payload(payload: dict[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify the exact raw 6D period-66 ADMM certificate."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=CERTIFICATE_DIR / "certificate_raw.json",
    )
    args = parser.parse_args()
    try:
        payload = certificate_payload()
    except Exception as error:
        payload = {
            "schema_version": 1,
            "instance_id": INSTANCE_ID,
            "implementation": "independent_raw_6d_basis_evaluation",
            "status": "error",
            "valid": False,
            "error": f"{type(error).__name__}: {error}",
        }
    write_payload(payload, args.output)
    print(
        json.dumps(
            {
                "instance_id": payload["instance_id"],
                "output": str(args.output.resolve()),
                "valid": payload["valid"],
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if payload["valid"] else 1)


if __name__ == "__main__":
    main()
