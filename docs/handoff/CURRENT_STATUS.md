# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T11:50:00Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x remains in v1.1 stabilization before release preparation. The generic
repo-governance core has been strengthened through parser/status/handoff checks,
document navigation split, target-install checklist, read-only target-install
check, read-only target-install plan, initial vertical governance, and Current
Status freshness gate. The active bounded work mechanizes existing low-risk /
auto-merge policy gates with a standalone read-only checker. The checker must not
infer low-risk status; it only confirms mechanically checkable PR-body gates and
keeps missing, unknown, pending, ambiguous, or unverifiable gates human-gated.

## Active work

```yaml
issue: "#92 [TOOLING] Mechanize existing low-risk policy gates"
pr: none
branch: tooling/policy-gate-check-92
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
- low-risk status by agent declaration

## Last completed

```yaml
issue: "#90 [DOCS] Add current-status update gate"
pr: "#91 docs: add current status freshness gate"
merge_commit: "7b02cc97823857c39af90c9f1c3f31a3d354f422"
note: "Current Status Impact is now a PR template and review gate. Details are in GitHub; do not duplicate historical logs here."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are authorized by the current active work.

## Next safe action

Review and complete the fail-closed policy gate checker PR for issue #92. The
bounded work should remain a standalone read-only checker plus docs updates. Do
not add new risk categories, auto-merge behavior, GitHub API calls, workflow
changes, schemas, dependencies, or `scripts/asgk.py` integration in this work
unit.
