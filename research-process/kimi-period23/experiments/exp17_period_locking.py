"""EXP17: hunt for period-locked attracting cycles (certifiable counterexample).

Strategy: for the top complex-|mu|>1 projector instances, strictify with
varying eps (this tunes the rotation number; period-locking windows should
exist). At each eps: run the true ADMM 120k steps from a perturbed start,
test the late pattern sequence for exact periodicity (period <= 500).
When periodic: build the product affine map of one period, check
rho < 1 (attraction), solve the affine fixed point, verify pattern
consistency and ||Phi^p(v) - v||, and confirm the cycle != KKT point.
A verified cycle with rho < 1 is a RIGOROUS counterexample to convergence
(open basin, unique KKT point, strictly convex quadratic instance).
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260727)

data = np.load(os.path.join(OUT, "exp14_top_projector_hits.npz"))
meta = data["meta"]


def find_period(seq, maxp=500):
    n = len(seq)
    for p in range(1, maxp):
        if np.all(seq[: n - p] == seq[p: n]):
            return p
    return None


def try_instance(PA, PB, m, mask, eps, verbose=False):
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
    for k in range(120000):
        x, y, t = step(x, y, t)
        if k >= 90000:
            pats.append(int(np.sum((t > 0) * (2.0 ** np.arange(m)))))
    pats = np.array(pats)
    p = find_period(pats)
    if p is None:
        return None
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
        return dict(period=p, error="singular I-M", rho=rho)
    # verify: iterate true map from vfix, check pattern consistency + return
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
    return dict(period=p, rho=rho, consistent=consistent, err=err,
                dist_kkt=dist_kkt, eps=eps, m=m, mask=mask,
                A=A, B=B, F=F, G=G, b=b, c1=c1, c2=c2,
                xs=xs, ys=ys, z=z, lam=lam, vfix=vfix, per=per.tolist())


t0 = time.time()
certified = []
for inst_i in range(4):
    mc0, m, dA, dB, mask = meta[inst_i]
    m, mask = int(m), int(mask)
    PA, PB = data[f"PA_{inst_i}"], data[f"PB_{inst_i}"]
    for eps in [1e-3, 2e-3, 3e-3, 5e-3, 8e-3, 1.2e-2, 2e-2, 3e-2, 5e-2]:
        r = try_instance(PA, PB, m, mask, eps)
        if r is None:
            continue
        print(f"inst={inst_i} eps={eps}: PERIOD {r['period']} found, rho={r.get('rho'):.6f}, "
              f"consistent={r.get('consistent')}, err={r.get('err'):.2e}, "
              f"dist_to_KKT={r.get('dist_kkt'):.3f}", flush=True)
        if (r.get("consistent") and r["err"] < 1e-9 and r["rho"] < 1.0
                and r["dist_kkt"] > 1e-3):
            certified.append(r)
            np.savez(os.path.join(OUT, f"exp17_cycle_inst{inst_i}_eps{eps}.npz"),
                     **{k: v for k, v in r.items() if k != "per"}, per=np.array(r["per"]))
            print(f"*** CERTIFIED ATTRACTING CYCLE (inst={inst_i}, eps={eps}, "
                  f"period={r['period']}, rho={r['rho']:.6f}) ***", flush=True)

with open(os.path.join(OUT, "exp17_summary.json"), "w") as f:
    json.dump({"seed": 20260727, "certified": [
        {k: (v.tolist() if isinstance(v, np.ndarray) else v)
         for k, v in r.items() if k != "per"} for r in certified],
        "elapsed_sec": time.time() - t0}, f, indent=2, default=str)
print(f"\nDONE: certified cycles: {len(certified)}, elapsed={time.time()-t0:.0f}s")
