#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
if [[ -z "${PYTHON_BIN:-}" ]]; then
  if [[ -x "${REPO_ROOT}/.venv/bin/python" ]]; then
    PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
  else
    PYTHON_BIN="$(command -v python3 || command -v python || true)"
  fi
fi

usage() {
  printf '%s\n' 'Usage: scripts/run-quality-checks.sh [--python-only] [--strict-infrastructure]'
}

python_only=false
strict_infrastructure=false
while (($# > 0)); do
  case "$1" in
    --python-only) python_only=true ;;
    --strict-infrastructure) strict_infrastructure=true ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

if [[ -z "${PYTHON_BIN}" || ! -x "${PYTHON_BIN}" ]]; then
  printf '%s\n' 'Python interpreter not found. Install Python or run scripts/bootstrap-quality.sh first.' >&2
  exit 1
fi

PYTHON_BIN_DIR="$(dirname -- "${PYTHON_BIN}")"
export PATH="${PYTHON_BIN_DIR}:${PATH}"

cd "${REPO_ROOT}"
RUN_ID="${QUALITY_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-$$}"
QUALITY_TEMP_ROOT="${REPO_ROOT}/tmp/quality"
PYTEST_BASE_TEMP="${QUALITY_TEMP_ROOT}/pytest-${RUN_ID}"
PIP_AUDIT_CACHE="${QUALITY_TEMP_ROOT}/pip-audit-cache-${RUN_ID}"
mkdir -p "${PYTEST_BASE_TEMP}" "${PIP_AUDIT_CACHE}"
"${PYTHON_BIN}" -m ruff check analysis experiments system tests
"${PYTHON_BIN}" -m ruff format --check analysis experiments system tests
"${PYTHON_BIN}" -m mypy analysis experiments system tests
"${PYTHON_BIN}" -m pytest --basetemp "${PYTEST_BASE_TEMP}" --cov=experiments.harness.fit_probe --cov=experiments.harness.kubernetes_fit_probe --cov=system.orderflow.service --cov-branch --cov-report=term-missing --cov-fail-under=100
"${PYTHON_BIN}" -m bandit -q -r analysis experiments system -s B310,B404,B603,B607
"${PYTHON_BIN}" -m pip_audit --cache-dir "${PIP_AUDIT_CACHE}"
bash scripts/check-compliance.sh

if [[ "${python_only}" == false ]]; then
  if [[ "${strict_infrastructure}" == true ]]; then
    bash scripts/validate-infrastructure.sh --strict
  else
    bash scripts/validate-infrastructure.sh
  fi
  bash scripts/run-cloc.sh
fi

printf '%s\n' 'Quality checks passed.'
