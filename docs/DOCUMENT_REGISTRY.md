# Document Registry

Status: active ASGK repository-local document registry.

This file is the complete ASGK repository document registry and canonical
ownership table.

`docs/DOCUMENT_MAP.md` is the compact navigation router. This file is the full
registry surface used when canonical ownership, read conditions, document roles,
or ownership rows must be inspected or updated.

## Scope

```text
DOCUMENT_REGISTRY.md is repo-local.
```

This file governs the ASGK repository only. Target repositories must create
their own `docs/DOCUMENT_REGISTRY.md` from
`templates/DOCUMENT_REGISTRY.template.md` when they adopt the source-only
governance scaffold.

## Relationship To DOCUMENT_MAP.md

```yaml
relationship:
  docs/DOCUMENT_MAP.md: compact navigation router
  docs/DOCUMENT_REGISTRY.md: complete document registry
  docs/control/DOCUMENT_MAP_POLICY.md: maintenance and split policy
```

Do not read this file by default. Read it only when:

```yaml
read_when:
  - canonical ownership is unclear
  - current issue changes document ownership
  - current issue changes document-map or registry structure
  - validation or reviewer feedback points to registry mismatch
  - target work explicitly requires a registry audit
```

## Registry Migration Status

```yaml
registry_migration_status:
  stage: migrated
  full_registry_tables_moved: true
  previous_full_registry_source: docs/DOCUMENT_MAP.md
  current_full_registry_source: docs/DOCUMENT_REGISTRY.md
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
  skill: Source-distributed reusable agent procedure.
  future_optional: Planned future capability, not part of current v1.x core.
```

## Entry And Startup Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `README.md` | summary | project positioning, source-adoption path, operating loop overview | yes | all new sessions | `lane_07_docs_handoff` |
| `LICENSE` | canonical | Apache-2.0 license for ASGK source release and copied/adapted ASGK-derived material | no | source release review, target-repo license handling, install-surface review | `lane_07_docs_handoff` |
| `AGENTS.md` | canonical | agent startup order, source-of-truth rule, work-unit rule, stop conditions | yes | all agent sessions | `lane_00_controller` |
| `docs/handoff/CURRENT_STATUS.md` | status | compact current repo snapshot and next safe work | yes | all new sessions, handoff recovery, handoff updates | `lane_07_docs_handoff` |
| current GitHub issue or PR | canonical | active task objective, allowed paths, acceptance, validation, merge state | yes | every work unit | active task lane |
| `docs/QUICKSTART.md` | summary | first-use workflow, onboarding, and target-repo source-adoption orientation | no | onboarding and first repository smoke test | `lane_07_docs_handoff` |
| `docs/INSTALL_SURFACE.md` | canonical | target-project source-only adoption surface, license handling, copy/template/customize/do-not-copy boundaries | no | adopting ASGK into another repository, field-test preparation, target-repo scaffold planning, license-handling review | `lane_07_docs_handoff` |
| `docs/SKILL_PACK.md` | summary | ASGK skill-pack usage modes, maintenance touchpoints, field-test sequence, and no-new-gates constraint | no | installing or referencing ASGK skills, reviewing architecture-to-skill impact, skill-pack field test, target adoption planning | `lane_07_docs_handoff` |
| `docs/DOCUMENT_REGISTRY.md` | canonical | complete repo-local document registry | no | canonical ownership lookup, registry repair, document-map split work | `lane_07_docs_handoff` |
| `docs/control/DOCUMENT_MAP_POLICY.md` | canonical | document-map router/registry split, size limits, and maintenance rules | no | document-map structure changes, registry split work, target-template navigation changes | `lane_07_docs_handoff` |
| `docs/EVOLUTION_MODEL.md` | canonical | docs-driven evolution, self-governance, self-validation maturity model | no | roadmap/evolution discussion | `lane_07_docs_handoff` |

## Source Adoption And Target Project Templates

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `templates/DOCUMENT_MAP.template.md` | template | target-project document-map router starter structure | no | adopting ASGK into another repository, target-repo document-map creation | `lane_07_docs_handoff` |
| `templates/DOCUMENT_REGISTRY.template.md` | template | target-project document-registry starter structure | no | adopting ASGK into another repository, target-repo document-registry creation | `lane_07_docs_handoff` |
| `templates/decision_packet.template.yaml` | template | reusable vertical-governance decision packet starting point | no | creating a decision packet for a major decision point | `lane_07_docs_handoff` |

