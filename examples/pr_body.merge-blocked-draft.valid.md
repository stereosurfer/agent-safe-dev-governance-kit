## Summary

Valid blocked-draft PR body coherence fixture.

## Task Reference

Issue #326.

## Changed Files

- `scripts/policy_gate_check.py`

## Validation

One required check has not passed.

## Evidence Of Completion

The body is complete enough to submit for review, but it does not claim merge
eligibility.

## Scope Boundaries

Allowed paths and expected output were checked before submission.

## Current Status Impact

```yaml
current_status_impact:
  status: not_applicable
  reason: "Fixture-only change does not alter repository recovery state."
  current_status_updated_in_this_pr: false
  post_merge_safe: not_applicable
  follow_up_issue: none
```

## Runtime Output Status

No runtime artifacts.

## Merge Decision

```yaml
merge_decision:
  issue: "#326"
  lane: lane_06_ci_github
  intelligence_level: frontier
  durable_source_of_truth: "GitHub issue #326"
  checks_passed: false
  allowed_paths_checked: true
  expected_output_checked: true
  contracts_checked: not_applicable
  schemas_checked: not_applicable
  storage_boundary: unchanged
  runtime_artifact_boundary: clean
  safety_review: "Review is still in progress."
  human_gates_checked: pending
  result: merge_blocked
  reason: "A required check is false and required human review is pending."
```

## Known Gaps

Strict merge eligibility must reject this fixture.

## Handoff Report

Submit the truthful blocked draft; do not merge it.
