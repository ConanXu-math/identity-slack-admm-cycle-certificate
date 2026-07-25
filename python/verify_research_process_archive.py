"""Verify the deterministic research-process archive manifest and privacy gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_ROOT = REPOSITORY_ROOT / "research-process"
MANIFEST = ARCHIVE_ROOT / "manifest.json"
TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".md",
    ".py",
    ".svg",
    ".txt",
    ".yaml",
    ".yml",
}
FORBIDDEN_TEXT_PATTERNS = (
    re.compile(r"/Users/"),
    re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?<![A-Za-z0-9])gh[opsu]_[A-Za-z0-9]{12,}"),
    re.compile(r"BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY"),
)
REQUIRED_PATHS = {
    "README.md",
    "codex-period66/research_state.md",
    "codex-period66/outputs/breakthrough_attempts/"
    "stage43_to_stage44_discovery/search.json",
    "codex-period66/outputs/breakthrough_attempts/"
    "stage44_strict_rational_66_cycle/certificate.json",
    "codex-period66/outputs/breakthrough_attempts/"
    "stage45_independent_raw_admm_audit/certificate.json",
    "codex-period66/outputs/breakthrough_attempts/"
    "stage46_decimal_precision_audit/certificate.json",
    "kimi-period23/START_GOAL.txt",
    "kimi-period23/RESEARCH_LOG.md",
    "kimi-period23/research/09_counterexample.md",
    "kimi-period23/experiments/exp17c_selfcontained.py",
    "kimi-period23/experiments/exp19b_exact_yt.py",
    "kimi-period23/experiments/results/exp19_certificate.json",
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_manifest() -> dict[str, object]:
    files: list[dict[str, object]] = []
    suffix_counts: Counter[str] = Counter()
    route_counts: Counter[str] = Counter()
    forbidden_hits: list[dict[str, object]] = []

    for path in sorted(ARCHIVE_ROOT.rglob("*")):
        if not path.is_file() or path == MANIFEST:
            continue
        relative = path.relative_to(ARCHIVE_ROOT).as_posix()
        data = path.read_bytes()
        suffix = path.suffix.lower() or "[none]"
        route = (
            relative.split("/", maxsplit=1)[0]
            if "/" in relative
            else "[root]"
        )
        suffix_counts[suffix] += 1
        route_counts[route] += 1
        files.append(
            {
                "path": relative,
                "bytes": len(data),
                "sha256": _sha256(data),
            }
        )

        if suffix in TEXT_SUFFIXES:
            text = data.decode("utf-8")
            for pattern in FORBIDDEN_TEXT_PATTERNS:
                for match in pattern.finditer(text):
                    forbidden_hits.append(
                        {
                            "path": relative,
                            "line": text.count("\n", 0, match.start()) + 1,
                            "pattern": pattern.pattern,
                        }
                    )

    retained_paths = {str(entry["path"]) for entry in files}
    missing_paths = sorted(REQUIRED_PATHS - retained_paths)
    return {
        "schema_version": 1,
        "archive_type": "curated_agent_research_process",
        "claim_boundary": (
            "Historical process evidence; root exact certificates and "
            "verifiers remain the mathematical acceptance layer."
        ),
        "excluded": [
            "raw chats and session JSONL",
            "credentials and private configuration",
            "user-specific absolute paths",
            "caches and virtual environments",
            "installed third-party skills",
            "teacher-provided images",
            "repetitive bulk outputs outside the selected decision path",
        ],
        "summary": {
            "file_count": len(files),
            "total_bytes": sum(int(entry["bytes"]) for entry in files),
            "route_counts": dict(sorted(route_counts.items())),
            "suffix_counts": dict(sorted(suffix_counts.items())),
        },
        "checks": {
            "forbidden_text_hits": forbidden_hits,
            "missing_required_paths": missing_paths,
        },
        "files": files,
        "valid": not forbidden_hits and not missing_paths,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="rewrite the deterministic manifest before verification",
    )
    args = parser.parse_args()

    payload = build_manifest()
    if args.write:
        MANIFEST.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if not MANIFEST.is_file():
        print(
            json.dumps(
                {
                    "error": "research-process/manifest.json is missing",
                    "valid": False,
                },
                sort_keys=True,
            )
        )
        return 2

    frozen = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_matches = frozen == payload
    valid = bool(payload["valid"]) and manifest_matches
    print(
        json.dumps(
            {
                "file_count": payload["summary"]["file_count"],
                "manifest_matches": manifest_matches,
                "privacy_and_required_paths_valid": payload["valid"],
                "valid": valid,
            },
            sort_keys=True,
        )
    )
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
