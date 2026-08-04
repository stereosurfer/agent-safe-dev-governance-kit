# Human-Gated Operations

Human approval is required before:

- destructive git actions;
- force push;
- deleting branches;
- repository visibility, permissions, rules, settings, or topics;
- credentials, secrets, or private material;
- external-system writes other than routine issue/PR metadata, or
  target-repository writes;
- security boundary changes;
- storage boundary changes;
- schema major version changes;
- database migrations;
- dependency graph changes;
- new parser/model dependency;
- new cloud egress;
- Google Drive API integration;
- MCP tool or MCP write capability;
- externalized responsibility moved into repo;
- raw source retention;
- publication/export/release decision;
- milestone or program-controller closure;
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

## Program Execution Authorization

An OWNER may authorize execution of a bounded multi-PR program without
repeating permission prompts for every source PR. This is execution authority,
not current-head human review.

Use this path only when:

- the program issue durably names the work graph and OWNER authorization;
- a durable OWNER-approved `scope_source` pre-exists the child issue and names
  the exact work-unit path/action set; the child issue may equal or narrow it
  but must not broaden it;
- the current child issue explicitly invokes that program authorization and
  carries exact allowed paths, stop conditions, rollback, and validation;
- the work changes tracked source only, has no external side effect beyond
  routine issue/PR metadata, and is recoverable completely by ordinary Git
  revert;
- scope and semantics remain inside the named program;
- independent cold review, required checks, CI, strict `check-pr`, and close-out
  remain mandatory; and
- no operation in this document's human-gated list applies.

When the path is used, record:

```yaml
program_execution_authorization:
  program_issue:
  owner_authorization_source:
  scope_source:
  current_issue:
  authorized_work_unit:
  current_issue_scope_is_subset_or_equal: true | false
  repo_local_only: true | false
  external_side_effects: none_beyond_issue_pr_metadata | present | unknown
  ordinary_git_revert_available: true | false
  current_head:
  current_diff:
  semantic_scope_match_review:
  no_human_gate_determination:
  independent_review:
  human_gated_operations: []
  decision: authorized | not_authorized
  reason:
```

For a protected source path, this record supports an autonomous merge only when
both canonical policy and the current child issue explicitly authorize the
program-scoped reversible path. A parent program grant alone is insufficient.

The OWNER program grant may remain valid across code commits. The current-head
scope review, no-human-gate determination, independent review, CI, and
`check-pr` do not: refresh them after every commit.

This path is non-self-amending. A PR that changes Human-Gated Operations,
program eligibility, merge authority, or gate enforcement/non-inference
semantics—including by creating, removing, loosening, tightening, or
reclassifying them—must use the stricter of baseline and proposed policy and
cannot invoke the path it changes. That PR requires current-head human approval.

The record must never say or imply that the OWNER reviewed an unseen current
head or diff. It does not approve release/publication, milestone closure,
external-system writes other than routine issue/PR metadata, target-repository
writes, private material, credentials,
dependency graph changes, cloud/API/MCP capability, security or storage
boundaries, repository settings, destructive history/branch operations, or any
other human-gated operation. Routine issue/PR metadata is allowed when it
changes no repository setting, visibility, permission, or rule.

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
