"""EXP17b: dense eps scan for period-locked attracting cycles.

Context (exp15/16): strictified projector instances (unique KKT point,
KKT-cone complex |mu|>1) show bounded, non-convergent, quasi-periodic
orbits. eps controls the eigenvalue modulus: eps=1e-3 non-convergent,
eps=3e-2 convergent (period 1). Between them, Arnol'd-tongue-type
period-locking windows are expected. Scan eps densely; at each value,
run 150k steps, test late pattern sequence for exact periodicity
(period <= 3000). For each periodic window: verify the cycle
(pattern-consistent fixed point of the period map, rho<1, cycle != KKT).
A verified cycle with rho<1 is a rigorous counterexample to convergence.
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260727)

data = np.load(os.path.join(OUT, "exp14_top_projector_hits.npz"))
meta = data["meta"]


def find_period(seq, maxp=3000):
    n = len(seq)
    for p in range(1, maxp):
        if n >= 3 * p and np.all(seq[: n - p] == seq[p: n]):
            return p
    return None


def run_at_eps(PA, PB, m, mask, eps):
    TA = (1 - eps) * PA + eps * (np.eye(m) - PA)
    TB = (1 - eps) * PB + eps * (np.eye(m) - PB)
    wA, VA = np.linalg.eigh(TA); A = VA @ np.diag(np.sqrt(np.clip(wA, 0, None))) @ VA.T
    wB, VB = np.linalg.eigh(TB); B = VB @ np.diag(np.sqrt(np.clip(wB, 0, None))) @ VB.T
    F = np.eye(m) - TA; G = np.eye(m) - TB
    sigma = np.array([1.0 if (mask >> i) & 1 else -1.0 for i in range(m)])
    xs = rng.standard_normal(m); ys = rng.standard_normal(m)
    z = np.where(sigma > 0, rng.uniform(0.3, 1.5, m), 0.0)
    lam = np.where(sigma < 0, -rng.uniform(0.3, 1.5, m), 0.0)
    b = A @ xs + B @ ys + z
    c1 = A.T @ lam - F @ xs; c2 = B.T @ lam - G @ ys
    t_star = z + lam
    Hx = F + A.T @ A; Hy = G + B.T @ B

    def step(x, y, t):
        at = np.abs(t)
        x2 = np.linalg.solve(Hx, -c1 - A.T @ (B @ y - b + at))
        y2 = np.linalg.solve(Hy, -c2 - B.T @ (A @ x2 - b + at))
        t2 = np.minimum(t, 0.0) - (A @ x2 + B @ y2 - b)
        return x2, y2, t2

    dr = rng.standard_normal(2 * m); dr /= np.linalg.norm(dr)
    x, y, t = np.zeros(m), ys + 1e-3 * dr[:m], t_star + 1e-3 * dr[m:]
    pats = []
    for k in range(150000):
        x, y, t = step(x, y, t)
        if k >= 100000:
            pats.append(int(np.sum((t > 0) * (2.0 ** np.arange(m)))))
    pats = np.array(pats)
    p = find_period(pats)
    if p is None:
        return None, None
    per = pats[:p]

    def period_map(v):
        xx, yy, tt = v[:m].copy(), v[m:2 * m].copy(), v[2 * m:].copy()
        for _ in range(p):
            xx, yy, tt = step(xx, yy, tt)
        return np.concatenate([xx, yy, tt])

    n = 3 * m
    c0 = period_map(np.zeros(n))
    M = np.column_stack([period_map(np.eye(n)[j]) - c0 for j in range(n)])
    rho = float(max(abs(np.linalg.eigvals(M))))
    try:
        vfix = np.linalg.solve(np.eye(n) - M, c0)
    except np.linalg.LinAlgError:
        return dict(period=p, rho=rho, error="singular"), None
    xx, yy, tt = vfix[:m].copy(), vfix[m:2 * m].copy(), vfix[2 * m:].copy()
    consistent = True
    for j in range(p):
        pat = int(np.sum((tt > 0) * (2.0 ** np.arange(m))))
        if pat != per[j]:
            consistent = False
            break
        xx, yy, tt = step(xx, yy, tt)
    err = float(np.linalg.norm(np.concatenate([xx, yy, tt]) - vfix))
    dist_kkt = float(np.linalg.norm(vfix - np.concatenate([xs, ys, t_star])))
    rec = dict(period=p, rho=rho, consistent=consistent, err=err,
               dist_kkt=dist_kkt, eps=eps, m=m, mask=mask,
               A=A, B=B, F=F, G=G, b=b, c1=c1, c2=c2,
               xs=xs, ys=ys, z=z, lam=lam, vfix=vfix, per=per)
    return rec, per


t0 = time.time()
certified = []
scan_log = []
for inst_i in range(3):
    mc0, m, dA, dB, mask = meta[inst_i]
    m, mask = int(m), int(mask)
    PA, PB = data[f"PA_{inst_i}"], data[f"PB_{inst_i}"]
    for eps in np.concatenate([np.linspace(1e-3, 1e-2, 10), np.linspace(1.2e-2, 3e-2, 10)]):
        rec, per = run_at_eps(PA, PB, m, mask, float(eps))
        if rec is None:
            scan_log.append((inst_i, float(eps), None))
            continue
        scan_log.append((inst_i, float(eps), rec["period"]))
        ok = (rec.get("consistent") and rec["err"] < 1e-9
              and rec["rho"] < 1.0 and rec["dist_kkt"] > 1e-3)
        print(f"inst={inst_i} eps={eps:.4f}: period={rec['period']} "
              f"rho={rec.get('rho'):.4f} consistent={rec.get('consistent')} "
              f"err={rec.get('err'):.1e} dKKT={rec.get('dist_kkt'):.3f}"
              + ("  *** CERTIFIED" if ok else ""), flush=True)
        if ok:
            certified.append(rec)
            np.savez(os.path.join(OUT, f"exp17b_cycle_i{inst_i}_e{eps:.4f}.npz"),
                     **{k: (np.array(v) if isinstance(v, list) else v)
                        for k, v in rec.items()})

with open(os.path.join(OUT, "exp17b_summary.json"), "w") as f:
    json.dump({"seed": 20260727, "scan": scan_log,
               "certified": [{k: (v.tolist() if isinstance(v, np.ndarray) else v)
                              for k, v in r.items() if k != "per"}
                             for r in certified],
               "elapsed_sec": time.time() - t0}, f, indent=2, default=str)
print(f"\nDONE: certified={len(certified)}, elapsed={time.time()-t0:.0f}s")
