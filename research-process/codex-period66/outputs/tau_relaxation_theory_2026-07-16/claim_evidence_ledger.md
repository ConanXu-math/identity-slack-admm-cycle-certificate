# Claim--Evidence Ledger for the Five-Page Note

| Paper claim | Scope | Evidence | Status |
| --- | --- | --- | --- |
| strict KKT branch plus Schur stability gives a projection-safe local ellipsoid | general finite-dimensional branch theorem | `notes/relaxed_multiplier_interval_theory.md`, Theorem 1 proof | supported |
| one rational `H` works for every `tau` in `[49/100,51/100]` | fixed rational QP; local states near the KKT point | exact endpoint Sylvester minors and chord identity in `certificate.json` | supported |
| the original period-66 initial point converges for every `tau` in `[4999999999/10^10,5000000001/10^10]` | fixed rational QP and fixed initial point | 232-step exact sensitivity enclosure and positive ellipsoid slack | supported |
| `0.9366061114 < tau_c < 0.9366061115` is the exact local branch boundary bracket | fixed `01` branch, `0<tau<1` | exact characteristic factorization, Schur recursion and Sturm root count | supported |
| the certified finite-prefix interval is maximal | none | no evidence; explicitly not claimed | excluded |
| every initial point converges whenever `tau<tau_c` | none | local spectral analysis is insufficient | explicitly not claimed |
| the whole identity-slack model class converges after multiplier relaxation | none | counterexample-specific certificate only | explicitly not claimed |

Primary machine artifact:
`outputs/tau_relaxation_theory_2026-07-16/results/certificate.json`.

Review artifact:
`proof_reviews/relaxed_multiplier_interval_theory/verification_report.json`.
