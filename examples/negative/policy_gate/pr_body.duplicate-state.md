## Summary

Negative fixture for duplicate durable decision state.

## Task Reference

Issue #000.

## Changed Files

- Fixture only.

## Validation

Expected strict and coherence failure.

## Evidence Of Completion

All unrelated fields are complete.

## Scope Boundaries

Duplicate `result` is the only intended defect.

## Current Status Impact

```yaml
current_status_impact:
  status: not_applicable
  reason: "negative fixture only"
  current_status_updated_in_this_pr: false
  post_merge_safe: not_applicable
  follow_up_issue: none
```

## Runtime Output Status

No runtime output.

## Merge Decision

```yaml
merge_decision:
  issue: "#000"
  lane: lane_06_ci_github
  intelligence_level: frontier
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
  validation_evidence_checked: true
  validation_claim_source:
    local_doctor: freshly_rerun
    ci: github_actions
  result: merge_allowed
  result: merge_blocked
  reason: "Expected failure because duplicate result fields are ambiguous."
```

## Known Gaps

No first-value or last-value interpretation is allowed.

## Handoff Report

Expected failure fixture.
