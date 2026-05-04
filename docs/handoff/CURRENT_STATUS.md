# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T16:20:00Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x stabilization has completed the required thin vertical-governance layer,
the first real-world field test, post-field-test readiness audit, and the
planning-only v1.0 release-preparation plan.

Release execution has not started. License selection, release tagging, GitHub
release creation, package publication, and external distribution remain
human-gated and require a separate explicit release decision or release-execution
issue.

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
issue: "#116 [RELEASE] Plan v1.0 release preparation"
pr: "#117 docs: plan v1 release preparation"
merge_commit: "4453e4e9d5ab1f6b7a5a0e4d67acbf6d625a1daf"
note: "Planning-only v1.0 release-preparation plan is in place. Release execution remains blocked until a separate gated issue exists."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are currently authorized.

## Next safe action

Open a separate gated issue for the next release decision. Likely next candidates
are license selection, final readiness review, or release-execution planning. Do
not tag, publish, package, choose a license, create a GitHub release, or start
release execution without explicit human approval in that issue.
