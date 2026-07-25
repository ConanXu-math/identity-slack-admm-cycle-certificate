"""EXP18 (decisive): search for REALIZABLE PERIODIC POINTS of the piecewise-
affine slack-ADMM map (affine quadratic instances, b != 0).

Key observation: a rigorous counterexample to convergence does NOT need an
attracting cycle. ONE exact periodic orbit of period p>1 suffices: from that
initial point the orbit is periodic, not constant, hence does not converge
(the unique candidate limit, a KKT point, is a period-1 fixed point).

For each constructed instance (strictly convex quadratic, unique KKT point):
  enumerate pattern sequences sigma_0..sigma_{p-1} (p <= p_max);
  compute the affine period map v -> Mv + c (product over the sequence);
  if 1 not in spec(M): solve v = Mv + c; check the realized sign pattern
  along the cycle from v reproduces the sequence exactly; check the cycle
  is not the KKT point; verify ||Phi^p(v) - v|| and one full cycle of the
  TRUE map in float64. Report the cycle's rho(M) (stability indicator).
"""
import numpy as np
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260728)


def pattern_matrix(TA, TB, m, mask):
    Dp = np.diag(np.array([(mask >> i) & 1 for i in range(m)], dtype=float))
    Dm = np.eye(m) - Dp
    J = Dp - Dm
    A_p = -TA; A_t = -TA @ J
    B_p = -TB @ A_p; B_t = -TB @ (A_t + J)
    C_p = -A_p - B_p; C_t = Dm - A_t - B_t
    return np.block([[B_p, B_t], [C_p, C_t]])


def build_instance(TA, TB, m, mask):
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
    return dict(A=A, B=B, F=F, G=G, b=b, c1=c1, c2=c2,
                xs=xs, ys=ys, z=z, lam=lam, Hx=Hx, Hy=Hy)


def true_step(inst, v, m):
    x, y, t = v[:m], v[m:2 * m], v[2 * m:]
    at = np.abs(t)
    x2 = np.linalg.solve(inst["Hx"], -inst["c1"] - inst["A"].T @ (inst["B"] @ y - inst["b"] + at))
    y2 = np.linalg.solve(inst["Hy"], -inst["c2"] - inst["B"].T @ (inst["A"] @ x2 - inst["b"] + at))
    t2 = np.minimum(t, 0.0) - (inst["A"] @ x2 + inst["B"] @ y2 - inst["b"])
    return np.concatenate([x2, y2, t2])


def affine_step_matrices(inst, m):
    """Return (M_sigma, c_sigma) for the full (x,y,t) state, for each mask."""
    A, B, Hx, Hy = inst["A"], inst["B"], inst["Hx"], inst["Hy"]
    b, c1, c2 = inst["b"], inst["c1"], inst["c2"]
    Hxi = np.linalg.inv(Hx); Hyi = np.linalg.inv(Hy)
    out = {}
    n = 3 * m
    for mask in range(2 ** m):
        Dp = np.diag(np.array([(mask >> i) & 1 for i in range(m)], dtype=float))
        Dm = np.eye(m) - Dp
        J = Dp - Dm
        # x' = -Hxi(c1 + A'(By - b + Jt)) =: P1 y + P2 t + q1
        P1 = -Hxi @ A.T @ B; P2 = -Hxi @ A.T @ J; q1 = -Hxi @ (c1 - A.T @ b)
        # y' = -Hyi(c2 + B'(Ax' - b + Jt)) =: R1 x' + R2 t + q2
        R1 = -Hyi @ B.T @ A; R2 = -Hyi @ B.T @ J; q2 = -Hyi @ (c2 - B.T @ b)
        # t' = Dm t - (Ax' + By' - b)
        Z = np.zeros((m, m))
        M = np.block([
            [Z, P1, P2],
            [R1 @ Z, R1 @ P1, R1 @ P2 + R2],
            [-A @ Z - B @ (R1 @ Z), -A @ P1 - B @ (R1 @ P1), -A @ P2 - B @ (R1 @ P2 + R2) + Dm],
        ])
        c = np.concatenate([q1, R1 @ q1 + q2, -A @ q1 - B @ (R1 @ q1 + q2) + b])
        out[mask] = (M, c)
    return out


