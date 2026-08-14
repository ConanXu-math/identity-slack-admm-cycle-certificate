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

The public recomputation bundle contains:

- [`session_audit_events.jsonl`](session_audit_events.jsonl), a sanitized
  event ledger containing request metadata, usage, completed step intervals,
  the 12 recorded human inputs, endpoint metadata, and raw-file hashes;
- [`terminal_artifacts/`](terminal_artifacts/), the byte-identical terminal
  script and stdout;
- [`start_manifest.json`](start_manifest.json) and
  [`start_tree.txt`](start_tree.txt), the actual frozen-start inventory and
  depth-limited tree; [`post_run_tree.txt`](post_run_tree.txt) is explicitly
  labeled as the later curated workspace tree;
- [`run_attestation.schema.json`](run_attestation.schema.json) and
  [`provenance_manifest.json`](provenance_manifest.json), the public schema and
  path/byte/hash inventory.

From the repository root, run:

```bash
python python/verify_kimi_provenance.py --check
```

An auditor who also holds the private native records can additionally run:

```bash
python python/verify_kimi_provenance.py --check \
  --raw-session-root /path/to/private/session \
  --start-archive /path/to/kimi_k3_strict_blind_workspace_v1.zip
```

The first command is the public CI gate. The second deterministically rebuilds
the sanitized ledger and start manifest before comparing them with the public
package. Neither command treats the telemetry as mathematical evidence for the
period-23 theorem.

The curated process archive retains the route's research log, experiments,
saved candidates, and verifier under
[`../../../research-process/kimi-period23/`](../../../research-process/kimi-period23/).
The `exp19b` script in the research-process archive is a post-hoc hardened
descendant of the endpoint script. The exact endpoint bytes are now retained
separately under `terminal_artifacts/`; the two files are not presented as
byte-identical.

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
