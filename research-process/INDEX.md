# Research-stage index

This index points to the most informative files in the 168-file archive.
Directories contain additional scripts, tests, machine outputs, and reviews.

## Codex period-66 route

| Stage | Evidence status | Main files |
| --- | --- | --- |
| Persistent task state | state snapshot | [`research_state.md`](codex-period66/research_state.md), [`work_orders.md`](codex-period66/work_orders.md), [`pause_summary.md`](codex-period66/notes/pause_summary.md) |
| Optimization model and sign convention | algebraic foundation | [`problem_formulation.md`](codex-period66/notes/problem_formulation.md), [`z_projection_identity.md`](codex-period66/notes/z_projection_identity.md) |
| Active-set reduction | derivation | [`active_set_effective_recurrence.md`](codex-period66/notes/active_set_effective_recurrence.md), [`general_active_mask_reduction.md`](codex-period66/notes/general_active_mask_reduction.md) |
| Short-cycle exclusions | scoped theorem chain | [`length2_pair_class_consolidation.md`](codex-period66/notes/length2_pair_class_consolidation.md), [`length3_switching_gate.md`](codex-period66/notes/length3_switching_gate.md) |
| Positive convergence families | exact scoped theorems | [`fixed_qp_phase_lyapunov_theorem.md`](codex-period66/notes/fixed_qp_phase_lyapunov_theorem.md), [`signed_pwa_two_layer_closure_summary.md`](codex-period66/notes/signed_pwa_two_layer_closure_summary.md), [Stage 10 outputs](codex-period66/outputs/breakthrough_attempts/stage10_phase_edge_certificate/), [Stage 25 outputs](codex-period66/outputs/breakthrough_attempts/stage25_fixed_qp_signed_pwa/) |
| Periodic search pressure | numerical screen | [Stage 27 period-margin outputs](codex-period66/outputs/breakthrough_attempts/stage27_periodic_margin/) |
| Remaining Lyapunov obstruction | exact obstruction with bounded scope | [`local_expansion_history_lyapunov_obstruction.md`](codex-period66/notes/local_expansion_history_lyapunov_obstruction.md), [Stage 43 certificate](codex-period66/outputs/breakthrough_attempts/stage43_local_expansion_history_obstruction/certificate.json) |
| Candidate discovery | numerical-to-rational transition | [Stage 43→44 search](codex-period66/outputs/breakthrough_attempts/stage43_to_stage44_discovery/search.json), [`search_stage43_to_strict_66_cycle.py`](codex-period66/experiments/breakthrough/search_stage43_to_strict_66_cycle.py) |
| Exact counterexample | exact certificate | [`strict_rational_66_cycle_counterexample.md`](codex-period66/notes/strict_rational_66_cycle_counterexample.md), [Stage 44 certificate](codex-period66/outputs/breakthrough_attempts/stage44_strict_rational_66_cycle/certificate.json) |
| Independent implementation checks | exact internal cross-check | [Stage 45 raw replay](codex-period66/outputs/breakthrough_attempts/stage45_independent_raw_admm_audit/certificate.json), [Stage 46 precision audit](codex-period66/outputs/breakthrough_attempts/stage46_decimal_precision_audit/certificate.json), [`adversarial_risk_register.md`](codex-period66/proof_reviews/strict_rational_66_cycle/adversarial_risk_register.md) |
| Multiplier relaxation | theorem, experiments, and review | [`relaxed_multiplier_interval_theory.md`](codex-period66/notes/relaxed_multiplier_interval_theory.md), [`tau_multiplier_relaxation_2026-07-15/`](codex-period66/outputs/tau_multiplier_relaxation_2026-07-15/), [`tau_relaxation_theory_2026-07-16/`](codex-period66/outputs/tau_relaxation_theory_2026-07-16/), [review package](codex-period66/proof_reviews/relaxed_multiplier_interval_theory/) |
| Process accounting | descriptive audit | [`ai_assisted_research_process_audit_2026-07-19.md`](codex-period66/report/ai_assisted_research_process_audit_2026-07-19.md), [`search_workflow_theory_numerics_counterexample.md`](codex-period66/report/search_workflow_theory_numerics_counterexample.md) |

## Kimi Code K3 period-23 route

| Stage | Evidence status | Main files |
| --- | --- | --- |
| Frozen start | initial input and rules | [`START_GOAL.txt`](kimi-period23/START_GOAL.txt), [`AGENTS.md`](kimi-period23/AGENTS.md), [`problem_statement.md`](kimi-period23/inputs/problem_statement.md) |
| Full route chronology | research log | [`RESEARCH_LOG.md`](kimi-period23/RESEARCH_LOG.md) |
| Reduction and early theory | derivation | [`01_theory_notes.md`](kimi-period23/research/01_theory_notes.md) |
| Detected wrong turn | explicitly withdrawn | [`02_theorem_H.md`](kimi-period23/research/02_theorem_H.md), [`03_theorem_Q.md`](kimi-period23/research/03_theorem_Q.md) |
| Remaining proof obligations | scoped open questions | [`04_proof_obligations.md`](kimi-period23/research/04_proof_obligations.md) |
| Positive partial theory | strict scoped results | [`05_theorem_m1.md`](kimi-period23/research/05_theorem_m1.md), [`06_theorem_S.md`](kimi-period23/research/06_theorem_S.md), [`08_conditional_theorems.md`](kimi-period23/research/08_conditional_theorems.md) |
| Failed proof routes | proof attempts and numerical falsification | [`07_proof_attempts.md`](kimi-period23/research/07_proof_attempts.md), [`exp11_cqlf.py`](kimi-period23/experiments/exp11_cqlf.py) |
| Targeted instability mechanism | numerical screen | [`exp14_targeted_repellent.py`](kimi-period23/experiments/exp14_targeted_repellent.py), [`exp16_trapping.py`](kimi-period23/experiments/exp16_trapping.py) |
| Period locking | candidate discovery and floating replay | [`exp17c_selfcontained.py`](kimi-period23/experiments/exp17c_selfcontained.py), [`exp17c_summary.json`](kimi-period23/experiments/results/exp17c_summary.json), [saved cycle NPZ files](kimi-period23/experiments/results/) |
| Exact period-23 result | route-original exact certificate | [`09_counterexample.md`](kimi-period23/research/09_counterexample.md), [`exp19b_exact_yt.py`](kimi-period23/experiments/exp19b_exact_yt.py), [`exp19_certificate.json`](kimi-period23/experiments/results/exp19_certificate.json) |
| Literature and final synthesis | research report | [`literature_notes.md`](kimi-period23/references/literature_notes.md), [`main.md`](kimi-period23/report/main.md) |

The root `certificates/` and `python/` directories remain the portable,
standalone acceptance package. The files indexed here preserve discovery and
research provenance.