## Source-Distributed Skills

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `skills/asgk-startup/SKILL.md` | skill | startup and live GitHub state reconciliation procedure | no | starting or resuming an ASGK-governed session | `lane_07_docs_handoff` |
| `skills/asgk-issue-scoping/SKILL.md` | skill | converting user requests into ASGK-compliant GitHub issues | no | creating or refining a durable work-unit issue | `lane_07_docs_handoff` |
| `skills/asgk-pr-evidence-merge-decision/SKILL.md` | skill | PR body evidence and Merge Decision Record procedure | no | opening or updating an ASGK PR body | `lane_07_docs_handoff` |
| `skills/asgk-gatekeeper/SKILL.md` | skill | PR readiness check procedure using existing validators | no | checking PR readiness or CI follow-up | `lane_06_ci_github` |
| `skills/asgk-post-merge-closeout/SKILL.md` | skill | post-merge issue/status closeout procedure | no | after a PR merges or stale issue closeout is suspected | `lane_07_docs_handoff` |
| `skills/asgk-current-status-handoff/SKILL.md` | skill | current-status impact and handoff refresh procedure | no | updating or auditing `docs/handoff/CURRENT_STATUS.md` | `lane_07_docs_handoff` |
| `skills/asgk-evidence-audit/SKILL.md` | skill | validation and completion evidence classification procedure | no | auditing PR evidence, reports, or release notes | `lane_07_docs_handoff` |
| `skills/asgk-release-prep/SKILL.md` | skill | source-only release planning, human-gated execution, and release-state closeout procedure | no | planning, executing, or closing out an ASGK source-only release | `lane_07_docs_handoff` |
| `skills/asgk-target-install-audit/SKILL.md` | skill | target-repository ASGK adoption audit procedure | no | evaluating or transferring ASGK into another repository | `lane_07_docs_handoff` |
| `skills/asgk-governance-health-check/SKILL.md` | skill | periodic governance drift health-check procedure | no | weekly review, milestone review, or public/customer handoff | `lane_07_docs_handoff` |

Template ownership rule:

```yaml
template_scope:
  asgk_repo_local_router: docs/DOCUMENT_MAP.md
  asgk_repo_local_registry: docs/DOCUMENT_REGISTRY.md
  target_project_router_template: templates/DOCUMENT_MAP.template.md
  target_project_registry_template: templates/DOCUMENT_REGISTRY.template.md
  target_project_finished_router: target_repo/docs/DOCUMENT_MAP.md
  target_project_finished_registry: target_repo/docs/DOCUMENT_REGISTRY.md
  decision_packet_template: templates/decision_packet.template.yaml
rule:
  - do not copy ASGK's repo-local router or registry unchanged into a target project
  - target repositories must customize their own router and registry
  - decision packets are used for major decision points and must reference durable sources of truth
```

