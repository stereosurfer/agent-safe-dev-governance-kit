---
name: asgk-issue-scoping
description: Use when turning a user request into an ASGK-compliant GitHub issue with objective, allowed paths, expected output, validation, non-goals, stop conditions, and rollback expectations.
---

# ASGK Issue Scoping

Use this skill before implementation when the user's request is not already captured in a durable GitHub issue.

## Authority

The created issue becomes the normal work-unit authority only after it is
written to GitHub. During independently verified GitHub unavailability, the
complete fallback defined by `docs/control/TASK_PACKET_FORMAT.md` may
temporarily bound local work, but this Skill does not prove the outage, approve
external action, or override repo rules.

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
7. Record the smallest exact `context_read_set` and the concrete
   `project_specific_validation`. These are execution gates, not extra
   task-identity fields. Repository entries must be existing in-root regular
   files; durable issue, PR, or URL references must occupy a complete item.
   Reject prose shortcuts, whole-repository, directory, glob, absolute, or
   outside-root context reads. A `not_applicable` project check must include a
   material reason.
8. Include validation commands, defaulting to the repository-local validation
   entrypoint for governance/scaffold work. In this ASGK source repository,
   that entrypoint is usually `python3 scripts/asgk.py doctor`; in target
   repositories, do not treat source-repo `doctor` as a universal completion
   gate.
9. For work that can claim completion, include the required completeness checks
   and the evidence boundary for what validation does not prove.
10. Create or update a GitHub issue before normal implementation. If GitHub is
    verifiably unavailable, write and validate the complete fallback before
    bounded local work, record the outage evidence, and keep a hard stop before
    PR creation or merge until the issue exists.
11. When the target provides `work-unit-check --authority-only`, run it before
    handing the issue to an executor. If the command is unavailable, record
    that boundary and manually verify the same fields without claiming a
    mechanical pass.

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

`reason` is the only formal name. Do not substitute
`intelligence_level_reason`.

## Required Execution Gates

- `context_read_set`
- `project_specific_validation`

The gates constrain reading and validation. They do not expand the 13-field task
identity or create another authority surface.

## Stop States

- `blocked`: allowed paths or validation are unclear.
- `blocked`: upgrade or adoption paths were proposed before read-only discovery.
- `requires_human`: protected paths, releases, visibility, dependencies, workflows, schemas, secrets, or other human-gated surfaces are involved.
- `fallback_ready_for_bounded_local_work`: GitHub unavailability is
  independently established, no escalation trigger applies, and a complete
  fallback passes its structural check; PR, merge, protected-path exceptions,
  and external actions remain blocked.
- `issue_created`: durable issue exists, contains the two execution gates, and
  has passed authority-only validation when that command is available.

## Exit Artifact

GitHub issue URL plus a one-paragraph note of the allowed paths, validation, and
first safe action; or, during an outage, the fallback path, outage evidence,
and exact issue-before-PR stop condition.
