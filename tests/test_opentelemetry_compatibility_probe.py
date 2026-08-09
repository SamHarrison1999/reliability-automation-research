"""Deterministic tests for the OpenTelemetry compatibility probe helpers."""

from __future__ import annotations

import base64
import gzip
import json
from pathlib import Path
from unittest.mock import patch

from observability.opentelemetry.compatibility_probe import (
    evaluate,
    read_sink_content_encodings,
    read_sink_payloads,
    read_sink_raw_payloads,
    sha256_bytes,
)
from observability.opentelemetry.telemetry_sink import SinkState


def test_sha256_bytes_is_stable() -> None:
    assert sha256_bytes(b"probe") == "ba9c736f19e7f60b7f6764adb0b7908c0a2b394e09b6c09863528c7f2bc86095"


def test_evaluate_records_complete_sequences_and_order() -> None:
    spans = [
        {
            "run_id": "run-1",
            "sequence": 1,
            "start_time_unix_nano": 10,
            "end_time_unix_nano": 11,
            "name": "span",
            "trace_id": "a",
            "span_id": "b",
        },
        {
            "run_id": "run-1",
            "sequence": 2,
            "start_time_unix_nano": 12,
            "end_time_unix_nano": 13,
            "name": "span",
            "trace_id": "c",
            "span_id": "d",
        },
    ]
    result = evaluate("run-1", [b"one"], spans, 2)
    assert result["sequence_complete"] is True
    assert result["timestamps_non_decreasing"] is True
    assert result["run_span_count"] == 2


def test_evaluate_records_transport_payload_metadata() -> None:
    raw_payload = gzip.compress(b"decoded", mtime=0)
    result = evaluate("run-1", [b"decoded"], [], 0, [raw_payload], ["gzip"])
    assert result["content_encodings"] == ["gzip"]
    assert result["payload_sha256"] == [sha256_bytes(b"decoded")]
    assert result["raw_transport_payload_sha256"] == [sha256_bytes(raw_payload)]


def test_sink_decompresses_gzip_and_preserves_transport_payload(tmp_path: Path) -> None:
    raw_payload = gzip.compress(b"decoded", mtime=0)
    state = SinkState(tmp_path)

    assert state.add(raw_payload, "gzip") == 1
    assert state.snapshot() == [b"decoded"]
    assert state.snapshot_records() == ([b"decoded"], [raw_payload], ["gzip"])
    assert (tmp_path / "payload-0001.transport").read_bytes() == raw_payload
    assert (tmp_path / "payload-0001.pb").read_bytes() == b"decoded"


def test_read_sink_payloads_decodes_base64_records() -> None:
    response = {
        "payloads_base64": [base64.b64encode(b"one").decode("ascii")],
        "raw_payloads_base64": [base64.b64encode(gzip.compress(b"one", mtime=0)).decode("ascii")],
        "content_encodings": ["gzip"],
    }
    with patch(
        "observability.opentelemetry.compatibility_probe.get_json",
        return_value=response,
    ):
        assert read_sink_payloads("http://sink") == [b"one"]
        assert read_sink_raw_payloads("http://sink") == [base64.b64decode(response["raw_payloads_base64"][0])]
        assert read_sink_content_encodings("http://sink") == ["gzip"]


def test_result_payload_can_be_serialised(tmp_path: Path) -> None:
    result = evaluate("run-1", [], [], 0)
    path = tmp_path / "result.json"
    path.write_text(json.dumps(result), encoding="utf-8")
    assert json.loads(path.read_text(encoding="utf-8"))["sequence_values"] == []
