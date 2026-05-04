## Summary

## Task Reference

## Changed Files

## Validation

For each validation claim, state both the result and the evidence source. Do
not write only `passed` when the check was not freshly rerun in this work unit.

```yaml
validation_evidence:
  local_commands:
    - command:
      status: passed | failed | not_run | not_applicable
      source: freshly_rerun | recorded_in_pr_body | existing_durable_record | not_run
      evidence: command output summary, PR comment, commit, or reason not run
  ci_checks:
    - name:
      status: passed | failed | pending | not_applicable
      source: github_actions | external_ci | not_run
      evidence: check name, run URL, or reason not applicable
  inferred_or_prior_evidence:
    - claim:
      source: merged_pr | issue_comment | repo_file | none
      evidence:
      current_work_unit_rerun: true | false
```

## Evidence Of Completion

## Scope Boundaries

## Current Status Impact

```yaml
current_status_impact:
  status: updated | not_applicable | deferred
  reason:
  current_status_updated_in_this_pr: true | false
  follow_up_issue: none | "#<number>"
```

Use `docs/control/CURRENT_STATUS_POLICY.md`.

## Runtime Output Status

## Merge Decision

```yaml
merge_decision:
  issue:
  lane:
  intelligence_level:
  durable_source_of_truth:
  checks_passed:
  allowed_paths_checked:
  expected_output_checked:
  contracts_checked:
  schemas_checked:
  storage_boundary:
  runtime_artifact_boundary:
  safety_review:
  human_gates_checked:
  validation_evidence_checked:
  validation_claim_source:
    local_doctor: freshly_rerun | recorded_in_pr_body | existing_durable_record | not_run | not_applicable
    ci: github_actions | external_ci | not_run | not_applicable
  result: merge_allowed | merge_blocked
  reason:
```

## Known Gaps

## Handoff Report
