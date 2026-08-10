#!/usr/bin/env python3
"""Freeze the exact Phase 5 primary batch before primary trial 1.

This module never deploys Kubernetes and never writes trial evidence.  It binds
the already-committed primary execution/analysis source snapshot, generates the
50-slot deterministic primary schedule and writes both freeze artefacts once.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, cast

from experiments.harness import phase_5_run_order

ROOT = Path(__file__).resolve().parents[2]
PILOT_MANIFEST = ROOT / "experiments" / "manifests" / "phase-5-pilot-manifest.json"
DEFAULT_RUN_ORDER = ROOT / "experiments" / "manifests" / "phase-5-primary-run-order.json"
DEFAULT_BATCH = ROOT / "experiments" / "manifests" / "phase-5-primary-batch.json"
PRIMARY_RAW_ROOT = ROOT / "results" / "phase-5" / "raw"

BATCH_FORMAT_VERSION = "phase-5-primary-batch-v1"
FREEZE_GENERATOR_VERSION = "phase-5-batch-freeze-generator-v1"

SOURCE_BINDING_PATHS = (
    "analysis/phase_5/phase_5_primary_metrics.py",
    "data/schemas/phase-5-primary-processed-observation.md",
    "docs/metrics/phase-5-primary-analysis.md",
    "docs/protocols/phase-5-technical-pilot.md",
    "experiments/harness/phase_5_batch_freeze.py",
    "experiments/harness/phase_5_primary_trial.py",
    "experiments/harness/phase_5_run_order.py",
    "experiments/harness/phase_5_single_trial.py",
    "experiments/manifests/phase-5-pilot-manifest.json",
    "infrastructure/kubernetes/Dockerfile",
    "infrastructure/kubernetes/entrypoint.sh",
    "infrastructure/kubernetes/orderflow-phase-5.yaml",
    "infrastructure/prototype/orderflow-phase-4.json",
    "infrastructure/prototype/orderflow-phase-5-primary.json",
    "infrastructure/prototype/orderflow-phase-5.json",
    "observability/opentelemetry/phase4-requirements.lock",
    "observability/opentelemetry/telemetry_sink.py",
    "pyproject.toml",
    "system/orderflow/otel_runtime.py",
    "system/orderflow/service.py",
)


def canonical_json_bytes(value: object) -> bytes:
    """Return stable pretty JSON bytes."""

    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    """Return lowercase SHA-256."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash exact file bytes."""

    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object."""

    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def run_git(*args: str) -> str:
    """Run one read-only Git command."""

    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def require_clean_tracked_tree() -> str:
    """Require no staged or unstaged tracked changes and return HEAD."""

    if subprocess.run(["git", "diff", "--quiet"], cwd=ROOT, check=False).returncode != 0:
        raise RuntimeError("tracked working-tree changes are present")
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False).returncode != 0:
        raise RuntimeError("staged changes are present")
    return run_git("rev-parse", "HEAD")


def require_no_primary_evidence(raw_root: Path = PRIMARY_RAW_ROOT) -> None:
    """Refuse batch freeze after any primary trial evidence exists."""

    if not raw_root.exists():
        return
    unexpected = [path for path in raw_root.iterdir() if path.name != ".gitkeep"]
    if unexpected:
        names = ", ".join(sorted(path.name for path in unexpected))
        raise RuntimeError(f"primary evidence already exists; batch freeze is no longer pre-data: {names}")


def source_bindings() -> dict[str, str]:
    """Hash every execution/analysis source file that affects the primary batch."""

    bindings: dict[str, str] = {}
    for relative in SOURCE_BINDING_PATHS:
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"required freeze source is missing: {relative}")
        bindings[relative] = sha256_file(path)
    return bindings


def reserve_templates(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Create the ten pre-declared same-cell reserve identities."""

    templates: list[dict[str, Any]] = []
    for cell in sorted(manifest["pilot_cells"], key=lambda item: str(item["cell_id"])):
        for ordinal in range(1, int(cell["reserve_slots"]) + 1):
            templates.append(
                {
                    "reserve_template_id": (f"{cell['cell_id']}-reserve-{ordinal}"),
                    "cell_id": cell["cell_id"],
                    "scenario_id": cell["scenario_id"],
                    "automation_condition": cell["automation_condition"],
                    "reserve_ordinal": ordinal,
                    "activation": "only-after-invalid-attempt-in-same-cell",
                    "source_invalid_trial_id_required": True,
                }
            )
    if len(templates) != 10:
        raise ValueError("Phase 5 primary batch must pre-declare exactly ten reserves")
    return templates


