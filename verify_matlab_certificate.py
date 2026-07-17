"""Compare the tracked MATLAB exact certificate with the Python artifacts."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
INSTANCE_ID = "identity_slack_p66_short_v1"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fraction(value: str) -> Fraction:
    return Fraction(value)


def _fraction_vector(values: list[str]) -> list[Fraction]:
    return [_fraction(value) for value in values]


def build_comparison(
    matlab: dict[str, Any],
    manifest: dict[str, Any],
    raw: dict[str, Any],
) -> dict[str, bool]:
    """Return exact cross-language agreement predicates."""
    shared = manifest["shared_certificate"]
    matlab_checks = matlab.get("checks", {})
    matlab_agreement = matlab.get("python_manifest_agreement", {})
    return {
        "matlab_certificate_valid": matlab.get("valid") is True,
        "matlab_mathematical_checks_valid": matlab.get("mathematical_valid")
        is True,
        "matlab_acceptance_checks_all_true": bool(matlab_checks)
        and all(value is True for value in matlab_checks.values()),
        "matlab_manifest_checks_all_true": bool(matlab_agreement)
        and all(value is True for value in matlab_agreement.values()),
        "instance_id_matches": matlab.get("instance_id")
        == shared.get("instance_id")
        == INSTANCE_ID,
        "formulation_matches": matlab.get("formulation")
        == shared.get("formulation")
        == "pure_quadratic_zero_linear_terms",
        "parameters_match": matlab.get("parameters") == shared.get("parameters"),
        "period_matches": matlab.get("period") == shared.get("period") == 66,
        "mask_word_matches": matlab.get("word_run_length_encoding")
        == shared.get("word_run_length_encoding")
        == [["00", 2], ["01", 64]],
        "minimum_margin_matches_exactly": _fraction(
            matlab["minimum_margin"]["exact"]
        )
        == _fraction(shared["minimum_margin"]["exact"]),
        "minimum_margin_location_matches": (
            matlab["minimum_margin"]["phase_zero_based"],
            matlab["minimum_margin"]["coordinate_zero_based"],
        )
        == (
            shared["minimum_margin"]["phase_zero_based"],
            shared["minimum_margin"]["coordinate_zero_based"],
        ),
        "margin_threshold_matches": _fraction(
            matlab["minimum_margin"]["threshold_exact"]
        )
        == _fraction(shared["minimum_margin"]["threshold_exact"]),
        "y0_matches_exactly": _fraction_vector(
            matlab["initial_state"]["y0_exact"]
        )
        == _fraction_vector(shared["initial_state"]["y0_exact"]),
        "q0_matches_exactly": _fraction_vector(
            matlab["initial_state"]["q0_exact"]
        )
        == _fraction_vector(shared["initial_state"]["q0_exact"]),
        "z0_matches_raw_certificate": _fraction_vector(
            matlab["initial_state"]["z0_exact"]
        )
        == _fraction_vector(raw["initial_state"]["z0_exact"]),
        "lambda0_matches_raw_certificate": _fraction_vector(
            matlab["initial_state"]["lambda0_exact"]
        )
        == _fraction_vector(raw["initial_state"]["lambda0_exact"]),
        "KKT_point_matches_raw_certificate": all(
            _fraction_vector(matlab["kkt_point"][field])
            == _fraction_vector(raw["kkt_point"][field])
            for field in ("x_exact", "y_exact", "z_exact", "lambda_exact")
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare the MATLAB exact certificate with Python artifacts."
    )
    parser.add_argument(
        "--matlab",
        type=Path,
        default=HERE / "certificate_matlab.json",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=HERE / "instance_manifest.json",
    )
    parser.add_argument(
        "--raw",
        type=Path,
        default=HERE / "certificate_raw.json",
    )
    args = parser.parse_args()

    comparisons = build_comparison(
        _load(args.matlab),
        _load(args.manifest),
        _load(args.raw),
    )
    valid = all(comparisons.values())
    print(
        json.dumps(
            {
                "instance_id": INSTANCE_ID,
                "matlab_certificate": str(args.matlab.resolve()),
                "comparisons": comparisons,
                "valid": valid,
            },
            indent=2,
            sort_keys=True,
        )
    )
    raise SystemExit(0 if valid else 1)


if __name__ == "__main__":
    main()
