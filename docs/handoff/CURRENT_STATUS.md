# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T23:40:00Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x stabilization, Vertical Governance Completion, the first real-world
field test, post-field-test readiness audit, planning-only v1.0 release
preparation, and final v1.0 readiness review are complete.

The active work records the human-approved v1.0 license and distribution path:
Apache-2.0 with a source-only GitHub release path. Release execution has not
started. Tag creation, GitHub release creation, package publication, and external
distribution beyond source-only GitHub release remain human-gated.

## Active work

```yaml
issue: "#124 [RELEASE] Decide v1.0 license and release execution path"
pr: none
branch: release/license-and-path-124
state: in_progress
```

## Current validation entrypoint

```bash
python3 scripts/asgk.py doctor
```

The workflow also runs the positive handoff fixture and core negative checks for
changed paths, closeout status, PR bodies, task packets, and handoff packets.
Policy-gate negative fixtures remain opt-in through
`python3 scripts/asgk.py negative policy-gate`. Target-install negative fixtures
remain opt-in through `python3 scripts/asgk.py negative target-install`.

## Closed gates

- runtime-specific profiles before v2.0
- cloud egress by default
- API/model calls by default
- MCP write capability
- schema breaking changes
- new dependencies
- publication/release without explicit release-preparation issue
- automatic handoff final-judgment generation
- installer scaffold before checker/planner and decision governance are stable
- low-risk status by agent declaration
- release execution before explicit human-gated release-execution issue

## Last completed

```yaml
issue: "#120 [RELEASE] Final v1.0 readiness review"
pr: "#121 docs: perform final v1 readiness review"
merge_commit: "f3b1a6cf909b431230443fdf80462555fa456eb8"
note: "Final v1.0 readiness review records ready_to_propose_release_execution, but release execution remains blocked until a separate human-gated issue exists."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are currently authorized.

## Next safe action

Complete the license and release-path PR for issue #124. Keep the work limited to
recording Apache-2.0, source-only GitHub release path, and related planning/status
updates. Do not tag, publish, package, create a GitHub release, or start release
execution in this work unit.
