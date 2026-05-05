# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-05T12:40:53Z`

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
task-packet schema-shaped validation are complete. The risk-gate mechanization
sequence is complete at the repository tooling level, with the remaining
default-CI self-certification limit recorded in
`docs/control/VALIDATION_STRATEGY.md`.

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
issue: "#157 [VALIDATION] Add task-packet schema validator"
pr: "#158 [VALIDATION] Add task-packet schema validator"
merge_commit: "31b1486624ffb3a7aed7d8ff24b8874f5a6378c3"
validation: "python3 scripts/asgk.py doctor passed on PR #158 and current main"
note: "Risk-gate mechanization closeout completed. Issue #154 was also closed as already satisfied by merged PR #156."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are currently authorized.

## Next safe action

Open a new durable GitHub issue before starting further work. Do not start
public visibility change, package publication, installer scaffold, runtime
adapter, external distribution, v1.1.x/v1.2 release work, or v2.0 follow-up work
without a new durable GitHub issue and explicit human approval where required.
