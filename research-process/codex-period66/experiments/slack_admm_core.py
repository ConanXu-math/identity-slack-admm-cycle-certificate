from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SlackQpProblem:
    q1: np.ndarray
    q2: np.ndarray
    a: np.ndarray
    bmat: np.ndarray
    rhs: np.ndarray
    beta: float


@dataclass(frozen=True)
class AdmmState:
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    lam: np.ndarray


@dataclass(frozen=True)
class AdmmRunResult:
    final_state: AdmmState
    iterations: int
    residual_norms: list[float]
    step_norms: list[float]
    tol: float


def project_nonnegative(v: np.ndarray) -> np.ndarray:
    return np.maximum(v, 0.0)


def slack_admm_step(state: AdmmState, problem: SlackQpProblem) -> AdmmState:
    beta = problem.beta

    x_shift = problem.bmat @ state.y + state.z - problem.rhs
    x_matrix = problem.q1 + beta * (problem.a.T @ problem.a)
    x_rhs = problem.a.T @ state.lam - beta * (problem.a.T @ x_shift)
    x_next = _solve_psd_system(x_matrix, x_rhs)

    y_shift = problem.a @ x_next + state.z - problem.rhs
    y_matrix = problem.q2 + beta * (problem.bmat.T @ problem.bmat)
    y_rhs = problem.bmat.T @ state.lam - beta * (problem.bmat.T @ y_shift)
    y_next = _solve_psd_system(y_matrix, y_rhs)

    z_argument = problem.rhs - problem.a @ x_next - problem.bmat @ y_next + state.lam / beta
    z_next = project_nonnegative(z_argument)

    residual = problem.a @ x_next + problem.bmat @ y_next + z_next - problem.rhs
    lam_next = state.lam - beta * residual

    return AdmmState(x=x_next, y=y_next, z=z_next, lam=lam_next)


def run_slack_admm(
    problem: SlackQpProblem,
    initial_state: AdmmState,
    max_iter: int,
    tol: float,
) -> AdmmRunResult:
    state = initial_state
    residual_norms: list[float] = []
    step_norms: list[float] = []

    for iteration in range(1, max_iter + 1):
        next_state = slack_admm_step(state, problem)
        residual = problem.a @ next_state.x + problem.bmat @ next_state.y + next_state.z - problem.rhs
        step = _pack_state(next_state) - _pack_state(state)

        residual_norms.append(float(np.linalg.norm(residual)))
        step_norms.append(float(np.linalg.norm(step)))
        state = next_state

        if residual_norms[-1] < tol and step_norms[-1] < tol:
            return AdmmRunResult(
                final_state=state,
                iterations=iteration,
                residual_norms=residual_norms,
                step_norms=step_norms,
                tol=tol,
            )

    return AdmmRunResult(
        final_state=state,
        iterations=max_iter,
        residual_norms=residual_norms,
        step_norms=step_norms,
        tol=tol,
    )


def generate_random_problem(
    seed: int,
    dim_x: int,
    dim_y: int,
    dim_m: int,
    beta: float,
) -> SlackQpProblem:
    rng = np.random.default_rng(seed)
    q1 = _random_psd(rng, dim_x)
    q2 = _random_psd(rng, dim_y)
    a = rng.normal(scale=0.7, size=(dim_m, dim_x))
    bmat = rng.normal(scale=0.7, size=(dim_m, dim_y))

    feasible_x = rng.normal(size=dim_x)
    feasible_y = rng.normal(size=dim_y)
    feasible_z = rng.uniform(0.1, 1.0, size=dim_m)
    rhs = a @ feasible_x + bmat @ feasible_y + feasible_z

    return SlackQpProblem(q1=q1, q2=q2, a=a, bmat=bmat, rhs=rhs, beta=beta)


