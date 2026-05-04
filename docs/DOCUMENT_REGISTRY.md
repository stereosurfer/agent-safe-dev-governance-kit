# Document Registry

Status: active repo-local registry surface.

This file is the designated home for the complete ASGK repository document
registry.

`docs/DOCUMENT_MAP.md` is the compact navigation router. This file is the full
registry surface used when canonical ownership, read conditions, or document-role
rows must be inspected or updated.

## Scope

```text
DOCUMENT_REGISTRY.md is repo-local.
```

This file governs the ASGK repository only. Target repositories must create
their own `docs/DOCUMENT_REGISTRY.md` from
`templates/DOCUMENT_REGISTRY.template.md` when they adopt the router + registry
split.

## Relationship To DOCUMENT_MAP.md

```yaml
relationship:
  docs/DOCUMENT_MAP.md: compact navigation router
  docs/DOCUMENT_REGISTRY.md: complete document registry
  docs/control/DOCUMENT_MAP_POLICY.md: maintenance and split policy
```

Do not read this file by default. Read it only when:

```yaml
read_when:
  - canonical ownership is unclear
  - current issue changes document ownership
  - current issue changes document-map or registry structure
  - validation or reviewer feedback points to registry mismatch
  - target work explicitly requires a registry audit
```

## Registry Migration Status

```yaml
registry_migration_status:
  stage: structure_created
  full_registry_tables_moved: false
  current_full_registry_source: docs/DOCUMENT_MAP.md
  next_work_unit: move full document registry tables from DOCUMENT_MAP.md to DOCUMENT_REGISTRY.md
```

## Future Registry Sections

The next migration work unit should move these full tables from
`docs/DOCUMENT_MAP.md` into this file:

```yaml
future_sections:
  - Entry And Startup Documents
  - Installation And Target Project Templates
  - Handoff And Recovery Documents
  - Adapter Mechanism And Future Runtime Profiles
  - Control Documents
  - Merge And Human-Gate Documents
  - Storage And Runtime Boundary Documents
  - Bootstrap Documents
  - Task Packet, Agent, And Template Documents
  - Contracts And Schemas
  - Scripts And CI
  - Examples And Fixtures
```

## Registry Row Format

Use this table format when the full registry is migrated:

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `<path>` | `<role>` | `<topic>` | no | `<condition>` | `<lane>` |

## Registry Rules

1. Add new document rows here after the split is complete.
2. Keep `docs/DOCUMENT_MAP.md` as a compact router.
3. Do not add task-type read sets here; use `docs/control/CONTEXT_BUDGET_POLICY.md`.
4. Do not add install-surface rules here; use `docs/INSTALL_SURFACE.md`.
5. If this registry conflicts with a canonical document, fix the registry or the
   stale summary in a separate issue.
