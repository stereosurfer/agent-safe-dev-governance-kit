---
name: asgk-release-prep
description: Use for ASGK source-only release preparation, human-gated release execution, and release-state closeout; requires release issues to name product-entry and handoff docs, explicit approval, final validation, and release-state-check before closeout.
---

# ASGK Release Prep

Use this skill for source-only ASGK release planning, release execution, or
release-state closeout.

## Authority

This skill does not authorize a release. Release execution requires a separate
GitHub issue with explicit human approval. Tags, GitHub releases, packages,
repository visibility changes, dependencies, workflows, schemas, runtime
adapters, installer scaffold, and v2.0 work remain human-gated unless the
release issue explicitly authorizes them.

If this skill conflicts with `AGENTS.md`, the release issue, a PR, or
`docs/control/SOURCE_ONLY_RELEASE_POLICY.md`, stop and use the durable repo
authority.

## Required Inputs

- Release target: tag, title, target commit, and source-only boundary.
- Release issue with explicit human approval before execution.
- Product-entry and handoff docs that must be synchronized, usually:
  - `README.md`
  - `docs/bootstrap/10_roadmap.md`
  - `docs/handoff/CURRENT_STATUS.md`
  - any release-specific control or readiness docs named by the issue
- Validation commands, including:
  - `python3 scripts/asgk.py doctor`
  - `python3 scripts/asgk.py release-state-check --tag <tag> --release-title "<title>"`
- Rollback or revoke plan for tag or release metadata mistakes.

## Procedure

### 1. Planning

Planning may define gates, checklist, blockers, release path, and docs to
synchronize. Planning must not create tags, publish packages, or create GitHub
releases.

Before execution is proposed, confirm:

```yaml
release_prep_gate:
  release_issue_exists: true
  explicit_human_approval_required_before_execution: true
  product_entry_docs_named: true
  handoff_docs_named: true
  target_release_state_check_named: true
  rollback_or_revoke_plan_named: true
```

### 2. Execution

Execute only when the release issue explicitly approves the exact tag, title,
target commit, distribution path, final validation, and rollback or revoke plan.

Required execution evidence:

```yaml
release_execution_evidence:
  issue:
  tag:
  title:
  target_commit:
  approval_source:
  final_doctor: freshly_rerun
  release_state_docs_plan:
    - README.md
    - docs/bootstrap/10_roadmap.md
    - docs/handoff/CURRENT_STATUS.md
```

Stop before tag or GitHub release creation if approval, target commit, release
title, validation, or release-state doc plan is missing.

### 3. Closeout

After release execution, update only the docs authorized by the release issue or
bounded closeout issue. The closeout is not complete until:

```yaml
release_closeout_required:
  tag_exists: true
  github_release_exists: true
  final_validation_recorded: true
  current_status_post_release_accurate_or_followup_exists: true
  product_entry_docs_accurate_or_followup_exists: true
  release_state_check_passed_or_followup_exists: true
```

Run:

```bash
python3 scripts/asgk.py release-state-check --tag <tag> --release-title "<title>"
python3 scripts/asgk.py doctor
```

If `release-state-check` fails for the current release after release execution,
do not weaken the checker. Repair only current release state; apply
`docs/control/ISSUE_HYGIENE_GATE.md` before turning observations into work.

Use summary-first closeout evidence. Record release metadata, validation result,
key evidence, and limits; keep full routine logs in PR, CI, release, or issue
artifacts instead of repeating them in chat or closeout comments.

If the release changed `skills/*`, remind the operator that source-distributed
skills do not automatically update installed client skills. Do not write to
installed/global skill directories unless explicitly asked. Record
`installed_skill_sync` as `not_applicable`, `reminder_given`, or
`synced_by_explicit_user_request`.

## Stop States

- `blocked`: release target, release issue, approval, validation, or docs plan is missing.
- `requires_human`: release execution, tag/release creation, publication, visibility, dependency, schema, workflow, runtime adapter, installer, or v2.0 work is requested.
- `ready_for_execution_issue`: planning is complete, but execution still needs explicit issue approval.
- `ready_for_human_execution`: explicit release issue approval and final validation exist.
- `closeout_required`: release exists but release-state docs or validation are not closed out.
- `closed_out`: release exists, validation is recorded, release-state docs are accurate, and required checks pass.

## Exit Artifact

For planning: a release-prep issue or release-execution issue proposal.

For execution: release issue comment with target commit, validation summary,
approval source, tag/release URL, and rollback or revoke plan.

For closeout: PR body or issue comment showing `release-state-check`, `doctor`,
Current Status Impact, Merge Decision, remaining human gates, and whether a
bounded follow-up issue exists. If `skills/*` changed, include the installed
skill sync status.
