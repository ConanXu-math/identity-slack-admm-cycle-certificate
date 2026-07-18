"""Exact convergence certificate for the relaxed strict-66-cycle witness.

The quadratic problem and the initial point are reconstructed by the
accompanying ``strict_cycle_certificate.py``.  Only the dual update is changed to

    lambda_next = lambda - (1/2) * (x_next + y_next + z_next - rhs).

The certificate proves convergence for this fixed QP and this fixed initial
point.  It does not claim convergence for arbitrary initial points or for the
whole identity-slack model class.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import sympy as sp


# The exact 208-step prefix produces very large rational numerators and
# denominators.  Python 3.11+ limits decimal integer rendering by default;
# disabling only that rendering guard does not change any arithmetic.
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = ROOT.parent
EXACT_VERIFIER = ROOT / "strict_cycle_certificate.py"
DEFAULT_OUTPUT = (
    REPOSITORY_ROOT / "certificates" / "relaxed_multiplier_half_certificate.json"
)
TAU = sp.Rational(1, 2)
SELECTOR_01 = sp.diag(0, 1)


def load_exact_verifier():
    """Load the exact witness constructor without creating a package dependency."""
    spec = importlib.util.spec_from_file_location("strict_66_cycle_exact", EXACT_VERIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load exact verifier: {EXACT_VERIFIER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def positive_part(vector: sp.Matrix) -> sp.Matrix:
    """Coordinatewise exact projection onto the nonnegative orthant."""
    return sp.Matrix([value if value > 0 else sp.Integer(0) for value in vector])


def mask(vector: sp.Matrix) -> str:
    """Return the strict sign mask used by the orthant projection."""
    return "".join("1" if value > 0 else "0" if value < 0 else "T" for value in vector)


def relaxed_components(
    state: sp.Matrix,
    problem: dict[str, object],
    selector: sp.Matrix | None,
) -> dict[str, sp.Matrix]:
    """Apply one exact sweep; ``selector=None`` uses the true positive part."""
    y = state[:2, 0]
    z = state[2:4, 0]
    lam = state[4:6, 0]
    x_next = problem["M"] * (lam - y - z + problem["rhs"])
    y_next = problem["N"] * (lam - x_next - z + problem["rhs"])
    q_next = problem["rhs"] - x_next - y_next + lam
    z_next = positive_part(q_next) if selector is None else selector * q_next
    residual = x_next + y_next + z_next - problem["rhs"]
    lambda_next = lam - TAU * residual
    next_state = y_next.col_join(z_next).col_join(lambda_next)
    return {
        "x": x_next,
        "y": y_next,
        "q": q_next,
        "z": z_next,
        "lambda": lambda_next,
        "residual": residual,
        "state": next_state,
    }


def affine_data(
    problem: dict[str, object], selector: sp.Matrix
) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
    """Return ``state_next=T state+c`` and ``q_next=C state+d`` exactly."""
    zero = sp.zeros(6, 1)
    base = relaxed_components(zero, problem, selector)
    state_columns: list[sp.Matrix] = []
    q_columns: list[sp.Matrix] = []
    for column in range(6):
        basis = sp.zeros(6, 1)
        basis[column] = 1
        update = relaxed_components(basis, problem, selector)
        state_columns.append(update["state"] - base["state"])
        q_columns.append(update["q"] - base["q"])
    return (
        sp.Matrix.hstack(*state_columns),
        base["state"],
        sp.Matrix.hstack(*q_columns),
        base["q"],
    )


def exact_discrete_lyapunov(matrix: sp.Matrix) -> sp.Matrix:
    """Solve ``H-matrix.T*H*matrix=I`` over the rationals."""
    variables = sp.symbols("h0:36")
    candidate = sp.Matrix(6, 6, variables)
    equations = list(candidate - matrix.T * candidate * matrix - sp.eye(6))
    solutions = sp.linsolve(equations, variables)
    solution = next(iter(solutions))
    if any(value.free_symbols for value in solution):
        raise RuntimeError("discrete Lyapunov equation did not have a unique solution")
    return sp.Matrix(6, 6, solution)


def leading_principal_minors(matrix: sp.Matrix) -> list[sp.Expr]:
    """Return exact Sylvester minors for a symmetric matrix."""
    return [sp.factor(matrix[:size, :size].det()) for size in range(1, 7)]


def canonical_hash(matrix: sp.Matrix) -> str:
    """Hash an exact matrix using canonical rational strings."""
    payload = ";".join(str(value) for value in matrix)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def fixed_decimal(value: sp.Expr, places: int = 20) -> str:
    """Render an exact value in fixed notation for human-facing summaries."""
    return format(sp.N(value, places + 20), f".{places}f")


def stringify_matrix(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(matrix[row, col]) for col in range(matrix.cols)] for row in range(matrix.rows)]


def build_certificate() -> dict[str, object]:
    """Construct and check every proof obligation for the fixed theorem."""
    verifier = load_exact_verifier()
    problem = verifier.build_problem()
    initial, _ = verifier.solve_period_equation(problem)
    kkt_state = (
        problem["y_star"]
        .col_join(problem["z_star"])
        .col_join(problem["lambda_star"])
    )

    branch_matrix, branch_offset, q_matrix, q_offset = affine_data(
        problem, SELECTOR_01
    )
    kkt_update = relaxed_components(kkt_state, problem, None)
    q_star = kkt_update["q"]

    lyapunov = exact_discrete_lyapunov(branch_matrix)
    minors = leading_principal_minors(lyapunov)
    lyapunov_identity = sp.simplify(
        lyapunov - branch_matrix.T * lyapunov * branch_matrix
    )

    # q_next-q_star = C(state-state_star).  If V=e^T H e is below alpha,
    # the H-metric Cauchy--Schwarz inequality preserves both strict signs of
    # q_star=(-1,1), so the next true projection uses branch 01.
    inverse_lyapunov = lyapunov.inv()
    sign_margins = [abs(q_star[index]) for index in range(2)]
    row_denominators = [
        sp.factor((q_matrix.row(index) * inverse_lyapunov * q_matrix.row(index).T)[0])
        for index in range(2)
    ]
    alpha_candidates = [
        sp.factor(sign_margins[index] ** 2 / row_denominators[index])
        for index in range(2)
    ]
    alpha = min(alpha_candidates)

    # Replay the true positive-part projection exactly until the state enters
    # the invariant ellipsoid.  No selector or mask is supplied here.
    state = initial
    masks: list[str] = []
    entry_step: int | None = None
    entry_value: sp.Expr | None = None
    entry_state: sp.Matrix | None = None
    for step in range(1, 401):
        update = relaxed_components(state, problem, None)
        masks.append(mask(update["q"]))
        state = update["state"]
        error = state - kkt_state
        value = sp.factor((error.T * lyapunov * error)[0])
        if entry_step is None and value < alpha:
            entry_step = step
            entry_value = value
            entry_state = state
            break

    if entry_step is None or entry_value is None or entry_state is None:
        raise RuntimeError("the exact prefix did not enter the invariant ellipsoid")

    trace_bound = sp.factor(sp.trace(lyapunov))
    contraction_factor = sp.factor(1 - 1 / trace_bound)
    checks = {
        "all_problem_and_initial_data_are_rational": all(
            value.is_Rational is True
            for matrix in [
                problem["Q1"],
                problem["Q2"],
                problem["rhs"],
                initial,
                branch_matrix,
                branch_offset,
                q_matrix,
                q_offset,
                lyapunov,
                entry_state,
            ]
            for value in matrix
        ),
        "unique_kkt_point_is_fixed_by_relaxed_update": (
            kkt_update["state"] == kkt_state
            and kkt_update["residual"] == sp.zeros(2, 1)
            and q_star == sp.Matrix([-1, 1])
        ),
        "branch_error_map_is_exact": (
            branch_matrix * kkt_state + branch_offset == kkt_state
            and q_matrix * kkt_state + q_offset == q_star
        ),
        "lyapunov_matrix_is_symmetric": lyapunov == lyapunov.T,
        "lyapunov_matrix_is_positive_definite": all(value > 0 for value in minors),
        "exact_lyapunov_identity": lyapunov_identity == sp.eye(6),
        "projection_safe_ellipsoid_has_positive_radius": (
            all(value > 0 for value in row_denominators)
            and all(value > 0 for value in alpha_candidates)
            and alpha > 0
        ),
        "true_projection_prefix_has_expected_masks": (
            masks[:2] == ["00", "00"]
            and all(value == "01" for value in masks[2:])
        ),
        "exact_prefix_enters_invariant_ellipsoid_at_step_208": (
            entry_step == 208 and entry_value < alpha
        ),
        "geometric_contraction_factor_is_strictly_between_zero_and_one": (
            0 < contraction_factor < 1
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "status": "proof_grade_exact_certificate_checked_by_codex",
        "valid": all(checks.values()),
        "theorem_scope": {
            "problem": "strict rational 66-cycle QP",
            "initial_point": "the exact period-66 initial point",
            "dual_step_tau": str(TAU),
            "claim": "the relaxed full-state ADMM converges to the unique KKT point",
            "not_claimed": [
                "convergence from every initial point for this QP",
                "convergence for every identity-slack strongly convex QP",
                "an exact characterization of all stable tau values",
            ],
        },
        "checks": checks,
        "exact_data": {
            "branch": "01",
            "branch_matrix": stringify_matrix(branch_matrix),
            "lyapunov_matrix": stringify_matrix(lyapunov),
            "q_error_matrix": stringify_matrix(q_matrix),
            "q_star": [str(value) for value in q_star],
            "leading_principal_minors": [str(value) for value in minors],
            "ellipsoid_alpha": str(alpha),
            "entry_step": entry_step,
            "entry_lyapunov_value": str(entry_value),
            "trace_bound": str(trace_bound),
            "geometric_contraction_factor": str(contraction_factor),
        },
        "display": {
            "ellipsoid_alpha": fixed_decimal(alpha),
            "entry_lyapunov_value": fixed_decimal(entry_value),
            "entry_ratio": fixed_decimal(entry_value / alpha),
            "geometric_contraction_factor": fixed_decimal(contraction_factor),
            "prefix_masks": f"00, 00, then 01 through step {entry_step}",
        },
        "hashes": {
            "branch_matrix_sha256": canonical_hash(branch_matrix),
            "lyapunov_matrix_sha256": canonical_hash(lyapunov),
            "entry_state_sha256": canonical_hash(entry_state),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    certificate = build_certificate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(certificate, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "valid": certificate["valid"],
        "entry_step": certificate["exact_data"]["entry_step"],
        "ellipsoid_alpha": certificate["display"]["ellipsoid_alpha"],
        "entry_ratio": certificate["display"]["entry_ratio"],
        "output": str(args.output),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
