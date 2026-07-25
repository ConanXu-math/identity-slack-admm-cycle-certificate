# Python exact verifiers

This directory owns the Python implementation and cross-check entry points.
Generated artifacts are written to `../certificates/`; no certificate JSON is
stored beside executable code.

## Entry points

- `signed_cycle_certificate.py`: exact four-dimensional signed-state checker.
- `strict_cycle_certificate.py`: independent exact six-dimensional checker.
- `verify_certificate_pair.py`: regenerates both Python certificates and the
  shared manifest.
- `verify_period23_certificate.py`: regenerates the exact dyadic period-23
  replay, source manifest, and Jury-stability certificate.
- `verify_all.py`: runs the period-66 and period-23 certificate paths and
  propagates the first failure.
- `verify_matlab_certificate.py`: compares the frozen MATLAB JSON with the
  Python artifacts.

Run from the repository root:

```bash
python python/verify_all.py
python -m unittest discover -s tests -p "test_*.py"
python python/verify_matlab_certificate.py
git diff --exit-code -- certificates/
```
