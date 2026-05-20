# Current Status

This is the compact current-status surface for the repository. It is
overwritten, not appended. Historical detail belongs in GitHub issues, PRs,
comments, releases, and merge commits.

Last updated: `2026-05-20T09:17:04Z`

## Durable source of truth

- GitHub issues, PRs, comments, releases, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x is a source-only generic repo-governance product line under the
Apache-2.0 license. The default operating profile remains generic; runtime
profiles, adapters, installers, packages, external distribution, and repository
visibility changes remain human-gated or deferred.

ASGK v1.7.2 is the latest completed source-only GitHub release. It was executed
under issue #317 after final doctor validation and explicit human approval. The
release is a v1.x source-local boundary patch: target-install and Skill wording
now distinguish ASGK source-repo validation/history semantics from target-repo
completion rules more explicitly.

Historical release detail is not duplicated here. GitHub releases, release
issues, PRs, Merge Decision Records, issue comments, tags, and merge commits are
the canonical release-history evidence. This file records only the current
recovery state and latest completed release.

Tag `v1.7.2` and GitHub release `ASGK v1.7.2` were created from target commit
`a6944432218cdadbd7815e6b9b89d6a55636913d`. v1.7.2 remains source-only: no
package, installer, runtime adapter, dependency, schema, workflow, repository
visibility change, cloud/API/model lane, MCP change, or v2.0 work was
performed. Changed Codex installed ASGK Skills were synced to
`~/.codex/skills` by explicit user request after release publication.

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

Additional focused checks:

- PR body create/edit: `python3 scripts/pr_governance_preflight.py check --body-file <body-file>`
- PR readiness: `python3 scripts/asgk.py check-pr --pr <number>`
- Release state: `python3 scripts/asgk.py release-state-check --tag <tag> --release-title "<title>"`
- Task packets: `python3 scripts/asgk.py task-packet-check --file <path>`

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
issue: "#317 Publish ASGK v1.7.2 source-only patch release"
state: "v1.7.2 source-only release executed and release-state docs synchronized"
latest_completed_release: "ASGK v1.7.2"
latest_completed_tag: v1.7.2
target_commit: "a6944432218cdadbd7815e6b9b89d6a55636913d"
release_url: "https://github.com/stereosurfer/agent-safe-dev-governance-kit/releases/tag/v1.7.2"
validation: "python3 scripts/asgk.py doctor passed before release execution; release-state-check and doctor passed during release-state closeout"
note: "Changed Codex installed ASGK Skills were synced by explicit user request. No package, installer, runtime adapter, dependency, schema, workflow, repository visibility, cloud/API/model lane, MCP change, or v2.0 work was performed."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files,
model cache, or external preparation outputs are currently authorized.

## Next safe action

No active release-state follow-up is required after the v1.7.2 closeout PR
merges. Future gated work must start from a separate durable issue.
