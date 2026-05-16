# Quickstart

Status: v1.x adoption guide.

This guide shows the shortest practical path to use ASGK for one safe,
bounded repository change. It is not the full policy layer. When policy details
matter, follow the canonical documents linked from `docs/DOCUMENT_MAP.md`.

## What You Are Setting Up

ASGK is a GitHub-native governance kit for AI-assisted repository work. It makes
GitHub issues, pull requests, validation, merge decisions, and handoff files the
durable source of truth.

It does not replace your coding agent or your project architecture. A human,
Codex, Claude Code, Cursor, ChatGPT, another AI agent, or automation can perform
the change. ASGK governs how that change is scoped, checked, reviewed, merged,
and handed off.

## Before You Start

There are two contexts:

```text
ASGK source repo
  = this repository, where ASGK itself is maintained and released

target repo
  = the repository where you copy/adapt the ASGK governance scaffold
```

Commands in this guide run from the repository root of whichever context is
being checked. Do not treat ASGK as a runtime package installed into an agent.
It is a governance scaffold copied and adapted into a repository.

You need:

```text
- a target GitHub repository;
- permission to create issues, branches, PRs, and commits;
- GitHub Actions enabled when using the included workflow;
- Python 3 for local validation;
- one small change to run through the process first.
```

Optional but useful:

```text
- gh CLI for GitHub operations;
- an AI coding agent for implementation;
- ASGK Skill Pack support in the agent client, or repository-reference access
  to skills/*;
- a human reviewer for human-gated or protected-surface work.
```

## Minimal Read Order

For a human adopting ASGK:

```text
1. README.md
2. docs/QUICKSTART.md
3. docs/INSTALL_SURFACE.md if installing into another repository
4. docs/DOCUMENT_MAP.md when you need canonical document ownership
5. docs/control/HUMAN_GATED_OPERATIONS.md before risky work
```

For an AI agent starting work in this repository:

```text
1. AGENTS.md
2. README.md
3. docs/handoff/CURRENT_STATUS.md
4. current GitHub issue or PR
5. docs/DOCUMENT_MAP.md only when context expansion is needed
```

Do not read the whole repository by default. Use the smallest context set that
can safely answer the current issue or PR.

## Optional Skill Pack

ASGK ships source-distributed skills under `skills/`. They are reusable
procedures, not a new authority layer.

Use them in one of two modes:

```text
client-installed mode
  = copy selected skills/* directories into the agent client's skill location

repository-reference mode
  = keep skills/* in the repo and read only the specific SKILL.md needed now
```

For the full list, usage timing, and maintenance touchpoints, see
`docs/SKILL_PACK.md`.

## Validate The Kit

From the ASGK source repository root, this validates the kit itself:

```bash
python3 scripts/asgk.py doctor
```

Expected high-level result:

```text
Project scaffold check passed.
Bootstrap validation passed.
Check passed.
Expected-failure checks passed.
```

The negative fixture failures printed during `doctor` are intentional when they
are followed by an expected-failure summary. They prove that unsafe examples are
blocked.

For a target repository, first copy and adapt the install surface described in
`docs/INSTALL_SURFACE.md`, then run the target repository's configured
validation command. If the ASGK checker is available from the source checkout,
you can also run a read-only install-surface sanity check:

```bash
python3 scripts/asgk.py target-install-check --repo-root /path/to/target/repo
```

The first success state is simple:

```text
- the target repo has its own AGENTS.md and docs/DOCUMENT_MAP.md;
- project boundary and current-status files are customized for that repo;
- validation passes;
- one small issue exists with allowed paths and stop conditions;
- one PR uses the template, evidence, Current Status Impact, and Merge Decision Record.
```

## Run Your First Governed Change

Choose a small docs-only change first. The goal is to learn the governance loop
without adding technical risk.

### 1. Create One Issue

Every task needs a durable GitHub issue or PR. Do not use chat as the task
authority.

Include these fields:

```yaml
lane: docs
intelligence_level: standard
reason: "why this level is enough"
durable_source_of_truth:
  - "this issue"
objective: "one concrete result"
plan:
  - "bounded step"
checklist:
  - "[ ] mechanical progress item"
acceptance_sheet:
  acceptance_condition: true
allowed_paths:
  - "specific/file.md"
expected_output:
  - "one PR"
non_goals:
  - "what must not change"
stop_conditions:
  - "when the agent must stop"
rollback_expectations: "how to revert or close safely"
```

