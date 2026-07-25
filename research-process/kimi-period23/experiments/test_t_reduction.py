"""Validate the (y,t) shadow-variable reduction against the direct (x,y,z,lam)
implementation on random convex inequality-constrained problems.

If research/01_theory_notes.md Sec.3 is correct, trajectories must coincide
exactly (up to floating point). Objectives: f(x)=0.5 x'FQ x, g(y)=0.5 y'GQ y
with FQ, GQ symmetric PSD (strongly convex after ridge), X, Y full spaces.
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from admm_core import homog_slack_step

rng = np.random.default_rng(20260722)


def run_direct(A, B, b, FQ, GQ, y0, z0, lam0, beta, K):
    """Direct (x,y,z,lam) iteration; x,y subproblems are convex quadratics."""
    n1 = A.shape[1]
    x = np.zeros(n1); y = y0.copy(); z = z0.copy(); lam = lam0.copy()
    Hx = FQ + beta * A.T @ A
    Hy = GQ + beta * B.T @ B
    traj = []
    for k in range(K):
        x = np.linalg.solve(Hx, -beta * A.T @ (B @ y + z - b - lam / beta))
        y = np.linalg.solve(Hy, -beta * B.T @ (A @ x + z - b - lam / beta))
        s = A @ x + B @ y - b
        z = np.maximum(lam / beta - s, 0.0)
        lam = lam - beta * (s + z)
        traj.append((x.copy(), y.copy(), z.copy(), lam.copy()))
    return traj


def run_tform(A, B, b, FQ, GQ, y0, t0, beta, K):
    """(y,t) shadow form of the same iteration."""
    Hx = FQ + beta * A.T @ A
    Hy = GQ + beta * B.T @ B
    y = y0.copy(); t = t0.copy()
    traj = []
    for k in range(K):
        at = np.abs(t)
        x = np.linalg.solve(Hx, -beta * A.T @ (B @ y - b + at))
        y = np.linalg.solve(Hy, -beta * B.T @ (A @ x - b + at))
        t = np.minimum(t, 0.0) - (A @ x + B @ y - b)
        traj.append((x.copy(), y.copy(), np.maximum(t, 0.0), beta * np.minimum(t, 0.0)))
    return traj


ok = True
for trial in range(20):
    m, n1, n2 = 4, 3, 2
    A = rng.standard_normal((m, n1))
    B = rng.standard_normal((m, n2))
    b = rng.standard_normal(m)
    FQ = rng.standard_normal((n1, n1)); FQ = FQ.T @ FQ + 0.1 * np.eye(n1)
    GQ = rng.standard_normal((n2, n2)); GQ = GQ.T @ GQ + 0.1 * np.eye(n2)
    y0 = rng.standard_normal(n2)
    t0 = rng.standard_normal(m)
    z0 = np.maximum(t0, 0.0)
    beta = 1.3
    lam0 = beta * np.minimum(t0, 0.0)   # lambda^k/beta = min(t^k,0)
    K = 50
    T1 = run_direct(A, B, b, FQ, GQ, y0, z0, lam0, beta, K)
    T2 = run_tform(A, B, b, FQ, GQ, y0, t0, beta, K)
    for k in range(K):
        for a_, b_ in zip(T1[k], T2[k]):
            if not np.allclose(a_, b_, atol=1e-9):
                ok = False
                print(f"MISMATCH trial={trial} k={k}: {a_} vs {b_}")
print("EQUIVALENCE TEST:", "PASS (20 random instances, 50 steps)" if ok else "FAIL")

# homogeneous slack step vs direct homogeneous iteration (f=g=0, b=0, beta=1)
ok2 = True
for trial in range(20):
    m, n1, n2 = 3, 3, 3
    A = rng.standard_normal((m, n1))
    B = rng.standard_normal((m, n2))
    y = rng.standard_normal(n2); t = rng.standard_normal(m)
    for k in range(30):
        x = -np.linalg.pinv(A) @ (B @ y + np.maximum(t, 0.0) - np.minimum(t, 0.0))
        y = -np.linalg.pinv(B) @ (A @ x + np.maximum(t, 0.0) - np.minimum(t, 0.0))
        s = A @ x + B @ y
        z = np.maximum(np.minimum(t, 0.0) - s, 0.0)
        lam = np.minimum(t, 0.0) - (s + z)
        y2, t2 = homog_slack_step(A, B, y, t)
        t = z + lam
        if not (np.allclose(y, y2, atol=1e-9) and np.allclose(t, t2, atol=1e-9)):
            ok2 = False
            print("HOMOG MISMATCH", trial, k)
print("HOMOGENEOUS EQUIVALENCE TEST:", "PASS" if ok2 else "FAIL")
