# Exact Periodic Nonconvergence Certificates for Identity-Slack Three-Block ADMM

**English** | [简体中文](README.zh-CN.md)

[![Exact certificate](https://github.com/ConanXu-math/identity-slack-admm-cycle-certificate/actions/workflows/certificate.yml/badge.svg)](https://github.com/ConanXu-math/identity-slack-admm-cycle-certificate/actions/workflows/certificate.yml)

This repository accompanies the manuscript
**“A Counterexample to the Convergence of Three-Block ADMM with an Identity
Third Constraint Block.”** It provides exact, replayable evidence for two
fixed convex quadratic programs on which the unmodified direct three-block
ADMM has a bounded non-KKT periodic sequence, despite a unique KKT point.

## Start here

| If you want to... | Start with |
| --- | --- |
| Read the mathematical argument | [Compiled manuscript](paper/slack_admm_arxiv.pdf) |
| Verify both counterexamples | [Five-minute verification](#five-minute-verification) |
| Inspect the exact machine certificates | [`certificates/`](certificates/) |
| Understand what each checker proves | [Reproducibility contract](docs/REPRODUCIBILITY.md) |
| Follow the Codex and Kimi discovery routes | [Research-stage index](research-process/INDEX.md) |
| Review time, token, and agent accounting | [Computational provenance](provenance/README.md) |
| Run the independent MATLAB check | [MATLAB instructions](matlab/README.md) |

The root package is the acceptance layer. The
[`research-process/`](research-process/) archive is historical evidence about
how the results were found; it is not a second acceptance layer.

## Certified results

| Certificate ID | Fixed instance | Exact conclusion | Main evidence |
| --- | --- | --- | --- |
| `identity_slack_p66_short_v1` | `m = 2`, `A = B = I_2`, `beta = 1` | A specified initialization generates a bounded non-KKT orbit of minimal period 66 | two independent Python representations and a MATLAB implementation |
| `identity_slack_p23_rational_v1` | `m = 3`, rational QP data, `beta = 1` | An open invariant set of reduced initializations converges phasewise to a non-KKT orbit of minimal period 23 | exact rational replay and Lyapunov certificate |

### Period 66

- Projection word: `(00)^2(01)^64`.
- Exact closure and minimal period: `66`.
- Strict projection checks: `132/132`.
- Minimum signed margin:
  `0.0037105246944352910173... > 1/1000`.
- The orbit is bounded and non-KKT; the QP has a unique KKT point.
- This certificate concerns a deliberately specified initialization. It does
  not claim attraction, unbounded divergence, or failure of corrected ADMM
  variants.

### Period 23

- All primitive QP coefficients are reduced fractions with numerator
  magnitude and denominator at most `100`.
- The frozen certificate contains the complete exact phase-zero state
  `(x^0,y^0,z^0,lambda^0)`.
- Exact closure and minimal period: `23`.
- Strict projection checks: `69/69`, with minimum margin greater than `1/250`.
- A rational matrix `P` satisfies
  `P - M_per^T P M_per > 0` exactly.
- The ellipsoid `e^T P e < 1/4000` is return-invariant in the canonical
  reduced `(y,t)` state, and every initialization in it converges phasewise
  to the period-23 sequence.
- This is a neighborhood of initializations for one fixed QP, not a
  perturbation result for the QP data or a global attraction theorem.

The Kimi Code K3 route originally reached an exact dyadic period-23 replay and
an exact Jury local-attraction certificate. The denominator-100 instance and
explicit invariant ellipsoid above are later release strengthening; see the
[`route attestation`](provenance/routes/kimi-period23/run_attestation.json).

### Multiplier relaxation for the period-66 QP

The exact relaxation certificate proves three separate statements:

1. one rational Lyapunov matrix works on the strict KKT branch for every
   `tau in [49/100, 51/100]`;
2. the former period-66 initialization follows a certified strict prefix for
   232 steps and enters the invariant ellipsoid for every
   `tau in [1/2 - 10^-10, 1/2 + 10^-10]`;
3. the strict KKT branch has a unique Schur boundary satisfying
   `0.9366061114 < tau_c < 0.9366061115`.

These are local or fixed-initialization results. They do not establish global
convergence from arbitrary initial points.

## Five-minute verification

The frozen Python environment is 3.13.5 with SymPy 1.13.3, NumPy 2.1.3, and
pytest 8.3.4.

```bash
git clone https://github.com/ConanXu-math/identity-slack-admm-cycle-certificate.git
cd identity-slack-admm-cycle-certificate
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python python/verify_all.py
python python/verify_research_process_archive.py
```

The certificate command should end with:

```json
{"checks": [{"name": "period66", "returncode": 0, "status": "passed"}, {"name": "period23", "returncode": 0, "status": "passed"}], "valid": true}
```

For the full release check used by GitHub Actions:

```bash
python python/verify_all.py
python python/verify_research_process_archive.py
python python/export_orbit_66.py
python python/certify_relaxed_multiplier_interval_theory.py
python python/verify_universal_step_obstruction.py --check
python -m pytest -q python/tests/test_relaxed_multiplier_interval_theory.py
python -m unittest discover -s tests -p "test_*.py"
python python/verify_matlab_certificate.py
git diff --exit-code -- certificates/
```

The last command is part of acceptance: regeneration must leave every tracked
certificate byte-for-byte unchanged.

## How the evidence is organized

| Layer | Purpose | Authoritative entry point |
| --- | --- | --- |
| Exact acceptance | Rebuilds the fixed QPs and checks every finite proof obligation | [`python/verify_all.py`](python/verify_all.py) |
| Frozen data | Canonical inputs, exact orbits, verdicts, hashes, and Lyapunov data | [`certificates/`](certificates/) |
| Implementation cross-checks | Independent signed-state, full-state, and MATLAB implementations for period 66 | [`python/README.md`](python/README.md), [`matlab/README.md`](matlab/README.md) |
| Process archive | Selected theory, experiments, failures, state files, and internal reviews | [`research-process/INDEX.md`](research-process/INDEX.md) |
| Route accounting | Scope and telemetry for the Codex/Kimi comparison | [`provenance/README.md`](provenance/README.md) |
| Continuous integration | Clean-environment regeneration and artifact-stability gate | [Exact certificate workflow](.github/workflows/certificate.yml) |

Agreement between implementations is an internal reproducibility cross-check,
not external peer review.

## Reading the research process

Use [`research-process/INDEX.md`](research-process/INDEX.md) rather than
browsing the archive chronologically:

- **Codex / period 66:** begin with the persistent task state and algebraic
  reductions, then follow Stages 43–46 from obstruction to numerical
  discovery, rationalization, exact replay, and precision audit.
- **Kimi Code K3 / period 23:** begin with `START_GOAL.txt` and
  `RESEARCH_LOG.md`, then follow the withdrawn routes, targeted instability
  experiments, period locking, and the exact certificate.

Archive labels matter:

- `numerical_screen` and `proof_attempt` are exploratory;
- `withdrawn` records a route that was rejected;
- `theorem` and `exact_certificate` are accepted only within their stated
  scope;
- `review` means an internal check, not external peer review.

Raw chats, credentials, private configuration, local absolute paths, caches,
and repetitive bulk outputs are intentionally excluded. The 168 retained
files are covered by [`research-process/manifest.json`](research-process/manifest.json)
and checked in CI.

## MATLAB reproduction

The MATLAB verifier covers the period-66 instance and requires MATLAB R2025a,
Symbolic Math Toolbox, and a valid license:

```matlab
addpath("matlab")
result = verify_exact_cycle_matlab();
assert(result.valid)
```

Then compare the generated MATLAB JSON against the frozen Python fields:

```bash
python python/verify_matlab_certificate.py
```

See [`matlab/README.md`](matlab/README.md) for the class-based test and licensed
GitHub Actions instructions.

## Repository map

```text
.
├── python/             exact Python verifiers and comparison drivers
├── matlab/             independent period-66 MATLAB verifier and tests
├── certificates/       frozen inputs and machine-readable certificates
├── research-process/   curated Codex and Kimi discovery archives
├── provenance/         comparison scope, accounting, and evidence boundaries
├── docs/               detailed reproducibility contract
├── paper/              compiled manuscript PDF
└── .github/            CI workflows and ownership rules
```

For script-level descriptions, see [`python/README.md`](python/README.md). For
the exact predicates, artifact meanings, runtime contract, and release
checklist, see [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

## Scope of the Codex–Kimi comparison

The two routes independently reached exact counterexamples to the same
proposed convergence principle, but they did not solve the same QP and were
not matched in compute, tools, telemetry, stopping policy, or human
intervention. The comparison is descriptive and endpoint-aligned; it cannot
support a causal ranking of model speed, cost, or capability.

## Release and citation status

This repository is currently private and has no public software license.
Before public release, the maintainers must freeze the author list, add
`CITATION.cff`, select a license, create an immutable tagged archive, assign
a DOI, and make the manuscript and code-availability statement point to that
same release.

Repository owner: [ConanXu-math](https://github.com/ConanXu-math).