Never write `see chat` for scope, acceptance, handoff, or merge authority.

### 2. Create A Branch

Branch from current `main` and keep the work unit narrow.

```text
main
  -> task branch
  -> one issue
  -> one PR
```

If a change needs paths outside the issue's allowed paths, stop and update the
durable issue or create a new issue. Do not silently expand scope.

### 3. Run Work-Unit Preflight

Before committing or opening a PR, check that the selected live work unit still
authorizes the local diff:

```bash
python3 scripts/asgk.py work-unit-check \
  --issue <issue-number> \
  --git-base origin/main \
  --git-head WORKTREE
```

For existing PR follow-up work, use `--pr <pr-number>`. Use
`--git-head WORKTREE` before committing so uncommitted and untracked local files
are checked. Use `--git-head HEAD` after committing. For deterministic fixtures
or captured metadata, use `--json-file work_unit.json` with
`--paths-file changed-paths.txt`.

This is a preflight and pre-PR guard. It blocks stale, wrong-type, closed,
merged, or outside-allowed-path work when run, but it does not intercept every
editor or agent filesystem write before the write occurs.

### 4. Change Only Allowed Paths

Use the issue as the boundary. If the issue says docs-only, do not change
scripts, schemas, workflows, dependencies, or protected paths.

Protected or human-gated areas include:

```text
.github/**
docs/control/**
schemas/** or contracts/**
dependency files
credentials or secrets
release/tag/package/visibility operations
runtime artifacts or private source material
```

When a protected path is required, record the trigger in the PR and keep the
merge human-gated.

### 5. Decide Current Status Impact

Most small PRs should not update `docs/handoff/CURRENT_STATUS.md`.

Use the PR's Current Status Impact section:

```yaml
current_status_impact:
  status: not_applicable
  reason: "This PR does not change the repository recovery surface."
  current_status_updated_in_this_pr: false
  post_merge_safe: not_applicable
  follow_up_issue: none
```

If a PR does update `docs/handoff/CURRENT_STATUS.md`, the update must be
post-merge-safe. It should describe the repository state after the PR merges,
not the temporary state of the PR itself.

For PR-specific checking, use a PR body file and changed-paths file:

```bash
python3 scripts/asgk.py current-status-impact-check \
  --pr-body pr.md \
  --changed-paths-file changed-paths.txt \
  --this-pr '#<pr>' \
  --closing-issue '#<issue>' \
  --this-branch '<branch>'
```

This check is local-only. It does not query GitHub.

### 6. Validate

For governance or scaffold changes:

```bash
python3 scripts/asgk.py doctor
```

`doctor` is a governance and scaffold validation entrypoint. It checks ASGK
surface integrity, compact status hygiene, changed-path guardrails, and known-bad
negative fixtures. It does not prove application behavior, code semantics,
security correctness, privacy safety, dependency health, or whether an agent used
current third-party API documentation.

Useful focused checks:

```bash
python3 scripts/asgk.py negative all
python3 scripts/pr_governance_preflight.py check --body-file pr.md
python3 scripts/asgk.py work-unit-check --issue <issue-number> --git-base origin/main --git-head WORKTREE
python3 scripts/asgk.py workspace-state-check
python3 scripts/policy_gate_check.py --pr-body pr.md
git diff --check
```

For project-specific code changes, also run the tests required by the issue.
Record what those tests cover and what they do not prove in the PR Validation
section.

`workspace-state-check` is a startup hygiene check. By default it reports local
warnings such as untracked artifacts or a branch already merged into the base ref
without failing the work unit; use `--strict` only when a caller wants those
warnings to block.

### 7. Open The PR

Draft the PR body in a file. Run local PR body governance preflight before
creating or editing the PR body:

```bash
python3 scripts/pr_governance_preflight.py check --body-file pr.md
```

For file-backed create/edit flows, use the wrapper so the body is checked before
`gh` submits it:

```bash
python3 scripts/pr_governance_preflight.py create --body-file pr.md -- <gh-pr-create-args>
python3 scripts/pr_governance_preflight.py edit --body-file pr.md -- <gh-pr-edit-args>
```

GitHub Actions remains the final governance backstop. Local preflight is the
first defense against missing PR body sections.

Every PR should include:

