# Agent Capability Matrix

Status: active control policy.

This document maps task types to the minimum acceptable agent intelligence
level, sub-agent eligibility, low-risk merge eligibility, human-gate
requirements, and context profile. It exists to prevent agents from treating all
work as the same risk class.

## Relationship To Other Documents

Canonical related sources:

```yaml
agent_level_definitions: agent/agent_rules.yaml
context_profiles: docs/control/CONTEXT_BUDGET_POLICY.md
low_risk_merge: docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
human_gates: docs/control/HUMAN_GATED_OPERATIONS.md
document_ownership: docs/DOCUMENT_MAP.md
```

If this matrix conflicts with `agent/agent_rules.yaml`, stop and open a
controller issue. Do not silently choose the more permissive rule.

## Intelligence Levels

| Level | Intended use | Must not do |
|---|---|---|
| `fast_basic` | mechanical search, inventory, formatting checks, typo fixes, small docs extraction | code changes, policy interpretation, schema work, security review |
| `standard` | narrow implementation, focused tests, UI polish, bounded docs updates | cross-module design, dependency changes, security-boundary changes |
| `advanced` | multi-file implementation, tricky debugging, adapter integration, nontrivial tests, UX workflows | final policy authority, final security gate, high-risk merge authority |
| `frontier` | architecture review, security-sensitive analysis, merge-risk review, parser/model planning, ambiguous tradeoffs | routine mechanical work when lower levels suffice |

## Matrix Columns

```yaml
columns:
  task_type: "Class of work."
  minimum_level: "Lowest acceptable intelligence level."
  subagent_allowed: "Whether the work may be assigned to a worker/sub-agent."
  low_risk_merge_possible: "Whether low-risk autonomous merge may apply if all gates pass."
  human_gate_required: "Whether explicit human approval is required before merge or implementation."
  context_profile: "Required profile from CONTEXT_BUDGET_POLICY.md."
  notes: "Extra constraints."
```

## Capability Matrix

| Task type | Minimum level | Sub-agent allowed | Low-risk merge possible | Human gate required | Context profile | Notes |
|---|---:|---:|---:|---:|---|---|
| typo / formatting in docs | `fast_basic` | yes | yes | no | `docs_only` | Must stay inside allowed paths. |
| small docs extraction or inventory | `fast_basic` | yes | no PR unless output committed | no | `docs_only` | Report output; avoid policy interpretation. |
| handoff status update | `standard` | yes | yes | no | `docs_only` | Must update only handoff/status files named by issue. |
| Quickstart / onboarding docs | `standard` | yes | yes | no | `docs_only` | No policy semantics change. |
| document map update | `standard` | yes | yes | no unless changing canonical ownership for security/merge | `control_policy` | Must not delete or consolidate docs in same work unit. |
| context budget policy update | `standard` | yes | yes if additive/clarifying | maybe | `control_policy` | Semantic tightening can be low-risk; semantic loosening requires review. |
| task packet example update | `standard` | yes | yes | no | `docs_only` | Must remain consistent with schema and task format. |
| issue template wording update | `standard` | yes | maybe | no unless required fields change | `tooling_or_validation` | Required-field changes may affect validation and need advanced review. |
| PR template wording update | `standard` | yes | maybe | no unless merge fields change | `tooling_or_validation` | Merge Decision Record changes escalate. |
| agent report format update | `standard` | yes | maybe | no if additive | `control_policy` | Removing sections escalates to frontier. |
| validation strategy docs | `standard` | yes | yes if docs-only | no | `tooling_or_validation` | Script behavior changes are separate. |
| negative test plan docs | `standard` | yes | yes | no | `tooling_or_validation` | Adding actual failing fixtures may require advanced. |
| governance hygiene script change | `advanced` | yes | maybe | no if narrow and tests pass | `tooling_or_validation` | Must include examples or test evidence. |
| validate_bootstrap.py change | `advanced` | yes | maybe | no if stricter/additive | `tooling_or_validation` | Loosening validation requires human review. |
| check_project.py change | `advanced` | yes | maybe | no if stricter/additive | `tooling_or_validation` | Avoid hidden dependencies. |
| GitHub Actions workflow change | `advanced` | yes | maybe | maybe | `tooling_or_validation` | Permission or external action expansion requires human gate. |
| schema fixture addition | `advanced` | yes | maybe | no if valid and scoped | `schema_or_contract` | Must not imply schema semantics change. |
| schema minor additive change | `advanced` | yes | maybe | maybe | `schema_or_contract` | Must be backward-compatible and tested. |
| schema breaking change | `frontier` | no final authority | no | yes | `schema_or_contract` | Explicit issue and migration/rollback plan required. |
| contract clarification | `advanced` | yes | maybe | no if non-semantic | `schema_or_contract` | Must align examples and schemas if current behavior changes. |
| contract semantic change | `frontier` | no final authority | no | yes | `schema_or_contract` | Requires architecture review. |
| storage profile clarification | `advanced` | yes | maybe | no if stricter/additive | `security_or_storage` | Must preserve three-root model. |
| storage boundary expansion | `frontier` | no final authority | no | yes | `security_or_storage` | Human-gated. |
| protected path policy change | `frontier` | no final authority | no | yes | `security_or_storage` | Never solo auto-merge. |
| runtime artifact policy change | `advanced` | yes | maybe | maybe | `security_or_storage` | Loosening commit boundaries is human-gated. |
| merge policy clarification | `frontier` | no final authority | no | yes if authority changes | `merge_decision` | Requires reviewer distinct from implementer. |
| low-risk merge gate loosening | `frontier` | no | no | yes | `merge_decision` | Human-gated by default. |
| human-gated operation list change | `frontier` | no final authority | no | yes | `merge_decision` | Adding gates may be safer; removing gates requires explicit approval. |
| dependency addition | `frontier` | no final authority | no | yes | `tooling_or_validation` | Requires rationale, license/security review, rollback plan. |
| parser/model dependency | `frontier` | no final authority | no | yes | `promotion_or_output_readiness` | Human-gated. |
| cloud/API lane addition | `frontier` | no final authority | no | yes | `promotion_or_output_readiness` | Requires explicit live-call gate and audit metadata. |
| MCP tool addition | `frontier` | no final authority | no | yes | `security_or_storage` | MCP write capability is always human-gated. |
| release/publication decision | `frontier` | no | no | yes | `promotion_or_output_readiness` | Never low-risk autonomous merge. |
| CLI wrapper initial implementation | `advanced` | yes | maybe | no if wraps existing scripts only | `tooling_or_validation` | New dependencies escalate. |
| CLI command that writes files | `frontier` | no final authority | no unless explicitly scoped | yes if destructive or broad | `tooling_or_validation` | Requires dry-run and path boundary checks. |
| productization positioning docs | `standard` | yes | yes | no | `docs_only` | No release decision. |
| roadmap planning | `advanced` | yes | no merge unless docs-only and scoped | maybe | `control_policy` | Future-only work must be labeled. |
| multi-agent lane dispatch | `frontier` | controller only | no by itself | maybe | `multi_agent_or_lane` | Worker tasks still need durable packets. |

