# Quickstart

Status: active source-adoption guide.

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
  = a repository being assessed against its own risks, controls, conventions,
    and existing governance surfaces
```

Commands in this guide run from the repository root of whichever context is
being checked.

Do not treat ASGK v1.x as a runtime package or a universal target-repository
shape. It is source-distributed governance guidance that may be selectively
adapted when a target assessment recommends it.

## Before You Start

You need a GitHub repository, permission to create issues/branches/PRs/commits,
Python 3 for local validation, and one small change to run through the process
first. GitHub Actions should be enabled when using the included workflow.

Optional helpers are the `gh` CLI, an AI coding agent, ASGK Skill Pack support
in the agent client, and a human reviewer for protected or human-gated work.

## Minimal Read Order

For a human assessing ASGK adoption:

```text
1. README.md
2. docs/INSTALL_SURFACE.md
3. skills/asgk-target-install-audit/SKILL.md
4. the target repository's own startup, authority, and handoff surfaces
5. only the additional target evidence identified during assessment
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

For target adoption or a material upgrade, the relevant Skill guides a
human-selected frontier-capability evaluator through evidence, boundaries,
alternatives, confidence, and unknowns. It does not contain a predetermined
adoption decision and does not select or switch models.

## Validate The Kit

From the ASGK source repository root, run:

```bash
python3 scripts/asgk.py doctor
```

Expected-failure output during `doctor` is intentional when followed by an
expected-failure summary. It confirms that current encoded fixtures trigger
their expected mechanical failures. Target-evidence fixtures prove only the
registered caller-claim behavior, not a semantic target-governance defect.

## Assess Adoption In A Target Repository

A human first chooses a frontier-capability evaluator. Use
`docs/INSTALL_SURFACE.md` with
`skills/asgk-target-install-audit/SKILL.md` to inspect the target repository
read-only. The evaluator uses target evidence and judgment to determine fit,
minimum sufficient adaptation, or whether no change or no adoption is the
better result.

Record the assessment in an existing target-owned issue, PR, or handoff lineage.
The assessment itself adds no approval gate. Existing gates apply only when its
implementation proposal touches a concrete protected or high-risk action.

If the ASGK source checkout is available, use explicit caller-supplied claims
for any mechanical observation produced during the assessment:

```bash
python3 scripts/asgk.py target-evidence-check \
  --repo-root /path/to/target/repo \
  --expect-path <target-relative-path> \
  --json
```

The command is read-only and assumes no target layout. Exit `0` means only that
the accepted named claims matched; it does not prove claim sufficiency,
semantic readiness, prescribe target architecture, or replace the evaluator's
judgment.

## First Governed Change

Choose a small docs-only change first. The goal is to learn the governance loop
without adding technical risk.

### 1. Create One Issue

Every executable task needs a durable GitHub issue or already-open PR. Do not
use chat as task authority.

The issue should name lane, intelligence level, reason, durable source of truth,
objective, plan, checklist, acceptance sheet, allowed paths, expected output,
non-goals, stop conditions, and rollback expectations.

It must separately record the smallest exact `context_read_set` of existing
repo files and complete durable references, plus concrete
`project_specific_validation`. These are execution gates, not extra
task-identity fields. Do not use prose shortcuts such as "whatever is needed."

Never write `see chat` for scope, acceptance, handoff, or merge authority.

Before creating a branch or editing files, validate the durable authority:

```bash
python3 scripts/asgk.py work-unit-check \
  --issue <issue-number> \
  --authority-only \
  --json
```

Task packets are optional. `issue_refinement` may only narrow the issue.
`github_unavailable_fallback` is temporary authority only for bounded local
work during verified GitHub unavailability, only when no escalation trigger
applies, and must be replaced by an issue before PR creation or merge. It
cannot authorize protected or otherwise escalated work.

During that outage only, validate the complete fallback with
`task-packet-check` before local work. The validator does not prove the outage;
record that evidence separately and retry issue creation before any PR action.

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

### 3. Run Post-Diff Work-Unit Check

Before committing or opening a PR, check that the selected work unit still
authorizes the local diff:

```bash
python3 scripts/asgk.py work-unit-check \
  --issue <issue-number> \
  --git-base origin/main \
  --git-head WORKTREE
```

For existing PR follow-up work, normally validate the PR's still-open linked
issue with `--issue <issue-number>`. Use `--pr <pr-number>` only when that PR
body itself is the complete current authority and visibly contains all 13
fields plus both execution gates. Use `WORKTREE` before committing so
uncommitted and untracked local files are checked.

This post-diff guard rechecks authority and changed paths. Unlike
`--authority-only`, it requires a non-empty diff source and runs path containment
and hygiene checks. Neither mode infers approval or low-risk status.

### 4. Change Only Allowed Paths

Use the issue as the boundary. If the issue says docs-only, do not change
scripts, schemas, workflows, dependencies, or protected paths.

Protected areas include `.github/**`, `docs/control/**`, `schemas/**`, and
`contracts/**`. Human-gated areas include dependencies, credentials,
release/tag/package operations, runtime-artifact or security/storage boundaries,
private source material, external target writes, and destructive history or
repository-setting changes.

When a protected path is required, record the trigger in the PR and keep the
merge human-gated unless canonical policy and the current issue explicitly allow
the program-scoped reversible path. That path requires an OWNER-approved exact
scope source, a child issue no broader than that source, tracked source only, no external side
effect beyond routine issue/PR metadata, ordinary-revert recovery, current-head
no-gate/scope review, independent review, CI, and strict `check-pr`. It cannot
cover a Human-Gated Operations item or a PR that changes the path itself,
including by creating, removing, loosening, tightening, or reclassifying it.

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

If any Human-Gated Operations item applies, merge only after explicit durable
current-head human approval. A protected source path may avoid a repeated
permission prompt only through the complete canonical program-scoped reversible
path; a program grant alone is insufficient and is never current-head review.

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

Use `docs/INSTALL_SURFACE.md` as the assessment boundary and
`skills/asgk-target-install-audit/SKILL.md` as the guided procedure.

The assessment should:

1. inspect the target's own authority, scope, forbidden actions, evidence,
   decision lineage, and handoff mechanisms;
2. identify actual risks and existing controls before proposing ASGK material;
3. reuse equivalent target-owned mechanisms when they already satisfy the need;
4. recommend the minimum sufficient adaptation, no change, or no adoption;
5. record evidence, limits, confidence, unknowns, protected surfaces, and any
   exact existing gate in the target's issue, PR, or handoff lineage.

Only after a change is recommended should a target-owned implementation issue
or PR authorize edits. The read-only assessment does not create an additional
human approval layer.

ASGK's `docs/DOCUMENT_MAP.md` and `docs/DOCUMENT_REGISTRY.md` remain authority
only for this repository. Their templates are optional references, not required
target files. Use them only when the assessment finds that the target lacks an
equivalent navigation or ownership surface.

Do not copy ASGK repo-local readiness audits, handoff history, roadmap state,
release-controller records, or superseded adapter planning as target-project
authority.

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
target adoption assessment: docs/INSTALL_SURFACE.md
guided target assessment: skills/asgk-target-install-audit/SKILL.md
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
