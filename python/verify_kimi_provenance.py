#!/usr/bin/env python3
"""Verify and, with private inputs, rederive the sanitized Kimi run record."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPOSITORY = Path(__file__).resolve().parents[1]
DEFAULT_ROUTE_DIR = REPOSITORY / "provenance" / "routes" / "kimi-period23"
LEDGER_NAME = "session_audit_events.jsonl"
ROUTE_MANIFEST_NAME = "provenance_manifest.json"
ENDPOINT_COMMAND = "python3 -u exp19b_exact_yt.py"
ENDPOINT_SCRIPT_SUFFIX = "experiments/exp19b_exact_yt.py"
GENERIC_CONTINUE_PROMPT = "/goal 继续，理论证明和反例搜索并行"
VERIFIER_VERSION = "1.1.0"
SANITIZER_VERSION = "1.0.0"
USAGE_FIELDS = (
    ("inputCacheCreation", "input_cache_creation"),
    ("inputCacheRead", "input_cache_read"),
    ("inputOther", "input_other"),
    ("output", "output"),
)
LEDGER_FIELDS = {
    "metadata": {
        "record_type",
        "schema_version",
        "sanitizer_version",
        "wire_protocol_versions",
        "session_created_utc",
        "agent_labels",
        "incomplete_step_begins",
        "privacy_boundary",
    },
    "endpoint": {
        "record_type",
        "time_unix_ms",
        "command",
        "endpoint_tool_call_id",
        "endpoint_script_write_call_id",
        "script_bytes",
        "script_sha256",
        "stdout_bytes",
        "stdout_sha256",
    },
    "raw_file_hash": {"record_type", "path", "bytes", "sha256"},
    "llm_request": {
        "record_type",
        "agent",
        "time_unix_ms",
        "provider",
        "model_id",
        "model_alias",
        "thinking_effort",
        "turn_step",
    },
    "usage": {
        "record_type",
        "agent",
        "time_unix_ms",
        "model_alias",
        "usage",
    },
    "step_interval": {
        "record_type",
        "agent",
        "interval_id",
        "begin_unix_ms",
        "end_unix_ms",
    },
    "human_input": {
        "record_type",
        "time_unix_ms",
        "event_kind",
        "classification",
        "text",
        "text_sha256",
    },
}


class ProvenanceError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProvenanceError(f"cannot read JSON {path}: {exc}") from exc


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ProvenanceError(
                    f"{path}:{line_number} is not a JSON object"
                )
            records.append(value)
    except (OSError, json.JSONDecodeError) as exc:
        raise ProvenanceError(f"cannot read JSONL {path}: {exc}") from exc
    return records


def validate_ledger_records(records: list[dict[str, Any]]) -> None:
    for index, record in enumerate(records, start=1):
        record_type = record.get("record_type")
        if not isinstance(record_type, str) or record_type not in LEDGER_FIELDS:
            raise ProvenanceError(
                f"unknown ledger record type at record {index}: {record_type!r}"
            )
        expected_fields = LEDGER_FIELDS[record_type]
        actual_fields = set(record)
        if actual_fields != expected_fields:
            missing = sorted(expected_fields - actual_fields)
            extra = sorted(actual_fields - expected_fields)
            raise ProvenanceError(
                f"ledger {record_type} fields mismatch at record {index}: "
                f"missing={missing}, extra={extra}"
            )
        if record_type == "human_input":
            text = record["text"]
            text_hash = record["text_sha256"]
            if not isinstance(text, str) or not isinstance(text_hash, str):
                raise ProvenanceError(
                    f"human input text/hash has invalid type at record {index}"
                )
            derived_hash = sha256_bytes(text.encode("utf-8"))
            if derived_hash != text_hash:
                raise ProvenanceError(
                    f"human input text hash mismatch at record {index}"
                )
        elif record_type == "usage":
            usage = record["usage"]
            expected_usage_fields = {target for _, target in USAGE_FIELDS}
            if not isinstance(usage, dict) or set(usage) != expected_usage_fields:
                raise ProvenanceError(
                    f"usage fields mismatch at ledger record {index}"
                )
        elif record_type == "raw_file_hash":
            digest = record["sha256"]
            if not isinstance(digest, str) or re.fullmatch(
                r"[0-9a-f]{64}", digest
            ) is None:
                raise ProvenanceError(
                    f"raw-file hash is invalid at ledger record {index}"
                )

    endpoints = [
        record for record in records if record["record_type"] == "endpoint"
    ]
    if len(endpoints) != 1 or not isinstance(
        endpoints[0]["time_unix_ms"], int
    ):
        raise ProvenanceError(
            f"expected one ledger endpoint, found {len(endpoints)}"
        )
    endpoint_time = endpoints[0]["time_unix_ms"]
    human_inputs = [
        record for record in records if record["record_type"] == "human_input"
    ]
    prompt_times = [
        record["time_unix_ms"]
        for record in human_inputs
        if record["event_kind"] == "prompt"
        and isinstance(record["time_unix_ms"], int)
    ]
    if not prompt_times:
        raise ProvenanceError("ledger has no human prompt")
    first_prompt_time = min(prompt_times)
    for index, record in enumerate(human_inputs, start=1):
        event_kind = record["event_kind"]
        time_unix_ms = record["time_unix_ms"]
        if event_kind not in {"prompt", "steer"} or not isinstance(
            time_unix_ms, int
        ):
            raise ProvenanceError(
                f"human input event kind/time is invalid at input {index}"
            )
        expected_classification = classify_human_input(
            event_kind=event_kind,
            text=record["text"],
            time_unix_ms=time_unix_ms,
            endpoint_unix_ms=endpoint_time,
            is_first_prompt=(
                event_kind == "prompt" and time_unix_ms == first_prompt_time
            ),
        )
        if record["classification"] != expected_classification:
            raise ProvenanceError(
                f"human input classification mismatch at input {index}"
            )


def validate_json_schema(
    value: Any,
    schema: dict[str, Any],
    *,
    path: str = "$",
) -> None:
    if not isinstance(schema, dict):
        raise ProvenanceError(f"schema at {path} is not an object")
    if "const" in schema and value != schema["const"]:
        raise ProvenanceError(
            f"schema const mismatch at {path}: "
            f"expected={schema['const']!r}, actual={value!r}"
        )
    expected_type = schema.get("type")
    type_checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float))
        and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    if expected_type is not None:
        check = type_checks.get(expected_type)
        if check is None:
            raise ProvenanceError(
                f"schema at {path} uses unsupported type {expected_type!r}"
            )
        if not check(value):
            raise ProvenanceError(
                f"schema type mismatch at {path}: expected {expected_type}"
            )
    if isinstance(value, dict):
        minimum = schema.get("minProperties")
        if minimum is not None and (
            not isinstance(minimum, int) or len(value) < minimum
        ):
            raise ProvenanceError(
                f"schema minProperties mismatch at {path}"
            )
        required = schema.get("required", [])
        if not isinstance(required, list) or not all(
            isinstance(key, str) for key in required
        ):
            raise ProvenanceError(f"schema required list is invalid at {path}")
        missing = [key for key in required if key not in value]
        if missing:
            raise ProvenanceError(
                f"schema required fields missing at {path}: {missing}"
            )
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            raise ProvenanceError(f"schema properties is invalid at {path}")
        for key, child_schema in properties.items():
            if key in value:
                validate_json_schema(
                    value[key],
                    child_schema,
                    path=f"{path}.{key}",
                )
        additional = schema.get("additionalProperties", True)
        extra_keys = set(value) - set(properties)
        if additional is False and extra_keys:
            raise ProvenanceError(
                f"schema additional properties at {path}: {sorted(extra_keys)}"
            )
        if isinstance(additional, dict):
            for key in extra_keys:
                validate_json_schema(
                    value[key],
                    additional,
                    path=f"{path}.{key}",
                )
    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            validate_json_schema(item, schema["items"], path=f"{path}[{index}]")
    if isinstance(value, str) and "pattern" in schema:
        pattern = schema["pattern"]
        if not isinstance(pattern, str) or re.search(pattern, value) is None:
            raise ProvenanceError(f"schema pattern mismatch at {path}")


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    payload = "".join(canonical_json(record) + "\n" for record in records)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def input_text(record: dict[str, Any]) -> str:
    parts = record.get("input")
    if not isinstance(parts, list) or not parts:
        raise ProvenanceError("human input is not a nonempty content list")
    text_parts: list[str] = []
    for part in parts:
        if not isinstance(part, dict) or part.get("type") != "text":
            raise ProvenanceError("human input contains a non-text part")
        text = part.get("text")
        if not isinstance(text, str):
            raise ProvenanceError("human text input is not a string")
        text_parts.append(text)
    return "".join(text_parts)


def tool_event(record: dict[str, Any], event_type: str) -> dict[str, Any] | None:
    event = record.get("event")
    if (
        record.get("type") == "context.append_loop_event"
        and isinstance(event, dict)
        and event.get("type") == event_type
    ):
        return event
    return None


def classify_human_input(
    *, event_kind: str, text: str, time_unix_ms: int, endpoint_unix_ms: int,
    is_first_prompt: bool,
) -> str:
    if time_unix_ms > endpoint_unix_ms:
        return "post_endpoint_user_prompt"
    if event_kind == "prompt" and is_first_prompt:
        return "initial_research_prompt"
    if event_kind == "prompt" and text.strip() == GENERIC_CONTINUE_PROMPT:
        return "generic_continue_search"
    if event_kind == "steer" and text.lstrip().startswith("/"):
        return "tool_mode_command"
    return "other_human_input"


def derive_sanitized_events(session_root: Path) -> list[dict[str, Any]]:
    state_path = session_root / "state.json"
    log_path = session_root / "logs" / "kimi-code.log"
    state = read_json(state_path)
    if not isinstance(state, dict):
        raise ProvenanceError("state.json is not an object")
    state_agents = state.get("agents")
    if not isinstance(state_agents, dict) or not state_agents:
        raise ProvenanceError("state.json does not declare agents")
    agent_labels = sorted(state_agents)

    records_by_agent: dict[str, list[dict[str, Any]]] = {}
    wire_paths: dict[str, Path] = {}
    for agent in agent_labels:
        path = session_root / "agents" / agent / "wire.jsonl"
        wire_paths[agent] = path
        records_by_agent[agent] = read_jsonl(path)

    main_records = records_by_agent.get("main")
    if main_records is None:
        raise ProvenanceError("session does not contain a main agent")

    endpoint_calls: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for record in main_records:
        event = tool_event(record, "tool.call")
        if event is None or event.get("name") != "Bash":
            continue
        args = event.get("args")
        if isinstance(args, dict) and str(args.get("command", "")).strip() == ENDPOINT_COMMAND:
            endpoint_calls.append((record, event))
    if len(endpoint_calls) != 1:
        raise ProvenanceError(
            f"expected one endpoint command, found {len(endpoint_calls)}"
        )
    endpoint_call_record, endpoint_call = endpoint_calls[0]
    endpoint_call_id = endpoint_call.get("toolCallId")
    if not isinstance(endpoint_call_id, str):
        raise ProvenanceError("endpoint tool call has no string ID")

    endpoint_results: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for record in main_records:
        event = tool_event(record, "tool.result")
        if event is not None and event.get("toolCallId") == endpoint_call_id:
            endpoint_results.append((record, event))
    if len(endpoint_results) != 1:
        raise ProvenanceError(
            f"expected one endpoint result, found {len(endpoint_results)}"
        )
    endpoint_result_record, endpoint_result = endpoint_results[0]
    endpoint_time = endpoint_result_record.get("time")
    if not isinstance(endpoint_time, int):
        raise ProvenanceError("endpoint result has no integer timestamp")
    result_payload = endpoint_result.get("result")
    if not isinstance(result_payload, dict) or not isinstance(
        result_payload.get("output"), str
    ):
        raise ProvenanceError("endpoint result has no string output")
    endpoint_stdout = result_payload["output"].encode("utf-8")

    script_candidates: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for record in main_records:
        event = tool_event(record, "tool.call")
        if event is None or event.get("name") != "Write":
            continue
        args = event.get("args")
        if not isinstance(args, dict):
            continue
        path = str(args.get("path", ""))
        if path.endswith(ENDPOINT_SCRIPT_SUFFIX) and isinstance(
            args.get("content"), str
        ):
            if int(record.get("time", 0)) <= int(endpoint_call_record.get("time", 0)):
                script_candidates.append((record, event))
    if not script_candidates:
        raise ProvenanceError("no endpoint script write precedes the endpoint command")
    script_record, script_event = max(
        script_candidates,
        key=lambda item: int(item[0].get("time", 0)),
    )
    script_call_id = script_event.get("toolCallId")
    script_args = script_event["args"]
    if not isinstance(script_call_id, str):
        raise ProvenanceError("endpoint script write has no string ID")
    endpoint_script = script_args["content"].encode("utf-8")

    protocol_versions = sorted(
        {
            str(record["protocol_version"])
            for records in records_by_agent.values()
            for record in records
            if record.get("type") == "metadata" and "protocol_version" in record
        }
    )
    if not protocol_versions:
        raise ProvenanceError("no wire protocol metadata found")

    dynamic_events: list[dict[str, Any]] = []
    begins: dict[tuple[str, str], int] = {}
    ends: dict[tuple[str, str], int] = {}
    for agent, records in records_by_agent.items():
        for record in records:
            record_type = record.get("type")
            time_unix_ms = record.get("time")
            if record_type == "llm.request":
                if not isinstance(time_unix_ms, int):
                    raise ProvenanceError("llm.request has no integer timestamp")
                dynamic_events.append(
                    {
                        "record_type": "llm_request",
                        "agent": agent,
                        "time_unix_ms": time_unix_ms,
                        "provider": record.get("provider"),
                        "model_id": record.get("model"),
                        "model_alias": record.get("modelAlias"),
                        "thinking_effort": record.get("thinkingEffort"),
                        "turn_step": record.get("turnStep"),
                    }
                )
            elif record_type == "usage.record":
                if not isinstance(time_unix_ms, int):
                    raise ProvenanceError("usage.record has no integer timestamp")
                usage = record.get("usage")
                if not isinstance(usage, dict):
                    raise ProvenanceError("usage.record has no usage object")
                normalized_usage: dict[str, int] = {}
                for source, target in USAGE_FIELDS:
                    value = usage.get(source)
                    if not isinstance(value, int) or value < 0:
                        raise ProvenanceError(f"invalid usage field {source}")
                    normalized_usage[target] = value
                dynamic_events.append(
                    {
                        "record_type": "usage",
                        "agent": agent,
                        "time_unix_ms": time_unix_ms,
                        "model_alias": record.get("model"),
                        "usage": normalized_usage,
                    }
                )

            event = record.get("event")
            if (
                record_type == "context.append_loop_event"
                and isinstance(event, dict)
                and event.get("type") in {"step.begin", "step.end"}
            ):
                uuid = event.get("uuid")
                if not isinstance(uuid, str) or not isinstance(time_unix_ms, int):
                    raise ProvenanceError("step event lacks UUID or timestamp")
                key = (agent, uuid)
                target = begins if event["type"] == "step.begin" else ends
                if key in target:
                    raise ProvenanceError(f"duplicate {event['type']} for {agent}")
                target[key] = time_unix_ms

    for key, end_time in ends.items():
        if key not in begins:
            raise ProvenanceError(f"step.end without step.begin for {key[0]}")
        begin_time = begins[key]
        if end_time < begin_time:
            raise ProvenanceError(f"negative step interval for {key[0]}")
        agent, uuid = key
        interval_id = sha256_bytes(f"{agent}\0{uuid}".encode("utf-8"))[:20]
        dynamic_events.append(
            {
                "record_type": "step_interval",
                "agent": agent,
                "interval_id": interval_id,
                "begin_unix_ms": begin_time,
                "end_unix_ms": end_time,
            }
        )

    human_records = [
        record
        for record in main_records
        if record.get("type") in {"turn.prompt", "turn.steer"}
        and isinstance(record.get("origin"), dict)
        and record["origin"].get("kind") == "user"
    ]
    prompt_times = [
        int(record["time"])
        for record in human_records
        if record.get("type") == "turn.prompt"
    ]
    first_prompt_time = min(prompt_times) if prompt_times else None
    for record in human_records:
        time_unix_ms = record.get("time")
        if not isinstance(time_unix_ms, int):
            raise ProvenanceError("human input has no integer timestamp")
        event_kind = "prompt" if record["type"] == "turn.prompt" else "steer"
        text = input_text(record)
        dynamic_events.append(
            {
                "record_type": "human_input",
                "time_unix_ms": time_unix_ms,
                "event_kind": event_kind,
                "classification": classify_human_input(
                    event_kind=event_kind,
                    text=text,
                    time_unix_ms=time_unix_ms,
                    endpoint_unix_ms=endpoint_time,
                    is_first_prompt=time_unix_ms == first_prompt_time,
                ),
                "text": text,
                "text_sha256": sha256_bytes(text.encode("utf-8")),
            }
        )

    metadata = {
        "record_type": "metadata",
        "schema_version": 1,
        "sanitizer_version": SANITIZER_VERSION,
        "wire_protocol_versions": protocol_versions,
        "session_created_utc": state.get("createdAt"),
        "agent_labels": agent_labels,
        "incomplete_step_begins": len(set(begins) - set(ends)),
        "privacy_boundary": (
            "Only request metadata, usage, completed step intervals, exact human "
            "inputs, endpoint metadata, and raw-file hashes are retained. Assistant "
            "messages, tool arguments other than the endpoint identity, tool output "
            "other than the endpoint artifact, and local paths are omitted."
        ),
    }
    endpoint = {
        "record_type": "endpoint",
        "time_unix_ms": endpoint_time,
        "command": ENDPOINT_COMMAND,
        "endpoint_tool_call_id": endpoint_call_id,
        "endpoint_script_write_call_id": script_call_id,
        "script_bytes": len(endpoint_script),
        "script_sha256": sha256_bytes(endpoint_script),
        "stdout_bytes": len(endpoint_stdout),
        "stdout_sha256": sha256_bytes(endpoint_stdout),
    }

    raw_paths = {
        **{
            f"agents/{agent}/wire.jsonl": path
            for agent, path in wire_paths.items()
        },
        "state.json": state_path,
        "logs/kimi-code.log": log_path,
    }
    raw_hash_events = []
    for relative_path, path in sorted(raw_paths.items()):
        raw_hash_events.append(
            {
                "record_type": "raw_file_hash",
                "path": relative_path,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    def event_sort_key(event: dict[str, Any]) -> tuple[Any, ...]:
        return (
            event.get("time_unix_ms", event.get("begin_unix_ms", -1)),
            event["record_type"],
            event.get("agent", ""),
            event.get("interval_id", ""),
        )

    return [metadata, endpoint, *raw_hash_events, *sorted(dynamic_events, key=event_sort_key)]


def derive_start_manifest(archive: Path) -> dict[str, Any]:
    files = []
    zip_member_count = 0
    try:
        with zipfile.ZipFile(archive) as bundle:
            all_members = bundle.infolist()
            zip_member_count = len(all_members)
            members = sorted(
                (member for member in all_members if not member.is_dir()),
                key=lambda member: member.filename,
            )
            for member in members:
                data = bundle.read(member)
                relative = member.filename.removeprefix("workspace/")
                files.append(
                    {
                        "path": relative,
                        "bytes": len(data),
                        "sha256": sha256_bytes(data),
                        "content_public": not relative.startswith(
                            "inputs/teacher_slides/"
                        ),
                    }
                )
    except (OSError, zipfile.BadZipFile) as exc:
        raise ProvenanceError(f"cannot read start archive {archive}: {exc}") from exc
    return {
        "schema_version": 1,
        "archive_label": archive.name,
        "archive_bytes": archive.stat().st_size,
        "archive_sha256": sha256_file(archive),
        "path_prefix_removed": "workspace/",
        "file_entry_count": len(files),
        "zip_member_count": zip_member_count,
        "privacy_note": (
            "Teacher-provided slide bytes remain private; their path, size, and "
            "SHA-256 are retained for audit. Other entries are listed for "
            "frozen-start reconstruction but are not duplicated in this route "
            "directory."
        ),
        "files": files,
    }


def exactly_one(
    records: Iterable[dict[str, Any]], record_type: str
) -> dict[str, Any]:
    matches = [record for record in records if record.get("record_type") == record_type]
    if len(matches) != 1:
        raise ProvenanceError(
            f"expected one {record_type} record, found {len(matches)}"
        )
    return matches[0]


def usage_sum(records: Iterable[dict[str, Any]]) -> dict[str, int]:
    totals = {
        "input_cache_creation": 0,
        "input_cache_read": 0,
        "input_other": 0,
        "output": 0,
    }
    count = 0
    for record in records:
        usage = record.get("usage")
        if not isinstance(usage, dict):
            raise ProvenanceError("usage event has no usage object")
        for field in totals:
            value = usage.get(field)
            if not isinstance(value, int) or value < 0:
                raise ProvenanceError(f"usage event has invalid {field}")
            totals[field] += value
        count += 1
    totals["total"] = sum(totals.values())
    totals["records"] = count
    return totals


def merged_interval_stats(
    intervals: Iterable[dict[str, Any]],
) -> tuple[int, int, int]:
    pairs: list[tuple[int, int]] = []
    interval_ids: set[str] = set()
    summed_ms = 0
    for interval in intervals:
        interval_id = interval.get("interval_id")
        begin = interval.get("begin_unix_ms")
        end = interval.get("end_unix_ms")
        if not isinstance(interval_id, str) or interval_id in interval_ids:
            raise ProvenanceError("duplicate or invalid step interval ID")
        interval_ids.add(interval_id)
        if not isinstance(begin, int) or not isinstance(end, int) or end < begin:
            raise ProvenanceError("invalid step interval endpoints")
        pairs.append((begin, end))
        summed_ms += end - begin
    merged: list[list[int]] = []
    for begin, end in sorted(pairs):
        if not merged or begin > merged[-1][1]:
            merged.append([begin, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    union_ms = sum(end - begin for begin, end in merged)
    return summed_ms, len(merged), union_ms


def utc_from_unix_ms(value: int) -> str:
    dt = datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def unix_ms_from_utc(value: str) -> int:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProvenanceError(f"invalid UTC timestamp: {value}") from exc
    return round(dt.timestamp() * 1000)


def derive_public_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    metadata = exactly_one(events, "metadata")
    endpoint = exactly_one(events, "endpoint")
    cutoff = endpoint.get("time_unix_ms")
    if not isinstance(cutoff, int):
        raise ProvenanceError("endpoint timestamp is not an integer")

    requests = [event for event in events if event.get("record_type") == "llm_request"]
    usages = [event for event in events if event.get("record_type") == "usage"]
    intervals = [
        event for event in events if event.get("record_type") == "step_interval"
    ]
    human_inputs = [
        event for event in events if event.get("record_type") == "human_input"
    ]
    raw_hashes = [
        event for event in events if event.get("record_type") == "raw_file_hash"
    ]

    endpoint_requests = [
        event for event in requests if int(event.get("time_unix_ms", -1)) <= cutoff
    ]
    endpoint_usages = [
        event for event in usages if int(event.get("time_unix_ms", -1)) <= cutoff
    ]
    endpoint_intervals = [
        event for event in intervals if int(event.get("end_unix_ms", -1)) <= cutoff
    ]
    endpoint_human_inputs = [
        event for event in human_inputs if int(event.get("time_unix_ms", -1)) <= cutoff
    ]
    post_endpoint_human_inputs = [
        event for event in human_inputs if int(event.get("time_unix_ms", -1)) > cutoff
    ]

    endpoint_usage = usage_sum(endpoint_usages)
    full_usage = usage_sum(usages)
    summed_ms, merged_count, union_ms = merged_interval_stats(endpoint_intervals)
    initial_inputs = [
        event
        for event in endpoint_human_inputs
        if event.get("classification") == "initial_research_prompt"
    ]
    if len(initial_inputs) != 1:
        raise ProvenanceError(
            f"expected one initial human input, found {len(initial_inputs)}"
        )
    initial_prompt_time = initial_inputs[0].get("time_unix_ms")
    if not isinstance(initial_prompt_time, int):
        raise ProvenanceError("initial prompt has no integer timestamp")
    created_utc = metadata.get("session_created_utc")
    if not isinstance(created_utc, str):
        raise ProvenanceError("metadata has no session creation timestamp")
    created_time = unix_ms_from_utc(created_utc)

    raw_hash_map: dict[str, str] = {}
    for record in raw_hashes:
        path = record.get("path")
        digest = record.get("sha256")
        if not isinstance(path, str) or not isinstance(digest, str):
            raise ProvenanceError("invalid raw-file hash record")
        if path in raw_hash_map:
            raise ProvenanceError(f"duplicate raw-file hash: {path}")
        raw_hash_map[path] = digest

    classifications: dict[str, int] = {}
    for record in endpoint_human_inputs:
        classification = str(record.get("classification"))
        classifications[classification] = classifications.get(classification, 0) + 1

    last_usage_time = max(int(record["time_unix_ms"]) for record in usages)
    last_human_time = max(int(record["time_unix_ms"]) for record in human_inputs)
    return {
        "metadata": metadata,
        "endpoint": endpoint,
        "session_created_utc": created_utc,
        "initial_prompt_utc": utc_from_unix_ms(initial_prompt_time),
        "endpoint_utc": utc_from_unix_ms(cutoff),
        "llm_requests_through_endpoint": len(endpoint_requests),
        "full_llm_requests": len(requests),
        "endpoint_usage": endpoint_usage,
        "full_usage": full_usage,
        "completed_step_intervals_through_endpoint": len(endpoint_intervals),
        "completed_step_interval_sum_hours": summed_ms / 3_600_000,
        "merged_active_interval_count": merged_count,
        "merged_active_wall_hours": union_ms / 3_600_000,
        "session_created_to_endpoint_hours": (cutoff - created_time) / 3_600_000,
        "initial_prompt_to_endpoint_hours": (cutoff - initial_prompt_time)
        / 3_600_000,
        "human_inputs_through_endpoint": len(endpoint_human_inputs),
        "human_input_classifications": classifications,
        "post_endpoint_user_prompts": len(post_endpoint_human_inputs),
        "last_recorded_usage_utc": utc_from_unix_ms(last_usage_time),
        "last_user_prompt_utc": utc_from_unix_ms(last_human_time),
        "providers": sorted({str(record.get("provider")) for record in requests}),
        "model_ids": sorted({str(record.get("model_id")) for record in requests}),
        "model_aliases": sorted(
            {str(record.get("model_alias")) for record in requests}
        ),
        "thinking_efforts": sorted(
            {str(record.get("thinking_effort")) for record in requests}
        ),
        "raw_hashes": raw_hash_map,
    }


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ProvenanceError(
            f"{label} mismatch: derived={actual!r}, attested={expected!r}"
        )


def require_close(actual: float, expected: float, label: str) -> None:
    if abs(actual - expected) > 1e-12:
        raise ProvenanceError(
            f"{label} mismatch: derived={actual!r}, attested={expected!r}"
        )


def expected_start_tree(start_manifest: dict[str, Any]) -> set[str]:
    files = start_manifest.get("files")
    if not isinstance(files, list):
        raise ProvenanceError("start manifest files is not a list")
    paths = {"."}
    for entry in files:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ProvenanceError("invalid start manifest entry")
        parts = Path(entry["path"]).parts
        if not parts or parts[0] == ".git":
            continue
        for depth in range(1, min(len(parts), 3) + 1):
            paths.add("./" + "/".join(parts[:depth]))
    return paths


def verify_start_inventory(route_dir: Path) -> dict[str, Any]:
    workspace_manifest = read_json(route_dir / "workspace_manifest.json")
    start_manifest_path = route_dir / "start_manifest.json"
    start_manifest = read_json(start_manifest_path)
    inventory = workspace_manifest.get("start_inventory")
    if not isinstance(inventory, dict):
        raise ProvenanceError("workspace manifest has no start_inventory")
    require_equal(
        start_manifest_path.stat().st_size,
        inventory.get("manifest_bytes"),
        "start manifest bytes",
    )
    require_equal(
        sha256_file(start_manifest_path),
        inventory.get("manifest_sha256"),
        "start manifest hash",
    )
    source = workspace_manifest.get("workspace_source")
    if not isinstance(source, dict):
        raise ProvenanceError("workspace manifest has no workspace_source")
    require_equal(
        start_manifest.get("archive_bytes"),
        source.get("bytes"),
        "start archive bytes",
    )
    require_equal(
        start_manifest.get("archive_sha256"),
        source.get("sha256"),
        "start archive hash",
    )
    start_tree_path = route_dir / "start_tree.txt"
    require_equal(
        start_tree_path.stat().st_size,
        inventory.get("tree_bytes"),
        "start tree bytes",
    )
    require_equal(
        sha256_file(start_tree_path),
        inventory.get("tree_sha256"),
        "start tree hash",
    )
    actual_tree = {
        line
        for line in start_tree_path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }
    require_equal(actual_tree, expected_start_tree(start_manifest), "start tree")
    start_files = {
        entry["path"]: entry
        for entry in start_manifest["files"]
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    for relative in ("AGENTS.md", "START_GOAL.txt", "inputs/problem_statement.md"):
        entry = start_files.get(relative)
        if entry is None:
            raise ProvenanceError(f"start manifest omits {relative}")
        public_name = "problem_statement.md" if relative.startswith("inputs/") else relative
        public_path = route_dir / "start_brief" / public_name
        require_equal(public_path.stat().st_size, entry.get("bytes"), f"start brief bytes {relative}")
        require_equal(sha256_file(public_path), entry.get("sha256"), f"start brief hash {relative}")
    require_equal(
        sha256_file(REPOSITORY / "provenance" / "prompts" / "kimi" / "P-K-01_start_goal.txt"),
        start_files["START_GOAL.txt"]["sha256"],
        "verbatim Kimi opening prompt hash",
    )
    return {
        "archive_file_entries": start_manifest.get("file_entry_count"),
        "archive_zip_members": start_manifest.get("zip_member_count"),
        "tree_paths": len(actual_tree),
    }


def verify_public_semantics(route_dir: Path) -> dict[str, Any]:
    ledger_path = route_dir / LEDGER_NAME
    ledger_text = ledger_path.read_text(encoding="utf-8")
    for forbidden in ("/Users/", "~/.kimi-code", "Authorization:", "Bearer "):
        if forbidden in ledger_text:
            raise ProvenanceError(f"privacy leak in public ledger: {forbidden}")
    events = read_jsonl(ledger_path)
    validate_ledger_records(events)
    summary = derive_public_summary(events)
    attestation = read_json(route_dir / "run_attestation.json")
    schema = read_json(route_dir / "run_attestation.schema.json")
    validate_json_schema(attestation, schema, path="attestation schema $")
    require_equal(
        attestation.get("schema_ref"),
        "run_attestation.schema.json",
        "attestation schema reference",
    )
    reconciliation = attestation.get("observer_manifest_reconciliation")
    if not isinstance(reconciliation, dict):
        raise ProvenanceError("attestation has no observer reconciliation")
    require_equal(
        reconciliation.get("verifier_version"),
        VERIFIER_VERSION,
        "attestation verifier version",
    )
    accounting = read_json(route_dir / "accounting.json")
    endpoint = attestation["route_endpoint"]
    timing = attestation["timing_through_endpoint"]
    usage = attestation["usage_through_endpoint"]
    human = attestation["human_input_through_endpoint"]
    post = attestation["post_endpoint_record_context"]
    session = attestation["session"]

    require_equal(summary["providers"], [session["provider"]], "provider")
    require_equal(summary["model_ids"], [session["model_id"]], "model ID")
    require_equal(summary["model_aliases"], [session["model_alias"]], "model alias")
    require_equal(
        summary["thinking_efforts"],
        sorted(session["thinking_efforts_observed"]),
        "thinking effort",
    )
    require_equal(summary["session_created_utc"], session["created_utc"], "session created UTC")
    require_equal(summary["initial_prompt_utc"], session["initial_prompt_utc"], "initial prompt UTC")
    topology = session.get("topology")
    if not isinstance(topology, dict):
        raise ProvenanceError("session topology is not an object")
    topology_labels = topology.get("agent_labels")
    if not isinstance(topology_labels, list) or not all(
        isinstance(label, str) for label in topology_labels
    ):
        raise ProvenanceError("session topology agent labels are invalid")
    require_equal(
        sorted(topology_labels),
        summary["metadata"].get("agent_labels"),
        "session topology agent labels",
    )
    require_equal(
        topology_labels.count("main"),
        1,
        "session topology main label count",
    )
    require_equal(topology.get("main_sessions"), 1, "session topology main sessions")
    require_equal(
        topology.get("subagents"),
        len(topology_labels) - 1,
        "session topology subagents",
    )
    require_equal(summary["endpoint"]["time_unix_ms"], endpoint["unix_ms"], "endpoint time")
    require_equal(summary["endpoint_utc"], endpoint["utc"], "endpoint UTC")
    require_equal(
        summary["endpoint"]["command"],
        ENDPOINT_COMMAND,
        "endpoint command",
    )
    require_equal(
        summary["endpoint"]["command"],
        endpoint["command"],
        "attested endpoint command",
    )
    require_equal(
        summary["metadata"]["wire_protocol_versions"],
        [endpoint["wire_protocol_version"]],
        "wire protocol",
    )
    require_equal(
        summary["endpoint"]["endpoint_tool_call_id"],
        endpoint["endpoint_tool_call_id"],
        "endpoint tool-call ID",
    )
    require_equal(
        summary["endpoint"]["endpoint_script_write_call_id"],
        endpoint["endpoint_script_write_call_id"],
        "endpoint script-write ID",
    )
    require_equal(
        summary["llm_requests_through_endpoint"],
        endpoint["llm_requests_through_endpoint"],
        "endpoint LLM request count",
    )
    require_equal(
        summary["completed_step_intervals_through_endpoint"],
        endpoint["completed_step_intervals"],
        "endpoint completed-step count",
    )
    for field in ("script_bytes", "script_sha256", "stdout_bytes", "stdout_sha256"):
        attested_field = field.replace("script_", "endpoint_script_").replace(
            "stdout_", "endpoint_stdout_"
        )
        require_equal(
            summary["endpoint"][field],
            endpoint[attested_field],
            f"endpoint {field}",
        )

    endpoint_usage = summary["endpoint_usage"]
    require_equal(endpoint_usage["records"], usage["usage_records"], "usage record count")
    for field in (
        "input_cache_creation",
        "input_cache_read",
        "input_other",
        "output",
        "total",
    ):
        require_equal(endpoint_usage[field], usage[field], f"usage {field}")
    require_close(
        summary["session_created_to_endpoint_hours"],
        timing["session_created_to_endpoint_hours"],
        "session elapsed hours",
    )
    require_close(
        summary["initial_prompt_to_endpoint_hours"],
        timing["initial_prompt_to_endpoint_hours"],
        "prompt elapsed hours",
    )
    require_close(
        summary["completed_step_interval_sum_hours"],
        timing["completed_step_interval_sum_hours"],
        "cumulative agent hours",
    )
    require_equal(
        summary["merged_active_interval_count"],
        timing["merged_active_interval_count"],
        "merged interval count",
    )
    require_close(
        summary["merged_active_wall_hours"],
        timing["merged_active_wall_hours"],
        "active wall hours",
    )

    classifications = summary["human_input_classifications"]
    require_equal(classifications.get("initial_research_prompt", 0), human["initial_research_prompt"], "initial prompt count")
    require_equal(classifications.get("generic_continue_search", 0), human["generic_continue_search_prompts"], "generic prompt count")
    require_equal(classifications.get("tool_mode_command", 0), human["tool_mode_commands"], "tool-mode command count")
    require_equal(summary["human_inputs_through_endpoint"], human["recorded_human_inputs"], "human input count")
    require_equal(classifications.get("other_human_input", 0), 0, "other human input count")

    require_equal(summary["full_llm_requests"], post["full_llm_requests"], "full LLM request count")
    full_usage = summary["full_usage"]
    require_equal(full_usage["records"], post["full_usage_records"], "full usage record count")
    for field in (
        "input_cache_creation",
        "input_cache_read",
        "input_other",
        "output",
        "total",
    ):
        require_equal(full_usage[field], post["full_recorded_tokens"][field], f"full usage {field}")
    require_equal(summary["last_recorded_usage_utc"], post["last_recorded_usage_utc"], "last usage UTC")
    require_equal(summary["post_endpoint_user_prompts"], post["post_endpoint_user_prompts"], "post-endpoint prompt count")
    require_equal(summary["last_user_prompt_utc"], post["last_user_prompt_utc"], "last user prompt UTC")
    require_equal(summary["raw_hashes"], attestation["private_raw_evidence_hashes"], "raw evidence hashes")

    terminal_script = route_dir / "terminal_artifacts" / "exp19b_exact_yt.endpoint.py"
    terminal_stdout = route_dir / "terminal_artifacts" / "exp19b_exact_yt.stdout.txt"
    require_equal(terminal_script.stat().st_size, endpoint["endpoint_script_bytes"], "terminal script bytes")
    require_equal(sha256_file(terminal_script), endpoint["endpoint_script_sha256"], "terminal script hash")
    require_equal(terminal_stdout.stat().st_size, endpoint["endpoint_stdout_bytes"], "terminal stdout bytes")
    require_equal(sha256_file(terminal_stdout), endpoint["endpoint_stdout_sha256"], "terminal stdout hash")

    audited = accounting["audited_route_endpoint"]
    require_equal(audited["unix_ms"], endpoint["unix_ms"], "accounting endpoint")
    require_equal(audited["utc"], endpoint["utc"], "accounting endpoint UTC")
    require_equal(
        audited["event"],
        f"successful tool result of {ENDPOINT_COMMAND}",
        "accounting endpoint event",
    )
    require_equal(audited["llm_requests"], endpoint["llm_requests_through_endpoint"], "accounting requests")
    require_equal(audited["usage_records"], usage["usage_records"], "accounting usage records")
    require_equal(audited["recorded_tokens"], {field: usage[field] for field in ("input_cache_creation", "input_cache_read", "input_other", "output", "total")}, "accounting usage")
    audited_timing = audited["timing_hours"]
    require_close(
        audited_timing["merged_active_wall"],
        timing["merged_active_wall_hours"],
        "accounting timing merged active wall",
    )
    require_close(
        audited_timing["cumulative_agent"],
        timing["completed_step_interval_sum_hours"],
        "accounting timing cumulative agent",
    )
    require_close(
        audited_timing["session_created_to_endpoint"],
        timing["session_created_to_endpoint_hours"],
        "accounting timing session elapsed",
    )
    paper_accounting = accounting["paper_reported_accounting"]
    paper_runtime = paper_accounting["approximate_run_time_hours"]
    require_equal(
        paper_runtime["value"],
        round(timing["merged_active_wall_hours"]),
        "paper runtime rounded value",
    )
    require_equal(paper_runtime["approximate"], True, "paper runtime approximate flag")
    paper_agent_time = paper_accounting["cumulative_agent_time_hours"]
    require_close(
        paper_agent_time["value"],
        round(timing["completed_step_interval_sum_hours"], 2),
        "paper cumulative agent time",
    )
    paper_tokens = paper_accounting["recorded_tokens"]
    require_equal(
        paper_tokens["total"]["audited_exact_value_before_rounding"],
        usage["total"],
        "paper total-token exact value",
    )
    require_equal(
        paper_tokens["total"]["value"],
        round(usage["total"], -4),
        "paper total-token rounded value",
    )
    require_equal(
        paper_tokens["output"]["audited_exact_value_before_rounding"],
        usage["output"],
        "paper output-token exact value",
    )
    require_equal(
        paper_tokens["output"]["value"],
        round(usage["output"], -2),
        "paper output-token rounded value",
    )
    require_equal(
        paper_tokens["billable_usage_claim"],
        usage["billable_usage_claim"],
        "paper billable-usage claim",
    )
    accounting_topology = paper_accounting["agent_topology"]
    require_equal(
        accounting_topology["main_sessions"],
        topology["main_sessions"],
        "accounting topology main sessions",
    )
    require_equal(
        accounting_topology["recorded_subagents"],
        topology["subagents"],
        "accounting topology subagents",
    )

    start_result = verify_start_inventory(route_dir)
    initial_prompt = next(
        event
        for event in events
        if event.get("record_type") == "human_input"
        and event.get("classification") == "initial_research_prompt"
    )
    require_equal(
        initial_prompt["text_sha256"],
        sha256_file(route_dir / "start_brief" / "START_GOAL.txt"),
        "initial prompt hash",
    )
    return {
        "ledger_records": len(events),
        "endpoint_requests": summary["llm_requests_through_endpoint"],
        "endpoint_usage_records": endpoint_usage["records"],
        "start_archive_file_entries": start_result["archive_file_entries"],
        "start_archive_zip_members": start_result["archive_zip_members"],
    }


def write_route_manifest(route_dir: Path) -> Path:
    manifest_path = route_dir / ROUTE_MANIFEST_NAME
    files = []
    for path in sorted(route_dir.rglob("*")):
        if not path.is_file() or path == manifest_path:
            continue
        files.append(
            {
                "path": path.relative_to(route_dir).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    payload = {
        "schema_version": 1,
        "route_id": "kimi-period23",
        "manifest_excludes": [ROUTE_MANIFEST_NAME],
        "verifier": {
            "version": VERIFIER_VERSION,
            "path": "python/verify_kimi_provenance.py",
            "bytes": Path(__file__).stat().st_size,
            "sha256": sha256_file(Path(__file__)),
        },
        "files": files,
    }
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def verify_route_manifest(route_dir: Path) -> dict[str, Any]:
    manifest_path = route_dir / ROUTE_MANIFEST_NAME
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict) or manifest.get("route_id") != "kimi-period23":
        raise ProvenanceError("invalid Kimi route provenance manifest")
    listed = manifest.get("files")
    if not isinstance(listed, list):
        raise ProvenanceError("route manifest files is not a list")
    expected_paths = {
        path.relative_to(route_dir).as_posix()
        for path in route_dir.rglob("*")
        if path.is_file() and path != manifest_path
    }
    listed_paths: set[str] = set()
    for entry in listed:
        if not isinstance(entry, dict):
            raise ProvenanceError("route manifest entry is not an object")
        relative = entry.get("path")
        if not isinstance(relative, str) or relative.startswith("/") or ".." in Path(relative).parts:
            raise ProvenanceError(f"unsafe route manifest path: {relative!r}")
        if relative in listed_paths:
            raise ProvenanceError(f"duplicate route manifest path: {relative}")
        listed_paths.add(relative)
        path = route_dir / relative
        if not path.is_file():
            raise ProvenanceError(f"route manifest file is missing: {relative}")
        if path.stat().st_size != entry.get("bytes"):
            raise ProvenanceError(f"route manifest byte count drift: {relative}")
        if sha256_file(path) != entry.get("sha256"):
            raise ProvenanceError(f"route manifest hash drift: {relative}")
    if listed_paths != expected_paths:
        missing = sorted(expected_paths - listed_paths)
        extra = sorted(listed_paths - expected_paths)
        raise ProvenanceError(
            f"route manifest inventory drift: missing={missing}, extra={extra}"
        )
    verifier = manifest.get("verifier")
    if not isinstance(verifier, dict):
        raise ProvenanceError("route manifest has no verifier record")
    verifier_path = REPOSITORY / str(verifier.get("path"))
    require_equal(verifier.get("version"), VERIFIER_VERSION, "verifier version")
    require_equal(verifier_path.stat().st_size, verifier.get("bytes"), "verifier bytes")
    require_equal(sha256_file(verifier_path), verifier.get("sha256"), "verifier hash")
    return {"file_count": len(listed_paths), "valid": True}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--route-dir", type=Path, default=DEFAULT_ROUTE_DIR)
    parser.add_argument("--raw-session-root", type=Path)
    parser.add_argument("--derive-ledger", action="store_true")
    parser.add_argument("--ledger-output", type=Path)
    parser.add_argument("--write-ledger", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--derive-start-manifest", action="store_true")
    parser.add_argument("--start-archive", type=Path)
    parser.add_argument("--start-manifest-output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.derive_start_manifest:
            if args.start_archive is None or args.start_manifest_output is None:
                raise ProvenanceError(
                    "--derive-start-manifest requires --start-archive and "
                    "--start-manifest-output"
                )
            manifest = derive_start_manifest(args.start_archive)
            write_json(args.start_manifest_output, manifest)
            print(
                json.dumps(
                    {
                        "file_entries": manifest["file_entry_count"],
                        "zip_members": manifest["zip_member_count"],
                        "output": str(args.start_manifest_output),
                        "valid": True,
                    },
                    sort_keys=True,
                )
            )
            return 0

        if args.derive_ledger:
            if args.raw_session_root is None or args.ledger_output is None:
                raise ProvenanceError(
                    "--derive-ledger requires --raw-session-root and --ledger-output"
                )
            events = derive_sanitized_events(args.raw_session_root)
            write_jsonl(args.ledger_output, events)
            print(
                json.dumps(
                    {
                        "output": str(args.ledger_output),
                        "records": len(events),
                        "valid": True,
                    },
                    sort_keys=True,
                )
            )
            return 0

        ledger_path = args.route_dir / LEDGER_NAME
        if args.write_ledger:
            if args.raw_session_root is None:
                raise ProvenanceError("--write-ledger requires --raw-session-root")
            write_jsonl(ledger_path, derive_sanitized_events(args.raw_session_root))
        if args.write_manifest:
            write_route_manifest(args.route_dir)

        if args.check or not (args.write_ledger or args.write_manifest):
            manifest_result = verify_route_manifest(args.route_dir)
            semantic_result = verify_public_semantics(args.route_dir)
            if args.raw_session_root is not None:
                expected = derive_sanitized_events(args.raw_session_root)
                actual = read_jsonl(ledger_path)
                if [canonical_json(item) for item in actual] != [
                    canonical_json(item) for item in expected
                ]:
                    raise ProvenanceError(
                        "public sanitized ledger does not match the raw session"
                    )
            if args.start_archive is not None:
                expected_start = derive_start_manifest(args.start_archive)
                actual_start = read_json(args.route_dir / "start_manifest.json")
                require_equal(
                    actual_start,
                    expected_start,
                    "public start manifest",
                )
            print(
                json.dumps(
                    {
                        "route_id": "kimi-period23",
                        "provenance_files": manifest_result["file_count"],
                        **semantic_result,
                        "valid": True,
                    },
                    sort_keys=True,
                )
            )
        return 0
    except ProvenanceError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
