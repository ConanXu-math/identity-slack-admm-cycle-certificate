---
name: admm-proof-workflow
description: Use when working on ADMM convergence proofs, multi-block ADMM counterexample search, slack-variable ADMM with [A,B,I] structure, Lyapunov/descent-function attempts, spectral-radius screening, or extracting reusable proof patterns from ADMM papers.
---

# ADMM Proof Workflow

Use this repo-local skill to continue the slack-variable three-block ADMM research workflow.

## Process

1. Read `notes/problem_formulation.md` and confirm the multiplier sign convention.
2. Read `notes/z_projection_identity.md` before using normal cone or complementarity claims.
3. Update `knowledge_base/literature_map.md` before adding a theorem, proof-pattern, or counterexample card.
4. For a convergence attempt, write the candidate energy in `knowledge_base/descent_functions/` and mark each controlled term and unresolved cross term.
5. For a counterexample attempt, start with convex quadratic data, run `experiments/random_qp_search.py`, then inspect active-set spectral radius with `experiments/spectral_radius_search.py`.
6. Treat random numerical behavior as screening evidence only. Promote it to a counterexample only after deriving the local iteration matrix and checking assumptions.
7. Do not claim slack-variable direct three-block ADMM converges unless the proof controls the \(B(y^{k+1}-y^k)\) and \(z^{k+1}-z^k\) cross term.

## Phase-Dependent Lyapunov Route

For quadratic slack QPs with finitely many projection masks, use the reviewed source-target route:

1. Build the canonical reduced state only after the first projection/multiplier update.
2. Construct all source-target maps \(A_{bc}\) and the dissipation map
   \(C_{bc}r=(\Delta\lambda,B\Delta y,\Delta z)\).
3. Treat the search for phase matrices \(H_b\) as an SDP and label its output
   `numerical_screen`; do not call solver feasibility a proof.
4. Rationalize a simple candidate independently of the floating result, then derive all maps again
   from the original rational QP.
5. Certify
   \[
   H_b-A_{bc}^\top H_cA_{bc}-\varepsilon C_{bc}^\top C_{bc}\succeq0
   \]
   by exact principal minors. For parameter intervals or boxes, clear only denominators proved
   strictly positive and certify numerator nonnegativity with exact tensor Bernstein coefficients.
6. Require a separate reviewer to check recurrence indexing, multiplier sign, canonical ties,
   coercivity, KKT bridging, and theorem scope.
7. For strict residual margin \(R_{bc}\succeq\eta I\), prefer the direct conclusion
   \(\sum_k\|r_k\|^2<\infty\) over an unnecessarily weak cluster-point argument.

Current accepted examples are indexed in `notes/fixed_qp_phase_lyapunov_theorem.md`,
`notes/joint_qp_box_phase_family_theorem.md`, and
`notes/reduced_mn_robust_neighborhood_theorem.md`.

For structure and red-team work, keep these scopes separate:

- `notes/phase_metric_six_parameter_ansatz.md` gives an accepted low-dimensional explanation for
  one fixed QP; it is not an optimality theorem.
- `notes/diagonal_phase_farkas_obstruction.md` gives an accepted exact obstruction only for
  diagonal phase matrices; off-diagonal metrics and actual orbit divergence remain open.
- A block-norm comparison matrix may give a global sufficient family. Prove its weighted norm
  contraction and the ADMM state/KKT bridge symbolically before promoting solver output.
- For a nonnegative two-block comparison, use the reviewed optimized-scaling gate in
  `notes/optimized_small_gain_scaling_theorem.md`: check
  \(a<1,d<1,bc<(1-a)(1-d)\), and use \(t=b/c\) only when \(b,c>0\).
- In the scalar quadratic case, prefer the accepted real-region classification in
  `notes/scalar_all_parameter_convergence_theorem.md` over the conservative small-gain gate.
  Its coordinatewise extension is valid only when the Hessians are diagonal in the fixed
  orthant projection coordinates.

## Output Expectations

- Prefer Markdown cards over chat-only reasoning.
- Preserve source links for literature claims.
- State whether evidence is a theorem, proof attempt, numerical screen, or conjecture.
- Keep teacher-facing summaries short and honest about proof status.
