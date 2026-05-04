# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T12:15:00Z`

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
freshness gate, and standalone fail-closed policy-gate checker. The active
bounded work adds opt-in negative fixtures proving `scripts/policy_gate_check.py`
blocks known-bad PR bodies without inferring low-risk status or wiring the check
into default CI.

## Active work

```yaml
issue: "#94 [TEST] Add negative policy-gate fixtures"
pr: none
branch: test/policy-gate-negative-fixtures-94
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
issue: "#92 [TOOLING] Mechanize existing low-risk policy gates"
pr: "#93 tooling: mechanize existing low-risk policy gates"
merge_commit: "c37826a3065be8aba60bd2a1472ce1629572eba9"
note: "Standalone fail-closed policy-gate checker is merged. Details are in GitHub; do not duplicate historical logs here."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are authorized by the current active work.

## Next safe action

Review and complete the policy-gate negative fixtures PR for issue #94. The
bounded work should remain fixture/docs/status only. Do not modify
`scripts/policy_gate_check.py`, `scripts/asgk.py`, workflows, schemas,
dependencies, auto-merge behavior, or default CI wiring in this work unit.
