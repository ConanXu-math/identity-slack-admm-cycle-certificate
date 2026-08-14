"""Regenerate the universal obstruction and its local-instability dependency."""

from __future__ import annotations

import argparse
import json
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
        text = json.dumps(builder(), indent=2) + "\n"
        if args.check:
            tracked = certificate_path.read_text(encoding="utf-8")
            if tracked != text:
                raise SystemExit(f"certificate drift: {display_path}")
            print(f"ok: {display_path}")
        else:
            certificate_path.parent.mkdir(parents=True, exist_ok=True)
            certificate_path.write_text(text, encoding="utf-8")
            print(f"wrote {display_path}")


if __name__ == "__main__":
    main()
