---
name: asgk-pr-evidence-merge-decision
description: Use when opening or updating an ASGK pull request body; structures validation evidence, Current Status Impact, Merge Decision Record, Known Gaps, and Handoff Report without turning prose into approval authority.
---

# ASGK PR Evidence And Merge Decision

Use this skill when creating a PR, refreshing PR evidence after CI, or preparing human review.

## Authority

This skill formats evidence. It does not certify low-risk status or approve merge. Merge authority remains in the issue, PR, repo policy, CI, validators, and human gates.

PR lifecycle, Merge Decision state, and proof state are orthogonal. Ready for
review means review was requested; it does not mean merge-ready.

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
3. Open the normal work path as a draft with `result: merge_blocked`.
   File-backed create/edit preflight checks `body-coherence`, not merge
   eligibility. A coherent blocked body may truthfully use `checks_passed` and
   `human_gates_checked` values `true`, `pending`, or `false`; blank, missing,
   or unknown states remain invalid. `allowed_paths_checked`,
   `expected_output_checked`, and `validation_evidence_checked` must always be
   the literal unquoted token `true`; quoted `"true"` is a string and does not
   satisfy an exact-true gate.
4. A draft may be marked ready for review while it remains `merge_blocked`.
   Ready for review requests review and does not authorize `merge_allowed`.
5. Mark `checks_passed: true` only when validation evidence supports it. This
   means the named checks passed; it is not a claim of semantic correctness,
   upgrade completeness, install completeness, or stale-reference cleanup unless
   those checks are explicitly listed with evidence.
6. When a human gate applies, keep `human_gates_checked` pending or false until
   a durable current-head record says `decision: approved`. A
   `changes_requested` or `rejected` decision requires
   `human_gates_checked: false` and `result: merge_blocked`. When no gate
   applies, cite the durable no-gate risk/path determination. The boolean is not
   evidence. Do not reuse review from a prior PR or an older head after new code
   commits unless the human reaffirms it.
7. Only after all required evidence and human gates are complete, update every
   required mechanical gate to true and set `result: merge_allowed`. For GitHub
   PR event auto-routing, the declared result selects the body-level mode:
   - `merge_blocked` -> `body-coherence`
   - `merge_allowed` -> strict `merge-decision`
   - missing or invalid result -> fail closed
   File-backed preflight explicitly selects `body-coherence`; direct CLI and
   `check-pr` explicitly select strict `merge-decision`. Draft status must not
   select the mode.
8. After strict `merge-decision` passes, run live repository-local PR
   validation. In this ASGK source repository, that is usually `python3
   scripts/asgk.py check-pr --pr <number>`. `check-pr` independently rejects
   drafts and `merge_blocked` results and composes live mergeability, review,
   latest checks, issue authority, changed paths, and hygiene. In target
   repositories without `check-pr`, record it as unavailable or not run with
   limits and cite the available repo-local checks instead.
9. Do not use chat-only authority or vague `passed` claims without evidence.
10. Use summary-first validation evidence. Record command name, result, key
   evidence, and limits; do not paste full routine command logs when PR, CI, or
   issue artifacts already preserve the full output. Include fuller detail only
   for failures, blockers, material behavior changes, or reviewer decisions.
11. For adoption or material-upgrade PRs, cite the durable assessment's
   recommendation, minimum bounded scope, target-owned state to preserve,
   material evidence, proof limits, and any exact `next_action_gate`. Do not
   require a fixed completion label or treat the assessment as approval.
12. Before creating or editing a PR body, run local file-backed PR body
   preflight when available:

   ```bash
   python3 scripts/pr_governance_preflight.py check --body-file <body-file>
   ```

   Use the same wrapper for `gh pr create` or `gh pr edit` when possible.
   Passing preflight means body coherence only; it infers neither merge
   eligibility, low-risk status, nor human approval.
13. If validation fails or evidence becomes stale, return the body to
   `merge_blocked` before further work and record the blocker before converting
   the PR to draft.
14. If the approach is wrong, record the abandonment reason and return the
   durable result to `merge_blocked` before closing the PR without merge.
   Preserve its branch/commits/CI/comments/decision record and restart
   authorized work from current `main` on a new branch. Do not delete history
   or transfer review from the abandoned diff.

## Stop States

Choose exactly one state. Use `closed_unmerged` for a terminated attempt;
otherwise apply `blocked`, `requires_human`, `pr_body_ready`, then
`merge_decision_clear` in that precedence order.

- `closed_unmerged`: the terminated attempt is preserved as evidence and did
  not change `main`.
- `blocked`: a non-human issue, changed-path, validation, Current Status Impact,
  or issue-required completeness defect remains.
- `requires_human`: no non-human defect remains and the only unresolved
  condition is a specific applicable human gate or a human-only merge decision
  that no canonical policy delegates.
- `pr_body_ready`: the PR body is coherent for its declared `merge_blocked`
  decision and is ready for ordinary review; no merge eligibility is implied.
- `merge_decision_clear`: `merge_allowed` and all required mechanical fields
  pass strict `merge-decision`; live `check-pr` remains, or it passed without a
  human-only blocker. A human or canonical policy still makes the final merge
  decision.

## Exit Artifact

Updated PR body and, when useful, an issue comment summarizing local validation,
CI, repository-local PR readiness evidence, unavailable checks with limits, and
remaining blockers.
