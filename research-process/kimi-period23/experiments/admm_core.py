"""Core ADMM iterations for the slack-variable three-block study.

Conventions (matching inputs/problem_statement.md):
  L_beta = f(x)+g(y)+delta_+(z) - <lam, r> + (beta/2)||r||^2, r = Ax+By+z-b.
  Update order x -> y -> z -> lambda, unit dual step: lam+ = lam - beta*r.

All experiments are reproducible: every script takes an explicit numpy Generator seed.
"""
from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Generic three-block direct ADMM for ZERO objectives (homogeneous setting).
# Subproblems are least squares; solution choice = minimum-norm (pinv).
# ---------------------------------------------------------------------------

def homog_equality_step(A1, A2, A3, y, z, lam, beta=1.0):
    """One direct 3-block ADMM sweep for min 0 s.t. A1 x + A2 y + A3 z = 0,
    variables free (the CHYY setting). Returns (y+, z+, lam+)."""
    m = A1.shape[0]
    # x-update: min_x ||A1 x + A2 y + A3 z - lam/beta||^2  (min-norm LS)
    c = A2 @ y + A3 @ z - lam / beta
    x = -np.linalg.pinv(A1) @ c
    # y-update
    c = A1 @ x + A3 @ z - lam / beta
    y_new = -np.linalg.pinv(A2) @ c
    # z-update
    c = A1 @ x + A2 @ y_new - lam / beta
    z_new = -np.linalg.pinv(A3) @ c
    # lambda update
    r = A1 @ x + A2 @ y_new + A3 @ z_new
    lam_new = lam - beta * r
    return y_new, z_new, lam_new


def homog_slack_step(A, B, y, t, beta=1.0):
    """One direct 3-block ADMM sweep for the slack form with f=g=0, b=0,
    expressed in the (y, t) shadow variables (t = z + lam/beta).
    Subproblem solutions: minimum-norm least squares.
    Returns (y+, t+)."""
    t_pos = np.maximum(t, 0.0)   # = z
    t_neg = np.minimum(t, 0.0)   # = lam/beta
    # x-update: min_x ||A x + B y + |t|||^2
    x = -np.linalg.pinv(A) @ (B @ y + np.abs(t))
    # y-update
    y_new = -np.linalg.pinv(B) @ (A @ x + np.abs(t))
    # t-update: t+ = min(t,0) - (A x + B y+)
    t_new = t_neg - (A @ x + B @ y_new)
    return y_new, t_new


def homog_slack_matrix(A, B, sigma):
    """Linear map M_sigma of homog_slack_step restricted to the cone
    {t : sign(t) = sigma}, in coordinates (xi, t) with p = B y = V_B xi.
    A, B : m x dA, m x dB (only their ranges matter).
    sigma : array of +/-1 of length m.
    Returns square matrix of size (dB + m)."""
    m, dB = B.shape
    UA, _ = np.linalg.qr(A)
    UB, _ = np.linalg.qr(B)
    PA = UA @ UA.T                      # projector onto range(A)
    Dp = np.diag((sigma > 0).astype(float))   # t_+ = Dp t
    Dm = np.diag((sigma < 0).astype(float))   # t_- = Dm t
    J = Dp - Dm                               # |t| = J t within this cone
    # a' = -PA (UB xi + J t)
    # xi' = -UB^T (a' + J t)
    # t'  = Dm t - a' - UB xi'
    # Assemble blocks: state v = (xi, t)
    A_xi = -PA @ UB
    A_t = -PA @ J
    # xi' = -UB^T a' - UB^T J t = -UB^T A_xi xi - (UB^T A_t + UB^T J) t
    B_xi = -UB.T @ A_xi
    B_t = -UB.T @ A_t - UB.T @ J
    # t' = -A_xi xi + (Dm - A_t) t - UB xi'
    #    = (-A_xi - UB B_xi) xi + (Dm - A_t - UB B_t) t
    C_xi = -A_xi - UB @ B_xi
    C_t = Dm - A_t - UB @ B_t
    M = np.block([[B_xi, B_t], [C_xi, C_t]])
    return M


def spectral_scan(A, B):
    """For all 2^m sign patterns, compute eigenvalues of M_sigma.
    Returns list of dicts with pattern, max |mu|, and the max-real-eigenvalue
    self-consistency info."""
    m = A.shape[0]
    out = []
    for mask in range(2 ** m):
        sigma = np.array([1.0 if (mask >> i) & 1 else -1.0 for i in range(m)])
        M = homog_slack_matrix(A, B, sigma)
        ev = np.linalg.eigvals(M)
        rho = np.max(np.abs(ev)) if ev.size else 0.0
        # best real eigenvalue > 0 with sign-consistent eigenvector
        best_consistent = None
        if ev.size:
            V = np.linalg.eig(M)[1]
            for j in range(ev.size):
                mu = ev[j]
                if abs(mu.imag) < 1e-10 and mu.real > 0:
                    vec = V[:, j].real
                    tvec = vec[B.shape[1]:]
                    s = np.sign(tvec)
                    # allow zeros in tvec (degenerate); require nonzero match
                    nz = np.abs(tvec) > 1e-9
                    if nz.all() and np.all(s[nz] == sigma[nz]):
                        if best_consistent is None or mu.real > best_consistent:
                            best_consistent = mu.real
        out.append({"sigma": sigma, "rho": rho, "mu_consistent": best_consistent})
    return out
