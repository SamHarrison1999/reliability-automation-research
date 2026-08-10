#!/usr/bin/env python3
"""Execute one guarded Phase 5 Kubernetes development-validation trial.

This controller is intentionally incapable of consuming the frozen 50-slot
primary pilot schedule.  It validates one explicitly selected scenario and
condition while the Phase 5 experiment machinery is still being implemented.
Its output is implementation-feasibility evidence, not pilot evidence.
"""

from __future__ import annotations

import argparse
import base64
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
PILOT_MANIFEST = ROOT / "experiments" / "manifests" / "phase-5-pilot-manifest.json"
PROTOCOL = ROOT / "docs" / "protocols" / "phase-5-technical-pilot.md"
PROTOTYPE_MANIFEST = ROOT / "infrastructure" / "prototype" / "orderflow-phase-5.json"
PARENT_PROTOTYPE_MANIFEST = ROOT / "infrastructure" / "prototype" / "orderflow-phase-4.json"
KUBERNETES_MANIFEST = ROOT / "infrastructure" / "kubernetes" / "orderflow-phase-5.yaml"

NAMESPACE = "orderflow-phase5"
KUBERNETES_NODE = "desktop-control-plane"
ORDER_PORT = 19580
INVENTORY_PORT = 19581
TELEMETRY_SINK_PORT = 19582
CONTROLLER_VERSION = "phase-5-single-trial-controller-v0.2"
EVIDENCE_BOUNDARY = "phase-5-implementation-feasibility-only"
DEVELOPMENT_REPETITION = 0
DEVELOPMENT_RUN_ORDER = 0
ALLOWED_SCENARIOS = {
    "no-fault-v1",
    "service-termination-v1",
    "dependency-latency-v1",
}
FAULT_SCENARIOS = {
    "service-termination-v1",
    "dependency-latency-v1",
}


