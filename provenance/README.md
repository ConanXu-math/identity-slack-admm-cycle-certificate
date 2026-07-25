# Computational provenance

This directory records how two AI-assisted research routes reached exact
counterexamples for direct three-block slack ADMM. The comparison is
**descriptive and endpoint-aligned**: each route is measured up to its first
exact, replayable nonconvergence certificate.

The routes address the same research question, but they do **not** solve the
same QP instance. The Codex route produced a rational two-dimensional
period-66 example; the Kimi Code K3 route produced a dyadic
three-dimensional period-23 example. Both lie in the identity-slack problem
class, the latter after invertible changes of variables.

## What the comparison supports

- Two different realized computational routes separately reached exact
  counterexamples to the same proposed convergence principle.
- Each terminal result can be discussed at a common evidence endpoint:
  exact replay, strict projection consistency, non-KKT status, and minimal
  period.
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

The route-specific accounting files preserve the definitions and additional
caveats:

- [`routes/codex-period66/accounting.json`](routes/codex-period66/accounting.json)
- [`routes/kimi-period23/accounting.json`](routes/kimi-period23/accounting.json)

## Terminal and later artifacts

For Kimi, the terminal artifact set established the exact dyadic period-23
sequence, strict signs, and exact Jury stability of the 23-step return map.
The explicit rational invariant ellipsoid used later to certify a concrete
open set of reduced initializations is a subsequent companion result. It is
not attributed to the terminal Kimi run and is not retained in this package.

The current Codex package also contains cross-checks added around or after the
first certificate, including separately implemented full-state and MATLAB
replays. These are internal reproducibility checks, not external independent
review.

See [`comparison_scope.yaml`](comparison_scope.yaml) for the machine-readable
scope contract and the route directories for curated asset inventories.

## Privacy boundary

No raw chats, credentials, private configuration, or absolute local paths are
included. The provenance records describe claims, accounting definitions, and
retained repository artifacts only.
