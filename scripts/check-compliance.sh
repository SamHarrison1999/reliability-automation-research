#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

required=(
  pyproject.toml
  docs/engineering-quality.md
  docs/observability/opentelemetry.md
  ansible/README.md
  observability/opentelemetry/collector-config.yaml
  tests/test_fit_probe.py
  tests/test_service.py
  scripts/run-psscriptanalyzer.ps1
  PSScriptAnalyzerSettings.psd1
  .yamllint
)

missing=()
for path in "${required[@]}"; do
  [[ -f "${path}" ]] || missing+=("${path}")
done
if (( ${#missing[@]} > 0 )); then
  printf 'Compliance check missing required files:\n' >&2
  printf '  %s\n' "${missing[@]}" >&2
  exit 1
fi

if grep -R -I -n -E --exclude-dir=.git --exclude-dir=.venv --exclude-dir=tmp \
  '(password|secret|api[_-]?key|private[_-]?key)[[:space:]]*[:=][[:space:]]*[A-Za-z0-9]' \
  .github ansible observability experiments system scripts tests 2>/dev/null; then
  printf '%s\n' 'Compliance check found a possible hard-coded secret.' >&2
  exit 1
fi

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git diff --check
fi
printf '%s\n' 'Compliance checks passed.'
