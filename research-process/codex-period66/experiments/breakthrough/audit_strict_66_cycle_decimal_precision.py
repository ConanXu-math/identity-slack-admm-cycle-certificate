"""Audit how many decimal places are needed for the strict 66-cycle witness.

The grid scans are floating-point discovery screens.  Any reported witness is
then rebuilt from exact decimal rationals and checked by both exact certifiers.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from heapq import heappush, heappushpop
from pathlib import Path
from time import perf_counter
from typing import Iterable

import sympy as sp

from experiments.breakthrough.audit_strict_rational_66_cycle_independent import (
    run as run_raw_audit,
)
from experiments.breakthrough.certify_strict_rational_66_cycle import (
    run as run_reduced_audit,
)
from experiments.breakthrough.search_stage43_to_strict_66_cycle import (
    evaluate_periodic_word,
)


TopItem = tuple[float, int, int]


def _scan_integer_rows(
    task: tuple[int, int, int, int, int, int],
) -> tuple[int, int, int, list[TopItem]]:
    digits, mu_start, mu_stop, nu_start, nu_stop, keep = task
    scale = 10**digits
    top: list[TopItem] = []
    total = 0
    positive = 0
    above_threshold = 0
    for mu_integer in range(mu_start, mu_stop):
        mu = mu_integer / scale
        for nu_integer in range(nu_start, nu_stop):
            nu = nu_integer / scale
            evaluation = evaluate_periodic_word(mu, nu, 2, 64)
            if evaluation is None:
                continue
            total += 1
            margin = float(evaluation["minimum_margin"])
            positive += margin > 0
            above_threshold += margin > 1.0e-3
            item = (margin, mu_integer, nu_integer)
            if len(top) < keep:
                heappush(top, item)
            elif item > top[0]:
                heappushpop(top, item)
    return total, positive, above_threshold, top


def scan_grid(
    digits: int,
    mu_integers: range,
    nu_integers: range,
    workers: int = 1,
    keep: int = 10,
) -> dict[str, object]:
    """Screen a finite decimal grid and retain its best points."""
    worker_count = max(1, min(workers, len(mu_integers)))
    chunk_size = (len(mu_integers) + worker_count - 1) // worker_count
    tasks = [
        (
            digits,
            start,
            min(mu_integers.stop, start + chunk_size),
            nu_integers.start,
            nu_integers.stop,
            keep,
        )
        for start in range(mu_integers.start, mu_integers.stop, chunk_size)
    ]
    started = perf_counter()
    if worker_count == 1:
        results: Iterable[tuple[int, int, int, list[TopItem]]] = map(
            _scan_integer_rows, tasks
        )
    else:
        pool = ProcessPoolExecutor(max_workers=worker_count)
        results = pool.map(_scan_integer_rows, tasks)

    total = 0
    positive = 0
    above_threshold = 0
    top: list[TopItem] = []
    try:
        for subtotal, subpositive, subthreshold, subtop in results:
            total += subtotal
            positive += subpositive
            above_threshold += subthreshold
            for item in subtop:
                if len(top) < keep:
                    heappush(top, item)
                elif item > top[0]:
                    heappushpop(top, item)
    finally:
        if worker_count != 1:
            pool.shutdown()

    scale = 10**digits
    return {
        "digits": digits,
        "total_grid_points": total,
        "positive_margin_count": positive,
        "margin_gt_1_over_1000_count": above_threshold,
        "elapsed_seconds": perf_counter() - started,
        "top": [
            {
                "mu": f"{mu_integer / scale:.{digits}f}",
                "nu": f"{nu_integer / scale:.{digits}f}",
                "floating_minimum_margin": margin,
            }
            for margin, mu_integer, nu_integer in sorted(top, reverse=True)
        ],
    }


def exact_cross_audit(
    mu_integer: int,
    nu_integer: int,
    digits: int,
) -> dict[str, object]:
    scale = 10**digits
    mu = sp.Rational(mu_integer, scale)
    nu = sp.Rational(nu_integer, scale)
    reduced = run_reduced_audit(mu=mu, nu=nu)
    raw = run_raw_audit(mu=mu, nu=nu)
    return {
        "digits": digits,
        "mu": sp.sstr(mu),
        "nu": sp.sstr(nu),
        "reduced_certificate_valid": reduced["valid"],
        "raw_admm_certificate_valid": raw["valid"],
        "minimum_margin_exact_decimal": reduced["minimum_margin_decimal"],
        "minimum_margin_hashes_match": (
            reduced["exact_hashes"]["minimum_margin"]
            == raw["exact_hashes"]["minimum_margin"]
        ),
        "reduced_failed_checks": [
            name for name, value in reduced["checks"].items() if not value
        ],
        "raw_failed_checks": [
            name for name, value in raw["checks"].items() if not value
        ],
        "reduced_exact_hashes": reduced["exact_hashes"],
        "raw_exact_hashes": raw["exact_hashes"],
    }


def run(workers: int = 4) -> dict[str, object]:
    original_box = {
        "three_digits": scan_grid(
            3, range(850, 981), range(995, 1000), workers=workers
        ),
        "four_digits": scan_grid(
            4, range(8500, 9801), range(9950, 10000), workers=workers
        ),
    }
    full_three_digit_box = scan_grid(
        3, range(1, 1000), range(1, 1000), workers=workers
    )
    exact_four_digit_witness = exact_cross_audit(8957, 9990, 4)
    return {
        "status": "decimal_precision_audit_for_strict_66_cycle",
        "fixed_word_run_length_encoding": [[0, 2], [1, 64]],
        "threshold": "1/1000",
        "original_stage43_search_box": {
            "mu": ["0.85", "0.98"],
            "nu": ["0.995", "0.9999999"],
            "screens": original_box,
        },
        "full_admissible_three_digit_screen": {
            "domain": "0 < mu,nu < 1 on the three-decimal grid",
            "screen": full_three_digit_box,
        },
        "exact_four_digit_witness": exact_four_digit_witness,
        "claim_boundary": [
            "Grid enumeration uses floating point and is discovery evidence.",
            "The four-digit witness is rebuilt as exact rationals and passes two exact implementations.",
            "Absence of a three-digit floating hit is not an interval-arithmetic impossibility theorem.",
            "Decimal-place minimality is relative to this mu,nu parameterization and fixed 66-letter word.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "outputs/breakthrough_attempts/"
            "stage46_decimal_precision_audit/certificate.json"
        ),
    )
    args = parser.parse_args()
    payload = run(workers=args.workers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "four_digit_exact_valid": payload["exact_four_digit_witness"][
                    "reduced_certificate_valid"
                ]
                and payload["exact_four_digit_witness"][
                    "raw_admm_certificate_valid"
                ],
                "four_digit_minimum_margin": payload[
                    "exact_four_digit_witness"
                ]["minimum_margin_exact_decimal"],
                "three_digit_positive_count_full_box": payload[
                    "full_admissible_three_digit_screen"
                ]["screen"]["positive_margin_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
