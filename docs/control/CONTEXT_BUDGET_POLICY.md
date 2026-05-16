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

The default router for deciding which document surface to inspect is
`docs/DOCUMENT_MAP.md`. Full canonical ownership rows live in
`docs/DOCUMENT_REGISTRY.md`. This policy turns those navigation surfaces into
operational read-set rules for agent sessions, task packets, reviews, merge
decisions, handoff recovery, and future CLI checks.

## Terminology Rule

Use `context read set` for this policy.

```yaml
preferred_term: context_read_set
legacy_or_informal_terms:
  - context profile
meaning: context-budget read-set only
not_meaning:
  - runtime profile
  - behavior profile
  - vendor adapter
  - platform-native subagent policy
  - goal workflow
  - platform-specific optimization layer
```

All repository work still uses the generic repo-agent governance core defined in
`AGENTS.md`. A context read set only decides which additional documents may be
read for a bounded work unit. It must not change allowed paths, merge behavior,
source-of-truth rules, or the Generic Operating Profile.

Runtime-specific profiles and adapters remain v2.0 planned/optional work and
must not be added to the v1.x default startup context.

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
    - docs/DOCUMENT_REGISTRY.md
    - docs/INSTALL_SURFACE.md
    - profiles/*
    - docs/adapters/*
```

Additional files are added only because the current work unit requires them.

## Context Read-Set Selection

Before changing files, the agent must classify the work unit into one primary
context read set. If multiple read sets apply, choose the narrowest read set that
covers the risk.

```yaml
context_read_set_selection:
  required_inputs:
    - current_issue_or_pr
    - task_type
    - allowed_paths
    - expected_output
    - risk_level
  output:
    - selected_context_read_set
    - files_to_read
    - context_expansion_reason_when_applicable
```

## Context Read Sets

These read sets are context-budget tools only. They do not define runtime or
behavior profiles.

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

### `handoff_recovery`

Use when a human, agent, model, browser session, IDE, or automation runner must
resume work after interruption or tool/runtime switch.

This read set is generic/runtime-agnostic. Runtime-specific adapters may later
optimize how a tool consumes the packet in v2.0, but they must not change this
minimum recovery set.

```yaml
handoff_recovery:
  always_read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - active GitHub issue
    - active PR if one exists
    - docs/control/HANDOFF_PACKET.md
    - docs/DOCUMENT_MAP.md
  read_from_packet:
    - must_read
    - modified_files
    - allowed_paths
  max_initial_documents: 6 plus active_issue active_pr and packet-listed files
  expansion_allowed_when:
    - handoff_packet.must_read names additional files
    - active PR changed files are outside the handoff packet modified_files list
    - validation_status is fail blocked or not_run
    - active issue and handoff packet disagree
    - next_safe_action references a specific canonical document
  stop_if:
    - active_issue_missing
    - active_issue_says_see_chat
    - next_safe_action_empty
    - validation_status_unknown
    - allowed_paths_missing
    - must_read_missing
    - handoff_packet_conflicts_with_active_pr
    - human_gate_detected_without_approval
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

Reading `.github/PULL_REQUEST_TEMPLATE.md` to prepare a governed PR body is a
context read, not a `.github/**` write. Modifying `.github/**` still triggers the
escalation rules in `AGENTS.md`.

### `control_policy`

Use for governance/control documents such as work-unit state, low-risk merge,
human gates, issue hygiene, context budget, handoff packets, or autonomous
runbooks.

```yaml
control_policy:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - docs/DOCUMENT_MAP.md
    - current GitHub issue or PR
    - target control document
    - related canonical control document named by DOCUMENT_MAP.md or DOCUMENT_REGISTRY.md
  max_initial_documents: 7
  expansion_allowed_when:
    - canonical owner is unclear
    - target document references another control document
    - change affects merge, human gates, handoff, or stop conditions
  stop_if:
    - policy conflict detected
    - human-gated operation would be expanded
    - validation behavior change is required but not scoped
```

Selecting `control_policy` is a context classification only. Changing
`docs/control/**` still requires the escalation record, stricter validation, and
human-gated handling required by `AGENTS.md`; read-set selection must not be used
to bypass those gates.

### `decision_point`

Use when a work unit reaches a major decision point that changes authority, risk,
scope, installation state, release state, external capability, or rollback
expectations.

This read set is a vertical-governance router. It must not become a reason to
read every policy document. Use `docs/control/DECISION_POINT_REGISTRY.md` to
identify the narrow canonical documents for the specific decision type.

```yaml
decision_point:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - current GitHub issue or PR
    - docs/control/DECISION_POINT_REGISTRY.md
    - templates/decision_packet.template.yaml when creating a packet
  optional_read:
    - docs/DOCUMENT_MAP.md
    - docs/DOCUMENT_REGISTRY.md
    - canonical documents named by DECISION_POINT_REGISTRY.md for the selected decision_type
  max_initial_documents: 7 plus selected canonical documents
  expansion_allowed_when:
    - selected decision type names additional canonical documents
    - authority conflict is detected
    - evidence is missing or ambiguous
    - human gate status is unclear
  stop_if:
    - decision_type_unclear
    - durable_source_of_truth_missing
    - required_evidence_missing
    - human_gate_required_but_missing
    - rollback_plan_required_but_missing
    - authority_conflict_unresolved
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
    - new_validator_dependency_required
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

## Task-type Reading Guide

Use this guide to reduce token consumption. These are task-specific read sets,
not runtime profiles.

```yaml
docs_only_task:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - current issue or PR
    - target file
    - .github/PULL_REQUEST_TEMPLATE.md

handoff_recovery_task:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - active issue
    - active PR if one exists
    - docs/control/HANDOFF_PACKET.md
    - docs/DOCUMENT_MAP.md
    - files listed in handoff_packet.must_read

closeout_or_status_repair_task:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - docs/control/CURRENT_STATUS_POLICY.md
    - current issue or PR
    - scripts/asgk.py when using `closeout-check`

install_surface_task:
  read:
    - AGENTS.md
    - docs/INSTALL_SURFACE.md
    - docs/QUICKSTART.md
    - templates/DOCUMENT_MAP.template.md
    - templates/agent_rules.template.yaml
    - docs/DOCUMENT_MAP.md

decision_point_task:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - current issue or PR
    - docs/control/DECISION_POINT_REGISTRY.md
    - templates/decision_packet.template.yaml when creating a packet

schema_or_contract_task:
  read:
    - AGENTS.md
    - docs/bootstrap/07_contract_first.md
    - relevant contract
    - relevant schema
    - relevant examples or fixtures
    - docs/control/TASK_PACKET_FORMAT.md

security_or_storage_task:
  read:
    - AGENTS.md
    - docs/bootstrap/01_physical_boundaries.md
    - docs/architecture/STORAGE_PROFILE.md
    - docs/architecture/LOG_AND_RECORD_RETENTION_POLICY.md
    - docs/control/HUMAN_GATED_OPERATIONS.md
    - relevant cache/runtime/storage policy

merge_decision_task:
  read:
    - current PR body
    - changed file list
    - docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
    - docs/control/HUMAN_GATED_OPERATIONS.md
    - docs/control/MERGE_DECISION_RECORD.md

multi_agent_or_lane_task:
  read:
    - AGENTS.md
    - docs/control/AUTONOMOUS_RUNBOOK.md
    - docs/control/LANE_STATUS.md
    - relevant agent/task_packets/*.yaml

promotion_or_output_readiness_task:
  read:
    - AGENTS.md
    - docs/bootstrap/13_artifact_promotion_policy.md
    - docs/bootstrap/16_downstream_promotion_matrix.md
    - docs/bootstrap/17_readiness_audit_policy.md
    - relevant promotion/validation schemas

historical_readiness_evidence_task:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - docs/control/HISTORICAL_ASGK_READINESS_EVIDENCE.md
    - docs/EVOLUTION_MODEL.md
    - docs/DOCUMENT_MAP.md

historical_stabilization_evidence_task:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - docs/control/HISTORICAL_ASGK_STABILIZATION_EVIDENCE.md
    - docs/control/HISTORICAL_ASGK_READINESS_EVIDENCE.md
    - docs/DOCUMENT_MAP.md

tooling_or_validation_task:
  read:
    - AGENTS.md
    - current issue or PR
    - target script or workflow file
    - docs/control/VALIDATION_STRATEGY.md
    - relevant examples/negative fixture if named by the issue
```

## Context Expansion Rules

Agents may expand context only when one of these is true:

```yaml
context_expansion_allowed_when:
  - target file references another canonical file
  - DOCUMENT_MAP.md routes to a relevant canonical source
  - DOCUMENT_REGISTRY.md says the related file is canonical for the current topic
  - DECISION_POINT_REGISTRY.md names canonical documents for the selected decision_type
  - validation failure points to a specific file
  - PR diff touches a file outside the expected group
  - issue acceptance criteria name an additional file
  - handoff packet must_read names an additional file
  - conflict exists between current issue PR body handoff packet and repository file
  - human or reviewer explicitly asks for a broader audit
```

Expansion must be recorded in the agent report:

```yaml
context_expansion_record:
  original_read_set:
  added_files:
  reason:
  result:
```

## Context Expansion Limits

```yaml
hard_limits:
  max_unrelated_files: 0
  max_documents_without_reason: 0
  max_initial_documents_without_read_set: 4
  max_full_repository_scans: 0
```

Full repository scans are not allowed as normal context gathering. Use targeted
search, file lists, handoff packet fields, or scripts instead.

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
  - runtime-specific adapters before v2.0
  - docs/DOCUMENT_REGISTRY.md
  - docs/INSTALL_SURFACE.md
```

## Required Report Section

Every PR or Agent Report should include a compact context section when the work
is non-trivial. This section belongs in the existing PR or Agent Report; do not
create a separate context protocol, context pack, or sidecar context artifact.

```md
## Context Budget

Context read set: <read-set-name>
Initial files read:
- <path>
Expanded files read:
- <path or none>
Expansion reason:
- <reason or none>
Estimated repo-context tokens: <integer or not_measured>
Measurement source: <command, fixture, or not_measured>
Actual model tokens: <integer or unavailable>
Actual model token source: <client_usage_log, provider_usage, or not_provided>
Files intentionally not read:
- <category or path>
```

Estimated repo-context tokens are a local, dependency-free approximation of repo
file text named by the work unit. They are not provider billing tokens and do not
include GitHub issue text, system/developer prompts, chat history, tool output,
retrieved web/app content, or model completion tokens. Record actual model token
usage only when a client or provider usage log is explicitly available.

For handoff recovery, include the handoff packet source and the next safe action.

## Token-Saving Rules

1. Prefer task packets, issue bodies, handoff packets, and current-status
   documents over full conversation history.
2. Prefer canonical documents over summaries.
3. Prefer changed-file lists and validator output over reading unrelated docs.
4. Prefer scripts for mechanical checks.
5. Do not ask the AI to remember policy when a validator or template can enforce
   it.
6. When a policy is stable, move it from prompt text into a document, schema, or
   script.

## Relationship To Document Navigation

`docs/DOCUMENT_MAP.md` routes document-navigation decisions.
`docs/DOCUMENT_REGISTRY.md` defines full canonical ownership rows.
This policy defines how to consume those surfaces under a context budget.

If the document map, document registry, and this policy disagree:

1. Stop the task.
2. Open or update a docs/control issue.
3. Do not silently choose the larger context set.

## Future CLI Mapping

The CLI wrapper may expose this policy through commands such as:

```bash
python3 scripts/asgk.py doctor
python3 scripts/asgk.py validate
python3 scripts/asgk.py hygiene --paths-file changed-paths.txt
python3 scripts/asgk.py handoff-check --file handoff.yaml
```

Runtime-specific profile/adapters are v2.0 optimization work and should not
alter the v1.x generic handoff recovery minimum set.
