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
KKT point.

The repository is a verification package, not a numerical-search archive.  It
contains only the frozen instance, two separately implemented exact checkers,
their comparison driver, and the generated machine-readable certificates.

## Certified statement

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

## Verification architecture

The package uses two state representations:

1. `signed_cycle_certificate.py` derives and verifies the four-dimensional
   signed recurrence `s = (y, q)`.
2. `strict_cycle_certificate.py` independently reconstructs affine maps on the
   six-dimensional unreduced essential state `(y, z, lambda)` by exact basis
   evaluation of the original ADMM updates.

Neither checker imports the other.  `verify_certificate_pair.py` regenerates
both JSON certificates and requires exact agreement of the instance, initial
state, orbit, word, KKT point, minimum margin, and canonical hashes.  This is
an internal implementation cross-check, not a second mathematical proof or
external peer review.

## Quick reproduction

The frozen runtime is Python 3.13.5 with SymPy 1.13.3.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python verify_certificate_pair.py
```

Expected terminal summary:

```json
{
  "instance_id": "identity_slack_p66_short_v1",
  "output": ".../instance_manifest.json",
  "valid": true
}
```

The command rewrites the following tracked artifacts deterministically:

- `certificate_raw.json`
- `certificate_signed.json`
- `instance_manifest.json`

To confirm that a checkout reproduces the committed certificate exactly, run:

```bash
python verify_certificate_pair.py
git diff --exit-code -- certificate_raw.json certificate_signed.json instance_manifest.json
```

## Repository layout

| Path | Purpose |
| --- | --- |
| `strict_cycle_certificate.py` | Independent exact checker on `(y,z,lambda)` |
| `signed_cycle_certificate.py` | Independent exact checker on `(y,q)` |
| `verify_certificate_pair.py` | Regenerates, compares, and hashes both certificates |
| `certificate_raw.json` | Stable machine-readable output of the six-dimensional checker |
| `certificate_signed.json` | Stable machine-readable output of the signed-state checker |
| `instance_manifest.json` | Shared claims, comparisons, runtime, and artifact hashes |
| `REPRODUCIBILITY.md` | Detailed proof-obligation and release contract |
| `.github/workflows/certificate.yml` | Clean GitHub Actions reproduction |

## Acceptance rule

The process exits successfully only when every exact predicate passes and the
two representations agree on every shared certificate field.  No floating-
point tolerance is used for theorem acceptance.  Decimal values are included
only as readable renderings of exact rationals.

## Versioning and release status

The initial private review tag is `v0.1.0-private`.  Before a public research
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
