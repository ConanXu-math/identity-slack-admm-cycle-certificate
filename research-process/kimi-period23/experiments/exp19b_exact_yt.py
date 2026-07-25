"""EXP19b: EXACT rational certification of the period-23 attracting cycle,
using the (y,t)-form (6x6) throughout. Exact arithmetic (fractions.Fraction
over the float64 instance data = exact binary rationals).

Certificate chain:
 (1) instance validity: F, G positive definite (Sylvester, exact leading
     principal minors); det A, det B nonzero (Bareiss);
 (2) exact unique fixed point w* of the piecewise map in the KKT cone,
     in-cone, within 1e-12 of the constructed KKT point;
 (3) exact product map (M,c) of the 23-pattern sequence; vhat solves
     (I-M)v=c exactly; the TRUE (y,t) map from vhat follows the recorded
     sign pattern for 23 steps and returns to vhat exactly;
 (4) vhat != wstar;
 (5) Jury stability criterion on the exact characteristic polynomial of M
     (Faddeev-LeVerrier, exact) -> all eigenvalues inside the open unit disk
     -> the cycle is locally attracting.
"""
import numpy as np
from fractions import Fraction as Fr
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
t00 = time.time()

d = np.load(os.path.join(OUT, "exp17c_cycle_i0_e0.0038.npz"), allow_pickle=False)
per = [int(x) for x in d["per"]]
m = 3
A, B, F, G, b, c1, c2, xs, ys, z, lam = (d[k] for k in
    ("A", "B", "F", "G", "b", "c1", "c2", "xs", "ys", "z", "lam"))


def to_fr(M):
    return [[Fr(float(x)) for x in row] for row in np.asarray(M)]


def matmul(X, Y):
    return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))]
            for i in range(len(X))]


def matvec(X, v):
    return [sum(X[i][k] * v[k] for k in range(len(v))) for i in range(len(X))]


def solve_exact(Mmat, rhs):
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
                Aug[r] = [a - f * bb for a, bb in zip(Aug[r], Aug[col])]
    return [Aug[i][n] for i in range(n)]


def det_exact(Mmat):
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


def eye(n):
    return [[Fr(1) if i == j else Fr(0) for j in range(n)] for i in range(n)]


def T(X):
    return [list(r) for r in zip(*X)]


A_, B_, F_, G_ = to_fr(A), to_fr(B), to_fr(F), to_fr(G)
b_ = [Fr(float(x)) for x in b]
c1_ = [Fr(float(x)) for x in c1]
c2_ = [Fr(float(x)) for x in c2]
ys_ = [Fr(float(x)) for x in ys]
t_star_ = [Fr(float(x)) for x in (z + lam)]
vstar_yt = ys_ + t_star_

# ---------------- (1) instance validity ----------------
print("(1) instance validity (exact):")


def leading_minors(Mmat):
    return [det_exact([row[:k] for row in Mmat[:k]]) for k in range(1, len(Mmat) + 1)]


lmF = leading_minors(F_); lmG = leading_minors(G_)
symF = F_ == T(F_); symG = G_ == T(G_)
print(f"  F symmetric exactly: {symF};  G symmetric exactly: {symG}")
print(f"  F leading minors > 0: {all(x > 0 for x in lmF)}")
print(f"  G leading minors > 0: {all(x > 0 for x in lmG)}")
detA = det_exact(A_); detB = det_exact(B_)
print(f"  det A != 0: {detA != 0};  det B != 0: {detB != 0}")

Hx_ = [[F_[i][j] + sum(A_[k][i] * A_[k][j] for k in range(m)) for j in range(m)] for i in range(m)]
Hy_ = [[G_[i][j] + sum(B_[k][i] * B_[k][j] for k in range(m)) for j in range(m)] for i in range(m)]
Hxi = T([solve_exact(Hx_, e) for e in eye(m)])
Hyi = T([solve_exact(Hy_, e) for e in eye(m)])

