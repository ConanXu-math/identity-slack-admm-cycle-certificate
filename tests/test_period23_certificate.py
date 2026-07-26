"""Regression tests for the canonical rational period-23 certificate."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY / "python" / "verify_period23_certificate.py"
SOURCE = REPOSITORY / "certificates" / "period23_instance.json"
FROZEN_CERTIFICATE = (
    REPOSITORY / "certificates" / "period23_certificate.json"
)

SPEC = importlib.util.spec_from_file_location("period23_verifier", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import verifier from {SCRIPT}")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class Period23CertificateTests(unittest.TestCase):
    def test_generated_certificate_matches_frozen_artifact(self) -> None:
        certificate = VERIFIER.verify_instance(SOURCE)

        self.assertTrue(certificate["valid"])
        self.assertEqual(
            certificate["schema"],
            "identity_slack_p23_rational_certificate_v1",
        )
        self.assertEqual(
            certificate["instance_id"],
            "identity_slack_p23_rational_v1",
        )
        self.assertTrue(all(certificate["exact_checks"].values()))
        self.assertEqual(certificate["input"]["maximum_denominator"], 100)
        self.assertEqual(
            certificate["periodic_orbit_certificate"]["phase_state_count"],
            23,
        )
        initialization = certificate["periodic_orbit_certificate"][
            "phase_zero_initialization"
        ]
        self.assertEqual(initialization["phase_zero_mask"], [1, 0, 1])
        exact_initialization = initialization["exact"]
        self.assertEqual(
            VERIFIER.canonical_vector_digest(
                [
                    Fraction(value)
                    for value in (
                        exact_initialization["y"]
                        + exact_initialization["t_z_plus_lambda"]
                    )
                ]
            ),
            certificate["return_map_certificate"][
                "phase_zero_exact_sha256"
            ],
        )
        t_values = [
            Fraction(value)
            for value in exact_initialization["t_z_plus_lambda"]
        ]
        self.assertEqual(
            [
                Fraction(value)
                for value in exact_initialization["z"]
            ],
            [max(value, 0) for value in t_values],
        )
        self.assertEqual(
            [
                Fraction(value)
                for value in exact_initialization[
                    "lambda_repo_sign_convention"
                ]
            ],
            [min(value, 0) for value in t_values],
        )
        self.assertEqual(
            [
                Fraction(z_value) + Fraction(lambda_value)
                for z_value, lambda_value in zip(
                    exact_initialization["z"],
                    exact_initialization[
                        "lambda_repo_sign_convention"
                    ],
                    strict=True,
                )
            ],
            [
                Fraction(value)
                for value in exact_initialization["t_z_plus_lambda"]
            ],
        )
        self.assertEqual(
            initialization["decimal_display_only"]["y"],
            [
                "0.227998838986",
                "-1.06559716363",
                "-0.727978937701",
            ],
        )
        self.assertGreater(
            certificate["periodic_orbit_certificate"][
                "minimum_projection_margin"
            ]["decimal"],
            1 / 250,
        )
        self.assertGreater(
            certificate["support_radius_certificate"]["rbar2"]["decimal"],
            1 / 4000,
        )
        self.assertNotIn(
            "rbar2_gt_1_over_2000",
            certificate["support_radius_certificate"],
        )
        self.assertEqual(
            certificate["numerical_display_only"]["spectral_radius"],
            0.770847536821,
        )
        self.assertFalse(certificate["verifier"]["external_npz_read"])
        self.assertEqual(
            json.loads(FROZEN_CERTIFICATE.read_text(encoding="utf-8")),
            certificate,
        )

    def test_noncanonical_fraction_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            payload = json.loads(SOURCE.read_text(encoding="utf-8"))
            payload["A"][0][0] = "0.5"
            corrupted_source = temporary / "period23_instance.json"
            corrupted_source.write_text(
                json.dumps(payload, indent=2) + "\n",
                encoding="utf-8",
            )
            certificate_output = temporary / "certificate.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(corrupted_source),
                    "--output",
                    str(certificate_output),
                ],
                capture_output=True,
                check=False,
                text=True,
            )

            self.assertNotEqual(completed.returncode, 0)
            certificate = json.loads(
                certificate_output.read_text(encoding="utf-8")
            )
            self.assertFalse(certificate["valid"])
            self.assertFalse(
                certificate["aggregate"]["all_exact_checks_pass"]
            )

    def test_root_acceptance_surface_has_one_period23_instance(self) -> None:
        self.assertTrue(SOURCE.is_file())
        self.assertFalse(
            (
                REPOSITORY
                / "certificates"
                / "period23_source_binary64.npz"
            ).exists()
        )
        self.assertFalse(
            (
                REPOSITORY
                / "certificates"
                / "period23_instance_manifest.json"
            ).exists()
        )
        for relative_path in (
            "README.md",
            "README.zh-CN.md",
            "docs/REPRODUCIBILITY.md",
            "python/README.md",
            "provenance/README.md",
            "provenance/comparison_scope.yaml",
            "provenance/routes/kimi-period23/README.md",
            "provenance/routes/kimi-period23/retained_artifacts.json",
        ):
            text = (REPOSITORY / relative_path).read_text(encoding="utf-8")
            lowered = text.lower()
            self.assertNotIn("identity_slack_p23_dyadic_v1", lowered)
            self.assertNotIn("later companion", lowered)
            self.assertNotIn("subsequent companion", lowered)


if __name__ == "__main__":
    unittest.main()
