from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp


def run() -> dict[str, object]:
    epsilon = sp.Rational(1, 1000)
    identity = sp.eye(2)
    first_direction = sp.Matrix([-1, 20])
    second_direction = sp.Matrix([-1, 10])
    m_matrix = epsilon * identity + (sp.Rational(9, 10) - epsilon) * (
        first_direction * first_direction.T
    ) / 401
    n_matrix = epsilon * identity + (sp.Rational(999, 1000) - epsilon) * (
        second_direction * second_direction.T
    ) / 101

    q1_matrix = m_matrix.inv() - identity
    q2_matrix = n_matrix.inv() - identity
    selector = sp.diag(0, 1)
    sign = 2 * selector - identity
    branch = sp.BlockMatrix(
        [
            [n_matrix * m_matrix, -n_matrix * (identity - m_matrix) * sign],
            [
                (identity - n_matrix) * m_matrix,
                selector - (identity - n_matrix) * (identity - m_matrix) * sign,
            ],
        ]
    ).as_explicit()

    variable = sp.symbols("t")
    characteristic = sp.Poly(branch.charpoly(variable).as_expr(), variable)
    cubic = sp.Poly(sp.cancel(characteristic.as_expr() / variable), variable)
    _, first, second, third = cubic.all_coeffs()
    jury_mid = sp.factor(1 - second + first * third - third**2)
    expected_jury_mid = -sp.Rational(
        433775258062294638209, 40047143579101562500000000
    )

    x_star = sp.zeros(2, 1)
    y_star = sp.zeros(2, 1)
    z_star = sp.Matrix([0, 1])
    lambda_star = sp.Matrix([-1, 0])
    rhs = z_star
    c1 = lambda_star
    c2 = lambda_star
    q_star = z_star + lambda_star

    recurrence_offset = (
        (identity - m_matrix) * rhs + m_matrix * c1 - c2
    )
    p_star = (
        m_matrix * y_star
        - (identity - m_matrix) * q_star.applyfunc(abs)
        + recurrence_offset
    )
    y_next = n_matrix * p_star
    q_next = (identity - n_matrix) * p_star + sp.Matrix([0, 1]) + c2

    checks = {
        "M_spectrum": set(m_matrix.eigenvals())
        == {sp.Rational(1, 1000), sp.Rational(9, 10)},
        "N_spectrum": set(n_matrix.eigenvals())
        == {sp.Rational(1, 1000), sp.Rational(999, 1000)},
        "Q1_positive_definite": q1_matrix[0, 0] > 0 and q1_matrix.det() > 0,
        "Q2_positive_definite": q2_matrix[0, 0] > 0 and q2_matrix.det() > 0,
        "primal_feasibility": x_star + y_star + z_star == rhs,
        "x_stationarity": q1_matrix * x_star + c1 == lambda_star,
        "y_stationarity": q2_matrix * y_star + c2 == lambda_star,
        "strict_complementarity": z_star[1] > 0 and lambda_star[0] < 0,
        "strict_signed_orthant": q_star[0] < 0 and q_star[1] > 0,
        "signed_recurrence_fixed_point": y_next == y_star and q_next == q_star,
        "zero_characteristic_root": characteristic.eval(0) == 0,
        "negative_jury_mid": jury_mid == expected_jury_mid and jury_mid < 0,
    }
    return {
        "status": "exact_strict_kkt_local_expansion_history_lyapunov_obstruction",
        "scope": "strongly convex rational A=B=I slack QP with a strict mixed-mask KKT point",
        "checks": {key: bool(value) for key, value in checks.items()},
        "jury_mid": str(jury_mid),
        "selector": [0, 1],
        "q_star": [str(value) for value in q_star],
        "claim_boundary": "Local branch expansion rules out locally norm-controlling monotone static or finite-history quadratic Lyapunov functions. It is not an ADMM divergence counterexample because trajectories may exit the branch and return.",
        "valid": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "outputs/breakthrough_attempts/stage43_local_expansion_history_obstruction/certificate.json"
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
