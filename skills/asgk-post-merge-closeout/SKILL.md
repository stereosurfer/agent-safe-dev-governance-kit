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
9. If status refresh is required, open a bounded issue or PR for that refresh.
10. Stop. Do not begin unrelated work.

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

## Stop States

- `blocked`: PR not merged, issue not satisfied, or closeout evidence is missing.
- `no_status_refresh_needed`: issue and status surfaces are accurate.
- `status_refresh_required`: repo-level recovery state would mislead the next session.
- `closed_out`: issue and status surfaces are accurate.

## Exit Artifact

Issue closeout comment, closed issue when appropriate, and a concise status-refresh decision: `no_status_refresh_needed`, `status_refresh_required`, or `blocked`.