## Escalation Rules

Escalate to a higher level when any of these are true:

```yaml
escalate_when:
  - task crosses more than one top-level directory group
  - task changes validation behavior
  - task changes merge authority
  - task changes human-gated operations
  - task changes security or storage boundaries
  - task adds dependency or external action
  - task touches schema semantics
  - task opens cloud/API/model/MCP capability
  - task has ambiguous tradeoffs
  - task requires rollback planning
```

If escalation is required but not authorized by the issue, stop and report.

## Downscoping Rules

Downscope instead of escalating when the high-risk part is separable.

```yaml
downscope_examples:
  - create docs-only plan now, defer script changes to a tooling issue
  - add negative test plan now, defer executable fixtures to a validation issue
  - clarify storage summary now, defer storage boundary change to a security issue
  - update quickstart now, defer CLI wrapper to a tooling issue
```

A downscoped PR must explicitly list deferred work in `Known Gaps`.

## Sub-agent Rules

Sub-agents may perform bounded work only when all required assignment fields are
present:

```yaml
subagent_assignment_required_fields:
  - lane
  - intelligence_level
  - intelligence_level_reason
  - durable_source_of_truth
  - allowed_paths
  - expected_output
  - plan
  - checklist
  - acceptance_sheet
  - stop_conditions
  - rollback_expectations
```

Sub-agents must not be final authority for:

- security gates;
- merge authority changes;
- human-gated operation changes;
- schema breaking changes;
- storage boundary expansion;
- new dependencies;
- cloud/API/MCP enablement;
- release or publication decisions.

## Low-risk Merge Compatibility

Low-risk autonomous merge may apply only when:

1. The matrix marks the task as low-risk merge possible.
2. `docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md` passes.
3. `docs/control/HUMAN_GATED_OPERATIONS.md` does not require explicit approval.
4. GitHub Actions pass.
5. The PR body includes a complete Merge Decision Record.
6. The changed files match the issue allowed paths.
7. No runtime artifacts or protected paths are touched.

If any condition is unknown, treat merge as blocked until verified.

## Human Gate Compatibility

When the matrix says `human_gate_required: yes`, the work may still be planned
or documented, but implementation or merge must stop until a durable approval
record exists.

Required approval record:

```yaml
human_gate:
  operation:
  reason:
  risks:
  rollback_plan:
  approval_source:
  approved_by:
  approved_at:
```

## Context Profile Binding

The `context_profile` column is binding. If a task uses a different profile, the
PR or Agent Report must include:

```yaml
context_profile_override:
  original_profile:
  used_profile:
  reason:
  additional_files_read:
```

## Review Checklist

Before completing a task, ask:

1. Is the minimum level sufficient for the actual work performed?
2. Did the task cross into a higher-risk category?
3. Are all sub-agent required fields present if a sub-agent was used?
4. Is low-risk merge allowed by both this matrix and the merge policy?
5. Does any human-gated operation apply?
6. Was the required context profile used or was an override recorded?
7. Are deferred high-risk items listed as known gaps?

## Maintenance Rule

When `agent/agent_rules.yaml` changes intelligence levels, roles, or forbidden
actions, update this matrix in the same PR or explicitly record why the matrix
remains valid.
