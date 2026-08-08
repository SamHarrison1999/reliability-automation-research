#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

required=(
  README.md .gitignore .gitattributes .editorconfig Makefile
  docs/research-design/phase-0.md docs/roadmap.md docs/progress-ledger.md
  docs/literature/evidence-matrix.csv docs/literature/phase-1-review-protocol.md
  docs/literature/search-log.csv docs/literature/screening-log.csv
  docs/literature/references.bib docs/adr/0001-repository-boundaries.md
  docs/adr/0002-provisional-technology-selection.md
  scripts/bootstrap.sh scripts/bootstrap.ps1 scripts/verify-repository.ps1
  .github/workflows/validate-repository.yml
)

missing=()
for path in "${required[@]}"; do
  [[ -f "${path}" ]] || missing+=("${path}")
done

if (( ${#missing[@]} > 0 )); then
  printf 'Missing required files:\n' >&2
  printf '  %s\n' "${missing[@]}" >&2
  exit 1
fi

if rg --glob '!docs/proposal/source/**' --glob '!scripts/verify-repository.sh' \
  --glob '!scripts/verify-repository.ps1' \
  'TODO|TBD|REPLACE_ME' README.md docs scripts .github; then
  printf 'Unexpected unresolved placeholder found in committed scaffolding.\n' >&2
  exit 1
fi

if find data/raw data/processed data/external results/generated -type f \
  ! -name .gitkeep -print -quit | rg -q .; then
  printf 'Generated or research data is present in a protected data directory.\n' >&2
  exit 1
fi

bash -n scripts/bootstrap.sh
if git -C "${REPO_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git diff --check
else
  printf '%s\n' 'Git validation skipped: this directory is not a valid Git repository.' >&2
fi

printf '%s\n' \
  'Repository verification passed.' \
  'Phase: 1 - scoping review and literature map.' \
  'Application implementation: intentionally absent.'
