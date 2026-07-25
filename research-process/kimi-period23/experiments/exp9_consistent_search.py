"""EXP9 (decisive, corrected matrices): search for SELF-CONSISTENT expanding
eigen-directions of the true pattern matrices (|t| = (Dp-Dm)t).

A self-consistent real eigenvalue mu>1 (eigenvector t-signs == sigma) gives a
rigorous divergence counterexample for the homogeneous quadratic class
(zero objectives included as special case), refuting the conjecture.

Sampling: PSD contractions with spectra biased toward 1 (weakest contraction),
plus pure projectors (f=g=0). For each: all 2^m patterns, all real eigenvalues
>1+tol, consistency check; if hit -> simulate to confirm geometric divergence
and save the instance.
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260723)


def pattern_mats(TA, TB, m):
    mats = []
    for mask in range(2 ** m):
        Dp = np.diag(np.array([(mask >> i) & 1 for i in range(m)], dtype=float))
        Dm = np.eye(m) - Dp
        J = Dp - Dm
        A_p = -TA; A_t = -TA @ J
        B_p = -TB @ A_p; B_t = -TB @ (A_t + J)
        C_p = -A_p - B_p; C_t = Dm - A_t - B_t
        mats.append(np.block([[B_p, B_t], [C_p, C_t]]))
    return mats


def consistent_directions(mats, m, tol=1e-9):
    """Yield (mask, mu, v) for real mu>1 with eigenvector t-signs == pattern."""
    for mask, M in enumerate(mats):
        ev, V = np.linalg.eig(M)
        sigma = np.array([1.0 if (mask >> i) & 1 else -1.0 for i in range(m)])
        for j in range(ev.size):
            mu = ev[j]
            if abs(mu.imag) < 1e-8 and mu.real > 1.0 + 1e-9:
                v = V[:, j].real
                if np.linalg.norm(M @ v - mu.real * v) > 1e-7 * abs(mu.real):
                    continue
                tv = v[m:]
                if np.all(np.abs(tv) > tol) and np.all(np.sign(tv) == sigma):
                    yield mask, mu.real, v


def rand_contraction(m, mode):
    U, _ = np.linalg.qr(rng.standard_normal((m, m)))
    if mode == "near1":
        s = 1.0 - 10.0 ** (-rng.uniform(0, 3, m))
    elif mode == "uniform":
        s = rng.random(m)
    else:  # projector: 0/1 spectrum
        s = (rng.random(m) < 0.5).astype(float)
    return U @ np.diag(s) @ U.T


def simulate(mats, m, v, K=300):
    cur = v.copy()
    norms = [np.linalg.norm(cur)]
    for k in range(K):
        p, t = cur[:m], cur[m:]
        mask = int(np.sum((t > 0) * (2.0 ** np.arange(m))))
        cur = mats[mask] @ cur
        norms.append(np.linalg.norm(cur))
    return np.array(norms)


t0 = time.time()
hits = []
stats = {"instances": 0, "patterns": 0, "rho_gt1": 0, "consistent": 0}
N = 30000
for it in range(N):
    m = int(rng.integers(2, 7))
    mode = ["near1", "uniform", "proj"][it % 3]
    TA = rand_contraction(m, mode); TB = rand_contraction(m, mode)
    mats = pattern_mats(TA, TB, m)
    rhos = [max(abs(np.linalg.eigvals(M))) for M in mats]
    stats["instances"] += 1
    stats["patterns"] += len(mats)
    if max(rhos) > 1.0:
        stats["rho_gt1"] += 1
        for mask, mu, v in consistent_directions(mats, m):
            stats["consistent"] += 1
            norms = simulate(mats, m, v / np.linalg.norm(v))
            grew = norms[-1] > 10.0
            hits.append(dict(it=it, m=m, mode=mode, mask=mask, mu=mu, grew=grew))
            np.savez(os.path.join(OUT, f"exp9_hit_{stats['consistent']}.npz"),
                     TA=TA, TB=TB, mask=mask, mu=mu, v=v, norms=norms)
            print(f"*** HIT it={it} m={m} mode={mode} mask={mask} mu={mu:.9f} "
                  f"sim300: {norms[-1]:.3e} {'DIVERGES' if grew else 'decays'}", flush=True)
    if it % 5000 == 0:
        print(f"it={it} elapsed={time.time()-t0:.0f}s stats={stats}", flush=True)

with open(os.path.join(OUT, "exp9_summary.json"), "w") as f:
    json.dump({"seed": 20260723, "stats": stats, "hits": hits,
               "elapsed_sec": time.time() - t0}, f, indent=2, default=str)
print(f"\nDONE: {stats}, hits={len(hits)}, elapsed={time.time()-t0:.0f}s")
