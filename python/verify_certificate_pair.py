"""Regenerate and compare the independent raw and signed certificates."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import platform
from pathlib import Path
from typing import Callable

import signed_cycle_certificate as signed_checker
import strict_cycle_certificate as raw_checker


HERE = Path(__file__).resolve().parent
CERTIFICATE_DIR = HERE.parent / "certificates"
INSTANCE_ID = "identity_slack_p66_short_v1"


def _stable_json(payload: dict[str, object]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def _json_hash(payload: dict[str, object]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module)
    return modules


def _safe_payload(
    implementation: str,
    builder: Callable[[], dict[str, object]],
) -> dict[str, object]:
    try:
        return builder()
    except Exception as error:
        return {
            "schema_version": 1,
            "instance_id": INSTANCE_ID,
            "implementation": implementation,
            "status": "error",
            "valid": False,
            "error": f"{type(error).__name__}: {error}",
        }


def build_manifest(
    raw_payload: dict[str, object],
    signed_payload: dict[str, object],
    raw_output: Path,
    signed_output: Path,
) -> dict[str, object]:
    """Compare the independently generated payloads field by field."""
    raw_source = Path(raw_checker.__file__).resolve()
    signed_source = Path(signed_checker.__file__).resolve()
    raw_imports = _imported_modules(raw_source)
    signed_imports = _imported_modules(signed_source)
    raw_checks = raw_payload.get("checks", {})
    signed_checks = signed_payload.get("checks", {})
    raw_hashes = raw_payload.get("exact_hashes", {})
    signed_hashes = signed_payload.get("exact_hashes", {})

    shared_hash_names = (
        "instance",
        "word",
        "orbit_y_q",
        "initial_y_q",
        "minimum_margin",
    )
    comparisons = {
        "raw_checker_valid": bool(raw_payload.get("valid", False)),
        "signed_checker_valid": bool(signed_payload.get("valid", False)),
        "raw_acceptance_checks_all_true": bool(raw_checks)
        and all(bool(value) for value in raw_checks.values()),
        "signed_acceptance_checks_all_true": bool(signed_checks)
        and all(bool(value) for value in signed_checks.values()),
        "instance_id_matches": raw_payload.get("instance_id")
        == signed_payload.get("instance_id")
        == INSTANCE_ID,
        "pure_quadratic_formulation_matches": raw_payload.get("formulation")
        == signed_payload.get("formulation")
        == "pure_quadratic_zero_linear_terms",
        "parameters_match": raw_payload.get("parameters")
        == signed_payload.get("parameters"),
        "period_matches": raw_payload.get("period")
        == signed_payload.get("period")
        == 66,
        "mask_word_matches": raw_payload.get("word_run_length_encoding")
        == signed_payload.get("word_run_length_encoding"),
        "minimum_margin_matches_exactly": raw_payload.get("minimum_margin")
        == signed_payload.get("minimum_margin"),
        "pure_y0_matches_exactly": raw_payload.get("initial_state", {}).get(
            "y0_exact"
        )
        == signed_payload.get("initial_state", {}).get("y0_exact"),
        "q0_matches_exactly": raw_payload.get("initial_state", {}).get(
            "q0_exact"
        )
        == signed_payload.get("initial_state", {}).get("q0_exact"),
        "KKT_point_matches_exactly": raw_payload.get("kkt_point")
        == signed_payload.get("kkt_point"),
        "all_shared_exact_hashes_match": all(
            raw_hashes.get(name) is not None
            and raw_hashes.get(name) == signed_hashes.get(name)
            for name in shared_hash_names
        ),
        "signed_cross_term_phase_1_positive_witness_passed": any(
            witness.get("source_phase_zero_based") == 1
            and witness.get("expected_sign") == "positive"
            and witness.get("passed") is True
            for witness in signed_payload.get("cross_term_sign_witnesses", [])
        ),
        "signed_cross_term_phase_20_negative_witness_passed": any(
            witness.get("source_phase_zero_based") == 20
            and witness.get("expected_sign") == "negative"
            and witness.get("passed") is True
            for witness in signed_payload.get("cross_term_sign_witnesses", [])
        ),
        "raw_checker_does_not_import_signed_checker": (
            "signed_cycle_certificate" not in raw_imports
        ),
        "signed_checker_does_not_import_raw_checker": (
            "strict_cycle_certificate" not in signed_imports
        ),
        "written_raw_JSON_matches_generated_payload": json.loads(
            raw_output.read_text(encoding="utf-8")
        )
        == raw_payload,
        "written_signed_JSON_matches_generated_payload": json.loads(
            signed_output.read_text(encoding="utf-8")
        )
        == signed_payload,
    }
    valid = all(comparisons.values())
    shared = {
        "instance_id": raw_payload.get("instance_id"),
        "formulation": raw_payload.get("formulation"),
        "parameters": raw_payload.get("parameters"),
        "period": raw_payload.get("period"),
        "word_run_length_encoding": raw_payload.get("word_run_length_encoding"),
        "minimum_margin": raw_payload.get("minimum_margin"),
        "initial_state": {
            "y0_exact": raw_payload.get("initial_state", {}).get("y0_exact"),
            "y0_decimal": raw_payload.get("initial_state", {}).get("y0_decimal"),
            "q0_exact": raw_payload.get("initial_state", {}).get("q0_exact"),
            "q0_decimal": raw_payload.get("initial_state", {}).get("q0_decimal"),
        },
        "exact_hashes": {
            name: raw_payload.get("exact_hashes", {}).get(name)
            for name in shared_hash_names
        },
    }
    return {
        "schema_version": 1,
        "instance_id": INSTANCE_ID,
        "status": "passed" if valid else "failed",
        "valid": valid,
        "comparison_boundary": (
            "The raw 6D and signed 4D checkers share no implementation "
            "imports. This driver compares their independently generated "
            "exact instance, initial state, margin, and orbit hashes."
        ),
        "runtime": {
            "python": platform.python_version(),
            "sympy": signed_checker.sp.__version__,
        },
        "comparisons": comparisons,
        "shared_certificate": shared,
        "signed_cross_term_sign_witnesses": signed_payload.get(
            "cross_term_sign_witnesses", []
        ),
        "artifacts": {
            "raw_certificate": raw_output.name,
            "signed_certificate": signed_output.name,
            "raw_certificate_JSON_sha256": _json_hash(raw_payload),
            "signed_certificate_JSON_sha256": _json_hash(signed_payload),
            "raw_checker_source": raw_source.name,
            "signed_checker_source": signed_source.name,
            "raw_checker_source_sha256": _file_hash(raw_source),
            "signed_checker_source_sha256": _file_hash(signed_source),
        },
        "claim_boundary": (
            "Agreement of the two exact implementations is an internal "
            "reproducibility cross-check, not external independent review."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate and compare the raw 6D and signed 4D certificates."
    )
    parser.add_argument(
        "--raw-output",
        type=Path,
        default=CERTIFICATE_DIR / "certificate_raw.json",
    )
    parser.add_argument(
        "--signed-output",
        type=Path,
        default=CERTIFICATE_DIR / "certificate_signed.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=CERTIFICATE_DIR / "instance_manifest.json",
    )
    args = parser.parse_args()

    raw_payload = _safe_payload(
        "independent_raw_6d_basis_evaluation",
        raw_checker.certificate_payload,
    )
    signed_payload = _safe_payload(
        "independent_signed_4d_recurrence",
        signed_checker.certificate_payload,
    )
    raw_checker.write_payload(raw_payload, args.raw_output)
    signed_checker.write_payload(signed_payload, args.signed_output)

    manifest = build_manifest(
        raw_payload,
        signed_payload,
        args.raw_output,
        args.signed_output,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(_stable_json(manifest), encoding="utf-8")
    print(
        json.dumps(
            {
                "instance_id": manifest["instance_id"],
                "output": str(args.output.resolve()),
                "valid": manifest["valid"],
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if manifest["valid"] else 1)


if __name__ == "__main__":
    main()
