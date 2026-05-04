# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T13:27:44Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x remains in v1.1 stabilization before release preparation. The generic
repo-governance core has been strengthened through parser/status/handoff checks,
document navigation split, target-install checklist, read-only target-install
check, read-only target-install plan, policy-gate negative fixtures, and
Vertical Governance Completion at the thin-router layer.

Vertical Governance Completion is being closed through issue #102. The milestone
does not claim five new standalone policy systems. It records that Decision
Control is completed as a thin registry/template layer, while Evidence,
Authority, Lifecycle, and Capability/Risk controls are covered inside that layer
and should become standalone policy or tooling only after field-test evidence
proves the need.

## Active work

```yaml
issue: "#102 [DOCS] Complete Vertical Governance Completion milestone"
pr: none
branch: docs/complete-vertical-governance-102
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
issue: "#100 [DOCS] Clarify vertical governance milestone phase state"
pr: "#101 docs: clarify vertical governance milestone phase"
merge_commit: "84c0cad9fa92ece44161e3e2521059bdb506a3d5"
note: "PR #101 clarified that #88 / PR #89 completed only the initial vertical governance layer, and issue #102 is closing the remaining milestone criteria."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are authorized by the current active work.

## Next safe action

Complete issue #102 by opening a docs-only PR that marks Vertical Governance
Completion complete, records the five vertical control lines as thin-layer
coverage, and moves the next active stabilization gate to the real-world field
test. If low-risk merge gates pass, merge and close #102; otherwise stop for
human review.
