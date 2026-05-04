# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T11:20:00Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x remains in v1.1 stabilization before release preparation. The generic
repo-governance core has been strengthened through parser/status/handoff checks,
document navigation split, target-install checklist, read-only target-install
check, read-only target-install plan, and the initial Vertical Governance
Completion layer. The active bounded work now adds a Current Status freshness gate
so milestone-impacting PRs must update `CURRENT_STATUS.md`, mark it not
applicable, or explicitly defer the update with a follow-up path.

## Active work

```yaml
issue: "#90 [DOCS] Add current-status update gate"
pr: none
branch: docs/current-status-update-gate-90
state: in_progress
```

## Current validation entrypoint

```bash
python3 scripts/asgk.py doctor
```

The workflow also runs the positive handoff fixture and core negative checks for
changed paths, closeout status, PR bodies, task packets, and handoff packets.

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

## Last completed

```yaml
issue: "#88 [MILESTONE] Vertical Governance Completion"
pr: "#89 docs: add vertical governance decision layer"
merge_commit: "37748fb37f93b1c511cebcaed860c01d6e20b3ee"
note: "Initial decision-point registry and decision-packet template are merged. Details are in GitHub; do not duplicate historical logs here."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are authorized by the current active work.

## Next safe action

Review and complete the Current Status freshness gate PR for issue #90. The
bounded work should remain docs-only: update `CURRENT_STATUS_POLICY.md`, PR
template, PR review checklist, document registry, and this current status file.
Do not add a new validator or CLI command in this work unit.