def classify_run(result: AdmmRunResult) -> str:
    if not result.residual_norms or not result.step_norms:
        return "stagnated"

    last_residual = result.residual_norms[-1]
    last_step = result.step_norms[-1]
    if last_residual < result.tol and last_step < result.tol:
        return "converged"

    all_values = np.array(result.residual_norms + result.step_norms, dtype=float)
    if not np.all(np.isfinite(all_values)):
        return "suspect_unstable"

    first_scale = max(result.residual_norms[0], result.step_norms[0], result.tol)
    if max(last_residual, last_step) > 100.0 * first_scale:
        return "suspect_unstable"
    if np.linalg.norm(_pack_state(result.final_state)) > 1.0e6:
        return "suspect_unstable"

    return "stagnated"


def estimate_active_set_spectral_radius(problem: SlackQpProblem, state: AdmmState) -> float:
    base = _pack_state(state)
    if base.size == 0:
        return 0.0

    epsilon = 1.0e-6
    jacobian = np.zeros((base.size, base.size))
    for column in range(base.size):
        perturbation = np.zeros_like(base)
        perturbation[column] = epsilon
        plus = _pack_state(slack_admm_step(_unpack_state(base + perturbation, problem), problem))
        minus = _pack_state(slack_admm_step(_unpack_state(base - perturbation, problem), problem))
        jacobian[:, column] = (plus - minus) / (2.0 * epsilon)

    eigenvalues = np.linalg.eigvals(jacobian)
    return float(np.max(np.abs(eigenvalues)))


def initial_zero_state(problem: SlackQpProblem) -> AdmmState:
    return AdmmState(
        x=np.zeros(problem.q1.shape[0]),
        y=np.zeros(problem.q2.shape[0]),
        z=np.zeros(problem.rhs.shape[0]),
        lam=np.zeros(problem.rhs.shape[0]),
    )


def result_to_dict(result: AdmmRunResult) -> dict[str, object]:
    return {
        "classification": classify_run(result),
        "iterations": result.iterations,
        "last_residual_norm": result.residual_norms[-1] if result.residual_norms else None,
        "last_step_norm": result.step_norms[-1] if result.step_norms else None,
        "residual_norms": result.residual_norms,
        "step_norms": result.step_norms,
        "final_state": {
            "x": result.final_state.x.tolist(),
            "y": result.final_state.y.tolist(),
            "z": result.final_state.z.tolist(),
            "lambda": result.final_state.lam.tolist(),
        },
    }


def problem_to_dict(problem: SlackQpProblem) -> dict[str, object]:
    return {
        "q1": problem.q1.tolist(),
        "q2": problem.q2.tolist(),
        "a": problem.a.tolist(),
        "bmat": problem.bmat.tolist(),
        "rhs": problem.rhs.tolist(),
        "beta": problem.beta,
    }


def _solve_psd_system(matrix: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    try:
        return np.linalg.solve(matrix, rhs)
    except np.linalg.LinAlgError:
        ridge = 1.0e-9 * np.eye(matrix.shape[0])
        return np.linalg.solve(matrix + ridge, rhs)


def _random_psd(rng: np.random.Generator, dim: int) -> np.ndarray:
    raw = rng.normal(size=(dim, dim))
    return raw.T @ raw + 1.0e-2 * np.eye(dim)


def _pack_state(state: AdmmState) -> np.ndarray:
    return np.concatenate([state.x, state.y, state.z, state.lam])


def _unpack_state(values: np.ndarray, problem: SlackQpProblem) -> AdmmState:
    dim_x = problem.q1.shape[0]
    dim_y = problem.q2.shape[0]
    dim_m = problem.rhs.shape[0]

    x_end = dim_x
    y_end = x_end + dim_y
    z_end = y_end + dim_m
    lam_end = z_end + dim_m

    return AdmmState(
        x=values[:x_end].copy(),
        y=values[x_end:y_end].copy(),
        z=values[y_end:z_end].copy(),
        lam=values[z_end:lam_end].copy(),
    )
