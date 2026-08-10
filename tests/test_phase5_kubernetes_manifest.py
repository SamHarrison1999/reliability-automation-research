from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "infrastructure" / "kubernetes" / "orderflow-phase-5.yaml"


def test_phase5_kubernetes_manifest_declares_bounded_topology() -> None:
    text = MANIFEST.read_text(encoding="utf-8")

    assert "name: orderflow-phase5" in text
    for deployment in ("telemetry-sink", "otel-collector", "inventory", "order-api"):
        assert f"name: {deployment}" in text

    assert "orderflow/inventory:phase5-v1" in text
    assert "orderflow/order-api:phase5-v1" in text
    assert "orderflow/telemetry-sink:phase5-v1" in text
    assert "otel/opentelemetry-collector:0.158.0" in text
    assert text.count("imagePullPolicy: Never") == 4


def test_phase5_manifest_wires_trial_identity_into_orderflow_services() -> None:
    text = MANIFEST.read_text(encoding="utf-8")

    for variable in (
        "ORDERFLOW_RUN_ID",
        "ORDERFLOW_SCENARIO_ID",
        "ORDERFLOW_TRIAL_ID",
        "ORDERFLOW_AUTOMATION_CONDITION",
        "ORDERFLOW_REPETITION",
        "ORDERFLOW_RUN_ORDER",
    ):
        assert text.count(f"name: {variable}") == 2

    assert text.count("ORDERFLOW_OTEL_ENDPOINT") == 2
    assert "http://inventory:8081" in text


def test_phase5_collector_is_traces_only_and_points_to_repository_sink() -> None:
    text = MANIFEST.read_text(encoding="utf-8")

    assert "pipelines:" in text
    assert "traces:" in text
    assert "metrics:" not in text
    assert "logs:" not in text
    assert "endpoint: http://telemetry-sink:4319" in text
