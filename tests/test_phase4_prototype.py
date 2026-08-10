"""Contract tests for the versioned Phase 4 OrderFlow prototype manifest."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "infrastructure" / "prototype" / "orderflow-phase-4.json"


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
    assert packaging["base_image"] == "python:3.12-slim"
    assert packaging["images"] == {
        "order-api": "orderflow/order-api:phase4-v1",
        "inventory": "orderflow/inventory:phase4-v1",
    }
    for key in ("dockerfile", "entrypoint"):
        assert (ROOT / packaging[key]).is_file()


def test_phase4_prototype_manifest_keeps_empirical_claims_out_of_scope() -> None:
    manifest = load_manifest()
    exclusions = set(manifest["exclusions"])
    assert "phase-5-pilot-execution" in exclusions
    assert "reliability-effect-claims" in exclusions
    assert "production-readiness-claims" in exclusions
    assert "human-participant-evidence" in exclusions
