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

This file governs the ASGK repository only. Target repositories are not
required to create ASGK-named map or registry files. They retain target-owned
authority and navigation surfaces; the templates are optional references used
only when a frontier-guided assessment identifies a missing equivalent.

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
  historical_evidence: Superseded or archival material for bounded historical or migration lookup; never current authority.
```

## Entry And Startup Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `README.md` | summary | product positioning, durable human-AI handoff, target-assessment entry, and operating loop overview | yes | all new sessions | `lane_07_docs_handoff` |
| `LICENSE` | canonical | Apache-2.0 license for ASGK source release and copied/adapted ASGK-derived material | no | source release review, target-repo license handling, install-surface review | `lane_07_docs_handoff` |
| `AGENTS.md` | canonical | agent startup order, generic operating profile, exactly 13 task-identity fields, execution-gate boundary, source-of-truth rule, work-unit rule, and stop conditions | yes | all agent sessions | `lane_00_controller` |
| `docs/handoff/CURRENT_STATUS.md` | status | compact current repo snapshot and next safe work | yes | all new sessions, handoff recovery, handoff updates | `lane_07_docs_handoff` |
| selected live GitHub issue, or a self-contained open PR | canonical | current executable authorization, 13 task fields, context read set, project-specific validation, acceptance, allowed paths, and merge state; an ordinary PR relies on its linked issue instead of duplicating authority | yes | every work unit | active task lane |
| `docs/QUICKSTART.md` | summary | first-use workflow, onboarding, and frontier-guided target-assessment orientation | no | onboarding and first repository smoke test | `lane_07_docs_handoff` |
| `docs/INSTALL_SURFACE.md` | canonical | frontier-guided read-only target assessment, evaluator/Skill/tool boundaries, invariants, license handling, and minimum sufficient adaptation | no | assessing ASGK adoption or a material upgrade, target evidence review, implementation planning after an assessment | `lane_07_docs_handoff` |
| `docs/SKILL_PACK.md` | summary | ASGK skill usage modes, guided evidence and judgment contract, maintenance touchpoints, and no-new-gates constraint | no | installing or referencing ASGK skills, reviewing architecture-to-skill impact, field testing, target adoption or upgrade assessment | `lane_07_docs_handoff` |
| `docs/DOCUMENT_REGISTRY.md` | canonical | complete repo-local document registry | no | canonical ownership lookup, registry repair, document-map split work | `lane_07_docs_handoff` |
| `docs/control/DOCUMENT_MAP_POLICY.md` | canonical | document-map router/registry split, size limits, and maintenance rules | no | document-map structure changes, registry split work, target-template navigation changes | `lane_07_docs_handoff` |
| `docs/EVOLUTION_MODEL.md` | historical_evidence | superseded pre-2.0 evolution and maturity framing; not current ASGK 2.0 authority | no | auditing or removing superseded evolution material | `lane_07_docs_handoff` |

## Target Assessment And Optional References

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `templates/DOCUMENT_MAP.template.md` | template | optional target-project navigation reference when assessment finds no equivalent surface | no | assessment recommends creating a target-owned compact router | `lane_07_docs_handoff` |
| `templates/DOCUMENT_REGISTRY.template.md` | template | optional target-project ownership-registry reference when assessment finds no equivalent surface | no | assessment recommends creating a target-owned registry | `lane_07_docs_handoff` |
| `templates/decision_packet.template.yaml` | historical_evidence | superseded parallel decision-packet projection awaiting W6B removal; not current authority | no | bounded W6B migration lookup only | `lane_07_docs_handoff` |

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
| `skills/asgk-target-install-audit/SKILL.md` | skill | frontier-guided read-only target-adoption assessment procedure | no | evaluating ASGK fit, minimum sufficient adaptation, or no-adoption outcome in another repository | `lane_07_docs_handoff` |
| `skills/asgk-upgrade-audit/SKILL.md` | skill | frontier-guided read-only comparison of newer ASGK guidance with target-owned governance | no | evaluating a material ASGK upgrade or deciding that no target change is needed | `lane_07_docs_handoff` |
| `skills/asgk-governance-health-check/SKILL.md` | skill | periodic governance drift health-check procedure | no | weekly review, milestone review, or public/customer handoff | `lane_07_docs_handoff` |

Optional-reference rule:

```yaml
reference_scope:
  asgk_repo_local_router: docs/DOCUMENT_MAP.md
  asgk_repo_local_registry: docs/DOCUMENT_REGISTRY.md
  optional_target_router_reference: templates/DOCUMENT_MAP.template.md
  optional_target_registry_reference: templates/DOCUMENT_REGISTRY.template.md
