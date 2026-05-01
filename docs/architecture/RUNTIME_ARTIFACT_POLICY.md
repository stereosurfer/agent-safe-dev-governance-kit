# Runtime Artifact Policy

Runtime outputs are not source code.

## Do not commit

```text
runs/
corpus/
artifacts/
raw captures
private files
SQLite live DB
model cache
preview cache
external preparation outputs
```

## Allowed in repo

```text
tests/fixtures/
examples/
```

Only small, sanitized, intentional fixtures may live in repo.

## Before commit

Run:

```bash
git status --short
git diff --cached --name-only
```

If runtime or private artifacts are staged, unstage them.
