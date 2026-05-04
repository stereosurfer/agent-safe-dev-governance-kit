# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-04T14:30:00Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x stabilization has completed the required thin vertical-governance layer
and the first real-world field test. The field test used issue #112 and PR #113
to add `python3 scripts/asgk.py negative target-install` as a bounded, non-docs-only
tooling/validation change with validation evidence, decision-packet-shaped merge
inputs, and issue closeout.

The post-field-test readiness audit now records the field-test result and lessons
learned. This does not start release preparation. The next gate is a separate
release-preparation planning issue covering final readiness review, license,
tag/release process, package/distribution boundary, explicit v2.0 deferrals, and
remaining human gates.

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

## Last completed

```yaml
issue: "#112 [FIELD TEST] Add opt-in target-install negative command"
pr: "#113 tooling: add target-install negative command"
merge_commit: "1dcdbd08a20a41a903d474ff8080317eefd87185"
note: "First real-world ASGK field test completed as a bounded tooling/validation change. Post-field-test readiness audit is recorded in issue #114."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are currently authorized.

## Next safe action

Create a release-preparation planning issue. It must remain planning-only unless
explicitly authorized, and should cover final readiness review, license selection,
tag/release process, package/distribution boundary, explicit v2.0 deferrals, and
remaining human gates. Do not tag, publish, package, or choose a license without
that gated issue.
