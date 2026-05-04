# Document Map

Status: target-project navigation router template.

This template is for a repository that installs or adopts ASGK governance. It is
not the ASGK repository's own document map.

The finished target-project `docs/DOCUMENT_MAP.md` should remain a small
repo-local navigation router. Put full registry tables in
`docs/DOCUMENT_REGISTRY.md`, not here.

## Scope Rule

```text
DOCUMENT_MAP.md is repo-local.
```

ASGK's internal `docs/DOCUMENT_MAP.md` governs only the ASGK repository. A target
project must own its own `docs/DOCUMENT_MAP.md` and `docs/DOCUMENT_REGISTRY.md`
after installation.

Do not copy ASGK's internal document map unchanged into a target repository.

## Core Rule

```text
Do not read the whole repository for every task.
Read the smallest set of canonical documents required by the work unit.
```

If two documents appear to disagree, prefer the document marked `canonical` for
that topic in `docs/DOCUMENT_REGISTRY.md`. If a summary document disagrees with a
canonical document, the summary document is stale and should be fixed in a
separate issue.

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

## Navigation Surfaces

```yaml
navigation_surfaces:
  router:
    path: docs/DOCUMENT_MAP.md
    read_by_default: false
    read_when:
      - document ownership is unclear
      - current issue asks for map/router work
  registry:
    path: docs/DOCUMENT_REGISTRY.md
    read_by_default: false
    read_when:
      - canonical ownership must be inspected or changed
      - registry row must be added or repaired
  read_sets:
    path: docs/control/CONTEXT_BUDGET_POLICY.md
    read_by_default: false
    read_when:
      - task-specific context selection is needed
      - context expansion is required
```

## Target Registry

The target repository should create its complete registry from
`templates/DOCUMENT_REGISTRY.template.md`:

```text
templates/DOCUMENT_REGISTRY.template.md
  -> target repo docs/DOCUMENT_REGISTRY.md
```

`docs/DOCUMENT_MAP.md` should point to the registry, not duplicate the full
registry tables.

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
  future_optional: Planned future capability, not part of the current core.
```

## Compact Entry Summary

Keep this section short. Full rows belong in `docs/DOCUMENT_REGISTRY.md`.

```yaml
entry_summary:
  default_startup:
    - AGENTS.md
    - README.md
    - docs/handoff/CURRENT_STATUS.md
    - current GitHub issue or PR
  full_registry: docs/DOCUMENT_REGISTRY.md
  context_read_sets: docs/control/CONTEXT_BUDGET_POLICY.md
```

## Maintenance Rules

1. Keep this file small enough to act as a router.
2. Add full document rows to `docs/DOCUMENT_REGISTRY.md`, not this file.
3. Add task-type read sets to `docs/control/CONTEXT_BUDGET_POLICY.md`, not this
   file.
4. Summary documents should point to canonical documents rather than repeating
   full policy text.
5. If a document becomes canonical for a new topic, update
   `docs/DOCUMENT_REGISTRY.md` in the same PR.
