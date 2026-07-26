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
  replay, full phase-zero initialization, Lyapunov, and
  invariant-neighborhood certificate.
- `verify_all.py`: runs the period-66 and period-23 certificate paths and
  propagates the first failure.
- `verify_matlab_certificate.py`: compares the frozen MATLAB JSON with the
  Python artifacts.
- `export_orbit_66.py`: writes all 66 cyclic phases as exact and decimal data.
- `certify_relaxed_multiplier_half_convergence.py`: exact `tau = 1/2` base
  certificate.
- `certify_relaxed_multiplier_interval_theory.py`: exact common-Lyapunov,
  finite-prefix capture, and local-Schur certificates.
- `tests/test_relaxed_multiplier_interval_theory.py`: direct-replay and
  algebraic regression tests for the relaxation result.

Run from the repository root:

```bash
python python/verify_all.py
python -m unittest discover -s tests -p "test_*.py"
python python/verify_matlab_certificate.py
python python/export_orbit_66.py
python python/certify_relaxed_multiplier_interval_theory.py
python -m pytest -q python/tests/test_relaxed_multiplier_interval_theory.py
git diff --exit-code -- certificates/
```
