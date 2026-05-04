# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T13:32:06Z`

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

Vertical Governance Completion is complete. The milestone did not add five new
standalone policy systems. Decision Control is complete as a thin
registry/template layer, while Evidence, Authority, Lifecycle, and
Capability/Risk controls are covered inside that layer and should become
standalone policy or tooling only after field-test evidence proves the need.

The next stabilization gate is a real-world field test before release
preparation.

## Active work

```yaml
issue: none
pr: none
branch: none
state: no_active_work
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
- release preparation before v1.1 stabilization, real-world field test, and
  post-test readiness audit update
- installer scaffold before checker/planner and decision governance are stable
- low-risk status by agent declaration

## Last completed

```yaml
issue: "#102 [DOCS] Complete Vertical Governance Completion milestone"
pr: "#103 docs: complete vertical governance milestone"
merge_commit: "2def8c2edb569dde5e9629ae0f59e7b0c12bbe4f"
note: "Vertical Governance Completion is complete at the thin-router layer. The next active gate is the real-world field test."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are currently authorized.

## Next safe action

Create or run the real-world field test work unit. It must have a durable GitHub
issue, allowed paths, PR Merge Decision Record, validation evidence, handoff
usage, issue closeout, lessons learned, and a post-test update to
`docs/control/V1_READINESS_AUDIT.md`. Do not start release preparation first.
