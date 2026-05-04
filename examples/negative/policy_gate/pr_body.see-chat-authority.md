## Summary

Negative fixture: PR body uses chat-only authority.

## Task Reference

Issue #000.

## Changed Files

- docs/example.md

## Validation

Not relevant; this is an expected-failure fixture.

## Evidence Of Completion

- Scope and acceptance are in see chat.

## Scope Boundaries

Allowed-path test surface only.

## Current Status Impact

```yaml
current_status_impact:
  status: not_applicable
  reason: "negative fixture only"
  current_status_updated_in_this_pr: false
  follow_up_issue: none
```

## Runtime Output Status

No runtime outputs.

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

## Known Gaps

This fixture is intentionally invalid.

## Handoff Report

```yaml
handoff:
  branch: test
  issue: "#000"
  validation_status: expected_failure
  next_safe_action: "Run policy_gate_check.py and expect failure."
```
