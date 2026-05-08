# Task Packet Format

Use this format for all agent-executable work.

```yaml
task_id:
lane:
intelligence_level:
intelligence_level_reason:
durable_source_of_truth:
objective:
product_context:
current_repository_context:
files_to_inspect_first:
allowed_paths:
expected_changes:
expected_output:
non_goals:
constraints:
plan:
checklist:
acceptance_sheet:
validation_commands:
stop_conditions:
rollback_expectations:
```

No field may say `see chat`.

## Context Read Gate

`files_to_inspect_first` is the task-level context read gate. It must name the
smallest specific files or durable pseudo-reference needed before work starts.

Allowed examples:

```yaml
files_to_inspect_first:
  - AGENTS.md
  - docs/handoff/CURRENT_STATUS.md
  - current GitHub issue or PR
  - docs/control/TASK_PACKET_FORMAT.md
```

Blocked examples:

```yaml
files_to_inspect_first:
  - whole repo
  - all docs
  - docs/**
  - .
  - "*"
```

Use `context_read_set` in the GitHub issue, PR Context Budget section, or Agent
Report when the task type needs read-set reporting. Do not create a separate
context protocol or sidecar context artifact.
