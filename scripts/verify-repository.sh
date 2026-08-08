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
  docs/research-design/phase-2.md docs/technology-selection/README.md
  docs/technology-selection/selection-matrix.csv docs/technology-selection/source-register.md
  docs/adr/0003-candidate-system-selection.md docs/adr/0004-experimental-deployment-model.md
  docs/adr/0005-observability-and-provenance-boundary.md docs/adr/0006-fault-injection-boundary.md
  docs/protocols/phase-2-fit-probe.md
  docs/fit-probe/phase-2-fit-probe-results.md data/schemas/technical-event-record.md
  infrastructure/local-fit-probe.json infrastructure/kubernetes/orderflow-fit-probe.yaml
  infrastructure/kubernetes/Dockerfile infrastructure/kubernetes/entrypoint.sh
  experiments/scenarios/no-fault.json experiments/scenarios/service-termination.json
  experiments/scenarios/dependency-latency.json experiments/harness/fit_probe.py
  experiments/harness/kubernetes_fit_probe.py
  system/orderflow/service.py scripts/run-phase-2-fit-probe.sh scripts/run-phase-2-fit-probe.ps1
  scripts/run-phase-2-kubernetes-fit-probe.ps1
  docs/diagrams/phase-2-candidate-architecture.mmd docs/diagrams/phase-2-experiment-control-flow.mmd
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

if grep -R -I -n -E \
  --exclude='verify-repository.sh' \
  --exclude='verify-repository.ps1' \
  --exclude-dir='source' \
  'TODO|TBD|REPLACE_ME' README.md docs scripts .github; then
  printf 'Unexpected unresolved placeholder found in committed scaffolding.\n' >&2
  exit 1
else
  scan_status=$?
  if (( scan_status > 1 )); then
    printf 'Placeholder scan failed (grep exit %d).\n' "${scan_status}" >&2
    exit "${scan_status}"
  fi
fi

if ! protected_file="$(find data/raw data/processed data/external results/generated \
  -type f ! -name .gitkeep -print -quit)"; then
  printf 'Protected-directory scan failed.\n' >&2
  exit 1
fi

if [[ -n "${protected_file}" ]]; then
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
  'Phase: 2 - software-system and technology selection.' \
  'Full application implementation: intentionally absent; fit-probe slice only.'
