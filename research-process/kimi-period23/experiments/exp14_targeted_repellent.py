"""EXP14 (Track B, sharpest): targeted repelling-KKT construction.

exp12 showed random KKT cones have no complex |mu|>1 (0/8000), but KKT-by-
construction lets us CHOOSE the active set. Take instances where some pattern
sigma has complex |mu|>1, declare sigma to be the KKT cone (choose z*/lam*
with that sign pattern; b, c1, c2 follow), creating a problem whose KKT point
is locally repelling within its own cone (by Proposition C2, research/08).
Then simulate from perturbations of the KKT point and classify outcomes:
(a) back to v*, (b) converges to another fixed point, (c) limit cycle,
(d) growth > 1e6.  (c)/(d) = counterexample to He's conjecture.
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260726)


def pattern_matrix(TA, TB, m, mask):
    Dp = np.diag(np.array([(mask >> i) & 1 for i in range(m)], dtype=float))
    Dm = np.eye(m) - Dp
    J = Dp - Dm
    A_p = -TA; A_t = -TA @ J
    B_p = -TB @ A_p; B_t = -TB @ (A_t + J)
    C_p = -A_p - B_p; C_t = Dm - A_t - B_t
    return np.block([[B_p, B_t], [C_p, C_t]])


def rand_T(m):
    U, _ = np.linalg.qr(rng.standard_normal((m, m)))
    s = 1 - 10.0 ** (-rng.uniform(0, 2.5, m))
    return U @ np.diag(s) @ U.T


def simulate_outcome(A, B, F, G, b, c1, c2, xs, ys, t_star, eps=1e-3, ndirs=40, K=6000):
    m = A.shape[0]
    Hx = F + A.T @ A; Hy = G + B.T @ B
    res = {"to_v*": 0, "other_fp": 0, "cycle": 0, "growth": 0}
    for d in range(ndirs):
        dr = rng.standard_normal(2 * m); dr /= np.linalg.norm(dr)
        y = ys + eps * dr[:m]; t = t_star + eps * dr[m:]
        traj = []
        for k in range(K):
            at = np.abs(t)
            x = np.linalg.solve(Hx, -c1 - A.T @ (B @ y - b + at))
            y = np.linalg.solve(Hy, -c2 - B.T @ (A @ x - b + at))
            t = np.minimum(t, 0.0) - (A @ x + B @ y - b)
            if k >= K - 800:
                traj.append(np.concatenate([x, y, t]))
        if np.linalg.norm(np.concatenate([x, y, t])) > 1e6:
            res["growth"] += 1
            continue
        if max(np.linalg.norm(x - xs), np.linalg.norm(y - ys), np.linalg.norm(t - t_star)) < 1e-6:
            res["to_v*"] += 1
            continue
        cyc = any(np.linalg.norm(traj[k1] - traj[k2]) < 1e-9
                  for k1 in range(0, 600, 37) for k2 in range(k1 + 7, 800, 53))
        res["cycle" if cyc else "other_fp"] += 1
    return res


t0 = time.time()
found_complex = 0
outcomes_all = []
for it in range(60000):
    m = int(rng.integers(3, 7))
    TA, TB = rand_T(m), rand_T(m)
    hit = None
    for mask in rng.permutation(2 ** m):
        ev = np.linalg.eigvals(pattern_matrix(TA, TB, m, mask))
        cmplx = ev[np.abs(ev.imag) > 1e-9]
        if len(cmplx) and np.max(np.abs(cmplx)) > 1.0:
            hit = (int(mask), float(np.max(np.abs(cmplx))))
            break
    if hit is None:
        continue
    mask, mc = hit
    found_complex += 1
    wA, VA = np.linalg.eigh(TA); A = VA @ np.diag(np.sqrt(np.clip(wA, 0, None))) @ VA.T
    wB, VB = np.linalg.eigh(TB); B = VB @ np.diag(np.sqrt(np.clip(wB, 0, None))) @ VB.T
    F = np.eye(m) - TA; G = np.eye(m) - TB
    xs = rng.standard_normal(m); ys = rng.standard_normal(m)
    sigma = np.array([1.0 if (mask >> i) & 1 else -1.0 for i in range(m)])
    z = np.where(sigma > 0, rng.uniform(0.2, 1.5, m), 0.0)
    lam = np.where(sigma < 0, -rng.uniform(0.2, 1.5, m), 0.0)
    b = A @ xs + B @ ys + z
    c1 = A.T @ lam - F @ xs; c2 = B.T @ lam - G @ ys
    t_star = z + lam
    out = simulate_outcome(A, B, F, G, b, c1, c2, xs, ys, t_star)
    outcomes_all.append(dict(it=it, m=m, mask=mask, modulus=mc, out=out))
    tag = "  *** COUNTEREXAMPLE?" if (out["cycle"] or out["growth"]) else ""
    print(f"hit {found_complex}: m={m} |mu|={mc:.6f} outcomes={out}{tag}", flush=True)
    if out["cycle"] or out["growth"]:
        np.savez(os.path.join(OUT, f"exp14_repellent_{found_complex}.npz"),
                 A=A, B=B, F=F, G=G, b=b, c1=c1, c2=c2, xs=xs, ys=ys,
                 z=z, lam=lam, mask=mask, modulus=mc)
    if found_complex >= 30:
        break

with open(os.path.join(OUT, "exp14_summary.json"), "w") as f:
    json.dump({"seed": 20260726, "searched": it + 1, "constructed": found_complex,
               "outcomes": outcomes_all, "elapsed_sec": time.time() - t0},
              f, indent=2, default=str)
print(f"\nsearched {it+1}, constructed repelling-KKT instances: {found_complex}, "
      f"elapsed={time.time()-t0:.0f}s")
