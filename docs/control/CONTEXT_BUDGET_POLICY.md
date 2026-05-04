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
agent sessions, task packets, reviews, merge decisions, handoff recovery, and
future CLI checks.

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
    - related canonical control document named by DOCUMENT_MAP.md
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

## Context Expansion Rules

Agents may expand context only when one of these is true:

```yaml
context_expansion_allowed_when:
  - target file references another canonical file
  - DOCUMENT_MAP.md says the related file is canonical for the current topic
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
```

## Required Report Section

Every PR or Agent Report should include a compact context section when the work
is non-trivial:

```md
## Context Budget

Context read set: <read-set-name>
Initial files read:
- <path>
Expanded files read:
- <path or none>
Expansion reason:
- <reason or none>
Files intentionally not read:
- <category or path>
```

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

## Relationship To DOCUMENT_MAP.md

`docs/DOCUMENT_MAP.md` defines document ownership. This policy defines how to
consume that ownership under a context budget.

If the document map and this policy disagree:

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
