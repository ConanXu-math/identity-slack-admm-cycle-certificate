"""Exact local-instability family for relaxed identity-slack ADMM.

This module studies the full ``(y, z, lambda)`` branch matrix for a
three-dimensional identity-slack quadratic program.  At the boundary of
strong convexity the two image matrices are rational rank-one projectors.
The relative multiplier step is coupled to a rational slope ``r`` by

    theta(r) = 80*r**2 / (7*(1+r**2)).

Hence rational ``r`` gives rational projectors and a rational relative step,
and ``theta(r)`` tends to zero with ``r``.  The exact Schur calculation in
this file is intended to decide whether the KKT branch is unstable along
that arbitrarily-small-step family.

Local instability is not by itself a nonconvergent-orbit certificate.
Strict strong convexification and a genuine switching orbit are separate
proof obligations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp


DIMENSION = 3
ACTIVE_MASK = 1


def schur_reduction_deltas(
    polynomial: sp.Poly, spectral_variable: sp.Symbol
) -> list[sp.Expr]:
    """Return leading-square minus constant-square Schur deltas."""

    current = polynomial
    deltas: list[sp.Expr] = []
    while current.degree() >= 1:
        leading = sp.factor(current.LC())
        constant = sp.factor(current.TC())
        deltas.append(sp.factor(leading**2 - constant**2))
        reverse = sp.Poly(
            sp.expand(
                spectral_variable ** current.degree()
                * current.as_expr().subs(
                    spectral_variable, 1 / spectral_variable
                )
            ),
            spectral_variable,
            domain="EX",
        )
        reduced = sp.cancel(
            (
                leading * current.as_expr()
                - constant * reverse.as_expr()
            )
            / spectral_variable
        )
        current = sp.Poly(
            reduced, spectral_variable, domain="EX"
        )
    return deltas


def relative_step(slope: sp.Expr) -> sp.Expr:
    """Return the rational relative step coupled to ``slope``."""

    return sp.factor(
        sp.Rational(80, 7) * slope**2 / (1 + slope**2)
    )


def boundary_projectors(
    slope: sp.Expr,
) -> tuple[sp.Matrix, sp.Matrix]:
    """Return the two rational rank-one image projectors.

    The vectors ``(1,r,0)`` and ``(1,3r/5,4r/5)`` have the same squared
    norm ``1+r**2``.  Their normalized outer products are therefore
    rational whenever ``r`` is rational.
    """

    denominator = 1 + slope**2
    vector_a = sp.Matrix([1, slope, 0])
    vector_b = sp.Matrix(
        [1, sp.Rational(3, 5) * slope, sp.Rational(4, 5) * slope]
    )
    return (
        sp.simplify(vector_a * vector_a.T / denominator),
        sp.simplify(vector_b * vector_b.T / denominator),
    )


def strictified_data(
    slope: sp.Expr, strict_parameter: sp.Expr
) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
    """Return exact rational ``(A, B, Q1, Q2)`` strictifying the boundary.

    The Pythagorean parametrization makes both image factors nonsingular and
    both quadratic Hessians positive definite while preserving

    ``Q1 + A.T*A = Q2 + B.T*B = I``.
    """

    projector_a, projector_b = boundary_projectors(slope)
    identity = sp.eye(DIMENSION)
    denominator = 1 + strict_parameter**2
    small = sp.factor(2 * strict_parameter / denominator)
    large = sp.factor(
        (1 - strict_parameter**2) / denominator
    )
    factor_a = sp.simplify(
        large * projector_a + small * (identity - projector_a)
    )
    factor_b = sp.simplify(
        large * projector_b + small * (identity - projector_b)
    )
    hessian_a = sp.simplify(
        small**2 * projector_a
        + large**2 * (identity - projector_a)
    )
    hessian_b = sp.simplify(
        small**2 * projector_b
        + large**2 * (identity - projector_b)
    )
    return factor_a, factor_b, hessian_a, hessian_b


def strict_branch_matrix(
    slope: sp.Expr, strict_parameter: sp.Expr
) -> sp.Matrix:
    """Return the exact strict active-mask branch matrix."""

    factor_a, factor_b, _, _ = strictified_data(
        slope, strict_parameter
    )
    identity = sp.eye(DIMENSION)
    selector = sp.diag(1, 0, 0)
    complement = identity - selector
    theta = relative_step(slope)
    image_a = sp.simplify(factor_a * factor_a.T)
    image_b = sp.simplify(factor_b * factor_b.T)

    y_y = sp.simplify(factor_b.T * image_a * factor_b)
    y_z = sp.simplify(-factor_b.T * (identity - image_a))
    y_lambda = -y_z
    q_y = sp.simplify(
        (identity - image_b) * image_a * factor_b
    )
    q_z = sp.simplify(image_a - image_b * image_a + image_b)
    q_lambda = sp.simplify(
        identity - image_a - image_b + image_b * image_a
    )

    first = y_y.row_join(y_z).row_join(y_lambda)
    second = (
        (selector * q_y)
        .row_join(selector * q_z)
        .row_join(selector * q_lambda)
    )
    third = (
        (theta * complement * q_y)
        .row_join(theta * complement * q_z)
        .row_join(
            (1 - theta) * identity
            + theta * complement * q_lambda
        )
    )
    return sp.simplify(first.col_join(second).col_join(third))


def boundary_branch_matrix(slope: sp.Expr) -> sp.Matrix:
    """Return the exact active-mask branch matrix on ``(y,z,lambda)``."""

    projector_a, projector_b = boundary_projectors(slope)
    identity = sp.eye(DIMENSION)
    selector = sp.diag(1, 0, 0)
    theta = relative_step(slope)

    # At the projector boundary, sqrt(P)=P.
    root_b = projector_b
    y_y = root_b * projector_a * root_b
    y_z = -root_b * (identity - projector_a)
    y_lambda = root_b * (identity - projector_a)

    q_y = (identity - projector_b) * projector_a * root_b
    q_z = projector_a - projector_b * projector_a + projector_b
    q_lambda = (
        identity
        - projector_a
        - projector_b
        + projector_b * projector_a
    )

    first = y_y.row_join(y_z).row_join(y_lambda)
    second = (
        (selector * q_y)
        .row_join(selector * q_z)
        .row_join(selector * q_lambda)
    )
    complement = identity - selector
    third = (
        (theta * complement * q_y)
        .row_join(theta * complement * q_z)
        .row_join(
            (1 - theta) * identity
            + theta * complement * q_lambda
        )
    )
    return sp.simplify(first.col_join(second).col_join(third))


def characteristic_quartic(
    slope: sp.Symbol, spectral_variable: sp.Symbol
) -> tuple[sp.Poly, sp.Expr, sp.Expr]:
    """Factor out the four zero roots and the root ``1-theta``."""

    matrix = boundary_branch_matrix(slope)
    characteristic = sp.factor(
        matrix.charpoly(spectral_variable).as_expr()
    )
    numerator, denominator = sp.together(characteristic).as_numer_denom()
    linear = sp.factor(
        (1 + slope**2)
        * (spectral_variable + relative_step(slope) - 1)
    )
    domain = sp.QQ.frac_field(slope)
    quotient, remainder = sp.div(
        sp.Poly(numerator, spectral_variable, domain=domain),
        sp.Poly(
            spectral_variable**4 * linear,
            spectral_variable,
            domain=domain,
        ),
    )
    if remainder.as_expr() != 0:
        raise AssertionError("expected zero and 1-theta factors")
    return (
        sp.Poly(
            sp.factor(quotient.as_expr()),
            spectral_variable,
            domain="EX",
        ),
        sp.factor(denominator),
        characteristic,
    )


def exact_certificate() -> dict[str, Any]:
    """Return the exact characteristic and Schur data."""

    slope = sp.symbols("r", positive=True)
    spectral_variable = sp.symbols("z")
    quartic, denominator, characteristic = characteristic_quartic(
        slope, spectral_variable
    )
    deltas = schur_reduction_deltas(quartic, spectral_variable)
    first_sign_factor = (
        1205 * slope**8
        + 1977 * slope**6
        - 4643 * slope**4
        - 7385 * slope**2
        - 2450
    )
    second_sign_factor = (
        14530 * slope**10
        + 57137 * slope**8
        - 131931 * slope**6
        - 449323 * slope**4
        - 329735 * slope**2
        - 82950
    )
    delta_one_quotient = sp.factor(deltas[1] / first_sign_factor)
    delta_two_quotient = sp.factor(deltas[2] / second_sign_factor)
    if not all(
        coefficient >= 0
        for coefficient in sp.Poly(
            -delta_one_quotient, slope
        ).all_coeffs()
    ):
        raise AssertionError("delta_1 quotient should be strictly negative")
    if not all(
        coefficient >= 0
        for coefficient in sp.Poly(
            delta_two_quotient, slope
        ).all_coeffs()
    ):
        raise AssertionError("delta_2 quotient should be strictly positive")

    first_negative_upper_bound = (
        -1461 * slope**4
        - 7385 * slope**2
        - 2450
    )
    second_negative_upper_bound = (
        -60264 * slope**6
        - 449323 * slope**4
        - 329735 * slope**2
        - 82950
    )
    if sp.simplify(
        first_negative_upper_bound
        - first_sign_factor
        - slope**4
        * (1 - slope**2)
        * (1205 * slope**2 + 3182)
    ) != 0:
        raise AssertionError("unexpected first sign bound")
    if sp.simplify(
        second_negative_upper_bound
        - second_sign_factor
        - slope**6
        * (1 - slope**2)
        * (14530 * slope**2 + 71667)
    ) != 0:
        raise AssertionError("unexpected second sign bound")

    numeric_checks: list[dict[str, float]] = []
    strict_numeric_checks: list[dict[str, float]] = []
    for value in (
        sp.Rational(1, 10),
        sp.Rational(1, 100),
        sp.Rational(1, 1000),
    ):
        matrix = np.asarray(boundary_branch_matrix(value), dtype=float)
        radius = float(np.max(np.abs(np.linalg.eigvals(matrix))))
        numeric_checks.append(
            {
                "slope": float(value),
                "theta": float(relative_step(value)),
                "spectral_radius": radius,
            }
        )
        strict_parameter = value**2 / 10
        strict_matrix = np.asarray(
            strict_branch_matrix(value, strict_parameter),
            dtype=float,
        )
        strict_numeric_checks.append(
            {
                "slope": float(value),
                "strict_parameter": float(strict_parameter),
                "theta": float(relative_step(value)),
                "spectral_radius": float(
                    np.max(np.abs(np.linalg.eigvals(strict_matrix)))
                ),
            }
        )

    return {
        "status": "exact_symbolic_local_instability",
        "scope": "identity_slack_projector_boundary_kkt_branch",
        "orbit_scope": "not_settled",
        "parameter_range": "0 < r <= 1/4",
        "relative_step": str(relative_step(slope)),
        "characteristic_polynomial": str(characteristic),
        "characteristic_denominator": str(denominator),
        "quartic_numerator": str(sp.factor(quartic.as_expr())),
        "schur_deltas": [str(sp.factor(delta)) for delta in deltas],
        "decisive_delta_index": 2,
        "sign_argument": {
            "delta_0": "positive for r > 0",
            "delta_1_sign_factor": str(first_sign_factor),
            "delta_1_upper_bound": str(first_negative_upper_bound),
            "delta_1_conclusion": "positive for 0 < r <= 1",
            "delta_2_sign_factor": str(second_sign_factor),
            "delta_2_upper_bound": str(second_negative_upper_bound),
            "delta_2_conclusion": "negative for 0 < r <= 1",
            "spectral_conclusion": (
                "the quartic has a root of modulus greater than one"
            ),
        },
        "strictification": {
            "parameters": (
                "choose rational q in (0,1), "
                "s=2q/(1+q^2), t=(1-q^2)/(1+q^2)"
            ),
            "image_factors": (
                "A_q=t*P_A+s*(I-P_A), "
                "B_q=t*P_B+s*(I-P_B)"
            ),
            "objectives": (
                "F_q=I-A_q^T*A_q=s^2*P_A+t^2*(I-P_A)>0; "
                "G_q analogous"
            ),
            "continuity_boundary": (
                "for every fixed rational r, sufficiently small rational q "
                "preserves the strict spectral-radius inequality"
            ),
        },
        "numeric_sanity_checks": numeric_checks,
        "strict_rational_sanity_checks": strict_numeric_checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "outputs/universal_dual_step/"
            "identity_slack_small_step_local_instability.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    certificate = exact_certificate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(certificate, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(certificate["numeric_sanity_checks"], indent=2))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
