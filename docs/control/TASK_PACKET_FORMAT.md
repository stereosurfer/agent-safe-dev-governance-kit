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