```text
## Summary
## Task Reference
## Context Read Set
## Changed Files
## Validation
## Evidence Of Completion
## Scope Boundaries
## Current Status Impact
## Runtime Output Status
## Merge Decision
## Known Gaps
## Handoff Report
```

The Merge Decision Record should be evidence-backed:

```yaml
merge_decision:
  issue: "#<number>"
  lane: "<lane>"
  intelligence_level: "<level>"
  durable_source_of_truth: "#<number>"
  checks_passed: true
  allowed_paths_checked: true
  expected_output_checked: true
  contracts_checked: true | not_applicable
  schemas_checked: true | not_applicable
  storage_boundary: clean
  runtime_artifact_boundary: clean
  safety_review: "why this is low risk or human-gated"
  human_gates_checked: true
  result: merge_allowed | merge_blocked
  reason: "why"
```

Do not mark checks as passed until they have actually run.

### 7. Wait For Gates

Before merge, confirm:

```text
- the PR belongs to the active issue;
- changed files match allowed paths;
- required local validation passed;
- GitHub Actions passed when applicable;
- the PR is mergeable and not draft;
- there are no unresolved requested changes;
- runtime artifact and private-source boundaries are clean;
- no human-gated operation is being bypassed.
```

If any high-risk or protected trigger applies, merge only after explicit human
approval.

### 8. Close Out

After merge:

```text
1. Comment on the issue with the PR, merge result, and validation evidence.
2. Close the issue as completed when authorized.
3. Update docs/handoff/CURRENT_STATUS.md only if the repository recovery surface
   actually changed.
4. Add one bounded decision-analysis block to the GitHub issue closeout comment
   using `docs/handoff/ISSUE_CLOSEOUT_REVIEW_RULES.md` as the writing guide.
   Do not create repo-file repair work solely to store routine reviews.
```

Routine closeout PRs should not be needed when `CURRENT_STATUS.md` was already
post-merge-safe or unchanged. Issue Closeout Reviews are still required in
issue closeout comments; keep routine entries bounded and evidence-dense
instead of skipping them. Do not replace decision analysis with a short summary.

## Adopt In Another Repository

Use `docs/INSTALL_SURFACE.md` as the installation boundary.

Important distinctions:

```text
ASGK docs/DOCUMENT_MAP.md
  = repo-local map for this ASGK repository

templates/DOCUMENT_MAP.template.md
  = starter template for target repositories

target repo docs/DOCUMENT_MAP.md
  = repo-local map owned by the target project after adoption
```

Do not copy ASGK repo-local readiness audits, handoff history, roadmap state,
release-controller records, or adapter placeholders as target-project authority.

After adapting a target repository, use the target-install check as a read-only
sanity pass:

```bash
python3 scripts/asgk.py target-install-check --repo-root /path/to/target/repo
```

## Common Stop Conditions

Stop and report instead of continuing when:

```text
- task authority exists only in chat;
- allowed paths are missing or unclear;
- a needed change is outside the issue scope;
- protected paths are required without authorization;
- validation cannot be run;
- a dependency, schema, workflow, release, visibility, cloud/API/model, or
  private-source change appears;
- GitHub Actions fail for unclear reasons;
- the PR body would need to claim evidence that does not exist.
```

## Common Mistakes

### Reading Too Much

Use the startup set and document map. Do not read the whole repository by
default.

### Treating Examples As Policy

Examples show patterns. Canonical policy lives in the documents named by
`docs/DOCUMENT_MAP.md` and by the current issue or PR.

### Using Current Status As An In-Flight Tracker

`docs/handoff/CURRENT_STATUS.md` is post-merge-safe by default. Put temporary PR
state in the issue, PR body, or handoff report.

### Merging While Checks Are Unknown

Pending, skipped, unknown, or failing checks are not the same as passing checks.

### Expanding A Docs-Only Issue Into Tooling

If docs reveal a tooling need, create a tooling issue. Do not widen the current
PR without durable authorization.

## Where To Go Next

After the first governed change works, read:

```text
docs/INSTALL_SURFACE.md
docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
docs/control/HUMAN_GATED_OPERATIONS.md
docs/control/CURRENT_STATUS_POLICY.md
docs/control/CONTEXT_BUDGET_POLICY.md
```

For ASGK maintainers, later product-entry follow-ups should stay separate:

```text
1. Align docs/INSTALL_SURFACE.md with the v1.x source-only adoption path.
2. Refresh docs/bootstrap/10_roadmap.md for v1.x and post-v1 direction.
```
