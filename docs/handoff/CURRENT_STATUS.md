# Current Status

This is the compact current-status surface for the repository. It is overwritten,
not appended. Historical detail belongs in GitHub issues, PRs, comments, and
merge commits.

Last updated: `2026-05-03T15:00:00Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions should read `AGENTS.md`, `README.md`, this file, and the
  active issue/PR if one exists.

## Current snapshot

ASGK v1.x remains in v1.1 stabilization before release preparation. Recent
governance-loop hardening is complete: handoff-template/check list alignment,
local closeout-check, uncontrolled-document audit, and document-map sync have
landed. The next bounded work should prepare the real-world field test, including
checking whether existing QUICKSTART/install guidance is sufficient.

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
changed paths, closeout status, PR bodies, task packets, and handoff packets.

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
issue: "#62 [DOCS] Sync document map after closeout-check and uncontrolled-document audit"
pr: "#63 docs: sync document map for closeout and audit"
merge_commit: "dfaae5dc1833b1b805a4ec2817cd742c3d44b4fe"
note: "Details are in GitHub; do not duplicate historical logs here."
```

## Runtime artifact status

No runtime artifacts, private source material, SQLite live DB, cache files, model
cache, or external preparation outputs are authorized by the current idle state.

## Next safe action

Open a bounded issue to prepare the real-world field test. First determine
whether existing QUICKSTART/install guidance is sufficient for the field test, or
whether a small usage guide is needed before testing.
