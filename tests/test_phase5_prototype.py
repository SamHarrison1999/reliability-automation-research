from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE = ROOT / "infrastructure" / "prototype" / "orderflow-phase-5.json"
ENTRYPOINT = ROOT / "infrastructure" / "kubernetes" / "entrypoint.sh"


def load_prototype() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(PROTOTYPE.read_text(encoding="utf-8")))


def test_phase5_prototype_inherits_bounded_phase4_lineage() -> None:
    prototype = load_prototype()

    assert prototype["prototype_id"] == "orderflow-phase-5-pilot-v1"
    assert prototype["parent_prototype"]["prototype_id"] == "orderflow-phase-4-v1"
    assert prototype["target_model"] == "docker-desktop-kubernetes"
    assert prototype["kubernetes"]["context"] == "docker-desktop"
    assert prototype["kubernetes"]["namespace"] == "orderflow-phase5"


def test_phase5_packaging_and_collector_remain_pinned() -> None:
    prototype = load_prototype()

    assert prototype["packaging"]["build_platform"] == "linux/amd64"
    assert prototype["packaging"]["base_image"].startswith("python:3.12-slim@sha256:")
    assert prototype["packaging"]["images"] == {
        "inventory": "orderflow/inventory:phase5-v1",
        "order-api": "orderflow/order-api:phase5-v1",
        "telemetry-sink": "orderflow/telemetry-sink:phase5-v1",
    }
    assert prototype["observability"]["collector"]["image"] == ("otel/opentelemetry-collector:0.158.0")
    assert prototype["observability"]["collector"]["digest"] == (
        "sha256:5b97e6e3550ec6e48a71dba6f6304d349a293af8df4ee1f51da67be94fce2ecd"
    )


def test_phase5_prototype_explicitly_blocks_primary_batch_consumption() -> None:
    guard = load_prototype()["execution_guard"]

    assert guard["mode"] == "single-development-validation-trial-only"
    assert guard["primary_batch_schedule_consumption"] is False
    assert guard["required_cli_flag"] == "--development-validation"
    assert guard["default_output_root"] == "results/phase-5/development/raw"


def test_entrypoint_passes_phase5_trial_identity_only_when_present() -> None:
    text = ENTRYPOINT.read_text(encoding="utf-8")

    for variable, argument in (
        ("ORDERFLOW_TRIAL_ID", "--trial-id"),
        ("ORDERFLOW_AUTOMATION_CONDITION", "--automation-condition"),
        ("ORDERFLOW_REPETITION", "--repetition"),
        ("ORDERFLOW_RUN_ORDER", "--run-order"),
    ):
        assert f"${{{variable}:-}}" in text
        assert argument in text
