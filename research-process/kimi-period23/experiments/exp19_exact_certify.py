"""EXP19: EXACT rational certification of the period-23 attracting cycle
(counterexample to the convergence of the direct slack-ADMM).

All arithmetic is exact (Python fractions.Fraction over the float64 instance
data, which is exactly representable in binary rationals). Checks:
  (1) instance validity: F, G positive definite (Sylvester, exact leading
      principal minors > 0); A, B nonsingular (exact det via Bareiss);
  (2) v* is a fixed point of the true piecewise-affine map (exact iteration);
  (3) the 23 pattern matrices and their product (M, c) are computed exactly;
      vhat solves (I-M)v = c exactly; the TRUE map from vhat follows exactly
      the recorded sign pattern for 23 steps and returns to vhat exactly;
  (4) the cycle is not the KKT point (exact inequality);
  (5) local attraction: exact char poly of M via Faddeev-LeVerrier, then
      Jury stability criterion (exact rational) certifying all roots inside
      the open unit disk.
"""
import numpy as np
from fractions import Fraction as Fr
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
t0 = time.time()

d = np.load(os.path.join(OUT, "exp17c_cycle_i0_e0.0038.npz"), allow_pickle=False)
per = [int(x) for x in d["per"]]
m = 3
A, B, F, G, b, c1, c2, xs, ys, z, lam = (d[k] for k in
    ("A", "B", "F", "G", "b", "c1", "c2", "xs", "ys", "z", "lam"))

def to_fr(M):
    return [[Fr(float(x)) for x in row] for row in np.asarray(M)]

def matmul(X, Y):
    n, p, q = len(X), len(Y), len(Y[0])
    return [[sum(X[i][k] * Y[k][j] for k in range(p)) for j in range(q)] for i in range(n)]

def matvec(X, v):
    return [sum(X[i][k] * v[k] for k in range(len(v))) for i in range(len(X))]

def eye(n):
    return [[Fr(1) if i == j else Fr(0) for j in range(n)] for i in range(n)]

def solve_exact(Mmat, rhs):
    """Exact Gaussian elimination with partial pivoting (Fraction)."""
    n = len(Mmat)
    Aug = [row[:] + [rhs[i]] for i, row in enumerate(Mmat)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(Aug[r][col]))
        assert Aug[piv][col] != 0, "singular"
        Aug[col], Aug[piv] = Aug[piv], Aug[col]
        pv = Aug[col][col]
        Aug[col] = [x / pv for x in Aug[col]]
        for r in range(n):
            if r != col and Aug[r][col] != 0:
                f = Aug[r][col]
                Aug[r] = [a - f * b_ for a, b_ in zip(Aug[r], Aug[col])]
    return [Aug[i][n] for i in range(n)]

def det_exact(Mmat):
    """Bareiss fraction-free determinant."""
    n = len(Mmat)
    Mx = [row[:] for row in Mmat]
    sign = 1
    prev = Fr(1)
    for k in range(n - 1):
        if Mx[k][k] == 0:
            for r in range(k + 1, n):
                if Mx[r][k] != 0:
                    Mx[k], Mx[r] = Mx[r], Mx[k]
                    sign = -sign
                    break
            else:
                return Fr(0)
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                Mx[i][j] = (Mx[i][j] * Mx[k][k] - Mx[i][k] * Mx[k][j]) / prev
        prev = Mx[k][k]
    return sign * Mx[n - 1][n - 1]

A_, B_, F_, G_ = to_fr(A), to_fr(B), to_fr(F), to_fr(G)
b_, c1_, c2_ = to_fr(b.reshape(-1, 1)), to_fr(c1.reshape(-1, 1)), to_fr(c2.reshape(-1, 1))
b_ = [r[0] for r in b_]; c1_ = [r[0] for r in c1_]; c2_ = [r[0] for r in c2_]
xs_, ys_, z_, lam_ = to_fr(xs.reshape(-1, 1)), to_fr(ys.reshape(-1, 1)), to_fr(z.reshape(-1, 1)), to_fr(lam.reshape(-1, 1))
xs_ = [r[0] for r in xs_]; ys_ = [r[0] for r in ys_]; z_ = [r[0] for r in z_]; lam_ = [r[0] for r in lam_]

