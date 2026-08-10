#!/usr/bin/env python3
"""Execute one bounded Phase 4 Kubernetes reproducibility validation.

This controller demonstrates only build/deploy/readiness/version/workload/
observation/cleanup/reset reproducibility for the Phase 4 OrderFlow prototype.
It does not execute the Phase 5 recovery-condition experiment.
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
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROTOTYPE_MANIFEST = ROOT / "infrastructure" / "prototype" / "orderflow-phase-4.json"
KUBERNETES_MANIFEST = ROOT / "infrastructure" / "kubernetes" / "orderflow-phase-4.yaml"
NAMESPACE = "orderflow-phase4"
KUBERNETES_NODE = "desktop-control-plane"
ORDER_PORT = 19480
INVENTORY_PORT = 19481
CONTROLLER_VERSION = "phase-4-reproducibility-controller-v1"
WORKLOAD_ID = "phase-4-fixed-synthetic-orders-v1"
WORKLOAD_COUNT = 3


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
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(args)}\n{detail}")
    return result


def command_version(args: list[str]) -> str:
    result = run_command(args, check=False)
    return (result.stdout.strip() or result.stderr.strip()).strip()


class Phase4Validation:
    def __init__(self, output_root: Path) -> None:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        self.run_id = f"phase4-repro-{stamp}-{uuid.uuid4().hex[:8]}"
        self.output_root = output_root
        self.run_dir = output_root / self.run_id
        self.event_file = self.run_dir / "events.jsonl"
        self.service_event_file = self.run_dir / "service-events.jsonl"
        self.workload_file = self.run_dir / "workload.json"
        self.metadata_file = self.run_dir / "metadata.json"
        self.validity_file = self.run_dir / "validity.json"
        self.events: list[dict[str, Any]] = []
        self.service_events: list[dict[str, Any]] = []
        self.port_forwards: list[subprocess.Popen[str]] = []
        self.prototype = json.loads(PROTOTYPE_MANIFEST.read_text(encoding="utf-8"))
        self.image_records: dict[str, dict[str, str]] = {}
        self.node_image_records: dict[str, dict[str, str]] = {}
        self.workload_records: list[dict[str, Any]] = []

    def emit(self, event_type: str, **fields: Any) -> None:
        event = {
            "event_id": f"phase4-controller-{len(self.events) + 1:05d}",
            "run_id": self.run_id,
            "scenario_id": "phase4-reproducibility-validation",
            "source_component": "phase4-reproducibility-controller",
            "event_type": event_type,
            "timestamp": utc_now(),
            "trace_id": uuid.uuid4().hex,
            "software_version": CONTROLLER_VERSION,
            **fields,
        }
        self.events.append(event)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        with self.event_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

    def kubectl(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return run_command(["kubectl", *args], check=check)

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
        self, port: int, path: str, method: str = "GET", body: dict[str, Any] | None = None
    ) -> tuple[int, dict[str, Any], float]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, method=method)
        if body is not None:
            request.add_header("Content-Type", "application/json")
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=3.0) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return response.status, payload, time.perf_counter() - started
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))
            return exc.code, payload, time.perf_counter() - started
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            return 0, {"error": "connection-failed"}, time.perf_counter() - started

    def ensure_prerequisites(self) -> None:
        missing = [tool for tool in ("docker", "kubectl", "git") if shutil.which(tool) is None]
        if missing:
            raise RuntimeError(f"missing required tools: {', '.join(missing)}")
        context = self.kubectl("config", "current-context").stdout.strip()
        if context != "docker-desktop":
            raise RuntimeError(f"unexpected Kubernetes context: {context!r}; expected 'docker-desktop'")
        self.emit("preflight_completed", tools=["docker", "kubectl", "git"], kubernetes_context=context)

    def verify_source_tree_clean(self) -> None:
        unstaged = run_command(["git", "diff", "--quiet"], check=False)
        staged = run_command(["git", "diff", "--cached", "--quiet"], check=False)
        invalid_codes = [result.returncode for result in (unstaged, staged) if result.returncode not in {0, 1}]
        if invalid_codes:
            raise RuntimeError(f"could not verify repository source state; git exit codes={invalid_codes}")
        if unstaged.returncode == 1 or staged.returncode == 1:
            raise RuntimeError("tracked or staged repository changes are present; refusing reproducibility validation")
        repo_sha = run_command(["git", "rev-parse", "HEAD"]).stdout.strip()
        self.emit("source_tree_verified", repository_commit_sha=repo_sha, tracked_changes=False)

    def clean_before_deploy(self) -> None:
        self.emit("pre_deploy_cleanup_started", namespace=NAMESPACE)
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
            raise RuntimeError("Phase 4 namespace still exists after pre-deploy cleanup")
        self.emit("clean_state_verified", stage="before_deploy", namespace_present=False)

    def build_images(self) -> None:
        packaging = self.prototype["packaging"]
        dockerfile = str(ROOT / packaging["dockerfile"])
        platform_name = packaging["build_platform"]
        for service in ("inventory", "order-api"):
            tag = packaging["images"][service]
            self.emit(
                "image_build_started",
                service=service,
                image=tag,
                platform=platform_name,
                base_image=packaging["base_image"],
            )
            run_command(
                [
                    "docker",
                    "build",
                    "--pull=false",
                    "--platform",
                    platform_name,
                    "--provenance=false",
                    "-t",
                    tag,
                    "-f",
                    dockerfile,
                    ".",
                ]
            )
            image_id = run_command(["docker", "image", "inspect", tag, "--format", "{{.Id}}"]).stdout.strip()
            repo_digests = run_command(
                ["docker", "image", "inspect", tag, "--format", "{{json .RepoDigests}}"]
            ).stdout.strip()
            self.image_records[service] = {"tag": tag, "image_id": image_id, "repo_digests": repo_digests}
            self.emit("image_build_completed", service=service, image=tag, image_id=image_id)

    def import_images_into_kubernetes_node(self) -> None:
        node_check = run_command(
            ["docker", "inspect", "--type", "container", KUBERNETES_NODE, "--format", "{{.State.Running}}"],
            check=False,
        )
        if node_check.returncode != 0 or node_check.stdout.strip().lower() != "true":
            raise RuntimeError(f"Kubernetes node container is not running: {KUBERNETES_NODE}")

        with tempfile.TemporaryDirectory(prefix="phase4-image-import-") as temp_dir:
            temp_root = Path(temp_dir)
            for service in ("inventory", "order-api"):
                tag = self.prototype["packaging"]["images"][service]
                expected_ref = f"docker.io/{tag}"
                archive = temp_root / f"{service}.tar"
                remote_archive = f"/tmp/{self.run_id}-{service}.tar"

                self.emit(
                    "image_import_started",
                    service=service,
                    image=tag,
                    kubernetes_node=KUBERNETES_NODE,
                    containerd_namespace="k8s.io",
                )
                run_command(["docker", "save", "--output", str(archive), tag])
                run_command(["docker", "cp", str(archive), f"{KUBERNETES_NODE}:{remote_archive}"])
                try:
                    run_command(
                        [
                            "docker",
                            "exec",
                            KUBERNETES_NODE,
                            "ctr",
                            "-n",
                            "k8s.io",
                            "images",
                            "import",
                            remote_archive,
                        ]
                    )
                finally:
                    run_command(
                        ["docker", "exec", KUBERNETES_NODE, "rm", "-f", remote_archive],
                        check=False,
                    )

                node_images = run_command(
                    ["docker", "exec", KUBERNETES_NODE, "ctr", "-n", "k8s.io", "images", "ls"]
                ).stdout.splitlines()
                matching = [line for line in node_images if line.startswith(expected_ref)]
                if not matching:
                    raise RuntimeError(f"imported image is not visible in Kubernetes node runtime: {expected_ref}")
                digest = next(
                    (field for field in matching[0].split() if field.startswith("sha256:")),
                    "",
                )
                if not digest:
                    raise RuntimeError(f"could not identify Kubernetes node image digest for {expected_ref}")
                self.node_image_records[service] = {
                    "node": KUBERNETES_NODE,
                    "containerd_namespace": "k8s.io",
                    "reference": expected_ref,
                    "digest": digest,
                }
                self.emit(
                    "node_image_verified",
                    service=service,
                    image_reference=expected_ref,
                    image_digest=digest,
                    kubernetes_node=KUBERNETES_NODE,
                )

        self.emit(
            "image_import_completed",
            imported_services=sorted(self.node_image_records),
            kubernetes_node=KUBERNETES_NODE,
        )

    def deploy(self) -> None:
        self.emit("deployment_started", manifest=str(KUBERNETES_MANIFEST.relative_to(ROOT)))
        self.kubectl("apply", "-f", str(KUBERNETES_MANIFEST))
        for deployment in ("inventory", "order-api"):
            self.kubectl(
                "-n",
                NAMESPACE,
                "set",
                "env",
                f"deployment/{deployment}",
                f"ORDERFLOW_RUN_ID={self.run_id}",
                "ORDERFLOW_SCENARIO_ID=phase4-reproducibility-validation",
            )
        for deployment in ("inventory", "order-api"):
            self.kubectl(
                "-n",
                NAMESPACE,
                "rollout",
                "status",
                f"deployment/{deployment}",
                "--timeout=120s",
            )
        self.emit("deployment_completed", namespace=NAMESPACE)

    def wait_and_forward(self) -> None:
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            result = self.kubectl("-n", NAMESPACE, "get", "pods", "-o", "json", check=False)
            if result.returncode == 0:
                items = json.loads(result.stdout or "{}").get("items", [])
                ready = {
                    item.get("metadata", {}).get("labels", {}).get("app")
                    for item in items
                    if any(
                        condition.get("type") == "Ready" and condition.get("status") == "True"
                        for condition in item.get("status", {}).get("conditions", [])
                    )
                }
                if ready == {"inventory", "order-api"}:
                    break
            time.sleep(1)
        else:
            raise RuntimeError("Phase 4 pods did not both become Ready")

        self.start_port_forward("inventory", INVENTORY_PORT, 8081)
        self.start_port_forward("order-api", ORDER_PORT, 8080)

        inventory_status, _, _ = self.request(INVENTORY_PORT, "/healthz")
        order_status, _, _ = self.request(ORDER_PORT, "/healthz")
        if inventory_status != 200 or order_status != 200:
            raise RuntimeError(f"readiness endpoints failed: inventory={inventory_status}, order-api={order_status}")
        self.emit(
            "readiness_verified",
            statuses={"inventory": inventory_status, "order-api": order_status},
        )

    def verify_versions(self) -> None:
        expected = {
            "inventory": self.prototype["topology"]["services"]["inventory"]["version"],
            "order-api": self.prototype["topology"]["services"]["order-api"]["version"],
        }
        observed: dict[str, str] = {}
        for service, port in (("inventory", INVENTORY_PORT), ("order-api", ORDER_PORT)):
            status, body, _ = self.request(port, "/version")
            version = str(body.get("version", ""))
            observed[service] = version
            if status != 200 or version != expected[service]:
                raise RuntimeError(
                    f"version check failed for {service}: status={status}, observed={version!r}, "
                    f"expected={expected[service]!r}"
                )
        self.emit("version_verified", expected=expected, observed=observed)

    def run_workload(self) -> None:
        self.emit("workload_started", workload_id=WORKLOAD_ID, request_count=WORKLOAD_COUNT)
        for index in range(1, WORKLOAD_COUNT + 1):
            order_id = f"{self.run_id}-order-{index:03d}"
            status, body, elapsed = self.request(
                ORDER_PORT,
                "/orders",
                method="POST",
                body={"order_id": order_id},
            )
            record = {
                "request_index": index,
                "order_id": order_id,
                "status": status,
                "result": "success" if status == 201 else "failure",
                "latency_ms": round(elapsed * 1000, 3),
                "response": body,
            }
            self.workload_records.append(record)
            self.emit("workload_response", **record)
            if status != 201:
                raise RuntimeError(f"deterministic workload request failed: {record}")
        self.workload_file.write_text(
            json.dumps(
                {"run_id": self.run_id, "workload_id": WORKLOAD_ID, "requests": self.workload_records},
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        self.emit("workload_completed", success_count=len(self.workload_records), failure_count=0)

    def capture_service_logs(self) -> None:
        result = self.kubectl("-n", NAMESPACE, "get", "pods", "-o", "json", check=False)
        if result.returncode != 0:
            return
        events: list[dict[str, Any]] = []
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
                event["source_component"] = event.get("source_component", component)
                events.append(event)
        self.service_events = sorted(events, key=lambda event: event.get("timestamp", ""))
        with self.service_event_file.open("w", encoding="utf-8") as handle:
            for event in self.service_events:
                handle.write(json.dumps(event, sort_keys=True) + "\n")
        components = {event.get("source_component") for event in self.service_events}
        if not {"inventory", "order-api"}.issubset(components):
            raise RuntimeError(
                f"service observation incomplete; observed components={sorted(str(x) for x in components)}"
            )
        traceable = [
            event
            for event in self.service_events
            if event.get("trace_id") and event.get("span_id") and event.get("run_id") == self.run_id
        ]
        if not traceable:
            raise RuntimeError("no correlated service event with trace_id/span_id was captured")
        self.emit(
            "observation_verified",
            service_event_count=len(self.service_events),
            observed_components=sorted(str(x) for x in components),
            traceable_event_count=len(traceable),
            telemetry_contract=self.prototype["telemetry_contract"],
        )

    def cleanup(self) -> None:
        self.stop_port_forwards()
        self.emit("cleanup_started", namespace=NAMESPACE)
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
        self.emit("cleanup_completed", result="clean" if clean else "contaminated")
        if not clean:
            raise RuntimeError("Phase 4 namespace remains after cleanup")

    def write_metadata(self) -> None:
        repo_sha = run_command(["git", "rev-parse", "HEAD"]).stdout.strip()
        docker_info = command_version(
            ["docker", "version", "--format", "Client={{.Client.Version}} Server={{.Server.Version}}"]
        )
        kubectl_version = command_version(["kubectl", "version"])
        context = self.kubectl("config", "current-context").stdout.strip()
        metadata = {
            "run_id": self.run_id,
            "evidence_boundary": "phase-4-reproducibility-only",
            "controller_version": CONTROLLER_VERSION,
            "repository_commit_sha": repo_sha,
            "prototype_manifest": str(PROTOTYPE_MANIFEST.relative_to(ROOT)),
            "prototype_manifest_sha256": sha256_file(PROTOTYPE_MANIFEST),
            "kubernetes_manifest": str(KUBERNETES_MANIFEST.relative_to(ROOT)),
            "kubernetes_manifest_sha256": sha256_file(KUBERNETES_MANIFEST),
            "prototype_id": self.prototype["prototype_id"],
            "prototype_version": self.prototype["prototype_version"],
            "base_image": self.prototype["packaging"]["base_image"],
            "build_platform": self.prototype["packaging"]["build_platform"],
            "images": self.image_records,
            "kubernetes_node_images": self.node_image_records,
            "target_model": self.prototype["target_model"],
            "kubernetes_context": context,
            "docker_version": docker_info,
            "kubectl_version": kubectl_version,
            "host": {
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "python": platform.python_version(),
            },
            "raw_files": {
                "controller_events": {
                    "path": str(self.event_file.relative_to(ROOT)),
                    "exists": self.event_file.exists(),
                },
                "service_events": {
                    "path": str(self.service_event_file.relative_to(ROOT)),
                    "exists": self.service_event_file.exists(),
                },
                "workload": {
                    "path": str(self.workload_file.relative_to(ROOT)),
                    "exists": self.workload_file.exists(),
                },
            },
            "created_at": utc_now(),
        }
        self.metadata_file.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def write_validity(self, execution_error: str | None = None) -> dict[str, Any]:
        event_types = {event["event_type"] for event in self.events}
        checks = {
            "preflight_completed": "preflight_completed" in event_types,
            "source_tree_verified": "source_tree_verified" in event_types,
            "clean_before_deploy": any(
                event["event_type"] == "clean_state_verified"
                and event.get("stage") == "before_deploy"
                and event.get("namespace_present") is False
                for event in self.events
            ),
            "images_built": set(self.image_records) == {"inventory", "order-api"},
            "node_images_available": set(self.node_image_records) == {"inventory", "order-api"}
            and "image_import_completed" in event_types,
            "deployment_completed": "deployment_completed" in event_types,
            "readiness_verified": "readiness_verified" in event_types,
            "version_verified": "version_verified" in event_types,
            "workload_completed": (
                "workload_completed" in event_types
                and len(self.workload_records) == WORKLOAD_COUNT
                and all(record["status"] == 201 for record in self.workload_records)
            ),
            "observation_verified": "observation_verified" in event_types,
            "clean_after_run": any(
                event["event_type"] == "clean_state_verified"
                and event.get("stage") == "after_cleanup"
                and event.get("namespace_present") is False
                for event in self.events
            ),
            "fresh_output_directory": self.run_dir.name == self.run_id,
            "provenance_written": self.metadata_file.exists(),
            "no_execution_error": execution_error is None,
        }
        validity = {
            "run_id": self.run_id,
            "evidence_boundary": "phase-4-reproducibility-only",
            "passed": all(checks.values()),
            "checks": checks,
            "execution_error": execution_error,
            "created_at": utc_now(),
        }
        self.validity_file.write_text(json.dumps(validity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return validity

    def execute(self) -> dict[str, Any]:
        if self.run_dir.exists():
            raise RuntimeError(f"refusing to reuse existing output directory: {self.run_dir}")
        self.run_dir.mkdir(parents=True)
        error: str | None = None
        self.emit("run_started", evidence_boundary="phase-4-reproducibility-only")
        try:
            self.ensure_prerequisites()
            self.verify_source_tree_clean()
            self.clean_before_deploy()
            self.build_images()
            self.import_images_into_kubernetes_node()
            self.deploy()
            self.wait_and_forward()
            self.verify_versions()
            self.run_workload()
            self.capture_service_logs()
            self.cleanup()
            self.emit("run_completed", result="success")
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            self.emit("run_failed", error=error)
            try:
                self.capture_service_logs()
            except Exception:
                pass
            try:
                self.cleanup()
            except Exception as cleanup_exc:
                self.emit("cleanup_failed", error=f"{type(cleanup_exc).__name__}: {cleanup_exc}")
        finally:
            self.stop_port_forwards()
            self.write_metadata()
        validity = self.write_validity(error)
        return validity


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "results" / "phase-4" / "raw",
        help="Directory containing fresh immutable run directories.",
    )
    args = parser.parse_args()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    validation = Phase4Validation(output_root)
    result = validation.execute()
    print(
        json.dumps(
            {
                "run_id": validation.run_id,
                "run_directory": str(validation.run_dir),
                "validity_file": str(validation.validity_file),
                "passed": result["passed"],
            },
            indent=2,
        )
    )
    return 0 if result["passed"] else 1


if __name__ == "__main__":  # pragma: no cover - CLI execution boundary
    sys.exit(main())
