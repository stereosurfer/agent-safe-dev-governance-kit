---
name: asgk-current-status-handoff
description: Use when updating or auditing docs/handoff/CURRENT_STATUS.md; decides updated, not_applicable, or deferred status impact while keeping the file compact and post-merge-safe.
---

# ASGK Current Status Handoff

Use this skill for interrupted work, long-running handoff, milestone transitions, release closeout, or suspected stale `CURRENT_STATUS.md`.

## Authority

`CURRENT_STATUS.md` is a compact recovery surface, not a history log. Historical detail belongs in GitHub issues, PRs, comments, and merge commits.

## Default Rule

Do not update `CURRENT_STATUS.md` by habit. Default to `not_applicable` when a PR does not change active work, next safe action, release/public/license/milestone gates, or handoff recovery state.

The core test is:

```text
If this PR merges and CURRENT_STATUS.md is left unchanged, would the next session be misled into the wrong action?
```

If the answer is no, do not update the file.

## Procedure

1. Read `docs/control/CURRENT_STATUS_POLICY.md` when status behavior is unclear.
2. Compare live GitHub state with the current status file.
3. Choose one:
   - `updated`: repo-level recovery state changed and the file will remain accurate after merge.
   - `not_applicable`: PR detail is already represented by issue/PR and next safe action is unchanged.
   - `deferred`: status refresh is required for repo-level recovery safety but
     cannot be safely done in the same PR.
4. Use `updated` only when leaving the file unchanged would mislead the next session.
5. If updating, make the content post-merge-safe; do not point active work at the PR that is about to merge.
6. Keep active work out of `CURRENT_STATUS.md` unless it is repo-level recovery state.
7. Preserve compactness and the validation entrypoint.
8. Run status and current-status-impact checks when applicable.

## Decision Examples

```yaml
not_applicable:
  - README wording update with no next-action change
  - LICENSE text-form fix after license decision is already recorded
  - fixture-only change with no recovery-state impact
updated:
  - release execution completed
  - public visibility gate changed
  - milestone/readiness phase changed
  - next safe action changed
  - CURRENT_STATUS currently points to stale active work
deferred:
  - post-merge status cannot be known safely before merge
  - human gate must resolve before the next safe action can be written
```

Do not use `deferred` for cosmetic cleanup, historical observations, or PR
details that are already recoverable from the issue or PR. Those may be reported
as observations, but they do not create a status-refresh follow-up unless the
next session would otherwise take the wrong action.

## Stop States

- `blocked`: status would become self-stale after merge.
- `not_applicable`: no status update is needed.
- `deferred`: a bounded follow-up issue or PR is required because repo-level recovery would otherwise be unsafe.
- `post_merge_safe`: status remains accurate after merge.

## Exit Artifact

Updated `CURRENT_STATUS.md` or PR Current Status Impact section explaining why no update is needed.
