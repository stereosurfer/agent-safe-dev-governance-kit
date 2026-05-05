---
name: asgk-post-merge-closeout
description: Use after an ASGK pull request merges; verifies issue closure, GitHub closing references, closeout evidence, and whether CURRENT_STATUS needs a post-merge-safe refresh.
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
7. If status refresh is required, open a bounded issue or PR for that refresh.
8. Stop. Do not begin unrelated work.

## Stop States

- `blocked`: PR not merged, issue not satisfied, or closeout evidence is missing.
- `status_refresh_required`: repo-level recovery state would mislead the next session.
- `closed_out`: issue and status surfaces are accurate.

## Exit Artifact

Issue closeout comment, closed issue when appropriate, and a concise status-refresh decision.
