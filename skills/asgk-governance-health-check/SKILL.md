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
6. Check for release or closeout residue: merged PRs with open issues, stale
   active work, missing status refresh, or human-gated work without explicit
   approval.
7. Classify each finding before recommending work:
   - `current_blocker`: affects the current open PR/issue, current recovery
     state, or current release closeout.
   - `legacy_observation`: historical or pre-rule residue that does not mislead
     the current recovery state.
   - `optional_cleanup`: improvement that may reduce confusion but is not needed
     for the current work unit.
8. Produce a compact health report. Recommend bounded follow-up issues only for
   `current_blocker` findings, or when a human explicitly requests a scoped
   backfill/cleanup issue.

## Health States

- `healthy`: no active drift found.
- `watch`: legacy observations, optional cleanup, or minor evidence gaps; no immediate blocker.
- `blocked`: stale status, open satisfied issue, failed doctor, missing closing references, or unresolved human-gated residue.
- `legacy_observation`: historical/pre-rule residue; report only unless a durable issue explicitly authorizes backfill.

## Non-Generation Rule

Health checks report observations. They do not create repair work from historical
gaps. Missing closeout decision analysis for an issue closed before PR #272
merged is `legacy_observation` or `watch`, not `blocked`.

## Exit Artifact

Issue comment, report, or final summary with observed evidence, limits, finding
classification, and any recommended follow-up issues. Do not start fixes without
durable authorization.
