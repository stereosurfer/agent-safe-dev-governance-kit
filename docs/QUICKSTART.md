# Quickstart

Status: v1.x adoption guide.

This guide shows the shortest practical path to use ASGK for one safe, bounded
repository change. It is an onboarding summary, not the full policy layer, PR
template, command reference, or target-install specification.

When policy details matter, follow the canonical documents named in
`docs/DOCUMENT_MAP.md` and `docs/DOCUMENT_REGISTRY.md`.

## What ASGK Sets Up

ASGK is a GitHub-native governance kit for AI-assisted repository work. It makes
GitHub issues, pull requests, validation, merge decisions, and handoff files the
durable source of truth.

It does not replace your coding agent, project architecture, runtime, package
manager, installer, or orchestration system. A human, Codex, Claude Code,
Cursor, ChatGPT, another AI agent, or automation can perform a change; ASGK
governs how that change is scoped, checked, reviewed, merged, and handed off.

## Source Repo And Target Repo

There are two common contexts:

```text
ASGK source repo
  = this repository, where ASGK itself is maintained and released

target repo
  = a repository that copies and adapts the ASGK governance scaffold
```

Commands in this guide run from the repository root of whichever context is
being checked.

Do not treat ASGK v1.x as a runtime package installed into an agent. It is a
source-only governance scaffold copied and adapted into a repository.

## Before You Start

You need a GitHub repository, permission to create issues/branches/PRs/commits,
Python 3 for local validation, and one small change to run through the process
first. GitHub Actions should be enabled when using the included workflow.

Optional helpers are the `gh` CLI, an AI coding agent, ASGK Skill Pack support
in the agent client, and a human reviewer for protected or human-gated work.

## Minimal Read Order

For a human adopting ASGK:

```text
1. README.md
2. docs/QUICKSTART.md
3. docs/INSTALL_SURFACE.md if installing into another repository
4. docs/DOCUMENT_MAP.md when canonical ownership is unclear
5. docs/control/HUMAN_GATED_OPERATIONS.md before risky work
```

For an AI agent starting work in an ASGK-governed repository:

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
procedures, not a new authority layer. Use `docs/SKILL_PACK.md` for the full
list, usage timing, client-installed mode, and repository-reference mode.

## Validate The Kit

From the ASGK source repository root, run:

```bash
python3 scripts/asgk.py doctor
```

Expected-failure output during `doctor` is intentional when followed by an
expected-failure summary. It proves known-bad governance examples are blocked.

For target repositories, first copy and adapt the install surface described in
`docs/INSTALL_SURFACE.md`, then run the target repository's configured
validation command. If the ASGK checker is available from the source checkout,
you can also run:

```bash
python3 scripts/asgk.py target-install-check --repo-root /path/to/target/repo
```

That check is read-only. It reports adoption-surface problems; it does not edit
the target repository.

## First Governed Change

Choose a small docs-only change first. The goal is to learn the governance loop
without adding technical risk.

### 1. Create One Issue

Every executable task needs a durable GitHub issue or already-open PR. Do not
use chat as task authority.

The issue should name lane, intelligence level, reason, durable source of truth,
objective, plan, checklist, acceptance sheet, allowed paths, expected output,
non-goals, stop conditions, and rollback expectations.

Never write `see chat` for scope, acceptance, handoff, or merge authority.

### 2. Create A Branch

Branch from current `main` and keep one issue to one PR unless the issue says
otherwise.

```text
main
  -> task branch
  -> one issue
  -> one PR
```

If a needed change is outside the issue's allowed paths, stop. Update the
durable issue or create a new issue instead of silently expanding scope.

### 3. Run Work-Unit Preflight

Before committing or opening a PR, check that the selected work unit still
authorizes the local diff:

```bash
python3 scripts/asgk.py work-unit-check \
  --issue <issue-number> \
  --git-base origin/main \
  --git-head WORKTREE
```

For existing PR follow-up work, use `--pr <pr-number>`. Use `WORKTREE` before
committing so uncommitted and untracked local files are checked.

This guard blocks stale, wrong-type, closed, merged, or outside-allowed-path
work when run. It does not intercept every editor write before it happens.

### 4. Change Only Allowed Paths

Use the issue as the boundary. If the issue says docs-only, do not change
scripts, schemas, workflows, dependencies, or protected paths.

Protected or human-gated areas include `.github/**`, `docs/control/**`,
`schemas/**`, `contracts/**`, dependencies, credentials, release/tag/package
operations, runtime artifacts, and private source material.

When a protected path is required, record the trigger in the PR and keep the
merge human-gated unless canonical policy and the current issue explicitly allow
otherwise.

### 5. Validate

For governance or scaffold changes:

```bash
python3 scripts/asgk.py doctor
```

For focused checks, use command help:

```bash
python3 scripts/asgk.py --help
python3 scripts/asgk.py <command> --help
```

For project-specific code changes, also run the tests required by the issue.
Record what those tests cover and what they do not prove in the PR Validation
section.

## Open The PR

Draft the PR body in a file and use `.github/PULL_REQUEST_TEMPLATE.md`.

Before creating or editing a PR body, run:

```bash
python3 scripts/pr_governance_preflight.py check --body-file pr.md
```

For file-backed create/edit flows, use:

```bash
python3 scripts/pr_governance_preflight.py create --body-file pr.md -- <gh-pr-create-args>
python3 scripts/pr_governance_preflight.py edit --body-file pr.md -- <gh-pr-edit-args>
```

Use the template and `docs/control/MERGE_DECISION_RECORD.md` for the exact PR
body structure. Do not mark checks as passed until they have actually run.

## Wait For Gates

Before merge, confirm that the PR belongs to the active issue, changed files
match allowed paths, required local validation and CI passed, the PR is
mergeable and not draft, unresolved requested changes are absent, runtime/private
source boundaries are clean, and no human-gated operation is being bypassed.

If any high-risk or protected trigger applies, merge only after explicit durable
human approval.

## Close Out

After merge, confirm the PR merged and the closing issue is satisfied, comment
with compact completion evidence, include one bounded `issue_closeout_review`
block in the GitHub issue comment, close the issue when authorized, and update
`docs/handoff/CURRENT_STATUS.md` only if leaving it unchanged would mislead the
next session.

Use `docs/handoff/ISSUE_CLOSEOUT_REVIEW_RULES.md` for the closeout review
writing guide. Do not create repo-file repair work solely to store routine
closeout reviews.

## Adopt In Another Repository

Use `docs/INSTALL_SURFACE.md` as the installation boundary.

Important distinction:

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

## Common Stop Conditions

Stop and report when task authority exists only in chat, allowed paths are
missing, required changes exceed issue scope, protected paths lack
authorization, validation cannot run, high-risk surfaces appear, CI fails for
unclear reasons, or the PR body would need to claim evidence that does not
exist.

## Where Details Live

```text
agent startup and stop rules: AGENTS.md
document routing: docs/DOCUMENT_MAP.md
target adoption boundary: docs/INSTALL_SURFACE.md
validation proof boundary: docs/control/VALIDATION_STRATEGY.md
negative test matrix: docs/control/NEGATIVE_TEST_PLAN.md
human gates: docs/control/HUMAN_GATED_OPERATIONS.md
low-risk merge policy: docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
current status policy: docs/control/CURRENT_STATUS_POLICY.md
issue closeout review rules: docs/handoff/ISSUE_CLOSEOUT_REVIEW_RULES.md
PR body shape: .github/PULL_REQUEST_TEMPLATE.md
```

After the first governed change works, use `docs/DOCUMENT_MAP.md` to decide
which canonical document to read next. Do not expand into all control documents
by habit.
