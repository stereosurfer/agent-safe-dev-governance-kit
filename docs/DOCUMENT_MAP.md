# Document Map

Status: active ASGK repository-local navigation router and transitional registry surface.

This file defines which documents are canonical, which documents are summaries,
which documents are examples, which files are executable governance surfaces,
and which files should be read only for specific task types.

Its main purpose is to reduce token use, prevent document role drift, and stop
agents from treating repeated summaries as competing authority.

## Repo-local Scope

```text
DOCUMENT_MAP.md is repo-local.
```

This file governs the ASGK repository only. It is not the document map to copy
unchanged into repositories that install or adopt ASGK.

When ASGK is installed into a target repository, that target repository must own
its own `docs/DOCUMENT_MAP.md` based on its actual files. Use
`templates/DOCUMENT_MAP.template.md` as a starter template, then keep the target
map as a compact router. Use `templates/DOCUMENT_REGISTRY.template.md` to create
the target repository's full registry.

The document-navigation split is:

```yaml
asgk_repo_local_router: docs/DOCUMENT_MAP.md
asgk_repo_local_registry: docs/DOCUMENT_REGISTRY.md
target_project_router_template: templates/DOCUMENT_MAP.template.md
target_project_registry_template: templates/DOCUMENT_REGISTRY.template.md
target_repo_local_router: docs/DOCUMENT_MAP.md in the target repository
target_repo_local_registry: docs/DOCUMENT_REGISTRY.md in the target repository
```

Migration note: this file still contains full registry tables until the bounded
registry-migration work unit moves them to `docs/DOCUMENT_REGISTRY.md`.

## Core Rule

```text
Do not read the whole repository for every task.
Read the smallest set of canonical documents required by the work unit.
```

If two documents appear to disagree, prefer the document marked `canonical` for
that topic. If a summary document disagrees with a canonical document, the
summary document is stale and should be fixed in a separate issue.

## Progressive Disclosure Surfaces

```yaml
progressive_disclosure_surfaces:
  router:
    path: docs/DOCUMENT_MAP.md
    purpose: compact repo-local navigation router
  registry:
    path: docs/DOCUMENT_REGISTRY.md
    purpose: complete repo-local document registry after migration
  policy:
    path: docs/control/DOCUMENT_MAP_POLICY.md
    purpose: document-map size limits, split ownership, and maintenance rules
  read_sets:
    path: docs/control/CONTEXT_BUDGET_POLICY.md
    purpose: context read sets and task-specific reading guide
  install_surface:
    path: docs/INSTALL_SURFACE.md
    purpose: target-project copy/template/customize/do-not-copy boundary
```

## Default Startup Set

Every new agent session should start with only this minimal set unless the
current issue, PR, or handoff packet points elsewhere:

```yaml
default_startup_set:
  - AGENTS.md
  - README.md
  - docs/handoff/CURRENT_STATUS.md
  - current GitHub issue or PR
```

Additional documents should be pulled by task type, not by habit.

## Profile And Adapter Boundary

ASGK v1.x uses a generic repo-agent governance core. Runtime-specific profile or
adapter documents for Codex, ChatGPT Web/GitHub connector, OpenGoat, Claude Code,
Cursor, Copilot, or other runtimes are v2.0 planned/optional work and are not
part of the current default startup set.

```yaml
profile_boundary:
  v1_x:
    current_profile: generic_repo_agent
    current_adapter_mode: generic_handoff_and_validation
    read_by_default: false
    purpose: runtime-agnostic governance core
  v2_0:
    planned_profiles_or_adapters:
      - codex-app
      - chatgpt-web-github-connector
      - opengoat
      - claude-code
      - cursor
      - copilot
    rule:
      - profiles and adapters are optimization layers
      - profiles and adapters must not bypass core governance
      - runtime-specific content requires vendor docs and observed tests
```

## Document Roles

```yaml
roles:
  canonical: Primary source of truth for a topic.
  summary: Short orientation document that points to canonical sources.
  example: Non-authoritative sample for humans and agents.
  schema: Machine-readable structure contract.
  contract: Semantic rules and invariants.
  template: Reusable starting point for work units or GitHub surfaces.
  status: Current handoff or state surface.
  script: Executable validation or hygiene behavior.
  future_optional: Planned future capability, not part of current v1.x core.
```

