"""EXP3b: Analyze the structure of Lyapunov-candidate increases observed in exp3.
For a few instances with V_increases>0, record the V trajectory and locate
increases (early transient vs late), their relative size, and the total
increase vs decrease. Also test whether V' = beta||B dy||^2 + beta||dt||^2
computed w.r.t. the true limit point (instead of the constructed KKT point)
behaves differently.
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from exp3_practical import make_instance, run_admm

# reproduce an instance with V increases: cfg 10 = condF=1e4, l1=0.5, rank_def=False, trial 1
inst = make_instance(6, 5, 4, condF=1e4, l1_mu=0.5, rank_def=False, seed=1000 + 97 * (10 * 100 + 1))
out = run_admm(inst, beta=0.5, K=5000, tol=1e-13)
V = np.array(out["hist"]["V"]); err = np.array(out["hist"]["err"])
dV = np.diff(V)
inc = dV > 0
print(f"k={out['k']}, V_increases={inc.sum()} / {len(dV)}")
idx = np.where(inc)[0]
print(f"increase steps: first={idx[0] if len(idx) else '-'}, last={idx[-1] if len(idx) else '-'}")
print(f"total increase = {dV[inc].sum():.3e}; total decrease = {-dV[~inc].sum():.3e}")
print(f"max relative increase = {np.max(dV[inc]/(V[:-1][inc]+1e-300)):.3e}")
print(f"V[0]={V[0]:.3e}, V[end]={V[-1]:.3e}")
# distribution over time: bucket increases into 10 phases
if len(idx):
    buckets = np.histogram(idx, bins=10, range=(0, len(dV)))[0]
    print("increases per decile of the run:", buckets)
# tail monotonicity: last increase position as fraction of run
print(f"last increase at {idx[-1]/len(dV):.1%} of run" if len(idx) else "no increases")
print(f"err[end]={err[-1]:.3e}")

# second instance: cfg 0 trial 0 (condF=1) with beta=2.0 had many increases
inst2 = make_instance(6, 5, 4, condF=1.0, l1_mu=0.0, rank_def=False, seed=1000 + 97 * (0 * 100 + 0))
out2 = run_admm(inst2, beta=2.0, K=5000, tol=1e-13)
V2 = np.array(out2["hist"]["V"]); dV2 = np.diff(V2); inc2 = dV2 > 0
idx2 = np.where(inc2)[0]
print(f"\ninstance2 (condF=1,beta=2): k={out2['k']}, increases={inc2.sum()}, "
      f"last at {idx2[-1]/len(dV2):.1%}" if len(idx2) else "none")
print(f"total inc={dV2[inc2].sum():.3e} vs total dec={-dV2[~inc2].sum():.3e}, "
      f"max rel inc={np.max(dV2[inc2]/(V2[:-1][inc2]+1e-300)) if inc2.any() else 0:.3e}")
b2 = np.histogram(idx2, bins=10, range=(0, len(dV2)))[0] if len(idx2) else None
print("increases per decile:", b2)
print(f"err[end]={out2['hist']['err'][-1]:.3e}")
