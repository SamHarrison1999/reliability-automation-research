#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
STRICT=false
if [[ "${1:-}" == '--strict' ]]; then STRICT=true; fi
cd "${REPO_ROOT}"
export ANSIBLE_CONFIG="${REPO_ROOT}/ansible/ansible.cfg"
export ANSIBLE_HOME="${REPO_ROOT}/tmp/ansible-home"
export ANSIBLE_LOCAL_TEMP="${REPO_ROOT}/tmp/ansible"
export XDG_CACHE_HOME="${REPO_ROOT}/tmp/cache"
mkdir -p "${ANSIBLE_HOME}" "${ANSIBLE_LOCAL_TEMP}" "${XDG_CACHE_HOME}"

fail_or_warn() {
  local message="$1"
  if [[ "${STRICT}" == true ]]; then
    printf 'ERROR: %s\n' "${message}" >&2
    exit 1
  fi
  printf 'WARNING: %s\n' "${message}" >&2
}

require_tool() {
  local tool="$1"
  if ! command -v "${tool}" >/dev/null 2>&1; then
    fail_or_warn "${tool} is unavailable."
    return 1
  fi
  return 0
}

missing=()
for tool in yamllint kubeconform; do
  if ! require_tool "${tool}"; then missing+=("${tool}"); fi
done

if (( ${#missing[@]} > 0 )) && [[ "${STRICT}" == true ]]; then exit 1; fi

if command -v shellcheck >/dev/null 2>&1; then
  shellcheck scripts/*.sh infrastructure/kubernetes/entrypoint.sh
else
  fail_or_warn 'ShellCheck is unavailable; shell validation was not performed.'
fi

if command -v pwsh >/dev/null 2>&1; then
  if pwsh -NoLogo -NoProfile -Command \
    'if (Get-Module -ListAvailable -Name PSScriptAnalyzer) { exit 0 } else { exit 1 }' \
    >/dev/null 2>&1; then
    pwsh -NoLogo -NoProfile -File scripts/run-psscriptanalyzer.ps1
  else
    fail_or_warn 'PSScriptAnalyzer is unavailable; PowerShell analysis was not performed.'
  fi
else
  fail_or_warn 'PowerShell (pwsh) is unavailable; PSScriptAnalyzer was not performed.'
fi

if command -v yamllint >/dev/null 2>&1; then
  yamllint ansible observability infrastructure .github
fi

if command -v kubeconform >/dev/null 2>&1; then
  kubeconform \
    -strict \
    -summary \
    -schema-location default \
    -schema-location 'https://raw.githubusercontent.com/yannh/kubernetes-json-schema/master/{{.ResourceKind}}{{.ResourceAPIVersion}}-standalone-strict.json' \
    infrastructure/kubernetes/*.yaml
fi

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    # ansible-core is not a supported native Windows controller. The Linux
    # CI job performs the authoritative syntax and lint checks. Do not invoke
    # it here: native execution fails before parsing the playbook (for example
    # while importing the POSIX-only grp module).
    printf '%s\n' 'Ansible native execution skipped on Windows; Linux CI is authoritative.'
    ;;
  *)
    missing_ansible=()
    for tool in ansible-playbook ansible-lint; do
      if ! require_tool "${tool}"; then missing_ansible+=("${tool}"); fi
    done
    if (( ${#missing_ansible[@]} == 0 )); then
      ansible-playbook --syntax-check -i "${REPO_ROOT}/ansible/inventory/local.yml" "${REPO_ROOT}/ansible/site.yml"
      ansible-lint "${REPO_ROOT}/ansible/site.yml"
    elif [[ "${STRICT}" == true ]]; then
      exit 1
    fi
    ;;
esac

printf '%s\n' 'Infrastructure validation passed.'
