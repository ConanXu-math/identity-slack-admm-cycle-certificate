# Computational provenance

This directory records how two AI-assisted research routes reached exact
counterexamples for direct three-block slack ADMM. The comparison is
**descriptive and endpoint-aligned**: each route is measured up to its first
exact, replayable nonconvergence certificate.

The routes address the same research question, but they do **not** solve the
same QP instance. The Codex route produced a rational two-dimensional
period-66 example. The Kimi Code K3 route produced an exact dyadic
three-dimensional period-23 example and certified local attraction by an
exact Jury test. The root acceptance layer uses a subsequently simplified and
independently strengthened denominator-100 rational instance with an explicit
invariant ellipsoid. Both lie in the identity-slack problem class, the latter
after invertible changes of variables.

## What the comparison supports

- Two different realized computational routes separately reached exact
  counterexamples to the same proposed convergence principle.
- Each terminal result reached exact replay, strict projection consistency,
  and non-KKT periodic nonconvergence. The public verifiers subsequently
  harmonize explicit pairwise-distinctness, minimal-period, and fail-closed
  guards without changing either route's candidate.
- The retained files make the mathematical certificates inspectable without
  publishing exploratory conversations or private machine paths.

## What it does not support

This is not a controlled model benchmark. The routes were not matched for
compute, tools, QP instance, search space, tokenization, stopping policy, or
human intervention. Their telemetry therefore cannot support a causal model
ranking or a claim that one system is intrinsically faster, cheaper, or more
capable.

The Codex route included human decisions about the problem specification,
evidence bar, and search priorities. The Kimi run began from a frozen
workspace containing the problem statement, three teacher-provided slides,
and generic evidence rules, but not the Codex candidate or a prescribed
counterexample method. Its record was audited post hoc rather than
preregistered. These conditions reduce direct candidate transfer; they do not
create an equal-start experiment.

## Paper-reported accounting

The following rounded values reproduce the manuscript's descriptive table.
“Total tokens” combines recorded cached input, noncached input, and output;
the two systems' telemetry and tokenizers differ.

| Route | Approx. run time | Recorded total tokens | Recorded output tokens | Recorded topology |
| --- | ---: | ---: | ---: | --- |
| GPT-5.6 Sol through Codex | ~40 h | ~1.704 billion | 7.869 million | 4 top-level and 237 subagent rollouts |
| Kimi Code K3 | ~9 h | ~63.27 million | 482,300 | 1 main session and 3 recorded subagents |

For the Kimi route, the exact endpoint totals are `63,269,210` recorded tokens
and `482,292` output tokens. The `~9 h` display is the union of overlapping
completed-step intervals (`8.9653475 h`); their unmerged sum is
`12.4316925` agent-hours. The endpoint, derivation rule, actual model identity,
and private raw-record hashes are recorded in
[`routes/kimi-period23/run_attestation.json`](routes/kimi-period23/run_attestation.json).

The route-specific accounting files preserve the definitions and additional
caveats:

- [`routes/codex-period66/accounting.json`](routes/codex-period66/accounting.json)
- [`routes/kimi-period23/accounting.json`](routes/kimi-period23/accounting.json)

## Route history and release acceptance

The Kimi process archive preserves the route-original witness and its
discovery scripts as historical evidence. The root acceptance package
designates the exact denominator-100 rational representative as the public
period-23 certificate and verifies its explicit invariant ellipsoid. Resource
accounting ends at the route-original exact dyadic replay and Jury certificate.
The later denominator-100 construction, Lyapunov matrix, support-radius bound,
and release-certificate regeneration are not charged to that endpoint.

The current Codex package also contains cross-checks added around or after the
first certificate, including separately implemented full-state and MATLAB
replays. These are internal reproducibility checks, not external independent
review.

See [`comparison_scope.yaml`](comparison_scope.yaml) for the machine-readable
scope contract and the route directories for curated asset inventories.

## Curated research-process archive

The terminal certificates alone do not explain the discovery process.
[`../research-process/`](../research-process/) therefore retains the important
agent-generated state files, theory notes, experimental scripts, numerical
outputs, withdrawn attempts, and review records for both routes.  The Codex
side is a decision-path selection from a much larger workspace; the Kimi side
preserves a curated research arc from the frozen-start run, excluding raw
session logs, installed third-party skills, and teacher-provided images.

The archive is historical evidence, not a second acceptance layer.  Current
mathematical acceptance remains governed by the exact checkers and frozen
certificates at the repository root.

## Privacy boundary

No raw chats, wire logs, credentials, private configuration, or user-specific
absolute paths are included. The provenance records publish sanitized session
aggregates and hashes, claim boundaries, accounting definitions, and retained
repository artifacts only.

## Route initialization and claim map

Additional machine-readable provenance for the manuscript:

- [`claim_to_artifact.json`](claim_to_artifact.json): claim → verifier → artifact map
- [`prompts/ledger.yaml`](prompts/ledger.yaml): prompt provenance classes
- [`interventions/human_interventions.csv`](interventions/human_interventions.csv): key human gates
- [`routes/*/workspace_manifest.json`](routes/codex-period66/workspace_manifest.json): what each route could see at start

These files document starting conditions and attribution. They are not part of
the mathematical acceptance layer under `certificates/` and `python/`.
