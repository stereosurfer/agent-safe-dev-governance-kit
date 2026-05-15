# Compact Handoff Profile

Status: opt-in profile. This file does not make compact handoff the default.

Compact handoff may shorten work-unit recovery notes only when it keeps
`CURRENT_STATUS.md` freshness checkable. A compact handoff is enough when the
repo-level recovery surface is already accurate and the active work detail lives
in the GitHub issue, PR, or handoff file.

## Required Shape

```yaml
compact_handoff:
  active_issue:
  active_pr:
  branch:
  durable_source_of_truth:
  objective:
  state:
  allowed_paths:
  validation_status:
    status:
    evidence:
  current_status_impact:
    status: updated | not_applicable | deferred
    reason:
    current_status_updated_in_this_pr: true | false
    post_merge_safe: true | false | not_applicable
    follow_up_issue: none | "#<number>"
  next_safe_action:
```

## Status Decision Rules

Use `not_applicable` only when leaving `docs/handoff/CURRENT_STATUS.md`
unchanged would not mislead the next session. The current-status active work
must not still point at a completed issue, PR, or branch.

Use `updated` only when the repository recovery state changed and the resulting
`CURRENT_STATUS.md` is post-merge-safe. The status file must pass:

```bash
python3 scripts/asgk.py status-check --file docs/handoff/CURRENT_STATUS.md
```

Use `deferred` only when a same-PR status update would be unsafe or
self-staling. The compact handoff must name a follow-up issue or a material next
safe action.

## Checker

Run:

```bash
python3 scripts/asgk.py compact-handoff-check \
  --file handoff.yaml \
  --current-status docs/handoff/CURRENT_STATUS.md \
  --completed-issue "#123" \
  --completed-pr "#124" \
  --completed-branch codex/example
```

The checker validates compact handoff fields, runs the current-status freshness
check, blocks stale active-work references, and always reports
`low_risk_inferred: false`.

## Non-Goals

- Do not replace issue, PR, CI, or Merge Decision authority with a handoff.
- Do not infer low-risk status from compact handoff.
- Do not use compact handoff to hide stale active work.
- Do not make `CURRENT_STATUS.md` a history log.
