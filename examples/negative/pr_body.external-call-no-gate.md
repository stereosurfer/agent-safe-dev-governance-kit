---
negative_case:
  id: NEG-022-cloud-api-mcp-without-gate
  title: PR opens external call capability without human gate
  expected_outcome: human_gated
  owner: human_gate_or_pr_review
  should_block_positive_validation: false
---

## Summary

Expected stop: the issue scopes a new live external API/model capability, but
the applicable human gate has no approval. This is review guidance, not an executable
scenario in the current registry.

## Task Reference

Refs #000

## Scope Boundaries

This PR enables a live external call within its current issue's scope but does
not show an applicable human approval record.

## Current Status Impact

```yaml
current_status_impact:
  status: not_applicable
  reason: "negative fixture"
  current_status_updated_in_this_pr: false
  post_merge_safe: not_applicable
  follow_up_issue: none
```

## Merge Decision

```yaml
merge_decision:
  issue: "#000"
  lane: "lane_00_controller"
  intelligence_level: "standard"
  durable_source_of_truth: "GitHub issue #000"
  checks_passed: true
  allowed_paths_checked: true
  expected_output_checked: true
  contracts_checked: "not applicable"
  schemas_checked: "not applicable"
  storage_boundary: "not checked"
  runtime_artifact_boundary: "not checked"
  safety_review: "incorrectly marked low risk"
  human_gates_checked: false
  result: merge_allowed
  reason: "bad example: should be human_gated, not merge_allowed"
```

## Handoff Report

This should be blocked or human-gated.
