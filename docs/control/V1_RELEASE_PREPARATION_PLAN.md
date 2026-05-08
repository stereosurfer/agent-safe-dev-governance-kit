# V1 Release Preparation Plan

Status: completed planning and release-execution record.

This document plans ASGK v1.0 release preparation after v1.1 stabilization,
Vertical Governance Completion, and the first real-world field test have
completed.

It began as a planning document only. It records the approved v1.0 license,
source-only release path, and the later human-gated source-only GitHub release
execution completed under issue #130.

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
    status: completed_by_130
    output: "v1.0.0 tag and source-only GitHub release created after explicit human approval"
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
    status: completed_by_130
    output: "issue #130 approved and executed source-only GitHub release v1.0.0"
```

## License Decision

```yaml
license_decision:
  issue: "#124"
  approved_by: human_operator
  selected_license: Apache-2.0
  license_file: LICENSE
  license_file_status: full_apache_2_0_text
  official_license_url: https://www.apache.org/licenses/LICENSE-2.0
  note: "The top-level LICENSE file contains the complete Apache License 2.0 text."
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
    - refresh docs/handoff/CURRENT_STATUS.md in the same authorized PR or create an immediate status-only closeout issue/PR
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
    - post-release CURRENT_STATUS closeout path
  status_closeout_requires:
    - "If release execution is metadata-only, create an immediate bounded status-refresh issue/PR."
    - "If release execution authorizes file changes, update docs/handoff/CURRENT_STATUS.md only when the result is post-merge-safe."
    - "Record the status-refresh issue, PR, or completed status update in the release execution closeout comment."
  product_entry_closeout_requires:
    - "README.md must identify the released version as the latest completed source-only GitHub release."
    - "docs/bootstrap/10_roadmap.md must not describe the released version as an active candidate or pending release execution."
    - "Run `python3 scripts/asgk.py release-state-check --tag <tag> --release-title \"<title>\"` after release-state docs are updated."
    - "If product-entry docs are intentionally deferred, record the bounded follow-up issue before claiming release closeout is complete."
    - "Before v1.3 or later release execution begins, the release issue must name the exact product-entry and handoff docs that will be synchronized and the target `release-state-check` command."
    - "Use `skills/asgk-release-prep/SKILL.md` when planning, executing, or closing out source-only releases."
  release_execution_not_fully_closed_until:
    - "tag and GitHub release are complete"
    - "final validation evidence is recorded"
    - "CURRENT_STATUS.md is post-release accurate or a bounded status-refresh issue exists"
    - "product-entry release-state docs are accurate or a bounded product-entry follow-up issue exists"
```

## Release Execution Result

```yaml
release_execution_result:
  issue: "#130"
  status: completed
  target_commit: "7d2e364c4c53d1296c7ce1c2d241291837d54c61"
  tag_name: v1.0.0
  release_title: "ASGK v1.0.0"
  release_url: https://github.com/stereosurfer/agent-safe-dev-governance-kit/releases/tag/v1.0.0
  release_type: source_only_github_release
  validation:
    command: python3 scripts/asgk.py doctor
    result: passed
  completed_at: "2026-05-05T05:12:52Z"
  not_performed:
    - package publication
    - runtime-specific adapter work
    - installer scaffold
    - dependency changes
    - schema or workflow changes
    - external distribution beyond GitHub source release
  status_closeout:
    v1_0_followup: "Issue #130 was followed by a separate current-status closeout path."
    rule_after_v1_1: "Future release execution must record a same-PR status update or immediate status-refresh issue/PR before claiming full closeout."
    rule_after_v1_2: "Future release execution must also verify product-entry release-state docs with release-state-check or record a bounded follow-up before claiming full closeout."
    rule_before_v1_3: "Future release execution issues must include the product-entry/handoff document synchronization plan before tag or GitHub release execution is attempted."
```

## v1.3 Release Preparation Record

```yaml
v1_3_release_preparation:
  issue: "#186"
  status: executed_by_188
  latest_completed_release: "ASGK v1.3.0"
  release_title: "ASGK v1.3.0"
  release_theme: "Operational burden reduction for governed agent workflows."
  released_scope:
    - "current-status default and post-merge closeout guidance hardening to reduce unnecessary handoff churn"
    - "ASGK upgrade-audit skill to reduce target-upgrade ambiguity"
    - "work-unit preflight validation to reduce stale or wrong-authority work"
    - "v1.2.1 release-state alignment to reduce post-release documentation drift"
    - "release-prep and release-execution skill guidance to reduce release sequencing mistakes"
  execution_record:
    issue: "#188"
    target_commit: "afe0f3c47040fc271bdbef9ec1e6a5055e8be30d"
    tag_name: v1.3.0
    release_url: https://github.com/stereosurfer/agent-safe-dev-governance-kit/releases/tag/v1.3.0
    release_type: source_only_github_release
    validation:
      command: python3 scripts/asgk.py doctor
      result: passed_before_release
    closeout:
      product_entry_and_handoff_docs:
        - README.md
        - docs/bootstrap/10_roadmap.md
        - docs/handoff/CURRENT_STATUS.md
        - docs/control/V1_RELEASE_PREPARATION_PLAN.md
      required_validation:
        - python3 scripts/asgk.py release-state-check --tag v1.3.0 --release-title "ASGK v1.3.0"
        - python3 scripts/asgk.py doctor
  not_performed:
    - package publication
    - repository visibility change
    - runtime adapter, installer scaffold, dependency, workflow, schema, or v2.0 work
