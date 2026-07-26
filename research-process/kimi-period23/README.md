# Kimi Code K3 period-23 research path

This directory is a sanitized snapshot of the isolated Kimi workspace. It
preserves the generated research arc rather than only the final JSON
certificate.

## Starting contract

- `AGENTS.md` contains the evidence and safety rules.
- `START_GOAL.txt` contains the initial independent-research instruction.
- `inputs/problem_statement.md` contains the mathematical problem supplied at
  the start.

The three teacher-provided images are intentionally excluded. Their role is
described in the research log, but they are user-provided source material
rather than agent-generated research output.

## Generated artifacts

- `RESEARCH_LOG.md` records plans, commands, seeds, corrections, negative
  findings, and the route to the counterexample.
- `research/` contains nine theory files. The withdrawn Theorem H/Q files are
  retained because the detected `|t|` implementation error materially changed
  the route.
- `experiments/` contains the full set of experiment/test scripts and saved
  JSON/NPZ results from the isolated workspace.
- `references/literature_notes.md` records the literature audit.
- `report/main.md` is the terminal research report.

The shortest discovery chain is
`exp14_targeted_repellent.py` -> `exp17c_selfcontained.py` ->
`exp19b_exact_yt.py`. It moves from a locally repelling KKT construction to
frequency locking and then to an exact route-original replay.

## Acceptance boundary

These files document the historical Kimi route; they are not the root
acceptance layer. The canonical release certificate is the exact
denominator-100 rational instance under `../../certificates/`, verified by
`../../python/verify_period23_certificate.py`. Raw chats, credentials,
installed skills, caches, and local machine paths are excluded.
