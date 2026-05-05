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
2. If a PR is open, treat it as the current work boundary and inspect only what is needed for that PR.
3. If no PR is open, compare live open issues with `CURRENT_STATUS.md`.
4. If `CURRENT_STATUS.md` is stale but live GitHub state is clear, prefer live GitHub state and plan a status refresh only when repo-level recovery state would mislead the next session.
5. If there is no active issue or PR, stop unless the user explicitly asks to create a durable issue.

## Stop States

- `blocked`: startup docs missing, GitHub state unavailable, or instructions conflict.
- `requires_human`: next action touches a human-gated operation.
- `ready_for_work_unit`: one durable issue or PR is identified.
- `no_active_work`: no current work exists; open a durable issue before editing.

## Exit Artifact

Return a compact status summary naming the PR or issue, allowed next action, required validation entrypoint, and stop condition. Do not leave task scope only in chat.