## Entry And Startup Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `README.md` | summary | project positioning, install path, operating loop overview | yes | all new sessions | `lane_07_docs_handoff` |
| `AGENTS.md` | canonical | agent startup order, source-of-truth rule, work-unit rule, stop conditions | yes | all agent sessions | `lane_00_controller` |
| `docs/handoff/CURRENT_STATUS.md` | status | compact current repo snapshot and next safe work | yes | all new sessions, handoff recovery, handoff updates | `lane_07_docs_handoff` |
| current GitHub issue or PR | canonical | active task objective, allowed paths, acceptance, validation, merge state | yes | every work unit | active task lane |
| `docs/QUICKSTART.md` | summary | first-use workflow, onboarding, and target-repo install-surface orientation | no | onboarding and first repository smoke test | `lane_07_docs_handoff` |
| `docs/INSTALL_SURFACE.md` | canonical | target-project install surface, copy/template/customize/do-not-copy boundaries | no | installing ASGK into another repository, field-test preparation, target-repo scaffold planning | `lane_07_docs_handoff` |
| `docs/DOCUMENT_REGISTRY.md` | canonical | complete repo-local document registry after migration | no | canonical ownership lookup, registry repair, document-map split work | `lane_07_docs_handoff` |
| `docs/control/DOCUMENT_MAP_POLICY.md` | canonical | document-map router/registry split, size limits, and maintenance rules | no | document-map structure changes, registry split work, target-template navigation changes | `lane_07_docs_handoff` |
| `docs/EVOLUTION_MODEL.md` | canonical | docs-driven evolution, self-governance, self-validation maturity model | no | roadmap/evolution discussion | `lane_07_docs_handoff` |

## Installation And Target Project Templates

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `templates/DOCUMENT_MAP.template.md` | template | target-project document-map router starter structure | no | installing ASGK into another repository, target-repo document-map creation | `lane_07_docs_handoff` |
| `templates/DOCUMENT_REGISTRY.template.md` | template | target-project document-registry starter structure | no | installing ASGK into another repository, target-repo document-registry creation | `lane_07_docs_handoff` |
| `templates/agent_rules.template.yaml` | template | target-project clean assignment/worker rules starter structure | no | installing ASGK into another repository, target-repo agent-rules creation | `lane_07_docs_handoff` |

Template ownership rule:

```yaml
template_scope:
  asgk_repo_local_router: docs/DOCUMENT_MAP.md
  asgk_repo_local_registry: docs/DOCUMENT_REGISTRY.md
  target_project_router_template: templates/DOCUMENT_MAP.template.md
  target_project_registry_template: templates/DOCUMENT_REGISTRY.template.md
  target_project_finished_router: target_repo/docs/DOCUMENT_MAP.md
  target_project_finished_registry: target_repo/docs/DOCUMENT_REGISTRY.md
  asgk_internal_agent_rules: agent/agent_rules.yaml
  target_project_agent_rules_template: templates/agent_rules.template.yaml
  target_project_finished_agent_rules: target_repo/agent/agent_rules.yaml
rule:
  - do not copy ASGK's repo-local router or registry unchanged into a target project
  - do not copy ASGK's internal agent_rules.yaml as the target default
  - target repositories must customize their own router, registry, and agent rules
```

## Handoff And Recovery Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/control/CURRENT_STATUS_POLICY.md` | canonical | current-status overwrite, compaction, stale-status, and size rules | no | current-status update, stale status repair, handoff policy work | `lane_07_docs_handoff` |
| `docs/control/HANDOFF_PACKET.md` | canonical | generic work-unit handoff packet fields, validation status values, recovery stop conditions | no | interruption, model switch, tool switch, handoff recovery, `asgk.py handoff-check` | `lane_00_controller` |
| `docs/handoff/CURRENT_STATUS.md` | status | repo-level compact current state and next safe work | yes | all sessions and handoff updates | `lane_07_docs_handoff` |
| `docs/handoff/DECISIONS.md` | status | durable architecture/governance decisions | no | decision lookup or update | `lane_07_docs_handoff` |
| `docs/handoff/AGENT_LOG.md` | status | optional agent report log or links | no | handoff/reporting work | `lane_07_docs_handoff` |

Canonical ownership rule for handoff work:

```yaml
handoff_canonical_sources:
  repo_level_status: docs/handoff/CURRENT_STATUS.md
  repo_level_status_policy: docs/control/CURRENT_STATUS_POLICY.md
  work_unit_packet_spec: docs/control/HANDOFF_PACKET.md
  recovery_context: docs/control/CONTEXT_BUDGET_POLICY.md
  source_of_truth_rule: AGENTS.md
```

