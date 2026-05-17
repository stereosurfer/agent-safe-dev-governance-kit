---
negative_case:
  id: NEG-031-pr-body-see-chat
  title: PR body uses chat as authority
  expected_outcome: blocked
  owner: pr_review_or_asgk_pr_body_check
  should_block_positive_validation: false
---

## Summary

Expected failure: PR body uses forbidden chat-only authority.

## Task Reference

Durable source of truth: see chat.

## Changed Files

- docs/example.md

## Validation

Expected failure fixture.

## Evidence Of Completion

Expected failure fixture.

## Scope Boundaries

Expected failure fixture.

## Current Status Impact

```yaml
current_status_impact:
  status: not_applicable
  reason: "negative fixture"
  current_status_updated_in_this_pr: false
  post_merge_safe: not_applicable
  follow_up_issue: none
```

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

Chat-only authority should block PR-body preflight.

## Handoff Report

Expected failure fixture.