## Handoff And Recovery Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/control/CURRENT_STATUS_POLICY.md` | canonical | current-status overwrite, compaction, stale-status, PR status freshness gate, and size rules | no | current-status update, stale status repair, handoff policy work, PR current-status impact review | `lane_07_docs_handoff` |
| `docs/control/HANDOFF_PACKET.md` | canonical | generic work-unit handoff packet fields, validation status values, recovery stop conditions | no | interruption, model switch, tool switch, handoff recovery, `asgk.py handoff-check` | `lane_00_controller` |
| `docs/handoff/CURRENT_STATUS.md` | status | repo-level compact current state and next safe work | yes | all sessions and handoff updates | `lane_07_docs_handoff` |
| `docs/handoff/DECISIONS.md` | status | durable architecture/governance decisions | no | decision lookup or update | `lane_07_docs_handoff` |
| `docs/handoff/ISSUE_CLOSEOUT_REVIEW_RULES.md` | status | writing rules for mandatory issue closeout decision analysis in GitHub issue comments | no | closeout review, governance health check, upgrade audit, or similar prior-work lookup | `lane_07_docs_handoff` |
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
| `docs/control/ISSUE_HYGIENE_GATE.md` | canonical | stale issue detection and issue-start gate | no | before selecting or closing issues | `lane_00_controller` |
| `docs/control/FAILURE_THRESHOLDS.md` | canonical | stop thresholds and notification conditions | no | repeated failures, blockers | `lane_00_controller` |
| `docs/control/CONTEXT_BUDGET_POLICY.md` | canonical | context read sets, handoff recovery read set, context expansion rules | no | context selection, handoff recovery, token-budget review | `lane_00_controller` |
| `docs/control/AGENT_CAPABILITY_MATRIX.md` | canonical | task risk classification, minimum intelligence level, low-risk merge compatibility, human-gate requirement, escalation/downscope decisions, context read-set binding | no | task risk review, escalation, downscoping, merge eligibility review | `lane_00_controller` |
| `docs/control/VALIDATION_STRATEGY.md` | canonical | validation layer responsibilities, blocking vs warning, negative test targets, fail-closed policy-gate validation | no | validation/tooling work, policy-gate checker review | `lane_06_ci_github` |
| `docs/control/PR_REVIEW_CHECKLIST.md` | canonical | repeatable PR review sequence, current-status freshness review, and outcomes | no | PR review, current-status impact review, merge readiness | `lane_00_controller` |
| `docs/control/NEGATIVE_TEST_PLAN.md` | canonical | negative test matrix, expected outcomes, implementation phases | no | negative fixture or validator work | `lane_00_controller` |
| `docs/control/UNCONTROLLED_DOCUMENT_AUDIT.md` | canonical | uncontrolled-document growth-risk classification and audit record | no | uncontrolled-document audit or status-like document growth review | `lane_07_docs_handoff` |
| `docs/control/HISTORICAL_ASGK_READINESS_EVIDENCE.md` | historical_evidence | archived ASGK source-only readiness evidence and first-release decision trail | no | auditing old ASGK readiness decisions or target-install do-not-copy boundaries | `lane_07_docs_handoff` |
| `docs/control/HISTORICAL_ASGK_STABILIZATION_EVIDENCE.md` | historical_evidence | archived ASGK early stabilization evidence and field-test lesson record | no | auditing old ASGK stabilization decisions or target-install do-not-copy boundaries | `lane_07_docs_handoff` |
| `docs/control/SOURCE_ONLY_RELEASE_POLICY.md` | canonical | Source-only release gates, human-gated release execution boundary, distribution boundary, version applicability, and release-history source-of-truth boundary | no | source-only release planning, release execution review, release-state closeout, distribution-boundary review | `lane_07_docs_handoff` |
| `docs/control/DOCUMENT_MAP_POLICY.md` | canonical | document-map router/registry split, size limits, and maintenance rules | no | document-map structure changes, registry split work, target-template navigation changes | `lane_07_docs_handoff` |
| `docs/control/DECISION_POINT_REGISTRY.md` | canonical | vertical-governance decision point router, authority order, decision packet trigger conditions | no | major decision point, decision packet creation, vertical-governance planning | `lane_07_docs_handoff` |
| `docs/control/TARGET_INSTALL_CHECKLIST.md` | canonical | target-project install readiness checklist and structural acceptance conditions | no | target install review, field-test preparation, target-install validation planning | `lane_07_docs_handoff` |
| `docs/control/TARGET_INSTALL_VALIDATION_PLAN.md` | canonical | target-install checker/planner behavior, future validator check categories, and output contract | no | target-install checker/planner behavior review, validator implementation planning, validation roadmap | `lane_06_ci_github` |

Capability matrix boundary rule:

```yaml
agent_capability_matrix_binding_for:
  - task risk classification
  - minimum intelligence level
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
| `docs/bootstrap/10_roadmap.md` | canonical | roadmap hierarchy and active milestone register | no | milestone/roadmap planning, active milestone review | `lane_00_controller` |
| `docs/bootstrap/12_productization_notes.md` | reference | productization framing, v1.x/v2.0 product boundary | no | productization planning only | `lane_07_docs_handoff` |
| `docs/bootstrap/13_artifact_promotion_policy.md` | summary | promotion chain overview and status values | no | artifact/data/evidence-heavy work | `lane_02_schema_contracts` |
| `docs/bootstrap/14_execution_lanes.md` | canonical | execution lanes and external-call boundaries | no | execution lane/API/provider discussions | `lane_05_security` |
| `docs/bootstrap/15_source_or_input_class_matrix.md` | optional module | source/input class use boundaries | no | evidence, source, claim, or context-pack projects | `lane_02_schema_contracts` |
| `docs/bootstrap/16_downstream_promotion_matrix.md` | optional module | downstream artifact eligibility | no | artifact promotion or output eligibility work | `lane_02_schema_contracts` |
| `docs/bootstrap/17_readiness_audit_policy.md` | canonical | readiness audit before output, API, import, publication, or external calls | no | API/model/provider/output readiness changes | `lane_05_security` |

## Task Packet And Report Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/control/TASK_PACKET_FORMAT.md` | canonical | human-readable task packet requirements | no | creating or validating task packets | `lane_00_controller` |
| `schemas/task_packet.schema.json` | schema | machine-readable task packet structure | no | task packet validation changes | `lane_02_schema_contracts` |
| `templates/task_packet.template.yaml` | template | reusable task packet starting point | no | creating repo task packets, `asgk.py task-packet-check` | `lane_00_controller` |
| `.github/ISSUE_TEMPLATE/agent_task.yml` | template | GitHub issue capture form | no | issue-template changes | `lane_06_ci_github` |
| `examples/task_packet.example.yaml` | example | sample task packet | no | onboarding, task packet examples | `lane_07_docs_handoff` |
| `docs/control/AGENT_REPORT_FORMAT.md` | canonical | required agent report sections | no | PR handoff/reporting work | `lane_00_controller` |
| `schemas/agent_report.schema.json` | schema | machine-readable report fields | no | report validation work | `lane_02_schema_contracts` |
| `examples/agent_report.example.md` | example | sample report | no | onboarding, report examples | `lane_07_docs_handoff` |

