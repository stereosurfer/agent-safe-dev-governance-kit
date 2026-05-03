# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-03T13:09:30Z`

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

Release preparation is currently deferred. The next phase is v1.1 stabilization.
Parser hardening and status-check are complete. The active work unit is the
positive handoff-template fixture.

## Active work

```yaml
issue: "#52 [TEST] Add positive handoff-template fixture"
pr: "none; PR not opened yet"
branch: "codex/positive-handoff-template-fixture"
state: active
```

## Current validation entrypoint

```bash
python3 scripts/asgk.py doctor
```

The target fixture check for this work unit is:

```bash
python3 scripts/asgk.py handoff-check --file examples/handoff_packet.valid.yaml --fail-on-todo
```

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
issue: "#50 [TOOL] Add asgk status-check"
pr: "not listed in this compact status file"
merge_commit: "a1e2ba4ba9d48555dd7c753aff971f45bd50f56c"
note: "Details are in GitHub; do not duplicate historical logs here."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are authorized for the active work unit.

## Next safe action

Open a PR for issue #52, verify GitHub Actions, update the Merge Decision
Record, merge only if low-risk gates pass, then close issue #52 with result
evidence.
