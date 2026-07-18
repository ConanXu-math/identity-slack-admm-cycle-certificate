# Exact Period-66 Certificate for Identity-Slack Three-Block ADMM

[![Exact certificate](https://github.com/ConanXu-math/identity-slack-admm-cycle-certificate/actions/workflows/certificate.yml/badge.svg)](https://github.com/ConanXu-math/identity-slack-admm-cycle-certificate/actions/workflows/certificate.yml)

> **Repository status:** private pre-publication research artifact.  The
> mathematical statement and software interface are frozen for internal
> review, but the public archive DOI, final author list, citation metadata, and
> open-source license have not yet been assigned.

This repository contains the exact-arithmetic certificate accompanying the
manuscript **“Direct Three-Block ADMM Can Cycle with an Identity Slack
Block.”**  It verifies an explicit rational instance for which the unmodified
direct three-block ADMM has a bounded, strictly admissible, non-KKT periodic
orbit of minimal period 66, even though the optimization problem has a unique
KKT point.  The manuscript also proves that the strict primitive cycle
persists on an open parameter neighborhood and gives exact, deliberately
local certificates showing how multiplier relaxation stabilizes the frozen
instance near `tau = 1/2`.

The repository is a verification package, not a numerical-search archive.  It
contains the frozen instance, separately implemented Python and MATLAB exact
checkers, comparison drivers, tests, machine-readable certificates, and the
compiled manuscript PDF.  Exploratory search histories and manuscript
authoring sources remain outside this release.

## Certified statement

- Model: two-dimensional pure-quadratic problem with `A = B = I_2`, an
  identity nonnegative slack block, and penalty parameter `beta = 1`.
- Instance identifier: `identity_slack_p66_short_v1`.
- Active-set word: `(00)^2(01)^64`.
- Minimal period: `66`.
- Strict projection tests: all `132` signed coordinate inequalities pass.
- Certified minimum signed margin:
  `0.0037105246944352910173... > 1/1000`.
- The strict primitive word and its period-66 orbit persist on an open
  neighborhood of the rational parameters.
- Proof boundary: bounded periodic nonconvergence; no claim of unbounded
  divergence or failure of every modified ADMM scheme.

## Certified multiplier-relaxation results

For the same rational QP, with the multiplier step changed from `1` to `tau`,
the exact certificate proves three narrower statements:

- one rational Lyapunov matrix works on the strict KKT branch for every
  `tau in [49/100, 51/100]`;
- the former period-66 initial state follows the certified strict prefix for
  232 steps and enters the invariant Lyapunov ellipsoid for every
  `tau in [1/2 - 10^-10, 1/2 + 10^-10]`;
- the strict KKT branch has a unique Schur boundary in `(0,1)`, bracketed by
  `0.9366061114 < tau_c < 0.9366061115`.

These statements do **not** prove global convergence from arbitrary initial
points, nor a uniform theorem for all identity-slack problems.

## Verification architecture

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

`python/certify_relaxed_multiplier_interval_theory.py` reconstructs the
parameterized six-dimensional branch map from the original four updates.  It
uses exact Sylvester tests, a rational finite-prefix enclosure, Schur
recursion, and Sturm root counting.  The targeted tests independently replay
both endpoints of the capture interval.

`python/export_orbit_66.py` writes all 66 cyclic phases to
`certificates/orbit_66.json`.  This is a complete exact data rendering, not an
additional proof or independent implementation.

## Quick reproduction

The frozen runtime is Python 3.13.5 with SymPy 1.13.3 and pytest 8.3.4.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python python/verify_certificate_pair.py
python python/export_orbit_66.py
python python/certify_relaxed_multiplier_interval_theory.py
python -m pytest -q python/tests/test_relaxed_multiplier_interval_theory.py
```

Expected terminal summary:

```json
{
  "instance_id": "identity_slack_p66_short_v1",
  "output": ".../certificates/instance_manifest.json",
  "valid": true
}
```

These commands rewrite the following tracked artifacts deterministically:

- `certificates/certificate_raw.json`
- `certificates/certificate_signed.json`
- `certificates/instance_manifest.json`
- `certificates/orbit_66.json`
- `certificates/relaxed_multiplier_certificate.json`
- `certificates/relaxed_multiplier_summary.md`

The MATLAB command similarly rewrites the tracked artifact
`certificates/certificate_matlab.json`.

To confirm that a checkout reproduces the committed certificate exactly, run:

```bash
python python/verify_certificate_pair.py
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
├── certificates/  # Frozen certificates, summaries, and complete orbit data
├── docs/          # Reproducibility and release documentation
├── paper/         # Compiled manuscript PDF only
└── .github/       # Continuous-integration workflows and ownership rules
```

| Path | Purpose |
| --- | --- |
| `python/` | Python exact checkers and comparison entry points |
| `python/strict_cycle_certificate.py` | Independent exact checker on `(y,z,lambda)` |
| `python/signed_cycle_certificate.py` | Independent exact checker on `(y,q)` |
| `python/verify_certificate_pair.py` | Regenerates, compares, and hashes both Python certificates |
| `python/export_orbit_66.py` | Exports every exact cyclic phase as machine-readable data |
| `python/certify_relaxed_multiplier_interval_theory.py` | Certifies the local multiplier-relaxation intervals and Schur boundary |
| `python/tests/test_relaxed_multiplier_interval_theory.py` | Direct-replay and algebraic regression tests for the relaxation certificate |
| `matlab/verify_exact_cycle_matlab.m` | Independent exact MATLAB checker on `(y,z,lambda)` |
| `matlab/tests/VerifyExactCycleMatlabTest.m` | Class-based MATLAB regression test |
| `python/verify_matlab_certificate.py` | Compares MATLAB JSON with frozen Python artifacts |
| `certificates/` | Stable machine-readable certificate bundle |
| `paper/slack_admm_arxiv.pdf` | Compiled manuscript; authoring sources are intentionally not distributed here |
| `docs/REPRODUCIBILITY.md` | Detailed proof-obligation and release contract |
| `.github/workflows/certificate.yml` | Clean GitHub Actions reproduction |
| `.github/workflows/matlab-certificate.yml` | Manual licensed MATLAB reproduction |

## Acceptance rule

The process exits successfully only when every exact predicate passes.  The
two counterexample representations must agree on every shared certificate
field, and the separate relaxation predicates and regression tests must all
pass.  No floating-point tolerance is used for theorem acceptance.  Decimal
values are included only as readable renderings of exact rationals.

## Versioning and release status

The current private review version is `v0.3.0-private`.  Before a public research
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