## Adapter Mechanism And Future Runtime Profiles

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/adapters/README.md` | canonical | v1.x generic adapter mechanism and v2.0 adapter boundary | no | adapter mechanism planning, v2.0 prep, handoff tool switch discussion | `lane_01_architecture` |
| `docs/adapters/ADAPTER_TEMPLATE.md` | template | future v2.0 runtime adapter structure | no | creating v2.0 adapter specs after vendor docs and observed tests exist | `lane_01_architecture` |
| `profiles/PROFILE_SPEC.md` | future_optional | v2.0 runtime profile schema and required fields | no | v2.0 profile work only | `lane_01_architecture` |
| `profiles/generic-repo-agent/` | future_optional | optional packaging of generic v1.x profile | no | v2.0 profile packaging work only | `lane_01_architecture` |
| `profiles/codex-app/` | future_optional | Codex-specific execution optimization | no | v2.0 runtime profile work after vendor docs and observed tests | `lane_01_architecture` |
| `profiles/chatgpt-web-github-connector/` | future_optional | ChatGPT Web/GitHub connector execution optimization | no | v2.0 runtime profile work after vendor docs and observed tests | `lane_01_architecture` |
| `profiles/opengoat/` | future_optional | OpenGoat-specific execution optimization | no | v2.0 runtime profile work after vendor docs and observed tests | `lane_01_architecture` |
| `profiles/claude-code/` | future_optional | Claude Code-specific execution optimization | no | v2.0 runtime profile work after vendor docs and observed tests | `lane_01_architecture` |
| `profiles/cursor/` | future_optional | Cursor-specific execution optimization | no | v2.0 runtime profile work after vendor docs and observed tests | `lane_01_architecture` |

Runtime profile or adapter docs must not be treated as prerequisites for v1.x
usage. They are optimization layers, not the governance core.

## Control Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/control/CONTROL_LAYER_V0.md` | canonical | durable control plane, work-unit states, operating loop, anti-drift rules | no | control-layer changes, onboarding, governance review | `lane_00_controller` |
| `docs/control/WORK_UNIT_STATE_MODEL.md` | canonical | valid work-unit states and transitions | no | issue/PR state changes, workflow design | `lane_00_controller` |
| `docs/control/AUTONOMOUS_RUNBOOK.md` | canonical | controller/worker duties, lane integration loop | no | multi-agent or multi-lane runs | `lane_00_controller` |
| `docs/control/LANE_STATUS.md` | status | lane queue, owner, blocker, next action | no | multi-lane coordination | `lane_00_controller` |
| `docs/control/ISSUE_HYGIENE_GATE.md` | canonical | stale issue detection and issue-start gate | no | before selecting or closing issues | `lane_00_controller` |
| `docs/control/FAILURE_THRESHOLDS.md` | canonical | stop thresholds and notification conditions | no | repeated failures, autonomous run blockers | `lane_00_controller` |
| `docs/control/CONTEXT_BUDGET_POLICY.md` | canonical | context read sets, handoff recovery read set, context expansion rules | no | context selection, handoff recovery, token-budget review | `lane_00_controller` |
| `docs/control/AGENT_CAPABILITY_MATRIX.md` | canonical | task risk classification, minimum assignment intelligence level, worker-assignment eligibility, low-risk merge compatibility, human-gate requirement, escalation/downscope decisions, context read-set binding | no | task risk review, agent assignment, escalation, downscoping, merge eligibility review | `lane_00_controller` |
| `docs/control/VALIDATION_STRATEGY.md` | canonical | validation layer responsibilities, blocking vs warning, negative test targets | no | validation/tooling work | `lane_06_ci_github` |
| `docs/control/PR_REVIEW_CHECKLIST.md` | canonical | repeatable PR review sequence and outcomes | no | PR review and merge readiness | `lane_00_controller` |
| `docs/control/NEGATIVE_TEST_PLAN.md` | canonical | negative test matrix, expected outcomes, implementation phases | no | negative fixture or validator work | `lane_00_controller` |
| `docs/control/UNCONTROLLED_DOCUMENT_AUDIT.md` | canonical | uncontrolled-document growth-risk classification and audit record | no | uncontrolled-document audit or status-like document growth review | `lane_07_docs_handoff` |
| `docs/control/V1_READINESS_AUDIT.md` | canonical | v1.0 readiness criteria, blockers, follow-ups, and v2.0 deferrals | no | v1.0 release preparation, readiness review, milestone planning | `lane_07_docs_handoff` |
| `docs/control/V1_1_STABILIZATION_PLAN.md` | canonical | v1.1 stabilization sequence before release preparation | no | stabilization planning, field-test planning, release-prep deferral review | `lane_07_docs_handoff` |
| `docs/control/DOCUMENT_MAP_POLICY.md` | canonical | document-map router/registry split, size limits, and maintenance rules | no | document-map structure changes, registry split work, target-template navigation changes | `lane_07_docs_handoff` |

