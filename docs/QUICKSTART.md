# Quickstart

Status: onboarding guide.

This guide shows how to use this repository's governance workflow for a first
bounded change. It is intentionally practical. For policy details, follow the
canonical documents linked below instead of treating this guide as the full
source of truth.

## What This Repository Provides

This repository is a GitHub-native governance scaffold for AI-assisted
software development. Its goal is to keep humans, ChatGPT, Codex, and other
agents working through durable GitHub and repository state rather than private
chat memory.

ASGK v1.x uses a generic repo-agent governance core. It does not assume a
specific runtime. Codex, ChatGPT Web, OpenGoat, Claude Code, Cursor, another AI
agent, or a human may perform work, but every repo change must pass through the
same ASGK governance flow.

Runtime-specific governance profiles are planned for ASGK v2.0. They are
optimization adapters for specific execution surfaces, not prerequisites for
using v1.x.

The core workflow is:

```text
issue
  -> branch
  -> allowed-path change
  -> PR
  -> GitHub Actions validation
  -> Merge Decision Record
  -> low-risk merge or human gate
  -> issue result comment
  -> issue close
```

## Installing Into Another Repository

`docs/DOCUMENT_MAP.md` is repo-local.

The ASGK repository's `docs/DOCUMENT_MAP.md` governs this repository only. Do not
copy it unchanged into a target project and treat it as that project's canonical
document map.

When ASGK is installed or adapted into another repository:

```text
1. Copy or generate the minimal ASGK governance scaffold.
2. Create the target repository's own docs/DOCUMENT_MAP.md.
3. Use templates/DOCUMENT_MAP.template.md as the starting point.
4. Delete placeholder rows that do not exist in the target repository.
5. Add the target repository's actual canonical documents, summaries, examples,
   schemas, contracts, status documents, scripts, and task-specific read sets.
6. Keep the target repository map local to that repository.
```

The three distinct artifacts are:

```text
ASGK docs/DOCUMENT_MAP.md
  = repo-local map for this ASGK repository

templates/DOCUMENT_MAP.template.md
  = starter template for target repositories

target repo docs/DOCUMENT_MAP.md
  = repo-local map owned by the target project after installation
```

## Prerequisites

You need:

```text
- A GitHub repository containing this kit.
- GitHub Actions enabled.
- Permission to create issues, branches, PRs, and commits.
- Python 3 available for local validation.
```

Optional but useful:

```text
- gh CLI for local GitHub operations.
- Codex or another coding agent for implementation work.
- ChatGPT GitHub connector for planning, review, and low-risk GitHub actions.
```

## Minimal Read Order

For humans:

```text
1. README.md
2. docs/QUICKSTART.md
3. docs/DOCUMENT_MAP.md
4. docs/control/CONTEXT_BUDGET_POLICY.md
```

For AI agents starting a work unit:

```text
1. AGENTS.md
2. README.md
3. docs/handoff/CURRENT_STATUS.md
4. current GitHub issue or PR
5. docs/DOCUMENT_MAP.md only when document ownership is unclear
6. task-specific canonical docs named by the issue or context read set
```

Do not read the whole repository by default. Use
`docs/control/CONTEXT_BUDGET_POLICY.md` to select the context read set.

## First Local Validation

From the repository root:

```bash
python3 scripts/check_project.py
python3 scripts/validate_bootstrap.py
git diff --check
```

Expected result:

```text
Project scaffold check passed.
Bootstrap validation passed.
```

If these fail, fix the scaffold before starting feature work.

## First Governance Smoke Test

Use a small docs-only change first. The already validated pattern is:

```text
1. Create a GitHub issue with objective, durable source of truth, lane,
   intelligence level, allowed paths, expected output, checklist, acceptance
   sheet, non-goals, stop conditions, and rollback expectations.
2. Create a branch from current main.
3. Change only the allowed file path.
4. Open a PR using .github/PULL_REQUEST_TEMPLATE.md.
5. Wait for GitHub Actions.
6. Update the PR's Merge Decision Record after checks pass.
7. Merge only if low-risk merge gates pass.
8. Comment the result on the issue.
9. Close the issue as completed.
```

This project has already validated that loop with a docs-only handoff update and
subsequent documentation-map/control-policy additions.

## Creating A Good Issue

A valid issue should include:

```yaml
objective: "one concrete result"
durable_source_of_truth: "this GitHub issue or a repo document"
lane: "one lane from agent/task_packets/"
intelligence_level: "fast_basic | standard | advanced | frontier"
intelligence_level_reason: "why this level is sufficient"
allowed_paths:
  - "specific/path/or/directory"
expected_output:
  - "observable output"
plan:
  - "bounded step"
checklist:
  - "[ ] mechanical progress item"
acceptance_sheet:
  - "[ ] externally checkable condition"
non_goals:
  - "what must not be done"
stop_conditions:
  - "when the agent must stop"
rollback_expectations: "how to safely undo or close without merge"
```

