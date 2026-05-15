## Summary

Compact PR body fixture.

Closes #1003

## Task Reference

- GitHub issue: #1003

## Compiled Report Reference

```yaml
compact_pr_report:
  report_source: examples/compact_governance/pr_report_body_profile.valid-report.json
  report_result: pass
  pr_status_result: pass
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
      status: passed
      source: freshly_rerun
      evidence: "Fixture body references a passing compiled report."
      limits: "Fixture only."
  ci_checks:
    - name: validate
      status: passed
      source: github_actions
      evidence: "Fixture report records passing CI."
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

- Fixture compact profile is complete.

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
  issue: "Closes #1003"
  lane: validation_tooling
  intelligence_level: frontier
  durable_source_of_truth: "GitHub issue #1003, this PR body, and compiled report fixture"
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
    ci: github_actions
  result: merge_allowed
  reason: "Fixture gates are complete."
```

## Known Gaps

- Fixture only.

## Handoff Report

No handoff action.
