---
name: asgk-startup
description: Use when starting or resuming work in an ASGK-governed repository; reads the minimal startup set, checks live GitHub PR/issue state, reconciles CURRENT_STATUS drift, and identifies the next safe action without creating new authority.
---

# ASGK Startup

Use this skill at the beginning of an ASGK repository session, after a context reset, or when the user asks to continue from current project state.

## Authority

This skill does not create scope, approval, or merge authority. If it conflicts with `AGENTS.md`, the current GitHub issue or PR, or repo control docs, stop and use the repo authority.

## Minimum Reads

1. `AGENTS.md`
2. `README.md`
3. `docs/handoff/CURRENT_STATUS.md`
4. Live open PR list
5. Live open issue list only after open PRs are checked

Use `docs/DOCUMENT_MAP.md` only if the work unit points to additional context.

## Procedure

1. Check live open PRs before selecting an issue.
2. If a PR is open, treat it as the current work boundary and inspect only what
   is needed for that PR. Distinguish its GitHub lifecycle state from its
   `merge_decision.result`:
   - draft or ready-for-review with `merge_blocked` is reviewable work, not
     merge eligibility;
   - `merge_allowed` is a body-level claim that still requires strict
     `merge-decision` and live `check-pr`;
   - draft status alone must not select the body validation mode.
3. Resolve human-gate evidence before treating `human_gates_checked: true` as
   supported:
   - when a gate applies, require a durable current-head record with
     `decision: approved`;
   - `changes_requested` or `rejected` requires
     `human_gates_checked: false` and `result: merge_blocked`;
   - when no gate applies, require a durable no-gate risk/path determination.
   A new code commit makes review of the older head stale unless reaffirmed. Do
   not reuse review from a closed-unmerged or superseded PR.
4. If validation failed or evidence is stale, the next safe action is to return
   the durable result to `merge_blocked` before more work. Record the blocker
   before converting the PR to draft for revision.
5. If an open PR represents an approach that should be abandoned, do not patch
   around it. Record the abandonment reason, return the durable result to
   `merge_blocked`, close it unmerged, preserve its branch, commits, CI,
   comments, and decision record, and restart authorized work from current
   `main` on a fresh branch. A closed-unmerged PR did not change `main` and
   needs no revert.
6. If no PR is open, compare live open issues with `CURRENT_STATUS.md`. A
   closed-unmerged PR is historical evidence, not authority for new edits.
7. If `CURRENT_STATUS.md` is stale but live GitHub state is clear, prefer live
   GitHub state and plan a status refresh only when repo-level recovery state
   would mislead the next session.
8. If GitHub is available and there is no active issue or PR, stop unless the
   user explicitly asks to create a durable issue. If GitHub is verifiably
   unavailable, proceed only from a complete validated fallback after confirming
   that no escalation trigger applies, and keep a hard stop before PR, merge,
   protected-path exception, or external action.
9. Before reporting `ready_for_work_unit`, confirm the authority contains the
   canonical 13 task fields plus separate `context_read_set` and
   `project_specific_validation` gates. When the repository provides the
   command, run:

   ```bash
   python3 scripts/asgk.py work-unit-check --issue <number> --authority-only --json
   ```

   For an open PR follow-up, normally validate its still-open linked issue with
   `--issue`. Use `--pr` only when the PR body itself visibly owns all 13 fields
   and both gates. If a source-distributed target lacks this command, record
   validation as unavailable and perform a bounded manual check; do not convert
   command absence into a false validator failure.

## Stop States

Report exactly one state. Apply `blocked`, `requires_human`,
`closed_unmerged_restart_ready`, `ready_for_work_unit`, then `no_active_work`
in that precedence order.

- `blocked`: startup docs are missing, GitHub state is unavailable without both
  independent outage evidence and a complete fallback, instructions conflict,
  or validation/evidence is stale and the durable Merge Decision has not yet
  returned to `merge_blocked`.
- `requires_human`: no non-human blocker remains and a specific applicable
  human gate or issue/policy-required semantic decision remains unresolved, or
  canonical policy and the current issue do not explicitly authorize the
  escalated next action. Routine review requested by an ordinary
  ready-for-review PR does not by itself create this state.
- `ready_for_work_unit`: one durable issue or PR is identified and its
  authority-only fields and execution gates are valid at the available proof
  boundary, or a verified outage has a complete fallback for bounded local work
  with the issue-before-PR stop condition recorded.
- `closed_unmerged_restart_ready`: the failed attempt is preserved and the
  authorized issue permits a fresh branch from current `main`.
- `no_active_work`: no current work exists; open a durable issue before editing.

## Exit Artifact

Return a compact status summary naming the PR or issue, allowed next action, required validation entrypoint, and stop condition. Do not leave task scope only in chat.
