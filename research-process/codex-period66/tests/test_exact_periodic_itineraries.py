import itertools

import sympy as sp

from experiments.breakthrough.certify_exact_periodic_itineraries import (
    _farkas_infeasibility_certificate,
    certify_word,
    exact_edge_checks,
    periodic_cell_rows,
    rational_problem,
    run,
)


def test_exact_periodic_itinerary_certificate_counts_short_words():
    payload = run(max_length=2)

    assert payload["word_count"] == 20
    assert payload["distinct_basepoint_count"] <= payload["word_count"]
    assert payload["distinct_inadmissible_basepoint_count"] <= 18
    assert payload["unit_root_word_count"] == 0
    assert payload["unit_root_words"] == []
    assert payload["counts"] == {
        "exact_rational_periodic_itinerary_witness": 2,
        "exact_unique_periodic_point_violates_edge_cell": 18,
    }
    witnesses = [
        record
        for record in payload["records"]
        if record["status"] == "exact_rational_periodic_itinerary_witness"
    ]
    assert all(set(tuple(mask) for mask in record["word"]) == {(1, 0)} for record in witnesses)
    assert all(all(phase["valid"] for phase in record["phases"]) for record in witnesses)
    assert payload["singular_boundary_regression"]["all_singular_words_decided"]


def test_singular_periodic_cells_receive_exact_witness_or_dual_certificate():
    problem = {
        "q1": sp.zeros(1),
        "q2": sp.zeros(1),
        "a": sp.eye(1),
        "b": sp.eye(1),
        "rhs": sp.Matrix([1]),
        "beta": sp.Rational(1),
    }
    records = [
        certify_word(problem, word)
        for length in range(1, 4)
        for word in itertools.product(((0,), (1,)), repeat=length)
    ]
    assert all(record["det_i_minus_p"] == "0" for record in records)
    assert all("requires_parametric_lp" not in record["status"] for record in records)
    assert all(record.get("valid", True) for record in records)
    assert any(
        record["status"] == "exact_rational_periodic_itinerary_witness"
        for record in records
    )
    assert not any(
        record["status"] == "exact_nonconstant_periodic_itinerary_witness"
        for record in records
    )
    assert any(
        record["status"]
        in {
            "exact_singular_periodic_cell_excluded_by_zero_margin_dual",
            "exact_singular_periodic_cell_infeasible_by_farkas",
        }
        for record in records
    )


def test_exact_farkas_certificate_for_weakly_infeasible_cell():
    certificate = _farkas_infeasibility_certificate(
        sp.Matrix([[1]]),
        sp.Matrix([0]),
        sp.Matrix([[1]]),
        sp.Matrix([1]),
    )
    assert certificate["valid"]
    assert certificate["contradiction_gap"] == "-1"
    assert certificate["stationarity_gap"] == ["0"]


def test_exact_pulled_rows_match_phasewise_edge_values():
    problem = rational_problem()
    word = ((0, 1), (1, 0), (1, 1))
    point = sp.Matrix([sp.Rational(1, 3), sp.Rational(2, 5), sp.Rational(4, 7)])
    rows = periodic_cell_rows(problem, word)
    pulled_values = [
        sp.factor((sp.Matrix(item["row"]) * point)[0] + item["constant"])
        for item in rows
    ]
    _, phases = exact_edge_checks(problem, word, point)
    phase_values = [
        sp.Rational(check["value"])
        for phase in phases
        for check in phase["checks"]
    ]
    assert pulled_values == phase_values