def search_instance(inst, m, p_max=10):
    affs = affine_step_matrices(inst, m)
    n = 3 * m
    masks = list(range(2 ** m))
    # DFS over sequences
    stack = [(np.eye(n), np.zeros(n), ())]
    while stack:
        M, c, seq = stack.pop()
        if seq:
            ev = np.linalg.eigvals(M)
            if np.min(np.abs(ev - 1.0)) > 1e-9:
                try:
                    v = np.linalg.solve(np.eye(n) - M, c)
                except np.linalg.LinAlgError:
                    v = None
                if v is not None:
                    # check realizability of the full cycle from v
                    cur = v.copy()
                    ok = True
                    for j, s in enumerate(seq):
                        t = cur[2 * m:]
                        pat = int(np.sum((t > 0) * (2.0 ** np.arange(m))))
                        if pat != s:
                            ok = False
                            break
                        cur = affs[s][0] @ cur + affs[s][1]
                    if ok and np.linalg.norm(cur - v) < 1e-8:
                        vstar = np.concatenate([inst["xs"], inst["ys"], inst["z"] + inst["lam"]])
                        if np.linalg.norm(v - vstar) > 1e-6:
                            # final verification with the TRUE map (two full cycles)
                            c1_ = v.copy(); c2_ = None
                            for _ in range(2 * len(seq)):
                                c2_ = true_step(inst, c1_, m); c1_ = c2_
                            err = np.linalg.norm(c1_ - v)
                            if err < 1e-8:
                                rho = float(max(abs(ev)))
                                return dict(seq=seq, v=v, rho=rho, err=err)
        if len(seq) < p_max:
            for s in masks:
                Ms, cs = affs[s]
                stack.append((Ms @ M, Ms @ c + cs, seq + (s,)))
    return None


def strictified_projectors(m, eps, rng):
    dA = int(rng.integers(1, m)); dB = int(rng.integers(1, m))
    UA, _ = np.linalg.qr(rng.standard_normal((m, dA)))
    UB, _ = np.linalg.qr(rng.standard_normal((m, dB)))
    PA = UA @ UA.T; PB = UB @ UB.T
    TA = (1 - eps) * PA + eps * (np.eye(m) - PA)
    TB = (1 - eps) * PB + eps * (np.eye(m) - PB)
    return TA, TB


t0 = time.time()
found = []
tested = 0
for it in range(3000):
    m = int(rng.integers(2, 4))
    eps = float(10 ** rng.uniform(-3, -1))
    TA, TB = strictified_projectors(m, eps, rng)
    # use a RANDOM kkt cone mask for instance construction (any works)
    kkt_mask = int(rng.integers(0, 2 ** m))
    inst = build_instance(TA, TB, m, kkt_mask)
    tested += 1
    hit = search_instance(inst, m, p_max=8 if m == 3 else 10)
    if hit:
        found.append(dict(it=it, m=m, eps=eps, kkt_mask=kkt_mask, **hit))
        np.savez(os.path.join(OUT, f"exp18_periodic_{it}.npz"),
                 seq=np.array(hit["seq"]), v=hit["v"], rho=hit["rho"],
                 **{k: inst[k] for k in ("A", "B", "F", "G", "b", "c1", "c2", "xs", "ys", "z", "lam")})
        print(f"*** PERIODIC ORBIT it={it} m={m} eps={eps:.1e} period={len(hit['seq'])} "
              f"rho={hit['rho']:.6f} err={hit['err']:.2e} seq={hit['seq']}", flush=True)
        if len(found) >= 5:
            break
    if it % 300 == 0:
        print(f"it={it} tested={tested} found={len(found)} elapsed={time.time()-t0:.0f}s", flush=True)

with open(os.path.join(OUT, "exp18_summary.json"), "w") as f:
    json.dump({"seed": 20260728, "tested": tested,
               "found": [{k: (v.tolist() if isinstance(v, np.ndarray) else v)
                          for k, v in r.items()} for r in found],
               "elapsed_sec": time.time() - t0}, f, indent=2, default=str)
print(f"\nDONE: tested={tested}, found={len(found)}, elapsed={time.time()-t0:.0f}s")
