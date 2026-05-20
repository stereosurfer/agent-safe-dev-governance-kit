# Source-Only Release Policy

Status: active source-only release policy.

This document defines ASGK v1.x source-only release gates, release-execution
boundaries, closeout requirements, and v2.0 deferrals. The version scope is an
applicability boundary, not a file naming convention to copy into target repos.
It is not a release history ledger and does not execute tags, GitHub releases,
packages, installers, or repository visibility changes.

## Scope

```yaml
source_only_release_policy_scope:
  applicability:
    - ASGK v1.x source-only releases
  allowed_in_this_policy:
    - final readiness review checklist
    - license-selection decision path
    - tag and release process plan
    - package or distribution boundary
    - explicit v2.0 deferrals
    - remaining human gates
  not_allowed_in_this_policy:
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
  initial_source_only_release_policy:
    status: completed
    source: "#116 / PR #117"
  current_status_closeout:
    status: completed
    source: "#118 / PR #119"
  final_readiness_review:
    status: completed
    source: "#120 / PR #121"
```

## Source-Only Release Gates

```yaml
source_only_release_gates:
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

## Tag And Release Process Policy

This policy may describe release process requirements. It must not execute them.

```yaml
tag_release_process:
  planned_steps:
    - create human-gated release-execution issue
    - confirm final readiness review
    - confirm Apache-2.0 license decision
    - run python3 scripts/asgk.py doctor
    - check git status and target commit
    - create tag only in release-execution issue
    - create GitHub release only if explicitly approved
    - refresh docs/handoff/CURRENT_STATUS.md in the same authorized PR or create an immediate status-only closeout issue/PR only when current release recovery state would otherwise be unsafe
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
    - these are not v1.x source-only release blockers unless a human-gated release issue explicitly changes scope
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
    - "If release execution is metadata-only and current release recovery state would otherwise be unsafe, create an immediate bounded status-refresh issue/PR."
    - "If release execution authorizes file changes, update docs/handoff/CURRENT_STATUS.md only when the result is post-merge-safe."
    - "Record the status-refresh issue, PR, or completed status update in the release execution closeout comment."
  product_entry_closeout_requires:
    - "README.md must identify the released version as the latest completed source-only GitHub release."
    - "docs/bootstrap/10_roadmap.md must not describe the released version as an active candidate or pending release execution."
    - "Run `python3 scripts/asgk.py release-state-check --tag <tag> --release-title \"<title>\"` after release-state docs are updated."
    - "If product-entry docs required for the current release are intentionally deferred, record the bounded follow-up issue before claiming release closeout is complete."
    - "Before v1.3 or later release execution begins, the release issue must name the exact product-entry and handoff docs that will be synchronized and the target `release-state-check` command."
    - "Use `skills/asgk-release-prep/SKILL.md` when planning, executing, or closing out source-only releases."
  release_execution_not_fully_closed_until:
    - "tag and GitHub release are complete"
    - "final validation evidence is recorded"
    - "CURRENT_STATUS.md is post-release accurate or a bounded status-refresh issue exists"
    - "product-entry release-state docs are accurate or a bounded product-entry follow-up issue exists"
```

## Release Evidence Boundary

Detailed release execution history is not duplicated in this repository
policy. The canonical historical evidence for each completed release lives in
GitHub releases, release issues, pull requests, Merge Decision Records, issue
closeout comments, tags, and merge commits.

This file keeps only the durable release rules and closeout requirements needed
for future source-only releases.

Release closeout follow-up issues are for current release state. Apply
`docs/control/ISSUE_HYGIENE_GATE.md` before turning observations into work.

```yaml
release_history_boundary:
  repo_documents_keep:
    - current latest release identity
    - source-only release gates
    - release execution boundary
    - product-entry and handoff freshness requirements
    - human-gated operations
    - explicit v2.0 deferrals
  github_keeps:
    - per-release target commits
    - full release notes
    - final validation evidence
    - rollback or revoke plans
    - release execution comments
    - pull request Merge Decision Records
    - issue closeout comments
  forbidden_repo_ledger_patterns:
    - one block per historical release execution
    - repeated target-commit lists for completed releases
    - repeated per-release validation transcripts
    - repeated release URL ledgers already present in GitHub
```

## Current Release Reference

```yaml
current_release_reference:
  latest_completed_release: "ASGK v1.7.2"
  latest_completed_tag: v1.7.2
  release_issue: "#317"
  release_url: https://github.com/stereosurfer/agent-safe-dev-governance-kit/releases/tag/v1.7.2
  source_of_truth_for_history: "GitHub releases, release issues, PRs, MDRs, comments, tags, and merge commits"
  validation_for_freshness:
    - python3 scripts/asgk.py release-state-check --tag v1.7.2 --release-title "ASGK v1.7.2"
    - python3 scripts/asgk.py doctor
```

## Acceptance Criteria

```yaml
acceptance:
  - Apache-2.0 license decision is recorded
  - LICENSE exists
  - source-only GitHub release path is recorded
  - release execution completed only after separate issue approval
  - detailed release history remains canonical in GitHub evidence, not repo-local ledgers
  - python3 scripts/asgk.py doctor passes
```
