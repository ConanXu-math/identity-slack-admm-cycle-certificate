import importlib.util
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "experiments" / "breakthrough" / "search_phase_edge_certificate.py"


def _module():
    spec = importlib.util.spec_from_file_location("search_phase_edge_certificate", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_builds_four_phases_and_all_sixteen_edges_without_cvxpy():
    module = _module()
    data = module.build_phase_edge_data()

    assert data.masks == ((0, 0), (0, 1), (1, 0), (1, 1))
    assert len(data.core) == 4
    assert len(data.edges) == 16
    assert data.matrix_size == 5
    for (source, target), form in data.edges.items():
        np.testing.assert_allclose(form.source_energy, data.core[source])
        assert form.transition_lift.shape == (5, 5)
        assert form.dissipation_map.shape == (6, 5)
        assert form.region_rows.shape == (4, 5)
        np.testing.assert_array_equal(
            form.region_strict, np.asarray(source + target, dtype=bool)
        )


def test_audit_reports_exact_core_candidate_residuals():
    module = _module()
    data = module.build_phase_edge_data()
    # This is deliberately not feasible: it tests deterministic residual
    # accounting, not the numerical solver or certificate existence.
    phase = {mask: data.core[mask].copy() for mask in data.masks}
    multipliers = {
        edge: np.zeros((form.region_rows.shape[0], form.region_rows.shape[0]))
        for edge, form in data.edges.items()
    }
    audit = module.audit_candidate(data, 0.0, phase, multipliers, 1.0)

    assert audit["correction_trace"] == 0.0
    assert audit["trace_budget_slack"] == 1.0
    assert audit["worst"]["max_homogeneous_last_row_residual"] == 0.0
    assert audit["worst"]["min_core_dominance_eigenvalue"] == 0.0
    assert audit["worst"]["min_multiplier_eigenvalue"] == 0.0
    assert audit["worst"]["min_multiplier_entry"] == 0.0
    for edge, form in data.edges.items():
        expected = form.energy_difference
        item = audit["edges"][module._edge_key(edge)]
        np.testing.assert_allclose(
            item["min_residual_eigenvalue"],
            np.linalg.eigvalsh(expected).min(),
            atol=1.0e-12,
        )


def test_audit_checks_shapes_and_report_marks_numerical_screen():
    module = _module()
    data = module.build_phase_edge_data()
    phase = {mask: data.core[mask].copy() for mask in data.masks}
    multipliers = {
        edge: np.zeros((4, 4)) for edge in data.edges
    }
    bad_phase = dict(phase)
    bad_phase[(0, 0)] = np.zeros((4, 4))
    with np.testing.assert_raises_regex(ValueError, r"H\[\(0, 0\)\]"):
        module.audit_candidate(data, 0.0, bad_phase, multipliers, 1.0)

    result = {
        "status": "optimal_inaccurate",
        "objective": 0.1,
        "epsilon": 0.1,
        "H": {},
        "multipliers": {},
        "audit": {},
    }
    report = module.build_report(result, "SCS", 100.0)
    assert report["evidence_kind"] == "numerical_screen"
    assert "not an exact certificate" in report["claim_scope"]
    assert report["model"]["edge_count"] == 16
    assert report["model"]["trace_budget"] == 100.0
