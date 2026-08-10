"""Unit tests for the Phase 4 reproducibility controller."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from experiments.harness import phase_4_reproducibility as phase4


def make_validation(tmp_path: Path) -> phase4.Phase4Validation:
    return phase4.Phase4Validation(tmp_path)


def test_sha256_file_is_deterministic(tmp_path: Path) -> None:
    path = tmp_path / "example.txt"
    path.write_text("phase4\n", encoding="utf-8")
    first = phase4.sha256_file(path)
    second = phase4.sha256_file(path)
    assert first == second
    assert len(first) == 64


def test_write_validity_requires_all_phase4_boundaries(tmp_path: Path) -> None:
    validation = make_validation(tmp_path)
    validation.run_dir.mkdir(parents=True)
    validation.image_records = {
        "inventory": {"tag": "inventory", "image_id": "sha256:a", "repo_digests": "[]"},
        "order-api": {"tag": "order", "image_id": "sha256:b", "repo_digests": "[]"},
        "telemetry-sink": {"tag": "sink", "image_id": "sha256:c", "repo_digests": "[]"},
    }
    validation.external_image_records = {
        "otel-collector": {"tag": "collector", "image_id": "sha256:d", "repo_digests": "[]"}
    }
    validation.node_image_records = {
        "inventory": {"reference": "docker.io/orderflow/inventory:phase4-v1"},
        "order-api": {"reference": "docker.io/orderflow/order-api:phase4-v1"},
        "telemetry-sink": {"reference": "docker.io/orderflow/telemetry-sink:phase4-v1"},
        "otel-collector": {"reference": "docker.io/otel/opentelemetry-collector:0.158.0"},
    }
    validation.workload_records = [
        {"status": 201},
        {"status": 201},
        {"status": 201},
    ]
    validation.metadata_file.write_text("{}\n", encoding="utf-8")
    for event_type, fields in (
        ("preflight_completed", {}),
        ("source_tree_verified", {}),
        ("external_image_verified", {}),
        ("image_import_completed", {}),
        ("clean_state_verified", {"stage": "before_deploy", "namespace_present": False}),
        ("deployment_completed", {}),
        ("readiness_verified", {}),
        ("version_verified", {}),
        ("workload_completed", {}),
        ("observation_verified", {}),
        ("otel_observation_verified", {}),
        ("clean_state_verified", {"stage": "after_cleanup", "namespace_present": False}),
    ):
        validation.events.append({"event_type": event_type, **fields})

    validity = validation.write_validity()

    assert validity["passed"] is True
    assert all(validity["checks"].values())


def test_write_validity_fails_when_cleanup_is_not_clean(tmp_path: Path) -> None:
    validation = make_validation(tmp_path)
    validation.run_dir.mkdir(parents=True)
    validation.metadata_file.write_text("{}\n", encoding="utf-8")
    validity = validation.write_validity("RuntimeError: cleanup failed")
    assert validity["passed"] is False
    assert validity["checks"]["clean_after_run"] is False
    assert validity["checks"]["no_execution_error"] is False


def test_build_images_records_image_identity(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    validation = make_validation(tmp_path)
    validation.run_dir.mkdir(parents=True)

    calls: list[list[str]] = []

    def fake_run(args: list[str], check: bool = True) -> Any:
        calls.append(args)
        if args[:3] == ["docker", "image", "inspect"] and args[-1] == "{{.Id}}":
            return SimpleNamespace(returncode=0, stdout="sha256:example\n", stderr="")
        if args[:3] == ["docker", "image", "inspect"] and args[-1] == "{{json .RepoDigests}}":
            return SimpleNamespace(returncode=0, stdout="[]\n", stderr="")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(phase4, "run_command", fake_run)
    validation.build_images()

    assert set(validation.image_records) == {"inventory", "order-api", "telemetry-sink"}
    assert validation.image_records["inventory"]["image_id"] == "sha256:example"
    build_calls = [call for call in calls if call[:2] == ["docker", "build"]]
    assert len(build_calls) == 3
    assert all("--pull=false" in call for call in build_calls)
    assert all("--provenance=false" in call for call in build_calls)
    assert all("linux/amd64" in call for call in build_calls)


def test_stream_docker_image_to_containerd_uses_stdin_pipeline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakePipe:
        def close(self) -> None:
            return None

        def read(self) -> bytes:
            return b""

    class FakeSaveProcess:
        def __init__(self) -> None:
            self.stdout = FakePipe()
            self.stderr = FakePipe()

        def wait(self) -> int:
            return 0

    class FakeImportProcess:
        returncode = 0

        def communicate(self) -> tuple[bytes, bytes]:
            return b"imported", b""

    calls: list[list[str]] = []

    def fake_popen(args: list[str], **kwargs: Any) -> Any:
        calls.append(args)
        if args[:2] == ["docker", "save"]:
            return FakeSaveProcess()
        if args[:3] == ["docker", "exec", "-i"]:
            return FakeImportProcess()
        raise AssertionError(args)

    monkeypatch.setattr(phase4.subprocess, "Popen", fake_popen)

    output = phase4.stream_docker_image_to_containerd("orderflow/inventory:phase4-v1")

    assert output == "imported"
    assert calls[0] == ["docker", "save", "orderflow/inventory:phase4-v1"]
    assert calls[1][-2:] == ["import", "-"]


def test_verify_external_images_accepts_pinned_collector_digest(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validation = make_validation(tmp_path)

    def fake_run(args: list[str], check: bool = True) -> Any:
        if args[-1] == "{{.Id}}":
            return SimpleNamespace(
                returncode=0,
                stdout="sha256:5b97e6e3550ec6e48a71dba6f6304d349a293af8df4ee1f51da67be94fce2ecd\n",
                stderr="",
            )
        if args[-1] == "{{json .RepoDigests}}":
            return SimpleNamespace(returncode=0, stdout="[]\n", stderr="")
        raise AssertionError(args)

    monkeypatch.setattr(phase4, "run_command", fake_run)
    validation.verify_external_images()
    assert (
        validation.external_image_records["otel-collector"]["image_id"]
        == "sha256:5b97e6e3550ec6e48a71dba6f6304d349a293af8df4ee1f51da67be94fce2ecd"
    )


def test_import_images_into_kubernetes_node_records_all_runtime_digests(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validation = make_validation(tmp_path)
    validation.run_dir.mkdir(parents=True)
    validation.image_records = {
        "inventory": {"tag": "inventory", "image_id": "sha256:aaa", "repo_digests": "[]"},
        "order-api": {"tag": "order", "image_id": "sha256:bbb", "repo_digests": "[]"},
        "telemetry-sink": {"tag": "sink", "image_id": "sha256:ccc", "repo_digests": "[]"},
    }
    validation.external_image_records = {
        "otel-collector": {
            "tag": "otel/opentelemetry-collector:0.158.0",
            "image_id": "sha256:ddd",
            "repo_digests": "[]",
        }
    }

    def fake_run(args: list[str], check: bool = True) -> Any:
        if args[:4] == ["docker", "inspect", "--type", "container"]:
            return SimpleNamespace(returncode=0, stdout="true\n", stderr="")
        if args[:3] == ["docker", "exec", phase4.KUBERNETES_NODE] and args[-2:] == ["images", "ls"]:
            return SimpleNamespace(
                returncode=0,
                stdout=(
                    "REF TYPE DIGEST SIZE PLATFORMS LABELS\n"
                    "docker.io/orderflow/inventory:phase4-v1 type sha256:aaa 1 linux/amd64 managed\n"
                    "docker.io/orderflow/order-api:phase4-v1 type sha256:bbb 1 linux/amd64 managed\n"
                    "docker.io/orderflow/telemetry-sink:phase4-v1 type sha256:ccc 1 linux/amd64 managed\n"
                    "docker.io/otel/opentelemetry-collector:0.158.0 type sha256:ddd 1 linux/amd64 managed\n"
                ),
                stderr="",
            )
        raise AssertionError(args)

    monkeypatch.setattr(phase4, "run_command", fake_run)
    monkeypatch.setattr(phase4, "stream_docker_image_to_containerd", lambda image: "imported")
    validation.import_images_into_kubernetes_node()

    assert set(validation.node_image_records) == {"inventory", "order-api", "telemetry-sink", "otel-collector"}
    assert validation.events[-1]["event_type"] == "image_import_completed"


def test_run_workload_uses_deterministic_order_identity(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    validation = make_validation(tmp_path)
    validation.run_dir.mkdir(parents=True)

    def fake_request(port: int, path: str, method: str = "GET", body: dict[str, Any] | None = None) -> Any:
        assert port == phase4.ORDER_PORT
        assert path == "/orders"
        assert method == "POST"
        assert body is not None
        return 201, {"status": "accepted", "order_id": body["order_id"]}, 0.001

    monkeypatch.setattr(validation, "request", fake_request)
    validation.run_workload()

    assert [record["request_index"] for record in validation.workload_records] == [1, 2, 3]
    assert all(validation.run_id in record["order_id"] for record in validation.workload_records)
    payload = json.loads(validation.workload_file.read_text(encoding="utf-8"))
    assert payload["workload_id"] == phase4.WORKLOAD_ID
    assert len(payload["requests"]) == 3


def test_capture_otel_observation_requires_exact_structured_event_parity(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validation = make_validation(tmp_path)
    validation.run_dir.mkdir(parents=True)
    validation.workload_records = [
        {"order_id": f"{validation.run_id}-order-001", "status": 201},
        {"order_id": f"{validation.run_id}-order-002", "status": 201},
        {"order_id": f"{validation.run_id}-order-003", "status": 201},
    ]
    validation.service_events = []
    spans = []
    for record in validation.workload_records:
        order_id = record["order_id"]
        for component, event_type in (
            ("order-api", "workload_request_received"),
            ("order-api", "dependency_request_started"),
            ("inventory", "dependency_request_received"),
            ("inventory", "dependency_request_succeeded"),
            ("order-api", "workload_request_succeeded"),
        ):
            trace_id = f"trace-{len(validation.service_events)}"
            span_id = f"span-{len(validation.service_events)}"
            validation.service_events.append(
                {
                    "run_id": validation.run_id,
                    "source_component": component,
                    "event_type": event_type,
                    "order_id": order_id,
                    "trace_id": trace_id,
                    "span_id": span_id,
                }
            )
            spans.append(
                {
                    "name": f"orderflow.{event_type}",
                    "trace_id": "otel-trace",
                    "span_id": "otel-span",
                    "parent_span_id": "",
                    "resource": {"service.name": f"orderflow-{component}"},
                    "attributes": {
                        "orderflow.run_id": validation.run_id,
                        "orderflow.source_component": component,
                        "orderflow.event_type": event_type,
                        "orderflow.order_id": order_id,
                        "orderflow.trace_id": trace_id,
                        "orderflow.span_id": span_id,
                    },
                }
            )

    monkeypatch.setattr(
        validation,
        "request",
        lambda *args, **kwargs: (
            200,
            {
                "payloads_base64": ["cGF5bG9hZA=="],
                "raw_payloads_base64": ["cmF3"],
                "content_encodings": ["identity"],
            },
            0.001,
        ),
    )
    monkeypatch.setattr(validation, "decode_otel_spans", lambda payloads: spans)

    validation.capture_otel_observation()

    assert len(validation.otel_spans) == 15
    assert validation.events[-1]["event_type"] == "otel_observation_verified"
    result = json.loads(validation.otel_span_file.read_text(encoding="utf-8"))
    assert result["signatures_match_structured_events"] is True
    assert set(result["component_span_counts"]) == {"inventory", "order-api"}


def test_verify_source_tree_clean_records_committed_source_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validation = make_validation(tmp_path)
    validation.run_dir.mkdir(parents=True)

    def fake_run(args: list[str], check: bool = True) -> Any:
        if args[:2] == ["git", "diff"]:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if args == ["git", "rev-parse", "HEAD"]:
            return SimpleNamespace(returncode=0, stdout="abc123\n", stderr="")
        raise AssertionError(args)

    monkeypatch.setattr(phase4, "run_command", fake_run)
    validation.verify_source_tree_clean()

    event = validation.events[-1]
    assert event["event_type"] == "source_tree_verified"
    assert event["repository_commit_sha"] == "abc123"
    assert event["tracked_changes"] is False


def test_verify_source_tree_clean_rejects_modified_tracked_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validation = make_validation(tmp_path)

    def fake_run(args: list[str], check: bool = True) -> Any:
        if args == ["git", "diff", "--quiet"]:
            return SimpleNamespace(returncode=1, stdout="", stderr="")
        if args == ["git", "diff", "--cached", "--quiet"]:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        raise AssertionError(args)

    monkeypatch.setattr(phase4, "run_command", fake_run)
    with pytest.raises(RuntimeError, match="tracked or staged repository changes"):
        validation.verify_source_tree_clean()


def test_execute_refuses_existing_run_directory(tmp_path: Path) -> None:
    validation = make_validation(tmp_path)
    validation.run_dir.mkdir(parents=True)
    with pytest.raises(RuntimeError, match="refusing to reuse existing output directory"):
        validation.execute()