# ---------------- (y,t) pattern maps ----------------
def yt_mats(mk):
    Dp = [[Fr(1 if ((mk >> i) & 1) else 0) if i == j else Fr(0) for j in range(m)] for i in range(m)]
    Dm = [[Fr(1) - Dp[i][i] if i == j else Fr(0) for j in range(m)] for i in range(m)]
    J = [[Dp[i][i] - Dm[i][i] if i == j else Fr(0) for j in range(m)] for i in range(m)]
    X_y = matmul(Hxi, [[-x for x in row] for row in matmul(T(A_), B_)])
    X_t = matmul(Hxi, [[-x for x in row] for row in matmul(T(A_), J)])
    x0 = matvec(Hxi, [-(c1_[i]) + sum(A_[k][i] * b_[k] for k in range(m)) for i in range(m)])
    Y_x = matmul(Hyi, [[-x for x in row] for row in matmul(T(B_), A_)])
    Y_t = matmul(Hyi, [[-x for x in row] for row in matmul(T(B_), J)])
    y0 = matvec(Hyi, [-(c2_[i]) + sum(B_[k][i] * b_[k] for k in range(m)) for i in range(m)])
    Myy = matmul(Y_x, X_y)
    Myt = [[sum(Y_x[i][k] * X_t[k][j] for k in range(m)) + Y_t[i][j] for j in range(m)] for i in range(m)]
    cy = [sum(Y_x[i][k] * x0[k] for k in range(m)) + y0[i] for i in range(m)]
    Mty = [[-sum(A_[i][k] * X_y[k][j] for k in range(m)) - sum(B_[i][k] * Myy[k][j] for k in range(m))
            for j in range(m)] for i in range(m)]
    Mtt = [[Dm[i][j] - sum(A_[i][k] * X_t[k][j] for k in range(m)) - sum(B_[i][k] * Myt[k][j] for k in range(m))
            for j in range(m)] for i in range(m)]
    ct = [b_[i] - sum(A_[i][k] * x0[k] for k in range(m)) - sum(B_[i][k] * cy[k] for k in range(m))
          for i in range(m)]
    M = [Myy[i] + Myt[i] for i in range(m)] + [Mty[i] + Mtt[i] for i in range(m)]
    c = cy + ct
    return M, c


def true_step_yt(v, mk):
    M, c = yt_mats(mk)
    return [sum(M[i][k] * v[k] for k in range(2 * m)) + c[i] for i in range(2 * m)]


def mask_of(v):
    return sum((1 << i) for i in range(m) if v[m + i] > 0)


n = 2 * m

# ---------------- (2) exact unique fixed point ----------------
KKT_MASK = 4
Ms_kkt, cs_kkt = yt_mats(KKT_MASK)
ImMs = [[(Fr(1) if i == j else Fr(0)) - Ms_kkt[i][j] for j in range(n)] for i in range(n)]
wstar = solve_exact(ImMs, cs_kkt)
dist_w = max(abs(wstar[i] - vstar_yt[i]) for i in range(n))
in_cone = (mask_of(wstar) == KKT_MASK)
print(f"(2) exact fixed point w*: dist(w*, v*) = {float(dist_w):.2e} (<1e-12: {dist_w < Fr(1, 10**12)}), "
      f"in KKT cone: {in_cone}")

# ---------------- (3) exact cycle ----------------
Mprod = eye(n); cprod = [Fr(0)] * n
for mk in per:
    Ms, cs = yt_mats(mk)
    cprod = [sum(Ms[i][k] * cprod[k] for k in range(n)) + cs[i] for i in range(n)]
    Mprod = matmul(Ms, Mprod)
print(f"(3) product map built exactly (6x6, period {len(per)})")
ImM = [[(Fr(1) if i == j else Fr(0)) - Mprod[i][j] for j in range(n)] for i in range(n)]
vhat = solve_exact(ImM, cprod)
v = vhat[:]
ok = True
cycle_states = []
for j in range(len(per)):
    cycle_states.append(v[:])
    if mask_of(v) != per[j]:
        ok = False
        print(f"  pattern mismatch at {j}: {mask_of(v)} != {per[j]}")
        break
    v = true_step_yt(v, per[j])
