# 04 File Structure

Recommended layout:

```text
docs/
  bootstrap/
  architecture/
  control/
  handoff/
agent/
  task_packets/
contracts/
schemas/
scripts/
tests/
examples/
.github/
```

## Dependency direction

Define implementation dependency direction before code grows.

Example:

```text
capture -> normalize -> extract -> validate -> package
```

Reverse dependency requires an architecture issue.

## Rule

File hierarchy is part of architecture. Agent tasks must not create new top-level directories without explicit approval.
