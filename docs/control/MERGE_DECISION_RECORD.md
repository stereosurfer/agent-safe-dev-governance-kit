# Merge Decision Record

Each merge-eligible PR must include a Merge Decision Record.

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

A missing or blocked Merge Decision Record blocks autonomous merge.

## Validation Evidence Source

Validation claims must say where the evidence came from. Do not collapse
different evidence sources into a generic `passed` statement.

Use this vocabulary when practical:

```yaml
validation_evidence_source:
  freshly_rerun: "The command was run in the current work unit."
  recorded_in_pr_body: "The PR body records the result, but the current reviewer did not rerun it."
  github_actions: "The result was observed from GitHub Actions or another named CI check."
  existing_durable_record: "The result comes from a merged PR, issue comment, repo file, or other durable record."
  inferred_from_merged_pr: "The result is inferred from the fact that a merged PR recorded or required it."
  not_run: "The check was not run."
  not_applicable: "The check does not apply to this work unit."
```

If a final report says a command passed, it should distinguish:

```yaml
validation:
  local_doctor:
    status: passed | failed | not_run | not_applicable
    source: freshly_rerun | recorded_in_pr_body | existing_durable_record | not_run | not_applicable
  github_actions:
    status: passed | failed | pending | not_applicable
    source: github_actions | external_ci | not_run | not_applicable
```
