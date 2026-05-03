# Context Budget Policy

Status: active control policy.

This policy defines how much repository context an AI agent should read for a
work unit. It exists to reduce token use, prevent context overload, and stop AI
agents from flattening multiple documents into an inaccurate summary.

## Core Rule

```text
Use the smallest sufficient context set.
Do not read the whole repository by default.
```

The default source for deciding which documents to read is
`docs/DOCUMENT_MAP.md`. This policy turns that map into operational rules for
agent sessions, task packets, reviews, merge decisions, and future CLI checks.

## Why This Policy Exists

Large context does not automatically improve agent quality. It can create four
specific failures:

1. The agent spends tokens on irrelevant material.
2. The agent merges similar but distinct rules into one simplified rule.
3. The agent treats summary documents as competing authority against canonical
   documents.
4. The agent misses the active issue or PR because repository history dominates
   the prompt.

This policy makes context expansion explicit and reportable.

## Default Startup Context

Every new agent session starts with this minimal set:

```yaml
default_startup_context:
  always_read:
    - AGENTS.md
    - README.md
    - docs/handoff/CURRENT_STATUS.md
    - current GitHub issue or PR
  do_not_read_by_default:
    - all docs/bootstrap/*
    - all docs/control/*
    - all docs/architecture/*
    - all schemas/*
    - all contracts/*
    - all examples/*
    - all agent/task_packets/*
```

Additional files are added only because the current work unit requires them.

## Context Profile Selection

Before changing files, the agent must classify the work unit into one primary
context profile. If multiple profiles apply, choose the narrowest profile that
covers the risk.

```yaml
context_profile_selection:
  required_inputs:
    - current_issue_or_pr
    - task_type
    - allowed_paths
    - expected_output
    - risk_level
  output:
    - selected_context_profile
    - files_to_read
    - context_expansion_reason_when_applicable
```

## Context Profiles

### `startup`

Use when orienting a new session without making changes.

```yaml
startup:
  read:
    - AGENTS.md
    - README.md
    - docs/handoff/CURRENT_STATUS.md
    - open PRs or current issue when relevant
  max_initial_documents: 4
  expansion_allowed_when:
    - current status points to a specific control document
    - active issue names a specific file
```

### `docs_only`

Use for bounded documentation changes that do not alter policy semantics,
validation behavior, schemas, dependencies, or workflows.

```yaml
docs_only:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - current GitHub issue or PR
    - target file
    - .github/PULL_REQUEST_TEMPLATE.md
  optional_read:
    - docs/DOCUMENT_MAP.md
  max_initial_documents: 6
  stop_if:
    - required_change_outside_allowed_paths
    - policy_semantics_change_detected
    - validation_script_change_required
```

### `control_policy`

Use for governance/control documents such as work-unit state, low-risk merge,
human gates, issue hygiene, context budget, or autonomous runbooks.

```yaml
control_policy:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - docs/DOCUMENT_MAP.md
    - current GitHub issue or PR
    - target control document
    - related canonical control document named by DOCUMENT_MAP.md
  max_initial_documents: 7
  expansion_allowed_when:
    - canonical owner is unclear
    - target document references another control document
    - change affects merge, human gates, or stop conditions
  stop_if:
    - policy conflict detected
    - human-gated operation would be expanded
    - validation behavior change is required but not scoped
```

### `schema_or_contract`

Use for schema, contract, fixture, or validation-structure work.

```yaml
schema_or_contract:
  read:
    - AGENTS.md
    - docs/bootstrap/07_contract_first.md
    - current GitHub issue or PR
    - relevant contract
    - relevant schema
    - relevant examples or fixtures
    - docs/control/TASK_PACKET_FORMAT.md when task packets are involved
  max_initial_documents: 8
  expansion_allowed_when:
    - contract and schema disagree
    - example fails schema expectations
    - validator behavior is explicitly in scope
  stop_if:
    - schema_breaking_change_required
    - new validator dependency_required
    - contract_semantics_unclear
```

### `security_or_storage`

Use for filesystem, protected-path, Artifact Root, Local State Root, cache,
workspace lock, private material, or externalized responsibility boundaries.

```yaml
security_or_storage:
  read:
    - AGENTS.md
    - docs/bootstrap/01_physical_boundaries.md
    - docs/architecture/STORAGE_PROFILE.md
    - docs/architecture/RUNTIME_ARTIFACT_POLICY.md
    - docs/control/HUMAN_GATED_OPERATIONS.md
    - current GitHub issue or PR
  optional_read:
    - docs/architecture/CACHE_AND_STATE_POLICY.md
    - docs/architecture/WORKSPACE_LOCK_POLICY.md
    - docs/architecture/EXTERNALIZED_RESPONSIBILITY_BOUNDARY.md
  max_initial_documents: 8
  stop_if:
    - broader_filesystem_permission_required
    - protected_path_change_required
    - cloud_or_external_api_gate_required
    - private_source_material_required
```

### `merge_decision`

Use before marking a PR ready, approving low-risk merge, or merging.

```yaml
merge_decision:
  read:
    - current PR body
    - changed file list
    - current GitHub issue
    - docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
    - docs/control/HUMAN_GATED_OPERATIONS.md
    - docs/control/MERGE_DECISION_RECORD.md
  optional_read:
    - docs/DOCUMENT_MAP.md
    - target files changed by the PR
  max_initial_documents: 6 plus changed-file list
  stop_if:
    - required_checks_missing_or_unknown
    - merge_decision_record_missing
    - human_gate_detected
    - changed_files_outside_allowed_paths
    - unresolved_review_comments
```

