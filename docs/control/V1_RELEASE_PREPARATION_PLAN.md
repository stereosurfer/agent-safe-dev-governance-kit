# V1 Release Preparation Plan

Status: active planning document.

This document plans ASGK v1.0 release preparation after v1.1 stabilization,
Vertical Governance Completion, and the first real-world field test have
completed.

It is a planning document only. It does not choose a license, tag a release,
publish a package, create a GitHub release, or start release execution.

## Scope

```yaml
release_preparation_scope:
  allowed_in_this_plan:
    - final readiness review checklist
    - license-selection decision path
    - tag and release process plan
    - package or distribution boundary
    - explicit v2.0 deferrals
    - remaining human gates
  not_allowed_in_this_plan:
    - license selection
    - release tag creation
    - GitHub release creation
    - package publication
    - installer scaffold
    - runtime-specific adapter work
    - dependency changes
    - schema or workflow changes
```

## Preconditions

```yaml
preconditions:
  vertical_governance_completion:
    status: completed
    source: "#102 / PR #103"
  real_world_field_test:
    status: completed
    source: "#112 / PR #113"
  post_field_test_readiness_audit:
    status: completed
    source: "#114 / PR #115"
  release_preparation_planning:
    status: completed
    source: "#116 / PR #117"
  current_status_closeout:
    status: completed
    source: "#118 / PR #119"
```

## Release Preparation Gates

```yaml
release_preparation_gates:
  final_readiness_review:
    required: true
    human_gate: true
    status: completed_by_120
    output: "ready_to_propose_release_execution_issue"
  license_selection:
    required: true
    human_gate: true
    status: not_selected
    output: "license choice or explicit no-license-release decision"
  tag_release_process:
    required: true
    human_gate: true
    status: not_started
    output: "documented process for release tag and GitHub release, but no tag created here"
  package_distribution_boundary:
    required: true
    human_gate: true
    status: not_selected
    output: "what is distributed, what remains source-only, and what is excluded"
  v2_0_deferrals:
    required: true
    human_gate: maybe
    status: explicit
    output: "explicit list of runtime-specific adapters and productization items deferred to v2.0"
  release_execution_issue:
    required: true
    human_gate: true
    status: not_created
    output: "separate issue if release execution is approved"
```

## Final Readiness Review Result

```yaml
final_readiness_review_result:
  issue: "#120"
  status: ready_to_propose_release_execution
  blockers:
    v1_0_core_blockers: []
    sequence_blockers: []
  recommendation: "Create a separate human-gated release-execution or release-decision issue."
  not_authorized:
    - license selection
    - release tag creation
    - GitHub release creation
    - package publication
    - external distribution
```

## Final Readiness Review Checklist

Before release execution can be considered, review:

```yaml
final_readiness_review:
  required_documents:
    - docs/control/V1_READINESS_AUDIT.md
    - docs/control/V1_1_STABILIZATION_PLAN.md
    - docs/bootstrap/10_roadmap.md
    - docs/control/HUMAN_GATED_OPERATIONS.md
    - docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
    - docs/DOCUMENT_REGISTRY.md
  required_checks:
    - python3 scripts/asgk.py doctor
  review_questions:
    - Are there any unresolved v1.0 core blockers?
    - Are all sequence gates either completed or explicitly deferred?
    - Are v2.0 runtime-specific adapters clearly excluded from v1.0?
    - Is the release surface source-only, package-based, or both?
    - Is license selection approved by a human?
    - Is release execution separated into a later issue?
```

## License Selection Decision Path

License selection is human-gated and must not be inferred by an agent.

```yaml
license_selection:
  status: not_selected
  human_gate_required: true
  allowed_outputs:
    - selected_license_with_approval
    - no_public_release_until_license_selected
    - internal_only_distribution_until_license_selected
  stop_conditions:
    - license not approved
    - license compatibility unclear
    - package/publication requested without license approval
```

## Tag And Release Process Plan

This planning document may describe a future process. It must not execute it.

```yaml
tag_release_process:
  planned_steps:
    - create release-execution issue
    - confirm final readiness review
    - confirm license decision
    - run python3 scripts/asgk.py doctor
    - check git status and target commit
    - create tag only in release-execution issue
    - create GitHub release only if explicitly approved
  forbidden_here:
    - git tag
    - gh release create
    - package publish
    - changelog publication as release announcement
```

## Package Or Distribution Boundary

```yaml
package_distribution_boundary:
  status: not_selected
  options_to_decide_later:
    - source-only GitHub release
    - template repository usage
    - downloadable archive
    - package manager publication
    - GitHub App or SaaS packaging
  v1_recommended_default_for_planning:
    - source-only repository release unless human chooses otherwise
  stop_conditions:
    - package manager publication requested
    - external distribution requested
    - generated artifact or runtime output included
```

## Explicit V2.0 Deferrals

```yaml
v2_0_deferrals:
  runtime_profiles:
    - Codex-specific profile
    - Claude Code profile
    - Cursor profile
    - ChatGPT Web / GitHub connector profile
    - OpenGoat profile
  productization:
    - GitHub App
    - SaaS
    - installer scaffold
    - default CI wiring for optional negative suites
    - runtime-specific adapter testing
  rule:
    - these are not v1.0 blockers unless a release-preparation issue explicitly changes scope
```

## Remaining Human Gates

```yaml
remaining_human_gates:
  - license selection
  - release tag creation
  - GitHub release creation
  - package publication
  - external distribution
  - any dependency/schema/workflow change during release prep
  - any claim that v2.0 runtime-specific adapters are release blockers
```

## Release Execution Boundary

Release execution must be a separate issue.

```yaml
release_execution_boundary:
  planning_issue_may:
    - define gates
    - define checklist
    - identify blockers
    - propose release path
  planning_issue_must_not:
    - execute tag
    - publish package
    - create GitHub release
    - select license without approval
  release_execution_requires:
    - separate GitHub issue
    - explicit human approval
    - final readiness evidence
    - rollback or revoke plan
```

## Acceptance Criteria For This Planning Stage

```yaml
acceptance:
  - this plan exists and is registered
  - readiness audit points to release-preparation planning
  - roadmap points to release-preparation planning
  - current status points to release-preparation planning
  - release execution remains blocked until a separate issue exists
  - final readiness review is complete
  - python3 scripts/asgk.py doctor passes
```
