import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import sympy as sp


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "experiments" / "breakthrough" / "certify_fixed_qp_signed_pwa.py"
NOTE = ROOT / "notes" / "fixed_qp_signed_pwa_contraction_theorem.md"


def _load_module():
    spec = importlib.util.spec_from_file_location("fixed_qp_signed_pwa", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


MODULE = _load_module()


def test_pd_checker_rejects_nonsymmetric_input():
    with pytest.raises(ValueError, match="exactly symmetric"):
        MODULE._positive_definite(sp.Matrix([[2, 1], [0, 2]]))


def _signed_map(state: np.ndarray) -> np.ndarray:
    data = MODULE.exact_data()
    m = np.asarray(data["m"], dtype=float)
    n = np.asarray(data["n"], dtype=float)
    y, q = state[:2], state[2:]
    p = m @ y - (np.eye(2) - m) @ np.abs(q)
    return np.concatenate((n @ p, (np.eye(2) - n) @ p + np.maximum(q, 0.0)))


def _original_admm_step(y: np.ndarray, z: np.ndarray, lam: np.ndarray):
    data = MODULE.exact_data()
    q1 = np.asarray(data["q1"], dtype=float)
    q2 = np.asarray(data["q2"], dtype=float)
    identity = np.eye(2)
    x_next = np.linalg.solve(q1 + identity, lam - y - z)
    y_next = np.linalg.solve(q2 + identity, lam - x_next - z)
    q_next = lam - x_next - y_next
    z_next = np.maximum(q_next, 0.0)
    lam_next = q_next - z_next
    return x_next, y_next, z_next, lam_next


def test_exact_jacobians_facets_and_edge_conjugacy():
    certificate = MODULE.build_certificate()
    assert certificate["valid"]
    assert certificate["review_status"] == "see_external_review_manifest"
    assert certificate["gamma"] == "99/100"
    assert certificate["Q2"] == [["4421/779", "2500/779"], ["2500/779", "1921/779"]]
    assert certificate["Q2_positive_check"]["positive"]
    assert len(certificate["jacobians"]) == 4
    assert len(certificate["edge_relations"]) == 16
    assert len(certificate["facet_checks"]) == 4
    assert all(item["matches_original_admm_elimination"] for item in certificate["jacobians"])
    assert all(item["contraction_check"]["positive"] for item in certificate["jacobians"])
    assert all(item["equals_signed_jacobian"] for item in certificate["edge_relations"])
    assert all(item["continuous"] for item in certificate["facet_checks"])


def test_instance_is_exactly_outside_old_small_gain_gate():
    gate = MODULE.build_certificate()["gate_exterior"]
    assert gate["a_bound_fails"]
    assert gate["b_bound_fails"]
    assert gate["a_residual_determinant"] == "-36725879/2073600000000"
    assert gate["b_residual_determinant"] == "-36725879/25600000000"


def test_region_jacobian_matches_direct_signed_map_including_ties():
    states = [
        np.array([0.3, -0.7, 0.2, -0.4]),
        np.array([-0.5, 0.1, -0.3, 0.8]),
        np.array([0.2, 0.4, 0.0, -0.6]),
        np.array([-0.1, 0.9, 0.0, 0.0]),
    ]
    for state in states:
        mask = tuple(int(value >= 0.0) for value in state[2:])
        matrix = np.asarray(MODULE.signed_jacobian(mask), dtype=float)
        np.testing.assert_allclose(matrix @ state, _signed_map(state), atol=1.0e-14, rtol=0.0)


def test_signed_map_matches_independent_original_admm_oracle():
    states = [
        np.array([0.3, -0.7, 0.2, -0.4]),
        np.array([-0.5, 0.1, -0.3, 0.8]),
        np.array([0.2, 0.4, 0.0, -0.6]),
        np.array([-0.1, 0.9, 0.0, 0.0]),
    ]
    for state in states:
        y, q = state[:2], state[2:]
        z, lam = np.maximum(q, 0.0), np.minimum(q, 0.0)
        _, y_next, z_next, lam_next = _original_admm_step(y, z, lam)
        np.testing.assert_allclose(
            np.concatenate((y_next, z_next + lam_next)),
            _signed_map(state),
            atol=1.0e-14,
            rtol=0.0,
        )


def test_arbitrary_initial_state_enters_signed_recurrence_after_one_step():
    y = np.array([0.7, -1.1])
    z = np.array([-0.4, 0.9])
    lam = np.array([0.8, -0.2])
    _, y, z, lam = _original_admm_step(y, z, lam)
    for _ in range(5):
        signed = np.concatenate((y, z + lam))
        expected = _signed_map(signed)
        _, y, z, lam = _original_admm_step(y, z, lam)
        np.testing.assert_allclose(
            np.concatenate((y, z + lam)), expected, atol=1.0e-14, rtol=0.0
        )


def test_global_incremental_contraction_on_cross_orthant_sanity_pairs():
    h = np.asarray(MODULE.exact_data()["h"], dtype=float)
    gamma = 0.99
    pairs = [
        (np.array([1.0, -2.0, 3.0, -4.0]), np.array([-2.0, 1.0, -1.0, 5.0])),
        (np.array([0.0, 0.0, -1.0, -1.0]), np.array([0.0, 0.0, 1.0, 1.0])),
        (np.array([0.2, -0.1, 0.0, 2.0]), np.array([-0.3, 0.8, 0.0, -2.0])),
    ]
    for left, right in pairs:
        image_gap = _signed_map(left) - _signed_map(right)
        state_gap = left - right
        assert image_gap @ h @ image_gap <= gamma**2 * (state_gap @ h @ state_gap) + 1.0e-12


def test_cli_and_chinese_theorem_card(tmp_path):
    json_path = tmp_path / "signed_pwa.json"
    markdown_path = tmp_path / "signed_pwa.md"
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--json-output", str(json_path), "--markdown-output", str(markdown_path)],
        cwd=ROOT,
        env=env,
        check=True,
    )
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    report = markdown_path.read_text(encoding="utf-8")
    note = NOTE.read_text(encoding="utf-8")
    assert payload["valid"]
    assert "Signed-State PWA exact 证书" in report
    assert "全局增量收缩" in note
    assert "Fixed Point 与 KKT 等价" in note
