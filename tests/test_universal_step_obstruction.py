from __future__ import annotations

import json
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


def copy_certificates(certificate_dir: Path) -> None:
    for name in CERTIFICATE_NAMES:
        shutil.copy2(ROOT / "certificates" / name, certificate_dir / name)


def run_check(certificate_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
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


class UniversalStepObstructionVerifierTests(unittest.TestCase):
    def test_check_accepts_sub_tolerance_spectral_radius_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            certificate_dir = Path(temporary_directory)
            copy_certificates(certificate_dir)
            companion_path = certificate_dir / CERTIFICATE_NAMES[0]
            companion = json.loads(companion_path.read_text(encoding="utf-8"))
            companion["numeric_sanity_checks"][0]["spectral_radius"] += 5e-13
            companion["strict_rational_sanity_checks"][0][
                "spectral_radius"
            ] += 5e-13
            companion_path.write_text(
                json.dumps(companion, indent=2) + "\n",
                encoding="utf-8",
            )

            result = run_check(certificate_dir)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_rejects_material_spectral_radius_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            certificate_dir = Path(temporary_directory)
            copy_certificates(certificate_dir)
            companion_path = certificate_dir / CERTIFICATE_NAMES[0]
            companion = json.loads(companion_path.read_text(encoding="utf-8"))
            companion["numeric_sanity_checks"][0]["spectral_radius"] += 2e-12
            companion_path.write_text(
                json.dumps(companion, indent=2) + "\n",
                encoding="utf-8",
            )

            result = run_check(certificate_dir)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(CERTIFICATE_NAMES[0], result.stderr)

    def test_check_rejects_material_strict_spectral_radius_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            certificate_dir = Path(temporary_directory)
            copy_certificates(certificate_dir)
            companion_path = certificate_dir / CERTIFICATE_NAMES[0]
            companion = json.loads(companion_path.read_text(encoding="utf-8"))
            companion["strict_rational_sanity_checks"][0][
                "spectral_radius"
            ] += 2e-12
            companion_path.write_text(
                json.dumps(companion, indent=2) + "\n",
                encoding="utf-8",
            )

            result = run_check(certificate_dir)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(CERTIFICATE_NAMES[0], result.stderr)

    def test_check_rejects_sub_tolerance_non_radius_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            certificate_dir = Path(temporary_directory)
            copy_certificates(certificate_dir)
            companion_path = certificate_dir / CERTIFICATE_NAMES[0]
            companion = json.loads(companion_path.read_text(encoding="utf-8"))
            companion["numeric_sanity_checks"][0]["theta"] += 5e-13
            companion_path.write_text(
                json.dumps(companion, indent=2) + "\n",
                encoding="utf-8",
            )

            result = run_check(certificate_dir)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(CERTIFICATE_NAMES[0], result.stderr)

    def test_check_rejects_nonfinite_spectral_radius(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            certificate_dir = Path(temporary_directory)
            copy_certificates(certificate_dir)
            companion_path = certificate_dir / CERTIFICATE_NAMES[0]
            companion = json.loads(companion_path.read_text(encoding="utf-8"))
            companion["numeric_sanity_checks"][0]["spectral_radius"] = float(
                "nan"
            )
            companion_path.write_text(
                json.dumps(companion, indent=2) + "\n",
                encoding="utf-8",
            )

            result = run_check(certificate_dir)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(CERTIFICATE_NAMES[0], result.stderr)

    def test_check_rejects_exact_symbolic_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            certificate_dir = Path(temporary_directory)
            copy_certificates(certificate_dir)
            companion_path = certificate_dir / CERTIFICATE_NAMES[0]
            companion = json.loads(companion_path.read_text(encoding="utf-8"))
            companion["quartic_numerator"] += " + 1"
            companion_path.write_text(
                json.dumps(companion, indent=2) + "\n",
                encoding="utf-8",
            )

            result = run_check(certificate_dir)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(CERTIFICATE_NAMES[0], result.stderr)

    def test_check_rejects_drift_in_companion_certificate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            certificate_dir = Path(temporary_directory)
            copy_certificates(certificate_dir)
            (certificate_dir / CERTIFICATE_NAMES[0]).write_text(
                "{}\n",
                encoding="utf-8",
            )

            result = run_check(certificate_dir)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(CERTIFICATE_NAMES[0], result.stderr)


if __name__ == "__main__":
    unittest.main()
