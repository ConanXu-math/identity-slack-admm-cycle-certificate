"""EXP8 (Track B): Adversarial orbit-growth optimization + non-quadratic searches.

(a) Hill-climb over (T_A, T_B) to maximize orbit growth of the homogeneous
    quadratic piecewise map (K=300 steps, best of 6 random starts).
(b) Piecewise-LINEAR objectives: f(x)=||x||_1, g(y)=||y||_1 (prox kinks ->
    T_A piecewise linear, NOT covered by Theorem Q), b=0, long runs.
(c) Affine drift: quadratic objectives, b != 0, long runs from random starts.

Any growth > 1e6 x is reported as a divergence candidate.
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260723)


def step_quad(TA, TB, p, t, b):
    """One piecewise step on the essential state (p, t), p = By in R^m:
    a = -TA(p + |t| - b); p' = -TB(a + |t| - b); t' = min(t,0) - (a + p' - b)."""
    at = np.abs(t)
    a = -TA @ (p + at - b)
    p2 = -TB @ (a + at - b)
    t2 = np.minimum(t, 0.0) - (a + p2 - b)
    return p2, t2


def orbit_growth(TA, TB, b, K=300, starts=6):
    m = TA.shape[0]
    best = 0.0
    for _ in range(starts):
        y = rng.standard_normal(m); t = rng.standard_normal(m)
        n0 = np.linalg.norm(y) + np.linalg.norm(t) + 1e-300
        for k in range(K):
            y, t = step_quad(TA, TB, y, t, b)
        g = (np.linalg.norm(y) + np.linalg.norm(t)) / n0
        best = max(best, g)
    return best


def rand_contraction(m, near1=True):
    U, _ = np.linalg.qr(rng.standard_normal((m, m)))
    if near1:
        s = 1.0 - 10.0 ** (-rng.uniform(0, 3, m))
    else:
        s = rng.random(m)
    s[rng.random(m) < .25] = 0
    return U @ np.diag(s) @ U.T


t0 = time.time()
print("=== (a) adversarial hill-climb (quadratic, b=0) ===")
bestG, bestInst = 0.0, None
for restart in range(30):
    m = int(rng.integers(2, 5))
    TA, TB = rand_contraction(m), rand_contraction(m)
    G = orbit_growth(TA, TB, np.zeros(m))
    for it in range(60):
        E = rng.standard_normal((m, m)); E = (E + E.T) / 2 * 0.05
        w, V = np.linalg.eigh(TA + E); w = np.clip(w, 0, 1)
        TA2 = V @ np.diag(w) @ V.T
        w, V = np.linalg.eigh(TB + E); w = np.clip(w, 0, 1)
        TB2 = V @ np.diag(w) @ V.T
        G2 = orbit_growth(TA2, TB2, np.zeros(m))
        if G2 > G:
            TA, TB, G = TA2, TB2, G2
    if G > bestG:
        bestG, bestInst = G, (m, TA.copy(), TB.copy())
    print(f"restart {restart}: best-so-far growth={bestG:.4g}", flush=True)
print(f"(a) max orbit growth found: {bestG:.4g}")

print("=== (b) piecewise-linear objectives f=g=||.||_1, b=0 ===")
def softth(u, a): return np.sign(u) * np.maximum(np.abs(u) - a, 0.0)
div_b = 0
for trial in range(300):
    m, n1, n2 = int(rng.integers(2, 5)), int(rng.integers(2, 5)), int(rng.integers(2, 5))
    A = rng.standard_normal((m, n1)); B = rng.standard_normal((m, n2))
    beta = float(10 ** rng.uniform(-1, 1))
    # prox of ||.||_1 + beta/2 ||A x + c||^2 : no closed form; use scalar prox
    # on |x| with quadratic penalty -> iterative; instead choose f = ||x||^2_1
    # with A = I-ish structure? Simpler: f(x) = ||x||_1, subproblem solved by
    # FISTA warm-started (50 iters).
    L1 = beta * np.linalg.norm(A, 2) ** 2
    L2 = beta * np.linalg.norm(B, 2) ** 2
    x = np.zeros(n1)
    y = rng.standard_normal(n2); t = rng.standard_normal(m)
    n0 = np.linalg.norm(y) + np.linalg.norm(t)
    for k in range(2000):
        at = np.abs(t)
        # x-subproblem: min ||x||_1 + beta/2||A x + B y + at||^2 via FBS
        c = B @ y + at
        for _ in range(50):
            x = softth(x - beta * A.T @ (A @ x + c) / L1, 1.0 / L1)
        c = A @ x + at
        for _ in range(50):
            y = softth(y - beta * B.T @ (B @ y + c) / L2, 1.0 / L2)
        t = np.minimum(t, 0.0) - (A @ x + B @ y)
    n1_ = np.linalg.norm(y) + np.linalg.norm(t)
    if n1_ > 1e6 * max(n0, 1e-12):
        div_b += 1
        print(f"GROWTH (b) trial={trial}: {n0:.2e} -> {n1_:.2e}")
print(f"(b) divergence candidates: {div_b}/300")

print("=== (c) affine drift: quadratic objectives, b != 0 ===")
div_c = 0
for trial in range(300):
    m = int(rng.integers(2, 5))
    TA, TB = rand_contraction(m), rand_contraction(m)
    wA, VA = np.linalg.eigh(TA); A = VA @ np.diag(np.sqrt(np.clip(wA, 0, None))) @ VA.T
    wB, VB = np.linalg.eigh(TB); B = VB @ np.diag(np.sqrt(np.clip(wB, 0, None))) @ VB.T
    F = np.eye(m) - TA; G = np.eye(m) - TB
    b = rng.standard_normal(m)
    beta = 1.0
    Hx = F + beta * A @ A; Hy = G + beta * B @ B
    y = rng.standard_normal(m); t = rng.standard_normal(m)
    n0 = np.linalg.norm(y) + np.linalg.norm(t)
    for k in range(3000):
        at = np.abs(t)
        x = np.linalg.solve(Hx, -beta * A @ (B @ y - b + at))
        y = np.linalg.solve(Hy, -beta * B @ (A @ x - b + at))
        t = np.minimum(t, 0.0) - (A @ x + B @ y - b)
    n1_ = np.linalg.norm(y) + np.linalg.norm(t)
    if n1_ > 1e6 * max(n0, 1e-12):
        div_c += 1
        print(f"GROWTH (c) trial={trial}: {n0:.2e} -> {n1_:.2e}")
print(f"(c) divergence candidates: {div_c}/300")

with open(os.path.join(OUT, "exp8_summary.json"), "w") as f:
    json.dump({"seed": 20260723, "max_growth_quad": bestG,
               "div_pwl": div_b, "div_affine": div_c,
               "elapsed_sec": time.time() - t0}, f, indent=2)
print(f"Done in {time.time()-t0:.0f}s")
