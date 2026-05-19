---
name: asgk-pr-evidence-merge-decision
description: Use when opening or updating an ASGK pull request body; structures validation evidence, Current Status Impact, Merge Decision Record, Known Gaps, and Handoff Report without turning prose into approval authority.
---

# ASGK PR Evidence And Merge Decision

Use this skill when creating a PR, refreshing PR evidence after CI, or preparing human review.

## Authority

This skill formats evidence. It does not certify low-risk status or approve merge. Merge authority remains in the issue, PR, repo policy, CI, validators, and human gates.

## Required Inputs

- GitHub issue number and title.
- Changed file list.
- Validation commands and outputs.
- CI status when available.
- Current Status Impact decision.
- Known human-gated triggers.
- Issue acceptance sheet and any required completeness checks for the work type.

## Evidence Labels

Use precise evidence sources:

- `freshly_rerun`
- `github_actions`
- `fixture`
- `repo_file`
- `inferred_from_merged_pr`
- `not_run`

Each evidence item needs a limit or non-proof.

## Procedure

1. Fill Summary, Task Reference, Changed Files, Validation, Evidence Of Completion, Scope Boundaries, Runtime Output Status, Merge Decision, Known Gaps, and Handoff Report.
2. Use `Closes #N` when the PR is expected to close the work-unit issue.
3. Mark `result: merge_blocked` while draft, CI pending, live `check-pr` failing, or human gates remain.
4. Mark `checks_passed: true` only when validation evidence supports it. This
   means the named checks passed; it is not a claim of semantic correctness,
   upgrade completeness, install completeness, or stale-reference cleanup unless
   those checks are explicitly listed with evidence.
5. Do not use chat-only authority or vague `passed` claims without evidence.
6. Use summary-first validation evidence. Record command name, result, key
   evidence, and limits; do not paste full routine command logs when PR, CI, or
   issue artifacts already preserve the full output. Include fuller detail only
   for failures, blockers, material behavior changes, or reviewer decisions.
7. For upgrade or adoption PRs, record the compact completion label used by the
   relevant audit skill, such as `full_target_upgrade_alignment`,
   `tooling_subset_only`, or `partial_followup_required`, and name the
   stale-reference and path-existence evidence when completion is claimed.
8. Before creating or editing a PR body, run local file-backed PR body
   preflight when available:

   ```bash
   python3 scripts/pr_governance_preflight.py check --body-file <body-file>
   ```

   Use the same wrapper for `gh pr create` or `gh pr edit` when possible.

## Stop States

- `blocked`: issue, changed paths, validation, Current Status Impact, or issue-required completeness evidence is missing.
- `requires_human`: escalated paths or human-gated operations are touched.
- `pr_body_ready`: PR body has evidence and can be checked by policy gate.

## Exit Artifact

Updated PR body and, when useful, an issue comment summarizing local validation, CI, live `check-pr`, and remaining blockers.
