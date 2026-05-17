# Decision Point Registry

Status: active vertical-governance registry.

This document is a thin router for major ASGK decision points. It does not
replace canonical policy documents. It tells humans and agents when a decision
packet is required, which canonical documents to read, what evidence is needed,
and which stop conditions apply.

## Purpose

Horizontal governance answers:

```text
issue -> branch -> PR -> CI -> merge decision -> handoff
```

Vertical governance answers:

```text
What kind of decision is this?
What evidence is required?
Who has authority?
When must the agent stop?
What rollback or next safe action is required?
```

Use this registry to make major decision points resumable, reviewable, and
portable across projects that adopt ASGK.

## Non-goal

This registry must not become a parallel policy system. Each decision point must
link to existing canonical policy documents instead of duplicating their full
rules.

```yaml
non_goals:
  - one policy document per decision type
  - duplicate policy text from canonical documents
  - runtime-specific subagent orchestration
  - vendor-specific profile routing
  - automatic approval
  - decision-check tooling in v1 of this layer
```

## When To Use A Decision Packet

Use `templates/decision_packet.template.yaml` when a task reaches a decision
point that changes authority, risk, scope, installation state, release state,
external capability, or rollback expectations.

```yaml
use_decision_packet_when:
  - merge authority is being exercised
  - low-risk auto-merge is considered
  - human-gated operation is considered
  - dependency or toolchain is changed
  - schema or contract compatibility is broken
  - target-install scaffold or file-writing installer behavior is considered
  - runtime adapter or profile work is activated
  - external API, model, cloud, or MCP capability is enabled
  - release or publication readiness is decided
  - storage or protected-path boundary changes
```

A decision packet is not required for routine docs-only edits where the GitHub
issue, PR body, validation evidence, and Merge Decision Record already capture
the full decision.

## Authority Order

When decision records disagree, use this authority order unless a more specific
canonical document says otherwise:

```yaml
authority_order:
  active_github_issue: highest_for_task_scope_and_allowed_paths
  canonical_repo_policy: highest_for_governance_rule
  active_pr_body: highest_for_current_change_summary_and_merge_decision
  decision_packet: highest_for_recorded_decision_inputs_evidence_and_next_safe_action
  docs_handoff_CURRENT_STATUS_md: compact_resume_surface_only
  examples: non_authoritative
  chat: non_authoritative
```

If authority conflict is material, stop and open or update a governance issue.
Do not silently choose the larger scope or more permissive interpretation.

## Common Decision Packet Fields

Every decision packet should capture:

```yaml
common_fields:
  - decision_type
  - lifecycle_position
  - durable_source_of_truth
  - canonical_documents
  - required_inputs
  - evidence
  - authority
  - allowed_actions
  - forbidden_actions
  - stop_conditions
  - rollback_plan
  - next_safe_action
  - human_gate
  - validation
```

## Decision Point Table

| Decision type | Lifecycle position | Minimum level | Human gate | Canonical documents | Required evidence | Stop conditions |
|---|---|---:|---:|---|---|---|
| `merge_decision` | `pre_merge` | `standard` | maybe | `docs/control/MERGE_DECISION_RECORD.md`, `docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md`, `.github/PULL_REQUEST_TEMPLATE.md` | PR body, changed files, CI status, issue allowed paths | checks pending, MDR incomplete, changed files outside allowed paths |
| `low_risk_auto_merge_decision` | `pre_merge` | `advanced` | no if all gates pass | `docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md`, `docs/control/HUMAN_GATED_OPERATIONS.md` | all low-risk gates, no human-gated operation, clean runtime artifact boundary | any gate unknown, human gate detected, unresolved review |
| `human_gated_operation_decision` | `issue_scoping` or `implementation` | `frontier` | yes | `docs/control/HUMAN_GATED_OPERATIONS.md`, `docs/control/AGENT_CAPABILITY_MATRIX.md` | explicit approval source, risk, rollback plan | approval missing, rollback unclear, protected path involved |
| `dependency_addition_decision` | `issue_scoping` | `frontier` | yes | `docs/bootstrap/03_tech_stack.md`, `docs/control/HUMAN_GATED_OPERATIONS.md` | rationale, dependency name/version, license/security note, rollback plan | dependency not authorized, license unknown, no rollback |
| `schema_breaking_change_decision` | `issue_scoping` or `implementation` | `frontier` | yes | `docs/bootstrap/07_contract_first.md`, `schemas/*`, `contracts/*`, `docs/control/AGENT_CAPABILITY_MATRIX.md` | breaking-change rationale, migration plan, affected examples/tests | migration absent, contract/schema mismatch unresolved |
| `target_install_scaffold_decision` | `target_install` | `frontier` | yes | `docs/INSTALL_SURFACE.md`, `docs/control/TARGET_INSTALL_CHECKLIST.md`, `docs/control/TARGET_INSTALL_VALIDATION_PLAN.md` | target-install plan output, target-install-check output, explicit approval | plan not reviewed, blocking findings exist, file-writing scope unclear |
| `runtime_adapter_profile_decision` | `roadmap` or `v2_0` | `frontier` | yes | `docs/adapters/README.md`, `profiles/PROFILE_SPEC.md`, `docs/DOCUMENT_REGISTRY.md` | vendor docs, observed tests, adapter boundary, non-bypass claim | vendor docs missing, runtime behavior unverified, core governance bypassed |
| `external_api_or_mcp_enablement_decision` | `issue_scoping` | `frontier` | yes | `docs/bootstrap/14_execution_lanes.md`, `docs/bootstrap/17_readiness_audit_policy.md`, `docs/control/HUMAN_GATED_OPERATIONS.md` | capability request, data boundary, egress/write risk, rollback | live external call without gate, MCP write capability, private data risk |
| `release_or_publication_decision` | `release` | `frontier` | yes | `docs/control/SOURCE_ONLY_RELEASE_POLICY.md`, `docs/bootstrap/17_readiness_audit_policy.md`, `docs/control/HUMAN_GATED_OPERATIONS.md` | current release policy, current readiness evidence, known gaps, rollback/revoke plan | current issue lacks release authority, readiness evidence missing, unresolved blockers |
| `storage_boundary_change_decision` | `issue_scoping` or `implementation` | `frontier` | yes | `docs/architecture/STORAGE_PROFILE.md`, `docs/architecture/RUNTIME_ARTIFACT_POLICY.md`, `docs/control/HUMAN_GATED_OPERATIONS.md` | path boundary diff, artifact/local-state impact, rollback plan | protected path changed, Artifact Root unclear, Local State Root risk |

## Relationship To Existing Control Documents

```yaml
relationships:
  agent_capability_matrix:
    role: supplies minimum level, low-risk merge compatibility, and human-gate relationship
  context_budget_policy:
    role: supplies read set and context expansion rules for decision-point work
  document_registry:
    role: supplies canonical ownership rows for decision documents
  merge_decision_record:
    role: remains canonical for PR merge decision format
  target_install_validation_plan:
    role: remains canonical for target-install checker/planner behavior
```

## Maintenance Rules

1. Add new decision types here only when the decision is cross-cutting and likely
   to recur across projects.
2. Do not add a new decision type when an existing canonical document already
   handles it without ambiguity.
3. Keep each decision row short and link to canonical documents instead of
   repeating full policy text.
4. If a decision type requires machine enforcement, create a separate tooling
   issue after the registry and template prove stable.
5. If this registry exceeds useful size, split examples into an examples file;
   do not create one policy document per decision type.
