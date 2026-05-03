# Current Status

This is the canonical current-status surface for the repository.

Last updated: `2026-05-03T05:43:48Z`

## Durable source of truth

- GitHub issues, PRs, comments, and repository files are authoritative.
- Chat memory is not authoritative.
- New agent sessions must read `AGENTS.md`, `README.md`, this file, open PRs, and open issues.

## Current snapshot

```text
ASGK v1.x is the runtime-agnostic governance core. It uses a generic repo-agent profile: humans, Codex, ChatGPT Web, OpenGoat, Claude Code, Cursor, or other runtimes may perform work, but every repository change must pass through the same issue, PR, validation, Merge Decision Record, and handoff governance layer.

Runtime-specific governance profiles are deferred to v2.0. They are optional optimization adapters that must be based on vendor documentation and observed behavior, and they must not bypass ASGK core governance.
```

## Active PRs

```text
Pending: generic-profile v1 roadmap clarification PR for issue #23.
```

## Active milestone

```text
v1.x runtime-agnostic governance core hardening.
```

## Active work unit

```yaml
issue: "#23 [DOCS] Clarify v1 generic profile and defer runtime-specific profiles to v2.0"
lane: "lane_07_docs_handoff"
intelligence_level: "standard"
durable_source_of_truth: "GitHub issue #23"
allowed_paths:
  - "README.md"
  - "docs/QUICKSTART.md"
  - "docs/DOCUMENT_MAP.md"
  - "docs/bootstrap/12_productization_notes.md"
  - "docs/control/AGENT_CAPABILITY_MATRIX.md"
  - "docs/handoff/CURRENT_STATUS.md"
expected_output:
  - "v1.x generic profile scope clarified"
  - "v2.0 runtime-specific profile scope deferred"
  - "docs avoid claiming runtime-specific profiles are implemented"
```

## Closed gates

- runtime-specific profiles before v2.0
- cloud egress
- API/model calls by default
- MCP write capability
- schema breaking changes
- new dependencies
- publication/release

## Runtime artifact status

```text
No runtime artifacts, private source material, SQLite live DB, cache files, model cache, or external preparation outputs are authorized for this work unit.
```

## Next safe work

```text
Complete issue #23 by opening the docs-only PR, verifying Actions, recording the Merge Decision Record, and merging only if low-risk gates pass.
```
