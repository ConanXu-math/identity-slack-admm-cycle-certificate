"""Exact obstruction to a problem-independent identity-slack dual step.

The companion module
``analyze_identity_slack_small_step_local_instability`` constructs, for
arbitrarily small relative multiplier steps, a strict KKT branch whose
boundary limit has spectral radius greater than one.

This module closes the remaining orbit gap by varying the rational
strong-convexification path.  At its isotropic endpoint the same branch is
strictly Schur stable.  Continuity therefore gives an interior parameter at
which the branch has a unit-modulus eigenvalue.  Eigenvalue one is excluded
by uniqueness of the KKT point.  A sufficiently small real unit-circle
eigenmode stays forever inside the strict branch and is a bounded
nonconvergent raw-ADMM orbit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sympy as sp

from analyze_identity_slack_small_step_local_instability import (
    relative_step,
    strictified_data,
)


MAX_SLOPE = sp.Rational(1, 4)
MAX_RELATIVE_STEP = sp.Rational(80, 119)


def slope_from_step(theta: sp.Expr) -> sp.Expr:
    """Invert ``theta(r)=80r^2/[7(1+r^2)]``."""

    return sp.sqrt(sp.factor(7 * theta / (80 - 7 * theta)))


def isotropic_parameter() -> sp.Expr:
    """Return the path parameter for ``s=t=1/sqrt(2)``."""

    return sp.sqrt(2) - 1


def isotropic_scalar_branch_matrix(
    theta: sp.Expr, active: bool
) -> sp.Matrix:
    """Return one scalar coordinate block at the isotropic endpoint."""

    root_half = sp.sqrt(2) / 2
    image = sp.Rational(1, 2)
    y_y = root_half * image * root_half
    y_z = -root_half * (1 - image)
    y_lambda = -y_z
    q_y = (1 - image) * image * root_half
    q_z = image - image**2 + image
    q_lambda = 1 - image - image + image**2
    selector = sp.Integer(1 if active else 0)
    complement = 1 - selector
    return sp.Matrix(
        [
            [y_y, y_z, y_lambda],
            [
                selector * q_y,
                selector * q_z,
                selector * q_lambda,
            ],
            [
                theta * complement * q_y,
                theta * complement * q_z,
                (1 - theta) + theta * complement * q_lambda,
            ],
        ]
    )


def isotropic_characteristic_polynomials() -> dict[str, sp.Expr]:
    """Return the exact active and inactive scalar factors."""

    theta = sp.symbols("theta", positive=True)
    spectral = sp.symbols("z")
    active = sp.factor(
        isotropic_scalar_branch_matrix(
            theta, active=True
        ).charpoly(spectral).as_expr()
    )
    inactive = sp.factor(
        isotropic_scalar_branch_matrix(
            theta, active=False
        ).charpoly(spectral).as_expr()
    )
    return {"active": active, "inactive": inactive}


def exact_certificate() -> dict[str, Any]:
    """Return the exact continuity-to-unit-circle obstruction."""

    theta = sp.symbols("theta", positive=True)
    spectral = sp.symbols("z")
    endpoint = isotropic_parameter()
    factor_a, factor_b, hessian_a, hessian_b = strictified_data(
        sp.symbols("r", positive=True), endpoint
    )
    identity = sp.eye(3)
    expected_factor = identity / sp.sqrt(2)
    expected_hessian = identity / 2
    if sp.simplify(factor_a - expected_factor) != sp.zeros(3):
        raise AssertionError("unexpected isotropic A endpoint")
    if sp.simplify(factor_b - expected_factor) != sp.zeros(3):
        raise AssertionError("unexpected isotropic B endpoint")
    if sp.simplify(hessian_a - expected_hessian) != sp.zeros(3):
        raise AssertionError("unexpected isotropic Q1 endpoint")
    if sp.simplify(hessian_b - expected_hessian) != sp.zeros(3):
        raise AssertionError("unexpected isotropic Q2 endpoint")

    polynomials = isotropic_characteristic_polynomials()
    expected_active = (
        (2 * spectral - 1) ** 2
        * (theta + spectral - 1)
        / 4
    )
    expected_inactive = (
        spectral
        * (
            4 * spectral**2
            + (3 * theta - 5) * spectral
            + 1
            - theta
        )
        / 4
    )
    if sp.simplify(polynomials["active"] - expected_active) != 0:
        raise AssertionError("unexpected active endpoint polynomial")
    if sp.simplify(polynomials["inactive"] - expected_inactive) != 0:
        raise AssertionError("unexpected inactive endpoint polynomial")

    if sp.simplify(relative_step(MAX_SLOPE) - MAX_RELATIVE_STEP) != 0:
        raise AssertionError("unexpected maximum relative step")

    # Jury inequalities for 4*z^2+(3*theta-5)z+(1-theta).
    jury = {
        "leading_minus_abs_constant_lower_bound": str(
            sp.factor(4 - (1 + MAX_RELATIVE_STEP))
        ),
        "value_at_plus_one": "2*theta > 0",
        "value_at_minus_one_lower_bound": str(
            sp.factor(10 - 4 * MAX_RELATIVE_STEP)
        ),
    }

    return {
        "status": (
            "exact_symbolic_identity_slack_nonconvergent_orbit_existence"
        ),
        "scope": "strongly_convex_full_row_rank_identity_slack_qp",
        "relative_step_range": "0 < theta <= 80/119",
        "slope_inverse": "r = sqrt(7*theta/(80 - 7*theta))",
        "unstable_endpoint": {
            "path_parameter": "q = 0",
            "certificate": (
                "certificates/"
                "identity_slack_small_step_local_instability.json"
            ),
            "conclusion": "spectral radius strictly greater than one",
        },
        "stable_endpoint": {
            "path_parameter": "q = sqrt(2) - 1",
            "data": "A=B=I/sqrt(2), Q1=Q2=I/2",
            "active_characteristic": str(polynomials["active"]),
            "inactive_characteristic": str(polynomials["inactive"]),
            "jury_inequalities": jury,
            "conclusion": (
                "every scalar branch is strictly Schur stable for "
                "0 < theta <= 80/119"
            ),
        },
        "continuity_step": {
            "statement": (
                "for every theta in the stated interval, continuity of the "
                "branch spectral radius along q in [0,sqrt(2)-1] yields "
                "an interior q_c with spectral radius one"
            ),
            "strictness": (
                "q_c>0 gives Q1,Q2 positive definite and A,B nonsingular"
            ),
        },
        "unit_eigenvalue_exclusion": {
            "statement": (
                "eigenvalue +1 would create a second nearby fixed point "
                "inside the strict affine branch"
            ),
            "contradiction": (
                "every fixed point of the raw ADMM map is a KKT point, "
                "whereas strong convexity and full row rank give a unique "
                "KKT point"
            ),
        },
        "orbit_lift": {
            "unit_modulus_mode": (
                "the unit-circle eigenvalue is either -1 or nonreal"
            ),
            "branch_invariance": (
                "scale a real eigenmode sufficiently small; its powers are "
                "bounded and the strict KKT projection signs never change"
            ),
            "conclusion": (
                "the resulting raw ADMM orbit is bounded and does not "
                "converge to the unique KKT point"
            ),
        },
        "quantified_conclusion": (
            "for every 0 < theta <= 80/119 there exists a strict "
            "identity-slack QP with a bounded nonconvergent ADMM orbit"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "certificates/identity_slack_universal_step_obstruction.json"
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
    print(json.dumps(certificate, indent=2))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
