"""Fail-closed exact verifier for the rational period-23 QP.

The verifier reads only the repository-contained JSON instance.  It does not
read the archived Kimi NPZ and does not import either of the earlier period-23
verification/search scripts.  Every proof-grade check uses fractions.Fraction;
NumPy is used only for the explicitly non-proof spectral-radius display.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

import numpy as np

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = (
    REPO_ROOT
    / "certificates"
    / "period23_instance.json"
)
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "certificates"
    / "period23_certificate.json"
)

DIMENSION = 3
REDUCED_DIMENSION = 2 * DIMENSION
F0 = Fraction(0)
F1 = Fraction(1)

# One means t_i > 0, hence z_i=t_i and lambda_i=0.
W23 = (
    ((1, 0, 1),) * 5
    + ((0, 1, 1),) * 7
    + ((0, 0, 1),) * 2
    + ((0, 0, 0),)
    + ((0, 0, 1),) * 8
)

P_NUMERATOR = (
    (2, 0, 0, 0, -1, 1),
    (0, 2, 1, 0, -2, 2),
    (0, 1, 6, 2, -7, 7),
    (0, 0, 2, 3, -3, 3),
    (-1, -2, -7, -3, 16, -13),
    (1, 2, 7, 3, -13, 14),
)

Matrix = list[list[Fraction]]
Vector = list[Fraction]


EXACT_CHECK_NAMES = (
    "input_schema_matches",
    "instance_id_matches",
    "dimension_is_3",
    "beta_is_1",
    "input_entry_count_is_45",
    "all_input_entries_have_numerator_and_denominator_at_most_100",
    "F_is_symmetric",
    "F_is_positive_definite",
    "G_is_symmetric",
    "G_is_positive_definite",
    "A_is_nonsingular",
    "B_is_nonsingular",
    "I_minus_Mper_is_nonsingular",
    "periodic_fixed_point_is_exact",
    "phase_zero_projection_identity_holds",
    "phase_zero_mask_is_101",
    "original_admm_update_equations_hold",
    "exact_replay_closes_after_23_steps",
    "full_state_closes_after_23_steps",
    "realized_word_matches_W23",
    "phase_state_count_is_23",
    "phase_states_are_pairwise_distinct",
    "minimal_period_is_23",
    "full_state_minimal_period_is_23",
    "projection_margin_exceeds_1_over_250",
    "kkt_linear_system_is_nonsingular",
    "kkt_stationarity_holds",
    "kkt_primal_feasibility_holds",
    "kkt_complementarity_holds",
    "kkt_is_strictly_complementary",
    "kkt_point_is_unique",
    "no_phase_state_is_the_kkt_point",
    "P_is_symmetric",
    "P_is_positive_definite",
    "lyapunov_gap_is_symmetric",
    "lyapunov_gap_is_positive_definite",
    "support_ratio_count_is_69",
    "support_quadratic_forms_are_positive",
    "all_support_ratios_exceed_1_over_4000",
    "all_support_ratios_exceed_29_over_100000",
)


def fraction_text(value: Fraction) -> str:
    return str(value)


def rounded_numerical_display(value: float, digits: int = 12) -> float:
    """Normalize display-only floating output across linear-algebra backends."""
    rounded = round(float(value), digits)
    return 0.0 if abs(rounded) < 10.0 ** (-digits) else rounded


def decimal_text(value: Fraction, digits: int = 12) -> str:
    """Return a deterministic, human-readable significant-digit display."""
    with localcontext() as context:
        context.prec = digits + 4
        decimal_value = Decimal(value.numerator) / Decimal(value.denominator)
        return format(decimal_value, f".{digits}g")


def vector_text(vector: Sequence[Fraction]) -> list[str]:
    return [fraction_text(value) for value in vector]


def vector_decimal_text(vector: Sequence[Fraction]) -> list[str]:
    return [decimal_text(value) for value in vector]


def matrix_text(matrix: Sequence[Sequence[Fraction]]) -> list[list[str]]:
    return [vector_text(row) for row in matrix]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_text(payload: str) -> str:
    return sha256_bytes(payload.encode("utf-8"))


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def parse_canonical_fraction(value: Any, location: str) -> Fraction:
    if not isinstance(value, str):
        raise ValueError(f"{location} must be a canonical fraction string")
    if value != value.strip():
        raise ValueError(f"{location} contains surrounding whitespace")
    try:
        parsed = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{location} is not a valid rational: {value!r}") from exc
    if value != fraction_text(parsed):
        raise ValueError(
            f"{location} must be in canonical lowest terms; "
            f"received {value!r}, canonical form is {fraction_text(parsed)!r}"
        )
    return parsed


def parse_matrix(data: dict[str, Any], key: str, size: int) -> Matrix:
    raw = data.get(key)
    if not isinstance(raw, list) or len(raw) != size:
        raise ValueError(f"{key} must be a {size}x{size} array")
    matrix: Matrix = []
    for i, raw_row in enumerate(raw):
        if not isinstance(raw_row, list) or len(raw_row) != size:
            raise ValueError(f"{key}[{i}] must contain exactly {size} entries")
        matrix.append(
            [
                parse_canonical_fraction(value, f"{key}[{i}][{j}]")
                for j, value in enumerate(raw_row)
            ]
        )
    return matrix


def parse_vector(data: dict[str, Any], key: str, size: int) -> Vector:
    raw = data.get(key)
    if not isinstance(raw, list) or len(raw) != size:
        raise ValueError(f"{key} must contain exactly {size} entries")
    return [
        parse_canonical_fraction(value, f"{key}[{i}]")
        for i, value in enumerate(raw)
    ]


def zero_matrix(rows: int, columns: int) -> Matrix:
    return [[F0 for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    return [
        [F1 if i == j else F0 for j in range(size)]
        for i in range(size)
    ]


def transpose(matrix: Sequence[Sequence[Fraction]]) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matrix_add(
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
) -> Matrix:
    return [
        [left[i][j] + right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def matrix_subtract(
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
) -> Matrix:
    return [
        [left[i][j] - right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def matrix_multiply(
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
) -> Matrix:
    return [
        [
            sum(
                (
                    left[i][k] * right[k][j]
                    for k in range(len(right))
                ),
                F0,
            )
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def matrix_vector(
    matrix: Sequence[Sequence[Fraction]],
    vector: Sequence[Fraction],
) -> Vector:
    return [
        sum(
            (matrix[i][j] * vector[j] for j in range(len(vector))),
            F0,
        )
        for i in range(len(matrix))
    ]


def vector_add(left: Sequence[Fraction], right: Sequence[Fraction]) -> Vector:
    return [a + b for a, b in zip(left, right)]


def vector_subtract(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
) -> Vector:
    return [a - b for a, b in zip(left, right)]


def solve_columns(
    matrix: Sequence[Sequence[Fraction]],
    right_hand_sides: Sequence[Sequence[Fraction]],
) -> list[Vector]:
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("exact solve requires a nonempty square matrix")
    if any(len(column) != size for column in right_hand_sides):
        raise ValueError("exact solve received an incompatible right-hand side")

    augmented = [
        list(matrix[i]) + [column[i] for column in right_hand_sides]
        for i in range(size)
    ]
    width = size + len(right_hand_sides)

    for column in range(size):
        pivot = next(
            (
                row
                for row in range(column, size)
                if augmented[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            raise ValueError("singular exact linear system")
        augmented[column], augmented[pivot] = (
            augmented[pivot],
            augmented[column],
        )
        pivot_value = augmented[column][column]
        augmented[column] = [
            value / pivot_value for value in augmented[column]
        ]
        for row in range(size):
            if row == column or augmented[row][column] == 0:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                augmented[row][j] - factor * augmented[column][j]
                for j in range(width)
            ]

    return [
        [augmented[i][size + rhs] for i in range(size)]
        for rhs in range(len(right_hand_sides))
    ]


def solve_vector(
    matrix: Sequence[Sequence[Fraction]],
    right_hand_side: Sequence[Fraction],
) -> Vector:
    return solve_columns(matrix, [right_hand_side])[0]


def inverse(matrix: Sequence[Sequence[Fraction]]) -> Matrix:
    return transpose(
        solve_columns(
            matrix,
            [
                [F1 if i == j else F0 for i in range(len(matrix))]
                for j in range(len(matrix))
            ],
        )
    )


def determinant(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("determinant requires a nonempty square matrix")
    work = [list(row) for row in matrix]
    result = F1
    for column in range(size):
        pivot = next(
            (
                row
                for row in range(column, size)
                if work[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            return F0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, size):
            if work[row][column] == 0:
                continue
            factor = work[row][column] / pivot_value
            for j in range(column, size):
                work[row][j] -= factor * work[column][j]
    return result


def leading_principal_minors(
    matrix: Sequence[Sequence[Fraction]],
) -> list[Fraction]:
    return [
        determinant([list(row[:size]) for row in matrix[:size]])
        for size in range(1, len(matrix) + 1)
    ]


def is_symmetric(matrix: Sequence[Sequence[Fraction]]) -> bool:
    return list(map(list, matrix)) == transpose(matrix)


def positive_definite_data(
    matrix: Sequence[Sequence[Fraction]],
) -> tuple[bool, list[Fraction]]:
    minors = leading_principal_minors(matrix)
    return is_symmetric(matrix) and all(value > 0 for value in minors), minors


def quadratic_row(
    row: Sequence[Fraction],
    matrix: Sequence[Sequence[Fraction]],
) -> Fraction:
    image = matrix_vector(matrix, row)
    return sum((a * b for a, b in zip(row, image)), F0)


def canonical_vector_digest(vector: Sequence[Fraction]) -> str:
    return sha256_text("|".join(fraction_text(value) for value in vector))


def canonical_matrix_digest(
    matrix: Sequence[Sequence[Fraction]],
) -> str:
    return sha256_text(
        "|".join(
            fraction_text(value)
            for row in matrix
            for value in row
        )
    )


def verify_instance(input_path: Path) -> dict[str, Any]:
    raw_input = input_path.read_bytes()
    input_sha256 = sha256_bytes(raw_input)
    try:
        data = json.loads(raw_input.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("input must be valid UTF-8 JSON") from exc
    if not isinstance(data, dict):
        raise ValueError("input JSON must contain an object")

    schema = data.get("schema")
    instance_id = data.get("instance_id")
    dimension = data.get("dimension")
    beta = parse_canonical_fraction(data.get("beta"), "beta")
    matrix_a = parse_matrix(data, "A", DIMENSION)
    matrix_b = parse_matrix(data, "B", DIMENSION)
    matrix_f = parse_matrix(data, "F", DIMENSION)
    matrix_g = parse_matrix(data, "G", DIMENSION)
    vector_b = parse_vector(data, "b", DIMENSION)
    vector_c1 = parse_vector(data, "c1", DIMENSION)
    vector_c2 = parse_vector(data, "c2", DIMENSION)

    input_entries = [
        value
        for matrix in (matrix_a, matrix_b, matrix_f, matrix_g)
        for row in matrix
        for value in row
    ] + vector_b + vector_c1 + vector_c2

    f_positive, f_minors = positive_definite_data(matrix_f)
    g_positive, g_minors = positive_definite_data(matrix_g)
    determinant_a = determinant(matrix_a)
    determinant_b = determinant(matrix_b)

    transpose_a = transpose(matrix_a)
    transpose_b = transpose(matrix_b)
    hessian_x = matrix_add(
        matrix_f,
        matrix_multiply(transpose_a, matrix_a),
    )
    hessian_y = matrix_add(
        matrix_g,
        matrix_multiply(transpose_b, matrix_b),
    )

    def step_from_y_z_lambda(
        y: Sequence[Fraction],
        z: Sequence[Fraction],
        lam: Sequence[Fraction],
    ) -> tuple[Vector, Vector, Vector, Vector, Vector, dict[str, bool]]:
        x_rhs = vector_subtract(
            matrix_vector(
                transpose_a,
                vector_subtract(
                    vector_add(vector_b, lam),
                    vector_add(matrix_vector(matrix_b, y), z),
                ),
            ),
            vector_c1,
        )
        x_new = solve_vector(hessian_x, x_rhs)

        y_rhs = vector_subtract(
            matrix_vector(
                transpose_b,
                vector_subtract(
                    vector_add(vector_b, lam),
                    vector_add(matrix_vector(matrix_a, x_new), z),
                ),
            ),
            vector_c2,
        )
        y_new = solve_vector(hessian_y, y_rhs)

        q = vector_subtract(
            vector_add(vector_b, lam),
            vector_add(
                matrix_vector(matrix_a, x_new),
                matrix_vector(matrix_b, y_new),
            ),
        )
        z_new = [value if value > 0 else F0 for value in q]
        lambda_projection = [
            q[i] - z_new[i] for i in range(DIMENSION)
        ]
        residual = vector_subtract(
            vector_add(
                vector_add(
                    matrix_vector(matrix_a, x_new),
                    matrix_vector(matrix_b, y_new),
                ),
                z_new,
            ),
            vector_b,
        )
        lambda_multiplier = vector_subtract(lam, residual)

        x_old_y_residual = vector_subtract(
            vector_add(
                vector_add(
                    matrix_vector(matrix_a, x_new),
                    matrix_vector(matrix_b, y),
                ),
                z,
            ),
            vector_b,
        )
        y_old_z_residual = vector_subtract(
            vector_add(
                vector_add(
                    matrix_vector(matrix_a, x_new),
                    matrix_vector(matrix_b, y_new),
                ),
                z,
            ),
            vector_b,
        )
        x_stationarity = vector_add(
            vector_subtract(
                vector_add(
                    matrix_vector(matrix_f, x_new),
                    vector_c1,
                ),
                matrix_vector(transpose_a, lam),
            ),
            matrix_vector(transpose_a, x_old_y_residual),
        )
        y_stationarity = vector_add(
            vector_subtract(
                vector_add(
                    matrix_vector(matrix_g, y_new),
                    vector_c2,
                ),
                matrix_vector(transpose_b, lam),
            ),
            matrix_vector(transpose_b, y_old_z_residual),
        )
        update_checks = {
            "x_subproblem_stationarity": all(
                value == 0 for value in x_stationarity
            ),
            "y_subproblem_stationarity": all(
                value == 0 for value in y_stationarity
            ),
            "z_is_exact_orthant_projection": all(
                z_new[i] == (q[i] if q[i] > 0 else F0)
                for i in range(DIMENSION)
            ),
            "multiplier_update_matches_projection_identity": (
                lambda_projection == lambda_multiplier
            ),
        }
        return (
            x_new,
            y_new,
            z_new,
            lambda_multiplier,
            q,
            update_checks,
        )

    def fixed_source_reduced_step(
        state: Sequence[Fraction],
        mask: Sequence[int],
    ) -> Vector:
        y = list(state[:DIMENSION])
        t = list(state[DIMENSION:])
        z = [t[i] if mask[i] else F0 for i in range(DIMENSION)]
        lam = [F0 if mask[i] else t[i] for i in range(DIMENSION)]
        _, y_new, _, _, q, _ = step_from_y_z_lambda(y, z, lam)
        return y_new + q

    def branch_map(mask: Sequence[int]) -> tuple[Matrix, Vector]:
        zero = [F0] * REDUCED_DIMENSION
        offset = fixed_source_reduced_step(zero, mask)
        columns: list[Vector] = []
        for coordinate in range(REDUCED_DIMENSION):
            basis = zero[:]
            basis[coordinate] = F1
            image = fixed_source_reduced_step(basis, mask)
            columns.append(vector_subtract(image, offset))
        return transpose(columns), offset

    return_matrix = identity(REDUCED_DIMENSION)
    return_offset = [F0] * REDUCED_DIMENSION
    partial_linear_maps: list[Matrix] = []
    for mask in W23:
        partial_linear_maps.append([row[:] for row in return_matrix])
        branch_matrix, branch_offset = branch_map(mask)
        return_matrix = matrix_multiply(branch_matrix, return_matrix)
        return_offset = vector_add(
            matrix_vector(branch_matrix, return_offset),
            branch_offset,
        )

    identity_six = identity(REDUCED_DIMENSION)
    identity_minus_return = matrix_subtract(
        identity_six,
        return_matrix,
    )
    determinant_identity_minus_return = determinant(identity_minus_return)
    if determinant_identity_minus_return == 0:
        raise ValueError("I-M_per is singular; the periodic fixed point is not unique")
    phase_zero = solve_vector(identity_minus_return, return_offset)
    fixed_point_exact = vector_add(
        matrix_vector(return_matrix, phase_zero),
        return_offset,
    ) == phase_zero

    states: list[Vector] = []
    realized_word: list[tuple[int, int, int]] = []
    update_checks: list[bool] = []
    x_updates: list[Vector] = []
    projection_margins: list[tuple[Fraction, int, int]] = []
    state = phase_zero[:]
    for phase in range(len(W23)):
        states.append(state[:])
        t = state[DIMENSION:]
        realized_word.append(
            tuple(1 if value > 0 else 0 for value in t)
        )
        projection_margins.extend(
            (abs(t[coordinate]), phase, coordinate + 1)
            for coordinate in range(DIMENSION)
        )

        y = state[:DIMENSION]
        z = [value if value > 0 else F0 for value in t]
        lam = [value if value < 0 else F0 for value in t]
        x_new, y_new, _, _, q, checks_for_step = step_from_y_z_lambda(
            y,
            z,
            lam,
        )
        x_updates.append(x_new)
        update_checks.append(all(checks_for_step.values()))
        state = y_new + q

    phase_zero_y = phase_zero[:DIMENSION]
    phase_zero_t = phase_zero[DIMENSION:]
    phase_zero_z = [
        value if value > 0 else F0 for value in phase_zero_t
    ]
    phase_zero_lambda = [
        value if value < 0 else F0 for value in phase_zero_t
    ]
    # The final transition maps phase 22 back to phase 0.  Its x-update is
    # therefore the x-coordinate paired with the phase-zero (y,z,lambda)
    # state, making the displayed full initialization exactly 23-periodic.
    phase_zero_x = x_updates[-1]
    phase_zero_mask = tuple(
        1 if value > 0 else 0 for value in phase_zero_t
    )
    phase_zero_projection_identity = (
        vector_add(phase_zero_z, phase_zero_lambda) == phase_zero_t
        and phase_zero_z
        == [value if value > 0 else F0 for value in phase_zero_t]
        and phase_zero_lambda
        == [value if value < 0 else F0 for value in phase_zero_t]
    )

    def full_state(
        x_value: Sequence[Fraction],
        reduced_state: Sequence[Fraction],
    ) -> Vector:
        y_value = list(reduced_state[:DIMENSION])
        t_value = list(reduced_state[DIMENSION:])
        z_value = [value if value > 0 else F0 for value in t_value]
        lambda_value = [
            value if value < 0 else F0 for value in t_value
        ]
        return list(x_value) + y_value + z_value + lambda_value

    full_phase_states = [
        full_state(
            x_updates[phase - 1] if phase > 0 else x_updates[-1],
            states[phase],
        )
        for phase in range(len(states))
    ]
    final_full_state = full_state(x_updates[-1], state)
    full_state_closes = final_full_state == full_phase_states[0]
    full_states_distinct = (
        len({tuple(value) for value in full_phase_states}) == len(W23)
    )

    minimum_margin, margin_phase, margin_coordinate = min(
        projection_margins,
        key=lambda item: item[0],
    )
    replay_closes = state == phase_zero
    states_distinct = len({tuple(value) for value in states}) == len(W23)

    # Active set at the unique KKT point:
    # z_1=z_2=0, lambda_3=0.  The solved signs are checked below.
    kkt_size = 3 * DIMENSION
    kkt_matrix = zero_matrix(kkt_size, kkt_size)
    kkt_rhs = [F0] * kkt_size
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            kkt_matrix[i][j] = matrix_f[i][j]
            kkt_matrix[DIMENSION + i][DIMENSION + j] = matrix_g[i][j]
            kkt_matrix[2 * DIMENSION + i][j] = matrix_a[i][j]
            kkt_matrix[2 * DIMENSION + i][DIMENSION + j] = matrix_b[i][j]
        for active_coordinate in range(2):
            kkt_matrix[i][2 * DIMENSION + active_coordinate] = (
                -transpose_a[i][active_coordinate]
            )
            kkt_matrix[DIMENSION + i][
                2 * DIMENSION + active_coordinate
            ] = -transpose_b[i][active_coordinate]
        kkt_rhs[i] = -vector_c1[i]
        kkt_rhs[DIMENSION + i] = -vector_c2[i]
        kkt_rhs[2 * DIMENSION + i] = vector_b[i]
    kkt_matrix[2 * DIMENSION + 2][2 * DIMENSION + 2] = F1

    kkt_determinant = determinant(kkt_matrix)
    if kkt_determinant == 0:
        raise ValueError("the exact active-set KKT system is singular")
    kkt_solution = solve_vector(kkt_matrix, kkt_rhs)
    kkt_x = kkt_solution[:DIMENSION]
    kkt_y = kkt_solution[DIMENSION : 2 * DIMENSION]
    kkt_lambda = [
        kkt_solution[2 * DIMENSION],
        kkt_solution[2 * DIMENSION + 1],
        F0,
    ]
    kkt_z = [F0, F0, kkt_solution[2 * DIMENSION + 2]]

    kkt_stationarity_x = vector_subtract(
        vector_add(matrix_vector(matrix_f, kkt_x), vector_c1),
        matrix_vector(transpose_a, kkt_lambda),
    )
    kkt_stationarity_y = vector_subtract(
        vector_add(matrix_vector(matrix_g, kkt_y), vector_c2),
        matrix_vector(transpose_b, kkt_lambda),
    )
    kkt_primal_residual = vector_subtract(
        vector_add(
            vector_add(
                matrix_vector(matrix_a, kkt_x),
                matrix_vector(matrix_b, kkt_y),
            ),
            kkt_z,
        ),
        vector_b,
    )
    kkt_stationarity = all(
        value == 0
        for value in kkt_stationarity_x + kkt_stationarity_y
    )
    kkt_feasibility = all(value == 0 for value in kkt_primal_residual)
    kkt_complementarity = (
        all(value >= 0 for value in kkt_z)
        and all(value <= 0 for value in kkt_lambda)
        and all(
            kkt_z[i] * kkt_lambda[i] == 0
            for i in range(DIMENSION)
        )
    )
    kkt_strict = all(
        (
            kkt_z[i] > 0
            and kkt_lambda[i] == 0
        )
        or (
            kkt_z[i] == 0
            and kkt_lambda[i] < 0
        )
        for i in range(DIMENSION)
    )
    kkt_reduced_state = kkt_y + vector_add(kkt_z, kkt_lambda)
    no_phase_is_kkt = all(
        state_value != kkt_reduced_state for state_value in states
    )

    matrix_p = [
        [Fraction(value, 2) for value in row]
        for row in P_NUMERATOR
    ]
    p_positive, p_minors = positive_definite_data(matrix_p)
    lyapunov_gap = matrix_subtract(
        matrix_p,
        matrix_multiply(
            transpose(return_matrix),
            matrix_multiply(matrix_p, return_matrix),
        ),
    )
    gap_positive, gap_minors = positive_definite_data(lyapunov_gap)

    inverse_p = inverse(matrix_p)
    support_ratios: list[tuple[Fraction, int, int]] = []
    support_forms_positive = True
    for phase, state_value in enumerate(states):
        for coordinate in range(DIMENSION):
            support_row = partial_linear_maps[phase][
                DIMENSION + coordinate
            ]
            support_form = quadratic_row(support_row, inverse_p)
            if support_form <= 0:
                support_forms_positive = False
                continue
            support_ratios.append(
                (
                    state_value[DIMENSION + coordinate] ** 2
                    / support_form,
                    phase,
                    coordinate + 1,
                )
            )

    if not support_ratios:
        raise ValueError("no positive support ratios were constructed")
    rbar2, rbar_phase, rbar_coordinate = min(
        support_ratios,
        key=lambda item: item[0],
    )

    float_return_matrix = np.array(
        [[float(value) for value in row] for row in return_matrix],
        dtype=float,
    )
    eigenvalues = np.linalg.eigvals(float_return_matrix)
    raw_spectral_radius = float(max(abs(value) for value in eigenvalues))
    if not math.isfinite(raw_spectral_radius):
        raise ValueError("numerical spectral-radius display is not finite")
    spectral_radius = rounded_numerical_display(raw_spectral_radius)
    display_eigenvalues = sorted(
        (
            {
                "real": rounded_numerical_display(value.real),
                "imag": rounded_numerical_display(value.imag),
            }
            for value in eigenvalues
        ),
        key=lambda value: (
            -(value["real"] ** 2 + value["imag"] ** 2),
            -value["real"],
            -value["imag"],
        ),
    )

    exact_checks = {
        "input_schema_matches": (
            schema == "identity_slack_p23_rational_instance_v1"
        ),
        "instance_id_matches": (
            instance_id == "identity_slack_p23_rational_v1"
        ),
        "dimension_is_3": dimension == DIMENSION,
        "beta_is_1": beta == F1,
        "input_entry_count_is_45": len(input_entries) == 45,
        "all_input_entries_have_numerator_and_denominator_at_most_100": all(
            abs(value.numerator) <= 100 and value.denominator <= 100
            for value in input_entries
        ),
        "F_is_symmetric": is_symmetric(matrix_f),
        "F_is_positive_definite": f_positive,
        "G_is_symmetric": is_symmetric(matrix_g),
        "G_is_positive_definite": g_positive,
        "A_is_nonsingular": determinant_a != 0,
        "B_is_nonsingular": determinant_b != 0,
        "I_minus_Mper_is_nonsingular": (
            determinant_identity_minus_return != 0
        ),
        "periodic_fixed_point_is_exact": fixed_point_exact,
        "phase_zero_projection_identity_holds": (
            phase_zero_projection_identity
        ),
        "phase_zero_mask_is_101": phase_zero_mask == W23[0],
        "original_admm_update_equations_hold": all(update_checks),
        "exact_replay_closes_after_23_steps": replay_closes,
        "full_state_closes_after_23_steps": full_state_closes,
        "realized_word_matches_W23": tuple(realized_word) == W23,
        "phase_state_count_is_23": len(states) == 23,
        "phase_states_are_pairwise_distinct": states_distinct,
        "minimal_period_is_23": replay_closes and states_distinct,
        "full_state_minimal_period_is_23": (
            full_state_closes and full_states_distinct
        ),
        "projection_margin_exceeds_1_over_250": (
            minimum_margin > Fraction(1, 250)
        ),
        "kkt_linear_system_is_nonsingular": kkt_determinant != 0,
        "kkt_stationarity_holds": kkt_stationarity,
        "kkt_primal_feasibility_holds": kkt_feasibility,
        "kkt_complementarity_holds": kkt_complementarity,
        "kkt_is_strictly_complementary": kkt_strict,
        "kkt_point_is_unique": (
            f_positive
            and g_positive
            and determinant_a != 0
            and kkt_stationarity
            and kkt_feasibility
            and kkt_complementarity
        ),
        "no_phase_state_is_the_kkt_point": no_phase_is_kkt,
        "P_is_symmetric": is_symmetric(matrix_p),
        "P_is_positive_definite": p_positive,
        "lyapunov_gap_is_symmetric": is_symmetric(lyapunov_gap),
        "lyapunov_gap_is_positive_definite": gap_positive,
        "support_ratio_count_is_69": len(support_ratios) == 69,
        "support_quadratic_forms_are_positive": support_forms_positive,
        "all_support_ratios_exceed_1_over_4000": all(
            ratio > Fraction(1, 4000)
            for ratio, _, _ in support_ratios
        ),
        "all_support_ratios_exceed_29_over_100000": all(
            ratio > Fraction(29, 100000)
            for ratio, _, _ in support_ratios
        ),
    }

    exact_check_set_matches = (
        tuple(exact_checks.keys()) == EXACT_CHECK_NAMES
    )
    all_exact_checks_pass = (
        exact_check_set_matches
        and all(exact_checks.get(name) is True for name in EXACT_CHECK_NAMES)
    )

    phase_state_hashes = [
        canonical_vector_digest(state_value) for state_value in states
    ]
    certificate = {
        "schema": "identity_slack_p23_rational_certificate_v1",
        "instance_id": instance_id,
        "verifier": {
            "path": repo_relative(Path(__file__)),
            "sha256": sha256_bytes(Path(__file__).read_bytes()),
            "arithmetic": "fractions.Fraction exact rational arithmetic",
            "external_npz_read": False,
            "imports_prior_period23_verifier_or_search": False,
        },
        "input": {
            "path": repo_relative(input_path),
            "sha256": input_sha256,
            "byte_size": len(raw_input),
            "schema": schema,
            "entry_count": len(input_entries),
            "maximum_absolute_numerator": max(
                abs(value.numerator) for value in input_entries
            ),
            "maximum_denominator": max(
                value.denominator for value in input_entries
            ),
        },
        "problem": {
            "dimension": dimension,
            "beta": fraction_text(beta),
            "word_masks": [list(mask) for mask in W23],
            "word_compact": "101^5 011^7 001^2 000 001^8",
        },
        "assumption_certificate": {
            "F_leading_principal_minors": vector_text(f_minors),
            "G_leading_principal_minors": vector_text(g_minors),
            "determinant_A": fraction_text(determinant_a),
            "determinant_B": fraction_text(determinant_b),
        },
        "return_map_certificate": {
            "determinant_I_minus_Mper": fraction_text(
                determinant_identity_minus_return
            ),
            "return_matrix_exact_sha256": canonical_matrix_digest(
                return_matrix
            ),
            "return_offset_exact_sha256": canonical_vector_digest(
                return_offset
            ),
            "phase_zero_exact_sha256": canonical_vector_digest(phase_zero),
        },
        "periodic_orbit_certificate": {
            "phase_state_count": len(states),
            "phase_state_exact_sha256": phase_state_hashes,
            "cycle_exact_sha256": sha256_text("|".join(phase_state_hashes)),
            "phase_zero_initialization": {
                "phase_convention": (
                    "state immediately after the z and multiplier updates; "
                    "x is the update produced on the phase-22 to phase-0 "
                    "transition"
                ),
                "reduced_coordinate_order": [
                    "y1",
                    "y2",
                    "y3",
                    "t1=z1+lambda1",
                    "t2=z2+lambda2",
                    "t3=z3+lambda3",
                ],
                "phase_zero_mask": list(phase_zero_mask),
                "exact": {
                    "x": vector_text(phase_zero_x),
                    "y": vector_text(phase_zero_y),
                    "z": vector_text(phase_zero_z),
                    "lambda_repo_sign_convention": vector_text(
                        phase_zero_lambda
                    ),
                    "t_z_plus_lambda": vector_text(phase_zero_t),
                },
                "decimal_display_only": {
                    "x": vector_decimal_text(phase_zero_x),
                    "y": vector_decimal_text(phase_zero_y),
                    "z": vector_decimal_text(phase_zero_z),
                    "lambda_repo_sign_convention": vector_decimal_text(
                        phase_zero_lambda
                    ),
                    "t_z_plus_lambda": vector_decimal_text(phase_zero_t),
                },
            },
            "realized_word_masks": [list(mask) for mask in realized_word],
            "minimum_projection_margin": {
                "exact": fraction_text(minimum_margin),
                "decimal": float(minimum_margin),
                "controlling_phase_zero_based": margin_phase,
                "controlling_coordinate_one_based": margin_coordinate,
                "certified_lower_bound": "1/250",
            },
        },
        "kkt_certificate": {
            "active_coordinates_one_based": [1, 2],
            "inactive_coordinates_one_based": [3],
            "linear_system_determinant": fraction_text(kkt_determinant),
            "x": vector_text(kkt_x),
            "y": vector_text(kkt_y),
            "z": vector_text(kkt_z),
            "lambda_repo_sign_convention": vector_text(kkt_lambda),
            "reduced_state_exact_sha256": canonical_vector_digest(
                kkt_reduced_state
            ),
        },
        "lyapunov_certificate": {
            "P": matrix_text(matrix_p),
            "P_leading_principal_minors": vector_text(p_minors),
            "P_minus_MtPM_leading_principal_minors": vector_text(
                gap_minors
            ),
        },
        "support_radius_certificate": {
            "support_ratio_count": len(support_ratios),
            "certified_radius_squared": "1/4000",
            "rbar2": {
                "exact": fraction_text(rbar2),
                "decimal": float(rbar2),
                "controlling_phase_zero_based": rbar_phase,
                "controlling_coordinate_one_based": rbar_coordinate,
            },
            "rbar2_gt_1_over_4000": rbar2 > Fraction(1, 4000),
            "rbar2_gt_29_over_100000": (
                rbar2 > Fraction(29, 100000)
            ),
        },
        "numerical_display_only": {
            "spectral_radius": spectral_radius,
            "eigenvalues": display_eigenvalues,
            "proof_status": (
                "informational floating-point display; excluded from the "
                "fail-closed exact-check aggregate"
            ),
        },
        "exact_checks": exact_checks,
        "aggregate": {
            "policy": (
                "fail_closed: valid is true only when the exact check set "
                "matches the verifier contract and every exact check is true"
            ),
            "expected_exact_checks": list(EXACT_CHECK_NAMES),
            "exact_check_set_matches_contract": exact_check_set_matches,
            "all_exact_checks_pass": all_exact_checks_pass,
            "valid": all_exact_checks_pass,
        },
        "valid": all_exact_checks_pass,
    }
    return certificate


def invalid_certificate(
    input_path: Path,
    error: Exception,
) -> dict[str, Any]:
    input_metadata: dict[str, Any] = {
        "path": repo_relative(input_path),
    }
    try:
        raw_input = input_path.read_bytes()
    except OSError:
        pass
    else:
        input_metadata.update(
            {
                "sha256": sha256_bytes(raw_input),
                "byte_size": len(raw_input),
            }
        )
    return {
        "schema": "identity_slack_p23_rational_certificate_v1",
        "instance_id": "identity_slack_p23_rational_v1",
        "verifier": {
            "path": repo_relative(Path(__file__)),
            "sha256": sha256_bytes(Path(__file__).read_bytes()),
            "arithmetic": "fractions.Fraction exact rational arithmetic",
            "external_npz_read": False,
            "imports_prior_period23_verifier_or_search": False,
        },
        "input": input_metadata,
        "error": {
            "type": type(error).__name__,
            "message": str(error),
        },
        "exact_checks": {},
        "aggregate": {
            "policy": (
                "fail_closed: any input, arithmetic, or verification error "
                "forces valid=false"
            ),
            "expected_exact_checks": list(EXACT_CHECK_NAMES),
            "exact_check_set_matches_contract": False,
            "all_exact_checks_pass": False,
            "valid": False,
        },
        "valid": False,
    }


def write_certificate(output_path: Path, certificate: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_name(output_path.name + ".tmp")
    temporary_path.write_text(
        json.dumps(certificate, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(output_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Verify the rational K3 period-23 QP using exact "
            "repository-contained rational data."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"instance JSON (default: {repo_relative(DEFAULT_INPUT)})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"certificate JSON (default: {repo_relative(DEFAULT_OUTPUT)})",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_path = args.input.resolve()
    output_path = args.output.resolve()

    if input_path == output_path:
        certificate = invalid_certificate(
            input_path,
            ValueError("input and output paths must be different"),
        )
    else:
        try:
            certificate = verify_instance(input_path)
        except Exception as exc:  # Fail closed and preserve machine evidence.
            certificate = invalid_certificate(input_path, exc)

    write_certificate(output_path, certificate)
    print(f"certificate: {output_path}")
    print(f"valid: {certificate['valid']}")
    if certificate["valid"]:
        margin = certificate["periodic_orbit_certificate"][
            "minimum_projection_margin"
        ]
        rbar2 = certificate["support_radius_certificate"]["rbar2"]
        spectral_radius = certificate["numerical_display_only"][
            "spectral_radius"
        ]
        print(
            "minimum projection margin: "
            f"{margin['decimal']:.16g} > {margin['certified_lower_bound']}"
        )
        print(
            "rbar^2: "
            f"{rbar2['decimal']:.16g} > "
            f"{certificate['support_radius_certificate']['certified_radius_squared']}"
        )
        print(
            "spectral radius (numerical display only): "
            f"{spectral_radius:.16g}"
        )
        return 0

    print(
        "verification failed closed: "
        f"{certificate.get('error', {}).get('message', 'an exact check failed')}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
