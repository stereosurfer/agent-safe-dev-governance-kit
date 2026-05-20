---
name: asgk-issue-scoping
description: Use when turning a user request into an ASGK-compliant GitHub issue with objective, allowed paths, expected output, validation, non-goals, stop conditions, and rollback expectations.
---

# ASGK Issue Scoping

Use this skill before implementation when the user's request is not already captured in a durable GitHub issue.

## Authority

The created issue becomes the work-unit authority only after it is written to GitHub. This skill may draft scope, but it does not approve work or override repo rules.

## Required Inputs

- User objective or observed repo problem.
- Target repository.
- Known allowed paths or enough repo context to propose conservative allowed paths.
- For upgrade or adoption work, read-only discovered ASGK-derived surfaces before
  allowed paths are finalized.
- Validation command if known.

## Procedure

1. Classify the task lane and risk level.
2. Propose the smallest work unit that can produce a reviewable output.
3. For upgrade or adoption work, run a read-only discovery pass before setting
   allowed paths. Include ASGK-derived docs, profiles, manifests, validators,
   planner references, and target-owned files that must be preserved but still
   inspected for stale references.
4. List allowed paths narrowly from the discovered surfaces. Do not make the
   issue narrow by guessing before discovery.
5. Write explicit non-goals and stop conditions.
6. Include rollback expectations.
7. Include validation commands, defaulting to the repository-local validation
   entrypoint for governance/scaffold work. In this ASGK source repository,
   that entrypoint is usually `python3 scripts/asgk.py doctor`; in target
   repositories, do not treat source-repo `doctor` as a universal completion
   gate.
8. For work that can claim completion, include the required completeness checks
   and the evidence boundary for what validation does not prove.
9. Create or update a GitHub issue; do not start edits until the durable issue exists.

## Required Issue Fields

- `lane`
- `intelligence_level`
- `reason`
- `durable_source_of_truth`
- `objective`
- `plan`
- `checklist`
- `acceptance_sheet`
- `allowed_paths`
- `expected_output`
- `non_goals`
- `stop_conditions`
- `rollback_expectations`

## Stop States

- `blocked`: allowed paths or validation are unclear.
- `blocked`: upgrade or adoption paths were proposed before read-only discovery.
- `requires_human`: protected paths, releases, visibility, dependencies, workflows, schemas, secrets, or other human-gated surfaces are involved.
- `issue_created`: durable issue exists and can be used by an executor.

## Exit Artifact

GitHub issue URL plus a one-paragraph note of the allowed paths, validation, and first safe action.
