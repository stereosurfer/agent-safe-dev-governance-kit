# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T10:45:00Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x remains in v1.1 stabilization before release preparation. The generic
repo-governance core has been strengthened through parser/status/handoff checks,
document navigation split, target-install checklist, read-only target-install
check, and read-only target-install plan. The active milestone is now **Vertical
Governance Completion**, which adds a thin decision-point registry and reusable
decision packet template so major decision points can be resumed and reviewed
consistently across projects using ASGK.

## Active work

```yaml
issue: "#88 [MILESTONE] Vertical Governance Completion"
pr: none
branch: docs/vertical-governance-88
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
issue: "#86 [TOOLING] Add read-only target install planner"
pr: "#87 tooling: add read-only target install planner"
merge_commit: "d4798690e027a8220ffc140bb2e1a111646f6400"
note: "Read-only target-install plan is available as scripts/target_install_plan.py. Details are in GitHub; do not duplicate historical logs here."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are authorized by the current active work.

## Next safe action

Review and complete the Vertical Governance Completion PR for issue #88. The
bounded work should remain docs/template only: add and review
`docs/control/DECISION_POINT_REGISTRY.md`, `templates/decision_packet.template.yaml`,
and related roadmap/status/context/registry updates. Do not add decision-check
CLI, schema, installer scaffold, or runtime adapter work in this work unit.
