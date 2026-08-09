#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${REPO_ROOT}/observability/opentelemetry/docker-compose.compatibility.yml"
PYTHON_BIN="${PYTHON_BIN:-python3}"
KEEP_STACK=false
SPAN_COUNT=5

while (($# > 0)); do
  case "$1" in
    --keep-stack) KEEP_STACK=true ;;
    --span-count) shift; SPAN_COUNT="$1" ;;
    -h|--help) printf '%s\n' 'Usage: scripts/run-opentelemetry-compatibility.sh [--keep-stack] [--span-count N]'; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
  shift
done

cd "${REPO_ROOT}"
"${PYTHON_BIN}" -m pip install -e "${REPO_ROOT}[observability]"
docker compose -f "${COMPOSE_FILE}" up -d --build

cleanup() {
  if [[ "${KEEP_STACK}" == false ]]; then
    docker compose -f "${COMPOSE_FILE}" down --volumes
  fi
}
trap cleanup EXIT

"${PYTHON_BIN}" observability/opentelemetry/compatibility_probe.py --span-count "${SPAN_COUNT}"