Never write:

```text
see chat
```

for task scope, acceptance, durable source of truth, or handoff.

## Choosing Assignment Level

Use `docs/control/AGENT_CAPABILITY_MATRIX.md`.

Common defaults:

```yaml
typo_or_formatting:
  level: fast_basic
  low_risk_merge_possible: true

docs_or_handoff_update:
  level: standard
  low_risk_merge_possible: true

validation_script_change:
  level: advanced
  low_risk_merge_possible: maybe

schema_breaking_change:
  level: frontier
  low_risk_merge_possible: false
  human_gate_required: true

cloud_api_mcp_or_release:
  level: frontier
  low_risk_merge_possible: false
  human_gate_required: true
```

If a task appears to need a higher level than the issue authorizes, stop or
downscope the task.

## Choosing Context

Use `docs/control/CONTEXT_BUDGET_POLICY.md`.

Examples:

```yaml
docs_only:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - current GitHub issue or PR
    - target file
    - .github/PULL_REQUEST_TEMPLATE.md

merge_decision:
  read:
    - current PR body
    - changed file list
    - current GitHub issue
    - docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
    - docs/control/HUMAN_GATED_OPERATIONS.md
    - docs/control/MERGE_DECISION_RECORD.md

security_or_storage:
  read:
    - AGENTS.md
    - docs/bootstrap/01_physical_boundaries.md
    - docs/architecture/STORAGE_PROFILE.md
    - docs/architecture/RUNTIME_ARTIFACT_POLICY.md
    - docs/control/HUMAN_GATED_OPERATIONS.md
```

If more files are needed, record the context expansion in the PR or Agent Report.

## Opening A PR

Every PR should include:

```text
## Summary
## Task Reference
## Changed Files
## Validation
## Evidence Of Completion
## Scope Boundaries
## Runtime Output Status
## Merge Decision
## Known Gaps
## Handoff Report
```

The Merge Decision Record should look like:

```yaml
merge_decision:
  issue: "#<number>"
  lane: "<lane>"
  intelligence_level: "<level>"
  durable_source_of_truth: "GitHub issue #<number>"
  checks_passed: true | "pending GitHub Actions"
  allowed_paths_checked: true
  expected_output_checked: true
  contracts_checked: "not applicable" | true
  schemas_checked: "not applicable" | true
  storage_boundary: "no Artifact Root or Local State Root writes"
  runtime_artifact_boundary: "no runtime artifacts committed"
  safety_review: "low-risk docs-only" | "blocked" | "human-gated"
  human_gates_checked: true
  result: merge_allowed | merge_blocked
  reason: "why"
```

Do not merge while checks are pending or unknown.

## Low-Risk Merge Checklist

Before merging, confirm:

```text
- PR belongs to the active issue.
- Changed files match the issue's allowed paths.
- GitHub Actions pass.
- PR is not draft and is mergeable.
- PR has no unresolved requested changes.
- Merge Decision Record is complete.
- Runtime artifact boundary is clean.
- No protected paths are touched.
- No human-gated operation applies.
```

Canonical details live in:

```text
docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
docs/control/HUMAN_GATED_OPERATIONS.md
docs/control/MERGE_DECISION_RECORD.md
```

## Common Stop Conditions

Stop and report instead of continuing when:

```text
- required change is outside allowed paths
- protected path change is required
- validation behavior must change but the issue is docs-only
- new dependency is required
- cloud/API/model/MCP capability would be opened
- schema breaking change is required
- GitHub Actions fail for unclear reasons
- human-gated operation applies
- task state exists only in chat
```

## Common Mistakes

### Mistake: reading the whole repository

Use the context read set. Read only what the task needs.

### Mistake: treating examples as policy

Examples are not policy. Canonical policy lives in the files named by
`docs/DOCUMENT_MAP.md`.

### Mistake: merging before Actions finish

Do not merge while checks are pending or unknown.

### Mistake: changing scripts during docs-only work

Stop and open a tooling issue.

### Mistake: adding negative fixtures as normal valid examples

Negative fixtures must be opt-in and must not break normal validation unless the
validator is designed to treat them as expected failures.

### Mistake: optimizing for a specific runtime too early

v1.x is runtime-agnostic. Do not add Codex/OpenGoat/Claude/Cursor-specific
profile work unless a v2.0 profile issue explicitly opens that lane.

## What To Do Next

After this quickstart is in place, recommended next work units are:

```text
1. Add PR review checklist.
2. Add negative test plan.
3. Add negative fixtures.
4. Strengthen governance_hygiene.py.
5. Add quota / external agent fallback policy.
6. Add first CLI wrapper.
7. Plan v2.0 runtime-specific governance profiles after the generic core is stable.
```

Keep this order conservative. CLI should wrap stable rules, not freeze unstable
ones. Runtime-specific profiles should optimize stable governance, not define it.