Capability matrix boundary rule:

```yaml
agent_capability_matrix_binding_for:
  - task risk classification
  - minimum assignment intelligence level
  - worker-assignment eligibility
  - low-risk merge compatibility
  - human-gate requirement
  - escalation and downscope decisions
  - context read-set binding
not_binding_for:
  - runtime-native subagent orchestration
  - vendor-specific profile routing
  - goal workflow behavior
  - platform tool scheduling
```

## Merge And Human-Gate Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md` | canonical | low-risk merge gates, allowed necessary operations, merge blockers | no | merge decisions, PR closeout | `lane_00_controller` |
| `docs/control/HUMAN_GATED_OPERATIONS.md` | canonical | operations requiring explicit human approval | no | high-risk change, restricted capability, unclear merge | `lane_05_security` |
| `docs/control/MERGE_DECISION_RECORD.md` | canonical | required merge decision YAML fields | no | any merge-eligible PR, `asgk.py pr-body-check` | `lane_06_ci_github` |
| `docs/bootstrap/11_auto_merge_policy.md` | summary | short bootstrap-level auto-merge overview | no | bootstrap orientation only | `lane_00_controller` |

Canonical ownership rule for merge work:

```yaml
merge_policy_canonical_sources:
  - docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
  - docs/control/HUMAN_GATED_OPERATIONS.md
  - docs/control/MERGE_DECISION_RECORD.md
summary_only:
  - docs/bootstrap/11_auto_merge_policy.md
```

## Storage And Runtime Boundary Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/architecture/STORAGE_PROFILE.md` | canonical | Code Repo / Artifact Root / Local State Root model | no | storage, workspace, artifact, cache, or sync work | `lane_01_architecture` |
| `docs/architecture/LOG_AND_RECORD_RETENTION_POLICY.md` | canonical | log and record placement, Artifact Root structure, Local State Root structure, retention, and naming conventions | no | log/record placement, artifact/local-state planning, field-test storage planning | `lane_05_security` |
| `docs/architecture/CACHE_AND_STATE_POLICY.md` | canonical | cache and live local state placement | no | cache, SQLite, preview, model-cache work | `lane_05_security` |
| `docs/architecture/WORKSPACE_LOCK_POLICY.md` | canonical | workspace lock behavior and sync-folder warning | no | artifact root writes, app runtime validation | `lane_05_security` |
| `docs/architecture/RUNTIME_ARTIFACT_POLICY.md` | canonical | runtime artifact commit boundaries | no | PR hygiene, artifact path changes | `lane_05_security` |
| `docs/bootstrap/02_storage_roots.md` | summary | short bootstrap-level storage overview | no | bootstrap orientation only | `lane_01_architecture` |
| `contracts/storage_profile.contract.yaml` | contract | storage-profile invariants | no | storage schema/contract changes | `lane_02_schema_contracts` |
| `schemas/storage_profile.schema.json` | schema | machine-readable storage profile structure | no | storage fixture or schema validation work | `lane_02_schema_contracts` |

Canonical ownership rule for storage work:

```yaml
storage_canonical_source: docs/architecture/STORAGE_PROFILE.md
retention_canonical_source: docs/architecture/LOG_AND_RECORD_RETENTION_POLICY.md
storage_summaries:
  - docs/bootstrap/02_storage_roots.md
storage_specialized_policies:
  - docs/architecture/CACHE_AND_STATE_POLICY.md
  - docs/architecture/WORKSPACE_LOCK_POLICY.md
  - docs/architecture/RUNTIME_ARTIFACT_POLICY.md
```

