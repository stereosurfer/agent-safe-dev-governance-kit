# Work Unit State Model

This document is canonical for PR lifecycle and rollback transitions. PR
lifecycle, Merge Decision state, and proof state are related but orthogonal.

## Work Unit States

```yaml
states:
  idea:
    meaning: raw concept, not executable
  scoped:
    meaning: objective, scope, paths, checks, and acceptance exist
  in_progress:
    meaning: the authorized issue or PR is being worked
  pr_open:
    meaning: repository change exists in pull request
  needs_review:
    meaning: diff/report/checks require evaluation
  needs_revision:
    meaning: PR is useful but not acceptable yet
  blocked:
    meaning: missing input, failing gate, or human decision required
  accepted:
    meaning: acceptance criteria satisfied
  merged:
    meaning: durable repo state updated
  closed:
    meaning: issue closeout and handoff are complete
```

## Orthogonal PR And Decision State

```yaml
pr_lifecycle:
  draft:
    meaning: work is shareable, but formal review has not been requested
  reviewable:
    meaning: review is requested; this does not imply merge permission
  closed_unmerged:
    meaning: the attempt ended without changing the durable base branch
  merged:
    meaning: the accepted change reached the durable base branch

merge_decision:
  merge_blocked:
    meaning: the record declares at least one unresolved merge blocker
  merge_allowed:
    meaning: the record declares its named checks and human gates complete

proof_layers:
  body_coherence:
    meaning: the PR body is complete and internally coherent with its declared decision
  merge_decision:
    meaning: a merge_allowed claim is mechanically supported by body fields
  check_pr:
    meaning: live PR state, current checks, issue scope, paths, body decision, and hygiene are composed
```

`ready_for_review` moves a PR from `draft` to `reviewable`. It does not make the
PR merge-eligible. `merge_allowed` is not Agent approval, low-risk inference, or
merge authority. Full checkable PR state belongs to `check-pr`; a human or
canonical policy still makes the merge decision.

## Forward Transition

1. `scoped -> in_progress`: create a task branch from current `main`.
2. `in_progress -> pr_open`: open a draft PR with `result: merge_blocked`.
3. Run file-backed `body-coherence` preflight. A coherent blocked body may
   truthfully record pending or false gates.
4. CI checks the declared blocked body and reports that merge remains blocked.
5. `draft -> reviewable`: mark ready for review while the durable result remains
   `merge_blocked`.
6. When human review applies, a human reviews the current head and diff; a later
   code commit makes that review stale unless reaffirmed. When no gate applies,
   record the durable no-gate risk/path determination.
7. Only after all required evidence and either applicable human gates or the
   durable no-gate determination are complete, set the exact-true gates to true,
   complete the attribution and boundary fields, and change the durable result
   to `merge_allowed`.
8. Run strict `merge-decision`, then live `check-pr`.
9. `accepted -> merged -> closed` only after the applicable human or policy
   merge decision and closeout.

## Revision And Rollback Transition

- A validation failure or stale evidence returns the durable result to
  `merge_blocked` before further work.
- When code revision is required, record the blocker and convert the PR to draft.
  Review tied to an older head is not reusable without reaffirmation.
- When the approach is wrong or a human decision rejects it, record the reason
  and return the durable result to `merge_blocked` before closing the PR
  unmerged. Preserve its branch, commits, CI, comments, and decision record. If
  the issue still authorizes the work, restart from current `main` on a fresh
  branch.
- A `closed_unmerged` attempt did not change `main` and does not require a
  repository revert.
- Rollback of an already merged semantic unit requires a separately authorized
  revert. Do not delete or rewrite history as the rollback mechanism.

## Transition Rules

- `idea` cannot go directly to `pr_open` or `merged`.
- `scoped` requires a GitHub issue or PR for executable work when
  GitHub is available. A task packet may refine the scope, but it cannot be the
  primary authorization for file edits.
- `accepted` requires validation evidence and current-head human review when a
  human gate applies.
- A coherent `merge_blocked` body may be reviewable, but it is never
  merge-eligible.
- `merged` requires a complete Merge Decision Record, live PR eligibility, and
  the applicable human or policy merge decision. Human approval does not replace
  missing checks, scope, or evidence.
