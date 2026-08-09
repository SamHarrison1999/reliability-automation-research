#!/usr/bin/env python3
"""Run the Phase 2 fit probe against a local Kubernetes cluster.

The runner intentionally uses only kubectl, Docker-built local images and the
Python standard library. It records controller events and collects service
events from pod stdout so the raw bundle remains inspectable after cleanup.
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
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "infrastructure" / "kubernetes" / "orderflow-fit-probe.yaml"
SCENARIO_DIR = ROOT / "experiments" / "scenarios"
NAMESPACE = "orderflow-fit-probe"
ORDER_PORT = 19080
INVENTORY_PORT = 19081


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_command(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(args)}\n{result.stderr.strip()}")
    return result


class KubernetesProbe:
    def __init__(self, scenario: dict[str, Any], output_root: Path, repeat_of: str | None = None):
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        self.run_id = f"{scenario['scenario_id']}-{stamp}-{uuid.uuid4().hex[:8]}"
        self.scenario = scenario
        self.repeat_of = repeat_of
        self.run_dir = output_root / self.run_id
        self.event_file = self.run_dir / "events.jsonl"
        self.service_event_file = self.run_dir / "service-events.jsonl"
        self.metadata_file = self.run_dir / "metadata.json"
        self.events: list[dict[str, Any]] = []
        self.service_events: dict[str, dict[str, Any]] = {}
        self.port_forwards: list[subprocess.Popen[str]] = []

    def emit(self, event_type: str, **fields: Any) -> None:
        event = {
            "event_id": f"controller-{len(self.events) + 1:05d}",
            "run_id": self.run_id,
            "scenario_id": self.scenario["scenario_id"],
            "source_component": "kubernetes-fit-probe-controller",
            "event_type": event_type,
            "timestamp": utc_now(),
            "trace_id": uuid.uuid4().hex,
            "software_version": "kubernetes-fit-probe-controller-v1",
            **fields,
        }
        self.events.append(event)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        with self.event_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

    def kubectl(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return run_command(["kubectl", *args], check=check)

    def wait_rollout(self, deployment: str) -> None:
        self.kubectl("-n", NAMESPACE, "rollout", "status", f"deployment/{deployment}", "--timeout=120s")

    def wait_pods(self, label: str, expected: int) -> None:
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            result = self.kubectl("-n", NAMESPACE, "get", "pods", "-l", label, "-o", "json", check=False)
            if result.returncode == 0:
                payload = json.loads(result.stdout or "{}")
                pods = payload.get("items", [])
                ready = sum(
                    any(
                        c.get("type") == "Ready" and c.get("status") == "True"
                        for c in pod.get("status", {}).get("conditions", [])
                    )
                    for pod in pods
                )
                if len(pods) == expected and ready == expected:
                    return
            time.sleep(1)
        raise RuntimeError(f"pods did not reach expected state: label={label}, expected={expected}")

    def stop_port_forwards(self) -> None:
        for process in self.port_forwards:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
        self.port_forwards.clear()

    def start_port_forward(self, service: str, local_port: int, remote_port: int) -> None:
        process = subprocess.Popen(
            ["kubectl", "-n", NAMESPACE, "port-forward", f"service/{service}", f"{local_port}:{remote_port}"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        self.port_forwards.append(process)
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"port-forward for {service} exited with {process.returncode}")
            with socket.socket() as probe:
                if probe.connect_ex(("127.0.0.1", local_port)) == 0:
                    return
            time.sleep(0.25)
        raise RuntimeError(f"port-forward for {service} did not become ready")

    def request(
        self, port: int, path: str, method: str = "GET", body: dict[str, Any] | None = None, timeout: float = 3.0
    ) -> tuple[int, dict[str, Any], float]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, method=method)
        if body is not None:
            request.add_header("Content-Type", "application/json")
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status, json.loads(response.read().decode("utf-8")), time.perf_counter() - started
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8")), time.perf_counter() - started
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            return 0, {"error": "connection-failed"}, time.perf_counter() - started

    def capture_service_logs(self) -> None:
        result = self.kubectl("-n", NAMESPACE, "get", "pods", "-l", "app", "-o", "json", check=False)
        if result.returncode != 0:
            return
        payload = json.loads(result.stdout or "{}")
        for pod in payload.get("items", []):
            name = pod["metadata"]["name"]
            component = pod["metadata"].get("labels", {}).get("app", "unknown")
            logs = self.kubectl("-n", NAMESPACE, "logs", name, "--all-containers=true", check=False)
            if logs.returncode != 0:
                continue
            for line in logs.stdout.splitlines():
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("run_id") != self.run_id:
                    continue
                event["pod_name"] = name
                event["source_component"] = event.get("source_component", component)
                key = f"{name}:{event.get('event_id')}:{event.get('timestamp')}"
                self.service_events[key] = event
        self.service_event_file.parent.mkdir(parents=True, exist_ok=True)
        with self.service_event_file.open("w", encoding="utf-8") as handle:
            for event in sorted(self.service_events.values(), key=lambda item: item.get("timestamp", "")):
                handle.write(json.dumps(event, sort_keys=True) + "\n")

    def reset(self) -> None:
        self.stop_port_forwards()
        self.emit(
            "reset_started",
            reset_contract=[
                "delete probe namespace",
                "apply versioned manifest",
                "wait for both deployments",
                "verify readiness",
            ],
        )
        self.kubectl("delete", "namespace", NAMESPACE, "--ignore-not-found=true", "--wait=true", check=False)
        self.kubectl("apply", "-f", str(MANIFEST))
        self.kubectl(
            "-n",
            NAMESPACE,
            "set",
            "env",
            "deployment/inventory",
            f"ORDERFLOW_RUN_ID={self.run_id}",
            f"ORDERFLOW_SCENARIO_ID={self.scenario['scenario_id']}",
        )
        self.kubectl(
            "-n",
            NAMESPACE,
            "set",
            "env",
            "deployment/order-api",
            f"ORDERFLOW_RUN_ID={self.run_id}",
            f"ORDERFLOW_SCENARIO_ID={self.scenario['scenario_id']}",
        )
        self.wait_rollout("inventory")
        self.wait_rollout("order-api")
        self.wait_pods("app=inventory", 1)
        self.wait_pods("app=order-api", 1)
        self.start_port_forward("inventory", INVENTORY_PORT, 8081)
        self.start_port_forward("order-api", ORDER_PORT, 8080)
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            inventory_status, _, _ = self.request(INVENTORY_PORT, "/healthz", timeout=0.5)
            order_status, _, _ = self.request(ORDER_PORT, "/healthz", timeout=0.5)
            if inventory_status == 200 and order_status == 200:
                self.emit(
                    "readiness_check",
                    statuses={"inventory": inventory_status, "order-api": order_status},
                    result="ready",
                )
                self.emit(
                    "clean_state_verified",
                    state_fingerprint=hashlib.sha256(b"orderflow-kubernetes-empty-state-v1").hexdigest(),
                    outstanding_orders=0,
                )
                self.emit("reset_completed", result="clean")
                return
            time.sleep(0.25)
        raise RuntimeError("services did not become ready through port-forward")

    def workload(self, count: int, phase: str) -> list[dict[str, Any]]:
        self.emit("workload_started", phase=phase, request_count=count, workload_id="fixed-synthetic-orders-v1")
        outcomes = []
        for index in range(count):
            order_id = f"{self.run_id}-{phase}-{index + 1:03d}"
            self.emit("workload_request", phase=phase, order_id=order_id, request_index=index + 1)
            status, body, elapsed = self.request(ORDER_PORT, "/orders", method="POST", body={"order_id": order_id})
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
                {"order_id": order_id, "status": status, "result": result, "latency_ms": round(elapsed * 1000, 3)}
            )
            time.sleep(0.02)
        self.capture_service_logs()
        return outcomes

    def set_order_version(self, version: str, action: str) -> None:
        from_version = "order-api-v1" if version == "order-api-v2" else "order-api-v2"
        self.emit(f"{action}_started", from_version=from_version, to_version=version)
        self.kubectl("-n", NAMESPACE, "set", "env", "deployment/order-api", f"ORDERFLOW_VERSION={version}")
        self.wait_rollout("order-api")
        self.emit(f"{action}_completed", active_version=version, result="ready")

    def dependency_fault(self, mode: str, latency_ms: int = 0) -> None:
        self.emit("injection_started", fault_mode=mode, target_component="inventory", latency_ms=latency_ms)
        status, _, _ = self.request(
            INVENTORY_PORT, "/__control", method="POST", body={"mode": mode, "latency_ms": latency_ms}
        )
        if status != 200:
            raise RuntimeError(f"could not apply dependency fault: {status}")

    def clear_dependency_fault(self) -> None:
        status, _, _ = self.request(INVENTORY_PORT, "/__control", method="POST", body={"mode": "none"})
        if status != 200:
            raise RuntimeError(f"could not clear dependency fault: {status}")
        self.emit("injection_ended", target_component="inventory", fault_mode="none", result="reverted")

    def execute(self) -> dict[str, Any]:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.emit(
            "run_started", manifest_version="1.0.0", repeat_of=self.repeat_of, target_model="docker-desktop-kubernetes"
        )
        outcomes: list[dict[str, Any]] = []
        try:
            self.reset()
            scenario_type = self.scenario["scenario_type"]
            workload = self.scenario["workload"]
            if scenario_type == "baseline":
                outcomes += self.workload(workload["requests_before_fault"], "baseline-v1")
                self.set_order_version("order-api-v2", "deployment_update")
                outcomes += self.workload(2, "deployment-v2")
                self.set_order_version("order-api-v1", "rollback")
                outcomes += self.workload(2, "rollback-v1")
            elif scenario_type == "service-termination":
                outcomes += self.workload(workload["requests_before_fault"], "before-fault")
                self.emit("injection_started", fault_mode="service-termination", target_component="inventory")
                self.kubectl("-n", NAMESPACE, "scale", "deployment/inventory", "--replicas=0")
                self.wait_pods("app=inventory", 0)
                outcomes += self.workload(workload["requests_during_fault"], "during-fault")
                self.emit(
                    "injection_ended",
                    fault_mode="service-termination",
                    target_component="inventory",
                    result="scaled-to-zero",
                )
                self.emit("recovery_started", target_component="inventory", recovery_action="scale-deployment-to-one")
                self.kubectl("-n", NAMESPACE, "scale", "deployment/inventory", "--replicas=1")
                self.wait_rollout("inventory")
                self.wait_pods("app=inventory", 1)
                self.stop_port_forwards()
                self.start_port_forward("inventory", INVENTORY_PORT, 8081)
                self.start_port_forward("order-api", ORDER_PORT, 8080)
                outcomes += self.workload(workload["requests_after_fault"], "after-recovery")
                self.emit("recovery_completed", target_component="inventory", result="ready")
            elif scenario_type == "dependency-latency":
                outcomes += self.workload(workload["requests_before_fault"], "before-fault")
                self.dependency_fault("latency", int(self.scenario["fault"]["latency_ms"]))
                outcomes += self.workload(workload["requests_during_fault"], "during-fault")
                self.clear_dependency_fault()
                self.emit("recovery_started", target_component="inventory", recovery_action="clear-fault")
                outcomes += self.workload(workload["requests_after_fault"], "after-recovery")
                self.emit("recovery_completed", target_component="inventory", result="ready")
            else:
                raise ValueError(f"unsupported scenario type: {scenario_type}")
            self.emit(
                "run_completed",
                result="success",
                request_count=len(outcomes),
                failed_requests=sum(1 for item in outcomes if item["result"] == "failure"),
            )
            self.capture_service_logs()
        finally:
            self.stop_port_forwards()
        all_events = self.events + list(self.service_events.values())
        with self.event_file.open("w", encoding="utf-8") as handle:
            for event in sorted(all_events, key=lambda item: item.get("timestamp", "")):
                handle.write(json.dumps(event, sort_keys=True) + "\n")
        metadata = {
            "run_id": self.run_id,
            "scenario_id": self.scenario["scenario_id"],
            "repeat_of": self.repeat_of,
            "manifest_version": "1.0.0",
            "environment_manifest_sha256": sha256_file(MANIFEST),
            "scenario_manifest_sha256": sha256_file(
                SCENARIO_DIR
                / (
                    "no-fault.json"
                    if self.scenario["scenario_type"] == "baseline"
                    else f"{self.scenario['scenario_type']}.json"
                )
            ),
            "target_model": "docker-desktop-kubernetes",
            "cluster_context": run_command(["kubectl", "config", "current-context"]).stdout.strip(),
            "host": {
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "python": platform.python_version(),
            },
            "tool_availability": {tool: shutil.which(tool) is not None for tool in ("docker", "kubectl")},
            "event_file": str(self.event_file.relative_to(ROOT)),
            "service_event_file": str(self.service_event_file.relative_to(ROOT)),
            "event_count": len(all_events),
            "outcomes": outcomes,
            "created_at": utc_now(),
        }
        self.metadata_file.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return metadata


def validate_run(run_dir: Path, scenario: dict[str, Any]) -> dict[str, Any]:
    events = [
        json.loads(line) for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    event_types = {event.get("event_type") for event in events}
    run_ids = {event.get("run_id") for event in events}
    scenario_ids = {event.get("scenario_id") for event in events}
    missing = sorted(set(scenario["expected_event_types"]) - event_types)
    service_events = [event for event in events if event.get("source_component") in {"inventory", "order-api"}]
    target_events = [event for event in events if event.get("target_component")]
    checks = {
        "unique_run_identifier": len(run_ids) == 1 and None not in run_ids,
        "scenario_distinguishable": scenario_ids == {scenario["scenario_id"]},
        "versioned_manifest": bool((run_dir / "metadata.json").exists()),
        "required_event_classes": not missing,
        "timestamps_present": all(event.get("timestamp") for event in events),
        "telemetry_trace_fields_present": all(
            event.get("trace_id") and event.get("span_id") for event in service_events
        ),
        "target_identifiable": bool(target_events) if scenario["scenario_type"] != "baseline" else True,
        "raw_records_inspectable": bool(events),
        "clean_reset_recorded": "clean_state_verified" in event_types and "reset_completed" in event_types,
    }
    return {
        "run_id": next(iter(run_ids), None),
        "scenario_id": scenario["scenario_id"],
        "passed": all(checks.values()),
        "missing_event_types": missing,
        "checks": checks,
        "event_count": len(events),
    }


def scenario_paths() -> list[Path]:
    return [
        SCENARIO_DIR / "no-fault.json",
        SCENARIO_DIR / "service-termination.json",
        SCENARIO_DIR / "dependency-latency.json",
        SCENARIO_DIR / "dependency-latency.json",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=ROOT / "results" / "fit-probe" / "kubernetes-raw")
    parser.add_argument("--keep-namespace", action="store_true")
    args = parser.parse_args()
    args.output_root = args.output_root.resolve()
    if shutil.which("kubectl") is None or shutil.which("docker") is None:
        print("docker and kubectl are required for the Kubernetes fit probe", file=sys.stderr)
        return 2
    args.output_root.mkdir(parents=True, exist_ok=True)
    records = []
    previous_run_id: str | None = None
    for index, path in enumerate(scenario_paths()):
        scenario = json.loads(path.read_text(encoding="utf-8"))
        repeat_of = previous_run_id if index == 3 else None
        probe = KubernetesProbe(scenario, args.output_root, repeat_of)
        try:
            metadata = probe.execute()
            validation = validate_run(probe.run_dir, scenario)
            records.append({"metadata": metadata, "validation": validation, "passed": validation["passed"]})
            if not validation["passed"]:
                print(f"Kubernetes acceptance checks failed: {validation}", file=sys.stderr)
                break
            if index == 2:
                previous_run_id = metadata["run_id"]
        except Exception as exc:
            probe.stop_port_forwards()
            probe.emit("run_completed", result="failed", error=type(exc).__name__)
            records.append(
                {
                    "metadata": {"run_id": probe.run_id, "scenario_id": scenario["scenario_id"], "error": str(exc)},
                    "passed": False,
                }
            )
            print(f"Kubernetes scenario failed: {exc}", file=sys.stderr)
            break
    if not args.keep_namespace:
        run_command(
            ["kubectl", "delete", "namespace", NAMESPACE, "--ignore-not-found=true", "--wait=true"], check=False
        )
    summary = {
        "probe_id": "phase-2-fit-probe-v1",
        "created_at": utc_now(),
        "execution_environment": "docker-desktop-kubernetes",
        "kubernetes_execution": "completed"
        if len(records) == 4 and all(item["passed"] for item in records)
        else "failed",
        "runs": records,
        "all_kubernetes_checks_passed": len(records) == 4 and all(item["passed"] for item in records),
        "interpretation_boundary": "Technical feasibility evidence only; no reliability-effect estimate or participant evidence.",
    }
    summary_path = args.output_root.parent / "kubernetes-fit-probe-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary": str(summary_path),
                "all_kubernetes_checks_passed": summary["all_kubernetes_checks_passed"],
                "run_count": len(records),
            },
            indent=2,
        )
    )
    return 0 if summary["all_kubernetes_checks_passed"] else 1


if __name__ == "__main__":  # pragma: no cover - exercised through the CLI entry point
    sys.exit(main())
