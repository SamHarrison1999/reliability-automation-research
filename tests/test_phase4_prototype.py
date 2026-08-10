"""Contract tests for the versioned Phase 4 OrderFlow prototype manifest."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "infrastructure" / "prototype" / "orderflow-phase-4.json"
DOCKERFILE = ROOT / "infrastructure" / "kubernetes" / "Dockerfile"

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
