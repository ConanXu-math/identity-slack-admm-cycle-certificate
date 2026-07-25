import numpy as np

from experiments.breakthrough.optimize_nonconstant_periodic_margin import (
    canonical_margin,
    canonical_words,
    periodic_margin,
    run,
)


def test_canonical_word_reduction_counts_length_two_and_three():
    words = canonical_words((2, 3))
    assert len(words) == 15
    assert sum(len(word) == 2 for word in words) == 4
    assert sum(len(word) == 3 for word in words) == 11


def test_periodic_margin_returns_all_pulled_cell_rows():
    word = ((0, 1), (1, 0), (1, 1))
    parameters = np.array([0.4, 0.7, 0.2, 0.3, 0.8, -0.4, 0.5])
    result = periodic_margin(parameters, word, rhs_chart=0)
    assert result is not None
    assert len(result["strict_values"]) + len(result["weak_values"]) == 4 * len(word)
    assert len(result["phase_states"]) == len(word)
    assert np.isfinite(result["periodicity_condition"])


def test_weak_rows_do_not_limit_strict_margin_once_feasible():
    strict_margin, weak_minimum, score = canonical_margin(
        [0.4, 0.2], [0.0, 0.3]
    )
    assert strict_margin == 0.2
    assert weak_minimum == 0.0
    assert score == 0.2

    _, weak_minimum, score = canonical_margin([0.4, 0.2], [-0.1, 0.3])
    assert weak_minimum == -0.1
    assert score == -0.1


def test_small_optimization_run_is_reproducible():
    first = run((2,), seed=7, maxiter=1, popsize=4, rhs_bound=2.0)
    second = run((2,), seed=7, maxiter=1, popsize=4, rhs_bound=2.0)
    assert first["canonical_word_count"] == 4
    assert first["best_margin"] == second["best_margin"]
    assert first["records"][0]["word"] == second["records"][0]["word"]
