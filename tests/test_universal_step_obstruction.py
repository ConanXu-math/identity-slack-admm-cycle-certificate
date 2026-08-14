from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE_NAMES = (
    "identity_slack_small_step_local_instability.json",
    "identity_slack_universal_step_obstruction.json",
)


class UniversalStepObstructionVerifierTests(unittest.TestCase):
    def test_check_rejects_drift_in_companion_certificate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            certificate_dir = Path(temporary_directory)
            for name in CERTIFICATE_NAMES:
                shutil.copy2(
                    ROOT / "certificates" / name,
                    certificate_dir / name,
                )
            (certificate_dir / CERTIFICATE_NAMES[0]).write_text(
                "{}\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "python" / "verify_universal_step_obstruction.py"),
                    "--check",
                    "--certificate-dir",
                    str(certificate_dir),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(CERTIFICATE_NAMES[0], result.stderr)


if __name__ == "__main__":
    unittest.main()
