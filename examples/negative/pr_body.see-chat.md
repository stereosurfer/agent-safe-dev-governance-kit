---
negative_case:
  id: NEG-031-pr-body-see-chat
  title: PR body uses chat as authority
  expected_outcome: blocked
  owner: pr_review_or_asgk_pr_body_check
  should_block_positive_validation: false
---

## Summary

This PR body intentionally uses forbidden chat-only authority language.

## Task Reference

Refs #000

Durable source of truth: see chat

## Changed Files

- docs/example.md

## Validation

Not relevant for this negative fixture.

## Evidence Of Completion

This is a bad example.

## Scope Boundaries

This is a bad example.

## Runtime Output Status

No runtime artifacts.

## Merge Decision

```yaml
merge_decision:
  issue: "#000"
  lane: "lane_00_controller"
  intelligence_level: "standard"
  durable_source_of_truth: "see chat"
  checks_passed: true
  allowed_paths_checked: true
  expected_output_checked: true
  contracts_checked: "not applicable"
  schemas_checked: "not applicable"
  storage_boundary: "not checked"
  runtime_artifact_boundary: "not checked"
  safety_review: "bad example"
  human_gates_checked: true
  result: merge_allowed
  reason: "bad example: should be blocked because it says see chat"
```

## Known Gaps

This should be blocked.

## Handoff Report

This should be blocked.
