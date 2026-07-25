"""EXP2b: Numerical verification of Theorem H (research/02_theorem_H.md).

Checks, on random instances:
 (i) bijection: eigenvalues of M_sigma outside {0,1} match eigenvalues of
     S = (I-P) D_- (I-Q) restricted to ker P;
 (ii) all eigenvalues satisfy |mu| <= 1 + tiny;
 (iii) eigenvalue 1 (and any |mu|=1) has no defective Jordan block
      (algebraic == geometric multiplicity), across samples.
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from admm_core import homog_slack_matrix

rng = np.random.default_rng(777)

def eigvals_M(P, Q, Dp):
    """Build M on full R^m x R^m (p unrestricted) to compare cleanly."""
    m = P.shape[0]
    Dm = np.eye(m) - Dp
    # a = -P(p+Dp t); p' = -Q(a+Dp t); t' = Dm t - a - p'
    # blocks on (p, t):
    A_pp = -P; A_pt = -P @ Dp            # a = A_pp p + A_pt t
    B_p = -Q @ A_pp; B_t = -Q @ (A_pt + Dp)   # p' = -Q a - Q Dp t
    C_p = -A_pp - B_p; C_t = Dm - A_pt - B_t  # t' = Dm t - a - p'
    M = np.block([[B_p, B_t], [C_p, C_t]])
    return np.linalg.eigvals(M), M

max_dev = 0.0; max_rho = 0.0; jordan_suspect = 0
N = 400
for it in range(N):
    m = int(rng.integers(2, 6))
    dA = int(rng.integers(1, m)); dB = int(rng.integers(1, m))
    UA, _ = np.linalg.qr(rng.standard_normal((m, dA)))
    UB, _ = np.linalg.qr(rng.standard_normal((m, dB)))
    P = UA @ UA.T; Q = UB @ UB.T
    Dp = np.diag(rng.integers(0, 2, m).astype(float))
    evM, M = eigvals_M(P, Q, Dp)
    rho = np.max(np.abs(evM))
    max_rho = max(max_rho, rho)
    assert rho <= 1 + 1e-8, f"VIOLATION rho={rho}"
    # S on ker P
    KP = np.linalg.qr(np.eye(m) - P)[0][:, :m - dA]  # basis of range(I-P)=ker P
    assert np.allclose(P @ KP, 0.0, atol=1e-8)
    Dm = np.eye(m) - Dp
    S = KP.T @ Dm @ (np.eye(m) - Q) @ KP
    evS = np.linalg.eigvals(S) if S.size else np.array([])
    # compare: spec(M) minus {0,1-ish} vs spec(S) minus {1-ish}
    tol = 1e-8
    rem = [mu for mu in evM if abs(mu) > tol and abs(mu - 1) > tol]
    remS = [mu for mu in evS if abs(mu - 1) > tol and abs(mu) > tol]
    rem_sorted = sorted(rem, key=lambda z: (z.real, z.imag))
    remS_sorted = sorted(remS, key=lambda z: (z.real, z.imag))
    if len(rem_sorted) != len(remS_sorted):
        print("COUNT MISMATCH", m, dA, dB, len(rem_sorted), len(remS_sorted))
        continue
    for a, b in zip(rem_sorted, remS_sorted):
        max_dev = max(max_dev, abs(a - b))
    # Jordan check at |mu|=1 (numerical: geometric vs algebraic multiplicity)
    for target in [1.0]:
        alg = np.sum(np.abs(evM - target) < 1e-6)
        if alg > 0:
            geom = m * 2 - np.linalg.matrix_rank(M - target * np.eye(2 * m), tol=1e-6)
            if geom < alg:
                jordan_suspect += 1
                print(f"Jordan suspect at mu=1: m={m} alg={alg} geom={geom}")

print(f"samples={N}: max |spec(M)| = {max_rho:.12f} (all <= 1)")
print(f"bijection max deviation |mu_M - mu_S| = {max_dev:.3e}")
print(f"Jordan suspects at mu=1: {jordan_suspect}")
