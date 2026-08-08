#!/usr/bin/env bash
set -euo pipefail

# Phase 0 repository bootstrap. This creates research boundaries and
# documentation scaffolding; it deliberately does not create application code.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROPOSAL_PATH=""

usage() {
  printf '%s\n' \
    "Usage: bash scripts/bootstrap.sh [--proposal /path/to/proposal.pdf]" \
    "Creates the Phase 0 repository structure without overwriting existing files."
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --proposal)
      [[ $# -ge 2 ]] || { printf 'Missing value for --proposal\n' >&2; exit 2; }
      PROPOSAL_PATH="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

directories=(
  docs/proposal/source
  docs/research-design
  docs/literature
  docs/protocols
  docs/ethics
  docs/diagrams
  docs/adr
  docs/templates
  system
  infrastructure
  experiments/scenarios
  experiments/configurations
  experiments/harness
  data/raw
  data/processed
  data/external
  data/schemas
  analysis
  scripts
  tests
  results/generated
  results/figures
  results/tables
)

for directory in "${directories[@]}"; do
  mkdir -p "${REPO_ROOT}/${directory}"
done

for marker in \
  data/raw/.gitkeep \
  data/processed/.gitkeep \
  data/external/.gitkeep \
  results/generated/.gitkeep \
  system/.gitkeep \
  infrastructure/.gitkeep \
  experiments/scenarios/.gitkeep \
  experiments/configurations/.gitkeep \
  experiments/harness/.gitkeep \
  data/schemas/.gitkeep \
  analysis/.gitkeep \
  tests/.gitkeep; do
  [[ -e "${REPO_ROOT}/${marker}" ]] || : > "${REPO_ROOT}/${marker}"
done

if [[ -n "${PROPOSAL_PATH}" ]]; then
  [[ -f "${PROPOSAL_PATH}" ]] || { printf 'Proposal not found: %s\n' "${PROPOSAL_PATH}" >&2; exit 1; }
  destination="${REPO_ROOT}/docs/proposal/source/$(basename -- "${PROPOSAL_PATH}")"
  if [[ -e "${destination}" ]]; then
    printf 'Keeping existing proposal: %s\n' "${destination}"
  else
    cp -- "${PROPOSAL_PATH}" "${destination}"
    printf 'Copied proposal to: %s\n' "${destination}"
  fi
fi

if ! git -C "${REPO_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git -C "${REPO_ROOT}" init -b main >/dev/null 2>&1; then
    printf 'Initialised Git repository on branch main: %s\n' "${REPO_ROOT}"
  elif git -C "${REPO_ROOT}" init >/dev/null 2>&1 && git -C "${REPO_ROOT}" branch -m main; then
    printf 'Initialised Git repository: %s\n' "${REPO_ROOT}"
  else
    printf '%s\n' \
      'Warning: Git could not be initialised in this directory.' \
      'The scaffold was created; run git init locally when the directory is writable.' >&2
  fi
else
  printf 'Keeping existing Git repository: %s\n' "${REPO_ROOT}"
fi

printf '%s\n' "Phase 0 repository bootstrap complete." "Run: bash scripts/verify-repository.sh"