rule:
  - do not copy ASGK's repo-local router or registry unchanged into a target project
  - reuse equivalent target-owned mechanisms when they already satisfy the need
  - use a template only when the assessment identifies a real gap
  - do not prescribe ASGK filenames or a universal document bundle
```

## Handoff And Recovery Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/control/CURRENT_STATUS_POLICY.md` | canonical | current-status overwrite, compaction, stale-status, PR status freshness gate, and size rules | no | current-status update, stale status repair, handoff policy work, PR current-status impact review | `lane_07_docs_handoff` |
| `docs/control/HANDOFF_PACKET.md` | canonical | one typed work-unit handoff core, validation status, recovery stop conditions, and proof boundary | no | interruption, model switch, tool switch, handoff recovery, `asgk.py handoff-check` | `lane_00_controller` |
| `docs/control/COMPACT_HANDOFF_PROFILE.md` | conditional | canonical handoff-core projection plus CURRENT_STATUS impact and freshness checks | no | compact handoff or CURRENT_STATUS freshness validation | `lane_00_controller` |
| `schemas/handoff_packet.schema.json` | schema | machine-readable core handoff and compact-projection shape | no | handoff schema, validator, or fixture work | `lane_02_schema_contracts` |
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
  compact_projection: docs/control/COMPACT_HANDOFF_PROFILE.md
  schema_projection: schemas/handoff_packet.schema.json
  recovery_context: docs/control/CONTEXT_BUDGET_POLICY.md
  source_of_truth_rule: AGENTS.md
```

## Superseded Adapter Planning Artifacts

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/adapters/README.md` | historical_evidence | superseded adapter-mechanism planning context; not current ASGK 2.0 direction | no | auditing or removing superseded adapter planning | `lane_01_architecture` |
| `docs/adapters/ADAPTER_TEMPLATE.md` | historical_evidence | superseded runtime-adapter template context; not current ASGK 2.0 direction | no | auditing or removing superseded adapter planning | `lane_01_architecture` |

The runtime-adapter/profile roadmap is superseded. These files are not product
direction, adoption prerequisites, or default context; their later removal is a
separately scoped cleanup.

## Control Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/control/CONTROL_LAYER_V0.md` | historical_evidence | superseded duplicate operating-rule surface awaiting W6B removal; cannot override `AGENTS.md` | no | bounded W6B migration lookup only | `lane_00_controller` |
| `docs/control/WORK_UNIT_STATE_MODEL.md` | historical_evidence | superseded duplicate work-unit model awaiting W6B removal; cannot override live issue/PR authority | no | bounded W6B migration lookup only | `lane_00_controller` |
| `docs/control/ISSUE_HYGIENE_GATE.md` | canonical | stale issue detection and issue-start gate | no | before selecting or closing issues | `lane_00_controller` |
| `docs/control/FAILURE_THRESHOLDS.md` | canonical | stop thresholds and notification conditions | no | repeated failures, blockers | `lane_00_controller` |
| `docs/control/CONTEXT_BUDGET_POLICY.md` | canonical | exact context-read gate, advisory read-set classifications, handoff recovery read set, and recorded expansion rules | no | context selection, handoff recovery, token-budget review | `lane_00_controller` |
| `docs/control/AGENT_CAPABILITY_MATRIX.md` | canonical | task risk and minimum capability, including the frontier-capability floor for target adoption and material-upgrade assessment; low-risk merge compatibility, human gates, escalation/downscope, and context binding | no | task risk review, target adoption or material-upgrade assessment, escalation, downscoping, merge eligibility review | `lane_00_controller` |
| `docs/control/VALIDATION_STRATEGY.md` | canonical | common JSON evidence envelope, validation proof boundaries, result and human-gate semantics, validation-layer responsibilities, negative-fixture ownership rules, fail-closed policy-gate validation, and validator change requirements | no | validation/tooling work, policy-gate checker review | `lane_06_ci_github` |
| `docs/control/PR_REVIEW_CHECKLIST.md` | canonical | repeatable PR review sequence, current-status freshness review, and outcomes | no | PR review, current-status impact review, merge readiness | `lane_00_controller` |
| `docs/control/NEGATIVE_TEST_PLAN.md` | canonical | human-readable negative-case intent, risk classification, candidate fixture paths, and planned gaps; not executable scenario expectations | no | negative fixture or validator work | `lane_00_controller` |
| `docs/control/UNCONTROLLED_DOCUMENT_AUDIT.md` | canonical | uncontrolled-document growth-risk classification and audit record | no | uncontrolled-document audit or status-like document growth review | `lane_07_docs_handoff` |
| `docs/control/HISTORICAL_ASGK_READINESS_EVIDENCE.md` | historical_evidence | archived ASGK source-only readiness evidence and first-release decision trail | no | auditing old ASGK readiness decisions or target source-state isolation | `lane_07_docs_handoff` |
| `docs/control/HISTORICAL_ASGK_STABILIZATION_EVIDENCE.md` | historical_evidence | archived ASGK early stabilization evidence and field-test lesson record | no | auditing old ASGK stabilization decisions or target source-state isolation | `lane_07_docs_handoff` |
| `docs/control/SOURCE_ONLY_RELEASE_POLICY.md` | canonical | Source-only release gates, human-gated release execution boundary, distribution boundary, version applicability, and release-history source-of-truth boundary | no | source-only release planning, release execution review, release-state closeout, distribution-boundary review | `lane_07_docs_handoff` |
| `docs/control/DOCUMENT_MAP_POLICY.md` | canonical | document-map router/registry split, size limits, and maintenance rules | no | document-map structure changes, registry split work, target-template navigation changes | `lane_07_docs_handoff` |
| `docs/control/DECISION_POINT_REGISTRY.md` | historical_evidence | superseded parallel decision router awaiting W6B removal; cannot expand the current issue read set or authority | no | bounded W6B migration lookup only | `lane_07_docs_handoff` |
| `docs/control/TARGET_INSTALL_CHECKLIST.md` | canonical | target-assessment questions, existing-control comparison, minimum sufficient adaptation, evidence, uncertainty, and outcome conditions | no | target adoption or material-upgrade assessment, target issue preparation | `lane_07_docs_handoff` |
| `docs/control/TARGET_INSTALL_VALIDATION_PLAN.md` | canonical | semantic-assessment versus mechanical-check proof boundaries, caller-supplied target claims, and legacy command limitations | no | target evidence review, checker behavior review, or legacy cutover work | `lane_06_ci_github` |

