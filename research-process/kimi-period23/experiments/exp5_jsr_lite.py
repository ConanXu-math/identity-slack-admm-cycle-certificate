"""EXP5-lite: JSR estimation for pattern-matrix families (lighter version).
For each family: exhaustive cyclic products up to length 3 (lower bound via
spectral radii) + 300 random products of length 80 (norm growth rate).
m <= 3 (at most 8 matrices). No heavy branch-and-bound.
"""
import numpy as np
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
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

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(31337)

def jsr_estimates(mats, n_rand=300, L=80):
    n = len(mats)
    lb = 0.0; info = None
    for Lc in (1, 2, 3):
        for seq in itertools.product(range(n), repeat=Lc):
            P = np.eye(mats[0].shape[0])
            for i in seq: P = P @ mats[i]
            r = float(max(np.abs(np.linalg.eigvals(P)))) ** (1.0 / Lc)
            if r > lb: lb, info = r, seq
    # random long products: growth rate of norms
    max_rate = 0.0
    for _ in range(n_rand):
        seq = rng.integers(0, n, L)
        P = np.eye(mats[0].shape[0])
        for i in seq: P = P @ mats[i]
        rate = np.linalg.norm(P, 2) ** (1.0 / L)
        max_rate = max(max_rate, rate)
    maxnorm = max(np.linalg.norm(M, 2) for M in mats)
    return lb, info, max_rate, maxnorm

records = []
t0 = time.time()
for kind in ("proj", "contr"):
    for trial in range(40):
        m = int(rng.integers(2, 4))
        if kind == "proj":
            dA = int(rng.integers(1, m)); dB = int(rng.integers(1, m))
            UA, _ = np.linalg.qr(rng.standard_normal((m, dA)))
            UB, _ = np.linalg.qr(rng.standard_normal((m, dB)))
            mats = pattern_mats_from_proj(UA @ UA.T, UB @ UB.T, m)
        else:
            U1, _ = np.linalg.qr(rng.standard_normal((m, m)))
            U2, _ = np.linalg.qr(rng.standard_normal((m, m)))
            s1 = rng.random(m); s2 = rng.random(m)
            s1[rng.random(m) < .3] = 0; s2[rng.random(m) < .3] = 0
            s1[rng.random(m) < .2] = 1; s2[rng.random(m) < .2] = 1
            mats = pattern_mats_from_contractions(U1 @ np.diag(s1) @ U1.T,
                                                  U2 @ np.diag(s2) @ U2.T, m)
        lb, info, rand_rate, maxnorm = jsr_estimates(mats)
        records.append(dict(kind=kind, m=m, lb=lb, rand_rate=rand_rate, maxnorm=maxnorm))
        if lb > 0.999 or rand_rate > 0.999:
            print(f"{kind} m={m}: cyclic lb={lb:.6f} (seq {info}), rand_rate={rand_rate:.6f}, max||M||={maxnorm:.4f}")

lbs = [r["lb"] for r in records]; rr = [r["rand_rate"] for r in records]
print(f"\nfamilies: {len(records)}; max cyclic lb = {max(lbs):.9f}; "
      f"max random-product rate = {max(rr):.9f}")
print(f"any lb>1: {any(x>1+1e-9 for x in lbs)}; any rand_rate>1: {any(x>1+1e-9 for x in rr)}")
print(f"fraction with max||M||>1: {np.mean([r['maxnorm']>1+1e-9 for r in records]):.2%}")
with open(os.path.join(OUT, "exp5_summary.json"), "w") as f:
    json.dump({"seed": 31337, "records": records, "max_lb": max(lbs),
               "max_rand_rate": max(rr), "elapsed_sec": time.time() - t0}, f, indent=2)
print(f"Done in {time.time()-t0:.1f}s")
