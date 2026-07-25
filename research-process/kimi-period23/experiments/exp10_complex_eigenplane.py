"""EXP10 (Track B, targeted): exploit complex eigenvalues |mu|>1 of the TRUE
pattern matrices. For instances where some pattern matrix M_sigma has a complex
eigenvalue with |mu|>1: simulate the true piecewise map from many starting
points in the expanding eigenplane span(v_re, v_im) (24 angles), K=2000 steps,
and record max norm growth. Any sustained growth -> divergence candidate.
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260724)


def pattern_mats_proj(P, Q, m):
    mats = []
    for mask in range(2 ** m):
        Dp = np.diag(np.array([(mask >> i) & 1 for i in range(m)], dtype=float))
        Dm = np.eye(m) - Dp
        J = Dp - Dm
        A_p = -P; A_t = -P @ J
        B_p = -Q @ A_p; B_t = -Q @ (A_t + J)
        C_p = -A_p - B_p; C_t = Dm - A_t - B_t
        mats.append(np.block([[B_p, B_t], [C_p, C_t]]))
    return mats


def piecewise_run(mats, m, v0, K=2000):
    v = v0.copy()
    n0 = np.linalg.norm(v)
    mx = 1.0
    for k in range(K):
        t = v[m:]
        mask = int(np.sum((t > 0) * (2.0 ** np.arange(m))))
        v = mats[mask] @ v
        n = np.linalg.norm(v)
        mx = max(mx, n / n0)
        if n > 1e12:
            return mx, True
    return mx, False


t0 = time.time()
stats = dict(instances=0, with_complex_gt1=0, max_growth=0.0)
suspects = []
for it in range(30000):
    m = int(rng.integers(3, 6))
    dA = int(rng.integers(1, m)); dB = int(rng.integers(1, m))
    UA, _ = np.linalg.qr(rng.standard_normal((m, dA)))
    UB, _ = np.linalg.qr(rng.standard_normal((m, dB)))
    P = UA @ UA.T; Q = UB @ UB.T
    mats = pattern_mats_proj(P, Q, m)
    stats["instances"] += 1
    for mask, M in enumerate(mats):
        ev, V = np.linalg.eig(M)
        for j in range(ev.size):
            if abs(ev[j]) > 1.0001 and abs(ev[j].imag) > 1e-9:
                stats["with_complex_gt1"] += 1
                vre, vim = V[:, j].real, V[:, j].imag
                best = 0.0
                for ang in np.linspace(0, 2 * np.pi, 24, endpoint=False):
                    v0 = np.cos(ang) * vre + np.sin(ang) * vim
                    v0 /= np.linalg.norm(v0)
                    g, blew = piecewise_run(mats, m, v0)
                    best = max(best, g)
                    if blew:
                        print(f"*** BLOWUP it={it} m={m} mask={mask} |mu|={abs(ev[j]):.6f} angle={ang:.2f}")
                        np.savez(os.path.join(OUT, f"exp10_blowup_{it}.npz"),
                                 P=P, Q=Q, mask=mask, mu=ev[j], v0=v0)
                stats["max_growth"] = max(stats["max_growth"], best)
                if best > 2.0:
                    suspects.append(dict(it=it, m=m, mask=mask, mu=complex(ev[j]).__repr__(), growth=best))
    if it % 10000 == 0:
        print(f"it={it} stats={stats} suspects={len(suspects)}", flush=True)

with open(os.path.join(OUT, "exp10_summary.json"), "w") as f:
    json.dump({"seed": 20260724, "stats": stats, "suspects": suspects,
               "elapsed_sec": time.time() - t0}, f, indent=2, default=str)
print(f"\nDONE: {stats}, suspects={len(suspects)}, elapsed={time.time()-t0:.0f}s")