```

## v1.4 Release Preparation Record

```yaml
v1_4_release_preparation:
  issue: "#194"
  status: executed_by_194
  latest_completed_release: "ASGK v1.4.0"
  release_title: "ASGK v1.4.0"
  release_theme: "Governance-preflight hardening for governed agent workflows."
  released_scope:
    - "PR body governance preflight wrapper path to catch missing PR sections before GitHub Actions"
    - "check-pr changed-file comparison against closing issue allowed_paths"
    - "target adoption dependency alignment for policy_gate_check.py"
    - "bootstrap validation workflow action refresh and explicit read-only permissions"
    - "release-roadmap stale baseline cleanup before release execution"
  execution_record:
    issue: "#194"
    target_commit: "ac39c4da8044560398730fb2a4d811656f79a239"
    tag_name: v1.4.0
    release_url: https://github.com/stereosurfer/agent-safe-dev-governance-kit/releases/tag/v1.4.0
    release_type: source_only_github_release
    validation:
      command: python3 scripts/asgk.py doctor
      result: passed_before_release
    closeout:
      product_entry_and_handoff_docs:
        - README.md
        - docs/bootstrap/10_roadmap.md
        - docs/handoff/CURRENT_STATUS.md
        - docs/control/V1_RELEASE_PREPARATION_PLAN.md
      required_validation:
        - python3 scripts/asgk.py release-state-check --tag v1.4.0 --release-title "ASGK v1.4.0"
        - python3 scripts/asgk.py doctor
  not_performed:
    - package publication
    - repository visibility change
    - runtime adapter, installer scaffold, dependency, schema, or v2.0 work
```

## v1.5 Release Candidate Preparation Record

```yaml
v1_5_release_candidate_preparation:
  issue: "#209"
  status: prepared_not_executed
  latest_completed_release_remains: "ASGK v1.4.0"
  candidate_tag: v1.5.0
  candidate_release_title: "ASGK v1.5.0"
  candidate_theme: "Context-boundary and closeout-learning hardening for governed agent workflows."
  candidate_scope:
    - "context read gate hardening through files_to_inspect_first validation"
    - "repo-context token measurement through context-budget-measure"
    - "work-unit required task-field completeness before changed paths can authorize work"
    - "chat output hygiene so routine governance mechanics stay out of chat"
    - "centralized advisory Issue Closeout Review ledger for reusable decisions and pitfalls"
  preparation_scope:
    - "fix Chat Output Hygiene gap in AGENTS.md"
    - "clarify Issue Closeout Review self-bootstrap/no-ledger-update behavior"
    - "record v1.5 candidate release framing without claiming release completion"
  release_execution_required:
    durable_issue: "new or updated release execution issue with explicit human approval"
    exact_tag: v1.5.0
    exact_release_title: "ASGK v1.5.0"
    exact_target_commit: "current main after the release-prep PR merges"
    release_type: source_only_github_release
    final_validation:
      - python3 scripts/asgk.py doctor
    post_release_closeout_docs:
      - README.md
      - docs/bootstrap/10_roadmap.md
      - docs/handoff/CURRENT_STATUS.md
      - docs/control/V1_RELEASE_PREPARATION_PLAN.md
    post_release_validation:
      - python3 scripts/asgk.py release-state-check --tag v1.5.0 --release-title "ASGK v1.5.0"
      - python3 scripts/asgk.py doctor
    rollback_or_revoke_plan_required: true
  not_authorized_by_this_preparation:
    - tag creation
    - GitHub release creation
    - package publication
    - repository visibility change
    - runtime adapter, installer scaffold, dependency, workflow, schema, or v2.0 work
```

## Acceptance Criteria For This Planning Stage

```yaml
acceptance:
  - Apache-2.0 license decision is recorded
  - LICENSE exists
  - source-only GitHub release path is recorded
  - release execution completed only after separate issue approval
  - python3 scripts/asgk.py doctor passes
```
