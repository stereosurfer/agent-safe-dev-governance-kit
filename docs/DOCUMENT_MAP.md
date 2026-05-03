# Document Map

Status: active repository navigation and source-ownership map.

This file defines which documents are canonical, which documents are summaries,
which documents are examples, which files are executable governance surfaces,
and which files should be read only for specific task types.

Its main purpose is to reduce token use, prevent document role drift, and stop
agents from treating repeated summaries as competing authority.

## Core Rule

```text
Do not read the whole repository for every task.
Read the smallest set of canonical documents required by the work unit.
```

If two documents appear to disagree, prefer the document marked `canonical` for
that topic. If a summary document disagrees with a canonical document, the
summary document is stale and should be fixed in a separate issue.

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
| `docs/handoff/CURRENT_STATUS.md` | status | current repo state, active PRs, active milestones, next safe work | yes | all new sessions, handoff recovery, handoff updates | `lane_07_docs_handoff` |
| current GitHub issue or PR | canonical | active task objective, allowed paths, acceptance, validation, merge state | yes | every work unit | active task lane |
| `docs/QUICKSTART.md` | summary | first-use workflow and onboarding | no | onboarding and first repository smoke test | `lane_07_docs_handoff` |
| `docs/EVOLUTION_MODEL.md` | canonical | docs-driven evolution, self-governance, self-validation maturity model | no | roadmap/evolution discussion | `lane_07_docs_handoff` |

## Handoff And Recovery Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/control/HANDOFF_PACKET.md` | canonical | generic work-unit handoff packet fields, validation status values, recovery stop conditions | no | interruption, model switch, tool switch, handoff recovery, `asgk.py handoff-check` | `lane_00_controller` |
| `docs/handoff/CURRENT_STATUS.md` | status | repo-level current state and next safe work | yes | all sessions and handoff updates | `lane_07_docs_handoff` |
| `docs/handoff/DECISIONS.md` | status | durable architecture/governance decisions | no | decision lookup or update | `lane_07_docs_handoff` |
| `docs/handoff/AGENT_LOG.md` | status | optional agent report log or links | no | handoff/reporting work | `lane_07_docs_handoff` |

Canonical ownership rule for handoff work:

```yaml
handoff_canonical_sources:
  repo_level_status: docs/handoff/CURRENT_STATUS.md
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
| `docs/control/CONTEXT_BUDGET_POLICY.md` | canonical | task context profiles, handoff recovery read set, context expansion rules | no | context selection, handoff recovery, token-budget review | `lane_00_controller` |
| `docs/control/AGENT_CAPABILITY_MATRIX.md` | canonical | task type to intelligence level/risk/human gate mapping | no | agent assignment, escalation, downscoping | `lane_00_controller` |
| `docs/control/VALIDATION_STRATEGY.md` | canonical | validation layer responsibilities, blocking vs warning, negative test targets | no | validation/tooling work | `lane_06_ci_github` |
| `docs/control/PR_REVIEW_CHECKLIST.md` | canonical | repeatable PR review sequence and outcomes | no | PR review and merge readiness | `lane_00_controller` |
| `docs/control/NEGATIVE_TEST_PLAN.md` | canonical | negative test matrix, expected outcomes, implementation phases | no | negative fixture or validator work | `lane_00_controller` |

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
| `docs/architecture/CACHE_AND_STATE_POLICY.md` | canonical | cache and live local state placement | no | cache, SQLite, preview, model-cache work | `lane_05_security` |
| `docs/architecture/WORKSPACE_LOCK_POLICY.md` | canonical | workspace lock behavior and sync-folder warning | no | artifact root writes, app runtime validation | `lane_05_security` |
| `docs/architecture/RUNTIME_ARTIFACT_POLICY.md` | canonical | runtime artifact commit boundaries | no | PR hygiene, artifact path changes | `lane_05_security` |
| `docs/bootstrap/02_storage_roots.md` | summary | short bootstrap-level storage overview | no | bootstrap orientation only | `lane_01_architecture` |
| `contracts/storage_profile.contract.yaml` | contract | storage-profile invariants | no | storage schema/contract changes | `lane_02_schema_contracts` |
| `schemas/storage_profile.schema.json` | schema | machine-readable storage profile structure | no | storage fixture or schema validation work | `lane_02_schema_contracts` |

Canonical ownership rule for storage work:

```yaml
storage_canonical_source: docs/architecture/STORAGE_PROFILE.md
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
| `agent/agent_rules.yaml` | canonical | roles, intelligence levels, sub-agent required fields, stop conditions | no | agent routing, sub-agent, or role changes | `lane_00_controller` |
| `agent/workflow.yaml` | canonical | workflow gate sequence | no | workflow automation changes | `lane_00_controller` |
| `agent/task_packets/*.yaml` | template/status | lane-specific assignment packets | no | lane work or autonomous runs | specific lane |

Canonical ownership rule for task packets:

```yaml
task_packet_canonical_human_spec: docs/control/TASK_PACKET_FORMAT.md
task_packet_canonical_schema: schemas/task_packet.schema.json
task_packet_machine_template: agent/task_packet.template.yaml
task_packet_github_surface: .github/ISSUE_TEMPLATE/agent_task.yml
task_packet_example: examples/task_packet.example.yaml
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
| `scripts/asgk.py` | script | minimal ASGK CLI wrapper for doctor/validate/hygiene/negative/pr-body/task-packet/handoff checks | no | local validation, handoff-check, PR-body/task-packet checks, future CLI work | `lane_06_ci_github` |
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
