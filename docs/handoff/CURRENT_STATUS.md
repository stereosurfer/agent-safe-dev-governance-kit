# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T12:47:17Z`

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
policy-gate fixtures. The active bounded work adds an ASGK CLI command for those
policy-gate fixtures without changing checker semantics, default CI wiring,
auto-merge behavior, schemas, dependencies, or GitHub API behavior.

## Active work

```yaml
issue: "#96 [TOOLING] Add opt-in policy-gate negative command"
pr: none
branch: tooling/policy-gate-negative-command-96
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
issue: "#94 [TEST] Add negative policy-gate fixtures"
pr: "#95 test: add negative policy-gate fixtures"
merge_commit: "d6f7c726245ae45616dda8666ad5096f13efd82b"
note: "Policy-gate expected-failure fixtures are merged. Details are in GitHub; do not duplicate historical logs here."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are authorized by the current active work.

## Next safe action

Complete issue #96 by opening a PR for the opt-in policy-gate negative command,
then wait for CI and human review. Do not change `scripts/policy_gate_check.py`
semantics, workflows, schemas, dependencies, auto-merge behavior, default CI
wiring, or GitHub API behavior in this work unit.
