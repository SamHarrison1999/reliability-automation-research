"""Tests for the bounded OrderFlow Phase 4 OpenTelemetry runtime wrapper."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "system" / "orderflow" / "otel_runtime.py"
ENTRYPOINT = ROOT / "infrastructure" / "kubernetes" / "entrypoint.sh"


def test_otel_runtime_mirrors_structured_event_identity() -> None:
    text = RUNTIME.read_text(encoding="utf-8")
    assert "ORDERFLOW_OTEL_ENDPOINT" in text
    assert "SimpleSpanProcessor" in text
    assert "OTLPSpanExporter" in text
    for field in (
        "event_id",
        "run_id",
        "scenario_id",
        "source_component",
        "event_type",
        "trace_id",
        "span_id",
        "order_id",
    ):
        assert f'"{field}"' in text
    assert "service.ServiceState" in text
    assert "structured-event-v1" in text


def test_entrypoint_preserves_non_otel_compatibility_and_sink_role() -> None:
    text = ENTRYPOINT.read_text(encoding="utf-8")
    assert 'ORDERFLOW_ROLE}" = "telemetry-sink"' in text
    assert "telemetry_sink.py" in text
    assert "python -m system.orderflow.otel_runtime" in text
