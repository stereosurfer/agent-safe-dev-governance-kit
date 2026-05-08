---
name: asgk-post-merge-closeout
description: Use after an ASGK pull request merges; verifies issue closure, GitHub closing references, closeout evidence, and recommends CURRENT_STATUS refresh only when stale status would mislead the next session.
---

# ASGK Post-Merge Closeout

Use this skill immediately after a PR merges or when the user says a PR has merged.

## Authority

This skill closes only work that is already satisfied by durable GitHub and repo evidence. It must not start the next work unit unless a separate durable issue already authorizes it.

## Required Inputs

- Merged PR number.
- Expected closing issue number.
- Merge commit.
- Latest `main`.

## Procedure

1. Confirm the PR is merged and record the merge commit.
2. Inspect `closingIssuesReferences`.
3. Inspect the expected issue state.
4. If the issue is still open but satisfied, comment evidence and close it.
5. If the issue was not satisfied, stop with a blocker report.
6. Decide whether `docs/handoff/CURRENT_STATUS.md` needs refresh under the current-status policy.
7. Recommend no status refresh when `CURRENT_STATUS.md` remains accurate for the next session.
8. Recommend a status refresh only when stale repo-level recovery state would mislead the next session.
9. Decide whether the issue qualifies for an advisory Issue Closeout Review in
   `docs/handoff/ISSUE_CLOSEOUT_REVIEWS.md`.
10. If the ledger is in the current issue's allowed paths, update it with one
    compact entry; otherwise record `no_ledger_update` in the issue closeout
    comment or open a bounded follow-up issue only when the lesson is genuinely
    reusable.
11. If status refresh is required, open a bounded issue or PR for that refresh.
12. Stop. Do not begin unrelated work.

## Closeout Decision Test

```yaml
status_refresh_required_when:
  - active work still points to the merged PR, closed issue, or merged branch
  - next safe action points to completed pre-merge work
  - release, public visibility, license, milestone, readiness, or handoff recovery state changed
  - leaving CURRENT_STATUS unchanged would make the next session choose the wrong next action
status_refresh_not_required_when:
  - CURRENT_STATUS already describes the post-merge repo state accurately
  - PR did not change active work, next safe action, or gated repo-level state
  - issue and PR history already hold the completed-work details
```

## Issue Closeout Review Test

```yaml
review_entry_required_when:
  - issue has more than one PR
  - issue is a release train or milestone closeout
  - issue changes validation behavior, docs/control/**, .github/**, or scripts/**
  - issue includes human-gated authorization
  - issue had failed attempts or repeated correction loops
  - issue produced a reusable operational lesson
review_entry_optional_when:
  - single small docs-only PR
  - typo, formatting, or simple target-file update
review_entry_not_needed_when:
  - issue is duplicate, abandoned, or has no reusable lesson
self_bootstrap_exception:
  - issue creates or materially revises docs/handoff/ISSUE_CLOSEOUT_REVIEWS.md
  - reusable rule is already captured in the ledger guidance and PR evidence
  - issue closeout comment records no_ledger_update with this reason
```

Issue Closeout Reviews are advisory. They do not override AGENTS.md, current
issue or PR scope, validators, control policies, merge decisions, CURRENT_STATUS,
or human gates.

## Stop States

- `blocked`: PR not merged, issue not satisfied, or closeout evidence is missing.
- `no_status_refresh_needed`: issue and status surfaces are accurate.
- `status_refresh_required`: repo-level recovery state would mislead the next session.
- `closed_out`: issue and status surfaces are accurate.

## Exit Artifact

Issue closeout comment, closed issue when appropriate, and a concise status-refresh decision: `no_status_refresh_needed`, `status_refresh_required`, or `blocked`.
