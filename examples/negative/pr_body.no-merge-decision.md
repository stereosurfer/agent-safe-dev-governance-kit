---
negative_case:
  id: NEG-004-missing-merge-decision
  title: PR body missing Merge Decision section
  expected_outcome: blocked
  owner: pr_review_or_future_pr_validator
  should_block_positive_validation: false
---

## Summary

Expected failure: missing `## Merge Decision`.

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

No runtime outputs.

## Known Gaps

Missing Merge Decision Record should block PR-body preflight.

## Handoff Report

Expected failure fixture.
