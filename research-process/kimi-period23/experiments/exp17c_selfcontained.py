"""EXP17c: self-contained period-lock hunt with CORRECT verification.

Pipeline per (instance, eps): run 150k-step orbit -> detect exact period p of
the late pattern sequence -> build the product affine map FROM THE OBSERVED
pattern sequence -> solve its fixed point -> check sign consistency along a
TRUE cycle -> verify err, rho(product), and distance from the KKT point.

Certified outcomes:
  (A) consistent cycle, rho < 1, != KKT  -> attracting periodic orbit:
      rigorous counterexample with an OPEN basin of non-converging starts.
  (B) consistent cycle, rho >= 1, != KKT -> exact periodic orbit:
      rigorous counterexample from that specific starting point.
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260729)

data = np.load(os.path.join(OUT, "exp14_top_projector_hits.npz"))
meta = data["meta"]


def build(PA, PB, m, mask, eps):
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
    Hx = F + A.T @ A; Hy = G + B.T @ B
    return dict(A=A, B=B, F=F, G=G, b=b, c1=c1, c2=c2, xs=xs, ys=ys, z=z, lam=lam, Hx=Hx, Hy=Hy)


def true_step(inst, v, m):
    x, y, t = v[:m], v[m:2 * m], v[2 * m:]
    at = np.abs(t)
    x2 = np.linalg.solve(inst["Hx"], -inst["c1"] - inst["A"].T @ (inst["B"] @ y - inst["b"] + at))
    y2 = np.linalg.solve(inst["Hy"], -inst["c2"] - inst["B"].T @ (inst["A"] @ x2 - inst["b"] + at))
    t2 = np.minimum(t, 0.0) - (inst["A"] @ x2 + inst["B"] @ y2 - inst["b"])
    return np.concatenate([x2, y2, t2])


def affine_mats(inst, m):
    A, B, Hx, Hy = inst["A"], inst["B"], inst["Hx"], inst["Hy"]
    b, c1, c2 = inst["b"], inst["c1"], inst["c2"]
    Hxi = np.linalg.inv(Hx); Hyi = np.linalg.inv(Hy)
    Z = np.zeros((m, m))
    out = {}
    for mask in range(2 ** m):
        Dp = np.diag(np.array([(mask >> i) & 1 for i in range(m)], dtype=float))
        Dm = np.eye(m) - Dp
        J = Dp - Dm
        P1 = -Hxi @ A.T @ B; P2 = -Hxi @ A.T @ J; q1 = -Hxi @ (c1 - A.T @ b)
        R1 = -Hyi @ B.T @ A; R2 = -Hyi @ B.T @ J; q2 = -Hyi @ (c2 - B.T @ b)
        M = np.block([
            [Z, P1, P2],
            [R1 @ Z, R1 @ P1, R1 @ P2 + R2],
            [-A @ Z - B @ (R1 @ Z), -A @ P1 - B @ (R1 @ P1), -A @ P2 - B @ (R1 @ P2 + R2) + Dm]])
        c = np.concatenate([q1, R1 @ q1 + q2, -A @ q1 - B @ (R1 @ q1 + q2) + b])
        out[mask] = (M, c)
    return out


def process(inst, m, K=150000, skip=100000):
    t_star = inst["z"] + inst["lam"]
    dr = rng.standard_normal(2 * m); dr /= np.linalg.norm(dr)
    v = np.concatenate([np.zeros(m), inst["ys"] + 1e-3 * dr[:m], t_star + 1e-3 * dr[m:]])
    pats = []
    for k in range(K):
        v = true_step(inst, v, m)
        if k >= skip:
            pats.append(int(np.sum((v[2 * m:] > 0) * (2.0 ** np.arange(m)))))
    pats = np.array(pats)
    n = len(pats)
    per = None
    for p in range(1, 3000):
        if n >= 3 * p and np.all(pats[: n - p] == pats[p: n]):
            per = pats[:p]
            break
    if per is None:
        return None
    affs = affine_mats(inst, m)
    n3 = 3 * m
    M = np.eye(n3); c = np.zeros(n3)
    for s in per:
        Ms, cs = affs[s]
        M, c = Ms @ M, Ms @ c + cs
    rho = float(max(abs(np.linalg.eigvals(M))))
    try:
        vfix = np.linalg.solve(np.eye(n3) - M, c)
    except np.linalg.LinAlgError:
        return dict(period=len(per), rho=rho, error="singular")
    cur = vfix.copy()
    consistent = True
    for j in range(len(per)):
        pat = int(np.sum((cur[2 * m:] > 0) * (2.0 ** np.arange(m))))
        if pat != per[j]:
            consistent = False
            break
        cur = true_step(inst, cur, m)
    err = float(np.linalg.norm(cur - vfix))
    dKKT = float(np.linalg.norm(vfix - np.concatenate([inst["xs"], inst["ys"], inst["z"] + inst["lam"]])))
    return dict(period=len(per), rho=rho, consistent=consistent, err=err,
                dist_kkt=dKKT, per=per, vfix=vfix)


t0 = time.time()
certified = []
log = []
for inst_i in range(3):
    mc0, m, dA, dB, mask = meta[inst_i]
    m, mask = int(m), int(mask)
    PA, PB = data[f"PA_{inst_i}"], data[f"PB_{inst_i}"]
    for eps in np.concatenate([np.linspace(0.0015, 0.012, 15)]):
        inst = build(PA, PB, m, mask, float(eps))
        r = process(inst, m)
        if r is None:
            log.append((inst_i, float(eps), None))
            continue
        tag = ""
        if r.get("consistent") and r["err"] < 1e-9 and r["dist_kkt"] > 1e-3:
            cls = "A" if r["rho"] < 1.0 else "B"
            tag = f"  *** CERTIFIED class {cls}"
            certified.append((inst_i, float(eps), r, inst))
            np.savez(os.path.join(OUT, f"exp17c_cycle_i{inst_i}_e{eps:.4f}.npz"),
                     per=r["per"], vfix=r["vfix"], rho=r["rho"],
                     **{k: inst[k] for k in ("A", "B", "F", "G", "b", "c1", "c2", "xs", "ys", "z", "lam")})
        log.append((inst_i, float(eps), r.get("period"), r.get("consistent"), r.get("rho")))
        print(f"inst={inst_i} eps={eps:.4f}: period={r.get('period')} rho={r.get('rho'):.4f} "
              f"consistent={r.get('consistent')} err={r.get('err'):.1e} dKKT={r.get('dist_kkt'):.3f}{tag}",
              flush=True)

with open(os.path.join(OUT, "exp17c_summary.json"), "w") as f:
    json.dump({"seed": 20260729, "log": log, "certified_count": len(certified),
               "elapsed_sec": time.time() - t0}, f, indent=2, default=str)
print(f"\nDONE: certified={len(certified)}, elapsed={time.time()-t0:.0f}s")
