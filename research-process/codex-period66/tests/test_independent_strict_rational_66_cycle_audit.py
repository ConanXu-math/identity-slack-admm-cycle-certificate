from experiments.breakthrough.audit_strict_rational_66_cycle_independent import run


def test_independent_raw_admm_audit_of_strict_rational_66_cycle():
    payload = run()
    assert payload["valid"] is True
    assert payload["status"] == "independent_exact_raw_admm_audit_passed"
    assert payload["period"] == 66
    assert payload["checks"]["linear_cycle_closes"] is True
    assert payload["checks"]["zero_linear_cycle_closes"] is True
    assert payload["checks"]["all_x_subproblems_exact"] is True
    assert payload["checks"]["all_y_subproblems_exact"] is True
    assert payload["checks"]["all_projection_steps_exact"] is True
    assert (
        payload["checks"]["raw_projection_itinerary_matches_word"] is True
    )
    assert payload["checks"]["all_multiplier_steps_exact"] is True
    assert payload["checks"]["all_state_conjugacies_exact"] is True
    assert payload["checks"]["uniform_margin_gt_1_over_1000"] is True
    assert payload["checks"]["no_earlier_return_before_66"] is True
    assert payload["exact_hashes"] == {
        "linear_initial_full_state": "00c0ecacfa976b3a6b49e0e1c7020a8030612f515bb475c9c522021e265961b7",
        "zero_linear_initial_full_state": "794191227fa1c88df642d69ec2e0dd42d44f907c779774234ebfbe933b59924e",
        "minimum_margin": "f0c44af06734fbaf4f21446ad0f55ba4bf8e84b86c25e516dd0e9c65868c3fb1",
    }
