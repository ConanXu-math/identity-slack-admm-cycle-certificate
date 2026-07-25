import importlib.util
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

from experiments.slack_admm_core import AdmmState, SlackQpProblem
from src.admm_identity.edge_energy import build_edge_energy_quadratic_form


SCRIPT = (
    Path(__file__).parents[1]
    / "experiments"
    / "breakthrough"
    / "certify_phase_edge_rational.py"
)
SPEC = importlib.util.spec_from_file_location("certify_phase_edge_rational", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _float_problem():
    return SlackQpProblem(
        q1=3.0 * np.eye(2),
        q2=np.array([[7.0, 4.0], [4.0, 3.0]]),
        a=np.eye(2),
        bmat=np.eye(2),
        rhs=np.zeros(2),
        beta=1.0,
    )


def test_certificate_has_four_phases_and_sixteen_edges():
    certificate = MODULE.build_certificate()
    assert certificate["status"] == "exact_certificate"
    assert certificate["phase_count"] == 4
    assert certificate["edge_count"] == 16
    assert len(certificate["phases"]) == 4
    assert len(certificate["edges"]) == 16


def test_every_exact_principal_minor_is_nonnegative():
    certificate = MODULE.build_certificate()
    phase_minors = [
        minor
        for phase in certificate["phases"]
        for minor in phase["difference_principal_minors"]
    ]
    edge_minors = [
        minor
        for edge in certificate["edges"]
        for minor in edge["residual_principal_minors"]
    ]
    assert len(phase_minors) == 4 * 15
    assert len(edge_minors) == 16 * 15
    assert all(minor["sign"] >= 0 for minor in phase_minors + edge_minors)


def test_principal_minor_check_rejects_nonsymmetric_matrix():
    with pytest.raises(ValueError, match="symmetric"):
        MODULE.principal_minors(sp.Matrix([[1, 1], [0, 1]]))


def test_exact_maps_match_float_edge_energy_for_all_edges():
    problem = _float_problem()
    kkt = AdmmState(
        x=np.zeros(2), y=np.zeros(2), z=np.zeros(2), lam=np.zeros(2)
    )
    for source in MODULE.MASKS:
        for target in MODULE.MASKS:
            exact_transition, exact_dissipation = MODULE.edge_matrices(source, target)
            form = build_edge_energy_quadratic_form(
                problem,
                kkt,
                np.array(source, dtype=bool),
                np.array(target, dtype=bool),
            )
            np.testing.assert_allclose(
                np.asarray(exact_transition, dtype=float),
                form.transition_lift[:-1, :-1],
                atol=1.0e-14,
                rtol=0.0,
            )
            np.testing.assert_allclose(
                np.asarray(exact_dissipation, dtype=float),
                form.dissipation_map[:, :-1],
                atol=1.0e-14,
                rtol=0.0,
            )
            np.testing.assert_allclose(
                np.asarray(MODULE.core_energy(source), dtype=float),
                form.source_energy[:-1, :-1],
                atol=1.0e-14,
                rtol=0.0,
            )
