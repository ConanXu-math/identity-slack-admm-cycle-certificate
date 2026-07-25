# Reproducibility and Certificate Contract

## Scope

This repository certifies two frozen theorem instances:

```text
instance_id = identity_slack_p66_short_v1
dimension   = 2
period      = 66
word        = (00)^2(01)^64
threshold   = 1/1000

instance_id = identity_slack_p23_dyadic_v1
dimension   = 3
period      = 23
word        = 5^5 6^7 4^2 0 4^8
threshold   = 7/1000
```

Search scripts, exploratory floating-point candidates, longer legacy
instances, and multiplier-relaxation experiments are intentionally excluded.

## Period-66 exact proof obligations

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

## Period-23 exact proof obligations

The period-23 certificate closes the following finite obligations:

1. Every stored binary64 input is interpreted as its exact dyadic-rational
   value and recorded canonically in the instance manifest.
2. `F` and `G` are symmetric positive definite and `A` and `B` are
   nonsingular.
3. The affine fixed point in the KKT projection cone is unique, lies in that
   cone, and satisfies primal feasibility, both stationarity equations,
   slack and multiplier signs, and complementarity exactly.
4. The prescribed 23-region word is realized exactly by the reduced `(y,t)`
   map.
5. All 69 projection inputs are strict, with minimum margin greater than
   `7/1000`.
6. The 23 phase states are pairwise distinct and phase 23 returns exactly to
   phase 0, establishing minimal period 23.
7. The periodic sequence differs from the KKT point.
8. The exact characteristic polynomial of the 23-step return matrix passes
   the Jury stability criterion.

The explicit rational invariant-neighborhood certificate in the manuscript
is a later companion artifact and is not part of the terminal Kimi certificate
defined above.

The strict-cell margin is not an explicit basin radius.  Exact Jury stability
and strict cell membership prove existence of a locally attracting periodic
orbit in the canonical reduced `(y,t)` state; they do not certify a parameter
interval, an arbitrary full ambient-state ball, or global attraction.

## Period-66 implementation separation

The signed checker implements the reduced recurrence on `(y,q)`.  The
six-dimensional checker independently reconstructs affine maps on the
unreduced essential state `(y,z,lambda)` by exact basis evaluation of the raw
ADMM update.  Source-import checks in `python/verify_certificate_pair.py` ensure that
neither implementation imports the other.

The comparison driver requires exact equality of the shared fields and hashes.
Agreement is a reproducibility guard against implementation, phase-indexing,
and state-translation mistakes.  It is not a substitute for mathematical peer
review.

The MATLAB checker is a third source implementation.  It independently
constructs the rational QP, solves the affine period equation on
`(y,z,lambda)`, and reruns the original projection updates.  It does not
invoke either Python checker.  `python/verify_matlab_certificate.py` is deliberately
only a result comparator: it reads JSON and checks common exact rational
fields, the KKT point, and the initial raw state.

## Deterministic commands

Run both public Python certificate paths with:

```bash
python python/verify_all.py
python -m unittest discover -s tests -p "test_*.py"
```

Acceptance requires:

```text
process exit status = 0
certificates/instance_manifest.json.valid = true
certificates/period23_certificate.json.valid = true
certificates/period23_instance_manifest.json.valid = true
```

The committed outputs must remain unchanged after regeneration:

```bash
git diff --exit-code -- certificates/
```

## MATLAB command and acceptance

The MATLAB implementation requires MATLAB R2025a and Symbolic Math Toolbox:

```matlab
addpath("matlab")
result = verify_exact_cycle_matlab();
assert(result.valid)
```

This writes `certificates/certificate_matlab.json`.  Cross-language acceptance then
requires:

```bash
python python/verify_matlab_certificate.py
```

The MATLAB test suite is class-based and exercises the public verifier:

```matlab
results = runtests("matlab/tests/VerifyExactCycleMatlabTest.m");
assert(all([results.Passed]))
```

For the current private repository, the manual GitHub Actions workflow needs
the repository secret `MLM_LICENSE_TOKEN`.  This is a MathWorks licensing
requirement for private-project jobs, not theorem data and not part of any
certificate JSON.

## Frozen runtime

```text
Python 3.13.5
SymPy  1.13.3
NumPy  2.1.3
MATLAB  R2025a (25.1.0.2943329)
Symbolic Math Toolbox 25.1
```

The period-66 checkers use SymPy exact rationals.  The period-23 checker uses
`fractions.Fraction` after reading binary64 arrays with NumPy, so every
arithmetic predicate is evaluated on exact dyadic rationals.  A different
compatible runtime may reproduce the same mathematical objects, but the
release manifests and continuous-integration workflow are pinned to the
versions above.

The period-23 source field `rho` is an exploratory binary64 estimate of the
return-map spectral radius, not the ADMM penalty parameter.  The certified
ADMM recurrence uses penalty parameter `1`.

## Artifact meanings

- `certificates/certificate_raw.json`: exact obligations evaluated by the six-dimensional
  checker.
- `certificates/certificate_signed.json`: exact obligations and cross-term witnesses
  evaluated by the signed-state checker.
- `certificates/instance_manifest.json`: common instance record, runtime, agreement checks,
  source hashes, output hashes, and the overall `valid` flag.
- `certificates/certificate_matlab.json`: generated result of the independent MATLAB
  checker; it is accepted only when both the MATLAB unit test and
  `python/verify_matlab_certificate.py` pass.
- `certificates/period23_source_binary64.npz`: frozen source container for the
  period-23 instance.
- `certificates/period23_certificate.json`: stable exact replay, strict-sign,
  minimal-period, non-KKT, and Jury verdicts.
- `certificates/period23_instance_manifest.json`: canonical shapes, dtypes,
  binary64 bit patterns, exact dyadic values, and source/verifier hashes.

The JSON files are theorem evidence only together with the checker sources and
the immutable commit that generated them.

## Release checklist

Before changing repository visibility to public:

- rerun the certificate in a clean checkout;
- confirm the GitHub Actions workflow passes;
- generate and freeze `certificates/certificate_matlab.json` under a valid MATLAB license;
- confirm that the period-23 NPZ and canonical exact manifest agree;
- run an independent secret and privacy scan on the release tree;
- freeze the final public tag;
- create a DOI-bearing archive from that tag;
- add final citation and author metadata;
- choose an explicit public software license;
- update the manuscript's code-availability statement with the DOI and tag.
