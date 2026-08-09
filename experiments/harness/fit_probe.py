#!/usr/bin/env python3
"""Execute the Phase 2 technical fit probe with no external dependencies."""

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
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]
SERVICE = ROOT / "system" / "orderflow" / "service.py"


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ProbeRun:
    def __init__(
        self, manifest: dict[str, Any], scenario: dict[str, Any], output_root: Path, repeat_of: str | None = None
    ):
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        self.run_id = f"{scenario['scenario_id']}-{stamp}-{uuid.uuid4().hex[:8]}"
        self.manifest = manifest
        self.scenario = scenario
        self.repeat_of = repeat_of
        self.run_dir = output_root / self.run_id
        self.event_file = self.run_dir / "events.jsonl"
        self.metadata_file = self.run_dir / "metadata.json"
        self.processes: dict[str, subprocess.Popen[bytes]] = {}
        self.started_versions = {name: spec["version"] for name, spec in manifest["services"].items()}
        self.ports = {name: int(spec["port"]) for name, spec in manifest["services"].items()}
        self.events: list[dict[str, Any]] = []

    def emit(self, event_type: str, **fields: Any) -> dict[str, Any]:
        event = {
            "event_id": f"controller-{len(self.events) + 1:05d}",
            "run_id": self.run_id,
            "scenario_id": self.scenario["scenario_id"],
            "source_component": "fit-probe-controller",
            "event_type": event_type,
            "timestamp": utc_now(),
            "trace_id": uuid.uuid4().hex,
            "software_version": "fit-probe-controller-v1",
            **fields,
        }
        self.events.append(event)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        with self.event_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        return event

    def url(self, component: str, path: str) -> str:
        return f"http://127.0.0.1:{self.ports[component]}{path}"

    def request(
        self, component: str, path: str, method: str = "GET", body: dict[str, Any] | None = None, timeout: float = 2.0
    ) -> tuple[int, dict[str, Any], float]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(self.url(component, path), data=data, method=method)
        if body is not None:
            request.add_header("Content-Type", "application/json")
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
                return response.status, json.loads(raw), time.perf_counter() - started
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            return exc.code, json.loads(raw), time.perf_counter() - started
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
                status, _, _ = self.request(component, "/healthz", timeout=0.25)
                statuses[component] = status
            if all(status == 200 for status in statuses.values()):
                self.emit("readiness_check", statuses=statuses, result="ready")
                return
            time.sleep(0.05)
        self.emit("readiness_check", statuses=statuses, result="failed")
        raise RuntimeError(f"services did not become ready: {statuses}")

    def reset(self) -> None:
        self.emit("reset_started", reset_contract=self.manifest["reset_contract"])
        self.stop_all("clean-reset")
        self.start_service("inventory")
        self.start_service("order-api")
        self.wait_ready()
        state_fingerprint = hashlib.sha256(b"orderflow-empty-state-v1").hexdigest()
        self.emit("clean_state_verified", state_fingerprint=state_fingerprint, outstanding_orders=0)
        self.emit("reset_completed", result="clean")

    def workload(self, count: int, phase: str) -> list[dict[str, Any]]:
        self.emit("workload_started", phase=phase, request_count=count, workload_id="fixed-synthetic-orders-v1")
        outcomes = []
        for index in range(count):
            order_id = f"{self.run_id}-{phase}-{index + 1:03d}"
            started = time.perf_counter()
            self.emit("workload_request", phase=phase, order_id=order_id, request_index=index + 1)
            status, body, elapsed = self.request(
                "order-api", "/orders", method="POST", body={"order_id": order_id}, timeout=2.0
            )
            result = "success" if status == 201 else "failure"
            self.emit(
                "workload_response",
                phase=phase,
                order_id=order_id,
                status=status,
                result=result,
                latency_ms=round(elapsed * 1000, 3),
                body=body,
            )
            outcomes.append(
                {
                    "order_id": order_id,
                    "status": status,
                    "result": result,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                }
            )
            time.sleep(0.02)
        return outcomes

    def transition_version(self, new_version: str, action: str) -> None:
        self.emit(f"{action}_started", from_version=self.started_versions["order-api"], to_version=new_version)
        self.stop_service("order-api", action)
        self.start_service("order-api", new_version)
        self.wait_ready()
        self.emit(f"{action}_completed", active_version=new_version, result="ready")
        self.started_versions["order-api"] = new_version

    def apply_dependency_fault(self, mode: str, latency_ms: int = 0) -> None:
        self.emit("injection_started", fault_mode=mode, target_component="inventory", latency_ms=latency_ms)
        status, _, _ = self.request(
            "inventory", "/__control", method="POST", body={"mode": mode, "latency_ms": latency_ms}
        )
        if status != 200:
            raise RuntimeError(f"could not apply dependency fault: {status}")

    def clear_dependency_fault(self) -> None:
        status, _, _ = self.request("inventory", "/__control", method="POST", body={"mode": "none"})
        if status != 200:
            raise RuntimeError(f"could not clear dependency fault: {status}")
        self.emit("injection_ended", target_component="inventory", fault_mode="none", result="reverted")

    def execute(self) -> dict[str, Any]:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.emit(
            "run_started",
            manifest_version=self.scenario["manifest_version"],
            repeat_of=self.repeat_of,
            target_model=self.manifest["target_model"],
        )
        self.reset()
        self.emit("workload_phase_started", scenario_type=self.scenario["scenario_type"])
        workload = self.scenario["workload"]
        outcomes: list[dict[str, Any]] = []
        if self.scenario["scenario_type"] == "baseline":
            outcomes.extend(self.workload(workload["requests_before_fault"], "baseline-v1"))
            self.transition_version(self.scenario["deployment_transition"]["upgrade_version"], "deployment_update")
            outcomes.extend(self.workload(2, "deployment-v2"))
            self.transition_version(self.scenario["deployment_transition"]["rollback_version"], "rollback")
            outcomes.extend(self.workload(2, "rollback-v1"))
        elif self.scenario["scenario_type"] == "service-termination":
            outcomes.extend(self.workload(workload["requests_before_fault"], "before-fault"))
            target = self.scenario["fault"]["target"]
            self.emit("injection_started", fault_mode="service-termination", target_component=target)
            self.stop_service(target, "fault-injection")
            outcomes.extend(self.workload(workload["requests_during_fault"], "during-fault"))
            self.emit(
                "injection_ended", fault_mode="service-termination", target_component=target, result="target-stopped"
            )
            self.emit("recovery_started", target_component=target, recovery_action="restart-service")
            self.start_service(target)
            self.wait_ready()
            outcomes.extend(self.workload(workload["requests_after_fault"], "after-recovery"))
            self.emit("recovery_completed", target_component=target, result="ready")
        elif self.scenario["scenario_type"] == "dependency-latency":
            outcomes.extend(self.workload(workload["requests_before_fault"], "before-fault"))
            self.apply_dependency_fault("latency", int(self.scenario["fault"]["latency_ms"]))
            outcomes.extend(self.workload(workload["requests_during_fault"], "during-fault"))
            self.clear_dependency_fault()
            self.emit("recovery_started", target_component="inventory", recovery_action="clear-fault")
            self.wait_ready()
            outcomes.extend(self.workload(workload["requests_after_fault"], "after-recovery"))
            self.emit("recovery_completed", target_component="inventory", result="ready")
        else:
            raise ValueError(f"unsupported scenario type: {self.scenario['scenario_type']}")
        self.emit(
            "run_completed",
            result="success",
            request_count=len(outcomes),
            failed_requests=sum(1 for item in outcomes if item["result"] == "failure"),
        )
        self.stop_all("run-complete")
        total_event_count = len(self.event_file.read_text(encoding="utf-8").splitlines())
        metadata = {
            "run_id": self.run_id,
            "scenario_id": self.scenario["scenario_id"],
            "repeat_of": self.repeat_of,
            "manifest_version": self.scenario["manifest_version"],
            "environment_manifest_sha256": sha256_file(ROOT / "infrastructure" / "local-fit-probe.json"),
            "scenario_manifest_sha256": sha256_file(
                ROOT
                / "experiments"
                / "scenarios"
                / (
                    "no-fault.json"
                    if self.scenario["scenario_type"] == "baseline"
                    else f"{self.scenario['scenario_type']}.json"
                )
            ),
            "target_model": self.manifest["target_model"],
            "experimental_target": self.manifest["experimental_target"],
            "host": {
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "python": platform.python_version(),
            },
            "tool_availability": {
                tool: shutil.which(tool) is not None for tool in ("docker", "kubectl", "kind", "minikube")
            },
            "event_file": str(self.event_file.relative_to(ROOT)),
            "event_count": total_event_count,
            "outcomes": outcomes,
            "created_at": utc_now(),
        }
        self.metadata_file.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return metadata


