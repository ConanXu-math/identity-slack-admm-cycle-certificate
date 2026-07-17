# Python exact verifiers

This directory owns the Python implementation and cross-check entry points.
Generated artifacts are written to `../certificates/`; no certificate JSON is
stored beside executable code.

## Entry points

- `signed_cycle_certificate.py`: exact four-dimensional signed-state checker.
- `strict_cycle_certificate.py`: independent exact six-dimensional checker.
- `verify_certificate_pair.py`: regenerates both Python certificates and the
  shared manifest.
- `verify_matlab_certificate.py`: compares the frozen MATLAB JSON with the
  Python artifacts.

Run from the repository root:

```bash
python python/verify_certificate_pair.py
python python/verify_matlab_certificate.py
git diff --exit-code -- certificates/
```
