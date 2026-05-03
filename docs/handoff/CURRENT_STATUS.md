# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-03T08:14:34Z`

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

Runtime-specific governance profiles are deferred to v2.0 as optional
optimization adapters. They must be based on vendor documentation and observed
behavior, and they must not bypass ASGK core governance.

## Active work

```yaml
issue: "#42 [DOCS] Add current status policy and compact current status"
pr: "none; PR not opened yet"
branch: "codex/current-status-policy"
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

## Last completed

```yaml
issue: "#40 [TOOLS] Add handoff-template command"
pr: "#41 tools: add handoff-template command"
merge_commit: "1ec327eb6cd4034baef522482088257a54c85968"
note: "Details are in GitHub; do not duplicate historical logs here."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are authorized for the active work unit.

## Next safe action

Open a docs-only PR for issue #42, verify Actions, update the Merge Decision
Record, merge only if low-risk gates pass, then close issue #42 with result
evidence.
