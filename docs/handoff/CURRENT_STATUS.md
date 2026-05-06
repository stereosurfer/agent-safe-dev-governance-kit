# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-05T14:04:52Z`

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
license-handling tooling alignment, source-only v1.1.0 release execution,
PR-body policy-gate default CI wiring, pull-request changed-path hygiene CI
wiring, GitHub PR status validation, PR closing issue reference validation, and
task-packet schema-shaped validation are complete. ASGK Skill Pack v0 source is
available under `skills/`, with usage and maintenance touchpoint guidance in
`docs/SKILL_PACK.md`. Source-only v1.2.1 release execution is complete. The
risk-gate mechanization and release-state closeout checkpoint sequence is
complete at the repository tooling level, with the remaining default-CI
self-certification limit recorded in `docs/control/VALIDATION_STRATEGY.md`.

Apache-2.0 is the selected v1.0 license. The selected distribution path is a
source-only GitHub release. Completed source-only releases are recorded in
GitHub releases and release issues: `v1.0.0` / `ASGK v1.0.0` under #130,
`v1.1.0` / `ASGK v1.1.0` under #145, and `v1.2.0` / `ASGK v1.2.0` under #169.

Tag `v1.2.1` and GitHub release `ASGK v1.2.1` were created from target commit
`e872cbae3aa6a22236fedad8d79c4483a1508b37` under issue #174 after explicit
human approval and final validation. v1.2.1 remains a source-only GitHub
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
Pull-request CI also runs the PR-body policy gate from the GitHub event payload
and changed-path hygiene from the checked-out git diff. Policy-gate negative
fixtures also run in default CI. Target-install negative fixtures remain opt-in
through `python3 scripts/asgk.py negative target-install`.
PR-level status, including GitHub closing issue references, can be checked with
`python3 scripts/asgk.py check-pr --pr <number>` after GitHub Actions have
reported.
Task packets can be checked as JSON, canonical YAML-like packets, or negative
fixtures with `python3 scripts/asgk.py task-packet-check --file <path>`.

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
issue: "#174 [RELEASE] Execute source-only v1.2.1 release"
release: "ASGK v1.2.1"
tag: v1.2.1
target_commit: "e872cbae3aa6a22236fedad8d79c4483a1508b37"
release_url: "https://github.com/stereosurfer/agent-safe-dev-governance-kit/releases/tag/v1.2.1"
validation: "python3 scripts/asgk.py doctor passed before release execution"
note: "Source-only v1.2.1 release completed and issue #174 closed. No package, installer, runtime adapter, dependency, schema, workflow, repository visibility, or v2 work was performed."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are currently authorized.

## Next safe action

Open a new durable GitHub issue before starting further work. Do not tag, create
a GitHub release, change repository visibility, publish a package, add an
installer scaffold, add a runtime adapter, or start v2.0 follow-up work without
a new durable GitHub issue and explicit human approval where required.
