# Human-Gated Operations

Human approval is required before:

- destructive git actions;
- force push;
- deleting branches;
- security boundary changes;
- storage boundary changes;
- schema major version changes;
- database migrations;
- new dependency;
- new parser/model dependency;
- new cloud egress;
- Google Drive API integration;
- MCP tool or MCP write capability;
- externalized responsibility moved into repo;
- raw source retention;
- publication/export/release decision;
- milestone closure;
- high-risk merge.

## Required human-gate record

```yaml
human_gate:
  operation:
  reason:
  risks:
  rollback_plan:
  approval_source:
  reviewed_head:
  reviewed_diff:
  decision: approved | changes_requested | rejected
  decided_by:
  decided_at:
  reaffirmed_after_head_change: true | false | not_applicable
```

The approval source must be durable GitHub or repository evidence. When a human
gate applies, `human_gates_checked: true` means the current-head record says
`decision: approved`. `changes_requested` or `rejected` requires
`human_gates_checked: false` and `result: merge_blocked`. The boolean is not
evidence and an Agent must not set it from its own judgment, a green workflow,
or review of a prior PR.

Human review applies to the recorded head and diff. A later code commit makes
the review stale unless the human reaffirms it for the new head. A review tied
to a closed-unmerged or superseded PR must not be transferred to replacement
work.

The body checker may validate record consistency, but it cannot certify human
approval. A human-gated PR remains `requires_human` even when its mechanical
Merge Decision and live `check-pr` checks pass, unless both canonical policy
and the current issue explicitly authorize that escalated merge path.

If no human-gated operation applies, record the durable risk/path determination
that supports `human_gates_checked: true`. The boolean alone is never the
reasoning record.

## Revision And Rollback

- If validation fails, evidence becomes stale, or changes are requested, set the
  durable Merge Decision to `merge_blocked` before continuing.
- Record the blocker before converting a PR to draft for revision.
- If the approach is wrong, record the abandonment reason and return the
  durable result to `merge_blocked` before closing the PR unmerged. Preserve
  its branch, commits, CI, comments, and decision record, then restart
  authorized work from current `main` on a new branch.
- A closed-unmerged attempt does not require reverting `main`.
- Reverting a merged semantic unit requires separate authorization and must
  preserve history.
