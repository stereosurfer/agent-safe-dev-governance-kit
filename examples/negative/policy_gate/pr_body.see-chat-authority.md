## Task Reference

Issue #000. Scope and acceptance are in see chat.

## Scope Boundaries

Expected failure: chat-only authority.

## Current Status Impact

```yaml
current_status_impact:
  status: not_applicable
  reason: "negative fixture only"
  current_status_updated_in_this_pr: false
  post_merge_safe: not_applicable
  follow_up_issue: none
```

## Merge Decision

```yaml
merge_decision:
  issue: "#000"
  lane: lane_07_docs_handoff
  intelligence_level: standard
  durable_source_of_truth: "negative fixture"
  checks_passed: true
  allowed_paths_checked: true
  expected_output_checked: true
  contracts_checked: not_applicable
  schemas_checked: not_applicable
  storage_boundary: no_runtime_or_storage_boundary_change
  runtime_artifact_boundary: no_runtime_artifacts_added
  safety_review: negative_fixture
  human_gates_checked: true
  result: merge_blocked
  reason: "Expected failure fixture."
```

## Handoff Report

Expected failure fixture.
