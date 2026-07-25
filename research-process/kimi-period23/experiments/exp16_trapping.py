"""EXP16 (certification attempt): trapping region for a candidate counterexample.

Instance: m=3 projector pair (PA_0, PB_0 from exp14 hits), eps=1e-3 strictified
-> A,B invertible, F=I-T_A, G=I-T_B positive definite -> strictly convex
objectives -> UNIQUE KKT point (constructed via KKT-by-construction).
The KKT cone's pattern matrix has complex |mu| ~= 1.034 > 1 (locally repelling).

If we can certify a compact TRAPPING REGION R (Phi(R) subseteq R) that excludes
the unique fixed point v*, then orbits starting in R never converge:
any convergent orbit's limit is a fixed point of the (continuous) piecewise
map; the only fixed point v* is outside R.

Certification (exact for piecewise-affine maps):
for each sign cone sigma, R ∩ cone_sigma is a box; its vertices map affinely;
conv(image) ⊆ R iff every image vertex ∈ R. We check all 2^(3m) vertices
per cone with margins, in float64, and report the maximum violation.
"""
import numpy as np
import sys, os, json, itertools, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260727)

data = np.load(os.path.join(OUT, "exp14_top_projector_hits.npz"))
meta = data["meta"]
mc0, m, dA, dB, mask = meta[0]
m, mask = int(m), int(mask)
PA, PB = data["PA_0"], data["PB_0"]
eps = 1e-3
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
c1 = A.T @ lam - F @ xs
c2 = B.T @ lam - G @ ys
t_star = z + lam
v_star = np.concatenate([xs, ys, t_star])
Hx = F + A.T @ A; Hy = G + B.T @ B

def admm_step(x, y, t):
    at = np.abs(t)
    x2 = np.linalg.solve(Hx, -c1 - A.T @ (B @ y - b + at))
    y2 = np.linalg.solve(Hy, -c2 - B.T @ (A @ x2 - b + at))
    t2 = np.minimum(t, 0.0) - (A @ x2 + B @ y2 - b)
    return x2, y2, t2

# --- sanity: v* is a fixed point; A,B invertible; F,G posdef; KKT unique
x1, y1, t1 = admm_step(xs.copy(), ys.copy(), t_star.copy())
fp_res = max(np.linalg.norm(x1 - xs), np.linalg.norm(y1 - ys), np.linalg.norm(t1 - t_star))
print(f"fixed-point residual of v*: {fp_res:.2e}")
print(f"det(A)={np.linalg.det(A):.3e}, det(B)={np.linalg.det(B):.3e}, "
      f"eig(F)>0: {np.linalg.eigvalsh(F)[0]:.3e}, eig(G)>0: {np.linalg.eigvalsh(G)[0]:.3e}")

# --- attractor exploration: long orbit from perturbed start
dr = rng.standard_normal(2 * m); dr /= np.linalg.norm(dr)
x, y, t = np.zeros(m), ys + 1e-3 * dr[:m], t_star + 1e-3 * dr[m:]
pts = []
for k in range(120000):
    x, y, t = admm_step(x, y, t)
    if k >= 20000:
        pts.append(np.concatenate([x, y, t]))
pts = np.array(pts)
lo = pts.min(axis=0); hi = pts.max(axis=0)
dkkt = np.linalg.norm(pts - v_star, axis=1)
print(f"attractor: dist-to-KKT in [{dkkt.min():.3f}, {dkkt.max():.3f}]")

def try_box(lo, hi, rel=0.15, abs_m=0.05):
    span = hi - lo
    L = lo - rel * span - abs_m
    H = hi + rel * span + abs_m
    # v* outside?
    if np.all((v_star >= L) & (v_star <= H)):
        return None, "v* inside box"
    # per-cone vertex check
    n = 3 * m
    max_viol = -np.inf
    worst = None
    for msk in range(2 ** m):
        Lc = L.copy(); Hc = H.copy()
        for i in range(m):
            if (msk >> i) & 1:   # t_i >= 0
                Lc[2 * m + i] = max(Lc[2 * m + i], 0.0)
            else:                # t_i <= 0
                Hc[2 * m + i] = min(Hc[2 * m + i], 0.0)
        if np.any(Lc > Hc):
            continue
        for corner in itertools.product(*[[Lc[j], Hc[j]] for j in range(n)]):
            w = np.array(corner)
            xw, yw, tw = w[:m], w[m:2 * m], w[2 * m:]
            x2, y2, t2 = admm_step(xw, yw, tw)
            w2 = np.concatenate([x2, y2, t2])
            viol = np.max(np.maximum(w2 - H, L - w2))
            if viol > max_viol:
                max_viol = viol; worst = (msk, w.copy(), w2.copy())
    return max_viol, worst

t0 = time.time()
for rel, abs_m in [(0.10, 0.02), (0.15, 0.05), (0.25, 0.10), (0.40, 0.20), (0.60, 0.40)]:
    viol, info = try_box(lo, hi, rel, abs_m)
    if viol is None:
        print(f"rel={rel},abs={abs_m}: v* inside box -> skip")
        continue
    status = "TRAPPING CERTIFIED" if viol <= 0 else f"violation={viol:.4e}"
    print(f"rel={rel}, abs={abs_m}: max violation = {viol:.6e}  {status}")
    if viol <= 0:
        json.dump({"m": m, "mask": mask, "eps": eps,
                   "A": A.tolist(), "B": B.tolist(), "F": F.tolist(), "G": G.tolist(),
                   "b": b.tolist(), "c1": c1.tolist(), "c2": c2.tolist(),
                   "xs": xs.tolist(), "ys": ys.tolist(), "z": z.tolist(), "lam": lam.tolist(),
                   "box_L": (lo - rel * (hi - lo) - abs_m).tolist(),
                   "box_H": (hi + rel * (hi - lo) + abs_m).tolist(),
                   "max_violation": float(viol)},
                  open(os.path.join(OUT, "exp16_trapping_certificate.json"), "w"), indent=2)
        print("certificate saved to results/exp16_trapping_certificate.json")
        break
print(f"elapsed {time.time()-t0:.0f}s")