### `multi_agent_or_lane`

Use for controller/worker coordination, lane packets, autonomous batches, or
parallel work.

```yaml
multi_agent_or_lane:
  read:
    - AGENTS.md
    - docs/control/AUTONOMOUS_RUNBOOK.md
    - docs/control/LANE_STATUS.md
    - current GitHub issue or PR
    - relevant agent/task_packets/*.yaml
  optional_read:
    - docs/control/FAILURE_THRESHOLDS.md
    - docs/control/WORK_UNIT_STATE_MODEL.md
  max_initial_documents: 8
  stop_if:
    - lane_write_scope_overlap
    - durable_packet_missing
    - failure_threshold_reached
    - controller_state_unclear
```

### `promotion_or_output_readiness`

Use for artifact promotion, source/input class boundaries, downstream output,
external calls, import/export, provider/model calls, or publication readiness.

```yaml
promotion_or_output_readiness:
  read:
    - AGENTS.md
    - docs/bootstrap/13_artifact_promotion_policy.md
    - docs/bootstrap/15_source_or_input_class_matrix.md
    - docs/bootstrap/16_downstream_promotion_matrix.md
    - docs/bootstrap/17_readiness_audit_policy.md
    - current GitHub issue or PR
  optional_read:
    - contracts/promotion_gate.contract.yaml
    - schemas/promotion_gate.schema.json
    - schemas/execution_lane.schema.json
  max_initial_documents: 9
  stop_if:
    - output_uses_unpromoted_artifact
    - deterministic_fallback_presented_as_production_success
    - live_external_call_without_explicit_gate
    - publication_or_release_gate_required
```

### `tooling_or_validation`

Use for validation scripts, path hygiene, CI workflow, future CLI wrapper, or
script behavior.

```yaml
tooling_or_validation:
  read:
    - AGENTS.md
    - docs/control/VALIDATION_STRATEGY.md if it exists
    - current GitHub issue or PR
    - target script or workflow file
    - relevant examples or negative fixtures named by the issue
  optional_read:
    - docs/DOCUMENT_MAP.md
    - scripts/check_project.py
    - scripts/validate_bootstrap.py
    - scripts/governance_hygiene.py
  max_initial_documents: 8
  stop_if:
    - new_dependency_required
    - CI_permissions_expand
    - validator_scope_changes_without_issue_authorization
```

If `docs/control/VALIDATION_STRATEGY.md` does not yet exist, use the current
issue as the durable scope and keep changes narrow.

## Context Expansion Rules

Agents may expand context only when one of these is true:

```yaml
context_expansion_allowed_when:
  - target file references another canonical file
  - DOCUMENT_MAP.md says the related file is canonical for the current topic
  - validation failure points to a specific file
  - PR diff touches a file outside the expected group
  - issue acceptance criteria name an additional file
  - conflict exists between current issue, PR body, and repository file
  - human or reviewer explicitly asks for a broader audit
```

Expansion must be recorded in the agent report:

```yaml
context_expansion_record:
  original_profile:
  added_files:
  reason:
  result:
```

## Context Expansion Limits

```yaml
hard_limits:
  max_unrelated_files: 0
  max_documents_without_reason: 0
  max_initial_documents_without_profile: 4
  max_full_repository_scans: 0
```

Full repository scans are not allowed as normal context gathering. Use targeted
search, file lists, or scripts instead.

## What Not To Load

Do not load these unless they are the direct target of the issue:

```yaml
do_not_load_by_default:
  - every schema file
  - every contract file
  - every bootstrap document
  - every control document
  - every example
  - generated artifacts
  - runtime outputs
  - private source files
  - cache directories
  - local state directories
```

## Required Report Section

Every PR or Agent Report should include a compact context section when the work
is non-trivial:

```md
## Context Budget

Profile: <profile>
Initial files read:
- <path>
Expanded files read:
- <path or none>
Expansion reason:
- <reason or none>
Files intentionally not read:
- <category or path>
```

For low-risk docs-only work, this section may be included in the Handoff Report
instead of a top-level PR section.

## Token-Saving Rules

1. Prefer task packets, issue bodies, and current-status documents over full
   conversation history.
2. Prefer canonical documents over summaries.
3. Prefer changed-file lists and validator output over reading unrelated docs.
4. Prefer scripts for mechanical checks.
5. Do not ask the AI to remember policy when a validator or template can enforce
   it.
6. When a policy is stable, move it from prompt text into a document, schema, or
   script.

## Relationship To DOCUMENT_MAP.md

`docs/DOCUMENT_MAP.md` defines document ownership. This policy defines how to
consume that ownership under a context budget.

If the document map and this policy disagree:

1. Stop the task.
2. Open or update a docs/control issue.
3. Do not silently choose the larger context set.

## Future CLI Mapping

A future CLI wrapper may expose this policy as commands such as:

```bash
asgk context docs-only
asgk context merge-decision --pr 12
asgk doctor
asgk validate
```

Until then, agents should apply this policy manually and record context expansion
in PRs or Agent Reports.
