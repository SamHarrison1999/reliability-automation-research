"""Contract tests for the versioned Phase 4 OrderFlow prototype manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "infrastructure" / "prototype" / "orderflow-phase-4.json"
DOCKERFILE = ROOT / "infrastructure" / "kubernetes" / "Dockerfile"
OTEL_LOCK = ROOT / "observability" / "opentelemetry" / "phase4-requirements.lock"

EXPECTED_BASE_DIGEST = "sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36"
EXPECTED_BASE_IMAGE = f"python:3.12-slim@{EXPECTED_BASE_DIGEST}"


def load_manifest() -> dict[str, object]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_phase4_prototype_manifest_declares_bounded_identity_and_target() -> None:
    manifest = load_manifest()
    assert manifest["manifest_version"] == "1.0.0"
    assert manifest["prototype_id"] == "orderflow-phase-4-v1"
    assert manifest["prototype_version"] == "1.0.0"
    assert manifest["target_model"] == "docker-desktop-kubernetes"
    assert manifest["evidence_boundary"] == "phase-4-reproducibility-only"


def test_phase4_prototype_manifest_preserves_two_service_topology() -> None:
    manifest = load_manifest()
    topology = manifest["topology"]
    assert topology["request_path"] == ["order-api", "inventory"]
    assert set(topology["services"]) == {"order-api", "inventory"}
    assert topology["services"]["order-api"]["dependency"] == "inventory"
    assert topology["services"]["order-api"]["container_port"] == 8080
    assert topology["services"]["inventory"]["container_port"] == 8081


def test_phase4_prototype_manifest_reuses_versioned_packaging_inputs() -> None:
    manifest = load_manifest()
    packaging = manifest["packaging"]
    assert packaging["dockerfile"] == "infrastructure/kubernetes/Dockerfile"
    assert packaging["entrypoint"] == "infrastructure/kubernetes/entrypoint.sh"
    assert packaging["build_platform"] == "linux/amd64"
    assert packaging["base_image_tag"] == "python:3.12-slim"
    assert packaging["base_image_digest"] == EXPECTED_BASE_DIGEST
    assert packaging["base_image"] == EXPECTED_BASE_IMAGE
    assert packaging["images"] == {
        "order-api": "orderflow/order-api:phase4-v1",
        "inventory": "orderflow/inventory:phase4-v1",
        "telemetry-sink": "orderflow/telemetry-sink:phase4-v1",
    }
    for key in ("dockerfile", "entrypoint"):
        assert (ROOT / packaging[key]).is_file()


def test_phase4_dockerfile_uses_the_manifest_pinned_base_image() -> None:
    manifest = load_manifest()
    packaging = manifest["packaging"]
    first_instruction = DOCKERFILE.read_text(encoding="utf-8").splitlines()[0]
    assert first_instruction == f"FROM {packaging['base_image']}"
    assert "@sha256:" in first_instruction
    assert first_instruction == f"FROM {EXPECTED_BASE_IMAGE}"


def test_phase4_prototype_manifest_keeps_empirical_claims_out_of_scope() -> None:
    manifest = load_manifest()
    exclusions = set(manifest["exclusions"])
    assert "phase-5-pilot-execution" in exclusions
    assert "reliability-effect-claims" in exclusions
    assert "production-readiness-claims" in exclusions
    assert "human-participant-evidence" in exclusions


def test_phase4_prototype_manifest_pins_bounded_opentelemetry_path() -> None:
    manifest = load_manifest()
    observability = manifest["observability"]
    assert observability["mode"] == "structured-event-span-mirror"
    assert observability["authoritative_audit_record"] == "structured-jsonl"
    assert observability["claim_boundary"] == "small-technical-trace-telemetry-only"
    assert observability["collector"]["image"] == "otel/opentelemetry-collector:0.158.0"
    assert (
        observability["collector"]["digest"]
        == "sha256:5b97e6e3550ec6e48a71dba6f6304d349a293af8df4ee1f51da67be94fce2ecd"
    )
    assert observability["python_packages"] == {
        "opentelemetry-api": "1.44.0",
        "opentelemetry-sdk": "1.44.0",
        "opentelemetry-exporter-otlp-proto-http": "1.44.0",
        "opentelemetry-proto": "1.44.0",
    }
    assert observability["expected_order_spans_per_request"] == 5
    assert observability["expected_order_span_count"] == 15
    assert observability["requirements_lock"] == {
        "path": "observability/opentelemetry/phase4-requirements.lock",
        "sha256": "9b0cd979109fe6054562678dce5ddb6089bf309ab8e0955de68c4e28dbd239e8",
        "resolution": "exact-pins-only-binary-wheels",
    }


def test_phase4_dockerfile_uses_locked_otel_runtime_dependencies_and_sink() -> None:
    text = DOCKERFILE.read_text(encoding="utf-8")
    lock_text = OTEL_LOCK.read_text(encoding="utf-8")
    for package in (
        "opentelemetry-api==1.44.0",
        "opentelemetry-sdk==1.44.0",
        "opentelemetry-exporter-otlp-proto-http==1.44.0",
        "opentelemetry-proto==1.44.0",
        "opentelemetry-exporter-otlp-proto-common==1.44.0",
        "opentelemetry-semantic-conventions==0.65b0",
        "protobuf==7.35.1",
        "requests==2.34.2",
    ):
        assert package in lock_text
    assert "COPY observability/opentelemetry/phase4-requirements.lock" in text
    assert "--only-binary=:all:" in text
    assert "-r /tmp/phase4-requirements.lock" in text
    assert "system/orderflow/otel_runtime.py" in text
    assert "observability/opentelemetry/telemetry_sink.py" in text


def test_phase4_otel_lock_hash_matches_manifest() -> None:
    manifest = load_manifest()
    expected = manifest["observability"]["requirements_lock"]["sha256"]
    assert hashlib.sha256(OTEL_LOCK.read_bytes()).hexdigest() == expected
