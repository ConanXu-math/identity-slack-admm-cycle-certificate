"""EXP12 (Track B, decisive): hunt for LOCALLY REPELLING KKT points.

Complex eigenvalues |mu|>1 of pattern matrices exist (exp9). If such an
eigenvalue belongs to the pattern matrix OF THE KKT CONE ITSELF, the KKT point
is locally repelling within its cone -- a potential counterexample route
(not covered by any earlier experiment; Theorem S only bounds real eigenvalues).

Setup: quadratic instances with KKT-by-construction (x*,y*,z*,lam* chosen,
b = Ax*+By*+z*, c1 = A'lam* - F x*, c2 = B'lam* - G y*, beta=1), so the KKT
point and its sign pattern sigma* = sign(t*), t* = z* + lam*, are known.
T_A = A(F+A'A)^{-1}A', T_B likewise. Check spec(M_{sigma*}).

Phase R: random instances, count KKT cones with complex |mu|>1.
Phase H: hill-climb over (F,G,A,B) keeping the KKT point fixed (recompute
         b,c1,c2) to maximize the complex modulus at sigma*.
Phase S: for every instance with max complex modulus > 1 at sigma*,
         simulate the TRUE ADMM from v* + eps*d (eps=1e-3, 40 directions,
         5000 steps) and classify: (a) back to v*, (b) other fixed point,
         (c) limit cycle, (d) growth > 1e6.  (c)/(d) = counterexample.
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), "results")
rng = np.random.default_rng(20260725)


def pattern_matrix(TA, TB, m, mask):
    Dp = np.diag(np.array([(mask >> i) & 1 for i in range(m)], dtype=float))
    Dm = np.eye(m) - Dp
    J = Dp - Dm
    A_p = -TA; A_t = -TA @ J
    B_p = -TB @ A_p; B_t = -TB @ (A_t + J)
    C_p = -A_p - B_p; C_t = Dm - A_t - B_t
    return np.block([[B_p, B_t], [C_p, C_t]])


def max_complex_modulus(TA, TB, m, mask):
    ev = np.linalg.eigvals(pattern_matrix(TA, TB, m, mask))
    cmplx = ev[np.abs(ev.imag) > 1e-9]
    return (max(abs(cmplx)) if len(cmplx) else 0.0), ev


def make_instance(m, seed):
    r = np.random.default_rng(seed)
    A = r.standard_normal((m, m)); B = r.standard_normal((m, m))
    F = r.standard_normal((m, m)); F = F.T @ F + 0.2 * np.eye(m)
    G = r.standard_normal((m, m)); G = G.T @ G + 0.2 * np.eye(m)
    xs = r.standard_normal(m); ys = r.standard_normal(m)
    act = r.random(m) < 0.5
    z = np.where(act, 0.0, r.uniform(0.2, 1.5, m))
    lam = np.where(act, -r.uniform(0.2, 1.5, m), 0.0)
    return dict(A=A, B=B, F=F, G=G, xs=xs, ys=ys, z=z, lam=lam)


def finish(inst):
    A, B, F, G = inst["A"], inst["B"], inst["F"], inst["G"]
    xs, ys, z, lam = inst["xs"], inst["ys"], inst["z"], inst["lam"]
    b = A @ xs + B @ ys + z
    c1 = A.T @ lam - F @ xs
    c2 = B.T @ lam - G @ ys
    t_star = z + lam
    return b, c1, c2, t_star


def kkt_cone_modulus(inst):
    A, B, F, G = inst["A"], inst["B"], inst["F"], inst["G"]
    m = A.shape[0]
    TA = A @ np.linalg.solve(F + A.T @ A, A.T)
    TB = B @ np.linalg.solve(G + B.T @ B, B.T)
    b, c1, c2, t_star = finish(inst)
    mask = int(np.sum((t_star > 0) * (2.0 ** np.arange(m))))
    return max_complex_modulus(TA, TB, m, mask), mask, (b, c1, c2, t_star), (TA, TB)


def simulate(inst, K=5000, eps=1e-3, ndirs=40):
    """Simulate true ADMM from perturbations of the KKT point; classify."""
    A, B, F, G = inst["A"], inst["B"], inst["F"], inst["G"]
    m = A.shape[0]
    b, c1, c2, t_star = finish(inst)
    Hx = F + A.T @ A; Hy = G + B.T @ B
    xs, ys = inst["xs"], inst["ys"]
    outcomes = {"to_v*": 0, "other_fp": 0, "cycle": 0, "growth": 0}
    for d in range(ndirs):
        dr = rng.standard_normal(2 * m); dr = dr / np.linalg.norm(dr)
        y = ys + eps * dr[:m]; t = t_star + eps * dr[m:]
        traj = []
        for k in range(K):
            at = np.abs(t)
            x = np.linalg.solve(Hx, -c1 - A.T @ (B @ y - b + at))
            y = np.linalg.solve(Hy, -c2 - B.T @ (A @ x - b + at))
            t = np.minimum(t, 0.0) - (A @ x + B @ y - b)
            if k >= K - 1500:
                traj.append(np.concatenate([x, y, t]))
        n_end = np.linalg.norm(np.concatenate([x, y, t]))
        if n_end > 1e6:
            outcomes["growth"] += 1
            continue
        d_end = max(np.linalg.norm(x - xs), np.linalg.norm(y - ys), np.linalg.norm(t - t_star))
        if d_end < 1e-6:
            outcomes["to_v*"] += 1
            continue
        # limit cycle detection: does a late state repeat?
        cyc = False
        for k1 in range(len(traj) - 100, len(traj) - 20):
            for k2 in range(k1 + 5, len(traj)):
                if np.linalg.norm(traj[k1] - traj[k2]) < 1e-9:
                    cyc = True; break
            if cyc: break
        if cyc:
            outcomes["cycle"] += 1
        else:
            # fixed point? check stationarity of last state
            outcomes["other_fp"] += 1
    return outcomes


t0 = time.time()
stats = dict(random_instances=0, kkt_complex_gt1=0, max_modulus=0.0)
candidates = []
print("=== Phase R: random KKT cones ===")
for i in range(8000):
    m = int(rng.integers(2, 7))
    inst = make_instance(m, seed=50000 + i)
    (mc, ev), mask, _, _ = kkt_cone_modulus(inst)
    stats["random_instances"] += 1
    stats["max_modulus"] = max(stats["max_modulus"], float(mc))
    if mc > 1.0:
        stats["kkt_complex_gt1"] += 1
        candidates.append(inst)
    elif mc > 0.999 and len(candidates) < 40:
        candidates.append(inst)
print(f"random: {stats['random_instances']} instances, KKT-cone complex |mu|>1: "
      f"{stats['kkt_complex_gt1']}, max modulus {stats['max_modulus']:.6f}", flush=True)

print("=== Phase H: hill-climb on near-1 candidates ===")
for idx, inst in enumerate(candidates[:40]):
    (mc, _), mask, _, _ = kkt_cone_modulus(inst)
    best = mc
    for it in range(150):
        m = inst["A"].shape[0]
        E = rng.standard_normal((m, m)) * 0.03
        inst2 = {k: (v + E if k in ("A", "B") else v) for k, v in inst.items()}
        # also perturb F, G (keep SPD)
        for key in ("F", "G"):
            E2 = rng.standard_normal((m, m)); E2 = (E2 + E2.T) * 0.03
            w, V = np.linalg.eigh(inst[key] + E2)
            if np.min(w) > 1e-3:
                inst2[key] = V @ np.diag(w) @ V.T
        (mc2, _), mask2, _, _ = kkt_cone_modulus(inst2)
        if mask2 == mask and mc2 > best:
            inst, best = inst2, mc2
    if best > 1.0:
        candidates.append(inst)
        print(f"hill-climb idx={idx}: modulus -> {best:.6f}", flush=True)

print("=== Phase S: perturb-and-simulate on KKT cones with |mu|>1 ===")
final = []
for idx, inst in enumerate(candidates):
    (mc, ev), mask, _, _ = kkt_cone_modulus(inst)
    if mc <= 1.0:
        continue
    out = simulate(inst)
    final.append(dict(idx=idx, modulus=float(mc), outcomes=out))
    print(f"instance {idx}: modulus={mc:.6f} outcomes={out}", flush=True)
    if out["cycle"] or out["growth"]:
        np.savez(os.path.join(OUT, f"exp12_repellent_{idx}.npz"),
                 **{k: v for k, v in inst.items()})
        print("*** POTENTIAL COUNTEREXAMPLE SAVED", flush=True)

with open(os.path.join(OUT, "exp12_summary.json"), "w") as f:
    json.dump({"seed": 20260725, "stats": stats, "phase_S": final,
               "elapsed_sec": time.time() - t0}, f, indent=2, default=str)
print(f"\nDONE: {stats}, phase-S instances: {len(final)}, elapsed={time.time()-t0:.0f}s")
