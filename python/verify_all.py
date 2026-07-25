"""Run the frozen period-66 and period-23 certificate verifiers."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
VERIFIERS = (
    ("period66", REPOSITORY_ROOT / "python" / "verify_certificate_pair.py"),
    (
        "period23",
        REPOSITORY_ROOT / "python" / "verify_period23_certificate.py",
    ),
)


def _run_verifier(name: str, script: Path) -> dict[str, object]:
    if not script.is_file():
        relative_script = script.relative_to(REPOSITORY_ROOT)
        message = f"required verifier is missing: {relative_script}"
        print(message, file=sys.stderr)
        return {
            "name": name,
            "returncode": 2,
            "status": "missing",
        }

    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    if completed.returncode != 0:
        if completed.stdout:
            print(completed.stdout, end="", file=sys.stderr)
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)

    return {
        "name": name,
        "returncode": completed.returncode,
        "status": "passed" if completed.returncode == 0 else "failed",
    }


def main() -> int:
    checks: list[dict[str, object]] = []
    for name, script in VERIFIERS:
        result = _run_verifier(name, script)
        checks.append(result)
        returncode = int(result["returncode"])
        if returncode != 0:
            print(
                json.dumps(
                    {
                        "checks": checks,
                        "failed": name,
                        "valid": False,
                    },
                    sort_keys=True,
                )
            )
            return returncode if returncode > 0 else 1

    print(json.dumps({"checks": checks, "valid": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
