#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${REPO_ROOT}/.venv"

usage() {
  printf '%s\n' 'Usage: scripts/bootstrap-quality.sh [--with-infrastructure]'
}

with_infrastructure=false
while (($# > 0)); do
  case "$1" in
    --with-infrastructure) with_infrastructure=true ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

"${PYTHON_BIN}" -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install -e "${REPO_ROOT}[dev]"

if [[ "${with_infrastructure}" == true ]]; then
  "${VENV_DIR}/bin/python" -m pip install -e "${REPO_ROOT}[infrastructure]"
  if command -v pwsh >/dev/null 2>&1; then
    pwsh -NoLogo -NoProfile -Command \
      'if (-not (Get-Module -ListAvailable -Name PSScriptAnalyzer)) { Install-Module -Name PSScriptAnalyzer -Scope CurrentUser -Force -AllowClobber }'
  else
    printf '%s\n' 'Warning: pwsh is unavailable; install PSScriptAnalyzer separately.' >&2
  fi
fi

printf '%s\n' 'Python quality environment is ready.'
printf '%s\n' 'Run: bash scripts/run-quality-checks.sh'
printf '%s\n' 'Install CLOC, ShellCheck and kubeconform with an OS/package manager before strict infrastructure validation.'