def utc_now() -> str:
    """Return a millisecond precision UTC timestamp."""

    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object."""

    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def canonical_json_bytes(value: object) -> bytes:
    """Return canonical compact JSON bytes for action identity."""

    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(value: object) -> str:
    """Hash canonical JSON."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash one file without normalising bytes."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_command(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run one repository-scoped command."""

    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(args)}\n{detail}")
    return result


def command_version(args: list[str]) -> str:
    """Return stdout/stderr from a version command."""

    result = run_command(args, check=False)
    return (result.stdout.strip() or result.stderr.strip()).strip()


def stream_docker_image_to_containerd(image: str) -> str:
    """Stream one Docker image into the Docker Desktop Kubernetes node runtime."""

    save = subprocess.Popen(
        ["docker", "save", image],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if save.stdout is None:
        raise RuntimeError(f"could not open docker save stream for {image}")

    importer = subprocess.Popen(
        [
            "docker",
            "exec",
            "-i",
            KUBERNETES_NODE,
            "ctr",
            "-n",
            "k8s.io",
            "images",
            "import",
            "-",
        ],
        cwd=ROOT,
        stdin=save.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
    )
    save.stdout.close()
    import_stdout, import_stderr = importer.communicate()
    save_stderr = save.stderr.read() if save.stderr is not None else b""
    save_returncode = save.wait()

    if save_returncode != 0:
        detail = save_stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"docker save failed for {image}: {detail}")
    if importer.returncode != 0:
        detail = import_stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"containerd image import failed for {image}: {detail}")

    return import_stdout.decode("utf-8", errors="replace").strip()


def validate_development_selection(scenario_id: str, condition: str, development_validation: bool) -> None:
    """Guard the controller from accidental primary-pilot use."""

    if not development_validation:
        raise ValueError("--development-validation is required; primary pilot execution is not enabled")
    if scenario_id not in ALLOWED_SCENARIOS:
        raise ValueError(f"unsupported Phase 5 scenario: {scenario_id}")
    if scenario_id == "no-fault-v1":
        if condition != "control":
            raise ValueError("no-fault-v1 requires condition=control")
    elif condition not in {"manual", "automated"}:
        raise ValueError("fault scenarios require condition=manual or condition=automated")


def canonical_recovery_action(manifest: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    """Return the single scenario-level recovery action shared by both conditions."""

    scenario = manifest["scenarios"][scenario_id]
    action = scenario.get("recovery_action")
    if not isinstance(action, dict):
        raise ValueError(f"scenario has no recovery action: {scenario_id}")
    return cast(dict[str, Any], action)


class Phase5DevelopmentTrial:
    """Run one immutable, guarded Phase 5 implementation-validation trial."""

    def __init__(
        self,
        scenario_id: str,
        condition: str,
        output_root: Path,
        development_validation: bool,
    ) -> None:
        validate_development_selection(scenario_id, condition, development_validation)
        self.design = load_json(PILOT_MANIFEST)
        self.prototype = load_json(PROTOTYPE_MANIFEST)
        self.scenario_id = scenario_id
        self.condition = condition
        self.scenario = cast(dict[str, Any], self.design["scenarios"][scenario_id])
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        self.trial_id = f"phase5-dev-{scenario_id}-{condition}-{stamp}-{uuid.uuid4().hex[:8]}"
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

        self.events: list[dict[str, Any]] = []
        self.service_events: list[dict[str, Any]] = []
        self.workload_records: list[dict[str, Any]] = []
        self.port_forwards: dict[str, subprocess.Popen[str]] = {}
        self.image_records: dict[str, dict[str, str]] = {}
        self.node_image_records: dict[str, dict[str, str]] = {}
        self.external_image_records: dict[str, dict[str, str]] = {}
        self.otel_spans: list[dict[str, Any]] = []
        self.recovery_action_hash: str | None = None
        self.execution_error: str | None = None

    def emit(self, event_type: str, **fields: Any) -> dict[str, Any]:
        """Write one controller event with complete development-trial identity."""

        event = {
            "event_id": f"phase5-controller-{self.trial_id}-{len(self.events) + 1:05d}",
            "trial_id": self.trial_id,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "automation_condition": self.condition,
            "repetition": DEVELOPMENT_REPETITION,
            "run_order": DEVELOPMENT_RUN_ORDER,
            "source_component": "phase5-single-trial-controller",
            "event_type": event_type,
            "timestamp": utc_now(),
            "monotonic_ns": time.monotonic_ns(),
            "software_version": CONTROLLER_VERSION,
            **fields,
        }
        self.events.append(event)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        with self.event_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        return event

    def kubectl(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        """Run kubectl."""

        return run_command(["kubectl", *args], check=check)

    def request(
        self,
        port: int,
        path: str,
        method: str = "GET",
        body: dict[str, Any] | None = None,
        timeout: float = 3.0,
    ) -> tuple[int, dict[str, Any], float]:
        """Perform one local port-forwarded HTTP request."""

        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, method=method)
        if body is not None:
            request.add_header("Content-Type", "application/json")
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return response.status, cast(dict[str, Any], payload), time.perf_counter() - started
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))
            return exc.code, cast(dict[str, Any], payload), time.perf_counter() - started
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            return 0, {"error": "connection-failed"}, time.perf_counter() - started

    def ensure_prerequisites(self) -> None:
        """Verify the declared local Kubernetes execution boundary."""

        missing = [tool for tool in ("docker", "kubectl", "git") if shutil.which(tool) is None]
        if missing:
            raise RuntimeError(f"missing required tools: {', '.join(missing)}")
        context = self.kubectl("config", "current-context").stdout.strip()
        if context != self.prototype["kubernetes"]["context"]:
            raise RuntimeError(
                f"unexpected Kubernetes context: {context!r}; expected {self.prototype['kubernetes']['context']!r}"
            )
        self.emit("preflight_completed", kubernetes_context=context)

    def verify_source_tree_clean(self) -> None:
        """Refuse execution from tracked/staged dirty source."""

        unstaged = run_command(["git", "diff", "--quiet"], check=False)
        staged = run_command(["git", "diff", "--cached", "--quiet"], check=False)
        if unstaged.returncode not in {0, 1} or staged.returncode not in {0, 1}:
            raise RuntimeError("could not verify repository source state")
        if unstaged.returncode == 1 or staged.returncode == 1:
            raise RuntimeError("tracked or staged repository changes are present; refusing trial")
        repo_sha = run_command(["git", "rev-parse", "HEAD"]).stdout.strip()
        self.emit("source_tree_verified", repository_commit_sha=repo_sha, tracked_changes=False)

    def materialise_trial_manifest(self) -> None:
        """Write the immutable development-trial manifest before deployment."""

        recovery = self.scenario.get("recovery_action")
        recovery_hash = sha256_json(recovery) if recovery is not None else None
        self.recovery_action_hash = recovery_hash
        payload = {
            "manifest_type": "phase-5-development-trial-manifest",
            "protocol_id": self.design["protocol_id"],
            "manifest_version": self.design["manifest_version"],
            "evidence_boundary": EVIDENCE_BOUNDARY,
            "trial_id": self.trial_id,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "automation_condition": self.condition,
            "repetition": DEVELOPMENT_REPETITION,
            "run_order": DEVELOPMENT_RUN_ORDER,
            "primary_schedule_slot": None,
            "reserve": False,
            "pilot_batch_id": None,
            "repository_commit_sha": run_command(["git", "rev-parse", "HEAD"]).stdout.strip(),
            "pilot_manifest_sha256": sha256_file(PILOT_MANIFEST),
            "protocol_sha256": sha256_file(PROTOCOL),
            "prototype_manifest_sha256": sha256_file(PROTOTYPE_MANIFEST),
            "parent_prototype_manifest_sha256": sha256_file(PARENT_PROTOTYPE_MANIFEST),
            "kubernetes_manifest_sha256": sha256_file(KUBERNETES_MANIFEST),
            "scenario": self.scenario,
            "canonical_recovery_action_sha256": recovery_hash,
            "controller_version": CONTROLLER_VERSION,
            "started_at": utc_now(),
        }
        if self.trial_manifest_file.exists():
            raise RuntimeError("trial manifest already exists")
        self.trial_manifest_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.emit(
            "trial_manifest_written",
            pilot_batch_id=None,
            primary_schedule_slot=None,
            canonical_recovery_action_sha256=recovery_hash,
        )

    def clean_before_deploy(self) -> None:
        """Delete any previous Phase 5 namespace and independently verify absence."""

        self.emit("reset_started", stage="before_deploy")
        self.kubectl(
            "delete",
            "namespace",
            NAMESPACE,
            "--ignore-not-found=true",
            "--wait=true",
            "--timeout=60s",
            check=False,
        )
        check = self.kubectl("get", "namespace", NAMESPACE, "-o", "name", check=False)
        if check.returncode == 0:
            raise RuntimeError("Phase 5 namespace still exists after pre-deploy reset")
        self.emit("clean_state_verified", stage="before_deploy", namespace_present=False)
        self.emit("reset_completed", stage="before_deploy")

    def build_images(self) -> None:
        """Build the three repository-controlled Phase 5 image tags."""

        packaging = self.prototype["packaging"]
        dockerfile = str(ROOT / packaging["dockerfile"])
        for service in ("inventory", "order-api", "telemetry-sink"):
            tag = packaging["images"][service]
            self.emit("image_build_started", service=service, image=tag)
            run_command(
                [
                    "docker",
                    "build",
                    "--pull=false",
                    "--platform",
                    packaging["build_platform"],
                    "--provenance=false",
                    "-t",
                    tag,
                    "-f",
                    dockerfile,
                    ".",
                ]
            )
            image_id = run_command(["docker", "image", "inspect", tag, "--format", "{{.Id}}"]).stdout.strip()
            self.image_records[service] = {"tag": tag, "image_id": image_id}
            self.emit("image_build_completed", service=service, image=tag, image_id=image_id)

    def verify_external_image(self) -> None:
        """Verify the exact local OpenTelemetry Collector image identity."""

        collector = self.prototype["observability"]["collector"]
        tag = collector["image"]
        expected = collector["digest"]
        result = run_command(["docker", "image", "inspect", tag, "--format", "{{.Id}}"], check=False)
        if result.returncode != 0:
            raise RuntimeError(f"required pinned Collector image is not local: {tag}")
        observed = result.stdout.strip()
        if observed != expected:
            raise RuntimeError(f"Collector image digest mismatch: expected={expected}, observed={observed}")
        self.external_image_records["otel-collector"] = {"tag": tag, "image_id": observed}
        self.emit("external_image_verified", image=tag, image_id=observed)

    def import_images_into_kubernetes_node(self) -> None:
        """Make repository/Collector images explicitly visible to the node runtime."""

        node_check = run_command(
            [
                "docker",
                "inspect",
                "--type",
                "container",
                KUBERNETES_NODE,
                "--format",
                "{{.State.Running}}",
            ],
            check=False,
        )
        if node_check.returncode != 0 or node_check.stdout.strip().lower() != "true":
            raise RuntimeError(f"Kubernetes node container is not running: {KUBERNETES_NODE}")

        targets = [
            (service, self.image_records[service]["tag"], self.image_records[service]["image_id"])
            for service in ("inventory", "order-api", "telemetry-sink")
        ]
        collector = self.external_image_records["otel-collector"]
        targets.append(("otel-collector", collector["tag"], collector["image_id"]))

        for role, tag, docker_image_id in targets:
            expected_ref = f"docker.io/{tag}"
            self.emit("image_import_started", service=role, image=tag)
            output = stream_docker_image_to_containerd(tag)
            lines = run_command(
                [
                    "docker",
                    "exec",
                    KUBERNETES_NODE,
                    "ctr",
                    "-n",
                    "k8s.io",
                    "images",
                    "ls",
                ]
            ).stdout.splitlines()
            matching = [line for line in lines if line.startswith(expected_ref)]
            if not matching:
                raise RuntimeError(f"node image is missing after import: {expected_ref}")
            digest = next((field for field in matching[0].split() if field.startswith("sha256:")), "")
            if digest != docker_image_id:
                raise RuntimeError(f"node image mismatch for {role}: docker={docker_image_id}, node={digest}")
            self.node_image_records[role] = {
                "reference": expected_ref,
                "digest": digest,
                "transfer_mode": "docker-save-stream",
            }
            self.emit(
                "node_image_verified",
                service=role,
                image_reference=expected_ref,
                image_digest=digest,
                import_output_present=bool(output),
            )
        self.emit("image_import_completed", imported_services=sorted(self.node_image_records))

    def deploy(self) -> None:
        """Deploy the Phase 5 manifest and bind the selected trial identity."""

        self.emit("deployment_started", namespace=NAMESPACE)
        self.kubectl("apply", "-f", str(KUBERNETES_MANIFEST))
        for deployment in ("inventory", "order-api"):
            self.kubectl(
                "-n",
                NAMESPACE,
                "set",
                "env",
                f"deployment/{deployment}",
                f"ORDERFLOW_RUN_ID={self.run_id}",
                f"ORDERFLOW_SCENARIO_ID={self.scenario_id}",
                f"ORDERFLOW_TRIAL_ID={self.trial_id}",
                f"ORDERFLOW_AUTOMATION_CONDITION={self.condition}",
                f"ORDERFLOW_REPETITION={DEVELOPMENT_REPETITION}",
                f"ORDERFLOW_RUN_ORDER={DEVELOPMENT_RUN_ORDER}",
            )
        for deployment in ("telemetry-sink", "otel-collector", "inventory", "order-api"):
            self.kubectl(
                "-n",
                NAMESPACE,
                "rollout",
                "status",
                f"deployment/{deployment}",
                "--timeout=120s",
            )
        self.emit("deployment_completed", namespace=NAMESPACE)

    def start_port_forward(self, service: str, local_port: int, remote_port: int) -> None:
        """Start a named port-forward, replacing any stale one."""

        self.stop_port_forward(service)
        process = subprocess.Popen(
            [
                "kubectl",
                "-n",
                NAMESPACE,
                "port-forward",
                f"service/{service}",
                f"{local_port}:{remote_port}",
            ],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        self.port_forwards[service] = process
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"port-forward for {service} exited with {process.returncode}")
            with socket.socket() as probe:
                if probe.connect_ex(("127.0.0.1", local_port)) == 0:
                    return
            time.sleep(0.25)
        raise RuntimeError(f"port-forward for {service} did not become ready")

    def stop_port_forward(self, service: str) -> None:
        """Stop one named port-forward if present."""

        process = self.port_forwards.pop(service, None)
        if process is None or process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)

    def stop_all_port_forwards(self) -> None:
        """Stop all active port-forwards."""

        for service in list(self.port_forwards):
            self.stop_port_forward(service)

    def wait_and_forward(self) -> None:
        """Verify all baseline pods and open the three local observation paths."""

        deadline = time.monotonic() + 120
        expected = {"telemetry-sink", "otel-collector", "inventory", "order-api"}
        while time.monotonic() < deadline:
            result = self.kubectl("-n", NAMESPACE, "get", "pods", "-o", "json", check=False)
            if result.returncode == 0:
                ready = {
                    item.get("metadata", {}).get("labels", {}).get("app")
                    for item in json.loads(result.stdout or "{}").get("items", [])
                    if any(
                        condition.get("type") == "Ready" and condition.get("status") == "True"
                        for condition in item.get("status", {}).get("conditions", [])
                    )
                }
                if ready == expected:
                    break
            time.sleep(1)
        else:
            raise RuntimeError("Phase 5 baseline pods did not all become Ready")

        self.start_port_forward("inventory", INVENTORY_PORT, 8081)
        self.start_port_forward("order-api", ORDER_PORT, 8080)
        self.start_port_forward("telemetry-sink", TELEMETRY_SINK_PORT, 4319)

        statuses = {
            "inventory": self.request(INVENTORY_PORT, "/healthz")[0],
            "order-api": self.request(ORDER_PORT, "/healthz")[0],
            "telemetry-sink": self.request(TELEMETRY_SINK_PORT, "/healthz")[0],
        }
        if set(statuses.values()) != {200}:
            raise RuntimeError(f"readiness endpoint failure: {statuses}")
        self.emit("readiness_verified", statuses=statuses)

    def verify_versions_and_clean_fault_state(self) -> None:
        """Verify service versions and force/verify inventory mode=none."""

        expected = {
            "inventory": self.prototype["topology"]["services"]["inventory"]["version"],
            "order-api": self.prototype["topology"]["services"]["order-api"]["version"],
        }
        observed: dict[str, str] = {}
        for service, port in (("inventory", INVENTORY_PORT), ("order-api", ORDER_PORT)):
            status, body, _ = self.request(port, "/version")
            observed[service] = str(body.get("version", ""))
            if status != 200 or observed[service] != expected[service]:
                raise RuntimeError(f"version check failed for {service}: {observed[service]}")
        status, body, _ = self.request(INVENTORY_PORT, "/__control", method="POST", body={"mode": "none"})
        if status != 200 or body.get("mode") != "none":
            raise RuntimeError(f"inventory clean fault state could not be verified: {body}")
        self.emit("version_verified", expected=expected, observed=observed)
        self.emit("fault_state_verified", mode="none", stage="before_workload")

    def workload_request(self, phase: str, request_index: int) -> dict[str, Any]:
        """Execute and record one offered order request."""

        order_id = f"{self.trial_id}-order-{request_index:03d}"
        request_event = self.emit(
            "workload_request",
            phase=phase,
            request_index=request_index,
            order_id=order_id,
        )
        status, body, elapsed = self.request(
            ORDER_PORT,
            "/orders",
            method="POST",
            body={"order_id": order_id},
            timeout=3.0,
        )
        record = {
            "request_index": request_index,
            "phase": phase,
            "order_id": order_id,
            "status": status,
            "result": "success" if status == 201 else "failure",
            "latency_ms": round(elapsed * 1000, 3),
            "response": body,
            "request_event_id": request_event["event_id"],
        }
        response_event = self.emit("workload_response", **record)
        record["response_event_id"] = response_event["event_id"]
        self.workload_records.append(record)
        return record

    def apply_fault(self) -> None:
        """Apply and positively verify the selected deterministic fault."""

        if self.scenario_id == "dependency-latency-v1":
            action = self.scenario["fault"]["apply_action"]
            status, body, _ = self.request(
                INVENTORY_PORT,
                action["path"],
                method=action["method"],
                body=action["payload"],
            )
            if status != 200 or body.get("mode") != "latency" or int(body.get("latency_ms", -1)) != 120:
                raise RuntimeError(f"latency fault verification failed: status={status}, body={body}")
            self.emit(
                "fault_application_verified",
                fault_id=self.scenario["fault"]["fault_id"],
                target="inventory",
                mode="latency",
                latency_ms=120,
            )
        elif self.scenario_id == "service-termination-v1":
            self.capture_service_logs(stage="before_service_termination")
            self.stop_port_forward("inventory")
            self.kubectl("-n", NAMESPACE, "scale", "deployment/inventory", "--replicas=0")
            deadline = time.monotonic() + 60
            verified = False
            while time.monotonic() < deadline:
                deployment = self.kubectl("-n", NAMESPACE, "get", "deployment/inventory", "-o", "json", check=False)
                pods = self.kubectl(
                    "-n",
                    NAMESPACE,
                    "get",
                    "pods",
                    "-l",
                    "app=inventory",
                    "-o",
                    "json",
                    check=False,
                )
                if deployment.returncode == 0 and pods.returncode == 0:
                    deploy_body = json.loads(deployment.stdout)
                    desired = int(deploy_body.get("spec", {}).get("replicas", -1))
                    ready_pods = [
                        item
                        for item in json.loads(pods.stdout or "{}").get("items", [])
                        if any(
                            condition.get("type") == "Ready" and condition.get("status") == "True"
                            for condition in item.get("status", {}).get("conditions", [])
                        )
                    ]
                    if desired == 0 and not ready_pods:
                        verified = True
                        break
                time.sleep(0.5)
            if not verified:
                raise RuntimeError("service-termination fault could not be positively verified")
            self.emit(
                "fault_application_verified",
                fault_id=self.scenario["fault"]["fault_id"],
                target="deployment/inventory",
                mode="deployment-scale-zero",
            )
        else:
            raise RuntimeError(f"fault application is not valid for {self.scenario_id}")

        self.emit(
            "injection_started",
            fault_id=self.scenario["fault"]["fault_id"],
            target=self.scenario["fault"]["target"],
        )

    def detect_fault(self, first_request_index: int) -> int:
        """Evaluate the shared workload-based detector and emit one detection boundary."""

        consecutive = 0
        threshold = 3
        for offset in range(threshold):
            record = self.workload_request("during-fault", first_request_index + offset)
            if self.scenario_id == "service-termination-v1":
                matched = record["status"] != 201
                observed_signal = f"http_status={record['status']}"
            else:
                matched = record["status"] == 201 and float(record["latency_ms"]) > 100.0
                observed_signal = f"latency_ms={record['latency_ms']}"
            consecutive = consecutive + 1 if matched else 0
            evaluation = self.emit(
                "detection_evaluation",
                detection_rule_version=self.scenario["detection_rule"]["version"],
                detection_rule_id=self.scenario["detection_rule"]["rule_id"],
                observed_signal=observed_signal,
                matched=matched,
                consecutive_matches=consecutive,
                parent_event_id=record["response_event_id"],
            )
            if consecutive == threshold:
                self.emit(
                    "fault_detected",
                    detection_rule_version=self.scenario["detection_rule"]["version"],
                    detection_rule_id=self.scenario["detection_rule"]["rule_id"],
                    observed_signal=observed_signal,
                    parent_event_id=evaluation["event_id"],
                )
                return first_request_index + offset + 1
        raise RuntimeError("shared detector did not reach the declared three-observation boundary")

    def recover(self) -> tuple[str, dict[str, Any], str]:
        """Apply the canonical recovery action but defer functional completion."""

        action = canonical_recovery_action(self.design, self.scenario_id)
        action_hash = sha256_json(action)
        if action_hash != self.recovery_action_hash:
            raise RuntimeError("canonical recovery action changed after trial manifest materialisation")

        if self.condition == "manual":
            initiator_event = self.emit(
                "external_intervention",
                initiator="manual",
                recovery_action_version=action["version"],
                canonical_recovery_action_sha256=action_hash,
            )
            initiator = "manual"
        else:
            initiator_event = self.emit(
                "automation_evaluation",
                initiator="automation",
                detection_rule_version=self.scenario["detection_rule"]["version"],
                observed_signal="shared_detector_satisfied",
                decision="recover",
                canonical_recovery_action_sha256=action_hash,
            )
            initiator = "automation"

        self.emit(
            "recovery_started",
            initiator=initiator,
            recovery_action_version=action["version"],
            recovery_action_id=action["action_id"],
            canonical_recovery_action_sha256=action_hash,
            parent_event_id=initiator_event["event_id"],
        )

        if self.scenario_id == "service-termination-v1":
            self.kubectl("-n", NAMESPACE, "scale", "deployment/inventory", "--replicas=1")
            self.kubectl(
                "-n",
                NAMESPACE,
                "rollout",
                "status",
                "deployment/inventory",
                "--timeout=120s",
            )
            self.start_port_forward("inventory", INVENTORY_PORT, 8081)
            status, _, _ = self.request(INVENTORY_PORT, "/healthz")
            if status != 200:
                raise RuntimeError("inventory readiness failed after scale-to-one recovery")
        else:
            status, body, _ = self.request(
                INVENTORY_PORT,
                action["path"],
                method=action["method"],
                body=action["payload"],
            )
            if status != 200 or body.get("mode") != "none":
                raise RuntimeError(f"latency recovery verification failed: {body}")

        self.emit(
            "recovery_action_completed",
            initiator=initiator,
            recovery_action_version=action["version"],
            recovery_action_id=action["action_id"],
            canonical_recovery_action_sha256=action_hash,
        )
        self.emit(
            "injection_ended",
            fault_id=self.scenario["fault"]["fault_id"],
            result="reverted",
        )
        return initiator, action, action_hash

    def execute_scenario_workload(self) -> None:
        """Run the selected no-fault or fault-scenario workload."""

        self.emit("workload_started", workload_id=self.design["shared_workload"]["workload_id"])
        next_index = 1

        if self.scenario_id == "no-fault-v1":
            request_count = int(self.scenario["workload"]["request_count"])
            for request_index in range(1, request_count + 1):
                record = self.workload_request("no-fault", request_index)
                if record["status"] != 201:
                    raise RuntimeError(f"no-fault request failed: {record}")
            self.emit("workload_completed", request_count=request_count)
            return

        for _ in range(2):
            record = self.workload_request("before-fault", next_index)
            if record["status"] != 201:
                raise RuntimeError(f"pre-fault request failed: {record}")
            next_index += 1

        self.apply_fault()
        next_index = self.detect_fault(next_index)
        initiator, action, action_hash = self.recover()

        post_recovery_records: list[dict[str, Any]] = []
        latency_threshold_ms = (
            float(self.scenario["detection_rule"]["threshold_ms"])
            if self.scenario_id == "dependency-latency-v1"
            else None
        )

        for post_recovery_index in range(2):
            record = self.workload_request("after-recovery", next_index)
            if record["status"] != 201:
                raise RuntimeError(f"post-recovery request failed: {record}")
            if latency_threshold_ms is not None and float(record["latency_ms"]) > latency_threshold_ms:
                raise RuntimeError(
                    "post-recovery latency remained above the detector threshold: "
                    f"latency_ms={record['latency_ms']}, threshold_ms={latency_threshold_ms}"
                )
            post_recovery_records.append(record)

            if post_recovery_index == 0:
                self.emit(
                    "recovery_completed",
                    initiator=initiator,
                    recovery_action_version=action["version"],
                    recovery_action_id=action["action_id"],
                    canonical_recovery_action_sha256=action_hash,
                    post_recovery_order_id=record["order_id"],
                    post_recovery_response_event_id=record["response_event_id"],
                )
            next_index += 1

        first_success = post_recovery_records[0]
        self.emit(
            "post_recovery_check",
            result="passed",
            first_success_order_id=first_success["order_id"],
            first_success_response_event_id=first_success["response_event_id"],
            request_count=len(post_recovery_records),
            maximum_latency_ms=max(float(record["latency_ms"]) for record in post_recovery_records),
            latency_threshold_ms=latency_threshold_ms,
        )
        self.emit("workload_completed", request_count=len(self.workload_records))

    def capture_service_logs(self, stage: str) -> None:
        """Capture available pod JSONL logs and merge them by event ID."""

        result = self.kubectl("-n", NAMESPACE, "get", "pods", "-o", "json", check=False)
        if result.returncode != 0:
            return
        merged = {str(event.get("event_id")): event for event in self.service_events}
        for pod in json.loads(result.stdout or "{}").get("items", []):
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
                event["capture_stage"] = stage
                event["source_component"] = event.get("source_component", component)
                merged[str(event.get("event_id"))] = event
        self.service_events = sorted(merged.values(), key=lambda event: event.get("timestamp", ""))
        with self.service_event_file.open("w", encoding="utf-8") as handle:
            for event in self.service_events:
                handle.write(json.dumps(event, sort_keys=True) + "\n")

    @staticmethod
    def decode_otel_spans(payloads: list[bytes]) -> list[dict[str, Any]]:
        """Decode the pinned OTLP protobuf payloads into auditable span records."""

        try:
            from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
                ExportTraceServiceRequest,
            )
        except ImportError as exc:
            raise RuntimeError("opentelemetry-proto 1.44.0 is required for Phase 5 trace validation") from exc

        records: list[dict[str, Any]] = []
        for payload in payloads:
            request = ExportTraceServiceRequest()
            request.ParseFromString(payload)
            for resource_spans in request.resource_spans:
                resource_attributes = {
                    item.key: item.value.string_value
                    for item in resource_spans.resource.attributes
                    if item.value.WhichOneof("value") == "string_value"
                }
                for scope_spans in resource_spans.scope_spans:
                    for span in scope_spans.spans:
                        attributes = {
                            item.key: item.value.string_value
                            for item in span.attributes
                            if item.value.WhichOneof("value") == "string_value"
                        }
                        records.append(
                            {
                                "name": span.name,
                                "trace_id": span.trace_id.hex(),
                                "span_id": span.span_id.hex(),
                                "parent_span_id": span.parent_span_id.hex(),
                                "resource": resource_attributes,
                                "attributes": attributes,
                            }
                        )
        return records

    def verify_observation(self) -> None:
        """Require structured coverage and exact order-event/OTel signature parity."""

        self.capture_service_logs(stage="final")
        components = {str(event.get("source_component")) for event in self.service_events}
        if not {"inventory", "order-api"}.issubset(components):
            raise RuntimeError(f"structured service observation incomplete: {sorted(components)}")
        trial_events = [
            event
            for event in self.service_events
            if event.get("trial_id") == self.trial_id and event.get("run_id") == self.run_id
        ]
        if not trial_events:
            raise RuntimeError("service events do not contain the selected Phase 5 trial identity")
        self.emit(
            "observation_verified",
            service_event_count=len(self.service_events),
            trial_identity_event_count=len(trial_events),
            observed_components=sorted(components),
        )

        expected = [
            event for event in self.service_events if event.get("order_id") and event.get("run_id") == self.run_id
        ]
        expected_signatures = sorted(
            (
                str(event["source_component"]),
                str(event["event_type"]),
                str(event["order_id"]),
                str(event["trace_id"]),
                str(event["span_id"]),
            )
            for event in expected
        )

        deadline = time.monotonic() + 20
        payloads: list[bytes] = []
        raw_payloads: list[bytes] = []
        encodings: list[str] = []
        matching_spans: list[dict[str, Any]] = []
        observed_signatures: list[tuple[str, str, str, str, str]] = []

        while time.monotonic() < deadline:
            status, body, _ = self.request(TELEMETRY_SINK_PORT, "/records")
            if status == 200:
                encoded = body.get("payloads_base64", [])
                encoded_raw = body.get("raw_payloads_base64", [])
                content_encodings = body.get("content_encodings", [])
                if isinstance(encoded, list) and isinstance(encoded_raw, list) and isinstance(content_encodings, list):
                    payloads = [base64.b64decode(str(item)) for item in encoded]
                    raw_payloads = [base64.b64decode(str(item)) for item in encoded_raw]
                    encodings = [str(item) for item in content_encodings]
                    decoded = self.decode_otel_spans(payloads)
                    matching_spans = [
                        span
                        for span in decoded
                        if span["attributes"].get("orderflow.run_id") == self.run_id
                        and span["attributes"].get("orderflow.order_id")
                    ]
                    observed_signatures = sorted(
                        (
                            str(span["attributes"].get("orderflow.source_component", "")),
                            str(span["attributes"].get("orderflow.event_type", "")),
                            str(span["attributes"].get("orderflow.order_id", "")),
                            str(span["attributes"].get("orderflow.trace_id", "")),
                            str(span["attributes"].get("orderflow.span_id", "")),
                        )
                        for span in matching_spans
                    )
                    if observed_signatures == expected_signatures:
                        break
            time.sleep(0.25)

        self.otel_payload_file.write_text(
            json.dumps(
                {
                    "trial_id": self.trial_id,
                    "run_id": self.run_id,
                    "payload_count": len(payloads),
                    "content_encodings": encodings,
                    "payload_sha256": [hashlib.sha256(item).hexdigest() for item in payloads],
                    "raw_payload_sha256": [hashlib.sha256(item).hexdigest() for item in raw_payloads],
                    "payloads_base64": [base64.b64encode(item).decode("ascii") for item in payloads],
                    "raw_payloads_base64": [base64.b64encode(item).decode("ascii") for item in raw_payloads],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        self.otel_spans = matching_spans
        self.otel_span_file.write_text(
            json.dumps(
                {
                    "trial_id": self.trial_id,
                    "run_id": self.run_id,
                    "expected_order_span_count": len(expected_signatures),
                    "observed_order_span_count": len(observed_signatures),
                    "signatures_match_structured_events": (observed_signatures == expected_signatures),
                    "spans": matching_spans,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        if observed_signatures != expected_signatures:
            raise RuntimeError(
                "OpenTelemetry structured-event parity failed: "
                f"expected={len(expected_signatures)}, observed={len(observed_signatures)}"
            )
        self.emit(
            "otel_observation_verified",
            expected_order_span_count=len(expected_signatures),
            observed_order_span_count=len(observed_signatures),
            parity_with_structured_events=True,
        )

    def verify_fault_clean_for_cleanup(self) -> None:
        """Restore/verify inventory before namespace teardown, even after failures."""

        if self.scenario_id == "service-termination-v1":
            self.kubectl("-n", NAMESPACE, "scale", "deployment/inventory", "--replicas=1", check=False)
            rollout = self.kubectl(
                "-n",
                NAMESPACE,
                "rollout",
                "status",
                "deployment/inventory",
                "--timeout=120s",
                check=False,
            )
            if rollout.returncode != 0:
                raise RuntimeError("inventory could not be restored to one replica during cleanup")
            self.start_port_forward("inventory", INVENTORY_PORT, 8081)
        if "inventory" in self.port_forwards:
            status, body, _ = self.request(INVENTORY_PORT, "/__control", method="POST", body={"mode": "none"})
            if status != 200 or body.get("mode") != "none":
                raise RuntimeError("inventory mode=none cleanup verification failed")
        self.emit("fault_state_verified", mode="none", stage="before_namespace_cleanup")

    def cleanup(self) -> None:
        """Restore fault state, always attempt namespace deletion, and verify absence."""

        self.emit("cleanup_started", namespace=NAMESPACE)
        restoration_error: str | None = None
        try:
            self.verify_fault_clean_for_cleanup()
        except Exception as exc:
            restoration_error = f"{type(exc).__name__}: {exc}"
            self.emit("fault_state_cleanup_failed", error=restoration_error)

        try:
            self.capture_service_logs(stage="cleanup")
        except Exception as exc:
            self.emit(
                "service_log_capture_failed",
                error=f"{type(exc).__name__}: {exc}",
                stage="cleanup",
            )
        finally:
            self.stop_all_port_forwards()

        self.kubectl(
            "delete",
            "namespace",
            NAMESPACE,
            "--ignore-not-found=true",
            "--wait=true",
            "--timeout=60s",
            check=False,
        )
        check = self.kubectl("get", "namespace", NAMESPACE, "-o", "name", check=False)
        clean = check.returncode != 0
        self.emit("clean_state_verified", stage="after_cleanup", namespace_present=not clean)

        if not clean:
            self.emit("cleanup_completed", result="contaminated")
            raise RuntimeError("Phase 5 namespace remains after cleanup")

        result = "clean" if restoration_error is None else "clean-with-pre-teardown-error"
        self.emit("cleanup_completed", result=result)
        if restoration_error is not None:
            raise RuntimeError(f"fault-state cleanup failed before verified namespace removal: {restoration_error}")

    def write_workload(self) -> None:
        """Persist all offered requests and responses."""

        self.workload_file.write_text(
            json.dumps(
                {
                    "trial_id": self.trial_id,
                    "run_id": self.run_id,
                    "scenario_id": self.scenario_id,
                    "automation_condition": self.condition,
                    "requests": self.workload_records,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def write_metadata(self) -> None:
        """Write immutable provenance metadata for this development trial."""

        repo_sha = run_command(["git", "rev-parse", "HEAD"]).stdout.strip()
        context = self.kubectl("config", "current-context", check=False).stdout.strip()
        metadata = {
            "trial_id": self.trial_id,
            "run_id": self.run_id,
            "evidence_boundary": EVIDENCE_BOUNDARY,
            "controller_version": CONTROLLER_VERSION,
            "scenario_id": self.scenario_id,
            "automation_condition": self.condition,
            "repository_commit_sha": repo_sha,
            "pilot_manifest_sha256": sha256_file(PILOT_MANIFEST),
            "protocol_sha256": sha256_file(PROTOCOL),
            "prototype_manifest_sha256": sha256_file(PROTOTYPE_MANIFEST),
            "parent_prototype_manifest_sha256": sha256_file(PARENT_PROTOTYPE_MANIFEST),
            "kubernetes_manifest_sha256": sha256_file(KUBERNETES_MANIFEST),
            "recovery_action_sha256": self.recovery_action_hash,
            "images": self.image_records,
            "kubernetes_node_images": self.node_image_records,
            "external_images": self.external_image_records,
            "kubernetes_context": context,
            "docker_version": command_version(
                [
                    "docker",
                    "version",
                    "--format",
                    "Client={{.Client.Version}} Server={{.Server.Version}}",
                ]
            ),
            "kubectl_version": command_version(["kubectl", "version"]),
            "host": {
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "python": platform.python_version(),
            },
            "created_at": utc_now(),
        }
        self.metadata_file.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def write_validity(self) -> dict[str, Any]:
        """Classify development-trial validity without pretending it is a pilot slot."""

        event_types = [str(event["event_type"]) for event in self.events]
        is_fault = self.scenario_id in FAULT_SCENARIOS
        checks = {
            "development_guard": True,
            "primary_schedule_not_consumed": True,
            "preflight_completed": "preflight_completed" in event_types,
            "source_tree_verified": "source_tree_verified" in event_types,
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
            "recovery_completed": "recovery_completed" in event_types if is_fault else True,
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
        validity = {
            "trial_id": self.trial_id,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "automation_condition": self.condition,
            "evidence_boundary": EVIDENCE_BOUNDARY,
            "pilot_batch_id": None,
            "primary_schedule_slot": None,
            "passed": all(checks.values()),
            "checks": checks,
            "execution_error": self.execution_error,
            "classification": (
                "valid-development-feasibility-trial"
                if all(checks.values())
                else "invalid-development-feasibility-trial"
            ),
            "created_at": utc_now(),
        }
        self.validity_file.write_text(json.dumps(validity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return validity

    def execute(self) -> dict[str, Any]:
        """Execute one guarded development trial and always attempt cleanup."""

        if self.run_dir.exists():
            raise RuntimeError(f"refusing to reuse output directory: {self.run_dir}")
        self.run_dir.mkdir(parents=True)
        self.emit("trial_started", evidence_boundary=EVIDENCE_BOUNDARY)
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


def main() -> int:
    """CLI entry point with an explicit development-only execution guard."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=sorted(ALLOWED_SCENARIOS), required=True)
    parser.add_argument(
        "--condition",
        choices=["control", "manual", "automated"],
        required=True,
    )
    parser.add_argument(
        "--development-validation",
        action="store_true",
        help="Required guard acknowledging that this is not a primary pilot trial.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "results" / "phase-5" / "development" / "raw",
    )
    args = parser.parse_args()

    try:
        validate_development_selection(args.scenario, args.condition, args.development_validation)
    except ValueError as exc:
        parser.error(str(exc))

    output_root = args.output_root.resolve()
    primary_root = (ROOT / "results" / "phase-5" / "raw").resolve()
    if output_root == primary_root or primary_root in output_root.parents:
        parser.error("single-trial development controller cannot write under results/phase-5/raw")
    output_root.mkdir(parents=True, exist_ok=True)

    trial = Phase5DevelopmentTrial(
        args.scenario,
        args.condition,
        output_root,
        development_validation=True,
    )
    validity = trial.execute()
    print(
        json.dumps(
            {
                "trial_id": trial.trial_id,
                "run_id": trial.run_id,
                "run_directory": str(trial.run_dir),
                "validity_file": str(trial.validity_file),
                "passed": validity["passed"],
                "evidence_boundary": EVIDENCE_BOUNDARY,
                "pilot_batch_id": None,
                "primary_schedule_slot": None,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if validity["passed"] else 1


if __name__ == "__main__":  # pragma: no cover - CLI execution boundary
    sys.exit(main())
