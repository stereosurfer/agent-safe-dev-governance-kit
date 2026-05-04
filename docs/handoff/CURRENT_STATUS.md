# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T14:45:00Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x stabilization has completed the required thin vertical-governance layer
and the first real-world field test. The post-field-test readiness audit records
that release preparation can now be planned as a separate gated work unit, but
release execution has not started.

The active work is release-preparation planning only. It adds a planning document
for final readiness review, license-selection path, tag/release process plan,
package/distribution boundary, explicit v2.0 deferrals, and remaining human gates.
It must not choose a license, tag, publish, package, create a GitHub release, or
start release execution.

## Active work

```yaml
issue: "#116 [RELEASE] Plan v1.0 release preparation"
pr: none
branch: docs/v1-release-prep-plan-116
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
issue: "#114 [DOCS] Close out real-world field test readiness audit"
pr: "#115 docs: close out real-world field test readiness audit"
merge_commit: "c5bb0c82a51f70528dd9fda442abf4b73d96c7bb"
note: "Post-field-test readiness audit is complete. Release preparation planning is now the active gate."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are currently authorized.

## Next safe action

Complete the release-preparation planning PR for issue #116. Keep the work
planning-only: define release gates and human decisions, but do not tag, publish,
package, choose a license, create a GitHub release, or start release execution.
