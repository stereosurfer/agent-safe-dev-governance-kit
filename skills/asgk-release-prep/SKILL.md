---
name: asgk-release-prep
description: Use for ASGK source-only release preparation, human-gated release execution, and release-state closeout; requires release issues to name product-entry and handoff docs, explicit approval, final validation, and release-state-check before closeout.
---

# ASGK Release Prep

Use this skill for source-only ASGK release planning, release execution, or
release-state closeout.

## Authority

This Skill and `release-state-check` do not authorize a release. Any release or
publication decision or execution—including tag creation, GitHub Release
creation, package publication, or external distribution—requires a separate
GitHub release-execution issue with explicit human approval for the exact tag,
title, target commit, distribution path, and rollback or revoke plan. Other
restricted operations remain governed by
`docs/control/HUMAN_GATED_OPERATIONS.md`; a release issue authorizes only the
exact actions it names.

Program execution authorization for repo-local source maintenance is not
release approval and is not current-head OWNER review. It must not be used as
the `approval_source` for release execution or described as review of an unseen
head or diff.

If this skill conflicts with `AGENTS.md`, the release issue, a PR, or
`docs/control/SOURCE_ONLY_RELEASE_POLICY.md`, stop and use the durable repo
authority.

## Required Inputs

- Release target: tag, title, target commit, and source-only boundary.
- Release issue with explicit human approval before execution.
- Local release-state documents mechanically checked for closeout:
  - `README.md`
  - `docs/handoff/CURRENT_STATUS.md`
  - `docs/control/SOURCE_ONLY_RELEASE_POLICY.md`
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
  release_state_inputs:
    - README.md
    - docs/handoff/CURRENT_STATUS.md
    - docs/control/SOURCE_ONLY_RELEASE_POLICY.md
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

A passing `release-state-check` is local-document evidence only. It does not
prove that a tag or GitHub Release exists, establish semantic release readiness,
or satisfy human approval or publication authority.

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
- `requires_human`: a release/publication decision or execution is requested,
  including tag or GitHub Release creation, package publication, external
  distribution, or any other operation named by Human-Gated Operations.
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
