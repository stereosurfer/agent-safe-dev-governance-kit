# Failure Thresholds

Stop autonomous work and notify the human when:

```yaml
failure_thresholds:
  repeated_test_failure_count: 2
  conflicting_instruction_count: 1
  protected_path_attempt_count: 1
  schema_breaking_change_required: true
  new_dependency_required: true
  external_call_required: true
  unrelated_diff_detected: true
  runtime_artifact_staged: true
```

## Notification conditions

- lane blocked by missing context;
- worker exceeds allowed paths;
- integration conflict requires policy decision;
- validation cannot run;
- issue and current status disagree;
- PR receives requested changes.
