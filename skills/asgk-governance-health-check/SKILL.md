---
name: asgk-governance-health-check
description: Use for periodic or milestone ASGK repository health checks; inspects open PRs/issues, CURRENT_STATUS drift, validation status, merge-decision hygiene, and release/closeout residue without starting new work.
---

# ASGK Governance Health Check

Use this skill weekly, before a milestone, after several merges, or before public/customer handoff.

## Authority

This skill reports drift. It does not fix issues unless a separate durable issue authorizes changes.

This skill runs only when explicitly requested or scheduled as a periodic,
milestone, public/customer handoff, release-readiness, or whole-repository
health check. Routine post-merge prompts such as "the PR merged" or "anything
else?" are closeout triggers, not health-check triggers. In those cases use
`asgk-post-merge-closeout` and stop unless a separate durable issue/comment
authorizes a wider health check.

## Procedure

1. Check open PRs.
2. Check open issues.
3. Compare `docs/handoff/CURRENT_STATUS.md` with live GitHub state.
4. Run the repository-local validation entrypoint. In this ASGK source
   repository, that is usually `python3 scripts/asgk.py doctor`; in target
   repositories, use their local validation command instead of source-repo
   parity checks.
5. Sample recent PRs for Merge Decision, Current Status Impact, closing references, and validation evidence.
6. Check for release or closeout residue: merged PRs with open issues, stale
   active work, missing status refresh, or human-gated work without explicit
   approval.
7. Apply `docs/control/ISSUE_HYGIENE_GATE.md` before recommending work from
   observations.
8. Produce a compact health report. Recommend bounded follow-up issues only for
   current blockers or explicit scoped backfill/cleanup.

## Health States

- `healthy`: no active drift found.
- `watch`: observations or minor evidence gaps; no immediate blocker.
- `blocked`: stale status, open satisfied issue, failed local validation,
  missing closing references, or unresolved human-gated residue.

## Exit Artifact

Issue comment, report, or final summary with observed evidence, limits, finding
classification, and any recommended follow-up issues. Do not start fixes without
durable authorization.
