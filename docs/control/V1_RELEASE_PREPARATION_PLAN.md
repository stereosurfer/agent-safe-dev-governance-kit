# V1 Release Preparation Plan

Status: active planning document.

This document plans ASGK v1.0 release preparation after v1.1 stabilization,
Vertical Governance Completion, and the first real-world field test have
completed.

It is a planning document only. It records the approved v1.0 license and
source-only release path, but it does not tag a release, publish a package,
create a GitHub release, or start release execution.

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
  final_readiness_review:
    status: completed
    source: "#120 / PR #121"
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
    status: selected_by_124
    output: Apache-2.0
  tag_release_process:
    required: true
    human_gate: true
    status: not_started
    output: "documented process for release tag and GitHub release, but no tag created here"
  package_distribution_boundary:
    required: true
    human_gate: true
    status: selected_by_124
    output: source_only_github_release
  v2_0_deferrals:
    required: true
    human_gate: maybe
    status: explicit
    output: "runtime-specific adapters and productization items deferred to v2.0"
  release_execution_issue:
    required: true
    human_gate: true
    status: not_created
    output: "separate issue if release execution is approved"
```

## License Decision

```yaml
license_decision:
  issue: "#124"
  approved_by: human_operator
  selected_license: Apache-2.0
  license_file: LICENSE
  license_file_status: created_with_spdx_identifier_and_official_license_url
  official_license_url: https://www.apache.org/licenses/LICENSE-2.0
  note: "The top-level LICENSE file uses the SPDX identifier and official Apache License 2.0 URL. If full-text license auto-detection is required, add the complete standard Apache-2.0 text in a later bounded issue."
```

## Distribution Path Decision

```yaml
distribution_path_decision:
  issue: "#124"
  approved_by: human_operator
  selected_path: source_only_github_release
  package_publication: not_selected
  github_app_or_saas: deferred_v2_or_later
  installer_scaffold: deferred
  note: "v1.0 release path should remain source-only unless a later human-gated issue approves broader distribution."
```

## Final Readiness Review Result

```yaml
final_readiness_review_result:
  issue: "#120"
  status: ready_to_propose_release_execution
  blockers:
    v1_0_core_blockers: []
    sequence_blockers: []
  recommendation: "Create a separate human-gated release-execution issue."
  not_authorized:
    - release tag creation
    - GitHub release creation
    - package publication
    - external distribution
```

## Tag And Release Process Plan

This planning document may describe a future process. It must not execute it.

```yaml
tag_release_process:
  planned_steps:
    - create release-execution issue
    - confirm final readiness review
    - confirm Apache-2.0 license decision
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
  selected_for_v1: source_only_github_release
  not_selected_for_v1:
    - package manager publication
    - GitHub App
    - SaaS
    - installer script
  allowed_later_only_with_human_gate:
    - downloadable archive beyond GitHub default source archives
    - package manager publication
    - external distribution beyond GitHub source release
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
  - release tag creation
  - GitHub release creation
  - package publication
  - external distribution
  - any dependency/schema/workflow change during release execution
  - any claim that v2.0 runtime-specific adapters are release blockers
```

## Release Execution Boundary

Release execution must be a separate issue.

```yaml
release_execution_boundary:
  license_status: selected_apache_2_0
  distribution_status: selected_source_only_github_release
  planning_issue_may:
    - define gates
    - define checklist
    - identify blockers
    - propose release path
  planning_issue_must_not:
    - execute tag
    - publish package
    - create GitHub release
  release_execution_requires:
    - separate GitHub issue
    - explicit human approval
    - final readiness evidence
    - rollback or revoke plan
```

## Acceptance Criteria For This Planning Stage

```yaml
acceptance:
  - Apache-2.0 license decision is recorded
  - LICENSE exists
  - source-only GitHub release path is recorded
  - release execution remains blocked until a separate issue exists
  - python3 scripts/asgk.py doctor passes
```
