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
6. Keep closeout comments compact. Link to the PR, release, CI, or validator
   evidence instead of repeating full validation logs already preserved there.
7. If the merged PR changed `skills/*`, remind the operator that
   source-distributed skills do not automatically update installed client
   skills. Do not write to installed/global skill directories unless explicitly
   asked. Record `installed_skill_sync` as `not_applicable`, `reminder_given`,
   or `synced_by_explicit_user_request`.
8. Decide whether `docs/handoff/CURRENT_STATUS.md` needs refresh under the current-status policy.
9. Recommend no status refresh when `CURRENT_STATUS.md` remains accurate for the next session.
10. Recommend a status refresh only when stale repo-level recovery state would mislead the next session.
11. For the current issue being closed after PR #272 merged, ensure the GitHub
    issue closeout comment includes one bounded decision-analysis block using
    `docs/handoff/ISSUE_CLOSEOUT_REVIEW_RULES.md` as the writing guide. Bounded means
    scope-limited and evidence-dense, not abbreviated, lossy, simplified, or
    summary-only.
12. Apply `docs/control/ISSUE_HYGIENE_GATE.md`: do not scan historical issues or
    create repo-file repair work solely to store routine closeout reviews.
13. If the issue comment cannot be written or closeout evidence is unclear,
    stop with a blocker.
14. If status refresh is required, open a bounded issue or PR only when
    repo-level recovery would otherwise mislead the next session.
15. Stop. Do not begin unrelated work.

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
  - current issue closeout performed after PR #272 merged
review_entry_not_required_when:
  - issue closed before PR #272 merged
  - historical issue is observed during health check but is not the current closeout target
review_entry_quality_floor:
  - preserve decision reasons
  - preserve rejected paths
  - preserve applicability boundaries
  - preserve evidence links
  - preserve known limits
review_entry_missing_result:
  - current post-#272 closeout is blocked until the GitHub issue closeout comment contains the required decision-analysis block
legacy_gap_result:
  - apply docs/control/ISSUE_HYGIENE_GATE.md
```

Issue Closeout Reviews are mandatory closeout evidence, but they do not override
AGENTS.md, current issue or PR scope, validators, control policies, merge
decisions, CURRENT_STATUS, or human gates.

## Stop States

- `blocked`: PR not merged, issue not satisfied, closeout evidence is missing, or the required issue closeout decision-analysis comment is missing.
- `no_status_refresh_needed`: issue and status surfaces are accurate.
- `status_refresh_required`: repo-level recovery state would mislead the next session.
- `closed_out`: issue and status surfaces are accurate.

## Exit Artifact

Issue closeout comment, closed issue when appropriate, and a concise status-refresh decision: `no_status_refresh_needed`, `status_refresh_required`, or `blocked`.
