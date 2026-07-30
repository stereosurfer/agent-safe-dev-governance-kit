## Summary

Positive fixture for a truthful draft whose declared Merge Decision remains
blocked while CI and human review are incomplete.

## Task Reference

GitHub issue #326.

## Changed Files

- `scripts/asgk.py`

## Validation

The fixture itself has been inspected, but live GitHub Actions and review remain
pending. This evidence proves body-state consistency only.

## Evidence Of Completion

- Required body sections and decision fields are present.
- The unresolved checks and human gate are recorded without claiming approval.

## Scope Boundaries

Fixture-only governance validation. No merge eligibility, low-risk status, or
human approval is inferred.

## Current Status Impact

```yaml
current_status_impact:
  status: not_applicable
  reason: "The fixture does not change repository recovery state."
  current_status_updated_in_this_pr: false
  post_merge_safe: not_applicable
  follow_up_issue: none
```

## Runtime Output Status

No runtime outputs or private source material are included.

## Merge Decision

```yaml
merge_decision:
  issue: "#326"
  lane: lane_06_ci_github
  intelligence_level: frontier
  durable_source_of_truth: "GitHub issue #326"
  checks_passed: pending
  allowed_paths_checked: true
  expected_output_checked: true
  contracts_checked: not_applicable
  schemas_checked: true
  storage_boundary: no_runtime_or_storage_boundary_change
  runtime_artifact_boundary: no_runtime_artifacts_added
  safety_review: fixture_boundary_reviewed
  human_gates_checked: false
  validation_evidence_checked: true
  validation_claim_source:
    local_doctor: not_run
    ci: not_run
  result: merge_blocked
  reason: "CI and durable human review of the current diff are incomplete; this body is coherent for submission but is not merge-eligible."
```

## Known Gaps

- Live PR metadata, CI, and human judgment are intentionally absent.

## Handoff Report

Next safe action: submit the body as a draft, wait for body-coherence CI, then
mark the PR ready for review while it remains `merge_blocked`.
