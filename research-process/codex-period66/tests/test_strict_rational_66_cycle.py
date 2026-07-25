from experiments.breakthrough.certify_strict_rational_66_cycle import run


def test_strict_rational_66_cycle_counterexample():
    payload = run()
    assert payload["valid"] is True
    assert payload["status"] == "proof_grade_strict_rational_66_cycle_counterexample"
    assert payload["period"] == 66
    assert payload["word_run_length_encoding"] == [[0, 2], [1, 64]]
    assert payload["checks"]["signed_period_closure"] is True
    assert payload["checks"]["all_strict_itinerary_margins"] is True
    assert payload["checks"]["uniform_margin_gt_1_over_1000"] is True
    assert payload["checks"]["all_original_admm_steps_exact"] is True
    assert payload["checks"]["all_zero_linear_original_admm_steps_exact"] is True
    assert payload["checks"]["non_kkt_cycle"] is True
    assert payload["checks"]["word_has_minimal_period_66"] is True
    assert payload["exact_hashes"] == {
        "M": "86f8478f6fc5b0e10d25126b8d368fb50bf948f2b743e412ced4c81bac1e3cc6",
        "N": "5a9a908662d0d57419fd44652c57cb61fd6282b36ea0d3d6acc71ed603f5e608",
        "signed_initial": "2a1f78a3e77262ba62a90e719c9fba639598a66b1acda04cffa01a8ddf7b1884",
        "minimum_margin": "f0c44af06734fbaf4f21446ad0f55ba4bf8e84b86c25e516dd0e9c65868c3fb1",
    }
