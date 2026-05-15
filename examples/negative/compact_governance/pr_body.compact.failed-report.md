## Summary

Compact PR body fixture with a failed compiled report.

Closes #1004

## Task Reference

- GitHub issue: #1004

## Compiled Report Reference

```yaml
compact_pr_report:
  report_source: examples/negative/compact_governance/pr-report.metadata-unavailable.json
  report_result: fail_closed
  pr_status_result: missing
  low_risk_inferred: false
```

## Context Read Set

```yaml
context_read_set:
  selected: tooling_or_validation
  files_read:
    - scripts/asgk.py
  expansion_reason: none
  limits: "Fixture only."
```

## Changed Files

- `scripts/asgk.py`

## Validation

```yaml
validation_evidence:
  local_commands:
    - command: "compact-pr-body-check fixture"
      status: failed
      source: freshly_rerun
      evidence: "Fixture intentionally references a failed report."
      limits: "Fixture only."
  ci_checks:
    - name: validate
      status: not_applicable
      source: not_run
      evidence: "Fixture only."
      limits: "Fixture only."
  inferred_or_prior_evidence: []
  project_specific_tests:
    - command: "not_applicable"
      status: not_applicable
      source: not_applicable
      evidence: "Fixture only."
      limits: "Fixture only."
```

## Evidence Of Completion

- Fixture intentionally fails.

## Scope Boundaries

- Fixture only.

## Current Status Impact

```yaml
current_status_impact:
  status: not_applicable
  reason: "Fixture does not change CURRENT_STATUS.md."
  current_status_updated_in_this_pr: false
  post_merge_safe: not_applicable
  follow_up_issue: none
```

## Runtime Output Status

No runtime outputs.

## Merge Decision

```yaml
merge_decision:
  issue: "Closes #1004"
  lane: validation_tooling
  intelligence_level: frontier
  durable_source_of_truth: "GitHub issue #1004, this PR body, and compiled report fixture"
  checks_passed: true
  allowed_paths_checked: true
  expected_output_checked: true
  contracts_checked: true
  schemas_checked: not_applicable
  storage_boundary: not_applicable
  runtime_artifact_boundary: true
  safety_review: true
  human_gates_checked: true
  validation_evidence_checked: true
  validation_claim_source:
    local_doctor: freshly_rerun
    ci: not_applicable
  result: merge_allowed
  reason: "Fixture intentionally overclaims despite failed report."
```

## Known Gaps

- Fixture only.

## Handoff Report

No handoff action.
