# Changelog

All notable changes to the certificate package will be recorded here.

## Unreleased

- Keep `paper/` PDF-only and remove the TeX source, bibliography, figure
  sources, and manuscript working files from the repository.

## v0.3.0-private - 2026-07-18

- Separate Python sources, MATLAB sources, generated certificates, and
  reproducibility documentation into dedicated top-level directories.
- Add the arXiv manuscript source, compiled PDF, bibliography, and vector
  figures under `paper/`.
- Prove that the strict primitive period-66 orbit persists on an open
  parameter neighborhood, while keeping the explicit rational instance as
  the frozen reproducibility target.
- Add exact multiplier-relaxation certificates for a common Lyapunov interval
  `tau in [49/100, 51/100]`, a 232-step fixed-initialization capture interval,
  and the local Schur boundary
  `0.9366061114 < tau_c < 0.9366061115`.
- Add targeted regression tests and run the relaxation certificate in the
  Python continuous-integration workflow.

## v0.2.0-private - 2026-07-18

- Add an independently authored MATLAB R2025a / Symbolic Math Toolbox
  verifier on the six-dimensional unreduced essential state.
- Add a class-based MATLAB regression test and a manual licensed GitHub
  Actions workflow.
- Add an exact JSON comparator for MATLAB/Python shared certificate fields.
- Add the stable MATLAB-generated JSON certificate and require its exact
  agreement with the frozen Python artifacts in continuous integration.
- Document the private-repository batch-token requirement and preserve the
  earlier 2026-07-15 Python-only package as historical provenance rather than
  treating it as the MATLAB implementation of the frozen instance.

## v0.1.0-private - 2026-07-17

- Freeze the rational instance `identity_slack_p66_short_v1`.
- Include separately implemented signed-state and six-dimensional exact
  checkers.
- Include stable raw, signed, and comparison JSON artifacts.
- Pin Python 3.13.5 and SymPy 1.13.3 for reproducibility.
- Add private pre-publication documentation and GitHub Actions verification.
