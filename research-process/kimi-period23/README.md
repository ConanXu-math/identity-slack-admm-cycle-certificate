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
frequency locking and then to exact dyadic replay with the Jury test.

## Attribution boundary

These files document the terminal Kimi route. The later explicit rational
invariant ellipsoid used in the manuscript was constructed after that run and
is not included or attributed to Kimi. Raw chats, credentials, installed
skills, caches, and local machine paths are excluded.
