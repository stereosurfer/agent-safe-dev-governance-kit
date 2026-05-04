# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T12:54:58Z`

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
policy-gate fixtures. The active bounded work refreshes this compact handoff
surface after PR #97 merged so completed #96 work is no longer listed as active.

## Active work

```yaml
issue: "#98 [DOCS] Refresh current status after policy-gate command merge"
pr: none
branch: docs/current-status-closeout-98
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
issue: "#96 [TOOLING] Add opt-in policy-gate negative command"
pr: "#97 tooling: add opt-in policy-gate negative command"
merge_commit: "56961fe65086483f29b726e34b6ae34dfdd37e79"
note: "Opt-in policy-gate negative command is merged. Details are in GitHub; do not duplicate historical logs here."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are authorized by the current active work.

## Next safe action

Complete issue #98 by opening a status-only PR, then wait for CI and human
review. Do not modify scripts, validation behavior, schemas, workflows,
templates, governance policy, or runtime artifacts in this work unit.
