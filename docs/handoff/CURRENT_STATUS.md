# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T23:10:00Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x stabilization, Vertical Governance Completion, the first real-world
field test, post-field-test readiness audit, planning-only v1.0 release
preparation, and final v1.0 readiness review are complete.

The final readiness review records that no v1.0 core blocker is currently known
and that release execution may be proposed only through a later separate
human-gated issue. Release execution has not started.

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
issue: "#120 [RELEASE] Final v1.0 readiness review"
pr: "#121 docs: perform final v1 readiness review"
merge_commit: "f3b1a6cf909b431230443fdf80462555fa456eb8"
note: "Final v1.0 readiness review records ready_to_propose_release_execution, but release execution remains blocked until a separate human-gated issue exists."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are currently authorized.

## Next safe action

Open a separate human-gated release decision issue. The likely next issue is
`[RELEASE] Decide v1.0 license and release execution path`. Do not tag, publish,
package, choose a license, create a GitHub release, or start release execution
without explicit human approval in that issue.
