"""Static contract tests for the Phase 4 Kubernetes deployment manifest."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "infrastructure" / "kubernetes" / "orderflow-phase-4.yaml"


def manifest_text() -> str:
    return MANIFEST.read_text(encoding="utf-8")


def test_phase4_kubernetes_manifest_has_dedicated_namespace_and_prototype_identity() -> None:
    text = manifest_text()
    assert "name: orderflow-phase4" in text
    assert "orderflow-fit-probe" not in text
    assert "research-prototype: orderflow-phase-4-v1" in text
    assert "evidence-boundary: reproducibility-only" in text
    assert "openai.com" not in text


def test_phase4_kubernetes_manifest_uses_declared_images_and_versions() -> None:
    text = manifest_text()
    assert "image: orderflow/order-api:phase4-v1" in text
    assert "image: orderflow/inventory:phase4-v1" in text
    assert "image: orderflow/telemetry-sink:phase4-v1" in text
    assert "image: otel/opentelemetry-collector:0.158.0" in text
    assert "value: order-api-phase4-v1" in text
    assert "value: inventory-phase4-v1" in text
    assert text.count("imagePullPolicy: Never") == 4


def test_phase4_kubernetes_manifest_preserves_orderflow_dependency_boundary() -> None:
    text = manifest_text()
    assert text.count("kind: Deployment") == 4
    assert text.count("kind: Service") == 4
    assert "value: http://inventory:8081" in text
    assert "containerPort: 8080" in text
    assert "containerPort: 8081" in text
    assert "INVENTORY_URL" not in text


def test_phase4_kubernetes_manifest_has_bounded_trace_only_otel_path() -> None:
    text = manifest_text()
    assert "name: otel-collector-config" in text
    assert "endpoint: 0.0.0.0:4318" in text
    assert "endpoint: http://telemetry-sink:4319" in text
    assert "value: http://otel-collector:4318/v1/traces" in text
    assert "pipelines:" in text
    assert "traces:" in text
    assert "metrics:" not in text
    assert "logs:" not in text
    assert "grafana" not in text.lower()
    assert "prometheus" not in text.lower()


def test_phase4_kubernetes_manifest_has_readiness_and_validation_identity() -> None:
    text = manifest_text()
    assert text.count("readinessProbe:") == 3
    assert text.count("path: /healthz") == 3
    assert text.count("value: phase4-validation-placeholder") == 2
    assert text.count("value: phase4-reproducibility-validation") == 2
