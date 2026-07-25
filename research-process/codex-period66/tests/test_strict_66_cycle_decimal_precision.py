import sympy as sp

from experiments.breakthrough.audit_strict_66_cycle_decimal_precision import (
    exact_cross_audit,
)


def test_four_digit_parameters_pass_both_exact_66_cycle_audits():
    payload = exact_cross_audit(8957, 9990, 4)
    assert payload["mu"] == sp.sstr(sp.Rational(8957, 10000))
    assert payload["nu"] == sp.sstr(sp.Rational(999, 1000))
    assert payload["reduced_certificate_valid"] is True
    assert payload["raw_admm_certificate_valid"] is True
    assert payload["minimum_margin_hashes_match"] is True
    assert sp.Rational(payload["minimum_margin_exact_decimal"]) > sp.Rational(
        1, 1000
    )
