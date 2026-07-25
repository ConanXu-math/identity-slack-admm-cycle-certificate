"""EXP7 (Track B): Exhaustive search for REALIZABLE expanding periodic orbits
in the homogeneous convex-quadratic slack-ADMM class.

By Theorem Q no single pattern cone can expand; a homogeneous divergence
counterexample must be a periodic orbit cycling through >=2 cones with
product eigenvalue mu>1 and sign-consistent orbit (self-realizable sequence).

For each instance (T_A, T_B symmetric PSD contractions, spectra biased toward 1):
  DFS over pattern sequences up to depth K;
  at every node: if product P has a real eigenvalue mu > 1+tol,
    take eigenvector v, simulate the TRUE piecewise orbit from v for len(seq)
    steps and check the realized sign pattern == seq and v_K ≈ mu*v.
  If consistent -> rigorous counterexample candidate (saved to results/).

m=2: K<=8 (all 4^<=8 ≈ 87k sequences per instance, 400 instances)
m=3: K<=5 (8^<=5 ≈ 37k sequences per instance, 200 instances)
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from exp5_jsr_lite import pattern_mats_from_contractions

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260723)
TOL = 1e-7


def rand_contraction_near1(m):
    U, _ = np.linalg.qr(rng.standard_normal((m, m)))
    s = 1.0 - 10.0 ** (-rng.uniform(0.0, 3.0, m))   # eigenvalues in [0,1), biased to 1
    s[rng.random(m) < 0.25] = 0.0
    return U @ np.diag(s) @ U.T


def simulate_check(mats_full, m, seq, v, mu):
    """Simulate true piecewise map from v (state (p,t) full R^{2m}) and verify
    the realized sign sequence equals seq and the orbit closes as mu*v."""
    cur = v.copy()
    for step, pat_idx in enumerate(seq):
        # apply one true piecewise step
        p, t = cur[:m], cur[m:]
        Dp = np.diag((t > 0).astype(float))
        realized = int(np.sum((t > 0) * (2 ** np.arange(m))))
        if realized != pat_idx:
            return False
        cur = mats_full[pat_idx] @ cur
    return np.linalg.norm(cur - mu * v) <= 1e-5 * max(1.0, abs(mu)) * np.linalg.norm(v)


def full_mats(TA, TB, m):
    """Pattern matrices on the FULL state (p,t) in R^{2m} (p unrestricted)."""
    out = []
    for mask in range(2 ** m):
        Dp = np.diag(np.array([(mask >> i) & 1 for i in range(m)], dtype=float))
        Dm = np.eye(m) - Dp
        J = Dp - Dm
        A_p = -TA; A_t = -TA @ J
        B_p = -TB @ A_p; B_t = -TB @ (A_t + J)
        C_p = -A_p - B_p; C_t = Dm - A_t - B_t
        out.append(np.block([[B_p, B_t], [C_p, C_t]]))
    return out


def search_instance(TA, TB, m, K):
    mats = full_mats(TA, TB, m)
    n = len(mats)
    d = 2 * m
    # DFS over sequences
    stack = [(np.eye(d), ())]
    while stack:
        P, seq = stack.pop()
        if seq:
            ev, V = np.linalg.eig(P)
            for j in range(ev.size):
                mu = ev[j]
                if abs(mu.imag) < 1e-9 and mu.real > 1.0 + TOL:
                    v = V[:, j].real
                    nrm = np.linalg.norm(v)
                    if nrm < 1e-12:
                        continue
                    v = v / nrm
                    if simulate_check(mats, m, seq, v, mu.real):
                        return dict(seq=seq, mu=mu.real, v=v, P=P)
        if len(seq) < K:
            for i in range(n):
                stack.append((P @ mats[i], seq + (i,)))
    return None


found = []
t0 = time.time()
stats = {"m2_instances": 0, "m3_instances": 0, "seqs_checked": 0}

for idx in range(400):
    m = 2
    TA, TB = rand_contraction_near1(m), rand_contraction_near1(m)
    hit = search_instance(TA, TB, m, K=8)
    stats["m2_instances"] += 1
    if hit:
        found.append(dict(m=m, idx=idx, mu=hit["mu"], seq=hit["seq"]))
        np.savez(os.path.join(OUT, f"exp7_counterexample_m2_{idx}.npz"),
                 TA=TA, TB=TB, seq=np.array(hit["seq"]), mu=hit["mu"], v=hit["v"])
        print(f"*** COUNTEREXAMPLE m=2 idx={idx} mu={hit['mu']:.9f} seq={hit['seq']}")
        break
    if idx % 50 == 0:
        print(f"m=2 instance {idx}/400, elapsed {time.time()-t0:.0f}s", flush=True)

if not found:
    for idx in range(200):
        m = 3
        TA, TB = rand_contraction_near1(m), rand_contraction_near1(m)
        hit = search_instance(TA, TB, m, K=5)
        stats["m3_instances"] += 1
        if hit:
            found.append(dict(m=m, idx=idx, mu=hit["mu"], seq=hit["seq"]))
            np.savez(os.path.join(OUT, f"exp7_counterexample_m3_{idx}.npz"),
                     TA=TA, TB=TB, seq=np.array(hit["seq"]), mu=hit["mu"], v=hit["v"])
            print(f"*** COUNTEREXAMPLE m=3 idx={idx} mu={hit['mu']:.9f} seq={hit['seq']}")
            break
        if idx % 20 == 0:
            print(f"m=3 instance {idx}/200, elapsed {time.time()-t0:.0f}s", flush=True)

with open(os.path.join(OUT, "exp7_summary.json"), "w") as f:
    json.dump({"seed": 20260723, "stats": stats, "found": found,
               "K_m2": 8, "K_m3": 5, "elapsed_sec": time.time() - t0},
              f, indent=2, default=str)
print(f"\nDONE: {stats}, found={len(found)}, elapsed={time.time()-t0:.0f}s")
