# Merge Decision Record

Each merge-eligible PR must include a Merge Decision Record.

```yaml
merge_decision:
  issue:
  lane:
  intelligence_level:
  durable_source_of_truth:
  checks_passed:
  allowed_paths_checked:
  expected_output_checked:
  contracts_checked:
  schemas_checked:
  storage_boundary:
  runtime_artifact_boundary:
  safety_review:
  human_gates_checked:
  result: merge_allowed | merge_blocked
  reason:
```

A missing or blocked Merge Decision Record blocks autonomous merge.
