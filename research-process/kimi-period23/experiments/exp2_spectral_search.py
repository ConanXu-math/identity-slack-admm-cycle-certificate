"""EXP2: Adversarial spectral search for divergence in the SLACK case
(three-block [A,B,I], theta3 = delta_+, homogeneous zero-objective setting).

By research/01_theory_notes.md Sec.5: divergence of the positively homogeneous
piecewise-linear iteration is implied by a self-consistent real eigenvalue
mu > 1 of some pattern matrix M_sigma (eigenvector t-signs match sigma).

Phase A: random scan over subspace pairs (range A, range B) for m=2,3,4,
         all 2^m sign patterns each; record max spectral radius and best
         self-consistent real eigenvalue > 1.
Phase B: for the highest-rho instances, simulate the actual piecewise map
         from random starts (K=4000) and measure growth.

Seeds fixed; results written to experiments/results/.
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from admm_core import homog_slack_matrix, homog_slack_step

OUT = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20260722)
t_start = time.time()


def consistent_real_expanding(A, B, sigma, tol=1e-8):
    """Return (mu, v) with largest real mu>0 whose eigenvector's t-part signs
    strictly match sigma, or (None, None)."""
    M = homog_slack_matrix(A, B, sigma)
    ev, V = np.linalg.eig(M)
    dB = B.shape[1]
    best = (None, None)
    for j in range(ev.size):
        mu = ev[j]
        if abs(mu.imag) < 1e-9 and mu.real > 0:
            v = V[:, j].real
            if np.linalg.norm(M @ v - mu.real * v) > 1e-6 * max(1.0, abs(mu.real)):
                continue
            tvec = v[dB:]
            if np.all(np.abs(tvec) > tol) and np.all(np.sign(tvec) == sigma):
                if best[0] is None or mu.real > best[0]:
                    best = (mu.real, v)
    return best


def rand_subspace(m, d):
    Q, _ = np.linalg.qr(rng.standard_normal((m, d)))
    return Q


records = []
top = []  # (rho, A, B, sigma)

def scan(m, dA, dB, n_samples):
    global top
    best_rho = 0.0; best_mu = 0.0; best_rho_info = None; best_mu_info = None
    for s in range(n_samples):
        A = rand_subspace(m, dA); B = rand_subspace(m, dB)
        for mask in range(2 ** m):
            sigma = np.array([1.0 if (mask >> i) & 1 else -1.0 for i in range(m)])
            M = homog_slack_matrix(A, B, sigma)
            ev = np.linalg.eigvals(M)
            rho = float(np.max(np.abs(ev)))
            if rho > best_rho:
                best_rho = rho; best_rho_info = (sigma.copy(), s)
            if rho > 1.0 + 1e-9:
                mu, v = consistent_real_expanding(A, B, sigma)
                if mu is not None and mu > best_mu:
                    best_mu = mu; best_mu_info = (sigma.copy(), s, v.copy(), A.copy(), B.copy())
            if rho > 0.999:
                top.append((rho, A.copy(), B.copy(), sigma.copy(), s))
    top.sort(key=lambda r: -r[0]); top = top[:20]
    rec = dict(m=m, dA=dA, dB=dB, n=n_samples, max_rho=best_rho,
               max_consistent_mu=best_mu)
    records.append(rec)
    print(f"m={m} dA={dA} dB={dB} N={n_samples}: max rho={best_rho:.9f} "
          f"(pattern {best_rho_info[0].astype(int)}, sample {best_rho_info[1]}), "
          f"max self-consistent mu={best_mu if best_mu>0 else 'none'}")
    if best_mu_info is not None:
        sigma, s, v, A, B = best_mu_info
        np.savez(os.path.join(OUT, f"exp2_counterexample_m{m}_dA{dA}_dB{dB}.npz"),
                 A=A, B=B, sigma=sigma, v=v, mu=best_mu)
    return best_rho, best_mu


# ---- Phase A: random scan
print("=== Phase A: random subspace scan ===")
for (m, dA, dB, N) in [(2, 1, 1, 20000),
                       (3, 1, 1, 20000), (3, 1, 2, 10000), (3, 2, 2, 10000),
                       (4, 1, 1, 10000), (4, 2, 2, 6000), (4, 1, 3, 6000),
                       (4, 2, 3, 6000), (4, 3, 3, 6000),
                       (5, 2, 2, 3000), (5, 2, 3, 3000), (5, 3, 3, 3000)]:
    scan(m, dA, dB, N)

print("\n=== Phase B: simulate piecewise map for top-rho instances ===")
div_found = 0
for (rho, A, B, sigma, s) in top[:12]:
    m = A.shape[0]; n2 = B.shape[1]
    grew = False
    for trial in range(3):
        y = rng.standard_normal(n2); t = rng.standard_normal(m)
        n0 = np.linalg.norm(y) + np.linalg.norm(t)
        for k in range(4000):
            y, t = homog_slack_step(A, B, y, t)
        n1 = np.linalg.norm(y) + np.linalg.norm(t)
        if n1 > 1e6 * max(n0, 1e-12):
            grew = True
    tag = "DIVERGES(sim)" if grew else "bounded(sim)"
    if grew: div_found += 1
    print(f"rho={rho:.9f} m={m} sigma={sigma.astype(int)} sim: {tag}")

with open(os.path.join(OUT, "exp2_summary.json"), "w") as f:
    json.dump({"seed": 20260722, "records": records,
               "elapsed_sec": time.time() - t_start,
               "sim_divergences": div_found}, f, indent=2, default=str)
print(f"\nDone in {time.time()-t_start:.1f}s. Summary in {OUT}/exp2_summary.json")
print("Interpretation: max_consistent_mu>1 => rigorous counterexample candidate;",
      "max rho<=1 everywhere => evidence for homogeneous-case nonexpansiveness.")
