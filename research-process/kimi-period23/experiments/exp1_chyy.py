"""EXP1: Reproduce the Chen-He-Ye-Yuan (2016) divergence example for the
direct three-block ADMM (equality-constrained, zero objectives, free variables).

Instance (from CHYY, Math. Program. 155:57-79, 2016):
  min 0*x + 0*y + 0*z  s.t.  A1 x + A2 y + A3 z = 0,
  A1=(1,1,1)', A2=(1,1,2)', A3=(1,2,2)', x,y,z in R, beta=1.

We (a) build the 5x5 iteration matrix M on (y, z, lambda) numerically,
(b) compute its spectral radius, (c) simulate from standard starts.
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from admm_core import homog_equality_step

A1 = np.array([[1.0], [1.0], [1.0]])
A2 = np.array([[1.0], [1.0], [2.0]])
A3 = np.array([[1.0], [2.0], [2.0]])

# --- build iteration matrix on v = (y, z, lam1, lam2, lam3)
def step_vec(v):
    y, z, lam = v[0:1], v[1:2], v[2:5]
    y1, z1, lam1 = homog_equality_step(A1, A2, A3, y, z, lam, beta=1.0)
    return np.concatenate([y1, z1, lam1])

M = np.column_stack([step_vec(np.eye(5)[j]) for j in range(5)])
np.set_printoptions(precision=6, suppress=True)
print("iteration matrix M on (y,z,lam):")
print(M)
ev, V = np.linalg.eig(M)
print("eigenvalues:", np.sort_complex(ev))
rho = max(abs(ev))
print(f"spectral radius rho(M) = {rho:.10f}")
j = int(np.argmax(np.abs(ev)))
print(f"dominant eigenvalue: {ev[j]:.10f}")
dom = V[:, j].real
dom = dom / np.linalg.norm(dom)
print("dominant eigenvector (real part, unit norm):", dom)

# --- simulate
rng = np.random.default_rng(20260722)
starts = {
    "lam=(0,0,1)": np.array([0.0, 0.0, 0.0, 0.0, 1.0]),
    "lam=(1,1,1)": np.array([0.0, 0.0, 1.0, 1.0, 1.0]),
    "random": rng.standard_normal(5),
}
for name, v0 in starts.items():
    v = v0.copy()
    norms = [np.linalg.norm(v)]
    for k in range(200):
        v = step_vec(v)
        norms.append(np.linalg.norm(v))
    norms = np.array(norms)
    ratio = norms[-1] / norms[-2]
    print(f"start {name}: ||v^0||={norms[0]:.3e}  ||v^200||={norms[-1]:.3e}  "
          f"asymptotic ratio={ratio:.8f}")
print("EXPECT: rho>1 and geometric growth (CHYY divergence).")
