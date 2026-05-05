# Document Map

Status: active ASGK repository-local navigation router.

This file is the compact routing surface for ASGK repository documents. It is
not the full document registry.

Use this file to decide where to look next. Do not read the whole repository by
default.

## Repo-local Scope

```text
DOCUMENT_MAP.md is repo-local.
```

This file governs the ASGK repository only. It is not the document map to copy
unchanged into repositories that install or adopt ASGK.

Target repositories must create their own compact `docs/DOCUMENT_MAP.md` from
`templates/DOCUMENT_MAP.template.md` and their own full
`docs/DOCUMENT_REGISTRY.md` from `templates/DOCUMENT_REGISTRY.template.md`.

## Core Rule

```text
Read the smallest set of canonical documents required by the work unit.
```

If two documents appear to disagree, prefer the document marked `canonical` for
that topic in `docs/DOCUMENT_REGISTRY.md`. If a summary document disagrees with a
canonical document, the summary document is stale and should be fixed in a
separate issue.

## Progressive Disclosure Surfaces

```yaml
progressive_disclosure_surfaces:
  router:
    path: docs/DOCUMENT_MAP.md
    purpose: compact repo-local navigation router
    read_by_default: false
  registry:
    path: docs/DOCUMENT_REGISTRY.md
    purpose: complete repo-local document registry and canonical ownership table
    read_by_default: false
    read_when:
      - canonical ownership is unclear
      - current issue changes document ownership
      - current issue changes document-map or registry structure
      - validation or reviewer feedback points to registry mismatch
  policy:
    path: docs/control/DOCUMENT_MAP_POLICY.md
    purpose: document-map size limits, split ownership, and maintenance rules
    read_by_default: false
  read_sets:
    path: docs/control/CONTEXT_BUDGET_POLICY.md
    purpose: context read sets, task-type reading guide, and expansion rules
    read_by_default: false
  install_surface:
    path: docs/INSTALL_SURFACE.md
    purpose: target-project copy/template/customize/do-not-copy boundary
    read_by_default: false
  skill_pack:
    path: docs/SKILL_PACK.md
    purpose: optional ASGK skill-pack source and usage modes
    read_by_default: false
```

## Default Startup Set

Every new agent session should start with only this minimal set unless the
current issue, PR, or handoff packet points elsewhere:

```yaml
default_startup_set:
  - AGENTS.md
  - README.md
  - docs/handoff/CURRENT_STATUS.md
  - current GitHub issue or PR
```

Additional documents should be pulled by task type, not by habit.

## Document Roles

```yaml
roles:
  canonical: Primary source of truth for a topic.
  summary: Short orientation document that points to canonical sources.
  example: Non-authoritative sample for humans and agents.
  schema: Machine-readable structure contract.
  contract: Semantic rules and invariants.
  template: Reusable starting point for work units or GitHub surfaces.
  status: Current handoff or state surface.
  script: Executable validation or hygiene behavior.
  future_optional: Planned future capability, not part of current v1.x core.
```

## Default Entry Summary

```yaml
default_entry_summary:
  read_first:
    - AGENTS.md
    - README.md
    - docs/handoff/CURRENT_STATUS.md
    - current GitHub issue or PR
  full_registry: docs/DOCUMENT_REGISTRY.md
  context_read_sets: docs/control/CONTEXT_BUDGET_POLICY.md
  install_boundary: docs/INSTALL_SURFACE.md
  skill_pack: docs/SKILL_PACK.md
  map_policy: docs/control/DOCUMENT_MAP_POLICY.md
```

## Profile And Adapter Boundary

ASGK v1.x uses a generic repo-agent governance core. Runtime-specific profile or
adapter documents for Codex, ChatGPT Web/GitHub connector, OpenGoat, Claude Code,
Cursor, Copilot, or other runtimes are ASGK v2.0 planned/optional work and are
not part of the current default startup set.

Runtime profile or adapter docs must not be treated as prerequisites for v1.x
usage. They are optimization layers, not the governance core.

## Target Project Boundary

```yaml
target_project_rule:
  router_template: templates/DOCUMENT_MAP.template.md
  registry_template: templates/DOCUMENT_REGISTRY.template.md
  agent_rules_template: templates/agent_rules.template.yaml
  do_not_copy_as_is:
    - docs/DOCUMENT_MAP.md
    - docs/DOCUMENT_REGISTRY.md
    - agent/agent_rules.yaml
```

Use `docs/INSTALL_SURFACE.md` for the complete copy/template/customize/do-not-copy
rules.

## Maintenance Rules

1. Add full document rows to `docs/DOCUMENT_REGISTRY.md`, not this file.
2. Add task-type read sets to `docs/control/CONTEXT_BUDGET_POLICY.md`, not this
   file.
3. Add install/copy/template boundaries to `docs/INSTALL_SURFACE.md`, not this
   file.
4. Add skill-pack usage guidance to `docs/SKILL_PACK.md`, not this file.
5. Keep this file small enough to act as a router.
6. If this router exceeds the limits in `docs/control/DOCUMENT_MAP_POLICY.md`,
   stop and open a document-map maintenance issue.
