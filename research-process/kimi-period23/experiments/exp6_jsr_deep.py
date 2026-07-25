"""EXP6: Deep JSR probe. exp5-lite flagged pattern families where each M_sigma
has rho<=1 (Theorem Q) yet random length-80 products grow at rate >1.
Questions:
 (i) Is the growth sustained (long random sequences) or transient?
 (ii) Can we find an explicit expanding PERIODIC cycle (beam search on
     normalized spectral radius)?  JSR = sup over periodic products
     rho(P)^(1/|P|) (Berger-Wang), so an expanding cycle certifies JSR>1.
 (iii) Are such expanding switching sequences REALIZABLE as actual orbits of
     the state-dependent piecewise map? (simulate from the expanding direction)
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from exp5_jsr_lite import pattern_mats_from_proj, pattern_mats_from_contractions

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(555)


def make_family(kind, m, seed):
    r = np.random.default_rng(seed)
    if kind == "proj":
        dA = int(r.integers(1, m)); dB = int(r.integers(1, m))
        UA, _ = np.linalg.qr(r.standard_normal((m, dA)))
        UB, _ = np.linalg.qr(r.standard_normal((m, dB)))
        mats = pattern_mats_from_proj(UA @ UA.T, UB @ UB.T, m)
        meta = dict(P=UA @ UA.T, Q=UB @ UB.T)
    else:
        U1, _ = np.linalg.qr(r.standard_normal((m, m)))
        U2, _ = np.linalg.qr(r.standard_normal((m, m)))
        s1 = r.random(m); s2 = r.random(m)
        s1[r.random(m) < .3] = 0; s2[r.random(m) < .3] = 0
        s1[r.random(m) < .2] = 1; s2[r.random(m) < .2] = 1
        mats = pattern_mats_from_contractions(U1 @ np.diag(s1) @ U1.T,
                                              U2 @ np.diag(s2) @ U2.T, m)
        meta = dict(TA=U1 @ np.diag(s1) @ U1.T, TB=U2 @ np.diag(s2) @ U2.T)
    return mats, meta


def random_growth(mats, L=4000, trials=5):
    n = len(mats); d = mats[0].shape[0]
    best = 0.0
    for _ in range(trials):
        v = rng.standard_normal(d); v /= np.linalg.norm(v)
        norms = [1.0]
        for k in range(L):
            v = mats[rng.integers(0, n)] @ v
            nv = np.linalg.norm(v)
            if nv > 1e250: break
            norms.append(nv)
            if nv > 1e100:
                v = v / nv; norms.append(1.0)
        # slope of log-norm per step (least squares on second half)
        logs = np.log(np.maximum(norms[int(L//2):], 1e-300))
        x = np.arange(len(logs))
        slope = np.polyfit(x, logs, 1)[0]
        best = max(best, float(np.exp(slope)))
    return best


def beam_search_cycle(mats, depth=40, width=60):
    """Beam search maximizing normalized spectral radius rho(P)^(1/len)."""
    n = len(mats); d = mats[0].shape[0]
    beam = [(np.eye(d), ())]
    best_r, best_seq = 0.0, ()
    for lev in range(1, depth + 1):
        cand = []
        for P, seq in beam:
            for i in range(n):
                P2 = P @ mats[i]
                seq2 = seq + (i,)
                r = float(max(np.abs(np.linalg.eigvals(P2)))) ** (1.0 / lev)
                cand.append((r, np.linalg.norm(P2, 2), P2, seq2))
                if r > best_r:
                    best_r, best_seq = r, seq2
        cand.sort(key=lambda c: -c[0])
        beam = [(P, s) for (r, nrm, P, s) in cand[:width]]
        if best_r > 1.02:
            break
    return best_r, best_seq


results = []
t0 = time.time()
for kind in ("proj", "contr"):
    for idx in range(10):
        m = 3
        mats, meta = make_family(kind, m, seed=9000 + idx)
        rate = random_growth(mats)
        r_cyc, seq = beam_search_cycle(mats)
        rec = dict(kind=kind, idx=idx, sustained_rate=rate,
                   cycle_rho=r_cyc, cycle_len=len(seq), cycle=seq)
        results.append(rec)
        print(f"{kind}#{idx}: sustained_rate={rate:.6f}  best_cycle rho^(1/k)={r_cyc:.6f} "
              f"(len {len(seq)}, seq {seq[:12]}{'...' if len(seq)>12 else ''})")
        if r_cyc > 1 + 1e-9:
            np.savez(os.path.join(OUT, f"exp6_expanding_cycle_{kind}_{idx}.npz"),
                     mats=np.array(mats), seq=np.array(seq), rho=r_cyc, **meta)

print(f"\nany sustained_rate>1: {any(r['sustained_rate']>1 for r in results)}")
print(f"any expanding cycle: {any(r['cycle_rho']>1+1e-9 for r in results)}")
with open(os.path.join(OUT, "exp6_summary.json"), "w") as f:
    json.dump({"seed": 555, "results": results, "elapsed_sec": time.time()-t0},
              f, indent=2, default=str)
print(f"Done in {time.time()-t0:.1f}s")
