"""EXP5: Switching-level analysis. After Theorem Q (no single-pattern expansion),
the only remaining homogeneous divergence mechanism is CROSS-PATTERN switching.
This script estimates the JOINT SPECTRAL RADIUS (JSR) of the pattern-matrix
family {M_sigma} for random instances (projector case and PSD-contraction case).

If JSR <= 1 for a family, then ALL orbits of the state-dependent piecewise map
are bounded (arbitrary switching bound => realizable switching bound).
If JSR > 1 for some instance, we flag it and test whether an expanding product
is REALIZABLE as an actual orbit (potential counterexample seed).

Method: Gripenberg-style branch and bound.
  lower bound lb: max over cyclic products P (len<=L) of rho(P)^(1/len)
  upper bound ub: max over products of len L of ||P||^(1/L) (any L)
Also report max_i ||M_i||_2 (if <=1, JSR<=1 trivially).
"""
import numpy as np
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
from admm_core import homog_slack_matrix

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260722)


def pattern_mats_from_proj(P, Q, m):
    mats = []
    for mask in range(2 ** m):
        Dp = np.diag(np.array([(mask >> i) & 1 for i in range(m)], dtype=float))
        Dm = np.eye(m) - Dp
        J = Dp - Dm
        A_p = -P; A_t = -P @ J
        B_p = -Q @ A_p; B_t = -Q @ (A_t + J)
        C_p = -A_p - B_p; C_t = Dm - A_t - B_t
        mats.append(np.block([[B_p, B_t], [C_p, C_t]]))
    return mats


def pattern_mats_from_contractions(TA, TB, m):
    mats = []
    for mask in range(2 ** m):
        Dp = np.diag(np.array([(mask >> i) & 1 for i in range(m)], dtype=float))
        Dm = np.eye(m) - Dp
        J = Dp - Dm
        A_p = -TA; A_t = -TA @ J
        B_p = -TB @ A_p; B_t = -TB @ (A_t + J)
        C_p = -A_p - B_p; C_t = Dm - A_t - B_t
        mats.append(np.block([[B_p, B_t], [C_p, C_t]]))
    return mats


def jsr_bounds(mats, max_depth=14, norm_cap=3.0):
    """Return (lb, ub, best_product_info). Gripenberg B&B."""
    d = mats[0].shape[0]
    n = len(mats)
    norms = [np.linalg.norm(M, 2) for M in mats]
    lb = max(float(max(np.abs(np.linalg.eigvals(M)))) for M in mats)
    lb_info = ("single", int(np.argmax([max(np.abs(np.linalg.eigvals(M))) for M in mats])))
    # candidate cycles up to length 2 for a better initial lb
    for i, j in itertools.product(range(n), repeat=2):
        P = mats[i] @ mats[j]
        r = float(max(np.abs(np.linalg.eigvals(P)))) ** 0.5
        if r > lb:
            lb, lb_info = r, ("pair", (i, j))
    best_ub = max(norms)
    # DFS with pruning
    stack = [(np.eye(d), (), 1.0)]  # product, seq, its norm
    while stack:
        P, seq, nrm = stack.pop()
        depth = len(seq)
        if depth > 0:
            r = float(max(np.abs(np.linalg.eigvals(P)))) ** (1.0 / depth)
            if r > lb:
                lb, lb_info = r, ("cycle", seq)
        if depth >= max_depth:
            continue
        for i, M in enumerate(mats):
            P2 = P @ M
            n2 = np.linalg.norm(P2, 2)
            seq2 = seq + (i,)
            d2 = len(seq2)
            # update ub candidate
            ub_c = n2 ** (1.0 / d2)
            # prune: if norm rate below lb, this branch cannot beat lb
            if ub_c > lb and n2 < norm_cap:
                stack.append((P2, seq2, n2))
                if d2 >= 4:
                    best_ub = max(best_ub, ub_c)
    # final upper bound: any length-L product norm bound
    return lb, min(best_ub, max(norms)), lb_info, max(norms)


if __name__ == "__main__":
    results = []
    t_start = time.time()
    print("=== projector families (Theorem H class) ===")
    for trial in range(60):
        m = int(rng.integers(2, 5))
        dA = int(rng.integers(1, m)); dB = int(rng.integers(1, m))
        UA, _ = np.linalg.qr(rng.standard_normal((m, dA)))
        UB, _ = np.linalg.qr(rng.standard_normal((m, dB)))
        P = UA @ UA.T; Q = UB @ UB.T
        mats = pattern_mats_from_proj(P, Q, m)
        lb, ub, info, maxnorm = jsr_bounds(mats, max_depth=12)
        results.append(dict(kind="proj", m=m, lb=lb, ub=ub, maxnorm=maxnorm))
        flag = "  <-- JSR>1?" if lb > 1 + 1e-9 else ""
        if lb > 0.999 or maxnorm > 1.0:
            print(f"proj m={m} dA={dA} dB={dB}: lb={lb:.6f} ub={ub:.6f} max||M||={maxnorm:.4f}{flag}")

    print("=== PSD contraction families (Theorem Q class) ===")
    for trial in range(60):
        m = int(rng.integers(2, 5))
        U1, _ = np.linalg.qr(rng.standard_normal((m, m)))
        U2, _ = np.linalg.qr(rng.standard_normal((m, m)))
        s1 = rng.random(m) * 0.999; s2 = rng.random(m) * 0.999
        s1[rng.random(m) < 0.3] = 0.0; s2[rng.random(m) < 0.3] = 0.0
        s1[rng.random(m) < 0.15] = 1.0; s2[rng.random(m) < 0.15] = 1.0
        TA = U1 @ np.diag(s1) @ U1.T; TB = U2 @ np.diag(s2) @ U2.T
        mats = pattern_mats_from_contractions(TA, TB, m)
        lb, ub, info, maxnorm = jsr_bounds(mats, max_depth=12)
        results.append(dict(kind="contr", m=m, lb=lb, ub=ub, maxnorm=maxnorm))
        flag = "  <-- JSR>1?" if lb > 1 + 1e-9 else ""
        if lb > 0.999 or maxnorm > 1.0:
            print(f"contr m={m}: lb={lb:.6f} ub={ub:.6f} max||M||={maxnorm:.4f}{flag}")

    lbs = [r["lb"] for r in results]
    maxnorms = [r["maxnorm"] for r in results]
    print(f"\ninstances: {len(results)}")
    print(f"max JSR lower bound found: {max(lbs):.9f}")
    print(f"fraction with max||M_sigma||>1: {np.mean([x>1+1e-9 for x in maxnorms]):.2%} "
          f"(spectral-norm contraction fails, as expected)")
    print(f"any JSR lower bound > 1: {any(x > 1+1e-9 for x in lbs)}")
    with open(os.path.join(OUT, "exp5_summary.json"), "w") as f:
        json.dump({"seed": 20260722, "n": len(results), "max_lb": max(lbs),
                   "frac_maxnorm_gt1": float(np.mean([x>1+1e-9 for x in maxnorms])),
                   "any_lb_gt1": bool(any(x > 1+1e-9 for x in lbs)),
                   "elapsed_sec": time.time() - t_start}, f, indent=2)
    print(f"Done in {time.time()-t_start:.1f}s")
