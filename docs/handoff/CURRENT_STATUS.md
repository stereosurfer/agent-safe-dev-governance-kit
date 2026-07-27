# Current Status

This is the compact current-status surface for the repository. It is
overwritten, not appended. Historical detail belongs in GitHub issues, PRs,
comments, releases, and merge commits.

Last updated: `2026-07-27T02:29:30Z`

## Durable source of truth

- GitHub issues, PRs, comments, releases, and repository files are authoritative.
- Chat memory and superseded roadmap documents are not current authority.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue or PR.

## Current snapshot

ASGK v1.7.3 remains the latest completed source-only GitHub release under the
Apache-2.0 license.

ASGK 2.0 is an active docs-driven evolution under issue #323. Its current
product facts center on safe, smooth human-AI handoff; work that stays
understandable, resumable, and traceable; and freedom from dependence on a
specific model, provider, Agent, or prior conversation.

Issue #325 establishes that introducing or materially upgrading ASGK is a
read-only, target-specific assessment by a human-selected frontier-capability
model. The Skill guides evidence, boundaries, uncertainty, and stopping; the
model judges fit, governance depth, minimum sufficient adaptation, or no change.
The assessment creates no extra human gate.

Current target-install scripts still retain legacy fixed-shape assumptions.
Their output is bounded mechanical evidence, not target-fit, architecture,
readiness, or approval authority. Tooling correction remains separate work
under the #323 program.

The old runtime-adapter/profile roadmap, fixed module selection, adoption
declaration, and historical planning documents are superseded and must not
drive new work.

## Active work

```yaml
issue: "#323 ASGK 2.0 program"
pr: none
branch: main
state: active_program
```

## Current validation entrypoint

```bash
python3 scripts/asgk.py doctor
```

Additional focused checks:

- PR body: `python3 scripts/pr_governance_preflight.py check --body-file <body-file>`
- PR readiness: `python3 scripts/asgk.py check-pr --pr <number>`
- Work-unit scope: `python3 scripts/asgk.py work-unit-check --issue <number> --git-base origin/main --git-head WORKTREE`

## Closed gates

- superseded roadmap or historical plan as current task authority
- automatic model selection, routing, switching, or price-tier dispatch
- fixed target file shape, module picker, or adoption declaration as fit proof
- legacy checker output as semantic readiness or architecture authority
- cloud egress, API/model calls, MCP writes, dependencies, schema changes,
  publication, or repository visibility changes without their existing gates
- low-risk or merge approval by Agent declaration

## Last completed

```yaml
issue: "#325 Restore frontier-guided adoption assessment in canonical docs and Skills"
state: "post-merge canonical adoption and material-upgrade responsibility boundary"
latest_completed_release: "ASGK v1.7.3"
latest_completed_tag: v1.7.3
validation: "doctor, work-unit scope, wording/reference scans, and Skill validation"
proof_limit: "documentation and Skills changed; legacy target-install scripts and compact-upgrade implementation did not"
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files,
model cache, or external preparation outputs are authorized by this status.

## Next safe action

Use the corrected binding facts in issue #323 to authorize one bounded next work
unit. Do not resume work from an old roadmap, historical plan, or deleted
module-selection interpretation.
