---
name: asgk-governance-health-check
description: Use for periodic or milestone ASGK repository health checks; inspects open PRs/issues, CURRENT_STATUS drift, validation status, merge-decision hygiene, and release/closeout residue without starting new work.
---

# ASGK Governance Health Check

Use this skill weekly, before a milestone, after several merges, or before public/customer handoff.

## Authority

This skill reports drift. It does not fix issues unless a separate durable issue authorizes changes.

## Procedure

1. Check open PRs.
2. Check open issues.
3. Compare `docs/handoff/CURRENT_STATUS.md` with live GitHub state.
4. Run `python3 scripts/asgk.py doctor`.
5. Sample recent PRs for Merge Decision, Current Status Impact, closing references, and validation evidence.
6. Check for release or closeout residue: merged PRs with open issues, stale active work, missing status refresh, or human-gated work without explicit approval.
7. Produce a compact health report and recommend bounded follow-up issues.

## Health States

- `healthy`: no active drift found.
- `watch`: minor docs or evidence gaps, no immediate blocker.
- `blocked`: stale status, open satisfied issue, failed doctor, missing closing references, or unresolved human-gated residue.

## Exit Artifact

Issue comment, report, or final summary with observed evidence, limits, and recommended follow-up issues. Do not start fixes without durable authorization.
