---
name: asgk-gatekeeper
description: Use when checking ASGK PR readiness with existing repo validators and GitHub metadata; reports blocked, eligible, or requires_human without approving merge or adding a new gate.
---

# ASGK Gatekeeper

Use this skill for PR readiness checks, CI follow-up, or pre-merge review.

## Authority

This skill selects and sequences existing checks. It must not create new approval authority. Use `blocked`, `eligible`, or `requires_human`; do not say `approved`.

It distinguishes three proof layers: `body-coherence`, strict
`merge-decision`, and live `check-pr`. Passing an earlier layer does not imply a
later one.

## Minimum Inputs

- PR number.
- Issue number.
- Local branch state when relevant.
- Changed paths.

## Procedure

1. Confirm the PR is open and associated with the intended issue.
2. For GitHub PR event auto-routing, select body validation from the durable
   `merge_decision.result`:
   - `merge_blocked` selects `body-coherence` and remains blocked from merge,
     whether draft or ready for review;
   - `merge_allowed` selects strict `merge-decision`;
   - missing or invalid result fails closed.
   File-backed preflight explicitly selects `body-coherence`; direct CLI and
   `check-pr` explicitly select strict `merge-decision`. Draft status alone must
   not select the validation mode.
3. When merge readiness is being assessed, independently require the PR to be
   non-draft. Ready for review means only that review was requested.
4. Run or inspect:
   - `python3 scripts/asgk.py doctor`
   - repository-local PR readiness checks when available. In this ASGK source
     repository, that is usually `python3 scripts/asgk.py check-pr --pr
     <number>`. In target repositories that do not implement `check-pr`, record
     it as unavailable and use the target's local PR body checks, GitHub CI and
     status, closing issue references, changed paths, and issue acceptance
     evidence instead.
   - PR CI status
   - `current-status-impact-check` when `docs/handoff/CURRENT_STATUS.md` changed
   - changed-path hygiene when local changed paths are available
5. Treat `check-pr` as the full checkable PR composition. It must always use
   strict `merge-decision`, independently reject `merge_blocked`, and check live
   open/non-draft/mergeable state, non-blocking review state, current checks,
   issue authority, allowed paths, and hygiene.
6. For repeated runs of the same check identity on one head, evaluate the latest
   reliably timestamped run. CheckRun identity includes its name plus
   workflow/app/provider; repeated same-name runs without that provider
   component fail closed. Keep older runs as superseded evidence. Latest
   failure or pending blocks; ambiguous ordering fails closed.
7. Identify human-gated triggers from changed paths and issue scope. When one
   applies, require a durable current-head record with `decision: approved`.
   `changes_requested` or `rejected` requires `human_gates_checked: false` and
   `result: merge_blocked`. When no gate applies, require a durable no-gate
   risk/path determination. A boolean, green workflow, or prior-PR review is not
   approval evidence. A new code commit invalidates older review unless
   reaffirmed.
8. Compare the PR's completion claim with the issue acceptance sheet. Named
   checks passing means only those checks passed; it does not prove semantic
   correctness, upgrade completeness, install completeness, or stale-reference
   cleanup unless the issue required and the PR records that evidence.
9. If validation fails or evidence becomes stale, require the durable result to
   return to `merge_blocked` before more work. Record the blocker before
   converting the PR to draft for revision.
10. If the approach is wrong, report the safe rollback: record the abandonment
    reason, return the durable result to `merge_blocked`, close the PR
    unmerged, preserve its branch/commits/CI/comments/decision record, and
    restart authorized work from current `main` on a fresh branch. Do not reuse
    review from the closed-unmerged diff.
11. Report only the narrow readiness state.

## Stop States

Choose exactly one state, in this precedence order: `blocked`,
`requires_human`, then `eligible`.

- `blocked`: a non-human validator or current CI failure exists, evidence is
  stale or ambiguous, issue-required completion evidence is missing, or the
  durable result is `merge_blocked` for a reason other than a sole named human
  decision. A coherent blocked PR may still be ready for review.
- `requires_human`: no non-human blocker remains and the only unresolved
  condition is a specific human-gated decision, issue/policy-required semantic
  acceptance, or a human-only merge decision that no canonical policy
  delegates. This may describe a coherent `merge_blocked` body awaiting that
  decision, or mechanically clear work that the skill cannot authorize.
  Routine review requested by an ordinary ready-for-review PR does not by
  itself create this state.
- `eligible`: strict `merge-decision` and live `check-pr` pass, and either no
  human gate applies or the applicable current-head approval plus canonical
  policy and the current issue explicitly authorize the escalated path. This
  does not infer low-risk status; a human or canonical policy still makes the
  merge decision.

## Exit Artifact

PR comment or final report listing checks, evidence source, blockers, and the next safe action.
