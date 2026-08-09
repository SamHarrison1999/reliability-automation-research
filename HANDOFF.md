# Phase 2 technology-decision close-out

This package finalises the Phase 2 technology decisions on
`chore/phase-2-closeout`.

## Apply

From the repository root after confirming the branch and working-tree state:

```powershell
Expand-Archive -Force .\phase2-technology-decision-closeout-20260809.zip .
Copy-Item .\phase2-technology-decision-closeout\docs\* .\docs\ -Recurse -Force

git diff --check
git add README.md docs
git diff --cached --check
git commit -m "Finalize Phase 2 technology decisions"
git push
```

The generated OpenTelemetry compatibility result is already part of the
Phase 2 branch. This package adds the decision record that interprets it; it
does not recreate or edit generated result bundles.

## What this closes

- Docker image packaging and Docker Desktop Kubernetes as the bounded local
  technical-pilot target.
- GitHub Actions as repository validation, separated from portable experiment
  execution.
- The pinned OpenTelemetry Python SDK 1.44.0 → OTLP/HTTP → Collector 0.158.0
  small-trace path, with raw gzip transport retention.
- Monitoring-triggered rule-based recovery and deterministic harness faults as
  the first technical comparison boundary.
- Automated deployment rollback and progressive deployment as explicit,
  separately validated/deferred extensions.

This is technical feasibility evidence only. It is not evidence of a
reliability effect, production readiness, generalisability or human behaviour.

## CI-fix wording retained

If the already-prepared CI correction still needs its own commit, use the
edited commit message and description:

```text
Fix CI ShellCheck validation and Node.js runtime warning

- Remove the redundant `PYTHON_BIN` self-assignment triggering ShellCheck `SC2269`.
- Preserve local virtual-environment and CI Python interpreter discovery.
- Upgrade `actions/setup-python` from v5 to v6 to use the Node.js 24 runtime.
- Remove the Node.js 20 deprecation warning without changing the quality checks.
```

## PR and local-branch cleanup

Because the earlier Phase 2 PR was already merged, open a new PR for this
close-out commit:

**Title:** `Finalize Phase 2 technology decisions and OpenTelemetry compatibility`

After that PR is merged, clean the local checkout while keeping the Phase 3
branch:

```powershell
git switch main
git pull --ff-only origin main
git fetch --prune origin

git branch --merged main

git branch -d chore/phase-2-closeout
git branch -d feat/phase-2-fit-probe
git branch -d chore/engineering-quality-baseline
git branch -d research/complete-literature-review
git branch -d research/phase-1-literature-evidence
git branch -d research/phase-1-literature-review

git branch
git status --short --branch
```

Keep `main` and `feat/phase-3-fault-model-metrics-protocol`. The `-d` option
is intentional: if Git refuses to delete a branch, stop and inspect
`git log main..<branch>` rather than forcing deletion. The current
`chore/phase-2-closeout` branch must remain until this close-out PR has been
merged.