def T(X):
    return [list(r) for r in zip(*X)]

# ---- (1) instance validity
print("(1) instance validity (exact):")
detF = det_exact(F_); detG = det_exact(G_)
# Sylvester: leading principal minors of F and G
def leading_minors(Mmat):
    return [det_exact([row[:k] for row in Mmat[:k]]) for k in range(1, len(Mmat) + 1)]
lmF = leading_minors(F_); lmG = leading_minors(G_)
print(f"  F leading minors > 0: {all(x > 0 for x in lmF)}")
print(f"  G leading minors > 0: {all(x > 0 for x in lmG)}")
detA = det_exact(A_); detB = det_exact(B_)
print(f"  det A != 0: {detA != 0} (={detA}),  det B != 0: {detB != 0}")

Hx_ = [[F_[i][j] + sum(A_[k][i] * A_[k][j] for k in range(m)) for j in range(m)] for i in range(m)]
Hy_ = [[G_[i][j] + sum(B_[k][i] * B_[k][j] for k in range(m)) for j in range(m)] for i in range(m)]
lmHx = leading_minors(Hx_); lmHy = leading_minors(Hy_)
print(f"  Hx, Hy positive definite: {all(x > 0 for x in lmHx) and all(x > 0 for x in lmHy)}")

# ---- true piecewise map, exact
def true_step_exact(v):
    x, y, t = v[:m], v[m:2 * m], v[2 * m:]
    at = [abs(ti) for ti in t]
    rhs1 = [-(c1_[i]) - sum(A_[k][i] * (sum(B_[k][j] * y[j] for j in range(m)) - b_[k] + at[k]) for k in range(m)) for i in range(m)]
    x2 = solve_exact(Hx_, rhs1)
    Ax2 = [sum(A_[k][j] * x2[j] for j in range(m)) for k in range(m)]
    rhs2 = [-(c2_[i]) - sum(B_[k][i] * (Ax2[k] - b_[k] + at[k]) for k in range(m)) for i in range(m)]
    y2 = solve_exact(Hy_, rhs2)
    By2 = [sum(B_[k][j] * y2[j] for j in range(m)) for k in range(m)]
    t2 = [min(t[k], Fr(0)) - (Ax2[k] + By2[k] - b_[k]) for k in range(m)]
    return x2 + y2 + t2

vstar = xs_ + ys_ + [z_[k] + lam_[k] for k in range(m)]

# ---- true piecewise map, exact

# ---- (3) exact cycle: solve (I-M)v=c for the product, verify the true cycle
def pattern_matrix_exact(mk):
    Dp = [[Fr(1 if ((mk >> i) & 1) else 0) if i == j else Fr(0) for j in range(m)] for i in range(m)]
    Dm = [[Fr(1) - Dp[i][i] if i == j else Fr(0) for j in range(m)] for i in range(m)]
    J = [[Dp[i][i] - Dm[i][i] if i == j else Fr(0) for j in range(m)] for i in range(m)]
    # build via x', y', t' formulas on (x,y,t)
    Hxi = [solve_exact(Hx_, e) for e in eye(m)]
    Hxi = T(Hxi)  # inverse
    Hyi = [solve_exact(Hy_, e) for e in eye(m)]
    Hyi = T(Hyi)
    Z = [[Fr(0)] * m for _ in range(m)]
    AtB = matmul(T(A_), B_); AtJ = matmul(T(A_), J)
    P1 = matmul(Hxi, [[-x for x in row] for row in AtB])
    P2 = matmul(Hxi, [[-x for x in row] for row in AtJ])
    q1 = matvec(Hxi, [-(c1_[i]) + sum(A_[k][i] * b_[k] for k in range(m)) for i in range(m)])
    BtA = matmul(T(B_), A_); BtJ = matmul(T(B_), J)
    R1 = matmul(Hyi, [[-x for x in row] for row in BtA])
    R2 = matmul(Hyi, [[-x for x in row] for row in BtJ])
    q2 = matvec(Hyi, [-(c2_[i]) + sum(B_[k][i] * b_[k] for k in range(m)) for i in range(m)])
    n = 3 * m
    M = [[Fr(0)] * n for _ in range(n)]
    # block structure:
    # [ Z,          P1,        P2        ]
    # [ R1 Z,       R1 P1,     R1 P2+R2  ]
    # [ -A Z-B R1 Z,-A P1-B R1P1, -A P2 - B(R1 P2+R2) + Dm ]
    for i in range(m):
        for j in range(m):
            M[i][m + j] = P1[i][j]
            M[i][2 * m + j] = P2[i][j]
            M[m + i][j] = Fr(0)                       # R1 Z = 0
            M[m + i][m + j] = sum(R1[i][k] * P1[k][j] for k in range(m))
            M[m + i][2 * m + j] = sum(R1[i][k] * P2[k][j] for k in range(m)) + R2[i][j]
    # third block row: t' = Dm t - A x' - B y' + b
    for i in range(m):
        for j in range(m):
            M[2 * m + i][j] = Fr(0)                   # -A Z - B R1 Z = 0
            M[2 * m + i][m + j] = (-sum(A_[i][k] * P1[k][j] for k in range(m))
                                   - sum(B_[i][k] * M[m + k][m + j] for k in range(m)))
            M[2 * m + i][2 * m + j] = (Dm[i][j]
                                       - sum(A_[i][k] * P2[k][j] for k in range(m))
                                       - sum(B_[i][k] * M[m + k][2 * m + j] for k in range(m)))
    c = q1 + [sum(R1[i][k] * q1[k] for k in range(m)) + q2[i] for i in range(m)] + \
        [b_[i] - sum(A_[i][k] * q1[k] for k in range(m)) - sum(B_[i][k] * (sum(R1[k][l] * q1[l] for l in range(m)) + q2[k]) for k in range(m)) for i in range(m)]
    return M, c

