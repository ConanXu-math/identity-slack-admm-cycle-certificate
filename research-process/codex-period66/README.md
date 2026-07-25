# Codex period-66 research path

This is a curated snapshot of the human-interactive GPT-5.6 Sol/Codex route.
The source workspace was substantially larger; this directory keeps the
artifacts needed to reconstruct the decisive changes of direction without
publishing raw conversations or thousands of repetitive intermediate files.

## Reading order

1. `research_state.md`, `work_orders.md`, and
   `skills/admm-proof-workflow/SKILL.md` record the persistent state and
   evidence rules used by the long-running workflow.
2. `notes/problem_formulation.md` and `notes/z_projection_identity.md` fix the
   optimization model and multiplier sign convention.
3. The active-set and switching notes develop the finite-dimensional,
   piecewise-affine representation and document proof routes that were closed,
   narrowed, or rejected.
4. Stage 10 and Stage 25 retain representative exact positive results; Stage
   27 records the periodic-margin search that redirected the route.
5. `notes/local_expansion_history_lyapunov_obstruction.md` and Stage 43 isolate
   the remaining obstruction. `stage43_to_stage44_discovery/search.json`
   records the numerical-to-rational transition.
6. Stages 44, 45, and 46 retain the exact period-66 certificate, independent
   raw-ADMM replay, and decimal-precision audit.
7. `notes/relaxed_multiplier_interval_theory.md` and the two `tau_*` output
   directories record the later multiplier-relaxation investigation.
8. `proof_reviews/` retains internal review gates and risk registers. These
   are implementation and proof checks, not external peer review.

## Reproduction boundary

The scripts are historical source snapshots and may refer to modules or bulk
outputs that were deliberately not copied. The standalone accepted
reproduction path is the root-level `python/` and `certificates/` package.
Commands containing `/opt/anaconda3` record the original runtime and may be
replaced by an equivalent active Python environment.

The archive retains failed and superseded routes when they explain a research
decision. Their original status labels remain authoritative; inclusion here
does not promote a numerical screen or proof attempt to a theorem.
