# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-05T04:45:00Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x stabilization, Vertical Governance Completion, the first real-world
field test, post-field-test readiness audit, planning-only v1.0 release
preparation, final v1.0 readiness review, license/distribution decision, and full
Apache-2.0 license text replacement are complete.

Apache-2.0 is the selected v1.0 license. The selected distribution path is a
source-only GitHub release. Release execution has not started. Tag creation,
GitHub release creation, package publication, and external distribution beyond
source-only GitHub release remain human-gated.

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
issue: "#126 [RELEASE] Replace LICENSE with full Apache-2.0 text"
pr: "#127 release: replace license with full Apache 2.0 text"
merge_commit: "b7db87c473f7c5785343c27a70cce18b536d21c0"
note: "LICENSE now contains complete Apache-2.0 text. Release execution remains blocked until a separate human-gated issue exists."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are currently authorized.

## Next safe action

Open a separate human-gated source-only v1.0 release execution issue. It should
confirm the target commit, final checks, tag/GitHub release decision, release
notes, and rollback or revoke plan. Do not tag, publish, package, create a GitHub
release, or start release execution without explicit human approval in that issue.