Canonical ownership rule for task packets:

```yaml
task_packet_canonical_human_spec: docs/control/TASK_PACKET_FORMAT.md
task_packet_canonical_schema: schemas/task_packet.schema.json
task_packet_machine_template: templates/task_packet.template.yaml
task_packet_github_surface: .github/ISSUE_TEMPLATE/agent_task.yml
task_packet_example: examples/task_packet.example.yaml
decision_packet_template: templates/decision_packet.template.yaml
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
| `scripts/policy_gate_check.py` | script | read-only fail-closed PR-body policy gate check without low-risk inference | no | policy-gate validation, PR-body gate coherence review | `lane_06_ci_github` |
| `scripts/asgk.py` | script | ASGK CLI wrapper for doctor/validate/hygiene/negative/status/closeout/pr-body/task-packet/handoff/target-install checks, including opt-in policy-gate and target-install expected failures | no | local validation, status-check, closeout-check, handoff-check, PR-body/task-packet checks, policy-gate negative checks, target-install negative checks, target-install-check | `lane_06_ci_github` |
| `scripts/pr_governance_preflight.py` | script | thin file-backed PR body preflight before `gh pr create` or `gh pr edit` | no | PR body create/edit, local preflight before GitHub Actions, target adoption of ASGK CLI tooling | `lane_06_ci_github` |
| `scripts/target_install_plan.py` | script | standalone read-only target-install plan generation | no | target-install planning, scaffold preparation, install-plan review | `lane_06_ci_github` |
| `.github/workflows/bootstrap-validation.yml` | template/script | GitHub Actions bootstrap validation workflow | no | CI/workflow changes | `lane_06_ci_github` |
| `.github/PULL_REQUEST_TEMPLATE.md` | template | required PR body sections, Current Status Impact, and Merge Decision Record surface | no | PR creation/review, current-status impact classification, template changes, `asgk.py pr-body-check` | `lane_06_ci_github` |

## Examples And Fixtures

| Path | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `examples/README.md` | summary | examples and fixture taxonomy, adoption boundary, and read boundary | no | onboarding, examples/fixture cleanup, target-adoption review | `lane_07_docs_handoff` |
| `examples/*.json` | example/fixture | valid sample payloads or machine fixtures | no | onboarding, validator examples, fixture design | `lane_07_docs_handoff` |
| `examples/*.yaml` | example/fixture | valid sample task packets or machine fixtures | no | onboarding, task packet examples, fixture design | `lane_07_docs_handoff` |
| `examples/*.md` | example/fixture | report, PR-body, or documentation examples and fixtures | no | onboarding, report examples, parser fixture design | `lane_07_docs_handoff` |
| `examples/negative/*` | fixture | opt-in expected-failure fixtures | no | negative validation work, `asgk.py negative`, governance hygiene tests | `lane_02_schema_contracts` |
| `examples/negative/policy_gate/*` | fixture | opt-in expected-failure PR-body policy-gate fixtures | no | policy-gate negative validation work | `lane_06_ci_github` |
| `examples/negative/target_install/*` | fixture | opt-in expected-failure target-install checker fixtures | no | target-install negative validation work | `lane_06_ci_github` |

Examples and fixtures are not policy authority. If an example or fixture
conflicts with a canonical policy, contract, schema, validator, or current
GitHub issue/PR, fix the example or the stale reference.

## Registry Rules

1. Add new document rows here after the split is complete.
2. Keep `docs/DOCUMENT_MAP.md` as a compact router.
3. Do not add task-type read sets here; use `docs/control/CONTEXT_BUDGET_POLICY.md`.
4. Do not add install-surface rules here; use `docs/INSTALL_SURFACE.md`.
5. If this registry conflicts with a canonical document, fix the registry or the
   stale summary in a separate issue.
