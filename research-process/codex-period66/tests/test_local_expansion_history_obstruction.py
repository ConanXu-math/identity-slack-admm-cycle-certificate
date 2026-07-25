from experiments.breakthrough.certify_local_expansion_history_obstruction import run


def test_local_expansion_history_lyapunov_obstruction():
    payload = run()
    assert payload["valid"] is True
    assert (
        payload["status"]
        == "exact_strict_kkt_local_expansion_history_lyapunov_obstruction"
    )
    assert payload["checks"]["strict_signed_orthant"] is True
    assert payload["checks"]["signed_recurrence_fixed_point"] is True
    assert payload["checks"]["negative_jury_mid"] is True
