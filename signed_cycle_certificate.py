"""Independent exact signed-state certificate for the period-66 ADMM orbit.

This checker derives and solves the four-dimensional piecewise-affine
recurrence in ``(y, q)`` directly for the pure quadratic problem.  It then
reconstructs every original ADMM step and applies the genuine positive-part
projection.  This module deliberately does not import the raw-state checker.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

import sympy as sp


HERE = Path(__file__).resolve().parent
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


def _word_labels(word: tuple[int, ...]) -> list[str]:
    return ["01" if bit else "00" for bit in word]


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
    word = (0, 0) + (1,) * 64

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


def build_signed_branches(
    problem: dict[str, object],
) -> tuple[dict[int, sp.Matrix], dict[int, sp.Matrix], sp.Matrix]:
    """Derive the two exact signed PWA branches without raw-state lifting."""
    identity = problem["I"]
    m_matrix = problem["M"]
    n_matrix = problem["N"]
    recurrence_offset = (identity - m_matrix) * problem["rhs"]
    affine_offset = (n_matrix * recurrence_offset).col_join(
        (identity - n_matrix) * recurrence_offset
    )

    branches: dict[int, sp.Matrix] = {}
    lifts: dict[int, sp.Matrix] = {}
    for bit in (0, 1):
        selector = sp.diag(0, bit)
        sign_matrix = 2 * selector - identity
        branch = sp.BlockMatrix(
            [
                [
                    n_matrix * m_matrix,
                    -n_matrix * (identity - m_matrix) * sign_matrix,
                ],
                [
                    (identity - n_matrix) * m_matrix,
                    selector
                    - (identity - n_matrix)
                    * (identity - m_matrix)
                    * sign_matrix,
                ],
            ]
        ).as_explicit()
        lift = branch.row_join(affine_offset).col_join(
            sp.zeros(1, 4).row_join(sp.ones(1, 1))
        )
        branches[bit] = branch
        lifts[bit] = lift
    return branches, lifts, affine_offset


def solve_period_equation(
    lifts: dict[int, sp.Matrix], word: tuple[int, ...]
) -> tuple[sp.Matrix, sp.Expr]:
    """Solve the exact four-dimensional period equation."""
    period_lift = sp.eye(5)
    for source_bit in word:
        period_lift = lifts[source_bit] * period_lift
    fixed_matrix = sp.eye(4) - period_lift[:4, :4]
    determinant = fixed_matrix.det()
    if determinant == 0:
        raise ValueError("the signed four-dimensional period system is singular")
    return fixed_matrix.inv() * period_lift[:4, 4], determinant


def _is_primitive_word(word: tuple[int, ...]) -> bool:
    proper_divisors = [value for value in range(1, len(word)) if len(word) % value == 0]
    return all(
        any(word[index] != word[index % divisor] for index in range(len(word)))
        for divisor in proper_divisors
    )


def _cross_term(
    states: list[sp.Matrix], problem: dict[str, object], source_phase: int
) -> sp.Expr:
    """Return <y^{k+1}-y*, z^{k+1}-z^k> for a source phase k."""
    target_phase = (source_phase + 1) % PERIOD
    y_next = states[target_phase][:2, 0]
    z_source = positive_part(states[source_phase][2:, 0])
    z_next = positive_part(states[target_phase][2:, 0])
    return ((y_next - problem["y_star"]).T * (z_next - z_source))[0]


def build_certificate() -> dict[str, object]:
    """Close the signed-state and reconstructed-ADMM obligations exactly."""
    problem = build_problem()
    branches, lifts, affine_offset = build_signed_branches(problem)
    initial, fixed_determinant = solve_period_equation(lifts, problem["word"])

    states: list[sp.Matrix] = []
    margins: list[sp.Expr] = []
    branch_recurrence_checks: list[bool] = []
    source_strict_checks: list[bool] = []
    source_word_checks: list[bool] = []

    current = initial
    closing_state = initial
    for source_bit in problem["word"]:
        states.append(current)
        q_state = current[2:, 0]
        actual_mask = strict_sign_mask(q_state)
        expected_mask = (0, source_bit)
        source_strict_checks.append(actual_mask is not None)
        source_word_checks.append(actual_mask == expected_mask)
        margins.extend([-q_state[0], q_state[1] if source_bit else -q_state[1]])
        lifted_next = lifts[source_bit] * current.col_join(sp.ones(1, 1))
        next_state = lifted_next[:4, 0]
        branch_recurrence_checks.append(
            next_state == branches[source_bit] * current + affine_offset
        )
        closing_state = next_state
        current = next_state

    source_decomposition_checks: list[bool] = []
    x_optimality_checks: list[bool] = []
    y_optimality_checks: list[bool] = []
    q_definition_checks: list[bool] = []
    projection_checks: list[bool] = []
    step_complementarity_checks: list[bool] = []
    reconstructed_state_checks: list[bool] = []
    multiplier_checks: list[bool] = []

    for phase, state in enumerate(states):
        target_phase = (phase + 1) % PERIOD
        expected_next = states[target_phase]
        y_state = state[:2, 0]
        q_state = state[2:, 0]
        z_state = positive_part(q_state)
        lambda_state = q_state - z_state

        source_decomposition_checks.append(
            all(value >= 0 for value in z_state)
            and all(value <= 0 for value in lambda_state)
            and (z_state.T * lambda_state)[0] == 0
            and q_state == z_state + lambda_state
        )
        x_next = problem["M"] * (
            lambda_state - y_state - z_state + problem["rhs"]
        )
        y_next = problem["N"] * (
            lambda_state - x_next - z_state + problem["rhs"]
        )
        q_next = problem["rhs"] - x_next - y_next + lambda_state
        z_next = positive_part(q_next)
        lambda_next = q_next - z_next
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
        reconstructed_state_checks.append(
            y_next == expected_next[:2, 0]
            and q_next == expected_next[2:, 0]
        )

    cross_terms = {
        1: _cross_term(states, problem, 1),
        20: _cross_term(states, problem, 20),
    }
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
    kkt_signed_state = problem["y_star"].col_join(
        problem["z_star"] + problem["lambda_star"]
    )

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
        "M_has_frozen_exact_spectrum": set(problem["M"].eigenvals())
        == {EPSILON, MU},
        "N_has_frozen_exact_spectrum": set(problem["N"].eigenvals())
        == {EPSILON, NU},
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
        "signed_period_system_invertible": fixed_determinant != 0,
        "signed_period_closure": closing_state == initial,
        "all_signed_branch_recurrences_exact": all(branch_recurrence_checks),
        "all_source_projection_signs_strict": all(source_strict_checks),
        "signed_projection_itinerary_matches_word": all(source_word_checks),
        "all_132_branch_margins_positive": all(margin > 0 for margin in margins),
        "uniform_margin_gt_1_over_1000": min(margins) > MARGIN_THRESHOLD,
        "all_source_decompositions_and_complementarity": all(
            source_decomposition_checks
        ),
        "all_x_subproblem_equalities_exact": all(x_optimality_checks),
        "all_y_subproblem_equalities_exact": all(y_optimality_checks),
        "all_projection_arguments_exact": all(q_definition_checks),
        "all_positive_part_updates_exact": all(projection_checks),
        "all_stepwise_complementarity_conditions": all(
            step_complementarity_checks
        ),
        "all_multiplier_updates_exact": all(multiplier_checks),
        "all_reconstructed_raw_ADMM_states_match": all(
            reconstructed_state_checks
        ),
        "no_earlier_signed_state_return": all(
            states[phase] != states[0] for phase in range(1, PERIOD)
        ),
        "mask_word_is_primitive": _is_primitive_word(problem["word"]),
        "all_66_source_states_are_non_KKT": all(
            state != kkt_signed_state for state in states
        ),
        "cross_term_source_phase_1_is_positive": cross_terms[1] > 0,
        "cross_term_source_phase_20_is_negative": cross_terms[20] < 0,
    }
    return {
        "valid": all(bool(value) for value in checks.values()),
        "checks": checks,
        "cross_terms": cross_terms,
        "fixed_determinant": fixed_determinant,
        "minimum_margin": min(margins),
        "margins": margins,
        "problem": problem,
        "states": states,
    }


def certificate_payload(certificate: dict[str, object] | None = None) -> dict[str, object]:
    """Return a stable, fully JSON-serializable certificate."""
    if certificate is None:
        certificate = build_certificate()
    problem = certificate["problem"]
    states = certificate["states"]
    initial = states[0]
    initial_y = initial[:2, 0]
    initial_q = initial[2:, 0]
    minimum_margin = certificate["minimum_margin"]
    minimum_index = certificate["margins"].index(minimum_margin)
    exact_hashes = {
        "instance": _instance_hash(problem),
        "word": _canonical_hash(_word_labels(problem["word"])),
        "orbit_y_q": _canonical_hash(
            sp.sstr(value) for state in states for value in state
        ),
        "initial_y_q": _canonical_hash(_exact_strings(initial)),
        "minimum_margin": _canonical_hash([sp.sstr(minimum_margin)]),
    }
    cross_term_witnesses = []
    for source_phase, expected_sign in ((1, "positive"), (20, "negative")):
        value = certificate["cross_terms"][source_phase]
        cross_term_witnesses.append(
            {
                "source_phase_zero_based": source_phase,
                "definition": "<y^(k+1)-y*, z^(k+1)-z^k>",
                "expected_sign": expected_sign,
                "exact": sp.sstr(value),
                "decimal": str(sp.N(value, 20)),
                "passed": bool(value > 0 if expected_sign == "positive" else value < 0),
            }
        )
    return {
        "schema_version": 1,
        "instance_id": INSTANCE_ID,
        "implementation": "independent_signed_4d_recurrence",
        "implementation_boundary": (
            "Derives the recurrence directly in (y,q), does not import the "
            "raw checker, and separately reconstructs all original ADMM "
            "subproblem, projection, and multiplier updates."
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
        },
        "kkt_point": {
            "x_exact": _exact_strings(problem["x_star"]),
            "y_exact": _exact_strings(problem["y_star"]),
            "z_exact": _exact_strings(problem["z_star"]),
            "lambda_exact": _exact_strings(problem["lambda_star"]),
        },
        "cross_term_sign_witnesses": cross_term_witnesses,
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
        description="Verify the exact signed 4D period-66 ADMM certificate."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "certificate_signed.json",
    )
    args = parser.parse_args()
    try:
        payload = certificate_payload()
    except Exception as error:
        payload = {
            "schema_version": 1,
            "instance_id": INSTANCE_ID,
            "implementation": "independent_signed_4d_recurrence",
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
