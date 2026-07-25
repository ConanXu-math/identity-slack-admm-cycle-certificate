"""EXP11: Common quadratic Lyapunov function (CQLF) feasibility for pattern
families of the TRUE matrices, via SDP (cvxpy + CLARABEL).

For each family {M_sigma}: solve
  find H s.t.  H ⪰ I,  M_sigma^T H M_sigma ⪯ H  for all sigma.
(Non-strict: eigenvalue 1 is present.) If feasible for all tested families ->
quadratic Lyapunov route is alive; if infeasible for some -> CQLF is dead and
we record it. m=2 (4 patterns), m=3 (8 patterns); projector & PSD classes.
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
import cvxpy as cp

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260724)


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


def rand_T(m, kind):
    U, _ = np.linalg.qr(rng.standard_normal((m, m)))
    if kind == "proj":
        s = (rng.random(m) < 0.5).astype(float)
    elif kind == "near1":
        s = 1 - 10.0 ** (-rng.uniform(0, 3, m))
    else:
        s = rng.random(m)
    return U @ np.diag(s) @ U.T


def cqlf_check(mats, d):
    H = cp.Variable((d, d), symmetric=True)
    cons = [H >> np.eye(d)]
    for M in mats:
        cons.append(H - M.T @ H @ M >> 0)
    prob = cp.Problem(cp.Minimize(0), cons)
    try:
        prob.solve(solver="CLARABEL")
    except Exception as e:
        return "solver_error", None
    if prob.status in ("optimal", "optimal_inaccurate"):
        return "feasible", H.value
    return "infeasible", None


results = []
t0 = time.time()
for trial in range(60):
    m = int(rng.integers(2, 4))
    kind = ["proj", "near1", "unif"][trial % 3]
    TA, TB = rand_T(m, kind), rand_T(m, kind)
    mats = pattern_mats(TA, TB, m)
    d = mats[0].shape[0]
    status, Hv = cqlf_check(mats, d)
    maxnorm = max(np.linalg.norm(M, 2) for M in mats)
    results.append(dict(trial=trial, m=m, kind=kind, status=status, maxnorm=float(maxnorm)))
    print(f"trial {trial}: m={m} {kind}: {status} (max||M||={maxnorm:.3f})", flush=True)

feas = sum(1 for r in results if r["status"] == "feasible")
infeas = sum(1 for r in results if r["status"] == "infeasible")
print(f"\nfeasible: {feas}/60, infeasible: {infeas}/60")
with open(os.path.join(OUT, "exp11_summary.json"), "w") as f:
    json.dump({"seed": 20260724, "results": results, "feasible": feas,
               "infeasible": infeas, "elapsed_sec": time.time() - t0}, f, indent=2)
print(f"Done in {time.time()-t0:.0f}s")
