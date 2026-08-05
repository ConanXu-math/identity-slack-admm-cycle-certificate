"""Regenerate the universal relative-step obstruction certificate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import analyze_identity_slack_universal_step_obstruction as obstruction


HERE = Path(__file__).resolve().parent
CERTIFICATE_PATH = (
    HERE.parent / "certificates" / "identity_slack_universal_step_obstruction.json"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail unless the regenerated certificate matches the tracked file",
    )
    args = parser.parse_args()
    payload = obstruction.exact_certificate()
    text = json.dumps(payload, indent=2) + "\n"
    if args.check:
        tracked = CERTIFICATE_PATH.read_text(encoding="utf-8")
        if tracked != text:
            raise SystemExit(
                f"certificate drift: regenerate with "
                f"python python/analyze_identity_slack_universal_step_obstruction.py"
            )
        print(f"ok: {CERTIFICATE_PATH.relative_to(HERE.parent)}")
        return
    CERTIFICATE_PATH.write_text(text, encoding="utf-8")
    print(f"wrote {CERTIFICATE_PATH.relative_to(HERE.parent)}")


if __name__ == "__main__":
    main()
