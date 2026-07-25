import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "experiments" / "breakthrough" / "analyze_relaxed_multiplier_66_cycle.py"


def load_module():
    spec = importlib.util.spec_from_file_location("relaxed_multiplier_66_cycle", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_tau_one_reproduces_the_full_state_66_cycle():
    module = load_module()
    witness = module.build_witness()
    state = witness.initial.copy()
    for _ in range(66):
        state, _, _, _ = module.relaxed_step(state, witness, tau=1.0)
    assert np.linalg.norm(state - witness.initial) < 1.0e-10
    assert np.linalg.norm(state - witness.kkt_state) > 1.0e-4


def test_kkt_state_is_fixed_for_every_positive_tau():
    module = load_module()
    witness = module.build_witness()
    for tau in (1.0, 0.5, 0.1):
        state, _, _, residual = module.relaxed_step(
            witness.kkt_state, witness, tau=tau
        )
        assert np.linalg.norm(residual) < 1.0e-12
        assert np.linalg.norm(state - witness.kkt_state) < 1.0e-12


def test_relaxed_multiplier_formula_changes_only_the_dual_increment():
    module = load_module()
    witness = module.build_witness()
    full_state, full_x, full_q, full_residual = module.relaxed_step(
        witness.initial, witness, tau=1.0
    )
    half_state, half_x, half_q, half_residual = module.relaxed_step(
        witness.initial, witness, tau=0.5
    )
    assert np.allclose(full_x, half_x)
    assert np.allclose(full_q, half_q)
    assert np.allclose(full_residual, half_residual)
    assert np.allclose(full_state[:4], half_state[:4])
    old_lambda = witness.initial[4:6]
    assert np.allclose(half_state[4:6], old_lambda - 0.5 * half_residual)
    assert np.allclose(full_state[4:6], old_lambda - full_residual)


def test_local_kkt_branch_crosses_the_unit_circle_between_0935_and_0940():
    module = load_module()
    witness = module.build_witness()
    assert module.local_spectral_radius(witness, 0.935) < 1.0
    assert module.local_spectral_radius(witness, 0.940) > 1.0
    threshold = module.local_stability_threshold(witness)
    assert 0.936 < threshold < 0.937
