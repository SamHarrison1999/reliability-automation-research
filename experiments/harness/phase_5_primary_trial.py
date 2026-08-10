#!/usr/bin/env python3
"""Guarded sequential executor for the frozen Phase 5 primary pilot.

The executor derives the next permissible action from preserved raw evidence.
It does not accept an arbitrary scenario, condition or schedule slot from the
operator.  A reserve can be activated only immediately after an invalid
same-cell attempt and at most twice per cell.
"""

from __future__ import annotations

import argparse
import json
import platform
import socket
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from experiments.harness import phase_5_single_trial as runtime

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BATCH = ROOT / "experiments" / "manifests" / "phase-5-primary-batch.json"
DEFAULT_RUN_ORDER = ROOT / "experiments" / "manifests" / "phase-5-primary-run-order.json"
PRIMARY_RAW_ROOT = ROOT / "results" / "phase-5" / "raw"
PRIMARY_PROTOTYPE = ROOT / "infrastructure" / "prototype" / "orderflow-phase-5-primary.json"

PRIMARY_EXECUTOR_VERSION = "phase-5-primary-trial-controller-v1.0"
PRIMARY_EVIDENCE_BOUNDARY = "technical-pilot-only"


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object."""

    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def sha256_file(path: Path) -> str:
    """Reuse exact-byte provenance hashing."""

    return runtime.sha256_file(path)


def completed_attempts(
    raw_root: Path,
    batch_id: str,
) -> list[dict[str, Any]]:
    """Load completed attempts for one batch and reject incomplete evidence."""

    if not raw_root.exists():
        return []

    attempts: list[dict[str, Any]] = []
    for directory in sorted(path for path in raw_root.iterdir() if path.is_dir()):
        manifest_path = directory / "trial-manifest.json"
        if not manifest_path.is_file():
            raise RuntimeError(f"primary raw directory has no trial manifest: {directory.name}")
        manifest = load_json(manifest_path)
        if manifest.get("pilot_batch_id") != batch_id:
            raise RuntimeError(f"primary raw evidence belongs to a different batch: {directory.name}")
        validity_path = directory / "validity.json"
        if not validity_path.is_file():
            raise RuntimeError(f"incomplete primary attempt has no validity record: {directory.name}")
        validity = load_json(validity_path)
        if validity.get("trial_id") != manifest.get("trial_id"):
            raise RuntimeError(f"trial/validity identity mismatch: {directory.name}")
        attempts.append(
            {
                "directory": directory,
                "manifest": manifest,
                "validity": validity,
            }
        )
    return attempts


def _attempt_for_primary_slot(
    attempts: list[dict[str, Any]],
    schedule_slot: int,
) -> dict[str, Any] | None:
    matches = [
        attempt
        for attempt in attempts
        if attempt["manifest"].get("reserve") is False
        and int(attempt["manifest"].get("primary_schedule_slot", -1)) == schedule_slot
    ]
    if len(matches) > 1:
        raise RuntimeError(f"primary schedule slot {schedule_slot} was attempted twice")
    return matches[0] if matches else None


def _reserves_for_repetition(
    attempts: list[dict[str, Any]],
    schedule_slot: int,
) -> list[dict[str, Any]]:
    reserves = [
        attempt
        for attempt in attempts
        if attempt["manifest"].get("reserve") is True
        and int(attempt["manifest"].get("primary_schedule_slot", -1)) == schedule_slot
    ]
    return sorted(
        reserves,
        key=lambda attempt: int(attempt["manifest"].get("reserve_ordinal", 0)),
    )


def next_action(
    batch: dict[str, Any],
    run_order: dict[str, Any],
    attempts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return the only next action permitted by the frozen schedule."""

    slots = cast(list[dict[str, Any]], run_order["slots"])
    attempt_sequence = len(attempts) + 1

    for slot in slots:
        schedule_slot = int(slot["schedule_slot"])
        primary = _attempt_for_primary_slot(attempts, schedule_slot)
        if primary is None:
            return {
                "action": "primary",
                "attempt_sequence": attempt_sequence,
                "schedule_slot": schedule_slot,
                "slot": slot,
            }

        if primary["validity"].get("passed") is True:
            continue

        reserves = _reserves_for_repetition(attempts, schedule_slot)
        if not reserves:
            return {
                "action": "reserve",
                "attempt_sequence": attempt_sequence,
                "schedule_slot": schedule_slot,
                "slot": slot,
                "reserve_ordinal": 1,
                "source_invalid_trial_id": primary["manifest"]["trial_id"],
            }

        last = reserves[-1]
        for expected, reserve in enumerate(reserves, start=1):
            if int(reserve["manifest"].get("reserve_ordinal", -1)) != expected:
                raise RuntimeError(f"non-contiguous reserve history for schedule slot {schedule_slot}")
            if reserve["manifest"].get("cell_id") != slot["cell_id"]:
                raise RuntimeError(f"reserve cell mismatch for schedule slot {schedule_slot}")

        if last["validity"].get("passed") is True:
            continue

        last_ordinal = int(last["manifest"]["reserve_ordinal"])
        if last_ordinal >= 2:
            return {
                "action": "pause",
                "reason": "reserve-exhausted",
                "schedule_slot": schedule_slot,
                "cell_id": slot["cell_id"],
                "last_invalid_trial_id": last["manifest"]["trial_id"],
            }

        return {
            "action": "reserve",
            "attempt_sequence": attempt_sequence,
            "schedule_slot": schedule_slot,
            "slot": slot,
            "reserve_ordinal": last_ordinal + 1,
            "source_invalid_trial_id": last["manifest"]["trial_id"],
        }

    return {
        "action": "complete",
        "completed_primary_slots": len(slots),
        "attempt_count": len(attempts),
    }


