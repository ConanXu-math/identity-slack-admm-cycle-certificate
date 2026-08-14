# Python exact verifiers

This directory owns the Python implementation and cross-check entry points.
Generated artifacts are written to `../certificates/`; no certificate JSON is
stored beside executable code.

## Entry points

- `signed_cycle_certificate.py`: exact four-dimensional signed-state checker.
- `strict_cycle_certificate.py`: independent exact six-dimensional checker.
- `verify_certificate_pair.py`: regenerates both Python certificates and the
  shared manifest.
- `verify_period23_certificate.py`: regenerates the exact rational period-23
  replay, full phase-zero initialization, 23-step return map, Lyapunov, and
  invariant-neighborhood certificate.
- `verify_all.py`: runs the period-66 and period-23 certificate paths and
  propagates the first failure.
- `verify_matlab_certificate.py`: compares the frozen MATLAB JSON with the
  Python artifacts.
- `export_orbit_66.py`: writes all 66 cyclic phases as exact and decimal data.
- `certify_relaxed_multiplier_half_convergence.py`: exact `tau = 1/2` base
  certificate.
- `analyze_identity_slack_universal_step_obstruction.py`: exact obstruction to a
  problem-independent relative multiplier step.
- `analyze_identity_slack_small_step_local_instability.py`: companion local
  instability family used by the universal-step obstruction.
- `verify_universal_step_obstruction.py`: regenerate/check the tracked
  universal-step obstruction certificate.
- `verify_kimi_provenance.py`: verify the sanitized Kimi route ledger,
  terminal bytes, accounting, frozen-start inventory, and route file hashes.
- `certify_relaxed_multiplier_interval_theory.py`: exact common-Lyapunov,
  finite-prefix capture, and local-Schur certificates.
- `tests/test_relaxed_multiplier_interval_theory.py`: direct-replay and
  algebraic regression tests for the relaxation result.

Run from the repository root:

```bash
python python/verify_all.py
python python/verify_kimi_provenance.py --check
python -m unittest discover -s tests -p "test_*.py"
python python/verify_matlab_certificate.py
python python/export_orbit_66.py
python python/certify_relaxed_multiplier_interval_theory.py
python python/verify_universal_step_obstruction.py --check
python -m pytest -q python/tests/test_relaxed_multiplier_interval_theory.py
git diff --exit-code -- certificates/
```