## Bootstrap Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/bootstrap/00_project_brief.md` | canonical | project mission and non-goals | no | project initialization, mission changes | `lane_01_architecture` |
| `docs/bootstrap/01_physical_boundaries.md` | canonical | writable paths, protected paths, forbidden actions | no | path, security, filesystem, CI, PR hygiene work | `lane_05_security` |
| `docs/bootstrap/02_storage_roots.md` | summary | short bootstrap-level storage overview | no | bootstrap orientation only | `lane_01_architecture` |
| `docs/bootstrap/03_tech_stack.md` | canonical | declared stack and dependency policy | no | dependency or toolchain changes | `lane_03_backend` |
| `docs/bootstrap/04_file_structure.md` | canonical | top-level file layout and dependency direction | no | new directories, repo structure changes | `lane_01_architecture` |
| `docs/bootstrap/05_context_budget.md` | summary | basic task context limits | no | task scoping, token-budget review | `lane_00_controller` |
| `docs/bootstrap/06_naming_versioning.md` | canonical | branch, commit, timestamp, and schema-version conventions | no | branch/commit/schema naming changes | `lane_06_ci_github` |
| `docs/bootstrap/07_contract_first.md` | canonical | contract-first rule | no | contract/schema/artifact work | `lane_02_schema_contracts` |
| `docs/bootstrap/08_acceptance_criteria.md` | canonical | three-layer acceptance model and definition of done | no | issue/PR acceptance changes | `lane_00_controller` |
| `docs/bootstrap/09_safety_checks.md` | summary | minimum safety check overview | no | safety orientation only | `lane_05_security` |
| `docs/bootstrap/10_roadmap.md` | template | roadmap hierarchy | no | milestone/roadmap planning | `lane_00_controller` |
| `docs/bootstrap/12_productization_notes.md` | reference | productization framing, v1.x/v2.0 product boundary | no | productization planning only | `lane_07_docs_handoff` |
| `docs/bootstrap/13_artifact_promotion_policy.md` | summary | promotion chain overview and status values | no | artifact/data/evidence-heavy work | `lane_02_schema_contracts` |
| `docs/bootstrap/14_execution_lanes.md` | canonical | execution lanes and external-call boundaries | no | execution lane/API/provider discussions | `lane_05_security` |
| `docs/bootstrap/15_source_or_input_class_matrix.md` | optional module | source/input class use boundaries | no | evidence, source, claim, or context-pack projects | `lane_02_schema_contracts` |
| `docs/bootstrap/16_downstream_promotion_matrix.md` | optional module | downstream artifact eligibility | no | artifact promotion or output eligibility work | `lane_02_schema_contracts` |
| `docs/bootstrap/17_readiness_audit_policy.md` | canonical | readiness audit before output, API, import, publication, or external calls | no | API/model/provider/output readiness changes | `lane_05_security` |

## Task Packet, Agent, And Template Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/control/TASK_PACKET_FORMAT.md` | canonical | human-readable task packet requirements | no | creating or validating task packets | `lane_00_controller` |
| `schemas/task_packet.schema.json` | schema | machine-readable task packet structure | no | task packet validation changes | `lane_02_schema_contracts` |
| `agent/task_packet.template.yaml` | template | reusable task packet starting point | no | creating repo task packets, `asgk.py task-packet-check` | `lane_00_controller` |
| `.github/ISSUE_TEMPLATE/agent_task.yml` | template | GitHub issue capture form | no | issue-template changes | `lane_06_ci_github` |
| `examples/task_packet.example.yaml` | example | sample task packet | no | onboarding, task packet examples | `lane_07_docs_handoff` |
| `docs/control/AGENT_REPORT_FORMAT.md` | canonical | required agent report sections | no | PR handoff/reporting work | `lane_00_controller` |
| `schemas/agent_report.schema.json` | schema | machine-readable report fields | no | report validation work | `lane_02_schema_contracts` |
| `examples/agent_report.example.md` | example | sample report | no | onboarding, report examples | `lane_07_docs_handoff` |
| `agent/agent_rules.yaml` | canonical | ASGK internal compatibility roles, intelligence levels, legacy compatibility keys, stop conditions | no | ASGK internal agent-rule compatibility work only; target projects should use `templates/agent_rules.template.yaml` | `lane_00_controller` |
| `agent/workflow.yaml` | canonical | workflow gate sequence | no | workflow automation changes | `lane_00_controller` |
| `agent/task_packets/*.yaml` | template/status | lane-specific assignment packets | no | lane work or autonomous runs | specific lane |

Canonical ownership rule for task packets and agent rules:

