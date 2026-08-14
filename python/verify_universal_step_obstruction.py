"""Regenerate the universal obstruction and its local-instability dependency."""

from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path

import analyze_identity_slack_small_step_local_instability as local_instability
import analyze_identity_slack_universal_step_obstruction as obstruction


HERE = Path(__file__).resolve().parent
DEFAULT_CERTIFICATE_DIR = HERE.parent / "certificates"
CERTIFICATE_BUILDERS = (
    (
        "identity_slack_small_step_local_instability.json",
        local_instability.exact_certificate,
    ),
    (
        "identity_slack_universal_step_obstruction.json",
        obstruction.exact_certificate,
    ),
)
LOCAL_INSTABILITY_CERTIFICATE = "identity_slack_small_step_local_instability.json"
NUMERIC_SANITY_RADIUS_PATHS = (
    ("numeric_sanity_checks", 0),
    ("numeric_sanity_checks", 1),
    ("numeric_sanity_checks", 2),
    ("strict_rational_sanity_checks", 0),
    ("strict_rational_sanity_checks", 1),
    ("strict_rational_sanity_checks", 2),
)
SPECTRAL_RADIUS_ABS_TOLERANCE = 1e-12


def _matches_tracked_certificate(
    filename: str,
    regenerated: dict[str, object],
    tracked_text: str,
) -> bool:
    regenerated_text = json.dumps(regenerated, indent=2) + "\n"
    if regenerated_text == tracked_text:
        return True
    if filename != LOCAL_INSTABILITY_CERTIFICATE:
        return False

    try:
        tracked = json.loads(tracked_text)
    except json.JSONDecodeError:
        return False
    if not isinstance(tracked, dict):
        return False

    normalized = copy.deepcopy(regenerated)
    for section, index in NUMERIC_SANITY_RADIUS_PATHS:
        regenerated_records = normalized.get(section)
        tracked_records = tracked.get(section)
        if not isinstance(regenerated_records, list) or not isinstance(
            tracked_records, list
        ):
            return False
        if index >= len(regenerated_records) or index >= len(tracked_records):
            return False
        regenerated_record = regenerated_records[index]
        tracked_record = tracked_records[index]
        if not isinstance(regenerated_record, dict) or not isinstance(
            tracked_record, dict
        ):
            return False
        regenerated_radius = regenerated_record.get("spectral_radius")
        tracked_radius = tracked_record.get("spectral_radius")
        if not isinstance(regenerated_radius, (int, float)) or isinstance(
            regenerated_radius, bool
        ):
            return False
        if not isinstance(tracked_radius, (int, float)) or isinstance(
            tracked_radius, bool
        ):
            return False
        if not math.isfinite(regenerated_radius) or not math.isfinite(
            tracked_radius
        ):
            return False
        if not math.isclose(
            regenerated_radius,
            tracked_radius,
            rel_tol=0.0,
            abs_tol=SPECTRAL_RADIUS_ABS_TOLERANCE,
        ):
            return False
        regenerated_record["spectral_radius"] = tracked_radius

    # Only the platform-dependent numerical sanity radii are normalized.
    # Serialization, ordering, and every exact symbolic field remain byte strict.
    return json.dumps(normalized, indent=2) + "\n" == tracked_text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail unless both regenerated certificates match the tracked files",
    )
    parser.add_argument(
        "--certificate-dir",
        type=Path,
        default=DEFAULT_CERTIFICATE_DIR,
        help="directory containing the two tracked certificate JSON files",
    )
    args = parser.parse_args()
    for filename, builder in CERTIFICATE_BUILDERS:
        certificate_path = args.certificate_dir / filename
        try:
            display_path = certificate_path.relative_to(HERE.parent)
        except ValueError:
            display_path = certificate_path
        certificate = builder()
        text = json.dumps(certificate, indent=2) + "\n"
        if args.check:
            tracked = certificate_path.read_text(encoding="utf-8")
            if not _matches_tracked_certificate(filename, certificate, tracked):
                raise SystemExit(f"certificate drift: {display_path}")
            print(f"ok: {display_path}")
        else:
            certificate_path.parent.mkdir(parents=True, exist_ok=True)
            certificate_path.write_text(text, encoding="utf-8")
            print(f"wrote {display_path}")


if __name__ == "__main__":
    main()