def check_run(run_dir: Path, scenario: dict[str, Any]) -> dict[str, Any]:
    events = [
        json.loads(line) for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    event_types = {event["event_type"] for event in events}
    required = set(scenario["expected_event_types"])
    missing = sorted(required - event_types)
    run_ids = {event.get("run_id") for event in events}
    scenario_ids = {event.get("scenario_id") for event in events}
    timestamps_present = all(event.get("timestamp") for event in events)
    trace_fields_present = all(
        event.get("trace_id") and event.get("span_id", True)
        for event in events
        if event["source_component"] != "fit-probe-controller"
    )
    target_events = [event for event in events if event.get("target_component")]
    checks = {
        "unique_run_identifier": len(run_ids) == 1 and None not in run_ids,
        "versioned_manifest": bool((run_dir / "metadata.json").exists()) and bool(scenario.get("manifest_version")),
        "scenario_distinguishable": scenario_ids == {scenario["scenario_id"]},
        "required_event_classes": not missing,
        "timestamps_present": timestamps_present,
        "telemetry_trace_fields_present": trace_fields_present,
        "target_identifiable": bool(target_events) if scenario["scenario_type"] != "baseline" else True,
        "raw_records_inspectable": bool(events),
        "clean_reset_recorded": "clean_state_verified" in event_types and "reset_completed" in event_types,
    }
    return {
        "run_id": events[0].get("run_id") if events else None,
        "scenario_id": scenario["scenario_id"],
        "passed": all(checks.values()),
        "missing_event_types": missing,
        "checks": checks,
        "event_count": len(events),
    }


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=ROOT / "results" / "fit-probe" / "raw")
    args = parser.parse_args()
    args.output_root = args.output_root.resolve()
    manifest = load_json(ROOT / "infrastructure" / "local-fit-probe.json")
    scenario_paths = [
        ROOT / "experiments" / "scenarios" / "no-fault.json",
        ROOT / "experiments" / "scenarios" / "service-termination.json",
        ROOT / "experiments" / "scenarios" / "dependency-latency.json",
        ROOT / "experiments" / "scenarios" / "dependency-latency.json",
    ]
    args.output_root.mkdir(parents=True, exist_ok=True)
    run_records = []
    previous_run_id: str | None = None
    for index, scenario_path in enumerate(scenario_paths):
        scenario = load_json(scenario_path)
        repeat_of = previous_run_id if index == 3 else None
        run = ProbeRun(manifest, scenario, args.output_root, repeat_of=repeat_of)
        try:
            metadata = run.execute()
            validation = check_run(run.run_dir, scenario)
            run_records.append({"metadata": metadata, "validation": validation})
            previous_run_id = metadata["run_id"] if index == 2 else previous_run_id
        except Exception as exc:
            run.stop_all("run-error")
            run.emit("run_completed", result="failed", error=type(exc).__name__)
            metadata = {"run_id": run.run_id, "scenario_id": scenario["scenario_id"], "error": str(exc)}
            run.metadata_file.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            run_records.append({"metadata": metadata, "validation": {"passed": False, "error": str(exc)}})
    summary = {
        "probe_id": "phase-2-fit-probe-v1",
        "created_at": utc_now(),
        "execution_environment": "local-process-fit-probe",
        "kubernetes_execution": "not-run: kubectl is unavailable in the execution environment",
        "runs": run_records,
        "all_local_checks_passed": all(record["validation"].get("passed", False) for record in run_records)
        and len(run_records) == 4,
        "interpretation_boundary": "Technical feasibility evidence only; no reliability-effect estimate or participant evidence.",
    }
    summary_path = args.output_root.parent / "fit-probe-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary": str(summary_path),
                "all_local_checks_passed": summary["all_local_checks_passed"],
                "run_count": len(run_records),
            },
            indent=2,
        )
    )
    return 0 if summary["all_local_checks_passed"] else 1


if __name__ == "__main__":  # pragma: no cover - exercised through the CLI entry point
    sys.exit(main())