def verify_batch_files(
    batch_path: Path,
    run_order_path: Path,
    batch: dict[str, Any],
) -> None:
    """Verify the freeze artefacts and every bound source byte."""

    expected_run_order = batch["primary_run_order"]["sha256"]
    observed_run_order = sha256_file(run_order_path)
    if observed_run_order != expected_run_order:
        raise RuntimeError(
            f"primary run-order hash mismatch: expected={expected_run_order}, observed={observed_run_order}"
        )

    for relative, expected in cast(dict[str, str], batch["source_bindings"]).items():
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"frozen source is missing: {relative}")
        observed = sha256_file(path)
        if observed != expected:
            raise RuntimeError(f"frozen source hash mismatch for {relative}: expected={expected}, observed={observed}")

    if batch_path.resolve() != DEFAULT_BATCH.resolve():
        raise RuntimeError("primary execution requires the canonical batch path")
    if run_order_path.resolve() != DEFAULT_RUN_ORDER.resolve():
        raise RuntimeError("primary execution requires the canonical run-order path")


def require_clean_tracked_tree() -> str:
    """Require a clean tracked tree and return actual execution HEAD."""

    for args, label in (
        (["git", "diff", "--quiet"], "unstaged"),
        (["git", "diff", "--cached", "--quiet"], "staged"),
    ):
        result = subprocess.run(args, cwd=ROOT, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"{label} tracked changes are present")
    return runtime.run_command(["git", "rev-parse", "HEAD"]).stdout.strip()


