"""Regression tests for the exact multiplier-relaxation interval certificate."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import sympy as sp


TEST_ROOT = Path(__file__).resolve().parent
PYTHON_ROOT = TEST_ROOT.parent
SCRIPT = PYTHON_ROOT / "certify_relaxed_multiplier_interval_theory.py"


def load_module():
    spec = importlib.util.spec_from_file_location("tau_interval_certificate", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def built_certificate():
    module = load_module()
    return module, module.build_certificate()


def test_parameterized_branch_matrix_matches_direct_original_updates(built_certificate):
    module, _ = built_certificate
    half = module.load_half_certifier()
    problem = half.load_exact_verifier().build_problem()
    for selector in (module.SELECTOR_00, module.SELECTOR_01):
        data = module.parameterized_branch_data(problem, selector)
        for tau in (sp.Rational(2, 5), sp.Rational(1, 2), sp.Rational(3, 5)):
            matrix, offset = module.evaluate_branch(data, tau)
            direct_matrix, direct_offset, direct_c, direct_d = module.direct_affine_data(
                problem, selector, tau
            )
            assert matrix == direct_matrix
            assert offset == direct_offset
            assert data["C"] == direct_c
            assert data["d"] == direct_d


def test_common_lyapunov_interval_is_exactly_certified(built_certificate):
    module, certificate = built_certificate
    common = certificate["common_lyapunov"]
    assert common["valid"] is True
    assert common["tau_interval"] == ["49/100", "51/100"]
    assert all(common["checks"].values())
    assert all(
        endpoint["all_sylvester_minors_positive"]
        for endpoint in common["endpoint_certificates"]
    )

    # Independent algebraic check of the chord identity used in Theorem 2.
    half = module.load_half_certifier()
    problem = half.load_exact_verifier().build_problem()
    data = module.parameterized_branch_data(problem, module.SELECTOR_01)
    matrix_half, _ = module.evaluate_branch(data, module.TAU_CENTER)
    matrix_lower, _ = module.evaluate_branch(data, module.COMMON_TAU_LOWER)
    matrix_upper, _ = module.evaluate_branch(data, module.COMMON_TAU_UPPER)
    h_matrix = half.exact_discrete_lyapunov(matrix_half)
    f_half = h_matrix - matrix_half.T * h_matrix * matrix_half
    f_lower = h_matrix - matrix_lower.T * h_matrix * matrix_lower
    f_upper = h_matrix - matrix_upper.T * h_matrix * matrix_upper
    chord_gap = sp.simplify(f_half - (f_lower + f_upper) / 2)
    expected_gap = sp.simplify(
        ((module.COMMON_TAU_UPPER - module.COMMON_TAU_LOWER) ** 2 / 4)
        * data["T_tau"].T
        * h_matrix
        * data["T_tau"]
    )
    assert chord_gap == expected_gap


def test_original_initial_point_has_a_nonempty_uniform_capture_interval(
    built_certificate,
):
    _, certificate = built_certificate
    prefix = certificate["finite_prefix_capture"]
    assert prefix["valid"] is True
    assert prefix["tau_interval"] == [
        "4999999999/10000000000",
        "5000000001/10000000000",
    ]
    assert prefix["steps"] == 232
    assert prefix["minimum_uniform_sign_lower_bound"]["sign"] == 1
    assert prefix["ellipsoid_slack"]["sign"] == 1


def test_both_capture_interval_endpoints_pass_direct_exact_replay(built_certificate):
    module, certificate = built_certificate
    half = module.load_half_certifier()
    verifier = half.load_exact_verifier()
    problem = verifier.build_problem()
    initial, _ = verifier.solve_period_equation(problem)
    kkt = (
        problem["y_star"]
        .col_join(problem["z_star"])
        .col_join(problem["lambda_star"])
    )
    data_01 = module.parameterized_branch_data(problem, module.SELECTOR_01)
    t_half, _ = module.evaluate_branch(data_01, module.TAU_CENTER)
    h_matrix = half.exact_discrete_lyapunov(t_half)
    c_matrix = data_01["C"]
    q_star = sp.Matrix([-1, 1])
    inverse_h = h_matrix.inv()
    alpha = min(
        sp.factor(q_star[index] ** 2 / (c_matrix.row(index) * inverse_h * c_matrix.row(index).T)[0])
        for index in range(2)
    )

    for tau in (module.PREFIX_TAU_LOWER, module.PREFIX_TAU_UPPER):
        state = initial
        masks = []
        for step in range(1, module.PREFIX_STEPS + 1):
            branch = module.expected_mask(step)
            data = module.parameterized_branch_data(
                problem,
                module.SELECTOR_00 if branch == "00" else module.SELECTOR_01,
            )
            matrix, offset = module.evaluate_branch(data, tau)
            q_value = data["C"] * state + data["d"]
            masks.append("".join("1" if value > 0 else "0" for value in q_value))
            state = matrix * state + offset
        error = state - kkt
        assert masks[:2] == ["00", "00"]
        assert all(value == "01" for value in masks[2:])
        assert (error.T * h_matrix * error)[0] < alpha


def test_exact_schur_boundary_has_a_unique_rationally_bracketed_root(
    built_certificate,
):
    _, certificate = built_certificate
    boundary = certificate["local_stability_boundary"]
    assert boundary["valid"] is True
    assert boundary["root_count_in_closed_0_1"] == 1
    assert boundary["tau_c_bracket_decimal"] == ["0.9366061114", "0.9366061115"]
    assert boundary["boundary_signs_at_bracket"] == [1, -1]
    assert all(
        record["positive_when_boundary_polynomial_is_positive"]
        for record in boundary["schur_margin_certificates"]
    )


def test_full_certificate_keeps_the_global_nonclaim_explicit(built_certificate):
    _, certificate = built_certificate
    assert certificate["valid"] is True
    assert "global convergence from arbitrary initial points" in (
        certificate["instance_scope"]["not_proved"]
    )
