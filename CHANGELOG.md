# Changelog

All notable changes to the certificate package will be recorded here.

## Unreleased

- Separate Python sources, MATLAB sources, generated certificates, and
  reproducibility documentation into dedicated top-level directories.
- Add the frozen Kimi Code K3 period-23 binary64 source, its exact
  dyadic-rational replay, source manifest, and exact Jury-stability
  certificate.
- Add a unified Python verification entry point, regression tests, and CI
  coverage for both the period-66 and period-23 certificates.
- Add route-level provenance and explicit limits for the descriptive,
  endpoint-aligned Codex/Kimi comparison.

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
