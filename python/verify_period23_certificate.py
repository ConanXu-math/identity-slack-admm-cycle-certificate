"""Verify the Kimi Code K3 period-23 ADMM certificate exactly.

The source instance is stored as NumPy binary64 arrays.  Every floating-point
entry is converted to ``Fraction(float(entry))`` before any mathematical
operation, so the replay proves a statement about the exact dyadic instance
encoded by the NPZ file rather than about a tolerance-based simulation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import numpy as np


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


HERE = Path(__file__).resolve().parent
CERTIFICATE_DIR = HERE.parent / "certificates"
DEFAULT_SOURCE = CERTIFICATE_DIR / "period23_source_binary64.npz"
DEFAULT_CERTIFICATE = CERTIFICATE_DIR / "period23_certificate.json"
DEFAULT_MANIFEST = CERTIFICATE_DIR / "period23_instance_manifest.json"

INSTANCE_ID = "identity_slack_p23_dyadic_v1"
EXPECTED_SOURCE_SHA256 = (
    "aa4309d424f599b66967dfae22ed9a61e36dd6b4c34f7cd197ae3d21c6e18a28"
)
UPSTREAM_VERIFIER_SHA256 = (
    "3866fa89c2747be95082e7817934b4128266e4f46178dfcde02cd52546aa3829"
)
DIMENSION = 3
KKT_MASK = 4
STRICT_MARGIN_LOWER_BOUND = Fraction(7, 1000)
KKT_CANDIDATE_TOLERANCE = Fraction(1, 10**12)

EXPECTED_ARRAYS = {
    "A": ((3, 3), "float64"),
    "B": ((3, 3), "float64"),
    "F": ((3, 3), "float64"),
    "G": ((3, 3), "float64"),
    "b": ((3,), "float64"),
    "c1": ((3,), "float64"),
    "c2": ((3,), "float64"),
    "lam": ((3,), "float64"),
    "per": ((23,), "int64"),
    "rho": ((), "float64"),
    "vfix": ((9,), "float64"),
    "xs": ((3,), "float64"),
    "ys": ((3,), "float64"),
    "z": ((3,), "float64"),
}

ExactMatrix = list[list[Fraction]]
ExactVector = list[Fraction]


def _stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def _canonical_json_hash(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _stable_json_bytes_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _fraction_vector(values: ExactVector) -> list[str]:
    return [_fraction_text(value) for value in values]


def _fraction_matrix(values: ExactMatrix) -> list[list[str]]:
    return [_fraction_vector(row) for row in values]


def _load_source(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as archive:
        arrays = {
            name: np.array(archive[name], copy=True)
            for name in archive.files
        }
    names = set(arrays)
    expected_names = set(EXPECTED_ARRAYS)
    if names != expected_names:
        missing = sorted(expected_names - names)
        extra = sorted(names - expected_names)
        raise ValueError(f"source array names differ: missing={missing}, extra={extra}")
    for name, (shape, dtype) in EXPECTED_ARRAYS.items():
        array = arrays[name]
        if tuple(array.shape) != shape or str(array.dtype) != dtype:
            raise ValueError(
                f"{name} has shape={array.shape}, dtype={array.dtype}; "
                f"expected shape={shape}, dtype={dtype}"
            )
    return arrays


def _to_exact_matrix(array: np.ndarray) -> ExactMatrix:
    return [
        [Fraction(float(entry)) for entry in row]
        for row in np.asarray(array)
    ]


def _to_exact_vector(array: np.ndarray) -> ExactVector:
    return [Fraction(float(entry)) for entry in np.asarray(array)]


def _transpose(matrix: ExactMatrix) -> ExactMatrix:
    return [list(row) for row in zip(*matrix)]


def _identity(size: int) -> ExactMatrix:
    return [
        [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]


def _matmul(left: ExactMatrix, right: ExactMatrix) -> ExactMatrix:
    return [
        [
            sum(
                left[row][index] * right[index][column]
                for index in range(len(right))
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def _matvec(matrix: ExactMatrix, vector: ExactVector) -> ExactVector:
    return [
        sum(
            matrix[row][column] * vector[column]
            for column in range(len(vector))
        )
        for row in range(len(matrix))
    ]


def _solve_exact(matrix: ExactMatrix, rhs: ExactVector) -> ExactVector:
    size = len(matrix)
    augmented = [
        row[:] + [rhs[row_index]]
        for row_index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = max(
            range(column, size),
            key=lambda row_index: abs(augmented[row_index][column]),
        )
        if augmented[pivot][column] == 0:
            raise ValueError("exact linear system is singular")
        augmented[column], augmented[pivot] = (
            augmented[pivot],
            augmented[column],
        )
        pivot_value = augmented[column][column]
        augmented[column] = [
            entry / pivot_value for entry in augmented[column]
        ]
        for row_index in range(size):
            if row_index == column or augmented[row_index][column] == 0:
                continue
            factor = augmented[row_index][column]
            augmented[row_index] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(
                    augmented[row_index],
                    augmented[column],
                )
            ]
    return [augmented[row_index][size] for row_index in range(size)]


def _det_exact(matrix: ExactMatrix) -> Fraction:
    size = len(matrix)
    work = [row[:] for row in matrix]
    sign = 1
    previous = Fraction(1)
    for column in range(size - 1):
        if work[column][column] == 0:
            for row_index in range(column + 1, size):
                if work[row_index][column] != 0:
                    work[column], work[row_index] = (
                        work[row_index],
                        work[column],
                    )
                    sign = -sign
                    break
            else:
                return Fraction(0)
        for row_index in range(column + 1, size):
            for column_index in range(column + 1, size):
                work[row_index][column_index] = (
                    work[row_index][column_index] * work[column][column]
                    - work[row_index][column] * work[column][column_index]
                ) / previous
        previous = work[column][column]
    return sign * work[size - 1][size - 1]


def _leading_minors(matrix: ExactMatrix) -> list[Fraction]:
    return [
        _det_exact([row[:size] for row in matrix[:size]])
        for size in range(1, len(matrix) + 1)
    ]


class ExactADMMMap:
    """Piecewise-affine ADMM map in the six-dimensional ``(y, t)`` state."""

    def __init__(self, arrays: dict[str, np.ndarray]) -> None:
        self.dimension = DIMENSION
        self.A = _to_exact_matrix(arrays["A"])
        self.B = _to_exact_matrix(arrays["B"])
        self.F = _to_exact_matrix(arrays["F"])
        self.G = _to_exact_matrix(arrays["G"])
        self.b = _to_exact_vector(arrays["b"])
        self.c1 = _to_exact_vector(arrays["c1"])
        self.c2 = _to_exact_vector(arrays["c2"])

        identity = _identity(self.dimension)
        hessian_x = [
            [
                self.F[row][column]
                + sum(
                    self.A[index][row] * self.A[index][column]
                    for index in range(self.dimension)
                )
                for column in range(self.dimension)
            ]
            for row in range(self.dimension)
        ]
        hessian_y = [
            [
                self.G[row][column]
                + sum(
                    self.B[index][row] * self.B[index][column]
                    for index in range(self.dimension)
                )
                for column in range(self.dimension)
            ]
            for row in range(self.dimension)
        ]
        self.hessian_x_inverse = _transpose(
            [_solve_exact(hessian_x, basis) for basis in identity]
        )
        self.hessian_y_inverse = _transpose(
            [_solve_exact(hessian_y, basis) for basis in identity]
        )

    def branch(self, mask: int) -> tuple[ExactMatrix, ExactVector]:
        dimension = self.dimension
        positive = [
            [
                Fraction(int(row == column and bool((mask >> row) & 1)))
                for column in range(dimension)
            ]
            for row in range(dimension)
        ]
        negative = [
            [
                Fraction(int(row == column)) - positive[row][column]
                if row == column
                else Fraction(0)
                for column in range(dimension)
            ]
            for row in range(dimension)
        ]
        signed = [
            [
                positive[row][row] - negative[row][row]
                if row == column
                else Fraction(0)
                for column in range(dimension)
            ]
            for row in range(dimension)
        ]

        x_from_y = _matmul(
            self.hessian_x_inverse,
            [
                [-entry for entry in row]
                for row in _matmul(_transpose(self.A), self.B)
            ],
        )
        x_from_t = _matmul(
            self.hessian_x_inverse,
            [
                [-entry for entry in row]
                for row in _matmul(_transpose(self.A), signed)
            ],
        )
        x_offset = _matvec(
            self.hessian_x_inverse,
            [
                -self.c1[index]
                + sum(
                    self.A[row][index] * self.b[row]
                    for row in range(dimension)
                )
                for index in range(dimension)
            ],
        )

        y_from_x = _matmul(
            self.hessian_y_inverse,
            [
                [-entry for entry in row]
                for row in _matmul(_transpose(self.B), self.A)
            ],
        )
        y_from_t_direct = _matmul(
            self.hessian_y_inverse,
            [
                [-entry for entry in row]
                for row in _matmul(_transpose(self.B), signed)
            ],
        )
        y_from_y = _matmul(y_from_x, x_from_y)
        y_from_t = [
            [
                sum(
                    y_from_x[row][index] * x_from_t[index][column]
                    for index in range(dimension)
                )
                + y_from_t_direct[row][column]
                for column in range(dimension)
            ]
            for row in range(dimension)
        ]
        y_offset_direct = _matvec(
            self.hessian_y_inverse,
            [
                -self.c2[index]
                + sum(
                    self.B[row][index] * self.b[row]
                    for row in range(dimension)
                )
                for index in range(dimension)
            ],
        )
        y_offset = [
            sum(
                y_from_x[row][index] * x_offset[index]
                for index in range(dimension)
            )
            + y_offset_direct[row]
            for row in range(dimension)
        ]

        t_from_y = [
            [
                -sum(
                    self.A[row][index] * x_from_y[index][column]
                    for index in range(dimension)
                )
                - sum(
                    self.B[row][index] * y_from_y[index][column]
                    for index in range(dimension)
                )
                for column in range(dimension)
            ]
            for row in range(dimension)
        ]
        t_from_t = [
            [
                negative[row][column]
                - sum(
                    self.A[row][index] * x_from_t[index][column]
                    for index in range(dimension)
                )
                - sum(
                    self.B[row][index] * y_from_t[index][column]
                    for index in range(dimension)
                )
                for column in range(dimension)
            ]
            for row in range(dimension)
        ]
        t_offset = [
            self.b[row]
            - sum(
                self.A[row][index] * x_offset[index]
                for index in range(dimension)
            )
            - sum(
                self.B[row][index] * y_offset[index]
                for index in range(dimension)
            )
            for row in range(dimension)
        ]

        matrix = [
            y_from_y[row] + y_from_t[row]
            for row in range(dimension)
        ] + [
            t_from_y[row] + t_from_t[row]
            for row in range(dimension)
        ]
        return matrix, y_offset + t_offset

    def step(self, state: ExactVector, mask: int) -> ExactVector:
        matrix, offset = self.branch(mask)
        return [
            sum(
                matrix[row][column] * state[column]
                for column in range(2 * self.dimension)
            )
            + offset[row]
            for row in range(2 * self.dimension)
        ]

    def mask(self, state: ExactVector) -> int:
        return sum(
            1 << index
            for index in range(self.dimension)
            if state[self.dimension + index] > 0
        )


def _compose_word(
    admm_map: ExactADMMMap,
    word: list[int],
) -> tuple[ExactMatrix, ExactVector]:
    state_dimension = 2 * admm_map.dimension
    product = _identity(state_dimension)
    offset = [Fraction(0)] * state_dimension
    for mask in word:
        branch_matrix, branch_offset = admm_map.branch(mask)
        offset = [
            sum(
                branch_matrix[row][column] * offset[column]
                for column in range(state_dimension)
            )
            + branch_offset[row]
            for row in range(state_dimension)
        ]
        product = _matmul(branch_matrix, product)
    return product, offset


def _fixed_point(
    matrix: ExactMatrix,
    offset: ExactVector,
) -> ExactVector:
    identity = _identity(len(matrix))
    return _solve_exact(
        [
            [
                identity[row][column] - matrix[row][column]
                for column in range(len(matrix))
            ]
            for row in range(len(matrix))
        ],
        offset,
    )


def _characteristic_polynomial(matrix: ExactMatrix) -> list[Fraction]:
    """Return coefficients of ``lambda^n + c1 lambda^(n-1) + ... + cn``."""
    size = len(matrix)
    auxiliary = _identity(size)
    coefficients: list[Fraction] = []
    for index in range(1, size + 1):
        multiplied = _matmul(matrix, auxiliary)
        trace = sum(multiplied[row][row] for row in range(size))
        coefficient = -trace / index
        coefficients.append(coefficient)
        auxiliary = [
            [
                multiplied[row][column]
                + (coefficient if row == column else Fraction(0))
                for column in range(size)
            ]
            for row in range(size)
        ]
    return coefficients


def _jury_certificate(
    coefficients: list[Fraction],
) -> tuple[bool, bool, list[list[Fraction]], dict[str, Fraction]]:
    polynomial = [Fraction(1)] + coefficients
    degree = len(coefficients)
    value_at_one = sum(polynomial)
    signed_value_at_minus_one = (
        (-1) ** degree
        * sum(
            polynomial[index] * ((-1) ** (degree - index))
            for index in range(degree + 1)
        )
    )
    preliminary = (
        value_at_one > 0
        and signed_value_at_minus_one > 0
        and abs(coefficients[-1]) < 1
    )
    table = [polynomial]
    stable = preliminary
    while stable and len(table[-1]) > 2:
        row = table[-1]
        last_index = len(row) - 1
        next_row = [
            row[0] * row[index] - row[last_index] * row[last_index - index]
            for index in range(last_index)
        ]
        table.append(next_row)
        if not abs(next_row[0]) > abs(next_row[-1]):
            stable = False
    witnesses = {
        "p_at_1": value_at_one,
        "signed_p_at_minus_1": signed_value_at_minus_one,
        "constant_coefficient_absolute_value": abs(coefficients[-1]),
    }
    return preliminary, stable, table, witnesses


def _exact_hash(values: Any) -> str:
    def encode(value: Any) -> Any:
        if isinstance(value, Fraction):
            return _fraction_text(value)
        if isinstance(value, list):
            return [encode(entry) for entry in value]
        if isinstance(value, tuple):
            return [encode(entry) for entry in value]
        if isinstance(value, dict):
            return {
                str(key): encode(entry)
                for key, entry in value.items()
            }
        return value

    return _canonical_json_hash(encode(values))


def certificate_payload(source: Path = DEFAULT_SOURCE) -> dict[str, Any]:
    arrays = _load_source(source)
    source_hash = _file_hash(source)
    word = [int(value) for value in arrays["per"]]
    admm_map = ExactADMMMap(arrays)

    leading_minors_f = _leading_minors(admm_map.F)
    leading_minors_g = _leading_minors(admm_map.G)
    symmetric_f = admm_map.F == _transpose(admm_map.F)
    symmetric_g = admm_map.G == _transpose(admm_map.G)
    determinant_a = _det_exact(admm_map.A)
    determinant_b = _det_exact(admm_map.B)

    kkt_matrix, kkt_offset = admm_map.branch(KKT_MASK)
    kkt_fixed_point = _fixed_point(kkt_matrix, kkt_offset)
    kkt_y = kkt_fixed_point[:DIMENSION]
    kkt_t = kkt_fixed_point[DIMENSION:]
    kkt_z = [max(value, Fraction(0)) for value in kkt_t]
    kkt_lambda = [min(value, Fraction(0)) for value in kkt_t]
    kkt_x = _solve_exact(
        admm_map.F,
        [
            sum(
                admm_map.A[row][column] * kkt_lambda[row]
                for row in range(DIMENSION)
            )
            - admm_map.c1[column]
            for column in range(DIMENSION)
        ],
    )
    kkt_x_stationarity = [
        sum(
            admm_map.F[row][column] * kkt_x[column]
            for column in range(DIMENSION)
        )
        + admm_map.c1[row]
        - sum(
            admm_map.A[column][row] * kkt_lambda[column]
            for column in range(DIMENSION)
        )
        for row in range(DIMENSION)
    ]
    kkt_y_stationarity = [
        sum(
            admm_map.G[row][column] * kkt_y[column]
            for column in range(DIMENSION)
        )
        + admm_map.c2[row]
        - sum(
            admm_map.B[column][row] * kkt_lambda[column]
            for column in range(DIMENSION)
        )
        for row in range(DIMENSION)
    ]
    kkt_primal_residual = [
        sum(
            admm_map.A[row][column] * kkt_x[column]
            for column in range(DIMENSION)
        )
        + sum(
            admm_map.B[row][column] * kkt_y[column]
            for column in range(DIMENSION)
        )
        + kkt_z[row]
        - admm_map.b[row]
        for row in range(DIMENSION)
    ]
    stored_kkt_candidate = _to_exact_vector(arrays["ys"]) + [
        Fraction(float(z_value)) + Fraction(float(lambda_value))
        for z_value, lambda_value in zip(arrays["z"], arrays["lam"])
    ]
    kkt_candidate_distance = max(
        abs(exact - stored)
        for exact, stored in zip(kkt_fixed_point, stored_kkt_candidate)
    )

    return_matrix, return_offset = _compose_word(admm_map, word)
    phase_zero = _fixed_point(return_matrix, return_offset)
    state = phase_zero[:]
    states: list[ExactVector] = []
    actual_masks: list[int] = []
    for expected_mask in word:
        states.append(state[:])
        actual_masks.append(admm_map.mask(state))
        state = admm_map.step(state, expected_mask)

    strict_margin = min(
        abs(cycle_state[DIMENSION + index])
        for cycle_state in states
        for index in range(DIMENSION)
    )
    states_distinct = len({tuple(cycle_state) for cycle_state in states}) == len(
        states
    )
    cycle_closed = state == phase_zero
    cycle_not_fixed = (
        admm_map.step(phase_zero, admm_map.mask(phase_zero)) != phase_zero
    )
    minimal_period = (
        len(word) == 23
        and cycle_closed
        and cycle_not_fixed
        and states_distinct
    )

    characteristic_coefficients = _characteristic_polynomial(return_matrix)
    (
        jury_preliminary,
        jury_stable,
        jury_table,
        jury_witnesses,
    ) = _jury_certificate(characteristic_coefficients)

    checks = {
        "source_SHA256_matches_frozen_artifact": (
            source_hash == EXPECTED_SOURCE_SHA256
        ),
        "F_is_exactly_symmetric": symmetric_f,
        "G_is_exactly_symmetric": symmetric_g,
        "F_is_positive_definite_by_exact_Sylvester_test": (
            symmetric_f and all(value > 0 for value in leading_minors_f)
        ),
        "G_is_positive_definite_by_exact_Sylvester_test": (
            symmetric_g and all(value > 0 for value in leading_minors_g)
        ),
        "A_is_nonsingular_exactly": determinant_a != 0,
        "B_is_nonsingular_exactly": determinant_b != 0,
        "KKT_branch_fixed_point_has_mask_4": (
            admm_map.mask(kkt_fixed_point) == KKT_MASK
        ),
        "KKT_primal_feasibility_holds_exactly": all(
            value == 0 for value in kkt_primal_residual
        ),
        "KKT_x_stationarity_holds_exactly": all(
            value == 0 for value in kkt_x_stationarity
        ),
        "KKT_y_stationarity_holds_exactly": all(
            value == 0 for value in kkt_y_stationarity
        ),
        "KKT_slack_is_nonnegative": all(value >= 0 for value in kkt_z),
        "KKT_multiplier_is_nonpositive": all(
            value <= 0 for value in kkt_lambda
        ),
        "KKT_complementarity_holds_exactly": all(
            slack * multiplier == 0
            for slack, multiplier in zip(kkt_z, kkt_lambda)
        ),
        "KKT_uniqueness_conditions_hold": (
            symmetric_f
            and symmetric_g
            and all(value > 0 for value in leading_minors_f)
            and all(value > 0 for value in leading_minors_g)
            and determinant_a != 0
        ),
        "stored_KKT_candidate_is_within_1e-12": (
            kkt_candidate_distance < KKT_CANDIDATE_TOLERANCE
        ),
        "cycle_masks_match_exactly": actual_masks == word,
        "strict_cell_margin_exceeds_7_over_1000": (
            strict_margin > STRICT_MARGIN_LOWER_BOUND
        ),
        "all_23_cycle_states_are_distinct_exactly": (
            len(states) == 23 and states_distinct
        ),
        "cycle_closes_after_23_steps_exactly": cycle_closed,
        "cycle_is_not_a_fixed_point": cycle_not_fixed,
        "minimal_period_is_23": minimal_period,
        "cycle_phase_differs_from_KKT_fixed_point": (
            phase_zero != kkt_fixed_point
        ),
        "Jury_preconditions_hold_exactly": jury_preliminary,
        "return_map_is_Schur_stable_by_exact_Jury_test": jury_stable,
    }
    valid = all(checks.values())

    return {
        "schema_version": 1,
        "instance_id": INSTANCE_ID,
        "status": "passed" if valid else "failed",
        "valid": valid,
        "formulation": {
            "problem": (
                "min 0.5*x^T*F*x+c1^T*x+0.5*y^T*G*y+c2^T*y"
                "+delta_{R_+^3}(z), s.t. A*x+B*y+z=b"
            ),
            "algorithm": "direct three-block ADMM",
            "penalty_parameter": "1",
            "exact_state": "(y,t) with t=z+lambda",
            "projection": "z=[t]_+ and lambda=[t]_- componentwise",
        },
        "source_interpretation": (
            "Every float64 entry in the NPZ source is converted with "
            "Fraction(float(entry)); all replay, closure, active-set, "
            "determinant, characteristic-polynomial, and Jury checks are exact."
        ),
        "period": len(word),
        "mask_word": word,
        "KKT_mask": KKT_MASK,
        "checks": checks,
        "exact_witnesses": {
            "determinant_A": _fraction_text(determinant_a),
            "determinant_B": _fraction_text(determinant_b),
            "F_leading_principal_minors": _fraction_vector(leading_minors_f),
            "G_leading_principal_minors": _fraction_vector(leading_minors_g),
            "KKT_candidate_max_norm_distance": _fraction_text(
                kkt_candidate_distance
            ),
            "KKT_point_x": _fraction_vector(kkt_x),
            "KKT_point_y": _fraction_vector(kkt_y),
            "KKT_point_z": _fraction_vector(kkt_z),
            "KKT_point_lambda": _fraction_vector(kkt_lambda),
            "KKT_primal_residual": _fraction_vector(kkt_primal_residual),
            "KKT_x_stationarity_residual": _fraction_vector(
                kkt_x_stationarity
            ),
            "KKT_y_stationarity_residual": _fraction_vector(
                kkt_y_stationarity
            ),
            "strict_cell_margin": _fraction_text(strict_margin),
            "strict_cell_margin_lower_bound": _fraction_text(
                STRICT_MARGIN_LOWER_BOUND
            ),
            "phase_zero": _fraction_vector(phase_zero),
            "KKT_fixed_point": _fraction_vector(kkt_fixed_point),
            "return_map_characteristic_polynomial": [
                "1",
                *_fraction_vector(characteristic_coefficients),
            ],
            "Jury_precondition_witnesses": {
                name: _fraction_text(value)
                for name, value in jury_witnesses.items()
            },
        },
        "exact_hashes": {
            "source_instance_arrays": _exact_hash(
                {
                    name: _nested_encode(
                        arrays[name].tolist(),
                        (
                            lambda value: Fraction(float(value))
                            if np.issubdtype(
                                arrays[name].dtype,
                                np.floating,
                            )
                            else int(value)
                        ),
                    )
                    for name in sorted(arrays)
                }
            ),
            "mask_word": _exact_hash(word),
            "cycle_states_y_t": _exact_hash(states),
            "phase_zero_y_t": _exact_hash(phase_zero),
            "KKT_fixed_point_y_t": _exact_hash(kkt_fixed_point),
            "return_affine_map": _exact_hash(
                {"matrix": return_matrix, "offset": return_offset}
            ),
            "return_map_characteristic_polynomial": _exact_hash(
                [Fraction(1), *characteristic_coefficients]
            ),
            "Jury_table": _exact_hash(jury_table),
        },
        "claim_boundary": (
            "This certificate proves an exact minimal period-23 orbit for one "
            "fixed m=3 dyadic QP and exact Schur stability of its strict-cell "
            "return map. Together with the positive strict-cell margin, this "
            "gives local attraction of the periodic orbit in the canonical "
            "reduced (y,t) state. The margin is not an explicit basin radius, "
            "and the result is not a parameter interval, a full ambient-state "
            "ball, or a global theorem for all instances or initializations."
        ),
    }


def _nested_encode(
    value: Any,
    scalar_encoder: Callable[[Any], Any],
) -> Any:
    if isinstance(value, list):
        return [
            _nested_encode(entry, scalar_encoder)
            for entry in value
        ]
    return scalar_encoder(value)


def _source_array_manifest(array: np.ndarray) -> dict[str, Any]:
    result: dict[str, Any] = {
        "shape": list(array.shape),
        "dtype": str(array.dtype),
        "numpy_dtype_descriptor": array.dtype.str,
        "C_order_data_SHA256": hashlib.sha256(
            array.tobytes(order="C")
        ).hexdigest(),
    }
    values = array.tolist()
    if np.issubdtype(array.dtype, np.floating):
        result.update(
            {
                "interpretation": (
                    "IEEE-754 binary64, interpreted as an exact dyadic rational"
                ),
                "binary64_hex": _nested_encode(
                    values,
                    lambda value: float(value).hex(),
                ),
                "exact_dyadic": _nested_encode(
                    values,
                    lambda value: _fraction_text(Fraction(float(value))),
                ),
            }
        )
    elif np.issubdtype(array.dtype, np.integer):
        result.update(
            {
                "interpretation": "exact signed integer",
                "exact_integer": _nested_encode(
                    values,
                    lambda value: int(value),
                ),
            }
        )
    else:
        raise TypeError(f"unsupported source dtype: {array.dtype}")
    return result


def instance_manifest(
    certificate: dict[str, Any],
    source: Path = DEFAULT_SOURCE,
) -> dict[str, Any]:
    arrays = _load_source(source)
    verifier_source = Path(__file__).resolve()
    checks = {
        "certificate_is_valid": bool(certificate.get("valid", False)),
        "source_SHA256_matches_expected": (
            _file_hash(source) == EXPECTED_SOURCE_SHA256
        ),
        "all_source_arrays_are_exposed": (
            set(arrays) == set(EXPECTED_ARRAYS)
        ),
    }
    valid = all(checks.values())
    return {
        "schema_version": 1,
        "instance_id": INSTANCE_ID,
        "status": "passed" if valid else "failed",
        "valid": valid,
        "checks": checks,
        "artifacts": {
            "source_binary64": {
                "file": DEFAULT_SOURCE.name,
                "SHA256": _file_hash(source),
            },
            "public_exact_verifier": {
                "file": verifier_source.name,
                "SHA256": _file_hash(verifier_source),
            },
            "frozen_certificate": {
                "file": DEFAULT_CERTIFICATE.name,
                "canonical_JSON_SHA256": _canonical_json_hash(certificate),
                "stable_file_bytes_SHA256": _stable_json_bytes_hash(certificate),
            },
            "upstream_Kimi_exact_verifier": {
                "file": "exp19b_exact_yt.py",
                "SHA256": UPSTREAM_VERIFIER_SHA256,
            },
        },
        "source_array_encoding": (
            "The manifest exposes shape, dtype, C-order byte hash, binary64 "
            "hexadecimal value, and exact Fraction value for every floating "
            "source entry. Integer entries are exposed as exact integers."
        ),
        "source_field_semantics": {
            "rho": (
                "exploratory binary64 estimate of the return-map spectral "
                "radius; it is not the ADMM penalty parameter"
            ),
            "vfix": "exploratory stored full-state fixed-point candidate",
        },
        "source_arrays": {
            name: _source_array_manifest(arrays[name])
            for name in sorted(arrays)
        },
        "claim_boundary": certificate["claim_boundary"],
    }


def _write_payload(payload: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_stable_json(payload), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Regenerate the exact dyadic period-23 ADMM certificate and "
            "its source-data manifest."
        )
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
    )
    parser.add_argument(
        "--certificate-output",
        type=Path,
        default=DEFAULT_CERTIFICATE,
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=DEFAULT_MANIFEST,
    )
    args = parser.parse_args()

    try:
        certificate = certificate_payload(args.source)
        manifest = instance_manifest(certificate, args.source)
    except Exception as error:
        print(
            _stable_json(
                {
                    "instance_id": INSTANCE_ID,
                    "status": "error",
                    "valid": False,
                    "error": f"{type(error).__name__}: {error}",
                }
            ),
            file=sys.stderr,
            end="",
        )
        raise SystemExit(1) from error

    if not certificate["valid"] or not manifest["valid"]:
        print(
            _stable_json(
                {
                    "instance_id": INSTANCE_ID,
                    "status": "failed",
                    "valid": False,
                    "checks": certificate["checks"],
                }
            ),
            file=sys.stderr,
            end="",
        )
        raise SystemExit(1)

    _write_payload(certificate, args.certificate_output)
    _write_payload(manifest, args.manifest_output)
    print(
        json.dumps(
            {
                "certificate": str(args.certificate_output.resolve()),
                "instance_id": INSTANCE_ID,
                "manifest": str(args.manifest_output.resolve()),
                "period": certificate["period"],
                "valid": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