strict_margin = min(abs(state[m + i]) for state in cycle_states for i in range(m))
strict_margin_gt_7_over_1000 = (
    len(cycle_states) == len(per) and strict_margin > Fr(7, 1000)
)
states_distinct = (
    len(cycle_states) == len(per)
    and len({tuple(state) for state in cycle_states}) == len(per)
)
cycle_closed = v == vhat
cycle_not_fixed = true_step_yt(vhat, mask_of(vhat)) != vhat
minimal_period_23 = len(per) == 23 and cycle_closed and cycle_not_fixed
print(f"  sign patterns along cycle match exactly: {ok}")
print(f"  strict cell margin > 7/1000 exactly: {strict_margin_gt_7_over_1000} "
      f"(decimal margin {float(strict_margin):.12g})")
print(f"  all {len(per)} cycle states distinct exactly: {states_distinct}")
print(f"  Phi^23(vhat) == vhat exactly: {cycle_closed}")
print(f"  minimal period is 23 (23 prime, cycle not fixed): {minimal_period_23}")

print(f"(4) cycle != KKT (exact): {vhat != wstar}")

# ---------------- (5) Jury on exact char poly ----------------
print("(5) local attraction (exact char poly via Faddeev-LeVerrier + Jury):")
Mp = Mprod
Bmat = eye(n)
coeffs = []
for k in range(1, n + 1):
    MB = matmul(Mp, Bmat)
    tr = sum(MB[i][i] for i in range(n))
    ak = -tr / k
    coeffs.append(ak)
    Bmat = [[MB[i][j] + (ak if i == j else Fr(0)) for j in range(n)] for i in range(n)]
# char poly: l^n + c1 l^{n-1} + ... + cn
p1 = sum([Fr(1)] + coeffs)
pm1 = sum((([Fr(1)] + coeffs)[i]) * ((-1) ** (n - i)) for i in range(n + 1))
jury_pre = (p1 > 0) and (((-1) ** n) * pm1 > 0) and (abs(coeffs[-1]) < 1)
tab = [[Fr(1)] + coeffs]
stable = jury_pre
if stable:
    while len(tab[-1]) > 2:
        r = tab[-1]
        k = len(r) - 1
        nxt = [r[0] * r[i] - r[k] * r[k - i] for i in range(k)]
        tab.append(nxt)
        if tab[-1][-1] != 0 or tab[-1][0] != 0:
            if not (abs(tab[-1][0]) > abs(tab[-1][-1])):
                stable = False
                break
print(f"  Jury necessary conditions: {jury_pre}; full criterion: {stable}")

cert = {
    "F_symmetric": bool(symF),
    "G_symmetric": bool(symG),
    "F_posdef": bool(symF and all(x > 0 for x in lmF)),
    "G_posdef": bool(symG and all(x > 0 for x in lmG)),
    "detA_nonzero": bool(detA != 0),
    "detB_nonzero": bool(detB != 0),
    "exact_fixed_point_dist": float(dist_w),
    "exact_fixed_point_in_cone": bool(in_cone),
    "cycle_patterns_exact": bool(ok),
    "strict_cell_margin": float(strict_margin),
    "strict_cell_margin_gt_7_over_1000": bool(strict_margin_gt_7_over_1000),
    "cycle_states_distinct": bool(states_distinct),
    "cycle_closed_exact": bool(cycle_closed),
    "cycle_not_fixed": bool(cycle_not_fixed),
    "minimal_period_23": bool(minimal_period_23),
    "cycle_neq_kkt": bool(vhat != wstar),
    "jury_stable": bool(stable),
    "period": len(per),
    "elapsed_sec": time.time() - t00,
}
required_checks = (
    cert["F_posdef"],
    cert["G_posdef"],
    cert["detA_nonzero"],
    cert["detB_nonzero"],
    dist_w < Fr(1, 10**12),
    cert["exact_fixed_point_in_cone"],
    cert["cycle_patterns_exact"],
    cert["strict_cell_margin_gt_7_over_1000"],
    cert["cycle_states_distinct"],
    cert["cycle_closed_exact"],
    cert["minimal_period_23"],
    cert["cycle_neq_kkt"],
    cert["jury_stable"],
)
cert["valid"] = bool(all(required_checks))
with open(os.path.join(OUT, "exp19_certificate.json"), "w") as f:
    json.dump(cert, f, indent=2)
print("\nCERTIFICATE:", json.dumps(cert, indent=2))
if not cert["valid"]:
    raise AssertionError("period-23 certificate validation failed")
