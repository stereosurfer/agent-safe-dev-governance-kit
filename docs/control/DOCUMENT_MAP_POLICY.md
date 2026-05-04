# Document Map Policy

Status: active control policy.

This policy defines how ASGK and target repositories keep document navigation
small, explicit, and maintainable over time.

## Purpose

`docs/DOCUMENT_MAP.md` must remain a small repo-local navigation router. It must
not grow into the full repository document database.

This policy prevents document-map bloat, repeated authority text, and context
loading drift by splitting navigation surfaces into progressive-disclosure
layers.

## Progressive Disclosure Model

```yaml
progressive_disclosure_model:
  router:
    path: docs/DOCUMENT_MAP.md
    purpose: small repo-local navigation router
  registry:
    path: docs/DOCUMENT_REGISTRY.md
    purpose: complete repo-local document registry and canonical ownership table
  read_sets:
    path: docs/control/CONTEXT_BUDGET_POLICY.md
    purpose: context read sets, task-type reading guide, and expansion rules
  install_surface:
    path: docs/INSTALL_SURFACE.md
    purpose: target-project install copy/template/customize/do-not-copy boundary
  policy:
    path: docs/control/DOCUMENT_MAP_POLICY.md
    purpose: maintenance, size limits, and split rules
```

## Router Rules

`docs/DOCUMENT_MAP.md` is the default repo-local document navigation router.

It may contain:

```yaml
document_map_may_contain:
  - repo-local scope rule
  - default startup set
  - document role definitions
  - pointers to DOCUMENT_REGISTRY.md
  - pointers to CONTEXT_BUDGET_POLICY.md
  - pointers to INSTALL_SURFACE.md
  - v1.x/v2.0 profile and adapter boundary summary
  - emergency conflict rule
  - compact maintenance summary
```

It must not contain, after the registry split is complete:

```yaml
document_map_must_not_contain_after_split:
  - full document registry tables
  - complete task-type reading guide
  - install-surface checklist details
  - historical audit records
  - detailed readiness or stabilization plans
  - runtime-specific adapter instructions
```

## Size Limits

```yaml
size_limits:
  document_map_soft_limit_lines: 150
  document_map_hard_limit_lines: 220
  registry_no_hard_limit: true
  policy_no_hard_limit: true
```

If `docs/DOCUMENT_MAP.md` exceeds the soft limit, new content should normally go
to `docs/DOCUMENT_REGISTRY.md`, `docs/control/CONTEXT_BUDGET_POLICY.md`, or
`docs/INSTALL_SURFACE.md` instead.

If it exceeds the hard limit, stop and open a document-map split issue unless the
current issue explicitly authorizes a temporary exception.

## Registry Rules

`docs/DOCUMENT_REGISTRY.md` is the correct home for full document tables and
canonical ownership rows.

It may contain:

```yaml
document_registry_may_contain:
  - complete document tables
  - canonical_for entries
  - read_when entries
  - owned_by_lane entries
  - registry-level ownership notes
  - summary-vs-canonical relationships
```

It must not become the default startup document.

Read it only when:

```yaml
read_document_registry_when:
  - canonical ownership is unclear
  - current issue changes document ownership
  - current issue changes document-map or registry structure
  - validation or reviewer feedback points to registry mismatch
  - target work explicitly requires a registry audit
```

## Context Read-Set Rules

Task-type reading guides and context expansion rules belong in
`docs/control/CONTEXT_BUDGET_POLICY.md`.

`docs/DOCUMENT_MAP.md` should point to that policy instead of duplicating full
read sets.

## Install-Surface Rules

Target-project copy/template/customize/do-not-copy rules belong in
`docs/INSTALL_SURFACE.md`.

`docs/DOCUMENT_MAP.md` should point to that policy instead of duplicating the
install checklist.

## Target Repository Rules

Target repositories that adopt ASGK should use the same split:

```yaml
target_repo_document_navigation:
  docs/DOCUMENT_MAP.md: small repo-local router
  docs/DOCUMENT_REGISTRY.md: full target repo registry
  docs/control/CONTEXT_BUDGET_POLICY.md: target repo read sets
```

Target repositories must not copy ASGK's internal `docs/DOCUMENT_MAP.md` or
`docs/DOCUMENT_REGISTRY.md` unchanged.

## Maintenance Rules

1. Add new document rows to `docs/DOCUMENT_REGISTRY.md`, not the router, unless
   the row is part of the default startup set.
2. Add new task-type read sets to `docs/control/CONTEXT_BUDGET_POLICY.md`.
3. Add new install/copy/template boundaries to `docs/INSTALL_SURFACE.md`.
4. Keep `docs/DOCUMENT_MAP.md` small enough to read as a routing document.
5. If a summary document repeats canonical policy text, replace the repeated text
   with a pointer to the canonical document in a separate issue.
6. If two documents disagree, prefer the document marked canonical for that topic
   and repair the stale summary or registry entry.
7. When changing this policy, update `docs/DOCUMENT_MAP.md`,
   `docs/DOCUMENT_REGISTRY.md`, and target templates if their split behavior
   changes.

## Migration Note

The first split stage may leave existing full registry tables in
`docs/DOCUMENT_MAP.md` temporarily while this policy and registry structure are
introduced. The next bounded work unit should move the full registry tables to
`docs/DOCUMENT_REGISTRY.md` and leave `docs/DOCUMENT_MAP.md` as a compact router.
