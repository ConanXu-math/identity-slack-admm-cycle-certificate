# Exact Periodic Nonconvergence Certificates for Identity-Slack Three-Block ADMM

[![Exact certificate](https://github.com/ConanXu-math/identity-slack-admm-cycle-certificate/actions/workflows/certificate.yml/badge.svg)](https://github.com/ConanXu-math/identity-slack-admm-cycle-certificate/actions/workflows/certificate.yml)

> **Repository status:** private pre-publication research artifact.  The
> mathematical statement and software interface are frozen for internal
> review, but the public archive DOI, final author list, citation metadata, and
> open-source license have not yet been assigned.

This repository contains the exact-arithmetic certificates accompanying the
manuscript **“Direct Three-Block ADMM Can Cycle with an Identity Slack
Block.”**  It verifies two explicit instances for which the unmodified direct
three-block ADMM has a bounded, strictly admissible, non-KKT periodic
sequence, even though each optimization problem has a unique KKT point.

The repository is a verification package, not a numerical-search archive.  It
contains frozen instances, exact checkers, comparison drivers, route-level
provenance, and machine-readable certificates.

## Certified results

| Certificate ID | Dimension | Certified conclusion | Verification |
| --- | ---: | --- | --- |
| `identity_slack_p66_short_v1` | 2 | Bounded non-KKT sequence of minimal period 66 | reduced Python, full-state Python, MATLAB |
| `identity_slack_p23_dyadic_v1` | 3 | Minimal period-23 non-KKT orbit, locally attracting in canonical `(y,t)` state | exact dyadic replay and Jury stability |

### Period 66

- Model: two-dimensional pure-quadratic problem with `A = B = I_2`, an
  identity nonnegative slack block, and penalty parameter `beta = 1`.
- Instance identifier: `identity_slack_p66_short_v1`.
- Active-set word: `(00)^2(01)^64`.
- Minimal period: `66`.
- Strict projection tests: all `132` signed coordinate inequalities pass.
- Certified minimum signed margin:
  `0.0037105246944352910173... > 1/1000`.
- Proof boundary: bounded periodic nonconvergence only; no claim of unbounded
  divergence or failure of ADMM variants with additional assumptions or
  correction steps.

### Period 23

- Model: three-dimensional strongly convex quadratic problem with a
  nonnegative identity slack block and penalty parameter `beta = 1`.
- Instance identifier: `identity_slack_p23_dyadic_v1`.
- Stored binary64 values are interpreted exactly as dyadic rationals.
- Minimal period: `23`.
- All `69` projection inputs are separated from zero, with exact minimum
  margin greater than `7/1000`.
- The exact 23-step return matrix satisfies the Jury stability criterion, so
  the periodic orbit is locally attracting in the canonical reduced `(y,t)`
  state.  The sign margin is not an explicit basin radius or a parameter
  interval.
- The explicit rational invariant-neighborhood certificate used in the
  manuscript was added after the terminal Kimi run and is not included in
  this terminal-equivalent package.

> [!IMPORTANT]
> The Codex and Kimi Code K3 records in `provenance/` are a descriptive,
> endpoint-aligned comparison of two realized research routes.  The runs were
> not matched in compute, tools, telemetry, or human intervention and do not
> support a causal ranking of model capability.

## Verification architecture

### Period-66 certificate

The Python implementation uses two state representations:

1. `python/signed_cycle_certificate.py` derives and verifies the four-dimensional
   signed recurrence `s = (y, q)`.
2. `python/strict_cycle_certificate.py` independently reconstructs affine maps on the
   six-dimensional unreduced essential state `(y, z, lambda)` by exact basis
   evaluation of the original ADMM updates.

Neither checker imports the other.  `python/verify_certificate_pair.py` regenerates
both JSON certificates and requires exact agreement of the instance, initial
state, orbit, word, KKT point, minimum margin, and canonical hashes.  This is
an internal implementation cross-check, not a second mathematical proof or
external peer review.

`matlab/verify_exact_cycle_matlab.m` is a third implementation written for
MATLAB R2025a and Symbolic Math Toolbox.  Like the raw Python checker, it
independently solves the exact six-dimensional period equation and then
reruns all 66 original ADMM updates with the genuine positive-part
projection.  It does not call Python.  The small Python utility
`python/verify_matlab_certificate.py` only compares the resulting JSON fields with
the frozen Python artifacts.

### Period-23 certificate

`python/verify_period23_certificate.py` loads the frozen binary64 source data,
converts every entry to its exact dyadic-rational value, rebuilds the
six-dimensional `(y,t)` branch maps, and checks instance validity, the unique
KKT point and its raw optimality conditions, strict projection signs, exact
23-step closure, minimality, separation from the KKT point, and exact Jury
stability.  It deterministically regenerates:

- `certificates/period23_certificate.json`;
- `certificates/period23_instance_manifest.json`.

The manifest records shapes, dtypes, binary64 bit patterns, exact dyadic
values, and source/verifier hashes.  Runtime telemetry is intentionally
excluded from the frozen certificate.

## Quick reproduction

The frozen runtime is Python 3.13.5 with SymPy 1.13.3 and NumPy 2.1.3.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python python/verify_all.py
```

Expected terminal summary:

```json
{"checks": [{"name": "period66", "returncode": 0, "status": "passed"}, {"name": "period23", "returncode": 0, "status": "passed"}], "valid": true}
```

The command rewrites the following tracked artifacts deterministically:

- `certificates/certificate_raw.json`
- `certificates/certificate_signed.json`
- `certificates/instance_manifest.json`
- `certificates/period23_certificate.json`
- `certificates/period23_instance_manifest.json`

The MATLAB command similarly rewrites the tracked artifact
`certificates/certificate_matlab.json`.

To confirm that a checkout reproduces the committed certificate exactly, run:

```bash
python python/verify_all.py
python -m unittest discover -s tests -p "test_*.py"
python python/verify_matlab_certificate.py
git diff --exit-code -- certificates/
```

### MATLAB reproduction

Required environment:

- MATLAB R2025a;
- Symbolic Math Toolbox;
- a valid local license, or a MATLAB batch licensing token for a private
  GitHub repository.

From the repository root, run:

```matlab
addpath("matlab")
result = verify_exact_cycle_matlab();
assert(result.valid)
```

This writes `certificates/certificate_matlab.json`.  Then compare the MATLAB output with
the frozen Python artifacts:

```bash
python python/verify_matlab_certificate.py
```

Run the class-based MATLAB regression test with:

```matlab
results = runtests("matlab/tests/VerifyExactCycleMatlabTest.m");
assert(all([results.Passed]))
```

The MATLAB workflow is intentionally manual while the repository is private.
MathWorks requires a batch licensing token for private-project jobs; store it
as the GitHub Actions secret `MLM_LICENSE_TOKEN` before dispatching the
workflow.  When the repository becomes public, the workflow can be enabled on
push without that private-project token requirement.

## Repository layout

```text
.
├── python/        # Python exact implementations and comparison drivers
├── matlab/        # MATLAB implementation, tests, and local instructions
├── certificates/  # Frozen inputs and machine-readable certificate artifacts
├── provenance/    # Route-level accounting and evidence boundaries
├── docs/          # Reproducibility and release documentation
└── .github/       # Continuous-integration workflows and ownership rules
```

| Path | Purpose |
| --- | --- |
| `python/` | Python exact checkers and comparison entry points |
| `python/strict_cycle_certificate.py` | Independent exact checker on `(y,z,lambda)` |
| `python/signed_cycle_certificate.py` | Independent exact checker on `(y,q)` |
| `python/verify_certificate_pair.py` | Regenerates, compares, and hashes both Python certificates |
| `python/verify_period23_certificate.py` | Exact dyadic period-23 replay and Jury verifier |
| `python/verify_all.py` | Runs both certificate paths and propagates failures |
| `matlab/verify_exact_cycle_matlab.m` | Independent exact MATLAB checker on `(y,z,lambda)` |
| `matlab/tests/VerifyExactCycleMatlabTest.m` | Class-based MATLAB regression test |
| `python/verify_matlab_certificate.py` | Compares MATLAB JSON with frozen Python artifacts |
| `certificates/` | Stable source data and machine-readable certificate bundle |
| `provenance/` | Descriptive route records; not a controlled benchmark |
| `docs/REPRODUCIBILITY.md` | Detailed proof-obligation and release contract |
| `.github/workflows/certificate.yml` | Clean GitHub Actions reproduction |
| `.github/workflows/matlab-certificate.yml` | Manual licensed MATLAB reproduction |

## Acceptance rule

The process exits successfully only when every result-specific exact
predicate passes; the period-66 representations must additionally agree on
every shared certificate field.  No floating-point tolerance is used for
period closure, minimality, projection signs, or Jury acceptance.  Decimal
values are included only as readable renderings of exact quantities.

## Versioning and release status

The current private review version is `v0.2.0-private`.  Before a public research
release, the maintainers will:

1. deposit an immutable archive and assign a DOI;
2. freeze the final author and citation metadata;
3. choose and add an explicit software license;
4. link the accepted or public manuscript version;
5. create a public release tag whose commit matches the archived source.

Until those steps are complete, no public license is granted and this private
repository should not be cited as the archival record.

## Contact

Repository owner: [ConanXu-math](https://github.com/ConanXu-math).

For the Chinese overview, see [README.zh-CN.md](README.zh-CN.md).