Capability matrix boundary rule:

```yaml
agent_capability_matrix_binding_for:
  - task risk classification
  - minimum intelligence level
  - frontier-capability floor for target adoption and material-upgrade assessment
  - low-risk merge compatibility
  - existing human-gate requirement
  - escalation and downscope decisions
  - context read-set binding
not_binding_for:
  - evaluator, model, provider, or price-tier selection
  - automatic model routing or switching
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
| `docs/bootstrap/10_roadmap.md` | historical_evidence | v1 milestone history and superseded runtime-adapter roadmap framing; not current ASGK 2.0 authority | no | release-history audit or removal of superseded roadmap material | `lane_00_controller` |
| `docs/bootstrap/12_productization_notes.md` | historical_evidence | superseded productization and v1.x/v2.0 roadmap framing; not current ASGK 2.0 authority | no | auditing or removing superseded roadmap material | `lane_07_docs_handoff` |
| `docs/bootstrap/13_artifact_promotion_policy.md` | summary | promotion chain overview and status values | no | artifact/data/evidence-heavy work | `lane_02_schema_contracts` |
| `docs/bootstrap/14_execution_lanes.md` | canonical | execution lanes and external-call boundaries | no | execution lane/API/provider discussions | `lane_05_security` |
| `docs/bootstrap/15_source_or_input_class_matrix.md` | optional module | source/input class use boundaries | no | evidence, source, claim, or context-pack projects | `lane_02_schema_contracts` |
| `docs/bootstrap/16_downstream_promotion_matrix.md` | optional module | downstream artifact eligibility | no | artifact promotion or output eligibility work | `lane_02_schema_contracts` |
| `docs/bootstrap/17_readiness_audit_policy.md` | canonical | readiness audit before output, API, import, publication, or external calls | no | API/model/provider/output readiness changes | `lane_05_security` |

## Task Packet And Report Documents

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `docs/control/TASK_PACKET_FORMAT.md` | canonical | the two optional task-packet modes and their projection/proof boundaries | no | creating or validating a task packet | `lane_00_controller` |
| `schemas/task_packet.schema.json` | schema | machine-readable projection of the two task-packet modes | no | task-packet schema or validator changes | `lane_02_schema_contracts` |
| `templates/task_packet.template.yaml` | template | optional issue-refinement starting point derived from the task-packet contract | no | creating an issue-refinement packet | `lane_00_controller` |
| `.github/ISSUE_TEMPLATE/agent_task.yml` | template | GitHub issue authority-capture projection for the 13 fields plus two execution gates | no | issue-template or work-unit authority changes | `lane_06_ci_github` |
| `examples/task_packet.example.yaml` | example | sample GitHub-unavailable fallback; conditional local-work scope only, never PR or merge authority | no | onboarding, task-packet examples | `lane_07_docs_handoff` |
| `docs/control/AGENT_REPORT_FORMAT.md` | canonical | required agent report sections | no | PR handoff/reporting work | `lane_00_controller` |
| `schemas/agent_report.schema.json` | schema | machine-readable report fields | no | report validation work | `lane_02_schema_contracts` |
| `examples/agent_report.example.md` | example | sample report | no | onboarding, report examples | `lane_07_docs_handoff` |

Canonical ownership rule for task packets:

```yaml
task_identity_owner: AGENTS.md
executable_authority_owner: current GitHub issue or PR
task_packet_mode_owner: docs/control/TASK_PACKET_FORMAT.md
task_packet_schema_projection: schemas/task_packet.schema.json
task_packet_template_projection: templates/task_packet.template.yaml
issue_capture_projection: .github/ISSUE_TEMPLATE/agent_task.yml
task_packet_example_projection: examples/task_packet.example.yaml
scope_comparison_engine: python3 scripts/asgk.py task-packet-check
compact_task_packet_command: delegates to scope_comparison_engine
```

## Contracts And Schemas

| Path | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `contracts/*.yaml` | contract | semantic contract rules and invariants | no | contract, schema, validation, artifact work | `lane_02_schema_contracts` |
| `schemas/*.json` | schema | machine-readable validation structures | no | schema validation, fixtures, tooling | `lane_02_schema_contracts` |
| `contracts/validation_result.contract.yaml` | contract | common validation-result meaning, invariants, and proof limit | no | retained JSON validator or evidence-envelope changes | `lane_02_schema_contracts` |
| `schemas/validation_result.schema.json` | schema | machine-readable common validation-result envelope and finding shape | no | retained JSON validator, scenario, or schema changes | `lane_02_schema_contracts` |

Contracts explain intent and invariants. Schemas enforce structure. If they
disagree, stop and open a schema/contract alignment issue.

## Scripts And CI

| Document | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `scripts/check_project.py` | historical_evidence | superseded directory-existence-only checker awaiting W6D removal; not active source-validation orchestration | no | bounded W6D removal evidence only | `lane_06_ci_github` |
| `scripts/asgk_lib/source_validation.py` | script | sole retained ASGK source required-set and source-check engine, including explicit validator/inspected-root provenance, trusted-source execution boundary, and supplied source-inventory proof boundaries | no | source validation, doctor, compatibility-wrapper, or source inventory work | `lane_06_ci_github` |
| `scripts/asgk_lib/target_evidence.py` | script | sole meaning owner for read-only caller-supplied target path/text claims, stable target-evidence findings, result mapping, and proof boundary; owns no target shape or recommendation | no | target adoption/upgrade assessment evidence, target-evidence validation, or legacy cutover review | `lane_06_ci_github` |
| `scripts/validate_bootstrap.py` | script | thin compatibility projection to `scripts/asgk_lib/source_validation.py`; owns no required list, rule, fixture expectation, or orchestration | no | compatibility-entrypoint validation or later bounded removal review | `lane_06_ci_github` |
| `scripts/governance_hygiene.py` | script | changed-path and protected-path hygiene | no | path hygiene, negative changed-path checks, future CLI work | `lane_06_ci_github` |
| `scripts/policy_gate_check.py` | script | read-only fail-closed PR-body policy gate check without low-risk inference | no | policy-gate validation, PR-body gate coherence review | `lane_06_ci_github` |
| `scripts/asgk_lib/validation_result.py` | script | dependency-free common envelope construction and fail-closed self-validation | no | retained JSON command, finding, result, or proof-boundary changes | `lane_06_ci_github` |
| `scripts/asgk_lib/scenario_registry.py` | script | sole executable owner of retained JSON owner commands, including target evidence, polarity, exact exits, results, finding-code multisets, human-gate states, proof boundaries, optional branch-specific checked/unchecked claims, task-packet alias parity, and source-wrapper parity | no | validator behavior, negative coverage, doctor, or CI scenario changes | `lane_06_ci_github` |
| `scripts/asgk_lib/scenario_runner.py` | script | exact scenario execution, one-JSON-object verification, alias parity, and false-evidence self-tests | no | validator evidence or scenario-runner changes | `lane_06_ci_github` |
| `scripts/asgk_lib/negative.py` | script | thin public negative-command facade over the canonical scenario owner and legacy bounded groups | no | negative CLI routing or compatibility review | `lane_06_ci_github` |
| `scripts/asgk_lib/negative_cases.py` | script | compatibility projection to `scenario_registry.py`; owns no expectation | no | bounded compatibility removal or regression review | `lane_06_ci_github` |
| `scripts/asgk_lib/negative_runner.py` | script | compatibility projection to `scenario_runner.py`; owns no execution semantics | no | bounded compatibility removal or regression review | `lane_06_ci_github` |
| `scripts/asgk.py` | script | ASGK CLI facade for canonical source validation, caller-supplied target evidence, common retained-JSON projections, and legacy fixed-shape target-install diagnostics; no mechanical target command owns fit, depth, recommendation, or approval | no | local source validation, target evidence, status/closeout/handoff/PR checks, policy-gate checks, or bounded legacy diagnostics | `lane_06_ci_github` |
| `scripts/pr_governance_preflight.py` | script | thin file-backed PR body preflight before `gh pr create` or `gh pr edit` | no | PR body create/edit, local preflight before GitHub Actions, target adoption of ASGK CLI tooling | `lane_06_ci_github` |
| `scripts/target_install_plan.py` | script | standalone legacy fixed-shape target-install observation plan; not an adoption recommendation or readiness proof | no | bounded legacy regression or clean-cutover review | `lane_06_ci_github` |
| `.github/workflows/bootstrap-validation.yml` | template/script | GitHub Actions projection of doctor plus dynamic PR-event policy routing and changed-path hygiene; owns no duplicate fixture list | no | CI/workflow changes | `lane_06_ci_github` |
| `.github/PULL_REQUEST_TEMPLATE.md` | template | required PR body sections, Current Status Impact, and Merge Decision Record surface | no | PR creation/review, current-status impact classification, template changes, `asgk.py pr-body-check` | `lane_06_ci_github` |

## Examples And Fixtures

| Path | Role | Canonical for | Read by default | Read when | Owned by lane |
|---|---|---|---:|---|---|
| `examples/README.md` | summary | examples and fixture taxonomy, adoption boundary, and read boundary | no | onboarding, examples/fixture cleanup, target-adoption review | `lane_07_docs_handoff` |
| `examples/*.json` | example/fixture | valid sample payloads or machine fixtures | no | onboarding, validator examples, fixture design | `lane_07_docs_handoff` |
| `examples/*.yaml` | example/fixture | valid sample task packets or machine fixtures | no | onboarding, task packet examples, fixture design | `lane_07_docs_handoff` |
| `examples/*.md` | example/fixture | report, PR-body, or documentation examples and fixtures | no | onboarding, report examples, parser fixture design | `lane_07_docs_handoff` |
| `examples/negative/*` | fixture | opt-in expected-failure inputs whose executable expectations belong to `scenario_registry.py` or an explicitly bounded legacy group | no | negative validation work, `asgk.py negative`, governance hygiene tests | `lane_02_schema_contracts` |
| `examples/negative/policy_gate/*` | fixture | opt-in expected-failure PR-body policy-gate fixtures | no | policy-gate negative validation work | `lane_06_ci_github` |
| `examples/source_validation/reference-superset.valid.json` | fixture | positive caller-supplied retained source-path inventory; proves membership only and does not inspect listed files | no | source-validation scenario or required-set changes | `lane_06_ci_github` |
| `examples/negative/source_validation/missing-required-path.json` | fixture | source inventory missing exactly one retained canonical path for exact `SV_REQUIRED_PATH_MISSING` coverage | no | source-validation negative scenario changes | `lane_06_ci_github` |
| `examples/target_evidence/arbitrary_layout/notes/project.marker` | fixture | positive arbitrary-layout target marker for all four caller-claim kinds; contains no ASGK-named target surface | no | target-evidence positive scenario or proof-boundary review | `lane_06_ci_github` |
| `examples/negative/target_evidence/mismatched_claims/notes/project.marker` | fixture | paired target marker producing the four exact target-evidence mismatch findings | no | target-evidence mismatch scenario changes | `lane_06_ci_github` |
| `examples/negative/target_install/*` | fixture | legacy target-install shape-check expected-failure fixtures | no | maintaining current mechanical diagnostics or planning their replacement | `lane_06_ci_github` |

Examples and fixtures are not policy authority. If an example or fixture
conflicts with a canonical policy, contract, schema, validator, or current
GitHub issue/PR, fix the example or the stale reference.

## Registry Rules

1. Add new document rows here after the split is complete.
2. Keep `docs/DOCUMENT_MAP.md` as a compact router.
3. Do not add context read-set definitions here; use
   `docs/control/CONTEXT_BUDGET_POLICY.md`.
4. Do not add target-assessment or optional-reference rules here; use
   `docs/INSTALL_SURFACE.md`.
5. If this registry conflicts with a canonical document, fix the registry or the
   stale summary in a separate issue.
