# Kimi Code K3 period-23 route

This route started from a frozen workspace containing the slack-ADMM problem
statement, three teacher-provided slides, and generic research and evidence
rules. It did not contain the Codex period-66 candidate or prescribe a
counterexample method. The route identified a three-dimensional period-23
mechanism. The root acceptance layer designates an exact
denominator-100 rational QP as the canonical certificate for that route.
Because its constraint matrices are nonsingular, an invertible change of
variables places it in the `[I3, I3, I3]` identity-slack form.

## Computational route

The realized route combined:

1. a reduced post-projection state using `t = z + lambda`;
2. spectral screening and numerical periodic-sequence search;
3. detection of the strict period-23 projection word;
4. exact rational replay of the 23 projection regions; and
5. an exact Lyapunov and support-radius certificate for the return map.

The release verifier establishes validity of the QP, a unique strictly
complementary KKT point, exact closure, 23 distinct phases, strict consistency
of all 69 projection signs with margin greater than `1/250`, separation from
the KKT point, and
`P - M_per^T P M_per > 0`.  Its support certificate gives
`rbar^2 > 29/100000 > 1/4000`, so `e^T P e < 1/4000` is an explicit
return-invariant neighborhood in the canonical reduced `(y,t)` state.

## Release certificate and route archive

The root files `certificates/period23_instance.json`,
`python/verify_period23_certificate.py`, and
`certificates/period23_certificate.json` form the portable acceptance layer.
The sanitized process archive retains the route-original logs, experiments,
saved candidates, and verifier for historical inspection. The recorded time
and token endpoint describes that research route, not the runtime of the
release verifier.

## Comparison boundary

The frozen starting workspace omitted the Codex candidate, but the run was
audited post hoc rather than preregistered. The route used a different QP from
the Codex period-66 route and was not matched for tools, compute, telemetry,
or human intervention. Its recorded time and token figures are descriptive,
not evidence for a causal model ranking.

See [`accounting.json`](accounting.json) for paper-reported resource figures
and [`retained_artifacts.json`](retained_artifacts.json) for the curated asset
inventory. The sanitized isolated-workspace archive is available under
[`../../../research-process/kimi-period23/`](../../../research-process/kimi-period23/).
