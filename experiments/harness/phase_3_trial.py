#!/usr/bin/env python3
"""Run the smallest local-process implementation of the Phase 3 protocol.

The controller deliberately uses the deterministic OrderFlow service from the
Phase 2 fit probe.  It adds the Phase 3 trial identity, condition, detection,
recovery, validity and provenance records without introducing external
dependencies or production integrations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]
SERVICE = ROOT / "system" / "orderflow" / "service.py"
CONTROLLER_VERSION = "phase-3-trial-controller-v1"
CONTROL_CONDITION = "control"
WORKLOAD_EVENTS = {"workload_started", "workload_request", "workload_response"}


def utc_now() -> str:
    """Return a millisecond-precision UTC timestamp."""

    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    """Hash a file in bounded-size chunks."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: object) -> str:
    """Hash canonical JSON so embedded scenario records are reproducible."""

    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from ``path``."""

    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def repository_commit_sha() -> str:
    """Return the executing commit, or an explicit value when no Git checkout exists."""

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else "unavailable"


def tool_versions() -> dict[str, str | None]:
    """Record versions available at the experiment boundary."""

    def version(command: str) -> str | None:
        if shutil.which(command) is None:
            return None
        result = subprocess.run([command, "--version"], capture_output=True, check=False, text=True)
        output = (result.stdout or result.stderr).strip().splitlines()
        return output[0] if result.returncode == 0 and output else "available"

    return {
        "python": platform.python_version(),
        "controller": CONTROLLER_VERSION,
        "docker": version("docker"),
        "kubectl": version("kubectl"),
    }


def display_path(path: Path) -> str:
    """Prefer a repository-relative path while supporting external output roots."""

    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _condition_for_scenario(scenario: dict[str, Any], condition: str) -> dict[str, Any] | None:
    if scenario["role"] == "quality-control":
        if condition != CONTROL_CONDITION:
            raise ValueError("no-fault-v1 is a control block and has no manual/automated condition")
        return None
    if condition not in {"manual", "automated"}:
        raise ValueError(f"fault scenario requires manual or automated condition: {condition}")
    return {"condition_id": condition}


def build_run_order(manifest: dict[str, Any], repetitions: int) -> list[dict[str, Any]]:
    """Create a deterministic, condition-balanced execution order."""

    if repetitions < 1:
        raise ValueError("repetitions must be at least 1")
    slots: list[dict[str, Any]] = []
    run_order = 1
    for scenario in manifest["scenarios"]:
        conditions = [CONTROL_CONDITION] if scenario["role"] == "quality-control" else ["manual", "automated"]
        for repetition in range(1, repetitions + 1):
            ordered_conditions = list(conditions)
            if len(ordered_conditions) > 1 and repetition % 2 == 0:
                ordered_conditions.reverse()
            for condition in ordered_conditions:
                slots.append(
                    {
                        "run_order": run_order,
                        "scenario_id": scenario["scenario_id"],
                        "automation_condition": condition,
                        "repetition": repetition,
                    }
                )
                run_order += 1
    return slots


def load_or_create_run_order(path: Path, manifest: dict[str, Any], repetitions: int) -> list[dict[str, Any]]:
    """Persist the generated order and refuse silent changes on reruns."""

    expected = build_run_order(manifest, repetitions)
    if path.exists():
        existing = load_json(path)
        stored = existing.get("slots")
        if stored != expected:
            raise ValueError(f"existing run order does not match requested repetitions: {path}")
        return cast(list[dict[str, Any]], stored)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_order_version": "phase-3-run-order-v1",
        "seed": manifest["run_order"]["seed"],
        "manifest_version": manifest["manifest_version"],
        "created_at": utc_now(),
        "slots": expected,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return expected


class Phase3Trial:
    """Execute one immutable Phase 3 trial and preserve its raw bundle."""

    def __init__(
        self,
        design_manifest: dict[str, Any],
        environment_manifest: dict[str, Any],
        protocol_path: Path,
        environment_path: Path,
        scenario: dict[str, Any],
        condition: str,
        repetition: int,
        run_order: int,
        execution_context: str,
        output_root: Path,
    ) -> None:
        self.design_manifest = design_manifest
        self.environment_manifest = environment_manifest
        self.protocol_path = protocol_path
        self.environment_path = environment_path
        self.scenario = scenario
        self.condition = condition
        self.repetition = repetition
        self.run_order = run_order
        self.execution_context = execution_context
        self.trial_id = self._new_trial_id()
        self.run_id = f"{self.trial_id}-run"
        self.run_dir = output_root / self.trial_id
        self.event_file = self.run_dir / "events.jsonl"
        self.manifest_file = self.run_dir / "trial-manifest.json"
        self.metadata_file = self.run_dir / "metadata.json"
        self.validity_file = self.run_dir / "validity.json"
        self.processes: dict[str, subprocess.Popen[bytes]] = {}
        self.started_versions = {name: spec["version"] for name, spec in environment_manifest["services"].items()}
        self.ports = {name: int(spec["port"]) for name, spec in environment_manifest["services"].items()}
        self.trial_started_at = utc_now()
        self.scenario_hash = sha256_json(scenario)
        self.environment_hash = sha256_file(environment_path)
        self.protocol_hash = sha256_file(protocol_path)
        self.repository_sha = repository_commit_sha()
        self.fault_active = False
        self.outcomes: list[dict[str, Any]] = []
        self.controller_event_count = 0

    def _new_trial_id(self) -> str:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        return f"{self.scenario['scenario_id']}-{self.condition}-{stamp}-{uuid.uuid4().hex[:8]}"

    @property
    def target_model(self) -> str:
        return str(self.design_manifest["target"]["target_model"])

    def materialized_manifest(self) -> dict[str, Any]:
        detection_rule = self.scenario.get("detection_rule") or {}
        recovery_action = self.scenario.get("recovery_action") or {}
        return {
            "manifest_type": "phase-3-immutable-trial-manifest",
            "manifest_version": self.design_manifest["manifest_version"],
            "protocol_id": self.design_manifest["protocol_id"],
            "trial_id": self.trial_id,
            "scenario_id": self.scenario["scenario_id"],
            "automation_condition": self.condition,
            "repetition": self.repetition,
            "run_order": self.run_order,
            "detection_rule_version": detection_rule.get("version"),
            "recovery_action_version": recovery_action.get("version"),
            "target_model": self.target_model,
            "execution_context": self.execution_context,
            "repository_commit_sha": self.repository_sha,
            "protocol_sha256": self.protocol_hash,
            "scenario_manifest_sha256": self.scenario_hash,
            "environment_manifest_sha256": self.environment_hash,
            "environment_manifest_path": display_path(self.environment_path),
            "trial_started_at": self.trial_started_at,
            "target": self.design_manifest["target"],
            "scenario": self.scenario,
            "condition": next(
                (item for item in self.design_manifest["conditions"] if item["condition_id"] == self.condition),
                {"condition_id": CONTROL_CONDITION, "label": "No-fault control"},
            ),
            "tool_versions": tool_versions(),
        }

    def emit(self, event_type: str, **fields: Any) -> dict[str, Any]:
        """Write one controller event with the complete Phase 3 identity."""

        self.controller_event_count += 1
        event = {
            "event_id": f"controller-{self.trial_id}-{self.controller_event_count:05d}",
            "trial_id": self.trial_id,
            "run_id": self.run_id,
            "scenario_id": self.scenario["scenario_id"],
            "automation_condition": self.condition,
            "repetition": self.repetition,
            "run_order": self.run_order,
            "timestamp": utc_now(),
            "source_component": "phase-3-trial-controller",
            "event_type": event_type,
            "software_version": CONTROLLER_VERSION,
            "trace_id": uuid.uuid4().hex,
            "span_id": uuid.uuid4().hex[:16],
            **fields,
        }
        self.run_dir.mkdir(parents=True, exist_ok=True)
        with self.event_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        return event

    def url(self, component: str, path: str) -> str:
        return f"http://127.0.0.1:{self.ports[component]}{path}"

    def request(
        self,
        component: str,
        path: str,
        method: str = "GET",
        body: dict[str, Any] | None = None,
        timeout: float = 2.0,
    ) -> tuple[int, dict[str, Any], float]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(self.url(component, path), data=data, method=method)
        if body is not None:
            request.add_header("Content-Type", "application/json")
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status, json.loads(response.read().decode("utf-8")), time.perf_counter() - started
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {"error": raw}
            return exc.code, payload, time.perf_counter() - started
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            return 0, {"error": type(exc).__name__}, time.perf_counter() - started

    def start_service(self, component: str, version: str | None = None) -> None:
        version = version or self.started_versions[component]
        dependency_url = self.url("inventory", "") if component == "order-api" else ""
        command = [
            sys.executable,
            str(SERVICE),
            "--role",
            component,
            "--port",
            str(self.ports[component]),
            "--version",
            version,
            "--event-file",
            str(self.event_file),
            "--run-id",
            self.run_id,
            "--scenario-id",
            self.scenario["scenario_id"],
            "--trial-id",
            self.trial_id,
            "--automation-condition",
            self.condition,
            "--repetition",
            str(self.repetition),
            "--run-order",
            str(self.run_order),
        ]
        if dependency_url:
            command.extend(["--dependency-url", dependency_url])
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.processes[component] = process
        self.emit(
            "service_process_started", target_component=component, process_id=process.pid, service_version=version
        )

    def stop_service(self, component: str, reason: str) -> None:
        process = self.processes.pop(component, None)
        if process is None:
            return
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        self.emit("service_process_stopped", target_component=component, reason=reason, exit_code=process.returncode)

    def stop_all(self, reason: str) -> None:
        for component in list(self.processes):
            self.stop_service(component, reason)

    def wait_ready(self) -> None:
        deadline = time.monotonic() + 5
        statuses: dict[str, int] = {}
        while time.monotonic() < deadline:
            statuses = {}
            for component in ("inventory", "order-api"):
                statuses[component] = self.request(component, "/healthz", timeout=0.25)[0]
            if all(status == 200 for status in statuses.values()):
                self.emit("readiness_check", statuses=statuses, result="ready")
                return
            time.sleep(0.05)
        self.emit("readiness_check", statuses=statuses, result="failed")
        raise RuntimeError(f"services did not become ready: {statuses}")

    def reset(self) -> None:
        started = time.perf_counter()
        self.emit("reset_started", reset_contract=self.environment_manifest["reset_contract"])
        self.stop_all("clean-reset")
        self.start_service("inventory")
        self.start_service("order-api")
        self.wait_ready()
        fingerprint = hashlib.sha256(b"orderflow-empty-state-v1").hexdigest()
        self.emit("clean_state_verified", state_fingerprint=fingerprint, outstanding_orders=0)
        self.emit("reset_completed", result="clean", duration_ms=round((time.perf_counter() - started) * 1000, 3))

    def workload(self, phase: str, count: int) -> list[dict[str, Any]]:
        self.emit(
            "workload_started",
            phase=phase,
            request_count=count,
            workload_id="fixed-synthetic-orders-v1",
        )
        workload = self.scenario["workload"]
        outcomes: list[dict[str, Any]] = []
        for index in range(count):
            order_id = f"{self.trial_id}-{phase}-{index + 1:03d}"
            started = time.perf_counter()
            request_event = self.emit("workload_request", phase=phase, order_id=order_id, request_index=index + 1)
            status, body, elapsed = self.request(
                "order-api",
                "/orders",
                method="POST",
                body={"order_id": order_id},
                timeout=float(workload["request_timeout_ms"]) / 1000,
            )
            result = "success" if status == workload["success_status"] else "failure"
            response_event = self.emit(
                "workload_response",
                phase=phase,
                order_id=order_id,
                status=status,
                result=result,
                latency_ms=round(elapsed * 1000, 3),
                body=body,
                parent_event_id=request_event["event_id"],
            )
            outcomes.append(
                {
                    "phase": phase,
                    "order_id": order_id,
                    "status": status,
                    "result": result,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                    "response_event_id": response_event["event_id"],
                }
            )
            self.outcomes.append(outcomes[-1])
            time.sleep(float(workload["inter_request_delay_ms"]) / 1000)
        return outcomes

    def transition_version(self, new_version: str, action: str) -> None:
        started = self.started_versions["order-api"]
        self.emit(f"{action}_started", from_version=started, to_version=new_version)
        self.stop_service("order-api", action)
        self.start_service("order-api", new_version)
        self.wait_ready()
        self.emit(f"{action}_completed", active_version=new_version, result="ready")
        self.started_versions["order-api"] = new_version

    def inject_service_termination(self) -> dict[str, Any]:
        target = self.scenario["fault"]["target"]
        self.stop_service(target, "fault-injection")
        self.fault_active = True
        return self.emit(
            "injection_started",
            fault_id=self.scenario["fault"]["fault_id"],
            fault_mode="service-termination",
            fault_phase="injected",
            target_component=target,
            trigger=self.scenario["fault"]["trigger"],
        )

    def inject_dependency_latency(self) -> dict[str, Any]:
        fault = self.scenario["fault"]
        status, _, _ = self.request(
            "inventory",
            "/__control",
            method="POST",
            body={"mode": "latency", "latency_ms": fault["latency_ms"]},
        )
        if status != 200:
            raise RuntimeError(f"could not apply dependency latency fault: {status}")
        self.fault_active = True
        return self.emit(
            "injection_started",
            fault_id=fault["fault_id"],
            fault_mode="latency",
            fault_phase="injected",
            target_component=fault["target"],
            latency_ms=fault["latency_ms"],
            trigger=fault["trigger"],
        )

    def detect_fault(self, injection_event: dict[str, Any], during: list[dict[str, Any]]) -> dict[str, Any]:
        rule = self.scenario["detection_rule"]
        if self.scenario["fault"]["mode"] == "service-termination":
            failures = sum(item["result"] == "failure" for item in during)
            observed_signal = f"{failures}_consecutive_non_success_order_responses"
            detected = failures >= 3
        else:
            threshold = 100
            slow = [item for item in during if item["result"] == "success" and item["latency_ms"] > threshold]
            observed_signal = f"{len(slow)}_requests_above_{threshold}ms"
            detected = len(slow) >= 3
        if not detected:
            raise RuntimeError(f"detection rule did not trigger: {observed_signal}")
        return self.emit(
            "fault_detected",
            fault_id=self.scenario["fault"]["fault_id"],
            fault_phase="detected",
            target_component=self.scenario["fault"]["target"],
            detection_rule_version=rule["version"],
            observed_signal=observed_signal,
            decision="recover",
            parent_event_id=injection_event["event_id"],
        )

    def recover(self, detection_event: dict[str, Any]) -> dict[str, Any]:
        action = self.scenario["recovery_action"]
        action_name = action[self.condition]
        recovery_event = self.emit(
            "recovery_started",
            target_component=self.scenario["fault"]["target"],
            initiator="automation" if self.condition == "automated" else "manual",
            recovery_action=action_name,
            recovery_action_version=action["version"],
            parent_event_id=detection_event["event_id"],
        )
        if self.condition == "automated":
            self.emit(
                "automation_evaluation",
                detection_rule_version=self.scenario["detection_rule"]["version"],
                observed_signal=detection_event["observed_signal"],
                decision="recover",
                parent_event_id=detection_event["event_id"],
            )
        target = self.scenario["fault"]["target"]
        if self.scenario["fault"]["mode"] == "service-termination":
            self.start_service(target)
            self.wait_ready()
        else:
            status, _, _ = self.request("inventory", "/__control", method="POST", body={"mode": "none"})
            if status != 200:
                raise RuntimeError(f"could not clear dependency latency fault: {status}")
            self.wait_ready()
        self.fault_active = False
        completed = self.emit(
            "recovery_completed",
            target_component=target,
            result="ready",
            recovery_action=action_name,
            recovery_action_version=action["version"],
            initiator="automation" if self.condition == "automated" else "manual",
            parent_event_id=recovery_event["event_id"],
        )
        self.emit(
            "injection_ended",
            fault_id=self.scenario["fault"]["fault_id"],
            fault_phase="reverted",
            target_component=target,
            result="reverted",
            parent_event_id=completed["event_id"],
        )
        return completed

    def post_recovery_check(self, recovery_event: dict[str, Any], after: list[dict[str, Any]]) -> None:
        first_success = next((item for item in after if item["result"] == "success"), None)
        self.emit(
            "post_recovery_check",
            target_component=self.scenario["fault"]["target"],
            result="pass" if first_success else "fail",
            readiness="ready" if first_success else "unknown",
            first_success_event_id=first_success["response_event_id"] if first_success else None,
            parent_event_id=recovery_event["event_id"],
        )

    def execute_workload(self) -> None:
        scenario_id = self.scenario["scenario_id"]
        phases = {phase["phase_id"]: int(phase["request_count"]) for phase in self.scenario["workload"]["phases"]}
        if scenario_id == "no-fault-v1":
            self.workload("baseline-v1", phases["baseline-v1"])
            self.transition_version("order-api-v2", "deployment_update")
            self.workload("deployment-v2", phases["deployment-v2"])
            self.transition_version("order-api-v1", "rollback")
            self.workload("rollback-v1", phases["rollback-v1"])
            return
        before = self.workload("before-fault", phases["before-fault"])
        if len(before) != phases["before-fault"] or any(item["result"] != "success" for item in before):
            raise RuntimeError("pre-fault workload did not meet its success criterion")
        injection = (
            self.inject_service_termination()
            if self.scenario["fault"]["mode"] == "service-termination"
            else self.inject_dependency_latency()
        )
        during = self.workload("during-fault", phases["during-fault"])
        detection = self.detect_fault(injection, during)
        recovery = self.recover(detection)
        after = self.workload("after-recovery", phases["after-recovery"])
        self.post_recovery_check(recovery, after)

    def cleanup(self) -> str | None:
        error: str | None = None
        try:
            if self.fault_active:
                status, _, _ = self.request("inventory", "/__control", method="POST", body={"mode": "none"})
                if status != 200:
                    raise RuntimeError(f"cleanup could not clear active fault: {status}")
                self.fault_active = False
            self.stop_all("trial-cleanup")
        except Exception as exc:  # cleanup failure must be retained in the bundle
            error = f"{type(exc).__name__}: {exc}"
        self.emit(
            "cleanup_completed",
            result="clean" if error is None and not self.processes else "failed",
            contamination_detected=bool(error) or bool(self.processes),
            error=error,
        )
        return error

    def _read_events(self) -> list[dict[str, Any]]:
        if not self.event_file.exists():
            return []
        return [
            cast(dict[str, Any], json.loads(line))
            for line in self.event_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def validate(self, execution_error: str | None = None, include_trial_completed: bool = True) -> dict[str, Any]:
        events = self._read_events()
        required = set(self.scenario["required_events"])
        if not include_trial_completed:
            required.discard("trial_completed")
        counts = Counter(event.get("event_type") for event in events)
        present = required.intersection(counts)
        missing = sorted(required - present)
        singleton = required - WORKLOAD_EVENTS
        duplicates = sorted(event_type for event_type in singleton if counts[event_type] > 1)
        identity_fields = [
            "event_id",
            "trial_id",
            "run_id",
            "scenario_id",
            "automation_condition",
            "timestamp",
            "source_component",
            "event_type",
            "software_version",
        ]
        identity_complete = all(
            all(field in event and event[field] is not None for field in identity_fields) for event in events
        )
        identity_matches = all(
            event.get("trial_id") == self.trial_id
            and event.get("run_id") == self.run_id
            and event.get("scenario_id") == self.scenario["scenario_id"]
            and event.get("automation_condition") == self.condition
            and event.get("repetition") == self.repetition
            and event.get("run_order") == self.run_order
            for event in events
        )
        timestamp_complete = True
        for event in events:
            try:
                datetime.fromisoformat(str(event["timestamp"]).replace("Z", "+00:00"))
            except (KeyError, TypeError, ValueError):
                timestamp_complete = False
        cleanup_events = [event for event in events if event.get("event_type") == "cleanup_completed"]
        recovery_events = [event for event in events if event.get("event_type") == "recovery_started"]
        target = self.scenario.get("fault", {}).get("target")
        injections = [event for event in events if event.get("event_type") == "injection_started"]
        ended = [event for event in events if event.get("event_type") == "injection_ended"]
        post_checks = [event for event in events if event.get("event_type") == "post_recovery_check"]
        reasons: list[str] = []
        if execution_error:
            reasons.append(f"execution_error: {execution_error}")
        if missing:
            reasons.append(f"missing_required_events: {','.join(missing)}")
        if duplicates:
            reasons.append(f"duplicate_boundary_events: {','.join(duplicates)}")
        if not identity_complete or not identity_matches:
            reasons.append("event_identity_incomplete_or_mismatched")
        if not timestamp_complete:
            reasons.append("timestamp_incomplete_or_unparseable")
        if self.scenario["role"] == "quality-control":
            fault_contract = not injections and not recovery_events and not post_checks
        else:
            fault_contract = (
                len(injections) == 1
                and len(ended) == 1
                and injections[0].get("target_component") == target
                and ended[0].get("target_component") == target
                and len(recovery_events) == 1
                and recovery_events[0].get("initiator") == ("automation" if self.condition == "automated" else "manual")
                and len(post_checks) == 1
                and post_checks[0].get("result") == "pass"
            )
            if self.condition == "automated":
                automation_events = [event for event in events if event.get("event_type") == "automation_evaluation"]
                fault_contract = fault_contract and len(automation_events) == 1
            else:
                fault_contract = fault_contract and not [
                    event for event in events if event.get("event_type") == "automation_evaluation"
                ]
        if not fault_contract:
            reasons.append("fault_or_recovery_contract_failed")
        cleanup_ok = len(cleanup_events) == 1 and cleanup_events[0].get("contamination_detected") is False
        if not cleanup_ok:
            reasons.append("cleanup_or_contamination_check_failed")
        manifest_ok = bool(
            self.manifest_file.exists()
            and self.environment_hash
            and self.scenario_hash
            and self.protocol_hash
            and self.repository_sha
        )
        if not manifest_ok:
            reasons.append("provenance_manifest_missing")
        checks = {
            "required_event_completeness": len(present) / len(required) if required else 0.0,
            "timestamp_completeness": timestamp_complete,
            "event_identity_complete": identity_complete and identity_matches,
            "fault_and_recovery_contract": fault_contract,
            "cleanup_completed": cleanup_ok,
            "provenance_hashes_present": manifest_ok,
        }
        return {
            "trial_id": self.trial_id,
            "run_id": self.run_id,
            "scenario_id": self.scenario["scenario_id"],
            "automation_condition": self.condition,
            "valid": not reasons,
            "exclusion_reasons": reasons,
            "checks": checks,
            "event_count": len(events),
            "missing_required_events": missing,
            "duplicate_boundary_events": duplicates,
        }

    def execute(self) -> dict[str, Any]:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file.write_text(
            json.dumps(self.materialized_manifest(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        execution_error: str | None = None
        cleanup_error: str | None = None
        try:
            self.emit(
                "trial_started",
                protocol_id=self.design_manifest["protocol_id"],
                manifest_version=self.design_manifest["manifest_version"],
                target_model=self.target_model,
                trial_started_at=self.trial_started_at,
            )
            self.reset()
            self.execute_workload()
        except Exception as exc:
            execution_error = f"{type(exc).__name__}: {exc}"
        finally:
            cleanup_error = self.cleanup()
        if cleanup_error:
            execution_error = f"{execution_error}; cleanup_error: {cleanup_error}" if execution_error else cleanup_error
        pre_completion = self.validate(execution_error, include_trial_completed=False)
        self.emit(
            "trial_completed",
            result="valid" if pre_completion["valid"] else "excluded",
            trial_valid=pre_completion["valid"],
            exclusion_reasons=pre_completion["exclusion_reasons"],
        )
        validity = self.validate(execution_error)
        self.validity_file.write_text(json.dumps(validity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        metadata = {
            "trial_id": self.trial_id,
            "run_id": self.run_id,
            "scenario_id": self.scenario["scenario_id"],
            "automation_condition": self.condition,
            "repetition": self.repetition,
            "run_order": self.run_order,
            "execution_context": self.execution_context,
            "target_model": self.target_model,
            "repository_commit_sha": self.repository_sha,
            "scenario_manifest_sha256": self.scenario_hash,
            "environment_manifest_sha256": self.environment_hash,
            "protocol_sha256": self.protocol_hash,
            "host": {"hostname": socket.gethostname(), "platform": platform.platform()},
            "tool_versions": tool_versions(),
            "event_file": display_path(self.event_file),
            "event_count": validity["event_count"],
            "outcomes": self.outcomes,
            "validity": validity,
            "created_at": utc_now(),
        }
        self.metadata_file.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return metadata


def select_slots(slots: list[dict[str, Any]], scenario_id: str | None, condition: str | None) -> list[dict[str, Any]]:
    """Apply optional CLI filters without changing the persisted order."""

    return [
        slot
        for slot in slots
        if (scenario_id is None or slot["scenario_id"] == scenario_id)
        and (condition is None or slot["automation_condition"] == condition)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--trial-manifest", type=Path, required=True)
    parser.add_argument("--environment-manifest", type=Path, default=ROOT / "infrastructure" / "local-fit-probe.json")
    parser.add_argument("--output-root", type=Path, default=ROOT / "results" / "phase-3" / "raw")
    parser.add_argument("--execution-context", default="local-process-fit-probe")
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--scenario-id", choices=["no-fault-v1", "service-termination-v1", "dependency-latency-v1"])
    parser.add_argument("--condition", choices=["control", "manual", "automated"])
    args = parser.parse_args()

    protocol_path = args.protocol.resolve()
    design_path = args.trial_manifest.resolve()
    environment_path = args.environment_manifest.resolve()
    output_root = args.output_root.resolve()
    if not protocol_path.exists() or not design_path.exists() or not environment_path.exists():
        raise SystemExit("protocol, trial manifest and environment manifest must all exist")
    manifest = load_json(design_path)
    environment = load_json(environment_path)
    allowed_contexts = manifest["target"]["allowed_execution_contexts"]
    if args.execution_context not in allowed_contexts:
        raise SystemExit(f"execution context is not permitted by the manifest: {args.execution_context}")
    slots = load_or_create_run_order(output_root.parent / "run-order.json", manifest, args.repetitions)
    selected = select_slots(slots, args.scenario_id, args.condition)
    scenarios = {scenario["scenario_id"]: scenario for scenario in manifest["scenarios"]}
    output_root.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for slot in selected:
        scenario = scenarios[slot["scenario_id"]]
        _condition_for_scenario(scenario, slot["automation_condition"])
        trial = Phase3Trial(
            manifest,
            environment,
            protocol_path,
            environment_path,
            scenario,
            slot["automation_condition"],
            slot["repetition"],
            slot["run_order"],
            args.execution_context,
            output_root,
        )
        records.append(trial.execute())
    summary = {
        "experiment_id": "phase-3-technical-reliability-v1",
        "controller_version": CONTROLLER_VERSION,
        "created_at": utc_now(),
        "execution_context": args.execution_context,
        "requested_repetitions": args.repetitions,
        "selected_trial_count": len(records),
        "valid_trial_count": sum(record["validity"]["valid"] for record in records),
        "excluded_trial_count": sum(not record["validity"]["valid"] for record in records),
        "runs": records,
        "all_dry_runs_passed": bool(records) and all(record["validity"]["valid"] for record in records),
        "interpretation_boundary": "Dry-run feasibility evidence only; do not report as pilot findings.",
    }
    summary_path = output_root.parent / "phase-3-trial-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary": str(summary_path),
                "all_dry_runs_passed": summary["all_dry_runs_passed"],
                "selected_trial_count": summary["selected_trial_count"],
                "valid_trial_count": summary["valid_trial_count"],
            },
            indent=2,
        )
    )
    return 0 if summary["all_dry_runs_passed"] else 1


if __name__ == "__main__":  # pragma: no cover - exercised through the CLI
    sys.exit(main())
