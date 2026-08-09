# Engineering-quality baseline

This baseline makes the research repository easier to inspect, reproduce and
review. It is a quality and maintainability gate; it is not evidence that the
OrderFlow system is reliable, that an automation strategy improves outcomes,
or that a production deployment is ready.

## Tool map

| Concern | Project tool | Purpose |
|---|---|---|
| Unit and integration tests | `pytest`, `pytest-cov` | Exercise the local controller, Kubernetes runner, event contract and service behaviour with a 100% line-and-branch coverage gate |
| Python linting and formatting | `ruff` | Replaces overlapping Flake8, pycodestyle, pyflakes, isort and Black checks |
| Static typing | `mypy` | Detect incompatible Python interfaces before execution |
| Python SAST | `bandit`, CodeQL | Complementary source-security checks |
| Dependency audit | `pip-audit` | Check Python dependencies for known published vulnerabilities |
| Complexity and size | `radon` when needed, `cloc` now | Keep code-size and complexity evidence separate from correctness gates |
| Shell quality | ShellCheck | Analyse Bash and POSIX shell scripts |
| PowerShell quality | PSScriptAnalyzer; Pester later | Analyse and eventually test PowerShell orchestration |
| YAML/Kubernetes | `yamllint`, `kubeconform` | Validate YAML syntax and Kubernetes schema |
| Ansible | `ansible-playbook --syntax-check`, `ansible-lint` | Validate the deferred environment-automation boundary |
| Container quality | Hadolint when Dockerfiles expand | Review Dockerfile practices without adding a permanent platform |
| Workflow quality | `actionlint` when installed; GitHub checks | Validate GitHub Actions configuration |
| Code inventory | CLOC | Produce a non-committed source-size report under `tmp/quality` |

The project does not add Pydantic merely for quality checking: Pydantic is a
runtime data-validation library. The current service has no runtime dependency
requiring it.

## Local use

```bash
bash scripts/bootstrap-quality.sh --with-infrastructure
bash scripts/run-quality-checks.sh --strict-infrastructure
```

On Windows PowerShell:

```powershell
.\scripts\bootstrap-quality.ps1 -WithInfrastructure
.\scripts\run-quality-checks.ps1 -StrictInfrastructure
```

CLOC, ShellCheck and kubeconform are operating-system tools and are
intentionally not installed by the Python environment. The infrastructure
bootstrap installs PSScriptAnalyzer when PowerShellGet is available; install
the other three with the platform's package manager, then run the strict
quality command. The report is disposable and must not be committed.

Each quality run uses fresh repository-local temporary directories for pytest
and pip-audit. This avoids stale Windows ACLs and pytest's shared
`%TEMP%\\pytest-*` cleanup links affecting later runs; the directories remain
under ignored `tmp/quality` and can be removed after the run if required.

Linux/WSL example:

```bash
sudo apt-get install --yes shellcheck
go install github.com/yannh/kubeconform/cmd/kubeconform@v0.7.0
pwsh -NoLogo -NoProfile -Command \
  'Install-Module PSScriptAnalyzer -Scope CurrentUser -Force -AllowClobber'
```

Windows PowerShell example:

```powershell
Install-Module PSScriptAnalyzer -Scope CurrentUser -Force -AllowClobber
winget install YannHamon.kubeconform
```

Installing Go and using `go install github.com/yannh/kubeconform/cmd/kubeconform@v0.7.0`
is also supported, but Go is not required when the Windows release is installed
with `winget`.

Install ShellCheck for Windows through an available package manager such as
Scoop or Chocolatey, or expose a Linux `shellcheck` through WSL. The strict
validator fails when a requested tool is missing; the non-strict validator
reports a warning for local development.

Ansible is executed natively by the Linux CI job. Native Windows Ansible
controllers are unsupported by ansible-core, so the Windows validator skips
that execution explicitly after completing YAML, Kubernetes, shell and
PowerShell checks. This avoids treating a POSIX-module startup error as a
playbook failure while retaining an authoritative cross-platform check.

## Coverage boundary

The enforced coverage target covers all three Python executables currently in
the fit-probe implementation: the local controller, the Kubernetes runner and
the deterministic OrderFlow service. The tests cover HTTP, subprocess,
readiness, fault, recovery, cleanup and CLI error paths. The PowerShell and
Bash orchestration scripts remain separately validated by their script-quality
checks because they are not Python modules and cannot be measured by
`pytest-cov`.
