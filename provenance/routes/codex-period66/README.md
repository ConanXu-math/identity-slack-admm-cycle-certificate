# Codex period-66 route

This route used GPT-5.6 Sol through Codex to construct an exact rational
two-dimensional identity-slack QP for which unmodified direct three-block ADMM
has a bounded, non-KKT sequence of minimal period 66.

## Computational route

The realized route combined:

1. the slack projection identity and a signed piecewise-affine reduction;
2. structured active-set and periodic-word searches;
3. solution of an affine period equation and rationalization of the candidate;
4. exact reduced-state and full-state replays; and
5. later precision and MATLAB cross-checks.

The certified projection word is `(00)^2(01)^64`. The current public
certificate verifies all 132 projection signs strictly, with uniform margin
greater than `1/1000`, as well as exact closure and minimal period.

## Endpoint and attribution

For the cross-route comparison, the stopping endpoint is the first exact,
replayable nonconvergence certificate. The additional full-state, paired, and
MATLAB checks retained in the repository strengthen reproducibility of the
same mathematical result; they are not separate counterexamples and are not
external independent review.

Human intervention was part of this workflow, including problem
specification, evidence requirements, and search-priority decisions. The
route should therefore be attributed to an AI-assisted human research
workflow, not to an autonomous or controlled model-only experiment.

The period-66 QP is not the QP used by the Kimi period-23 route. The routes
share a research question and a problem class, not an instance.

See [`accounting.json`](accounting.json) for paper-reported resource figures
and [`retained_artifacts.json`](retained_artifacts.json) for the curated asset
inventory.
