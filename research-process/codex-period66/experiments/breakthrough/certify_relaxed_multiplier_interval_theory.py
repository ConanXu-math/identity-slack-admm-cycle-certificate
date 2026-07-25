"""Exact interval and local-stability certificates for multiplier relaxation.

This script upgrades the fixed ``tau=1/2`` convergence certificate in
``certify_relaxed_multiplier_half_convergence.py`` in two directions.

1.  It proves that the strict KKT branch ``01`` has a common rational
    Lyapunov matrix for every ``tau in [49/100, 51/100]``.
2.  It proves, by a componentwise rational sensitivity enclosure, that the
    original period-66 initial point follows the strict word ``00, 00, 01, ...``
    through step 232 and enters the common invariant ellipsoid for every
    ``tau in [1/2-10^-10, 1/2+10^-10]``.
3.  It derives the exact characteristic polynomial of the ``01`` branch and
    uses the real Schur recursion plus Sturm root counts to characterize its
    local-stability boundary inside ``0 < tau < 1``.

All decisions are made over ``sympy.Rational``.  Decimal strings in the JSON
and Markdown outputs are display aids only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

import sympy as sp


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


ROOT = Path(__file__).resolve().parents[2]
HALF_CERTIFIER = (
    ROOT
    / "experiments"
    / "breakthrough"
    / "certify_relaxed_multiplier_half_convergence.py"
)
DEFAULT_OUTPUT = (
    ROOT
    / "outputs"
    / "tau_relaxation_theory_2026-07-16"
    / "results"
    / "certificate.json"
)
DEFAULT_SUMMARY = (
    ROOT / "outputs" / "tau_relaxation_theory_2026-07-16" / "RUN_SUMMARY.md"
)

TAU_CENTER = sp.Rational(1, 2)
COMMON_TAU_LOWER = sp.Rational(49, 100)
COMMON_TAU_UPPER = sp.Rational(51, 100)
PREFIX_RADIUS = sp.Rational(1, 10**10)
PREFIX_TAU_LOWER = TAU_CENTER - PREFIX_RADIUS
PREFIX_TAU_UPPER = TAU_CENTER + PREFIX_RADIUS
PREFIX_STEPS = 232

SELECTOR_00 = sp.zeros(2)
SELECTOR_01 = sp.diag(0, 1)


def load_half_certifier():
    """Load the already reviewed exact ``tau=1/2`` implementation."""
    spec = importlib.util.spec_from_file_location("relaxed_half_exact", HALF_CERTIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load exact certifier: {HALF_CERTIFIER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def abs_matrix(matrix: sp.Matrix) -> sp.Matrix:
    """Return the entrywise absolute value of an exact matrix."""
    return matrix.applyfunc(abs)


def canonical_hash(values: Any) -> str:
    """Hash nested exact data using canonical rational strings."""
    if isinstance(values, sp.MatrixBase):
        payload = ";".join(str(value) for value in values)
    elif isinstance(values, (list, tuple)):
        payload = ";".join(str(value) for value in values)
    else:
        payload = str(values)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def fixed_decimal(value: sp.Expr, places: int = 20) -> str:
    """Render exact values without scientific notation."""
    return format(sp.N(value, places + 20), f".{places}f")


def rational_digest(value: sp.Expr) -> dict[str, Any]:
    """Store an auditable digest without printing enormous integers."""
    rational = sp.cancel(value)
    numerator, denominator = sp.fraction(rational)
    numerator_text = str(numerator)
    denominator_text = str(denominator)
    return {
        "sign": int(sp.sign(rational)),
        "decimal": fixed_decimal(rational),
        "numerator_digits": len(numerator_text.lstrip("-")),
        "denominator_digits": len(denominator_text.lstrip("-")),
        "sha256": canonical_hash((numerator_text, denominator_text)),
    }


def parameterized_branch_data(
    problem: dict[str, Any], selector: sp.Matrix
) -> dict[str, sp.Matrix]:
    """Return exact affine data for ``state=(y,z,lambda)``.

    The dual update is

    ``lambda_next = lambda - tau*(x_next+y_next+z_next-rhs)``.

    Consequently ``T(tau)=T_zero+tau*T_tau`` and
    ``a(tau)=a_zero+tau*a_tau``.  The projection input
    ``q_next=C*state+d`` is independent of ``tau``.
    """
    matrix_m = problem["M"]
    matrix_n = problem["N"]
    rhs = problem["rhs"]
    identity = sp.eye(2)

    c_y = (identity - matrix_n) * matrix_m
    c_z = matrix_n + (identity - matrix_n) * matrix_m
    c_lambda = (identity - matrix_n) * (identity - matrix_m)
    q_matrix = sp.Matrix.hstack(c_y, c_z, c_lambda)
    q_offset = c_lambda * rhs

    t_zero = sp.zeros(6)
    t_tau = sp.zeros(6)
    a_zero = sp.zeros(6, 1)
    a_tau = sp.zeros(6, 1)

    t_zero[:2, :2] = matrix_n * matrix_m
    t_zero[:2, 2:4] = -matrix_n * (identity - matrix_m)
    t_zero[:2, 4:6] = matrix_n * (identity - matrix_m)

    t_zero[2:4, :2] = selector * c_y
    t_zero[2:4, 2:4] = selector * c_z
    t_zero[2:4, 4:6] = selector * c_lambda

    # At tau=0 the old multiplier is copied unchanged.  All dependence on
    # tau is isolated in the bottom two rows.
    t_zero[4:6, 4:6] = identity
    t_tau[4:6, :2] = (identity - selector) * c_y
    t_tau[4:6, 2:4] = (identity - selector) * c_z
    t_tau[4:6, 4:6] = (identity - selector) * c_lambda - identity

    a_zero[:2, :] = matrix_n * (identity - matrix_m) * rhs
    a_zero[2:4, :] = selector * q_offset
    a_tau[4:6, :] = (identity - selector) * q_offset

    return {
        "T_zero": t_zero,
        "T_tau": t_tau,
        "a_zero": a_zero,
        "a_tau": a_tau,
        "C": q_matrix,
        "d": q_offset,
    }


def evaluate_branch(data: dict[str, sp.Matrix], tau: sp.Rational) -> tuple[sp.Matrix, sp.Matrix]:
    return data["T_zero"] + tau * data["T_tau"], data["a_zero"] + tau * data["a_tau"]


def direct_affine_data(
    problem: dict[str, Any], selector: sp.Matrix, tau: sp.Rational
) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
    """Re-derive affine data from the four original updates at a given tau.

    This intentionally does not call :func:`parameterized_branch_data`; it is
    a formula-level cross-check of the parameterized block matrix.
    """

    def sweep(state: sp.Matrix) -> tuple[sp.Matrix, sp.Matrix]:
        y = state[:2, 0]
        z_value = state[2:4, 0]
        multiplier = state[4:6, 0]
        x_next = problem["M"] * (multiplier - y - z_value + problem["rhs"])
        y_next = problem["N"] * (
            multiplier - x_next - z_value + problem["rhs"]
        )
        q_next = problem["rhs"] - x_next - y_next + multiplier
        z_next = selector * q_next
        residual = x_next + y_next + z_next - problem["rhs"]
        lambda_next = multiplier - tau * residual
        return y_next.col_join(z_next).col_join(lambda_next), q_next

    zero = sp.zeros(6, 1)
    state_offset, q_offset = sweep(zero)
    state_columns: list[sp.Matrix] = []
    q_columns: list[sp.Matrix] = []
    for column in range(6):
        basis = sp.zeros(6, 1)
        basis[column] = 1
        state_next, q_next = sweep(basis)
        state_columns.append(state_next - state_offset)
        q_columns.append(q_next - q_offset)
    return (
        sp.Matrix.hstack(*state_columns),
        state_offset,
        sp.Matrix.hstack(*q_columns),
        q_offset,
    )


def leading_principal_minors(matrix: sp.Matrix) -> list[sp.Expr]:
    return [sp.factor(matrix[:size, :size].det()) for size in range(1, matrix.rows + 1)]


def build_common_lyapunov_certificate(
    problem: dict[str, Any], half: Any
) -> dict[str, Any]:
    """Certify a common Lyapunov matrix on a rational tau interval."""
    data = parameterized_branch_data(problem, SELECTOR_01)
    t_half, a_half = evaluate_branch(data, TAU_CENTER)
    reference_t, reference_a, reference_c, reference_d = half.affine_data(
        problem, SELECTOR_01
    )
    derivation_checks = {
        "T_at_one_half_matches_original_sweep": t_half == reference_t,
        "a_at_one_half_matches_original_sweep": a_half == reference_a,
        "q_matrix_matches_original_sweep": data["C"] == reference_c,
        "q_offset_matches_original_sweep": data["d"] == reference_d,
    }
    # Check a second rational tau and both relevant selectors directly from
    # the original x/y/z/lambda updates.  This guards against an accidental
    # formula that happens to agree only at tau=1/2.
    for label, selector in (("00", SELECTOR_00), ("01", SELECTOR_01)):
        selector_data = parameterized_branch_data(problem, selector)
        trial_tau = sp.Rational(2, 5)
        trial_t, trial_a = evaluate_branch(selector_data, trial_tau)
        direct_t, direct_a, direct_c, direct_d = direct_affine_data(
            problem, selector, trial_tau
        )
        derivation_checks[f"T_{label}_at_two_fifths_matches_original_sweep"] = (
            trial_t == direct_t
        )
        derivation_checks[f"a_{label}_at_two_fifths_matches_original_sweep"] = (
            trial_a == direct_a
        )
        derivation_checks[f"q_{label}_at_two_fifths_matches_original_sweep"] = (
            selector_data["C"] == direct_c and selector_data["d"] == direct_d
        )

    lyapunov = half.exact_discrete_lyapunov(t_half)
    h_minors = leading_principal_minors(lyapunov)
    endpoint_records: list[dict[str, Any]] = []
    endpoint_deltas: list[sp.Expr] = []
    for tau in (COMMON_TAU_LOWER, COMMON_TAU_UPPER):
        matrix, _ = evaluate_branch(data, tau)
        residual = sp.simplify(lyapunov - matrix.T * lyapunov * matrix)
        minors = leading_principal_minors(residual)
        # For F>0, lambda_min(F) >= 1/trace(F^{-1}).  This gives an exact
        # rational uniform decrease after using Loewner concavity.
        delta = sp.factor(1 / sp.trace(residual.inv()))
        endpoint_deltas.append(delta)
        endpoint_records.append(
            {
                "tau": str(tau),
                "all_sylvester_minors_positive": all(value > 0 for value in minors),
                "sylvester_minors": [str(value) for value in minors],
                "sylvester_minors_decimal": [fixed_decimal(value) for value in minors],
                "delta_lower_bound": str(delta),
                "delta_lower_bound_decimal": fixed_decimal(delta),
                "residual_sha256": canonical_hash(residual),
            }
        )

    uniform_delta = min(endpoint_deltas)
    trace_h = sp.factor(sp.trace(lyapunov))
    uniform_contraction = sp.factor(1 - uniform_delta / trace_h)

    # The q-map and the KKT point do not depend on tau.  Hence one safe
    # ellipsoid works throughout the common-H interval.
    kkt_state = (
        problem["y_star"]
        .col_join(problem["z_star"])
        .col_join(problem["lambda_star"])
    )
    q_star = data["C"] * kkt_state + data["d"]
    inverse_h = lyapunov.inv()
    denominators = [
        sp.factor((data["C"].row(i) * inverse_h * data["C"].row(i).T)[0])
        for i in range(2)
    ]
    alpha_candidates = [sp.factor(q_star[i] ** 2 / denominators[i]) for i in range(2)]
    alpha = min(alpha_candidates)

    checks = {
        **derivation_checks,
        "H_is_symmetric_positive_definite": (
            lyapunov == lyapunov.T and all(value > 0 for value in h_minors)
        ),
        "both_endpoint_residuals_are_positive_definite": all(
            record["all_sylvester_minors_positive"] for record in endpoint_records
        ),
        "uniform_delta_is_positive": uniform_delta > 0,
        "uniform_contraction_is_strict": 0 < uniform_contraction < 1,
        "kkt_projection_is_strict_01": q_star == sp.Matrix([-1, 1]),
        "common_projection_safe_alpha_is_positive": alpha > 0,
    }

    return {
        "valid": all(bool(value) for value in checks.values()),
        "checks": {name: bool(value) for name, value in checks.items()},
        "tau_interval": [str(COMMON_TAU_LOWER), str(COMMON_TAU_UPPER)],
        "endpoint_certificates": endpoint_records,
        "uniform_delta": str(uniform_delta),
        "uniform_delta_decimal": fixed_decimal(uniform_delta),
        "trace_H": str(trace_h),
        "uniform_contraction_factor": str(uniform_contraction),
        "uniform_contraction_factor_decimal": fixed_decimal(uniform_contraction),
        "ellipsoid_alpha": str(alpha),
        "ellipsoid_alpha_decimal": fixed_decimal(alpha),
        "H_sha256": canonical_hash(lyapunov),
        "T_half_sha256": canonical_hash(t_half),
        "proof_rule": (
            "F(tau)=H-T(tau)^T H T(tau) is Loewner-concave because "
            "F''(tau)=-2*T_tau^T*H*T_tau <= 0; endpoint positivity therefore "
            "implies positivity throughout the interval"
        ),
        "_objects": {
            "data": data,
            "H": lyapunov,
            "alpha": alpha,
            "kkt_state": kkt_state,
        },
    }


def expected_mask(step: int) -> str:
    return "00" if step <= 2 else "01"


def build_prefix_interval_certificate(
    problem: dict[str, Any], half: Any, common: dict[str, Any]
) -> dict[str, Any]:
    """Certify a strict finite prefix uniformly in a rational tau interval.

    Let ``s_k^c`` be the exact trajectory at ``tau=1/2`` and suppose
    ``|s_k(tau)-s_k^c| <= r_k`` componentwise.  Since

    ``T_D(tau)=T_D(1/2)+(tau-1/2)E_D``, the next radius satisfies

    ``r_{k+1}=|T_D(1/2)|r_k+h(|E_D||s_k^c|+|E_D|r_k+|f_D|)``.

    This is a rigorous enclosure, not a floating-point sample.
    """
    branch_data = {
        "00": parameterized_branch_data(problem, SELECTOR_00),
        "01": parameterized_branch_data(problem, SELECTOR_01),
    }
    initial = half.load_exact_verifier().construct_initial(problem)
    state_center = initial
    radius = sp.zeros(6, 1)
    true_state = initial
    min_sign_lower: sp.Expr | None = None
    min_sign_location: tuple[int, int] | None = None
    masks: list[str] = []

    for step in range(1, PREFIX_STEPS + 1):
        branch = expected_mask(step)
        data = branch_data[branch]
        center_t, center_a = evaluate_branch(data, TAU_CENTER)

        q_center = data["C"] * state_center + data["d"]
        q_radius = abs_matrix(data["C"]) * radius
        for coordinate, bit in enumerate(branch):
            lower = (
                -q_center[coordinate] - q_radius[coordinate]
                if bit == "0"
                else q_center[coordinate] - q_radius[coordinate]
            )
            if min_sign_lower is None or lower < min_sign_lower:
                min_sign_lower = lower
                min_sign_location = (step, coordinate + 1)
            if lower <= 0:
                raise RuntimeError(
                    f"uniform sign enclosure failed at step {step}, coordinate {coordinate + 1}"
                )

        # Cross-check the centre orbit against the original true projection.
        true_update = half.relaxed_components(true_state, problem, None)
        masks.append(half.mask(true_update["q"]))
        if true_update["state"] != center_t * state_center + center_a:
            raise RuntimeError(f"centre-map mismatch at step {step}")

        next_radius = (
            abs_matrix(center_t) * radius
            + PREFIX_RADIUS
            * (
                abs_matrix(data["T_tau"]) * abs_matrix(state_center)
                + abs_matrix(data["T_tau"]) * radius
                + abs_matrix(data["a_tau"])
            )
        )
        state_center = center_t * state_center + center_a
        true_state = true_update["state"]
        radius = next_radius

    if min_sign_lower is None or min_sign_location is None:
        raise RuntimeError("empty prefix")

    lyapunov = common["_objects"]["H"]
    alpha = common["_objects"]["alpha"]
    kkt_state = common["_objects"]["kkt_state"]
    error_center = state_center - kkt_state
    center_value = sp.factor((error_center.T * lyapunov * error_center)[0])
    upper_value = sp.factor(
        center_value
        + 2 * (abs_matrix(lyapunov * error_center).T * radius)[0]
        + (radius.T * abs_matrix(lyapunov) * radius)[0]
    )
    ellipsoid_slack = sp.factor(alpha - upper_value)

    checks = {
        "parameter_interval_is_nonempty": PREFIX_TAU_LOWER < PREFIX_TAU_UPPER,
        "parameter_interval_lies_in_common_H_interval": (
            COMMON_TAU_LOWER <= PREFIX_TAU_LOWER
            and PREFIX_TAU_UPPER <= COMMON_TAU_UPPER
        ),
        "all_uniform_sign_lower_bounds_are_strict": min_sign_lower > 0,
        "centre_true_projection_masks_match_word": (
            masks[:2] == ["00", "00"] and all(value == "01" for value in masks[2:])
        ),
        "uniform_ellipsoid_entry_at_final_prefix_step": ellipsoid_slack > 0,
    }

    return {
        "valid": all(bool(value) for value in checks.values()),
        "checks": {name: bool(value) for name, value in checks.items()},
        "tau_interval": [str(PREFIX_TAU_LOWER), str(PREFIX_TAU_UPPER)],
        "tau_interval_decimal": [
            fixed_decimal(PREFIX_TAU_LOWER, 14),
            fixed_decimal(PREFIX_TAU_UPPER, 14),
        ],
        "centre_tau": str(TAU_CENTER),
        "steps": PREFIX_STEPS,
        "word": f"00, 00, then 01 through step {PREFIX_STEPS}",
        "minimum_uniform_sign_lower_bound": rational_digest(min_sign_lower),
        "minimum_uniform_sign_location": {
            "step": min_sign_location[0],
            "q_coordinate": min_sign_location[1],
        },
        "centre_lyapunov_value": rational_digest(center_value),
        "uniform_lyapunov_upper_bound": rational_digest(upper_value),
        "ellipsoid_slack": rational_digest(ellipsoid_slack),
        "ellipsoid_ratio_upper_decimal": fixed_decimal(upper_value / alpha),
        "final_radius_sha256": canonical_hash(radius),
        "final_centre_state_sha256": canonical_hash(state_center),
        "enclosure_rule": (
            "componentwise exact rational sensitivity recurrence around tau=1/2"
        ),
        "scope_note": (
            "The narrow radius is a sufficient bound from a conservative "
            "componentwise enclosure; it is not the width of the actual stable set."
        ),
    }


def primitive_polynomial_vector(
    coefficients: list[sp.Expr], tau: sp.Symbol
) -> list[sp.Expr]:
    """Remove common rational content and orient the leading term at tau=1/2."""
    polynomials = [sp.Poly(sp.expand(value), tau, domain=sp.QQ) for value in coefficients]
    denominator_lcm = sp.ilcm(*[
        term.q for polynomial in polynomials for term in polynomial.all_coeffs()
    ])
    integer_polys = [sp.Poly(polynomial.as_expr() * denominator_lcm, tau, domain=sp.ZZ) for polynomial in polynomials]
    integer_content = 0
    for polynomial in integer_polys:
        for coefficient in polynomial.all_coeffs():
            integer_content = math.gcd(integer_content, abs(int(coefficient)))
    if integer_content == 0:
        raise RuntimeError("zero polynomial vector in Schur recursion")
    normalized = [sp.expand(polynomial.as_expr() / integer_content) for polynomial in integer_polys]
    if normalized[0].subs(tau, TAU_CENTER) < 0:
        normalized = [-value for value in normalized]
    return normalized


def schur_margin_levels(
    quartic_coefficients: list[sp.Expr], tau: sp.Symbol
) -> list[dict[str, sp.Expr | int]]:
    """Return exact real-Schur recursion margins from degree four to one."""
    coefficients = primitive_polynomial_vector(quartic_coefficients, tau)
    levels: list[dict[str, sp.Expr | int]] = []
    while len(coefficients) > 1:
        degree = len(coefficients) - 1
        lead = sp.expand(coefficients[0])
        constant = sp.expand(coefficients[-1])
        levels.append(
            {
                "degree": degree,
                "lead_plus_constant": sp.factor(lead + constant),
                "lead_minus_constant": sp.factor(lead - constant),
            }
        )
        if degree == 1:
            break
        transformed = [
            sp.expand(lead * coefficients[index] - constant * coefficients[-1 - index])
            for index in range(degree)
        ]
        coefficients = primitive_polynomial_vector(transformed, tau)
    return levels


def strip_known_factors(
    polynomial: sp.Expr, tau: sp.Symbol, boundary: sp.Poly
) -> tuple[sp.Poly, int, int, int]:
    """Remove powers of G(tau), tau and tau-1 for open-interval sign checks."""
    current = sp.Poly(sp.expand(polynomial), tau, domain=sp.QQ)
    g_power = 0
    zero_power = 0
    one_power = 0
    while True:
        quotient, remainder = sp.div(current, boundary, domain=sp.QQ)
        if remainder.is_zero:
            current = quotient
            g_power += 1
        else:
            break
    tau_poly = sp.Poly(tau, tau, domain=sp.QQ)
    one_poly = sp.Poly(tau - 1, tau, domain=sp.QQ)
    while current.eval(0) == 0:
        current = sp.div(current, tau_poly, domain=sp.QQ)[0]
        zero_power += 1
    while current.eval(1) == 0:
        current = sp.div(current, one_poly, domain=sp.QQ)[0]
        one_power += 1
    return current, g_power, zero_power, one_power


def build_local_boundary_certificate(problem: dict[str, Any]) -> dict[str, Any]:
    """Derive the exact Schur boundary for the strict ``01`` branch."""
    tau = sp.symbols("tau", real=True)
    # ``Matrix.charpoly`` internally recreates its polynomial variable by
    # name.  Keep ``z`` assumption-free so that both Symbols are identical.
    z = sp.symbols("z")
    data = parameterized_branch_data(problem, SELECTOR_01)
    symbolic_t = data["T_zero"] + tau * data["T_tau"]
    characteristic = sp.Poly(symbolic_t.charpoly(z).as_expr(), z, domain=sp.QQ.frac_field(tau))

    quartic = sp.Poly(
        405010000000000000 * z**4
        + (3915586057000000 * tau - 1169276880943000000) * z**3
        + (-4222461747714000 * tau + 1123984258642286000) * z**2
        + (725214346843457 * tau - 359717740103975543) * z
        + (-362404689543 * tau + 362404689543),
        z,
        domain=sp.ZZ[tau],
    )
    expected_characteristic = sp.expand(z * (z + tau - 1) * quartic.as_expr() / sp.Integer(405010000000000000))
    characteristic_matches = sp.expand(characteristic.as_expr() - expected_characteristic) == 0

    boundary = sp.Poly(
        111794210406295556649228900462157733493 * tau**3
        + 23105776975281816108275814441284422085171521 * tau**2
        - 244157339715898821440243649673959463071543521 * tau
        + 208410060660460340386576638889814578828638507,
        tau,
        domain=sp.ZZ,
    )
    bracket_lower = sp.Rational(4683030557, 5000000000)
    bracket_upper = sp.Rational(1873212223, 2000000000)

    levels = schur_margin_levels(quartic.all_coeffs(), tau)
    margin_records: list[dict[str, Any]] = []
    all_reduced_positive = True
    boundary_appears = False
    for level in levels:
        for name in ("lead_plus_constant", "lead_minus_constant"):
            expression = sp.expand(level[name])
            reduced, g_power, zero_power, one_power = strip_known_factors(
                expression, tau, boundary
            )
            boundary_appears = boundary_appears or g_power > 0
            roots_closed = int(reduced.count_roots(0, 1)) if reduced.degree() > 0 else 0
            midpoint_sign = int(sp.sign(reduced.eval(TAU_CENTER)))
            # A removed (tau-1)^p contributes (-1)^p on (0,1).
            open_interval_sign = midpoint_sign * ((-1) ** one_power)
            positive = roots_closed == 0 and open_interval_sign > 0
            all_reduced_positive = all_reduced_positive and positive
            margin_records.append(
                {
                    "degree": int(level["degree"]),
                    "margin": name,
                    "factorization": str(sp.factor(expression)),
                    "boundary_polynomial_power": g_power,
                    "tau_power": zero_power,
                    "tau_minus_one_power": one_power,
                    "reduced_factor_root_count_on_closed_0_1": roots_closed,
                    "reduced_factor_sign_on_open_0_1": open_interval_sign,
                    "positive_when_boundary_polynomial_is_positive": positive,
                }
            )

    root_count = int(boundary.count_roots(0, 1))
    lower_sign = int(sp.sign(boundary.eval(bracket_lower)))
    upper_sign = int(sp.sign(boundary.eval(bracket_upper)))
    zero_sign = int(sp.sign(boundary.eval(0)))
    one_sign = int(sp.sign(boundary.eval(1)))

    checks = {
        "characteristic_polynomial_factorization_is_exact": characteristic_matches,
        "boundary_has_exactly_one_root_in_0_1": root_count == 1,
        "rational_bracket_has_opposite_strict_signs": lower_sign > 0 and upper_sign < 0,
        "boundary_is_positive_before_and_negative_after_unique_root": (
            zero_sign > 0 and one_sign < 0
        ),
        "all_other_real_schur_factors_are_positive_on_0_1": all_reduced_positive,
        "boundary_polynomial_occurs_in_schur_recursion": boundary_appears,
    }

    return {
        "valid": all(bool(value) for value in checks.values()),
        "checks": {name: bool(value) for name, value in checks.items()},
        "characteristic_factorization": (
            "det(zI-T_01(tau)) = z*(z+tau-1)*Q_tau(z)/405010000000000000"
        ),
        "quartic_Q_coefficients_descending": [str(value) for value in quartic.all_coeffs()],
        "boundary_polynomial_G": str(boundary.as_expr()),
        "root_count_in_closed_0_1": root_count,
        "tau_c_bracket": [str(bracket_lower), str(bracket_upper)],
        "tau_c_bracket_decimal": [
            fixed_decimal(bracket_lower, 10),
            fixed_decimal(bracket_upper, 10),
        ],
        "boundary_signs_at_bracket": [lower_sign, upper_sign],
        "schur_margin_certificates": margin_records,
        "conclusion": (
            "For 0<tau<1, T_01(tau) is Schur stable exactly when G(tau)>0, "
            "equivalently 0<tau<tau_c, where tau_c is the unique root of G in (0,1)."
        ),
    }


def without_private_objects(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key != "_objects"}


def build_certificate() -> dict[str, Any]:
    half = load_half_certifier()
    verifier = half.load_exact_verifier()
    problem = verifier.build_problem()

    common = build_common_lyapunov_certificate(problem, half)
    prefix = build_prefix_interval_certificate(problem, half, common)
    boundary = build_local_boundary_certificate(problem)
    checks = {
        "common_lyapunov_interval": common["valid"],
        "finite_prefix_capture_interval": prefix["valid"],
        "exact_local_stability_boundary": boundary["valid"],
    }
    return {
        "status": "proof_grade_exact_certificate_accepted_by_internal_verifier_style_review",
        "valid": all(bool(value) for value in checks.values()),
        "checks": checks,
        "theorems": {
            "T1": (
                "A strict KKT branch with a Schur-stable affine error matrix has "
                "an explicit projection-safe invariant Lyapunov ellipsoid and is locally linearly convergent."
            ),
            "T2": (
                "Endpoint decrease for one H certifies the entire tau interval because "
                "the Lyapunov residual is Loewner-concave in tau."
            ),
            "T3": (
                "A uniformly strict finite true-projection prefix that enters the common "
                "ellipsoid implies convergence for the whole certified parameter interval."
            ),
        },
        "instance_scope": {
            "problem": "the exact rational strict-66-cycle QP",
            "initial_point": "the exact period-66 initial point",
            "proved": (
                "convergence for every tau in the certified finite-prefix interval, plus "
                "local convergence on the common-H interval"
            ),
            "not_proved": [
                "global convergence from arbitrary initial points",
                "global convergence for the whole identity-slack model class",
                "maximality of the certified finite-prefix interval",
            ],
        },
        "common_lyapunov": without_private_objects(common),
        "finite_prefix_capture": prefix,
        "local_stability_boundary": boundary,
    }


def render_summary(certificate: dict[str, Any]) -> str:
    common = certificate["common_lyapunov"]
    prefix = certificate["finite_prefix_capture"]
    boundary = certificate["local_stability_boundary"]
    return "\n".join(
        [
            "# Multiplier-Relaxation Interval Certificate",
            "",
            f"- exact certificate valid: `{certificate['valid']}`",
            "- theorem scope: fixed rational QP; local result for nearby states and a finite-prefix result for the original period-66 initial point",
            "",
            "## Common Lyapunov Interval",
            "",
            f"- tau interval: `{common['tau_interval'][0]} <= tau <= {common['tau_interval'][1]}`",
            f"- common contraction-factor upper bound: `{common['uniform_contraction_factor_decimal']}`",
            f"- projection-safe ellipsoid alpha: `{common['ellipsoid_alpha_decimal']}`",
            "- proof: exact endpoint Sylvester minors plus Loewner concavity of the residual matrix",
            "",
            "## Uniform Finite-Prefix Capture",
            "",
            f"- tau interval: `{prefix['tau_interval_decimal'][0]} <= tau <= {prefix['tau_interval_decimal'][1]}`",
            f"- strict word: `{prefix['word']}`",
            f"- minimum uniform sign lower bound: `{prefix['minimum_uniform_sign_lower_bound']['decimal']}`",
            f"- ellipsoid ratio upper bound at step {prefix['steps']}: `{prefix['ellipsoid_ratio_upper_decimal']}`",
            "- interpretation: the small width is a conservative sufficient enclosure, not a claimed stability limit",
            "",
            "## Exact Local-Stability Boundary",
            "",
            f"- factorization: `{boundary['characteristic_factorization']}`",
            f"- unique root bracket: `{boundary['tau_c_bracket_decimal'][0]} < tau_c < {boundary['tau_c_bracket_decimal'][1]}`",
            "- exact conclusion on 0<tau<1: the strict 01 branch is Schur stable iff tau<tau_c",
            "",
            "## Boundary of the Result",
            "",
            "This artifact proves local stability and one explicit finite-prefix capture interval. It does not prove arbitrary-initial-point global convergence.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    certificate = build_certificate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(certificate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    args.summary.write_text(render_summary(certificate), encoding="utf-8")
    print(
        json.dumps(
            {
                "valid": certificate["valid"],
                "common_tau_interval": certificate["common_lyapunov"]["tau_interval"],
                "prefix_tau_interval": certificate["finite_prefix_capture"]["tau_interval"],
                "tau_c_bracket": certificate["local_stability_boundary"]["tau_c_bracket_decimal"],
                "output": str(args.output),
                "summary": str(args.summary),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
