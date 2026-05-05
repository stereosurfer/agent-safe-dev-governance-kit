---
name: asgk-current-status-handoff
description: Use when updating or auditing docs/handoff/CURRENT_STATUS.md; decides updated, not_applicable, or deferred status impact while keeping the file compact and post-merge-safe.
---

# ASGK Current Status Handoff

Use this skill for interrupted work, long-running handoff, milestone transitions, release closeout, or suspected stale `CURRENT_STATUS.md`.

## Authority

`CURRENT_STATUS.md` is a compact recovery surface, not a history log. Historical detail belongs in GitHub issues, PRs, comments, and merge commits.

## Procedure

1. Read `docs/control/CURRENT_STATUS_POLICY.md` when status behavior is unclear.
2. Compare live GitHub state with the current status file.
3. Choose one:
   - `updated`: repo-level recovery state changed and the file will remain accurate after merge.
   - `not_applicable`: PR detail is already represented by issue/PR and next safe action is unchanged.
   - `deferred`: status refresh is required but cannot be safely done in the same PR.
4. Keep active work out of `CURRENT_STATUS.md` unless it is repo-level recovery state.
5. Preserve compactness and the validation entrypoint.
6. Run status and current-status-impact checks when applicable.

## Stop States

- `blocked`: status would become self-stale after merge.
- `deferred`: a bounded follow-up issue or PR is required.
- `post_merge_safe`: status remains accurate after merge.

## Exit Artifact

Updated `CURRENT_STATUS.md` or PR Current Status Impact section explaining why no update is needed.
