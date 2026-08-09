#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
OUTPUT_DIR="${REPO_ROOT}/tmp/quality"
OUTPUT_FILE="${OUTPUT_DIR}/cloc.json"

if ! command -v cloc >/dev/null 2>&1; then
  printf '%s\n' 'CLOC is not installed. Install it with your OS package manager, then rerun this script.' >&2
  exit 2
fi

mkdir -p "${OUTPUT_DIR}"
cd "${REPO_ROOT}"
cloc --json --by-file --exclude-dir=.git,.venv,tmp,results,upload --out="${OUTPUT_FILE}" .
printf 'CLOC report written to %s\n' "${OUTPUT_FILE}"

