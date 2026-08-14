# Reproducibility and Certificate Contract

## Scope

This repository certifies two frozen theorem instances:

```text
instance_id = identity_slack_p66_short_v1
dimension   = 2
period      = 66
word        = (00)^2(01)^64
threshold   = 1/1000

instance_id = identity_slack_p23_rational_v1
dimension   = 3
period      = 23
word        = 101^5 011^7 001^2 000 001^8
threshold   = 1/250
basin level = 1/4000
```

The root acceptance package also certifies three multiplier-relaxation
statements for the period-66 QP: a common local Lyapunov interval, a
fixed-initialization finite-prefix capture interval, and a local Schur
boundary.  Curated search and discovery artifacts are kept separately from
these acceptance-layer files.

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

The complete 66-phase orbit is exported to `certificates/orbit_66.json` from
the accepted raw certificate.  It is a data rendering rather than another
proof implementation.

## Period-23 exact proof obligations

The period-23 certificate closes the following finite obligations:

1. Every primitive QP input is a canonical reduced fraction; all 45 entries
   have numerator absolute value and denominator at most 100.
2. `F` and `G` are symmetric positive definite and `A` and `B` are
   nonsingular.
3. The affine fixed point in the KKT projection cone is unique, lies in that
   cone, and satisfies primal feasibility, both stationarity equations,
   slack and multiplier signs, and complementarity exactly.
4. The prescribed 23-region word is realized exactly by the reduced `(y,t)`
   map.
5. The frozen certificate exposes the exact rational phase-zero
   `(x,y,z,lambda)` initialization as well as a 12-significant-digit display;
   its exact reduced `(y,t)` coordinates reproduce the recorded phase-zero
   hash.  It also exposes every exact entry of the 23-step return matrix and
   offset; their hashes and fixed-point equation are checked independently.
6. All 69 projection inputs are strict, with minimum margin greater than
   `1/250`.
7. The 23 phase states are pairwise distinct and phase 23 returns exactly to
   phase 0, establishing minimal period 23.
8. The periodic sequence differs from the KKT point.
9. The rational matrix `P` and the Lyapunov gap
   `P - M_per^T P M_per` are positive definite by exact Sylvester tests.
10. All 69 support ratios are positive and exceed
   `29/100000 > 1/4000`.

Consequently, `e^T P e < 1/4000` is an explicit return-invariant open set in
the canonical reduced `(y,t)` state.  This is an initialization neighborhood
for one fixed QP, not a parameter interval, an arbitrary full
ambient-state ball, or a global attraction theorem.

## Exact multiplier-relaxation obligations

For the multiplier update

```text
lambda_next = lambda - tau * (x_next + y_next + z_next - rhs),
```

the relaxation certificate closes the following finite obligations:

1. The parameterized six-dimensional branch maps agree exactly with direct
   basis evaluation of the four original ADMM updates.
2. At `tau = 1/2`, the strict `01` KKT branch admits an exact rational
   discrete Lyapunov matrix `H`.
3. The endpoint residuals at `tau = 49/100` and `tau = 51/100` are positive
   definite by exact Sylvester minors; the quadratic chord identity extends
   the certificate to the entire closed interval.
4. For every `tau in [1/2 - 10^-10, 1/2 + 10^-10]`, componentwise rational
   enclosures preserve the strict source masks for 232 steps from the former
   periodic initialization and place the final state strictly inside the
   common invariant ellipsoid.
5. Exact real Schur recursion and Sturm root counting establish one boundary
   inside `(0,1)`, with
   `0.9366061114 < tau_c < 0.9366061115`.

These obligations do not establish global convergence from arbitrary initial
states or a uniform convergence theorem for the model class.

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
python python/verify_research_process_archive.py
python python/export_orbit_66.py
python python/certify_relaxed_multiplier_interval_theory.py
python python/verify_universal_step_obstruction.py --check
python -m pytest -q python/tests/test_relaxed_multiplier_interval_theory.py
python -m unittest discover -s tests -p "test_*.py"
```

Acceptance requires:

```text
process exit status = 0
certificates/instance_manifest.json.valid = true
certificates/period23_certificate.json.valid = true
certificates/relaxed_multiplier_certificate.json.valid = true
research-process/manifest.json.valid = true
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
pytest 8.3.4
MATLAB  R2025a (25.1.0.2943329)
Symbolic Math Toolbox 25.1
```

The period-66 checkers use SymPy exact rationals.  The period-23 checker parses
canonical JSON fractions directly with `fractions.Fraction`; NumPy is used
only for a non-proof spectral-radius display.  A different compatible runtime
may reproduce the same mathematical objects, but the release manifests and
continuous-integration workflow are pinned to the versions above.  The
certified ADMM recurrence uses penalty parameter `1`.

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
- `certificates/period23_instance.json`: canonical exact rational input for
  the period-23 instance.
- `certificates/period23_certificate.json`: stable exact replay, strict-sign,
  minimal-period, non-KKT, Lyapunov, and support-radius verdicts.
- `certificates/orbit_66.json`: complete exact and decimal rendering of all
  period-66 cyclic phases.
- `certificates/relaxed_multiplier_certificate.json`: exact common-Lyapunov,
  finite-prefix, and local-Schur predicates for multiplier relaxation.
- `certificates/relaxed_multiplier_summary.md`: human-readable rendering of
  the exact relaxation certificate.

The JSON files are theorem evidence only together with the checker sources and
the immutable commit that generated them.

## Release checklist

Before changing repository visibility to public:

- rerun the certificate in a clean checkout;
- confirm the GitHub Actions workflow passes;
- generate and freeze `certificates/certificate_matlab.json` under a valid MATLAB license;
- confirm that all 66 exported phases and the relaxation artifacts regenerate
  byte for byte;
- confirm that the period-23 canonical rational input regenerates the frozen
  certificate byte for byte;
- confirm that the research-process manifest, required-path gate, and privacy
  scan pass;
- run an independent secret and privacy scan on the release tree;
- freeze the final public tag;
- create a DOI-bearing archive from that tag;
- add final citation and author metadata;
- choose an explicit public software license;
- update the manuscript's code-availability statement with the DOI and tag.