class Phase5PrimaryTrial(runtime.Phase5DevelopmentTrial):
    """Reuse the validated Kubernetes mechanics under frozen primary identity."""

    def __init__(
        self,
        batch_path: Path,
        run_order_path: Path,
        batch: dict[str, Any],
        action: dict[str, Any],
        output_root: Path,
    ) -> None:
        slot = cast(dict[str, Any], action["slot"])
        super().__init__(
            str(slot["scenario_id"]),
            str(slot["automation_condition"]),
            output_root,
            development_validation=True,
        )
        self.batch_path = batch_path
        self.run_order_path = run_order_path
        self.batch = batch
        self.action = action
        self.prototype = load_json(PRIMARY_PROTOTYPE)
        self.repetition = int(slot["repetition"])
        self.run_order = int(action["attempt_sequence"])
        self.primary_schedule_slot = int(slot["schedule_slot"])
        self.cell_id = str(slot["cell_id"])
        self.reserve = action["action"] == "reserve"
        self.reserve_ordinal = int(action["reserve_ordinal"]) if self.reserve else None
        self.source_invalid_trial_id = str(action["source_invalid_trial_id"]) if self.reserve else None

        prefix = "reserve" if self.reserve else "primary"
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        self.trial_id = (
            f"phase5-{prefix}-slot-{self.primary_schedule_slot:03d}-"
            f"{self.scenario_id}-{self.condition}-{stamp}-{uuid.uuid4().hex[:8]}"
        )
        self.run_id = f"{self.trial_id}-run"
        self.run_dir = output_root / self.trial_id
        self.event_file = self.run_dir / "events.jsonl"
        self.service_event_file = self.run_dir / "service-events.jsonl"
        self.workload_file = self.run_dir / "workload.json"
        self.trial_manifest_file = self.run_dir / "trial-manifest.json"
        self.metadata_file = self.run_dir / "metadata.json"
        self.validity_file = self.run_dir / "validity.json"
        self.otel_payload_file = self.run_dir / "otel-payloads.json"
        self.otel_span_file = self.run_dir / "otel-spans.json"

    def emit(self, event_type: str, **fields: Any) -> dict[str, Any]:
        """Write one controller event with frozen primary identity."""

        if event_type == "trial_started":
            fields["evidence_boundary"] = PRIMARY_EVIDENCE_BOUNDARY

        event = {
            "event_id": (f"phase5-primary-controller-{self.trial_id}-{len(self.events) + 1:05d}"),
            "trial_id": self.trial_id,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "automation_condition": self.condition,
            "repetition": self.repetition,
            "run_order": self.run_order,
            "primary_schedule_slot": self.primary_schedule_slot,
            "pilot_batch_id": self.batch["pilot_batch_id"],
            "reserve": self.reserve,
            "source_component": "phase5-primary-trial-controller",
            "event_type": event_type,
            "timestamp": runtime.utc_now(),
            "monotonic_ns": time.monotonic_ns(),
            "software_version": PRIMARY_EXECUTOR_VERSION,
            "runtime_controller_version": runtime.CONTROLLER_VERSION,
            **fields,
        }
        self.events.append(event)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        with self.event_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        return event

    def verify_source_tree_clean(self) -> None:
        """Verify cleanliness plus the exact frozen source bindings."""

        head = require_clean_tracked_tree()
        verify_batch_files(
            self.batch_path,
            self.run_order_path,
            self.batch,
        )
        self.emit(
            "source_tree_verified",
            repository_commit_sha=head,
            bound_source_commit_sha=self.batch["bound_source_commit_sha"],
            tracked_changes=False,
            source_binding_count=len(self.batch["source_bindings"]),
            frozen_bindings_match=True,
        )

    def deploy(self) -> None:
        """Deploy while propagating actual primary repetition/run order."""

        self.emit("deployment_started", namespace=runtime.NAMESPACE)
        self.kubectl("apply", "-f", str(runtime.KUBERNETES_MANIFEST))
        for deployment in ("inventory", "order-api"):
            self.kubectl(
                "-n",
                runtime.NAMESPACE,
                "set",
                "env",
                f"deployment/{deployment}",
                f"ORDERFLOW_RUN_ID={self.run_id}",
                f"ORDERFLOW_SCENARIO_ID={self.scenario_id}",
                f"ORDERFLOW_TRIAL_ID={self.trial_id}",
                f"ORDERFLOW_AUTOMATION_CONDITION={self.condition}",
                f"ORDERFLOW_REPETITION={self.repetition}",
                f"ORDERFLOW_RUN_ORDER={self.run_order}",
            )
        for deployment in (
            "telemetry-sink",
            "otel-collector",
            "inventory",
            "order-api",
        ):
            self.kubectl(
                "-n",
                runtime.NAMESPACE,
                "rollout",
                "status",
                f"deployment/{deployment}",
                "--timeout=120s",
            )
        self.emit("deployment_completed", namespace=runtime.NAMESPACE)

    def materialise_trial_manifest(self) -> None:
        """Write the frozen primary identity before treatment execution."""

        recovery = self.scenario.get("recovery_action")
        recovery_hash = runtime.sha256_json(recovery) if recovery is not None else None
        self.recovery_action_hash = recovery_hash
        payload = {
            "manifest_type": "phase-5-primary-trial-manifest",
            "protocol_id": self.design["protocol_id"],
            "manifest_version": self.design["manifest_version"],
            "evidence_boundary": PRIMARY_EVIDENCE_BOUNDARY,
            "trial_id": self.trial_id,
            "run_id": self.run_id,
            "cell_id": self.cell_id,
            "scenario_id": self.scenario_id,
            "automation_condition": self.condition,
            "repetition": self.repetition,
            "run_order": self.run_order,
            "primary_schedule_slot": self.primary_schedule_slot,
            "reserve": self.reserve,
            "reserve_ordinal": self.reserve_ordinal,
            "source_invalid_trial_id": self.source_invalid_trial_id,
            "pilot_batch_id": self.batch["pilot_batch_id"],
            "repository_commit_sha": runtime.run_command(["git", "rev-parse", "HEAD"]).stdout.strip(),
            "bound_source_commit_sha": self.batch["bound_source_commit_sha"],
            "batch_manifest_sha256": sha256_file(self.batch_path),
            "primary_run_order_sha256": sha256_file(self.run_order_path),
            "pilot_manifest_sha256": sha256_file(runtime.PILOT_MANIFEST),
            "protocol_sha256": sha256_file(runtime.PROTOCOL),
            "prototype_manifest_sha256": sha256_file(PRIMARY_PROTOTYPE),
            "kubernetes_manifest_sha256": sha256_file(runtime.KUBERNETES_MANIFEST),
            "scenario": self.scenario,
            "canonical_recovery_action_sha256": recovery_hash,
            "controller_version": runtime.CONTROLLER_VERSION,
            "primary_execution_controller_version": PRIMARY_EXECUTOR_VERSION,
            "timing_contract_version": "phase-5-primary-timing-v1",
            "started_at": runtime.utc_now(),
        }
        if self.trial_manifest_file.exists():
            raise RuntimeError("trial manifest already exists")
        self.trial_manifest_file.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.emit(
            "trial_manifest_written",
            canonical_recovery_action_sha256=recovery_hash,
            reserve_ordinal=self.reserve_ordinal,
            source_invalid_trial_id=self.source_invalid_trial_id,
        )

    def write_metadata(self) -> None:
        """Write immutable primary provenance metadata."""

        head = runtime.run_command(["git", "rev-parse", "HEAD"]).stdout.strip()
        context = self.kubectl("config", "current-context", check=False).stdout.strip()
        metadata = {
            "trial_id": self.trial_id,
            "run_id": self.run_id,
            "evidence_boundary": PRIMARY_EVIDENCE_BOUNDARY,
            "controller_version": runtime.CONTROLLER_VERSION,
            "primary_execution_controller_version": PRIMARY_EXECUTOR_VERSION,
            "scenario_id": self.scenario_id,
            "automation_condition": self.condition,
            "cell_id": self.cell_id,
            "repetition": self.repetition,
            "run_order": self.run_order,
            "primary_schedule_slot": self.primary_schedule_slot,
            "reserve": self.reserve,
            "reserve_ordinal": self.reserve_ordinal,
            "source_invalid_trial_id": self.source_invalid_trial_id,
            "pilot_batch_id": self.batch["pilot_batch_id"],
            "repository_commit_sha": head,
            "bound_source_commit_sha": self.batch["bound_source_commit_sha"],
            "batch_manifest_sha256": sha256_file(self.batch_path),
            "primary_run_order_sha256": sha256_file(self.run_order_path),
            "pilot_manifest_sha256": sha256_file(runtime.PILOT_MANIFEST),
            "protocol_sha256": sha256_file(runtime.PROTOCOL),
            "prototype_manifest_sha256": sha256_file(PRIMARY_PROTOTYPE),
            "kubernetes_manifest_sha256": sha256_file(runtime.KUBERNETES_MANIFEST),
            "recovery_action_sha256": self.recovery_action_hash,
            "images": self.image_records,
            "kubernetes_node_images": self.node_image_records,
            "external_images": self.external_image_records,
            "kubernetes_context": context,
            "docker_version": runtime.command_version(
                [
                    "docker",
                    "version",
                    "--format",
                    "Client={{.Client.Version}} Server={{.Server.Version}}",
                ]
            ),
            "kubectl_version": runtime.command_version(["kubectl", "version"]),
            "host": {
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "python": platform.python_version(),
            },
            "created_at": runtime.utc_now(),
        }
        self.metadata_file.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def write_validity(self) -> dict[str, Any]:
        """Classify the primary attempt while preserving invalid evidence."""

        event_types = [str(event["event_type"]) for event in self.events]
        is_fault = self.scenario_id in runtime.FAULT_SCENARIOS
        checks = {
            "primary_guard": True,
            "frozen_batch_bound": True,
            "source_bindings_verified": any(
                event["event_type"] == "source_tree_verified" and event.get("frozen_bindings_match") is True
                for event in self.events
            ),
            "preflight_completed": "preflight_completed" in event_types,
            "trial_manifest_written": self.trial_manifest_file.exists(),
            "clean_before_deploy": any(
                event["event_type"] == "clean_state_verified"
                and event.get("stage") == "before_deploy"
                and event.get("namespace_present") is False
                for event in self.events
            ),
            "images_built": set(self.image_records) == {"inventory", "order-api", "telemetry-sink"},
            "node_images_available": set(self.node_image_records)
            == {"inventory", "order-api", "telemetry-sink", "otel-collector"},
            "deployment_completed": "deployment_completed" in event_types,
            "readiness_verified": "readiness_verified" in event_types,
            "version_verified": "version_verified" in event_types,
            "fault_application_verified": ("fault_application_verified" in event_types if is_fault else True),
            "fault_detected": "fault_detected" in event_types if is_fault else True,
            "recovery_completed": ("recovery_completed" in event_types if is_fault else True),
            "correct_initiator": (
                (
                    self.condition == "manual"
                    and "external_intervention" in event_types
                    and "automation_evaluation" not in event_types
                )
                or (
                    self.condition == "automated"
                    and "automation_evaluation" in event_types
                    and "external_intervention" not in event_types
                )
                if is_fault
                else True
            ),
            "workload_completed": "workload_completed" in event_types,
            "observation_verified": "observation_verified" in event_types,
            "otel_observation_verified": "otel_observation_verified" in event_types,
            "clean_after_run": any(
                event["event_type"] == "clean_state_verified"
                and event.get("stage") == "after_cleanup"
                and event.get("namespace_present") is False
                for event in self.events
            ),
            "fresh_output_directory": self.run_dir.name == self.trial_id,
            "provenance_written": self.metadata_file.exists(),
            "no_execution_error": self.execution_error is None,
        }
        passed = all(checks.values())
        validity = {
            "trial_id": self.trial_id,
            "run_id": self.run_id,
            "cell_id": self.cell_id,
            "scenario_id": self.scenario_id,
            "automation_condition": self.condition,
            "evidence_boundary": PRIMARY_EVIDENCE_BOUNDARY,
            "pilot_batch_id": self.batch["pilot_batch_id"],
            "primary_schedule_slot": self.primary_schedule_slot,
            "run_order": self.run_order,
            "repetition": self.repetition,
            "reserve": self.reserve,
            "reserve_ordinal": self.reserve_ordinal,
            "source_invalid_trial_id": self.source_invalid_trial_id,
            "passed": passed,
            "checks": checks,
            "execution_error": self.execution_error,
            "classification": ("valid-primary-pilot-trial" if passed else "invalid-primary-pilot-trial"),
            "created_at": runtime.utc_now(),
        }
        self.validity_file.write_text(
            json.dumps(validity, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return validity

    def execute(self) -> dict[str, Any]:
        """Execute exactly one schedule-derived primary or reserve attempt."""

        if self.run_dir.exists():
            raise RuntimeError(f"refusing to reuse output directory: {self.run_dir}")
        self.run_dir.mkdir(parents=True)
        self.emit("trial_started", evidence_boundary=PRIMARY_EVIDENCE_BOUNDARY)
        try:
            self.ensure_prerequisites()
            self.verify_source_tree_clean()
            self.materialise_trial_manifest()
            self.clean_before_deploy()
            self.build_images()
            self.verify_external_image()
            self.import_images_into_kubernetes_node()
            self.deploy()
            self.wait_and_forward()
            self.verify_versions_and_clean_fault_state()
            self.execute_scenario_workload()
            self.verify_observation()
            self.cleanup()
            self.emit("trial_completed", result="success")
        except Exception as exc:
            self.execution_error = f"{type(exc).__name__}: {exc}"
            self.emit("trial_failed", error=self.execution_error)
            try:
                self.capture_service_logs(stage="failure")
            except Exception as capture_exc:
                self.emit(
                    "service_log_capture_failed",
                    error=f"{type(capture_exc).__name__}: {capture_exc}",
                )
            try:
                self.cleanup()
            except Exception as cleanup_exc:
                self.emit(
                    "cleanup_failed",
                    error=f"{type(cleanup_exc).__name__}: {cleanup_exc}",
                )
        finally:
            self.stop_all_port_forwards()
            self.write_workload()
            self.write_metadata()
        return self.write_validity()


def load_frozen_state(
    batch_path: Path = DEFAULT_BATCH,
    run_order_path: Path = DEFAULT_RUN_ORDER,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load and cross-check the canonical batch/run-order files."""

    if not batch_path.is_file() or not run_order_path.is_file():
        raise RuntimeError("primary batch has not been frozen")
    batch = load_json(batch_path)
    run_order = load_json(run_order_path)
    if run_order.get("primary_slot_count") != 50:
        raise RuntimeError("frozen primary run order does not contain 50 slots")
    if batch.get("pilot_batch_id") in (None, ""):
        raise RuntimeError("frozen batch has no pilot_batch_id")
    verify_batch_files(batch_path, run_order_path, batch)
    return batch, run_order


def plan_next(
    raw_root: Path = PRIMARY_RAW_ROOT,
) -> dict[str, Any]:
    """Return the next permissible action without executing Kubernetes."""

    batch, run_order = load_frozen_state()
    attempts = completed_attempts(raw_root, str(batch["pilot_batch_id"]))
    return next_action(batch, run_order, attempts)


def main() -> int:
    """Plan or execute the only schedule-permitted next attempt."""

    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan-next", action="store_true")
    mode.add_argument("--execute-next", action="store_true")
    parser.add_argument(
        "--confirm-frozen-primary",
        action="store_true",
        help="Required acknowledgement for primary Kubernetes execution.",
    )
    args = parser.parse_args()

    batch, run_order = load_frozen_state()
    attempts = completed_attempts(PRIMARY_RAW_ROOT, str(batch["pilot_batch_id"]))
    action = next_action(batch, run_order, attempts)

    if args.plan_next:
        print(json.dumps(action, indent=2, sort_keys=True))
        return 0

    if not args.confirm_frozen_primary:
        parser.error("--confirm-frozen-primary is required with --execute-next")
    if action["action"] == "pause":
        parser.error(f"primary pilot is paused: {action['reason']}")
    if action["action"] == "complete":
        print(json.dumps(action, indent=2, sort_keys=True))
        return 0
    if action["action"] not in {"primary", "reserve"}:
        parser.error(f"unexpected next action: {action['action']}")

    require_clean_tracked_tree()
    trial = Phase5PrimaryTrial(
        DEFAULT_BATCH,
        DEFAULT_RUN_ORDER,
        batch,
        action,
        PRIMARY_RAW_ROOT,
    )
    validity = trial.execute()
    print(
        json.dumps(
            {
                "trial_id": trial.trial_id,
                "run_id": trial.run_id,
                "run_directory": str(trial.run_dir),
                "passed": validity["passed"],
                "classification": validity["classification"],
                "pilot_batch_id": batch["pilot_batch_id"],
                "primary_schedule_slot": trial.primary_schedule_slot,
                "run_order": trial.run_order,
                "repetition": trial.repetition,
                "reserve": trial.reserve,
                "reserve_ordinal": trial.reserve_ordinal,
                "next_action_requires_replanning": True,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if validity["passed"] else 1


if __name__ == "__main__":  # pragma: no cover - CLI boundary
    sys.exit(main())