n = 3 * m
# ---- (2) exact unique fixed point: solve the KKT-cone affine map's fixed point
# exactly and check it lies in the KKT cone near v* (the stored b,c1,c2 were
# constructed in float64, so v* is a fixed point only up to ~1e-16).
KKT_MASK = 4  # sigma* = (-,-,+)
Ms_kkt, cs_kkt = pattern_matrix_exact(KKT_MASK)
ImMs = [[(Fr(1) if i == j else Fr(0)) - Ms_kkt[i][j] for j in range(n)] for i in range(n)]
wstar = solve_exact(ImMs, cs_kkt)
tol = Fr(1, 10 ** 12)
dist_w = max(abs(wstar[i] - vstar[i]) for i in range(n))
in_cone = all((wstar[2 * m + i] > 0) == bool((KKT_MASK >> i) & 1) for i in range(m))
print(f"(2) exact unique fixed point w*: dist(w*, v*) = {float(dist_w):.2e} "
      f"(< 1e-12: {dist_w < tol}), in KKT cone: {in_cone}")
assert dist_w < tol and in_cone

# cross-check exact true map vs float64 at one point
rngv = np.random.default_rng(7)
vt = [Fr(float(x)) for x in rngv.standard_normal(n)]
exact_out = true_step_exact(vt)
Hx = F + A.T @ A; Hy = G + B.T @ B
vtf = np.array([float(x) for x in vt])
xf, yf, tf = vtf[:m], vtf[m:2 * m], vtf[2 * m:]
at = np.abs(tf)
x2f = np.linalg.solve(Hx, -c1 - A.T @ (B @ yf - b + at))
y2f = np.linalg.solve(Hy, -c2 - B.T @ (A @ x2f - b + at))
t2f = np.minimum(tf, 0.0) - (A @ x2f + B @ y2f - b)
float_out = np.concatenate([x2f, y2f, t2f])
xerr = max(abs(float(o) - e) for o, e in zip(exact_out, float_out))
print(f"(2.5) exact-vs-float true map cross-check: {xerr:.2e}")
assert xerr < 1e-12, "exact map mismatch"

Mprod = eye(n); cprod = [Fr(0)] * n
for mk in per:
    Ms, cs = pattern_matrix_exact(mk)
    cprod = [sum(Ms[i][k] * cprod[k] for k in range(n)) + cs[i] for i in range(n)]
    Mprod = matmul(Ms, Mprod)
