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
- Validation command if known.

## Procedure

1. Classify the task lane and risk level.
2. Propose the smallest work unit that can produce a reviewable output.
3. List allowed paths narrowly.
4. Write explicit non-goals and stop conditions.
5. Include rollback expectations.
6. Include validation commands, defaulting to `python3 scripts/asgk.py doctor` for governance/scaffold work.
7. Create or update a GitHub issue; do not start edits until the durable issue exists.

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
- `requires_human`: protected paths, releases, visibility, dependencies, workflows, schemas, secrets, or other human-gated surfaces are involved.
- `issue_created`: durable issue exists and can be used by an executor.

## Exit Artifact

GitHub issue URL plus a one-paragraph note of the allowed paths, validation, and first safe action.
