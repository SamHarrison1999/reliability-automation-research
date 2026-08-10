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
        ("clean_state_verified", {"stage": "before_deploy", "namespace_present": False}),
        ("deployment_completed", {}),
        ("readiness_verified", {}),
        ("version_verified", {}),
        ("workload_completed", {}),
        ("observation_verified", {}),
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

    assert set(validation.image_records) == {"inventory", "order-api"}
    assert validation.image_records["inventory"]["image_id"] == "sha256:example"
    build_calls = [call for call in calls if call[:2] == ["docker", "build"]]
    assert len(build_calls) == 2
    assert all("--pull=false" in call for call in build_calls)
    assert all("linux/amd64" in call for call in build_calls)


def test_run_workload_uses_deterministic_order_identity(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    validation = make_validation(tmp_path)
    validation.run_dir.mkdir(parents=True)

    def fake_request(port: int, path: str, method: str = "GET", body: dict[str, Any] | None = None) -> Any:
        assert port == phase4.ORDER_PORT
        assert path == "/orders"
        assert method == "POST"
        return 201, {"status": "accepted", "order_id": body["order_id"]}, 0.001

    monkeypatch.setattr(validation, "request", fake_request)
    validation.run_workload()

    assert [record["request_index"] for record in validation.workload_records] == [1, 2, 3]
    assert all(validation.run_id in record["order_id"] for record in validation.workload_records)
    payload = json.loads(validation.workload_file.read_text(encoding="utf-8"))
    assert payload["workload_id"] == phase4.WORKLOAD_ID
    assert len(payload["requests"]) == 3


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