def build_batch_payload(
    source_commit_sha: str,
    bindings: dict[str, str],
    run_order_payload: dict[str, Any],
    run_order_sha256: str,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Build the deterministic timestamp-free primary batch object."""

    seed_payload = {
        "batch_format_version": BATCH_FORMAT_VERSION,
        "freeze_generator_version": FREEZE_GENERATOR_VERSION,
        "source_commit_sha": source_commit_sha,
        "source_bindings": bindings,
        "primary_run_order_sha256": run_order_sha256,
        "pilot_manifest_sha256": sha256_file(PILOT_MANIFEST),
        "protocol_id": manifest["protocol_id"],
        "manifest_version": manifest["manifest_version"],
    }
    batch_fingerprint = sha256_bytes(canonical_json_bytes(seed_payload))
    batch_id = f"phase5-primary-{batch_fingerprint[:16]}"

    return {
        "batch_format_version": BATCH_FORMAT_VERSION,
        "freeze_generator_version": FREEZE_GENERATOR_VERSION,
        "pilot_batch_id": batch_id,
        "protocol_id": manifest["protocol_id"],
        "pilot_manifest_version": manifest["manifest_version"],
        "evidence_boundary": "technical-pilot-only",
        "bound_source_commit_sha": source_commit_sha,
        "source_bindings": bindings,
        "primary_run_order": {
            "path": str(DEFAULT_RUN_ORDER.relative_to(ROOT)).replace("\\", "/"),
            "sha256": run_order_sha256,
            "primary_slot_count": run_order_payload["primary_slot_count"],
            "run_order_version": run_order_payload["run_order_version"],
            "generator_version": run_order_payload["generator_version"],
            "seed": run_order_payload["seed"],
            "balance_summary": run_order_payload["balance_summary"],
        },
        "reserve_policy": manifest["reserve_policy"],
        "reserve_templates": reserve_templates(manifest),
        "allocation": manifest["allocation"],
        "timing_authority": manifest["timing_authority"],
        "execution_guard": {
            "clean_tracked_tree_required": True,
            "exact_source_binding_match_required": True,
            "sequential_primary_schedule_required": True,
            "invalid_trial_preservation_required": True,
            "reserve_must_immediately_resolve_invalid_attempt": True,
            "maximum_reserves_per_cell": 2,
            "outcome_adaptive_primary_reordering": False,
            "primary_output_root": "results/phase-5/raw",
        },
        "analysis_binding": {
            "tool": "analysis/phase_5/phase_5_primary_metrics.py",
            "descriptive_only": True,
            "p_values": False,
            "utc_fallback_permitted": False,
        },
        "claim_boundary": {
            "supports": [
                "bounded technical pilot execution",
                "descriptive technical reliability observations",
            ],
            "does_not_support": [
                "production readiness",
                "universal reliability improvement",
                "human performance or workload effects",
                "generalised causal conclusions",
            ],
        },
    }


def write_immutable(path: Path, payload: dict[str, Any]) -> bool:
    """Write once, accept byte-identical reruns and reject divergent overwrite."""

    encoded = canonical_json_bytes(payload)
    if path.exists():
        if path.read_bytes() != encoded:
            raise FileExistsError(f"refusing to overwrite different freeze artefact: {path}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return True


def freeze_batch(
    run_order_path: Path = DEFAULT_RUN_ORDER,
    batch_path: Path = DEFAULT_BATCH,
) -> dict[str, Any]:
    """Create or byte-verify both primary freeze artefacts."""

    source_commit = require_clean_tracked_tree()
    require_no_primary_evidence()
    manifest = load_json(PILOT_MANIFEST)
    phase_5_run_order.validate_manifest(manifest)

    run_order_payload = phase_5_run_order.build_run_order_payload(PILOT_MANIFEST, manifest)
    run_order_bytes = phase_5_run_order.canonical_json_bytes(run_order_payload)
    run_order_sha = sha256_bytes(run_order_bytes)

    bindings = source_bindings()
    batch_payload = build_batch_payload(
        source_commit,
        bindings,
        run_order_payload,
        run_order_sha,
        manifest,
    )

    run_order_created = write_immutable(run_order_path, run_order_payload)
    batch_created = write_immutable(batch_path, batch_payload)

    return {
        "pilot_batch_id": batch_payload["pilot_batch_id"],
        "bound_source_commit_sha": source_commit,
        "primary_slot_count": run_order_payload["primary_slot_count"],
        "reserve_template_count": len(batch_payload["reserve_templates"]),
        "run_order_sha256": run_order_sha,
        "batch_sha256": sha256_file(batch_path),
        "run_order_created": run_order_created,
        "batch_created": batch_created,
        "run_order_path": str(run_order_path),
        "batch_path": str(batch_path),
        "pilot_evidence_created": False,
    }


def main() -> int:
    """Freeze the batch; this never runs Kubernetes."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--run-order-output", type=Path, default=DEFAULT_RUN_ORDER)
    parser.add_argument("--batch-output", type=Path, default=DEFAULT_BATCH)
    args = parser.parse_args()

    result = freeze_batch(args.run_order_output, args.batch_output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI boundary
    raise SystemExit(main())
