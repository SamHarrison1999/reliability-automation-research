from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "experiments" / "harness" / "phase_5_batch_freeze.py"
MANIFEST = ROOT / "experiments" / "manifests" / "phase-5-pilot-manifest.json"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("phase_5_batch_freeze", MODULE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_manifest() -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads(MANIFEST.read_text(encoding="utf-8")),
    )


def test_source_bindings_include_execution_analysis_and_runtime_assets() -> None:
    module = load_module()

    required = {
        "analysis/phase_5/phase_5_primary_metrics.py",
        "experiments/harness/phase_5_batch_freeze.py",
        "experiments/harness/phase_5_primary_trial.py",
        "experiments/harness/phase_5_run_order.py",
        "experiments/harness/phase_5_single_trial.py",
        "infrastructure/kubernetes/Dockerfile",
        "infrastructure/kubernetes/entrypoint.sh",
        "infrastructure/prototype/orderflow-phase-5-primary.json",
        "observability/opentelemetry/telemetry_sink.py",
        "system/orderflow/otel_runtime.py",
        "system/orderflow/service.py",
    }
    assert required.issubset(set(module.SOURCE_BINDING_PATHS))


def test_reserve_templates_are_exactly_two_for_every_cell() -> None:
    module = load_module()

    templates = module.reserve_templates(load_manifest())

    assert len(templates) == 10
    by_cell: dict[str, list[int]] = {}
    for item in templates:
        by_cell.setdefault(item["cell_id"], []).append(item["reserve_ordinal"])
        assert item["activation"] == "only-after-invalid-attempt-in-same-cell"
        assert item["source_invalid_trial_id_required"] is True
    assert all(sorted(ordinals) == [1, 2] for ordinals in by_cell.values())
    assert len(by_cell) == 5


def test_batch_payload_is_deterministic_and_timestamp_free() -> None:
    module = load_module()
    manifest = load_manifest()
    run_order = {
        "primary_slot_count": 50,
        "run_order_version": "phase-5-pilot-run-order-v1",
        "generator_version": "phase-5-pilot-run-order-generator-v1",
        "seed": "phase-5-pilot-run-order-v1",
        "balance_summary": {"cell_counts": {"x": 10}},
    }
    bindings = {"a.py": "a" * 64}

    first = module.build_batch_payload(
        "1" * 40,
        bindings,
        run_order,
        "2" * 64,
        manifest,
    )
    second = module.build_batch_payload(
        "1" * 40,
        bindings,
        run_order,
        "2" * 64,
        manifest,
    )

    assert first == second
    encoded = module.canonical_json_bytes(first)
    assert b'"created_at"' not in encoded
    assert b'"frozen_at"' not in encoded
    assert first["pilot_batch_id"].startswith("phase5-primary-")
    assert first["execution_guard"]["sequential_primary_schedule_required"] is True


def test_immutable_writer_rejects_different_freeze_bytes(tmp_path: Path) -> None:
    module = load_module()
    path = tmp_path / "batch.json"
    payload = {"a": 1}

    assert module.write_immutable(path, payload) is True
    assert module.write_immutable(path, payload) is False

    path.write_text('{"different": true}\n', encoding="utf-8")
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        module.write_immutable(path, payload)


def test_freeze_refuses_existing_primary_evidence(tmp_path: Path) -> None:
    module = load_module()
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / ".gitkeep").write_text("", encoding="utf-8")
    module.require_no_primary_evidence(raw)

    (raw / "phase5-primary-existing").mkdir()
    with pytest.raises(RuntimeError, match="primary evidence already exists"):
        module.require_no_primary_evidence(raw)
