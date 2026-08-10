"""Build the deterministic Phase 5 primary processed dataset.

This post-collection tool:

* reads raw empirical evidence from an immutable Git commit;
* preserves all 53 attempts in a corpus index;
* selects exactly one valid resolving attempt for each of 50 planned slots;
* derives observations using the frozen primary metric derivation tool;
* emits deterministic JSON;
* records cryptographic provenance;
* performs no inferential or comparative analysis.

The raw corpus is never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

TOOL_VERSION = "phase-5-primary-dataset-builder-v1.0"

EXPECTED_BATCH_ID = "phase5-primary-16f9cefff0d6b017"
EXPECTED_ATTEMPTS = 53
EXPECTED_PRIMARY_ATTEMPTS = 50
EXPECTED_RESERVE_ATTEMPTS = 3
EXPECTED_VALID_ATTEMPTS = 50
EXPECTED_INVALID_ATTEMPTS = 3
EXPECTED_PLANNED_SLOTS = 50

RAW_ROOT = "results/phase-5/raw"
PRIMARY_METRIC_TOOL = "analysis/phase_5/phase_5_primary_metrics.py"

CORE_FILES = {
    "events.jsonl",
    "metadata.json",
    "service-events.jsonl",
    "trial-manifest.json",
    "validity.json",
    "workload.json",
}

OTEL_FILES = {
    "otel-payloads.json",
    "otel-spans.json",
}

VALID_FILE_SET = CORE_FILES | OTEL_FILES
INVALID_FILE_SET = CORE_FILES

EXPECTED_CELL_COUNTS = {
    "no-fault-v1|control": 10,
    "service-termination-v1|manual": 10,
    "service-termination-v1|automated": 10,
    "dependency-latency-v1|manual": 10,
    "dependency-latency-v1|automated": 10,
}


def run_git(
    repo: Path,
    *args: str,
    binary: bool = False,
) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    if binary:
        return result.stdout

    return result.stdout.decode("utf-8").strip()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> str:
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return sha256_bytes(payload)


def parse_ls_tree(repo: Path, commit: str) -> dict[str, str]:
    output = run_git(
        repo,
        "ls-tree",
        "-r",
        commit,
        "--",
        RAW_ROOT,
    )

    assert isinstance(output, str)

    entries: dict[str, str] = {}

    if not output:
        return entries

    for line in output.splitlines():
        metadata, path = line.split("\t", 1)
        _mode, object_type, blob_sha = metadata.split(" ", 2)

        if object_type != "blob":
            continue

        entries[path] = blob_sha

    return entries


def git_blob_bytes(repo: Path, commit: str, path: str) -> bytes:
    value = run_git(
        repo,
        "show",
        f"{commit}:{path}",
        binary=True,
    )

    assert isinstance(value, bytes)
    return value


def git_blob_sha(repo: Path, commit: str, path: str) -> str:
    value = run_git(
        repo,
        "rev-parse",
        f"{commit}:{path}",
    )

    assert isinstance(value, str)
    return value


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")

    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def derive_observation(
    repo: Path,
    trial_dir: Path,
    output_path: Path,
) -> dict[str, Any]:
    subprocess.run(
        [
            sys.executable,
            str(repo / PRIMARY_METRIC_TOOL),
            "--trial-dir",
            str(trial_dir),
            "--output",
            str(output_path),
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.DEVNULL,
    )

    return read_json(output_path)


def build_attempt_index(
    repo: Path,
    raw_commit: str,
    extraction_root: Path,
) -> list[dict[str, Any]]:
    tree = parse_ls_tree(repo, raw_commit)

    grouped: dict[str, list[str]] = {}

    for path in sorted(tree):
        relative = Path(path)

        require(
            len(relative.parts) == 5,
            f"unexpected raw evidence path: {path}",
        )

        trial_directory = relative.parts[3]
        grouped.setdefault(trial_directory, []).append(path)

    require(
        len(grouped) == EXPECTED_ATTEMPTS,
        f"expected {EXPECTED_ATTEMPTS} trial directories; "
        f"found {len(grouped)}",
    )

    attempts: list[dict[str, Any]] = []

    for trial_directory, paths in grouped.items():
        local_dir = extraction_root / trial_directory
        local_dir.mkdir(parents=True, exist_ok=False)

        file_records: list[dict[str, str]] = []

        for path in sorted(paths):
            filename = Path(path).name
            payload = git_blob_bytes(repo, raw_commit, path)

            (local_dir / filename).write_bytes(payload)

            file_records.append(
                {
                    "path": path,
                    "filename": filename,
                    "git_blob_sha": tree[path],
                    "sha256": sha256_bytes(payload),
                }
            )

        manifest = read_json(local_dir / "trial-manifest.json")
        validity = read_json(local_dir / "validity.json")

        actual_files = {record["filename"] for record in file_records}
        passed = bool(validity.get("passed"))

        expected_files = (
            VALID_FILE_SET if passed else INVALID_FILE_SET
        )

        require(
            actual_files == expected_files,
            "unexpected evidence file set for "
            f"{trial_directory}: {sorted(actual_files)}",
        )

        classification = str(validity.get("classification"))

        if passed:
            require(
                classification == "valid-primary-pilot-trial",
                f"unexpected valid classification: {trial_directory}",
            )
        else:
            require(
                classification == "invalid-primary-pilot-trial",
                f"unexpected invalid classification: {trial_directory}",
            )

        reserve_ordinal = manifest.get("reserve_ordinal")

        attempt = {
            "trial_id": str(manifest["trial_id"]),
            "directory": trial_directory,
            "primary_schedule_slot": int(
                manifest["primary_schedule_slot"]
            ),
            "run_order": int(manifest["run_order"]),
            "repetition": int(manifest["repetition"]),
            "scenario_id": str(manifest["scenario_id"]),
            "automation_condition": str(
                manifest["automation_condition"]
            ),
            "reserve": bool(manifest["reserve"]),
            "reserve_ordinal": (
                int(reserve_ordinal)
                if reserve_ordinal is not None
                else None
            ),
            "pilot_batch_id": str(manifest["pilot_batch_id"]),
            "passed": passed,
            "classification": classification,
            "files": file_records,
            "_local_dir": local_dir,
        }

        attempts.append(attempt)

    attempts.sort(key=lambda item: item["run_order"])
    return attempts


def validate_attempt_corpus(
    attempts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    require(
        len(attempts) == EXPECTED_ATTEMPTS,
        "unexpected attempt count",
    )

    require(
        [item["run_order"] for item in attempts]
        == list(range(1, EXPECTED_ATTEMPTS + 1)),
        "run-order sequence is not exactly 1..53",
    )

    require(
        {item["pilot_batch_id"] for item in attempts}
        == {EXPECTED_BATCH_ID},
        "pilot batch identity mismatch",
    )

    primary = [item for item in attempts if not item["reserve"]]
    reserves = [item for item in attempts if item["reserve"]]
    valid = [item for item in attempts if item["passed"]]
    invalid = [item for item in attempts if not item["passed"]]

    require(
        len(primary) == EXPECTED_PRIMARY_ATTEMPTS,
        "unexpected primary attempt count",
    )
    require(
        len(reserves) == EXPECTED_RESERVE_ATTEMPTS,
        "unexpected reserve attempt count",
    )
    require(
        len(valid) == EXPECTED_VALID_ATTEMPTS,
        "unexpected valid attempt count",
    )
    require(
        len(invalid) == EXPECTED_INVALID_ATTEMPTS,
        "unexpected invalid attempt count",
    )

    require(
        [item["run_order"] for item in invalid] == [19, 21, 22],
        "unexpected invalid attempt lineage",
    )

    require(
        [item["run_order"] for item in reserves] == [20, 22, 23],
        "unexpected reserve attempt lineage",
    )

    resolved: list[dict[str, Any]] = []

    for slot in range(1, EXPECTED_PLANNED_SLOTS + 1):
        slot_attempts = [
            item
            for item in attempts
            if item["primary_schedule_slot"] == slot
        ]

        slot_primary = [
            item for item in slot_attempts if not item["reserve"]
        ]
        slot_valid = [
            item for item in slot_attempts if item["passed"]
        ]

        require(
            len(slot_primary) == 1,
            f"slot {slot} does not contain one primary attempt",
        )
        require(
            len(slot_valid) == 1,
            f"slot {slot} does not contain one resolving attempt",
        )
        require(
            slot_attempts[-1]["passed"],
            f"final attempt for slot {slot} is invalid",
        )

        resolved.append(slot_valid[0])

    resolved.sort(key=lambda item: item["primary_schedule_slot"])

    cell_counts = Counter(
        f'{item["scenario_id"]}|{item["automation_condition"]}'
        for item in resolved
    )

    require(
        dict(cell_counts) == EXPECTED_CELL_COUNTS,
        f"unexpected resolved cell balance: {dict(cell_counts)}",
    )

    for cell in EXPECTED_CELL_COUNTS:
        scenario, condition = cell.split("|", 1)

        repetitions = sorted(
            item["repetition"]
            for item in resolved
            if item["scenario_id"] == scenario
            and item["automation_condition"] == condition
        )

        require(
            repetitions == list(range(1, 11)),
            f"unexpected repetition sequence for {cell}",
        )

    return resolved


def serialisable_attempt(
    attempt: dict[str, Any],
    selected_run_orders: set[int],
) -> dict[str, Any]:
    return {
        key: value
        for key, value in attempt.items()
        if key != "_local_dir"
    } | {
        "selected_for_primary_dataset": (
            attempt["run_order"] in selected_run_orders
        )
    }


def build_dataset(
    repo: Path,
    raw_commit: str,
    tooling_commit: str,
    output_dir: Path,
) -> dict[str, str]:
    raw_commit_resolved = str(
        run_git(repo, "rev-parse", raw_commit)
    )
    tooling_commit_resolved = str(
        run_git(repo, "rev-parse", tooling_commit)
    )

    current_metric_blob = git_blob_sha(
        repo,
        tooling_commit_resolved,
        PRIMARY_METRIC_TOOL,
    )

    raw_anchor_metric_blob = git_blob_sha(
        repo,
        raw_commit_resolved,
        PRIMARY_METRIC_TOOL,
    )

    require(
        current_metric_blob == raw_anchor_metric_blob,
        "primary metric derivation tool changed after raw-corpus anchor",
    )

    dataset_tool_path = (
        "analysis/phase_5/phase_5_primary_dataset.py"
    )

    dataset_tool_blob = git_blob_sha(
        repo,
        tooling_commit_resolved,
        dataset_tool_path,
    )

    batch_manifest_path = (
        "experiments/manifests/phase-5-primary-batch.json"
    )

    batch_manifest_blob = git_blob_sha(
        repo,
        raw_commit_resolved,
        batch_manifest_path,
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="phase5-primary-dataset-"
    ) as temporary:
        temporary_root = Path(temporary)
        extraction_root = temporary_root / "raw"
        derivation_root = temporary_root / "derived"

        extraction_root.mkdir()
        derivation_root.mkdir()

        attempts = build_attempt_index(
            repo,
            raw_commit_resolved,
            extraction_root,
        )

        resolved = validate_attempt_corpus(attempts)

        observations_by_run: dict[int, dict[str, Any]] = {}

        for attempt in attempts:
            output = derivation_root / (
                f'run-{attempt["run_order"]:03d}.json'
            )

            observation = derive_observation(
                repo,
                attempt["_local_dir"],
                output,
            )

            require(
                observation.get(
                    "eligible_for_primary_pilot_analysis"
                )
                is True,
                "structurally ineligible attempt at run order "
                f'{attempt["run_order"]}',
            )

            quality = observation["measurement_quality"]

            require(
                bool(quality["trial_valid"])
                == bool(attempt["passed"]),
                "trial-validity disagreement at run order "
                f'{attempt["run_order"]}',
            )

            require(
                quality["utc_fallback_permitted"] is False,
                "UTC fallback unexpectedly permitted at run order "
                f'{attempt["run_order"]}',
            )

            observations_by_run[
                attempt["run_order"]
            ] = observation

        selected_run_orders = {
            item["run_order"] for item in resolved
        }

        selected_observations = [
            observations_by_run[item["run_order"]]
            for item in resolved
        ]

        require(
            len(selected_observations)
            == EXPECTED_PLANNED_SLOTS,
            "unexpected selected observation count",
        )

        corpus_index = {
            "schema_version": "1.0.0",
            "tool_version": TOOL_VERSION,
            "pilot_batch_id": EXPECTED_BATCH_ID,
            "raw_corpus_commit": raw_commit_resolved,
            "attempt_count": len(attempts),
            "selection_rule": (
                "exactly-one-valid-resolving-attempt-per-planned-slot"
            ),
            "attempts": [
                serialisable_attempt(
                    attempt,
                    selected_run_orders,
                )
                for attempt in attempts
            ],
        }

        observations_document = {
            "schema_version": "1.0.0",
            "tool_version": TOOL_VERSION,
            "pilot_batch_id": EXPECTED_BATCH_ID,
            "raw_corpus_commit": raw_commit_resolved,
            "observation_count": len(selected_observations),
            "ordering": "primary_schedule_slot-ascending",
            "observations": selected_observations,
        }

        cell_counts = Counter(
            f'{item["scenario_id"]}|'
            f'{item["automation_condition"]}'
            for item in resolved
        )

        summary_document = {
            "schema_version": "1.0.0",
            "tool_version": TOOL_VERSION,
            "pilot_batch_id": EXPECTED_BATCH_ID,
            "raw_corpus_commit": raw_commit_resolved,
            "attempt_count": len(attempts),
            "primary_attempt_count": sum(
                not item["reserve"] for item in attempts
            ),
            "reserve_attempt_count": sum(
                item["reserve"] for item in attempts
            ),
            "valid_attempt_count": sum(
                item["passed"] for item in attempts
            ),
            "invalid_attempt_count": sum(
                not item["passed"] for item in attempts
            ),
            "resolved_planned_slot_count": len(resolved),
            "invalid_run_orders": [
                item["run_order"]
                for item in attempts
                if not item["passed"]
            ],
            "reserve_run_orders": [
                item["run_order"]
                for item in attempts
                if item["reserve"]
            ],
            "resolved_design_cells": dict(
                sorted(cell_counts.items())
            ),
            "substantive_metric_summary_included": False,
        }

        corpus_hash = write_json(
            output_dir / "corpus-index.json",
            corpus_index,
        )

        observations_hash = write_json(
            output_dir / "observations.json",
            observations_document,
        )

        summary_hash = write_json(
            output_dir / "summary.json",
            summary_document,
        )

        provenance_document = {
            "schema_version": "1.0.0",
            "tool_version": TOOL_VERSION,
            "pilot_batch_id": EXPECTED_BATCH_ID,
            "raw_corpus_commit": raw_commit_resolved,
            "tooling_commit": tooling_commit_resolved,
            "primary_metric_tool": {
                "path": PRIMARY_METRIC_TOOL,
                "git_blob_sha": current_metric_blob,
                "unchanged_from_raw_corpus_anchor": True,
            },
            "primary_dataset_tool": {
                "path": dataset_tool_path,
                "git_blob_sha": dataset_tool_blob,
            },
            "primary_batch_manifest": {
                "path": batch_manifest_path,
                "git_blob_sha": batch_manifest_blob,
            },
            "input_policy": (
                "raw-bytes-read-from-immutable-git-corpus-commit"
            ),
            "selection_policy": (
                "one-valid-resolving-attempt-per-primary-schedule-slot"
            ),
            "ordering": "primary_schedule_slot-ascending",
            "output_sha256": {
                "corpus-index.json": corpus_hash,
                "observations.json": observations_hash,
                "summary.json": summary_hash,
            },
            "utc_fallback_permitted": False,
            "opentelemetry_primary_timing": False,
            "substantive_analysis_performed": False,
        }

        provenance_hash = write_json(
            output_dir / "provenance.json",
            provenance_document,
        )

    return {
        "corpus-index.json": corpus_hash,
        "observations.json": observations_hash,
        "provenance.json": provenance_hash,
        "summary.json": summary_hash,
    }


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--raw-corpus-commit",
        required=True,
    )

    parser.add_argument(
        "--tooling-commit",
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
    )

    args = parser.parse_args()

    repo_value = run_git(
        Path.cwd(),
        "rev-parse",
        "--show-toplevel",
    )

    assert isinstance(repo_value, str)
    repo = Path(repo_value)

    output_dir = args.output_dir

    if not output_dir.is_absolute():
        output_dir = repo / output_dir

    hashes = build_dataset(
        repo=repo,
        raw_commit=args.raw_corpus_commit,
        tooling_commit=args.tooling_commit,
        output_dir=output_dir,
    )

    print(
        json.dumps(
            {
                "tool_version": TOOL_VERSION,
                "pilot_batch_id": EXPECTED_BATCH_ID,
                "raw_corpus_commit": str(
                    run_git(
                        repo,
                        "rev-parse",
                        args.raw_corpus_commit,
                    )
                ),
                "attempt_count": EXPECTED_ATTEMPTS,
                "resolved_observation_count":
                    EXPECTED_PLANNED_SLOTS,
                "substantive_analysis_performed": False,
                "output_sha256": hashes,
            },
            indent=2,
            sort_keys=True,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())