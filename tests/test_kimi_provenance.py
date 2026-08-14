from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class KimiProvenanceTests(unittest.TestCase):
    @staticmethod
    def _rehash_route_file(route_dir: Path, relative_path: str) -> None:
        manifest_path = route_dir / "provenance_manifest.json"
        manifest = json.loads(manifest_path.read_text())
        entry = next(
            item for item in manifest["files"] if item["path"] == relative_path
        )
        payload = (route_dir / relative_path).read_bytes()
        entry["bytes"] = len(payload)
        entry["sha256"] = hashlib.sha256(payload).hexdigest()
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_public_package_verifies(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "python" / "verify_kimi_provenance.py"),
                "--check",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["route_id"], "kimi-period23")

    def test_raw_session_derivation_emits_sanitized_events(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            session_root = Path(temporary_directory) / "session"
            for agent in ("main", "agent-0", "agent-1", "agent-2"):
                (session_root / "agents" / agent).mkdir(parents=True)
            (session_root / "logs").mkdir()
            (session_root / "logs" / "kimi-code.log").write_text(
                "synthetic fixture\n",
                encoding="utf-8",
            )
            (session_root / "state.json").write_text(
                json.dumps(
                    {
                        "createdAt": "2026-07-22T00:00:00.000Z",
                        "agents": {
                            "main": {},
                            "agent-0": {},
                            "agent-1": {},
                            "agent-2": {},
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            metadata = {
                "type": "metadata",
                "protocol_version": "1.4",
                "created_at": 1000,
            }
            for agent in ("agent-0", "agent-1", "agent-2"):
                (session_root / "agents" / agent / "wire.jsonl").write_text(
                    json.dumps(metadata) + "\n",
                    encoding="utf-8",
                )

            main_records = [
                metadata,
                {
                    "type": "turn.prompt",
                    "time": 1001,
                    "origin": {"kind": "user"},
                    "input": [{"type": "text", "text": "initial prompt\n"}],
                },
                {
                    "type": "llm.request",
                    "time": 1010,
                    "provider": "kimi",
                    "model": "kimi-k3",
                    "modelAlias": "moonshot-cn/kimi-k3",
                    "thinkingEffort": "high",
                    "turnStep": 1,
                },
                {
                    "type": "context.append_loop_event",
                    "time": 1010,
                    "event": {"type": "step.begin", "uuid": "step-1"},
                },
                {
                    "type": "context.append_loop_event",
                    "time": 1020,
                    "event": {"type": "step.end", "uuid": "step-1"},
                },
                {
                    "type": "usage.record",
                    "time": 1020,
                    "model": "moonshot-cn/kimi-k3",
                    "usage": {
                        "inputCacheCreation": 0,
                        "inputCacheRead": 3,
                        "inputOther": 5,
                        "output": 7,
                    },
                },
                {
                    "type": "context.append_loop_event",
                    "time": 1030,
                    "event": {
                        "type": "tool.call",
                        "name": "Write",
                        "toolCallId": "Write_1",
                        "args": {
                            "path": "experiments/exp19b_exact_yt.py",
                            "content": "print('ok')\n",
                        },
                    },
                },
                {
                    "type": "context.append_loop_event",
                    "time": 1040,
                    "event": {
                        "type": "tool.call",
                        "name": "Bash",
                        "toolCallId": "Bash_1",
                        "args": {"command": "python3 -u exp19b_exact_yt.py"},
                    },
                },
                {
                    "type": "context.append_loop_event",
                    "time": 1050,
                    "event": {
                        "type": "tool.result",
                        "toolCallId": "Bash_1",
                        "result": {"output": "ok\n"},
                    },
                },
            ]
            main_wire = session_root / "agents" / "main" / "wire.jsonl"
            main_wire.write_text(
                "".join(json.dumps(record) + "\n" for record in main_records),
                encoding="utf-8",
            )
            ledger = Path(temporary_directory) / "events.jsonl"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "python" / "verify_kimi_provenance.py"),
                    "--derive-ledger",
                    "--raw-session-root",
                    str(session_root),
                    "--ledger-output",
                    str(ledger),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            events = [json.loads(line) for line in ledger.read_text().splitlines()]
            counts = {
                kind: sum(event["record_type"] == kind for event in events)
                for kind in ("llm_request", "usage", "step_interval", "human_input")
            }
            self.assertEqual(
                counts,
                {"llm_request": 1, "usage": 1, "step_interval": 1, "human_input": 1},
            )
            endpoint = next(
                event for event in events if event["record_type"] == "endpoint"
            )
            self.assertEqual(endpoint["time_unix_ms"], 1050)
            self.assertEqual(endpoint["endpoint_tool_call_id"], "Bash_1")

    def test_usage_drift_fails_after_manifest_is_rehashed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            route_dir = Path(temporary_directory) / "kimi-period23"
            shutil.copytree(
                ROOT / "provenance" / "routes" / "kimi-period23",
                route_dir,
            )
            ledger = route_dir / "session_audit_events.jsonl"
            events = [json.loads(line) for line in ledger.read_text().splitlines()]
            usage = next(event for event in events if event["record_type"] == "usage")
            usage["usage"]["output"] += 1
            ledger.write_text(
                "".join(
                    json.dumps(
                        event,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    + "\n"
                    for event in events
                ),
                encoding="utf-8",
            )

            self._rehash_route_file(route_dir, "session_audit_events.jsonl")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "python" / "verify_kimi_provenance.py"),
                    "--route-dir",
                    str(route_dir),
                    "--check",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("usage", result.stderr.lower())

    def test_human_input_text_must_match_its_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            route_dir = Path(temporary_directory) / "kimi-period23"
            shutil.copytree(
                ROOT / "provenance" / "routes" / "kimi-period23",
                route_dir,
            )
            ledger = route_dir / "session_audit_events.jsonl"
            events = [json.loads(line) for line in ledger.read_text().splitlines()]
            human_input = next(
                event
                for event in events
                if event.get("record_type") == "human_input"
            )
            human_input["text"] = "COMPLETELY DIFFERENT PROMPT"
            ledger.write_text(
                "".join(
                    json.dumps(
                        event,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    + "\n"
                    for event in events
                ),
                encoding="utf-8",
            )
            self._rehash_route_file(route_dir, "session_audit_events.jsonl")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "python" / "verify_kimi_provenance.py"),
                    "--route-dir",
                    str(route_dir),
                    "--check",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("human input text hash", result.stderr.lower())

    def test_attestation_must_satisfy_published_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            route_dir = Path(temporary_directory) / "kimi-period23"
            shutil.copytree(
                ROOT / "provenance" / "routes" / "kimi-period23",
                route_dir,
            )
            attestation_path = route_dir / "run_attestation.json"
            attestation = json.loads(attestation_path.read_text())
            attestation["route_id"] = "wrong-route"
            attestation_path.write_text(
                json.dumps(attestation, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            self._rehash_route_file(route_dir, "run_attestation.json")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "python" / "verify_kimi_provenance.py"),
                    "--route-dir",
                    str(route_dir),
                    "--check",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("schema", result.stderr.lower())

    def test_attestation_verifier_version_is_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            route_dir = Path(temporary_directory) / "kimi-period23"
            shutil.copytree(
                ROOT / "provenance" / "routes" / "kimi-period23",
                route_dir,
            )
            attestation_path = route_dir / "run_attestation.json"
            attestation = json.loads(attestation_path.read_text())
            attestation["observer_manifest_reconciliation"][
                "verifier_version"
            ] = "0.0.0"
            attestation_path.write_text(
                json.dumps(attestation, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            self._rehash_route_file(route_dir, "run_attestation.json")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "python" / "verify_kimi_provenance.py"),
                    "--route-dir",
                    str(route_dir),
                    "--check",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("verifier_version", result.stderr.lower())

    def test_unknown_ledger_record_type_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            route_dir = Path(temporary_directory) / "kimi-period23"
            shutil.copytree(
                ROOT / "provenance" / "routes" / "kimi-period23",
                route_dir,
            )
            ledger = route_dir / "session_audit_events.jsonl"
            with ledger.open("a", encoding="utf-8") as stream:
                stream.write(
                    json.dumps(
                        {
                            "record_type": "assistant_chat",
                            "text": "undeclared raw chat",
                        },
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    + "\n"
                )
            self._rehash_route_file(route_dir, "session_audit_events.jsonl")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "python" / "verify_kimi_provenance.py"),
                    "--route-dir",
                    str(route_dir),
                    "--check",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown ledger record type", result.stderr.lower())

    def test_endpoint_command_is_part_of_the_attested_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            route_dir = Path(temporary_directory) / "kimi-period23"
            shutil.copytree(
                ROOT / "provenance" / "routes" / "kimi-period23",
                route_dir,
            )
            ledger = route_dir / "session_audit_events.jsonl"
            events = [json.loads(line) for line in ledger.read_text().splitlines()]
            endpoint = next(
                event for event in events if event["record_type"] == "endpoint"
            )
            endpoint["command"] = "different-command"
            ledger.write_text(
                "".join(
                    json.dumps(
                        event,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    + "\n"
                    for event in events
                ),
                encoding="utf-8",
            )
            self._rehash_route_file(route_dir, "session_audit_events.jsonl")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "python" / "verify_kimi_provenance.py"),
                    "--route-dir",
                    str(route_dir),
                    "--check",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("endpoint command", result.stderr.lower())

    def test_session_topology_must_match_ledger_and_accounting(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            route_dir = Path(temporary_directory) / "kimi-period23"
            shutil.copytree(
                ROOT / "provenance" / "routes" / "kimi-period23",
                route_dir,
            )
            attestation_path = route_dir / "run_attestation.json"
            attestation = json.loads(attestation_path.read_text())
            attestation["session"]["topology"] = {
                "main_sessions": 99,
                "subagents": 0,
                "agent_labels": ["fake"],
            }
            attestation_path.write_text(
                json.dumps(attestation, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            self._rehash_route_file(route_dir, "run_attestation.json")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "python" / "verify_kimi_provenance.py"),
                    "--route-dir",
                    str(route_dir),
                    "--check",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("topology", result.stderr.lower())

    def test_accounting_timing_and_paper_values_are_recomputed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            route_dir = Path(temporary_directory) / "kimi-period23"
            shutil.copytree(
                ROOT / "provenance" / "routes" / "kimi-period23",
                route_dir,
            )
            accounting_path = route_dir / "accounting.json"
            accounting = json.loads(accounting_path.read_text())
            accounting["audited_route_endpoint"]["timing_hours"][
                "merged_active_wall"
            ] = 999
            accounting["paper_reported_accounting"][
                "approximate_run_time_hours"
            ]["value"] = 999
            accounting_path.write_text(
                json.dumps(accounting, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            self._rehash_route_file(route_dir, "accounting.json")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "python" / "verify_kimi_provenance.py"),
                    "--route-dir",
                    str(route_dir),
                    "--check",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("accounting timing", result.stderr.lower())

    def test_start_archive_derivation_hashes_private_teacher_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            archive = Path(temporary_directory) / "start.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("workspace/START_GOAL.txt", "goal\n")
                bundle.writestr(
                    "workspace/inputs/teacher_slides/image-1.png",
                    b"synthetic image bytes",
                )
            output = Path(temporary_directory) / "start_manifest.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "python" / "verify_kimi_provenance.py"),
                    "--derive-start-manifest",
                    "--start-archive",
                    str(archive),
                    "--start-manifest-output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads(output.read_text())
            self.assertEqual(manifest["file_entry_count"], 2)
            self.assertEqual(manifest["zip_member_count"], 2)
            slide = next(
                entry
                for entry in manifest["files"]
                if entry["path"] == "inputs/teacher_slides/image-1.png"
            )
            self.assertFalse(slide["content_public"])
            self.assertEqual(slide["bytes"], len(b"synthetic image bytes"))


if __name__ == "__main__":
    unittest.main()
