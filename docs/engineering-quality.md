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

## Provenance-frozen analysis formatting boundary

Phase 5 analysis code is covered by Ruff linting, mypy, tests and
Bandit.

The repository-wide Ruff formatter gate does not retrospectively
reformat analysis source after that source has become a provenance
anchor for an immutable processed dataset or analysis artifact.

This prevents a formatting-only closeout change from changing the
source blob associated with an already-recorded empirical derivation.

Analysis tooling should therefore be Ruff-formatted before its
empirical provenance anchor is created. Once an empirical artifact is
bound to that historical tooling commit, later repository quality
checks preserve that source representation while continuing to apply
linting, type checking, testing and security analysis.

### Bandit boundary for provenance-frozen Phase 5 analysis

The provenance-frozen Phase 5 dataset and descriptive-analysis source
files contain reviewed `assert isinstance(...)` statements used for
type narrowing.

Bandit reports these statements as B101 because Python assertions can
be removed when execution uses optimisation.

Changing those historical source files after their empirical outputs
have been bound to their Git commits would change the provenance
anchor solely to satisfy a post-collection static-analysis rule.

The quality runner therefore applies a path-specific exception:

- all other analysis, experiment and system source remains subject to
  B101;
- `phase_5_primary_dataset.py` and
  `phase_5_primary_descriptive.py` remain subject to the full Bandit
  scan except B101;
- the pre-existing B310, B404, B603 and B607 repository skips remain
  unchanged.

The exception does not use `--exit-zero`, does not suppress Bandit for
the analysis directory as a whole, and does not suppress any
non-B101 finding specifically because a file is provenance-frozen.

Future analysis tooling should resolve applicable Bandit findings
before its empirical provenance anchor is created.
