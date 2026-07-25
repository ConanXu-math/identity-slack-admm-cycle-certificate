"""EXP13 (Track B): deeper realizable expanding cycle search via beam search.
For instances with the largest pattern-matrix spectral radii (regenerated),
beam-search pattern sequences to depth 14 (width 300), checking realizability
(simulate the true piecewise orbit from candidate eigen-directions and verify
the realized sign sequence == candidate sequence and the orbit grows).
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260726)


def pattern_mats(TA, TB, m):
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


def rand_contraction(m):
    U, _ = np.linalg.qr(rng.standard_normal((m, m)))
    s = 1.0 - 10.0 ** (-rng.uniform(0, 3, m))
    s[rng.random(m) < .25] = 0
    return U @ np.diag(s) @ U.T


def simulate(mats, m, v, K):
    cur = v.copy()
    seq = []
    for k in range(K):
        t = cur[m:]
        mask = int(np.sum((t > 0) * (2.0 ** np.arange(m))))
        seq.append(mask)
        cur = mats[mask] @ cur
    return cur, seq


def beam_check(mats, m, depth=14, width=300):
    n = len(mats); d = 2 * m
    beam = [(np.eye(d), ())]
    for lev in range(1, depth + 1):
        cand = []
        for P, seq in beam:
            for i in range(n):
                P2 = P @ mats[i]
                seq2 = seq + (i,)
                ev = np.linalg.eigvals(P2)
                realmax = max(ev.real) if len(ev) else 0.0
                rho = max(abs(ev))
                cand.append((realmax, rho, P2, seq2))
                # realizability check for real mu>1
                if realmax > 1.0 + 1e-9:
                    w, V = np.linalg.eig(P2)
                    for j in range(len(w)):
                        if abs(w[j].imag) < 1e-9 and w[j].real > 1.0 + 1e-9:
                            v = V[:, j].real
                            vend, realized = simulate(mats, m, v / np.linalg.norm(v), lev)
                            if realized == list(seq2) and np.linalg.norm(vend) > 1.0:
                                return dict(mu=w[j].real, seq=seq2, v=v)
        cand.sort(key=lambda c: -(c[0] + 0.3 * c[1]))
        beam = [(P, s) for (_, _, P, s) in cand[:width]]
    return None


t0 = time.time()
found = []
tested = 0
for idx in range(60):
    m = int(rng.integers(2, 5))
    TA, TB = rand_contraction(m), rand_contraction(m)
    mats = pattern_mats(TA, TB, m)
    rho_max = max(max(abs(np.linalg.eigvals(M))) for M in mats)
    if rho_max < 0.9999 and idx < 40:
        continue
    tested += 1
    hit = beam_check(mats, m)
    if hit:
        found.append(dict(idx=idx, m=m, mu=hit["mu"], seq=hit["seq"]))
        np.savez(os.path.join(OUT, f"exp13_cycle_{idx}.npz"),
                 TA=TA, TB=TB, seq=np.array(hit["seq"]), mu=hit["mu"], v=hit["v"])
        print(f"*** REALIZABLE EXPANDING CYCLE idx={idx} mu={hit['mu']:.9f} seq={hit['seq']}", flush=True)
        break
    if idx % 10 == 0:
        print(f"idx={idx} tested={tested} elapsed={time.time()-t0:.0f}s", flush=True)

with open(os.path.join(OUT, "exp13_summary.json"), "w") as f:
    json.dump({"seed": 20260726, "tested": tested, "found": found,
               "depth": 14, "width": 300, "elapsed_sec": time.time() - t0},
              f, indent=2, default=str)
print(f"\nDONE: tested={tested}, found={len(found)}, elapsed={time.time()-t0:.0f}s")
