# Kimi Code K3 period-23 route

This route started from a frozen workspace containing the slack-ADMM problem
statement, three teacher-provided slides, and generic research and evidence
rules. The workspace did not contain the Codex period-66 candidate or prescribe
a counterexample method. The route produced an exact dyadic
three-dimensional QP with a locally attracting non-KKT sequence of minimal
period 23. Because its constraint matrices are nonsingular, an invertible
change of variables places it in the $[I_3,I_3,I_3]$ identity-slack form.

## Realized computational route

The terminal Kimi route combined:

1. a reduced post-projection state using $t=z+\lambda$;
2. spectral screening and numerical periodic-sequence search;
3. detection of a strict period-23 projection word;
4. interpretation of the stored binary64 candidate as exact dyadic rationals;
5. exact replay of all 23 projection regions; and
6. an exact Jury test for the 23-step return matrix.

The terminal verifier recorded positive leading minors, nonsingular
constraint matrices, the exact KKT-branch fixed point, exact 23-step closure,
exact consistency with the recorded projection word, separation from the KKT
point, and Schur stability of the return matrix. Strict signs and Schur
stability imply local attraction in the canonical reduced $(y,t)$ state, but
that endpoint did not provide an explicit basin radius. The retained post-hoc
hardened verifier made symmetry, the strict margin, 23 distinct phases,
minimality, and fail-closed acceptance explicit without changing the
route-original candidate.

## Post-route release strengthening

The root acceptance layer uses a subsequently simplified denominator-100
rational representative of the period-23 mechanism. Later release work added
a rational Lyapunov matrix, exact support-radius bounds, and the explicit
return-invariant ellipsoid $e^\top P e<1/4000$. These additions strengthen the
portable public certificate, but they are not terminal Kimi-run artifacts and
are not charged to the Kimi route's time or token endpoint.

The root files `certificates/period23_instance.json`,
`python/verify_period23_certificate.py`, and
`certificates/period23_certificate.json` form that portable acceptance layer.
The mathematical conclusion of period-23 nonconvergence does not depend on
the route attribution or telemetry record.

## Attestation and process archive

[`run_attestation.json`](run_attestation.json) records the retained session ID,
actual provider/model identifiers, exact endpoint, usage and timing derivation,
and SHA-256 hashes of the private native session records. Raw wire logs are not
published because they contain chats and user-specific paths.

The curated process archive retains the route's research log, experiments,
saved candidates, and verifier under
[`../../../research-process/kimi-period23/`](../../../research-process/kimi-period23/).
The public `exp19b` script is a post-hoc hardened descendant of the endpoint
script; both hashes are recorded in the attestation rather than presented as
byte-identical artifacts.

## Comparison boundary

The starting workspace omitted the Codex candidate, but the run was audited
post hoc rather than preregistered. The intended experiment-specific Kimi home
and observer checkpoint exporter were not used, so the public record does not
claim operating-system-enforced filesystem isolation. A post-hoc audit found
no recorded tool call that accessed the Codex project or another sibling
workspace.

The route used a different QP from the Codex period-66 route and was not
matched for tools, compute, telemetry, or human intervention. Its recorded
time and token figures are descriptive, not evidence for a causal model
ranking.

See [`accounting.json`](accounting.json) for the reconciled route endpoint and
[`retained_artifacts.json`](retained_artifacts.json) for the artifact lineage.