```yaml
task_packet_canonical_human_spec: docs/control/TASK_PACKET_FORMAT.md
task_packet_canonical_schema: schemas/task_packet.schema.json
task_packet_machine_template: agent/task_packet.template.yaml
task_packet_github_surface: .github/ISSUE_TEMPLATE/agent_task.yml
task_packet_example: examples/task_packet.example.yaml
asgk_internal_agent_rules: agent/agent_rules.yaml
target_project_agent_rules_template: templates/agent_rules.template.yaml
```

## Contracts And Schemas

| Path | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `contracts/*.yaml` | contract | semantic contract rules and invariants | no | contract, schema, validation, artifact work | `lane_02_schema_contracts` |
| `schemas/*.json` | schema | machine-readable validation structures | no | schema validation, fixtures, tooling | `lane_02_schema_contracts` |

Contracts explain intent and invariants. Schemas enforce structure. If they
disagree, stop and open a schema/contract alignment issue.

## Scripts And CI

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `scripts/check_project.py` | script | required directory scaffold check | no | CI/tooling/debug validation | `lane_06_ci_github` |
| `scripts/validate_bootstrap.py` | script | bootstrap governance validation behavior | no | CI/tooling/debug validation | `lane_06_ci_github` |
| `scripts/governance_hygiene.py` | script | changed-path and protected-path hygiene | no | path hygiene, negative changed-path checks, future CLI work | `lane_06_ci_github` |
| `scripts/asgk.py` | script | minimal ASGK CLI wrapper for doctor/validate/hygiene/negative/status/closeout/pr-body/task-packet/handoff checks | no | local validation, status-check, closeout-check, handoff-check, PR-body/task-packet checks, future CLI work | `lane_06_ci_github` |
| `.github/workflows/bootstrap-validation.yml` | template/script | GitHub Actions bootstrap validation workflow | no | CI/workflow changes | `lane_06_ci_github` |
| `.github/PULL_REQUEST_TEMPLATE.md` | template | required PR body sections and Merge Decision Record surface | no | PR creation/review, template changes, `asgk.py pr-body-check` | `lane_06_ci_github` |

## Examples And Fixtures

| Path | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `examples/*.json` | example | valid sample payloads | no | onboarding, validator examples, fixture design | `lane_07_docs_handoff` |
| `examples/*.yaml` | example | valid sample task packets | no | onboarding, task packet examples | `lane_07_docs_handoff` |
| `examples/*.md` | example | report or documentation examples | no | onboarding, report examples | `lane_07_docs_handoff` |
| `examples/negative/*` | example | opt-in expected-failure fixtures | no | negative validation work, `asgk.py negative`, governance hygiene tests | `lane_02_schema_contracts` |

Examples are not policy. If an example conflicts with a canonical policy,
contract, or schema, fix the example.

## Task-type Reading Guide

Use this guide to reduce token consumption.

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

readiness_audit_task:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - docs/control/V1_READINESS_AUDIT.md
    - docs/EVOLUTION_MODEL.md
    - docs/DOCUMENT_MAP.md

stabilization_planning_task:
  read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - docs/control/V1_1_STABILIZATION_PLAN.md
    - docs/control/V1_READINESS_AUDIT.md
    - docs/DOCUMENT_MAP.md

tooling_or_validation_task:
  read:
    - AGENTS.md
    - current issue or PR
    - target script or workflow file
    - docs/control/VALIDATION_STRATEGY.md
    - relevant examples/negative fixture if named by the issue
```

## Maintenance Rules

1. Do not delete or consolidate overlapping documents until the canonical owner
   is recorded here.
2. Summary documents should point to canonical documents rather than repeating
   full policy text.
3. If a document becomes canonical for a new topic, update this map in the same
   PR.
4. If validation behavior changes, update the relevant script, schema, example,
   and this map together.
5. If an agent task reads more than the task-type reading guide requires, the
   agent report should state why.
6. Do not add runtime-specific profile or adapter docs to the default read set
   before v2.0.
7. When a new CLI command becomes canonical for a check, record it in Scripts And
   CI and in the relevant task-type reading guide.
8. Do not treat this ASGK repository-local map as the target-project map during
   installation. Use `templates/DOCUMENT_MAP.template.md` and customize it in the
   target repository.
9. Do not treat ASGK's internal `agent/agent_rules.yaml` as the target-project
   default. Use `templates/agent_rules.template.yaml` and customize it in the
   target repository.
