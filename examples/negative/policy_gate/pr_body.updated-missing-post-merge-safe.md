## Task Reference

Refs #132.

## Scope Boundaries

Current-status-only negative fixture.

## Current Status Impact

```yaml
current_status_impact:
  status: updated
  reason: "Updates current status but omits post_merge_safe."
  current_status_updated_in_this_pr: true
  follow_up_issue: none
```

## Merge Decision

```yaml
merge_decision:
  issue: "#132"
  lane: test
  intelligence_level: standard
  durable_source_of_truth: "#132"
  checks_passed: true
  allowed_paths_checked: true
  expected_output_checked: true
  contracts_checked: true
  schemas_checked: not_applicable
  storage_boundary: clean
  runtime_artifact_boundary: clean
  safety_review: "Fixture expects policy-gate failure."
  human_gates_checked: true
  result: merge_allowed
  reason: "Expected failure because post_merge_safe is missing."
```

## Handoff Report

Expected failure fixture.
