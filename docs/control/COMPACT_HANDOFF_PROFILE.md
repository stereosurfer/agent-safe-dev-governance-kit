# Compact Handoff Profile

Status: opt-in conditional projection. It is not a second handoff contract.

A compact handoff uses the complete canonical core from
`docs/control/HANDOFF_PACKET.md` under the `compact_handoff` root and adds one
freshness decision for `CURRENT_STATUS.md`.

## Shape

The following is an illustrative W3B self-use example, not current work
authority. Its issue, PR, branch, and next action become historical example data
when that work unit closes.

```yaml
compact_handoff:
  active_issue: "#333 ASGK 2.0 W3B"
  active_pr: "#334 W3B handoff and CURRENT_STATUS convergence"
  durable_source_of_truth:
    - "GitHub issue #333"
    - "GitHub PR #334"
  branch: "codex/asgk-2-w3b-handoff-status-convergence"
  objective: "Converge typed handoff and recovery-only CURRENT_STATUS."
  current_state: "Implementation and validation are complete; human review is pending."
  remaining:
    - "Obtain current-head human approval."
  allowed_paths:
    - "docs/control/HANDOFF_PACKET.md"
  modified_files:
    - "docs/control/HANDOFF_PACKET.md"
  non_goals:
    - "Do not implement W3C."
  must_not_do:
    - "Do not merge without current-head human approval."
  must_read:
    - "AGENTS.md"
    - "GitHub issue #333"
    - "GitHub PR #334"
  validation_status:
    status: "pass"
    evidence:
      - "python3 scripts/asgk.py doctor: pass"
    reason: "The named local validation completed successfully."
  blockers:
    - "current-head human approval is not yet recorded"
  next_safe_action: "Review the exact PR head and record the human decision."
  current_status_impact:
    status: updated
    reason: "The repo-level recovery state changes from W3A to the next W3C work unit."
    current_status_updated_in_this_pr: true
    post_merge_safe: true
    follow_up_issue: none
```

The schema is `schemas/handoff_packet.schema.json`. Compact handoff does not
rename, omit, or reinterpret a core field.

## Evaluation Order

```text
canonical core evaluator
  -> only if pass: current_status_impact shape and consistency
  -> only then: supplied CURRENT_STATUS freshness checks
```

If the core fails, `compact-handoff-check` returns the original `HP_*` findings
and `freshness_checked: false`. It does not hide the core reason behind a
generic compact failure.

After a valid core, compact-only findings use stable `CH_*` codes for:

- missing or malformed `current_status_impact`;
- inconsistent update, post-merge-safe, and deferral claims;
- a missing or invalid CURRENT_STATUS file;
- caller-supplied completed issue, PR, or branch references that remain active;
- a pre-merge-only next safe action.

## Status Decision Rules

Use `not_applicable` only when leaving
`docs/handoff/CURRENT_STATUS.md` unchanged would not mislead a new session.

Use `updated` only when the resulting status file describes the repository
after merge. Both booleans must be true.

Use `deferred` only when a same-PR update would be unsafe. Name a follow-up
issue or preserve one material next safe action.

## Command

```bash
python3 scripts/asgk.py compact-handoff-check \
  --handoff handoff.yaml \
  --current-status docs/handoff/CURRENT_STATUS.md \
  --completed-issue "#333" \
  --completed-pr "#334" \
  --completed-branch codex/asgk-2-w3b-handoff-status-convergence \
  --json
```

`--file` remains an input spelling for existing callers and invokes the same
implementation.

## Proof Boundary

The compact command proves only:

- the same local core shape and material-content checks as `handoff-check`;
- local `current_status_impact` type and consistency checks;
- the local status-check result;
- absence of caller-supplied completed refs in the status file's active block.

It does not query GitHub, decide whether a status update is semantically
correct, infer low risk, approve a handoff, or authorize merge.

## Non-Goals

- Do not replace issue, PR, CI, or Merge Decision authority.
- Do not create a smaller competing handoff core.
- Do not infer low-risk status from validator success.
- Do not use compact handoff to hide stale active work.
- Do not make CURRENT_STATUS a completed-work ledger.
