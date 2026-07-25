"""EXP4: Verify Theorem Q (research/03_theorem_Q.md) by adversarial scanning
over arbitrary symmetric PSD contractions (T_A, T_B) -- equivalent to the
homogeneous convex-quadratic class.

 (i) random scan: sample T_A, T_B with spectra in [0,1] (including 0/1-heavy),
     all sign patterns, assert rho(M) <= 1 + tol;
 (ii) hill-climb: try to maximize rho beyond 1 (stress test);
 (iii) realization check: build A=T^{1/2}, F=beta(I-T), run the actual ADMM
     (quadratic objectives, b=0) from random starts, confirm boundedness.
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260722)
t0 = time.time()

def pattern_matrix_quad(TA, TB, Dp):
    m = TA.shape[0]
    Dm = np.eye(m) - Dp
    # a = -TA(p + J t); p' = -TB(a + J t); t' = Dm t - a - p', J = Dp - Dm
    J = Dp - Dm
    A_p = -TA; A_t = -TA @ J
    B_p = -TB @ A_p; B_t = -TB @ (A_t + J)
    C_p = -A_p - B_p; C_t = Dm - A_t - B_t
    return np.block([[B_p, B_t], [C_p, C_t]])

def rand_psd_contraction(m, zero_frac=0.3, one_frac=0.15):
    U, _ = np.linalg.qr(rng.standard_normal((m, m)))
    s = rng.random(m)
    n0 = int(m * zero_frac); n1 = int(m * one_frac)
    s[:n0] = 0.0; s[n0:n0+n1] = 1.0
    rng.shuffle(s)
    return U @ np.diag(s) @ U.T

max_rho = 0.0; worst = None
N = 3000
print("=== (i) random scan over symmetric PSD contractions ===")
for it in range(N):
    m = int(rng.integers(2, 7))
    TA = rand_psd_contraction(m); TB = rand_psd_contraction(m)
    for mask in range(2 ** m):
        Dp = np.diag(np.array([(mask >> i) & 1 for i in range(m)], dtype=float))
        M = pattern_matrix_quad(TA, TB, Dp)
        rho = float(np.max(np.abs(np.linalg.eigvals(M))))
        if rho > max_rho:
            max_rho = rho; worst = (m, TA.copy(), TB.copy(), Dp.copy())
        assert rho <= 1 + 1e-8, f"THEOREM Q VIOLATED: rho={rho}"
print(f"N={N} instances x all patterns: max rho = {max_rho:.12f}")

print("=== (ii) hill-climb stress (perturb worst, try to push rho>1) ===")
m, TA, TB, Dp = worst
cur = max_rho
for it in range(2000):
    eps = 0.05
    for T in (TA, TB):
        E = rng.standard_normal((m, m)); E = (E + E.T) / 2
        T2 = T + eps * E
        # project back to PSD contraction
        w, V = np.linalg.eigh(T2)
        w = np.clip(w, 0, 1)
        T2 = V @ np.diag(w) @ V.T
        M = pattern_matrix_quad(T2 if T is TA else TA, T2 if T is TB else TB, Dp)
        rho = float(np.max(np.abs(np.linalg.eigvals(M))))
        if rho > cur:
            cur = rho
            if T is TA: TA = T2
            else: TB = T2
print(f"after hill-climb: rho = {cur:.12f} (theorem predicts <= 1)")

print("=== (iii) realization: actual ADMM with quadratic objectives, b=0 ===")
beta = 1.0
bounded_all = True
for trial in range(30):
    m = int(rng.integers(2, 6))
    TA = rand_psd_contraction(m); TB = rand_psd_contraction(m)
    # A = T^{1/2} via eigh
    wA, VA = np.linalg.eigh(TA); A = VA @ np.diag(np.sqrt(np.clip(wA,0,None))) @ VA.T
    wB, VB = np.linalg.eigh(TB); B = VB @ np.diag(np.sqrt(np.clip(wB,0,None))) @ VB.T
    F = beta * (np.eye(m) - TA); G = beta * (np.eye(m) - TB)
    Hx = F + beta * A @ A; Hy = G + beta * B @ B
    y = rng.standard_normal(m); t = rng.standard_normal(m)
    n0 = np.linalg.norm(y) + np.linalg.norm(t)
    for k in range(3000):
        at = np.abs(t)
        x = np.linalg.solve(Hx, -beta * A @ (B @ y + at))
        y = np.linalg.solve(Hy, -beta * B @ (A @ x + at))
        t = np.minimum(t, 0.0) - (A @ x + B @ y)
    n1 = np.linalg.norm(y) + np.linalg.norm(t)
    if n1 > 1e5 * max(n0, 1e-12):
        bounded_all = False
        print(f"GROWTH trial={trial}: {n0:.2e} -> {n1:.2e}")
print("all 30 realization runs bounded:", bounded_all)

with open(os.path.join(OUT, "exp4_summary.json"), "w") as f:
    json.dump({"seed": 20260722, "N_scan": N, "max_rho_scan": max_rho,
               "max_rho_hillclimb": cur, "bounded_realizations": bounded_all,
               "elapsed_sec": time.time() - t0}, f, indent=2)
print(f"Done in {time.time()-t0:.1f}s")
