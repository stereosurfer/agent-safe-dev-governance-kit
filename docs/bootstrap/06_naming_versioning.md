# 06 Naming Versioning

## Branches

```text
codex/<short-task-name>
feat/issue-000-short-name
fix/issue-000-short-name
docs/issue-000-short-name
```

## Commits

```text
feat(scope): short imperative summary
fix(scope): short imperative summary
docs(scope): short imperative summary
test(scope): short imperative summary
```

## Time

Use UTC ISO 8601:

```text
2026-05-01T00:00:00Z
```

Filename-safe timestamps:

```text
20260501T000000Z
```

## Schema versions

```yaml
schema_version: 0.1.0
```

```text
patch = clarification or compatible validation fix
minor = backward-compatible field addition
major = semantic change or field removal
```
