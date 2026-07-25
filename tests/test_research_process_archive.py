"""Regression tests for the curated agent research-process archive."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY / "python" / "verify_research_process_archive.py"
MANIFEST = REPOSITORY / "research-process" / "manifest.json"


class ResearchProcessArchiveTests(unittest.TestCase):
    def test_manifest_and_privacy_gate(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPOSITORY,
            capture_output=True,
            check=False,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["valid"])
        self.assertTrue(result["manifest_matches"])
        self.assertGreaterEqual(result["file_count"], 160)

    def test_archive_preserves_both_research_arcs(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertTrue(manifest["valid"])
        route_counts = manifest["summary"]["route_counts"]
        self.assertGreaterEqual(route_counts["codex-period66"], 70)
        self.assertGreaterEqual(route_counts["kimi-period23"], 65)
        suffix_counts = manifest["summary"]["suffix_counts"]
        self.assertGreaterEqual(suffix_counts[".md"], 50)
        self.assertGreaterEqual(suffix_counts[".py"], 50)
        self.assertEqual(suffix_counts[".npz"], 9)


if __name__ == "__main__":
    unittest.main()
