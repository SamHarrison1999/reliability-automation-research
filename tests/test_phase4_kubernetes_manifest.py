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
    assert "value: order-api-phase4-v1" in text
    assert "value: inventory-phase4-v1" in text
    assert text.count("imagePullPolicy: Never") == 2


def test_phase4_kubernetes_manifest_preserves_two_service_dependency_boundary() -> None:
    text = manifest_text()
    assert text.count("kind: Deployment") == 2
    assert text.count("kind: Service") == 2
    assert "value: http://inventory:8081" in text
    assert "containerPort: 8080" in text
    assert "containerPort: 8081" in text


def test_phase4_kubernetes_manifest_has_readiness_and_validation_identity() -> None:
    text = manifest_text()
    assert text.count("readinessProbe:") == 2
    assert text.count("path: /healthz") == 2
    assert text.count("value: phase4-validation-placeholder") == 2
    assert text.count("value: phase4-reproducibility-validation") == 2
