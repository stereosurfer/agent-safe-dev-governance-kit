# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-03T09:17:34Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x is the runtime-agnostic governance core. It uses a generic repo-agent
profile: humans, Codex, ChatGPT Web, OpenGoat, Claude Code, Cursor, or other
runtimes may perform work, but every repository change must pass through the
same issue, PR, validation, Merge Decision Record, and handoff governance layer.

Release preparation is currently deferred. The next phase is v1.1 stabilization:
parser hardening, status-check, positive handoff-template fixture,
uncontrolled-document audit, and at least one real-world field test before
license/release/tag work.

## Active work

```yaml
issue: "#46 [DOCS] Add v1.1 stabilization plan before release preparation"
pr: "none; PR not opened yet"
branch: "codex/v1-1-stabilization-plan"
state: active
```

## Current validation entrypoint

```bash
python3 scripts/asgk.py doctor
```

The workflow also runs expected-failure checks for changed-path, PR-body,
task-packet, and handoff-packet negative fixtures.

## Closed gates

- runtime-specific profiles before v2.0
- cloud egress by default
- API/model calls by default
- MCP write capability
- schema breaking changes
- new dependencies
- publication/release
- automatic handoff final-judgment generation
- release preparation before v1.1 stabilization and field test

## Last completed

```yaml
issue: "#44 [DOCS] Add v1.0 readiness audit"
pr: "#45 docs: add v1 readiness audit"
merge_commit: "4ec5ec0dd2e0563be9490a06739fb955d186b2d6"
note: "Details are in GitHub; do not duplicate historical logs here."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are authorized for the active work unit.

## Next safe action

Open a docs-only PR for issue #46, verify Actions, update the Merge Decision
Record, merge only if low-risk gates pass, then close issue #46 with result
evidence.
