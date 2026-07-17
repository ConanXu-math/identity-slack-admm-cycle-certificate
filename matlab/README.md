# MATLAB exact verifier

This directory contains an independently authored MATLAB implementation of
the frozen instance `identity_slack_p66_short_v1`.

## Method

`verify_exact_cycle_matlab.m` performs the following operations using exact
Symbolic Math Toolbox rationals:

1. constructs the pure-quadratic two-dimensional QP from
   `epsilon = 1/1000`, `mu = 8957/10000`, and `nu = 999/1000`;
2. reconstructs the affine branch maps on the unreduced essential state
   `(y,z,lambda)` by basis evaluation;
3. solves the exact period equation for `(00)^2(01)^64`;
4. discards the branch selectors and reruns 66 original ADMM steps using the
   genuine componentwise positive-part projection;
5. checks strict signs, all 132 margins, subproblem equations, multiplier
   updates, KKT conditions, exact closure, and absence of an earlier return;
6. compares shared exact fields with the Python-generated
   `instance_manifest.json`.

The MATLAB checker does not call the Python checkers.  The separate Python
script `verify_matlab_certificate.py` only compares the generated JSON output
with the frozen Python artifacts.

## Requirements

- MATLAB R2025a
- Symbolic Math Toolbox
- a valid MATLAB license

## Run

From the repository root:

```matlab
addpath("matlab")
result = verify_exact_cycle_matlab();
assert(result.valid)
```

The default output is `certificate_matlab.json` in the repository root.
After generation, run:

```bash
python verify_matlab_certificate.py
```

## Test

```matlab
results = runtests("matlab/tests/VerifyExactCycleMatlabTest.m");
assert(all([results.Passed]))
```

The manual GitHub Actions workflow uses the official `matlab-actions` v3
actions.  A private repository must provide a MATLAB batch licensing token as
the secret `MLM_LICENSE_TOKEN`.
