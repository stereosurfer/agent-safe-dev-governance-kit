# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-03T13:40:30Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x is the runtime-agnostic governance core. Release preparation remains
deferred while v1.1 stabilization continues. Parser hardening, `asgk
status-check`, and the positive handoff-template fixture are complete. The next
work should address governance-loop correctness before continuing the remaining
stabilization items.

## Active work

```yaml
issue: none
pr: none
branch: main
state: idle
```

## Current validation entrypoint

```bash
python3 scripts/asgk.py doctor
```

The workflow also runs the positive handoff fixture and core negative checks for
changed paths, PR bodies, task packets, and handoff packets.

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
issue: "#52 [TEST] Add positive handoff-template fixture"
pr: "#53 test: add positive handoff packet fixture"
merge_commit: "c2f9dcb3929d173069dfa49d083efa0fa1fb1820"
note: "Details are in GitHub; do not duplicate historical logs here."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are authorized by the current idle state.

## Next safe action

Open the next bounded issue or PR for governance-loop correctness before
continuing uncontrolled-document audit or field-test work.
