# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T13:14:28Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x remains in v1.1 stabilization before release preparation. The generic
repo-governance core has been strengthened through parser/status/handoff checks,
document navigation split, target-install checklist, read-only target-install
check, read-only target-install plan, initial vertical governance, Current Status
freshness gate, standalone fail-closed policy-gate checker, and opt-in negative
policy-gate fixtures. The active bounded work clarifies that PR #89 completed
only the first thin layer of Vertical Governance Completion; the milestone
remains active until a real decision-packet exercise and remaining exit criteria
are satisfied.

## Active work

```yaml
issue: "#100 [DOCS] Clarify vertical governance milestone phase state"
pr: none
branch: docs/vertical-governance-phase-100
state: in_progress
```

## Current validation entrypoint

```bash
python3 scripts/asgk.py doctor
```

The workflow also runs the positive handoff fixture and core negative checks for
changed paths, closeout status, PR bodies, task packets, and handoff packets.
Policy-gate negative fixtures remain opt-in through
`python3 scripts/asgk.py negative policy-gate`.

## Closed gates

- runtime-specific profiles before v2.0
- cloud egress by default
- API/model calls by default
- MCP write capability
- schema breaking changes
- new dependencies
- publication/release
- automatic handoff final-judgment generation
- release preparation before v1.1 stabilization, vertical governance completion,
  and field test
- installer scaffold before checker/planner and decision governance are stable
- low-risk status by agent declaration

## Last completed

```yaml
issue: "#98 [DOCS] Refresh current status after policy-gate command merge"
pr: "#99 docs: refresh current status after policy-gate command merge"
merge_commit: "6295b5fa36ad9b2550c7eaafbb35b60cd9063fe5"
note: "Current status closeout after PR #97 is merged. Details are in GitHub; do not duplicate historical logs here."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are authorized by the current active work.

## Next safe action

Complete issue #100 by opening a docs-only PR that makes milestone phase state
discoverable from repository files alone. If low-risk merge gates pass, merge
and close #100; otherwise stop for human review.
