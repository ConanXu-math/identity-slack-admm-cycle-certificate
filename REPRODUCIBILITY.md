# Reproducibility and Certificate Contract

## Scope

This repository certifies one frozen theorem instance:

```text
instance_id = identity_slack_p66_short_v1
period      = 66
word        = (00)^2(01)^64
threshold   = 1/1000
```

Search scripts, exploratory floating-point candidates, longer legacy
instances, and multiplier-relaxation experiments are intentionally excluded.

## Exact proof obligations

The generated certificates close the following finite obligations:

1. `Q1` and `Q2` are positive definite, so the two quadratic subproblems are
   uniquely solvable.
2. The displayed rational primal-dual point satisfies feasibility,
   stationarity, slack signs, complementarity, and multiplier uniqueness.
3. The rational affine period system is nonsingular and determines an exact
   candidate initial state.
4. Rerunning the genuine componentwise projection realizes the source-mask
   word `(00)^2(01)^64`.
5. All 132 coordinatewise sign inequalities are strict, with minimum margin
   greater than `1/1000`.
6. Every original `x`, `y`, projection, and multiplier update holds over the
   rationals.
7. Phase 66 returns exactly to phase 0 and no phase 1 through 65 returns
   earlier.
8. Every cycle state differs from the unique KKT state.
9. The lag cross term has one exact positive witness and one exact negative
   witness.

## Implementation separation

The signed checker implements the reduced recurrence on `(y,q)`.  The
six-dimensional checker independently reconstructs affine maps on the
unreduced essential state `(y,z,lambda)` by exact basis evaluation of the raw
ADMM update.  Source-import checks in `verify_certificate_pair.py` ensure that
neither implementation imports the other.

The comparison driver requires exact equality of the shared fields and hashes.
Agreement is a reproducibility guard against implementation, phase-indexing,
and state-translation mistakes.  It is not a substitute for mathematical peer
review.

## Deterministic command

```bash
python verify_certificate_pair.py
```

Acceptance requires both:

```text
process exit status = 0
instance_manifest.json.valid = true
```

The committed outputs must remain unchanged after regeneration:

```bash
git diff --exit-code -- certificate_raw.json certificate_signed.json instance_manifest.json
```

## Frozen runtime

```text
Python 3.13.5
SymPy  1.13.3
```

All theorem predicates use SymPy exact rationals and exact comparisons.  A
different compatible runtime may reproduce the same mathematical object, but
the release manifest and continuous-integration workflow are pinned to the
versions above.

## Artifact meanings

- `certificate_raw.json`: exact obligations evaluated by the six-dimensional
  checker.
- `certificate_signed.json`: exact obligations and cross-term witnesses
  evaluated by the signed-state checker.
- `instance_manifest.json`: common instance record, runtime, agreement checks,
  source hashes, output hashes, and the overall `valid` flag.

The JSON files are theorem evidence only together with the checker sources and
the immutable commit that generated them.

## Release checklist

Before changing repository visibility to public:

- rerun the certificate in a clean checkout;
- confirm the GitHub Actions workflow passes;
- freeze the final public tag;
- create a DOI-bearing archive from that tag;
- add final citation and author metadata;
- choose an explicit public software license;
- update the manuscript's code-availability statement with the DOI and tag.
