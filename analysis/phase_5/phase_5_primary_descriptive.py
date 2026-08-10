"""Deterministic descriptive analysis for the Phase 5 primary pilot.

The analysis is intentionally descriptive. It performs no NHST,
p-values, confidence intervals, statistical-significance testing,
human-effect analysis, production-readiness assessment, or universal
causal inference.

Input is read directly from the immutable processed-dataset Git commit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

TOOL_VERSION = "phase-5-primary-descriptive-analysis-v1.0"

EXPECTED_DATASET_COMMIT = (
    "be3119d44842a8b737a86e0f40dca37b3aa4dbf7"
)
EXPECTED_RAW_COMMIT = (
    "b832c96c1dd3665f6025394447b35db58cd0e2a9"
)
EXPECTED_DATASET_TOOLING_COMMIT = (
    "77d8a65fa4bd672d54865b7cc71980c5f0357d72"
)

CORPUS_PATH = (
    "data/processed/phase-5/primary/corpus-index.json"
)
OBSERVATIONS_PATH = (
    "data/processed/phase-5/primary/observations.json"
)
PROVENANCE_PATH = (
    "data/processed/phase-5/primary/provenance.json"
)
SUMMARY_PATH = (
    "data/processed/phase-5/primary/summary.json"
)

EXPECTED_DATASET_HASHES = {
    CORPUS_PATH:
        "ed3c39c41fe7a21b8d1142ae4e4367c9a79094b7b38eb3c398577181a2fc3bad",
    OBSERVATIONS_PATH:
        "ff63303abb89c8d6ccc8f059a8bceca4f54039641d1cf1382663838ffe85dedb",
    PROVENANCE_PATH:
        "d42fbaea197abcd582a32814bdefc2689d52d47a452b3eea81d2423f27f0c657",
    SUMMARY_PATH:
        "be44fb5d84a4c15f938daf636ee88b3823b4c4b0311aec4bc325afdcf4a90860",
}

EXPECTED_CELL_COUNTS = {
    "no-fault-v1|control": 10,
    "service-termination-v1|manual": 10,
    "service-termination-v1|automated": 10,
    "dependency-latency-v1|manual": 10,
    "dependency-latency-v1|automated": 10,
}

PRIMARY_METRIC_ROLES = {
    "detection_latency_ms":
        "shared-detector-fidelity-and-balance-check",
    "recovery_time_ms":
        "treatment-relevant-technical-outcome",
    "failure_impact_rate":
        "treatment-relevant-technical-outcome",
}

NUMERIC_SECONDARY_METRICS = (
    "active_recovery_duration_ms",
    "automation_decision_count",
    "failed_requests_count",
    "latency_inflation_ratio",
    "manual_intervention_count",
    "time_to_first_post_recovery_success_ms",
)

BOOLEAN_SECONDARY_METRICS = (
    "recovery_success",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


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


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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


def git_blob_bytes(
    repo: Path,
    commit: str,
    path: str,
) -> bytes:
    value = run_git(
        repo,
        "show",
        f"{commit}:{path}",
        binary=True,
    )

    assert isinstance(value, bytes)
    return value


def git_blob_sha(
    repo: Path,
    commit: str,
    path: str,
) -> str:
    value = run_git(
        repo,
        "rev-parse",
        f"{commit}:{path}",
    )

    assert isinstance(value, str)
    return value


def parse_json_bytes(payload: bytes) -> dict[str, Any]:
    value = json.loads(payload.decode("utf-8"))

    if not isinstance(value, dict):
        raise ValueError("expected JSON object")

    return value


def rounded(value: float) -> float:
    result = round(float(value), 6)

    if result == 0:
        return 0.0

    return result


def quantile_type7(
    values: list[float],
    probability: float,
) -> float:
    """Return the Hyndman-Fan/R type-7 sample quantile."""

    require(bool(values), "quantile requires at least one value")
    require(
        0.0 <= probability <= 1.0,
        "probability must be between zero and one",
    )

    ordered = sorted(float(value) for value in values)

    if len(ordered) == 1:
        return ordered[0]

    h = (len(ordered) - 1) * probability
    lower = math.floor(h)
    upper = math.ceil(h)

    if lower == upper:
        return ordered[lower]

    fraction = h - lower

    return (
        ordered[lower]
        + fraction * (ordered[upper] - ordered[lower])
    )


def describe_numeric(
    values: list[float],
) -> dict[str, int | float]:
    require(bool(values), "descriptive summary requires values")

    numeric = [float(value) for value in values]

    return {
        "n": len(numeric),
        "mean": rounded(sum(numeric) / len(numeric)),
        "median": rounded(quantile_type7(numeric, 0.50)),
        "p25": rounded(quantile_type7(numeric, 0.25)),
        "p75": rounded(quantile_type7(numeric, 0.75)),
        "p95": rounded(quantile_type7(numeric, 0.95)),
        "min": rounded(min(numeric)),
        "max": rounded(max(numeric)),
    }


def status_counts(
    observations: list[dict[str, Any]],
    section: str,
    metric: str,
) -> dict[str, int]:
    counts = Counter(
        str(observation[section][metric]["status"])
        for observation in observations
    )

    return dict(sorted(counts.items()))


def numeric_metric_summary(
    observations: list[dict[str, Any]],
    section: str,
    metric: str,
) -> dict[str, Any]:
    statuses = status_counts(
        observations,
        section,
        metric,
    )

    observed_values: list[float] = []

    for observation in observations:
        value = observation[section][metric]

        if value["status"] != "observed":
            continue

        metric_value = value["value"]

        require(
            isinstance(metric_value, (int, float))
            and not isinstance(metric_value, bool),
            f"{section}.{metric} observed value is not numeric",
        )

        observed_values.append(float(metric_value))

    result: dict[str, Any] = {
        "status_counts": statuses,
    }

    if observed_values:
        result["observed"] = describe_numeric(observed_values)

    return result


def boolean_metric_summary(
    observations: list[dict[str, Any]],
    section: str,
    metric: str,
) -> dict[str, Any]:
    statuses = status_counts(
        observations,
        section,
        metric,
    )

    true_count = 0
    false_count = 0

    for observation in observations:
        value = observation[section][metric]

        if value["status"] != "observed":
            continue

        metric_value = value["value"]

        require(
            isinstance(metric_value, bool),
            f"{section}.{metric} observed value is not boolean",
        )

        if metric_value:
            true_count += 1
        else:
            false_count += 1

    return {
        "status_counts": statuses,
        "observed_boolean_counts": {
            "false": false_count,
            "true": true_count,
        },
    }


def cell_key(observation: dict[str, Any]) -> str:
    return (
        f'{observation["scenario_id"]}|'
        f'{observation["automation_condition"]}'
    )


def build_cell_summary(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    repetitions = sorted(
        int(observation["repetition"])
        for observation in observations
    )

    require(
        repetitions == list(range(1, 11)),
        "cell repetition sequence is not exactly 1..10",
    )

    primary = {
        metric: {
            "role": PRIMARY_METRIC_ROLES[metric],
            **numeric_metric_summary(
                observations,
                "primary_metrics",
                metric,
            ),
        }
        for metric in PRIMARY_METRIC_ROLES
    }

    secondary: dict[str, Any] = {}

    for metric in NUMERIC_SECONDARY_METRICS:
        secondary[metric] = numeric_metric_summary(
            observations,
            "secondary_metrics",
            metric,
        )

    for metric in BOOLEAN_SECONDARY_METRICS:
        secondary[metric] = boolean_metric_summary(
            observations,
            "secondary_metrics",
            metric,
        )

    return {
        "n": len(observations),
        "repetitions": repetitions,
        "primary_metrics": primary,
        "secondary_metrics": secondary,
    }


def paired_primary_metric(
    observations: list[dict[str, Any]],
    metric: str,
) -> dict[str, Any]:
    manual = {
        int(observation["repetition"]): observation
        for observation in observations
        if observation["automation_condition"] == "manual"
    }

    automated = {
        int(observation["repetition"]): observation
        for observation in observations
        if observation["automation_condition"] == "automated"
    }

    require(
        sorted(manual) == list(range(1, 11)),
        "manual comparison repetitions are not 1..10",
    )
    require(
        sorted(automated) == list(range(1, 11)),
        "automated comparison repetitions are not 1..10",
    )

    manual_values: list[float] = []
    automated_values: list[float] = []
    differences: list[float] = []

    lower = 0
    equal = 0
    higher = 0

    for repetition in range(1, 11):
        manual_metric = manual[repetition]["primary_metrics"][metric]
        automated_metric = automated[repetition]["primary_metrics"][metric]

        require(
            manual_metric["status"] == "observed",
            f"manual {metric} is not observed",
        )
        require(
            automated_metric["status"] == "observed",
            f"automated {metric} is not observed",
        )

        manual_value = float(manual_metric["value"])
        automated_value = float(automated_metric["value"])
        difference = automated_value - manual_value

        manual_values.append(manual_value)
        automated_values.append(automated_value)
        differences.append(difference)

        if difference < 0:
            lower += 1
        elif difference > 0:
            higher += 1
        else:
            equal += 1

    return {
        "role": PRIMARY_METRIC_ROLES[metric],
        "pairing": "same-repetition",
        "pair_count": 10,
        "difference_definition": "automated-minus-manual",
        "manual": describe_numeric(manual_values),
        "automated": describe_numeric(automated_values),
        "paired_difference": describe_numeric(differences),
        "direction_counts": {
            "automated_lower": lower,
            "equal": equal,
            "automated_higher": higher,
        },
    }


def execution_stability(
    corpus: dict[str, Any],
    summary: dict[str, Any],
) -> dict[str, Any]:
    attempts = list(corpus["attempts"])

    by_cell: dict[str, Any] = {}

    grouped: dict[str, list[dict[str, Any]]] = {}

    for attempt in attempts:
        key = (
            f'{attempt["scenario_id"]}|'
            f'{attempt["automation_condition"]}'
        )
        grouped.setdefault(key, []).append(attempt)

    for key in sorted(grouped):
        cell_attempts = grouped[key]
        attempt_count = len(cell_attempts)
        invalid_count = sum(
            not bool(attempt["passed"])
            for attempt in cell_attempts
        )

        by_cell[key] = {
            "attempt_count": attempt_count,
            "primary_attempt_count": sum(
                not bool(attempt["reserve"])
                for attempt in cell_attempts
            ),
            "reserve_attempt_count": sum(
                bool(attempt["reserve"])
                for attempt in cell_attempts
            ),
            "valid_attempt_count": sum(
                bool(attempt["passed"])
                for attempt in cell_attempts
            ),
            "invalid_attempt_count": invalid_count,
            "invalid_attempt_fraction": rounded(
                invalid_count / attempt_count
            ),
        }

    return {
        "overall": {
            "attempt_count": int(summary["attempt_count"]),
            "primary_attempt_count": int(
                summary["primary_attempt_count"]
            ),
            "reserve_attempt_count": int(
                summary["reserve_attempt_count"]
            ),
            "valid_attempt_count": int(
                summary["valid_attempt_count"]
            ),
            "invalid_attempt_count": int(
                summary["invalid_attempt_count"]
            ),
            "resolved_planned_slot_count": int(
                summary["resolved_planned_slot_count"]
            ),
            "invalid_run_orders": list(
                summary["invalid_run_orders"]
            ),
            "reserve_run_orders": list(
                summary["reserve_run_orders"]
            ),
        },
        "by_design_cell": by_cell,
        "interpretation": (
            "execution-stability-descriptor-only;"
            "invalid-attempts-excluded-from-valid-metric-summaries"
        ),
    }


def load_and_validate_dataset(
    repo: Path,
    dataset_commit: str,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    resolved = run_git(
        repo,
        "rev-parse",
        dataset_commit,
    )
    assert isinstance(resolved, str)

    require(
        resolved == EXPECTED_DATASET_COMMIT,
        "unexpected processed-dataset commit",
    )

    documents: dict[str, dict[str, Any]] = {}

    for path, expected_hash in EXPECTED_DATASET_HASHES.items():
        payload = git_blob_bytes(
            repo,
            resolved,
            path,
        )

        require(
            sha256_bytes(payload) == expected_hash,
            f"processed-dataset hash mismatch: {path}",
        )

        documents[path] = parse_json_bytes(payload)

    corpus = documents[CORPUS_PATH]
    observations_document = documents[OBSERVATIONS_PATH]
    provenance = documents[PROVENANCE_PATH]
    summary = documents[SUMMARY_PATH]

    require(
        int(corpus["attempt_count"]) == 53,
        "unexpected corpus attempt count",
    )
    require(
        int(observations_document["observation_count"]) == 50,
        "unexpected observation count",
    )

    require(
        provenance["raw_corpus_commit"] == EXPECTED_RAW_COMMIT,
        "unexpected raw-corpus provenance",
    )
    require(
        provenance["tooling_commit"]
        == EXPECTED_DATASET_TOOLING_COMMIT,
        "unexpected dataset-tooling provenance",
    )
    require(
        provenance["utc_fallback_permitted"] is False,
        "UTC fallback unexpectedly permitted",
    )
    require(
        provenance["opentelemetry_primary_timing"] is False,
        "OpenTelemetry unexpectedly used as primary timing",
    )

    require(
        list(summary["invalid_run_orders"]) == [19, 21, 22],
        "unexpected invalid-run lineage",
    )
    require(
        list(summary["reserve_run_orders"]) == [20, 22, 23],
        "unexpected reserve-run lineage",
    )

    selected = [
        attempt
        for attempt in corpus["attempts"]
        if attempt["selected_for_primary_dataset"]
    ]

    require(
        len(selected) == 50,
        "unexpected selected-attempt count",
    )
    require(
        all(bool(attempt["passed"]) for attempt in selected),
        "invalid attempt selected into processed dataset",
    )

    return (
        corpus,
        observations_document,
        provenance,
        summary,
    )


def build_analysis(
    repo: Path,
    dataset_commit: str,
    tooling_commit: str,
) -> dict[str, Any]:
    resolved_tooling = run_git(
        repo,
        "rev-parse",
        tooling_commit,
    )
    assert isinstance(resolved_tooling, str)

    head = run_git(repo, "rev-parse", "HEAD")
    assert isinstance(head, str)

    require(
        head == resolved_tooling,
        "HEAD does not match descriptive-analysis tooling commit",
    )

    corpus, observations_document, provenance, summary = (
        load_and_validate_dataset(
            repo,
            dataset_commit,
        )
    )

    observations = list(observations_document["observations"])

    require(
        len(observations) == 50,
        "expected exactly 50 observations",
    )

    for observation in observations:
        require(
            observation["eligible_for_primary_pilot_analysis"]
            is True,
            "structurally ineligible observation",
        )
        require(
            observation["measurement_quality"]["trial_valid"]
            is True,
            "invalid observation in primary dataset",
        )
        require(
            observation["measurement_quality"][
                "primary_monotonic_completeness"
            ]
            == 1.0,
            "incomplete monotonic primary timing",
        )
        require(
            observation["measurement_quality"][
                "utc_fallback_permitted"
            ]
            is False,
            "UTC fallback found in selected observation",
        )

    counts = Counter(
        cell_key(observation)
        for observation in observations
    )

    require(
        dict(counts) == EXPECTED_CELL_COUNTS,
        "processed design-cell balance mismatch",
    )

    no_fault = [
        observation
        for observation in observations
        if observation["scenario_id"] == "no-fault-v1"
    ]

    fault = [
        observation
        for observation in observations
        if observation["scenario_id"] != "no-fault-v1"
    ]

    require(
        len(no_fault) == 10 and len(fault) == 40,
        "unexpected control/fault observation split",
    )

    for metric in PRIMARY_METRIC_ROLES:
        no_fault_statuses = Counter(
            observation["primary_metrics"][metric]["status"]
            for observation in no_fault
        )
        fault_statuses = Counter(
            observation["primary_metrics"][metric]["status"]
            for observation in fault
        )

        require(
            no_fault_statuses == {"not_applicable": 10},
            f"unexpected no-fault statuses for {metric}",
        )
        require(
            fault_statuses == {"observed": 40},
            f"unexpected fault statuses for {metric}",
        )

    cell_summaries: dict[str, Any] = {}

    for key in sorted(EXPECTED_CELL_COUNTS):
        cell_observations = [
            observation
            for observation in observations
            if cell_key(observation) == key
        ]

        cell_summaries[key] = build_cell_summary(
            cell_observations
        )

    scenario_comparisons: dict[str, Any] = {}

    for scenario in (
        "dependency-latency-v1",
        "service-termination-v1",
    ):
        scenario_observations = [
            observation
            for observation in observations
            if observation["scenario_id"] == scenario
        ]

        require(
            len(scenario_observations) == 20,
            f"unexpected comparison count for {scenario}",
        )

        scenario_comparisons[scenario] = {
            "pairing": "manual-versus-automated-by-repetition",
            "pair_count": 10,
            "primary_metrics": {
                metric: paired_primary_metric(
                    scenario_observations,
                    metric,
                )
                for metric in PRIMARY_METRIC_ROLES
            },
        }

    analysis_tool_path = (
        "analysis/phase_5/phase_5_primary_descriptive.py"
    )

    return {
        "schema_version": "1.0.0",
        "analysis_tool_version": TOOL_VERSION,
        "analysis_scope": "phase-5-technical-pilot-descriptive-only",
        "dataset": {
            "processed_dataset_commit": EXPECTED_DATASET_COMMIT,
            "raw_corpus_commit": EXPECTED_RAW_COMMIT,
            "dataset_tooling_commit":
                EXPECTED_DATASET_TOOLING_COMMIT,
            "processed_observation_count": 50,
            "dataset_artifact_sha256": {
                Path(path).name: digest
                for path, digest
                in sorted(EXPECTED_DATASET_HASHES.items())
            },
        },
        "provenance": {
            "descriptive_analysis_tooling_commit":
                resolved_tooling,
            "descriptive_analysis_tool_git_blob_sha":
                git_blob_sha(
                    repo,
                    resolved_tooling,
                    analysis_tool_path,
                ),
            "input_policy":
                "read-directly-from-immutable-processed-dataset-commit",
            "dataset_provenance_verified": True,
        },
        "claim_boundary": {
            "inferential_statistics_performed": False,
            "p_values_included": False,
            "nhst_performed": False,
            "statistical_significance_claims_permitted": False,
            "human_effect_claims_permitted": False,
            "production_readiness_claims_permitted": False,
            "universal_causal_claims_permitted": False,
            "detection_latency_interpretation":
                "shared-detector-fidelity-and-balance-check",
        },
        "collection_execution_stability": execution_stability(
            corpus,
            summary,
        ),
        "cell_summaries": cell_summaries,
        "scenario_comparisons": scenario_comparisons,
    }


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset-commit",
        required=True,
    )
    parser.add_argument(
        "--tooling-commit",
        required=True,
    )
    parser.add_argument(
        "--output",
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

    output = args.output
    if not output.is_absolute():
        output = repo / output

    analysis = build_analysis(
        repo,
        args.dataset_commit,
        args.tooling_commit,
    )

    payload = canonical_json_bytes(analysis)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output.write_bytes(payload)

    print(
        json.dumps(
            {
                "analysis_tool_version": TOOL_VERSION,
                "dataset_commit": EXPECTED_DATASET_COMMIT,
                "processed_observation_count": 50,
                "design_cell_count": 5,
                "paired_scenario_count": 2,
                "inferential_statistics_performed": False,
                "substantive_metrics_emitted_to_console": False,
                "output_sha256": sha256_bytes(payload),
            },
            indent=2,
            sort_keys=True,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())