## Summary

Negative fixture: missing Merge Decision section.

## Task Reference

Issue #000.

## Changed Files

- docs/example.md

## Validation

Not relevant; this is an expected-failure fixture.

## Evidence Of Completion

- Fixture intentionally omits Merge Decision.

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
