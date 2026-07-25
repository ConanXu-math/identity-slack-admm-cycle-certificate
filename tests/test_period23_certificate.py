"""Regression tests for the frozen period-23 exact certificate."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY / "python" / "verify_period23_certificate.py"
SOURCE = REPOSITORY / "certificates" / "period23_source_binary64.npz"
FROZEN_CERTIFICATE = (
    REPOSITORY / "certificates" / "period23_certificate.json"
)
FROZEN_MANIFEST = (
    REPOSITORY / "certificates" / "period23_instance_manifest.json"
)

SPEC = importlib.util.spec_from_file_location("period23_verifier", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import verifier from {SCRIPT}")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class Period23CertificateTests(unittest.TestCase):
    def test_generated_payloads_match_frozen_artifacts(self) -> None:
        certificate = VERIFIER.certificate_payload(SOURCE)
        manifest = VERIFIER.instance_manifest(certificate, SOURCE)

        self.assertTrue(certificate["valid"])
        self.assertTrue(all(certificate["checks"].values()))
        self.assertEqual(certificate["period"], 23)
        self.assertTrue(manifest["valid"])
        self.assertEqual(
            json.loads(FROZEN_CERTIFICATE.read_text(encoding="utf-8")),
            certificate,
        )
        self.assertEqual(
            json.loads(FROZEN_MANIFEST.read_text(encoding="utf-8")),
            manifest,
        )
        self.assertNotIn("elapsed", json.dumps(certificate).lower())
        self.assertEqual(
            set(manifest["source_arrays"]),
            set(VERIFIER.EXPECTED_ARRAYS),
        )

    def test_corrupted_source_exits_nonzero_without_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            corrupted = bytearray(SOURCE.read_bytes())
            corrupted[0] ^= 0xFF
            corrupted_source = temporary / "corrupted.npz"
            corrupted_source.write_bytes(corrupted)
            certificate_output = temporary / "certificate.json"
            manifest_output = temporary / "manifest.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source",
                    str(corrupted_source),
                    "--certificate-output",
                    str(certificate_output),
                    "--manifest-output",
                    str(manifest_output),
                ],
                capture_output=True,
                check=False,
                text=True,
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(certificate_output.exists())
            self.assertFalse(manifest_output.exists())


if __name__ == "__main__":
    unittest.main()
