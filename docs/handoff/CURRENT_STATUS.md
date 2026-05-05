# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-05T07:55:00Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x stabilization, Vertical Governance Completion, the first real-world
field test, post-field-test readiness audit, planning-only v1.0 release
preparation, final v1.0 readiness review, license/distribution decision, full
Apache-2.0 license text replacement, source-only v1.0 release execution,
post-merge-safe current-status policy, v1.x product-entry documentation,
source-only adoption/license-handling clarification, target-install
license-handling tooling alignment, and source-only v1.1.0 release execution are
complete.

Apache-2.0 is the selected v1.0 license. The selected distribution path is a
source-only GitHub release. Tag `v1.0.0` and GitHub release `ASGK v1.0.0` were
created from target commit `7d2e364c4c53d1296c7ce1c2d241291837d54c61` under
issue #130 after explicit human approval and final validation.

Tag `v1.1.0` and GitHub release `ASGK v1.1.0` were created from target commit
`2bcf59dee754d8223b715ff904eca709aa5d53a5` under issue #145 after explicit
human approval and final validation. v1.1.0 remains a source-only GitHub
release; no package, installer, runtime adapter, dependency, schema, workflow,
or repository visibility change was performed.

Package publication, runtime-specific adapters, installer scaffold work,
external distribution beyond source-only GitHub release, and repository
visibility changes remain human-gated.

## Active work

```yaml
issue: none
pr: none
branch: main
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

- runtime-specific profiles/adapters before v2.0
- cloud egress by default
- API/model calls by default
- MCP write capability
- schema breaking changes
- new dependencies
- package publication without explicit human-gated issue
- repository visibility change without explicit human approval
- automatic handoff final-judgment generation
- installer scaffold before checker/planner and decision governance are stable
- low-risk status by agent declaration
- v2.0 follow-up work without a new durable issue

## Last completed

```yaml
issue: "#145 [RELEASE] Execute source-only v1.1.0 release"
tag: v1.1.0
release: "ASGK v1.1.0"
target_commit: "2bcf59dee754d8223b715ff904eca709aa5d53a5"
release_url: "https://github.com/stereosurfer/agent-safe-dev-governance-kit/releases/tag/v1.1.0"
validation: "python3 scripts/asgk.py doctor passed"
note: "Source-only GitHub release completed. No package, installer, runtime adapter, dependency, schema, workflow, repository visibility, or external distribution change was performed."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are currently authorized.

## Next safe action

Open a new durable GitHub issue before starting further work. Do not start
public visibility change, package publication, installer scaffold, runtime
adapter, external distribution, v1.1.x/v1.2 release work, or v2.0 follow-up work
without a new durable GitHub issue and explicit human approval where required.
