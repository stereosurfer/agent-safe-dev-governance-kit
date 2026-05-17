---
negative_case:
  id: NEG-PR-BODY-missing-current-status-impact
  title: PR body missing Current Status Impact section
  expected_outcome: blocked
  owner: pr_body_check
  should_block_positive_validation: false
---

## Summary

Expected failure: missing `## Current Status Impact`.

## Task Reference

Refs #000

## Changed Files

- docs/example.md

## Validation

Expected failure fixture.

## Evidence Of Completion

Expected failure fixture.

## Scope Boundaries

Expected failure fixture.

## Runtime Output Status

No runtime outputs.

## Merge Decision

```yaml
merge_decision:
  issue: "#000"
  lane: validation_tooling
  intelligence_level: standard
  durable_source_of_truth: "negative fixture"
  checks_passed: true
  allowed_paths_checked: true
  expected_output_checked: true
  contracts_checked: not_applicable
  schemas_checked: not_applicable
  storage_boundary: clean
  runtime_artifact_boundary: clean
  safety_review: negative_fixture
  human_gates_checked: true
  result: merge_blocked
  reason: "Expected failure fixture."
```

## Known Gaps

Missing Current Status Impact should block PR-body preflight.

## Handoff Report

Expected failure fixture.
