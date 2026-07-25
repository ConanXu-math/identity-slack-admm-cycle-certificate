"""EXP3: Practical convergence behavior of the direct slack-ADMM on
inequality-constrained problems with a KNOWN KKT point (by construction).

Instance: min 0.5 x'Fx + c1'x  + 0.5 y'Gy + c2'y (+ mu*||y||_1 optional)
          s.t. A x + B y <= b.
KKT-by-construction: pick x*, y*, z*>=0, lam*<=0 with <z*,lam*>=0,
b = Ax*+By*+z*, c1 = -F x* - A'lam*, c2 = -G y* - B'lam* - v (v in mu d|.|(y*)).

Tracks: distance to (x*,y*,z*,lam*); the Lyapunov candidate
  V^k = beta*||B(y^k-y*)||^2 + beta*||t^k - t*||^2   (t = z + lam/beta)
and whether V is nonincreasing along every orbit.
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260722)


def make_instance(m, n1, n2, condF=1.0, l1_mu=0.0, rank_def=False, seed=None):
    r = np.random.default_rng(seed)
    A = r.standard_normal((m, n1))
    B = r.standard_normal((m, n2))
    if rank_def and n1 > 1:
        A[:, -1] = A[:, 0] + 1e-10 * r.standard_normal(m)  # near rank-deficient
    x = r.standard_normal(n1); y = r.standard_normal(n2)
    # active set: about half constraints active
    act = r.random(m) < 0.5
    z = np.where(act, 0.0, r.random(m))          # z*>0 on inactive
    lam = np.where(act, -r.random(m), 0.0)       # lam*<0 on active
    b = A @ x + B @ y + z
    UF, _ = np.linalg.qr(r.standard_normal((n1, n1)))
    sF = np.geomspace(1.0, condF, n1)
    F = UF @ np.diag(sF) @ UF.T
    UG, _ = np.linalg.qr(r.standard_normal((n2, n2)))
    G = UG @ np.diag(np.geomspace(1.0, condF, n2)) @ UG.T
    # KKT stationarity for the ALGORITHM's sign convention
    # (L_beta = f+g+delta_+ - <lam,r> + beta/2||r||^2, lam* <= 0):
    #     A'lam* in d theta1(x*),  B'lam* in d theta2(y*)
    c1 = A.T @ lam - F @ x
    v = l1_mu * np.sign(y) + l1_mu * (np.abs(y) < 1e-12) * r.uniform(-1, 1, n2)
    c2 = B.T @ lam - G @ y - v
    return dict(A=A, B=B, b=b, F=F, G=G, c1=c1, c2=c2, l1_mu=l1_mu,
                xs=x, ys=y, zs=z, lams=lam)


def softth(u, a):
    return np.sign(u) * np.maximum(np.abs(u) - a, 0.0)


def run_admm(inst, beta=1.0, K=20000, tol=1e-12, y0=None, t0=None):
    A, B, b, F, G, c1, c2 = inst["A"], inst["B"], inst["b"], inst["F"], inst["G"], inst["c1"], inst["c2"]
    mu = inst["l1_mu"]
    n1, n2 = A.shape[1], B.shape[1]
    Hx = F + beta * A.T @ A
    Hy = G + beta * B.T @ B
    Lx = np.linalg.cholesky(Hx)
    y = np.zeros(n2) if y0 is None else y0.copy()
    t = np.zeros(A.shape[0]) if t0 is None else t0.copy()
    ts = inst["zs"] + inst["lams"] / beta
    Vprev = None
    V_increases = 0
    hist = {"err": [], "V": [], "res": []}
    for k in range(K):
        at = np.abs(t)
        # x-update
        rhs = -c1 - beta * A.T @ (B @ y - b + at)
        x = np.linalg.solve(Lx.T, np.linalg.solve(Lx, rhs))
        # y-update (with optional l1 prox)
        rhsq = -c2 - beta * B.T @ (A @ x - b + at)
        if mu > 0:
            # solve (G + beta B'B) y = rhsq + mu*prox  -> fixed-point (prox-g);
            # G strongly convex: use a few FBS iterations to machine precision
            yg = y.copy()
            L = np.linalg.eigvalsh(Hy)[-1]
            for _ in range(40):
                yg = softth(yg - (Hy @ yg - rhsq) / L, mu / L)
            y = yg
        else:
            y = np.linalg.solve(Hy, rhsq)
        s = A @ x + B @ y - b
        t = np.minimum(t, 0.0) - s
        # errors
        z = np.maximum(t, 0.0); lam = beta * np.minimum(t, 0.0)
        err = max(np.linalg.norm(x - inst["xs"]), np.linalg.norm(y - inst["ys"]),
                  np.linalg.norm(z - inst["zs"]), np.linalg.norm(lam - inst["lams"]))
        V = beta * np.linalg.norm(B @ (y - inst["ys"])) ** 2 + beta * np.linalg.norm(t - ts) ** 2
        if Vprev is not None and V > Vprev * (1 + 1e-12) + 1e-18:
            V_increases += 1
        Vprev = V
        hist["err"].append(err); hist["V"].append(V)
        hist["res"].append(np.linalg.norm(np.maximum(s, 0.0)))
        if err < tol:
            break
    return dict(k=k + 1, err=err, V_increases=V_increases, hist=hist)


results = []
t_start = time.time()
configs = []
for condF in [1.0, 1e2, 1e4]:
    for l1 in [0.0, 0.5]:
        for rank_def in [False, True]:
            configs.append(dict(condF=condF, l1_mu=l1, rank_def=rank_def))

for ci, cfg in enumerate(configs):
    for trial in range(4):
        seed = 1000 + 97 * (ci * 100 + trial)
        m, n1, n2 = 6, 5, 4
        inst = make_instance(m, n1, n2, seed=seed, **cfg)
        for beta in [0.5, 2.0]:
            out = run_admm(inst, beta=beta, K=5000, tol=1e-11)
            results.append(dict(cfg=ci, trial=trial, beta=beta, k=out["k"],
                                err=out["err"], V_inc=out["V_increases"], **cfg))

conv = [r for r in results if r["err"] < 1e-8]
fail = [r for r in results if r["err"] >= 1e-8]
vinc = [r for r in results if r["V_inc"] > 0]
print(f"total runs: {len(results)}  (configs x trials x betas)")
print(f"converged to err<1e-8 within 20000 steps: {len(conv)}; not converged: {len(fail)}")
print(f"runs with any Lyapunov-candidate increase: {len(vinc)}")
ks = [r["k"] for r in conv]
if ks:
    print(f"iterations to converge: median={np.median(ks):.0f}, max={max(ks)}")
if fail:
    for r in fail[:10]:
        print("FAIL:", r)
with open(os.path.join(OUT, "exp3_summary.json"), "w") as f:
    json.dump({"seed": 20260722, "n_runs": len(results), "n_converged": len(conv),
               "n_failed": len(fail), "n_V_increase": len(vinc),
               "median_k": float(np.median(ks)) if ks else None,
               "max_k": max(ks) if ks else None,
               "elapsed_sec": time.time() - t_start}, f, indent=2)
print(f"Done in {time.time()-t_start:.1f}s")
