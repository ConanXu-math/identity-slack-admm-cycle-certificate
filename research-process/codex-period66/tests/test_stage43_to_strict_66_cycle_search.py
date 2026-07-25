import pytest

from experiments.breakthrough.search_stage43_to_strict_66_cycle import (
    candidate_seed,
    evaluate_periodic_word,
)


def test_recovered_seed_for_discovery_word():
    assert candidate_seed(2, 64) == 20260978


def test_rounded_stage44_parameters_retain_a_strict_positive_margin():
    evaluation = evaluate_periodic_word(
        mu=0.89581516,
        nu=0.99883501,
        zero_count=2,
        one_count=64,
    )
    assert evaluation is not None
    assert evaluation["minimum_margin"] == pytest.approx(
        0.00434107968440684942,
        rel=1.0e-10,
        abs=1.0e-12,
    )
    assert evaluation["minimum_margin_phase"] == 0
    assert evaluation["minimum_margin_coordinate"] == 1
    assert evaluation["floating_closure_error_inf"] < 1.0e-11