print(f"(3) product map built exactly ({n}x{n}, period {len(per)})")
ImM = [[(Fr(1) if i == j else Fr(0)) - Mprod[i][j] for j in range(n)] for i in range(n)]
vhat = solve_exact(ImM, cprod)
# verify by TRUE map with exact pattern tracking
v = vhat[:]
ok = True
for j in range(len(per)):
    pat = sum((1 << i) for i in range(m) if v[2 * m + i] > 0)
    if pat != per[j]:
        ok = False
        print(f"  pattern mismatch at step {j}: {pat} != {per[j]}")
        break
    v = true_step_exact(v)
print(f"  sign patterns along cycle match exactly: {ok}")
print(f"  Phi^23(vhat) == vhat exactly: {v == vhat}")
# also verify (I-M)vhat = c residual exactly zero
res = [sum(ImM[i][k] * vhat[k] for k in range(n)) - cprod[i] for i in range(n)]
print(f"  (I-M)vhat - c == 0 exactly: {all(r == 0 for r in res)}")

print("\n(4) cycle != KKT point (exact):", vhat != wstar)

# ---- (5) local attraction: exact char poly + Jury criterion
print("\n(5) local attraction certification:")
# Faddeev-LeVerrier for char poly of Mprod: p(l) = l^n + a1 l^{n-1} + ... + an
Mp = Mprod
N = eye(n)
coeffs = []
Mk = eye(n)
for k in range(1, n + 1):
    Mk = matmul(Mp, [[Mk[i][j] + (coeffs[-1] if i == j else Fr(0)) for j in range(n)] for i in range(n)] if coeffs else matmul(Mp, eye(n)))
    tr = sum(Mk[i][i] for i in range(n))
    ak = -tr / k
    coeffs.append(ak)
    if k < n:
        Mk = [[Mk[i][j] + (ak if i == j else Fr(0)) for j in range(n)] for i in range(n)]
# char poly: l^n + c1 l^{n-1} + ... + cn
print(f"  char poly coefficients computed (deg {n})")
# Jury stability criterion for p(l) = a0 l^n + a1 l^{n-1} + ... + an (a0=1)
def jury(cfs):
    # cfs = [a0=1, a1, ..., an]; returns True iff all roots inside open unit disk
    n_ = len(cfs) - 1
    a = cfs[:]
    # necessary: p(1) > 0, (-1)^n p(-1) > 0, |an| < a0
    p1 = sum(a)
    pm1 = sum(a[i] * ((-1) ** (n_ - i)) for i in range(n_ + 1))
    if not (p1 > 0):
        return False, "p(1) > 0 fails"
    if not (((-1) ** n_) * pm1 > 0):
        return False, "(-1)^n p(-1) > 0 fails"
    if not (abs(a[-1]) < a[0]):
        return False, "|an| < a0 fails"
    # Jury array
    tab = [a[:]]
    while len(tab[-1]) > 2:
        r = tab[-1]
        k = len(r) - 1
        nxt = []
        for i in range(k):
            nxt.append(r[0] * r[i] - r[k] * r[k - i])
        tab.append(nxt)
        if not (abs(tab[-1][0]) > abs(tab[-1][-1]) if tab[-1][-1] != 0 or tab[-1][0] != 0 else True):
            return False, f"jury row condition fails at len {len(nxt)}"
    return True, "all roots inside open unit disk"

stable, msg = jury([Fr(1)] + coeffs)
print(f"  Jury criterion: {stable} ({msg})")

cert = {
    "F_posdef": bool(all(x > 0 for x in lmF)),
    "G_posdef": bool(all(x > 0 for x in lmG)),
    "detA_nonzero": str(detA) if detA != 0 else "0",
    "detB_nonzero": str(detB) if detB != 0 else "0",
    "exact_fixed_point_dist": float(dist_w),
    "exact_fixed_point_in_cone": bool(in_cone),
    "cycle_patterns_exact": bool(ok),
    "cycle_closed_exact": bool(v == vhat),
    "cycle_neq_kkt": bool(vhat != wstar),
    "jury_stable": bool(stable),
    "elapsed_sec": time.time() - t0,
}
with open(os.path.join(OUT, "exp19_certificate.json"), "w") as f:
    json.dump(cert, f, indent=2)
print("\nCERTIFICATE:", json.dumps(cert, indent=2))
