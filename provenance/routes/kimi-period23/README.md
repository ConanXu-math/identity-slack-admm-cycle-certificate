# Kimi Code K3 period-23 route

This route started from a frozen workspace containing the slack-ADMM problem
statement, three teacher-provided slides, and generic research and evidence
rules. It did not contain the Codex period-66 candidate or prescribe a
counterexample method. The route produced an exact dyadic three-dimensional
QP with a non-KKT sequence of minimal period 23. Because its constraint
matrices are nonsingular, an invertible change of variables places it in the
`[I3, I3, I3]` identity-slack form.

## Computational route

The realized route combined:

1. a reduced post-projection state using `t = z + lambda`;
2. spectral screening and numerical periodic-sequence search;
3. interpretation of stored binary64 data as exact dyadic rationals;
4. exact replay of the 23 projection regions; and
5. an exact Jury test for the 23-step return matrix.

The terminal exact verifier establishes validity of the QP, a unique KKT
point, exact closure, 23 distinct phases, strict consistency of all 69
projection signs with margin greater than `7/1000`, separation from the KKT
point, and Schur stability of the return matrix. The latter two strict
properties imply local attraction of the orbit in the canonical reduced
`(y,t)` state; the sign margin is not an explicit basin radius.

## Terminal artifact boundary

The terminal Kimi artifact set consists of the source binary64 data, the exact
dyadic replay, and the Jury stability certificate. The repository contains a
curated, path-independent form of those assets.

The explicit rational invariant ellipsoid
`e^T P e < 1/2000`, used subsequently to certify a concrete open set of
nonconvergent reduced initializations, was constructed after the terminal
Kimi run. It is a companion certificate, is not attributed to the terminal
run, and is not retained in this package.

## Comparison boundary

The frozen starting workspace omitted the Codex candidate, but the run was
audited post hoc rather than preregistered. The route used a different QP from
the Codex period-66 route and was not matched for tools, compute, telemetry,
or human intervention. Its recorded time and token figures are descriptive,
not evidence for a causal model ranking.

See [`accounting.json`](accounting.json) for paper-reported resource figures
and [`retained_artifacts.json`](retained_artifacts.json) for the curated asset
inventory.
