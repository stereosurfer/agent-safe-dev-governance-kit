# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T22:30:00Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x stabilization, Vertical Governance Completion, the first real-world
field test, post-field-test readiness audit, and planning-only v1.0 release
preparation are complete. The active work is final v1.0 readiness review.

This review may conclude that release execution can be proposed in a later
separate human-gated issue. It must not choose a license, tag, publish, package,
create a GitHub release, or start release execution.

## Active work

```yaml
issue: "#120 [RELEASE] Final v1.0 readiness review"
pr: none
branch: docs/final-v1-readiness-review-120
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
issue: "#118 [DOCS] Refresh current status after release preparation planning"
pr: "#119 docs: refresh current status after release preparation planning"
merge_commit: "13c67bc961593036c535093f710b6840e7441fbd"
note: "Current status now records no active work after release-preparation planning; next release decisions remain gated."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are currently authorized.

## Next safe action

Complete the final v1.0 readiness review PR for issue #120. Keep the work review-only:
record whether release execution may be proposed, but do not tag, publish,
package, choose a license, create a GitHub release, or start release execution.
