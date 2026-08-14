# Curated agent research process

This directory preserves the important process artifacts behind the two exact
counterexamples. It complements the compact certificate package at the
repository root: JSON certificates answer whether a claim replays exactly,
while this archive records how candidate mechanisms, experiments, failures,
proof obligations, and independent checks evolved.

## Routes

- [`codex-period66/`](codex-period66/) is a curated decision path from the
  larger Codex workspace. It retains state snapshots, central reductions,
  representative positive and negative theoretical results, the decisive
  Stage 43--46 search/certification chain, multiplier-relaxation follow-up,
  tests, and review artifacts.
- [`kimi-period23/`](kimi-period23/) preserves a curated research arc from the
  frozen-start Kimi Code K3 workspace: starting contract, research log, theory
  notes (including explicitly withdrawn claims), all experiment scripts and
  saved results, literature notes, and final report. Raw native session logs
  remain private.

## Evidence labels

Files must be read with their recorded status:

- `initial_input` or `state_snapshot`: scope and resumable research state;
- `proof_attempt` or `withdrawn`: useful history, not an accepted theorem;
- `numerical_screen`: exploration that cannot establish the final claim;
- `theorem` or `exact_certificate`: a stated mathematical result with its
  declared scope;
- `review`: an internal verification or adversarial check, not external peer
  review.

The current acceptance boundary remains the exact root-level verifiers and
frozen certificates. Historical notes may mention superseded paths; the route
README and the newest state file take precedence.

For a compact map from research stages to files and evidence status, see
[`INDEX.md`](INDEX.md).

## Selection and privacy boundary

The archive intentionally excludes raw chats, session JSONL, credentials,
private configuration, caches, virtual environments, installed third-party
skills, teacher-provided images, and repetitive bulk outputs. User-specific
absolute paths were removed. The deterministic
[`manifest.json`](manifest.json) records every retained file, byte size, and
SHA-256 digest and is checked in CI.
