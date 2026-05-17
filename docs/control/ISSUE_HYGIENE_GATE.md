# Issue Hygiene Gate

Before starting an issue:

1. Confirm issue is open and authorized.
2. Confirm acceptance criteria are not already satisfied.
3. Check recent merged PRs and current `main`.
4. Check `docs/handoff/CURRENT_STATUS.md`.
5. If stale, comment with evidence and stop.
6. If follow-up work is needed, create or request a new issue.
7. Do not infer missing work from stale issues when handoff says complete.

## Observation-To-Work Boundary

A finding creates work only when it affects current authorized work, current
recovery state, or current release closeout. Historical or pre-rule residue,
optional cleanup, and evidence already recoverable from GitHub are observations
unless a durable issue explicitly scopes backfill or cleanup.

## Completion comment format

```md
## Issue Hygiene Result

Status: already_satisfied | still_valid | stale | blocked
Evidence:
- <file/PR/check>
Recommended action:
- <close/relabel/new issue/continue>
```
