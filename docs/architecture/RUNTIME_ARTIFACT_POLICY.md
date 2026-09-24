# Runtime Artifact Policy

Runtime outputs are not source code.

Use `docs/architecture/LOG_AND_RECORD_RETENTION_POLICY.md` for ASGK source
record classes. It does not choose a target application's runtime storage
layout. A live target-owned issue must authorize any external or private
destination; a delivery contract may refine placement but cannot grant write
or human-gate authority by itself.

## Do not commit

Do not commit raw captures, private files, live databases, model or preview
caches, scratch, generated run outputs, or external preparation outputs. The
ASGK source hygiene check recognizes paths such as `runs/`, `corpus/`, and
`artifacts/` as blocking changed-path findings; that path-only check is not a
universal target-repo directory specification.

## Allowed in repo

```text
tests/fixtures/
examples/
```

Only small, sanitized, intentional fixtures may live in the ASGK source repo.
Versioned Lessons, tests, and task methods are source changes only after
issue/PR review; raw experience dumps and Bot memory are not fixtures.

## Before commit

Run:

```bash
git status --short
git diff --cached --name-only
```

If runtime or private artifacts are staged, unstage them.
