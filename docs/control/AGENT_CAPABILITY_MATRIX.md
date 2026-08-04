# Agent Capability Matrix

Status: active control policy.

This document classifies task risk and the minimum reasoning depth needed for
work under the generic ASGK governance flow. It does not assign agents, choose a
provider or model, route work, authorize platform-native subagents, or create a
human approval gate. A human selects the evaluator; the selected model and
client remain external to ASGK.

## Purpose

Use this matrix to decide:

- whether the current issue or PR scope is still appropriate;
- whether a human gate applies;
- whether low-risk autonomous merge can even be considered;
- which context read set is required.

`lane` and `intelligence_level` are task metadata. They do not create a second
source of authority and do not bypass GitHub issue-first work.

For an infrequent, high-impact ASGK adoption or material-upgrade assessment,
selecting frontier capability protects the evaluator's ability to reason from
the target repository's actual state. The relevant Skill guides attention,
evidence, boundaries, uncertainty, and stop behavior; it does not prescribe the
target architecture or recommendation.

## Related Sources

```yaml
context_read_sets: docs/control/CONTEXT_BUDGET_POLICY.md
low_risk_merge: docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
human_gates: docs/control/HUMAN_GATED_OPERATIONS.md
document_ownership: docs/DOCUMENT_MAP.md
```

If these sources conflict, stop and report the conflict.

## Intelligence Levels

| Level | Intended use | Must not do |
|---|---|---|
| `fast_basic` | mechanical search, inventory, formatting checks, typo fixes | code changes, policy interpretation, security review |
| `standard` | narrow implementation, focused tests, bounded docs updates | cross-module design, dependency changes, security-boundary changes |
| `advanced` | multi-file implementation, tricky debugging, nontrivial tests, UX workflows | final policy authority, final security gate, high-risk merge authority |
| `frontier` | architecture review, target adoption or material-upgrade assessment, security-sensitive analysis, merge-risk review, ambiguous tradeoffs | treating its judgment as implementation approval, mechanical proof, or authority to overwrite target state |

## Capability Matrix

| Task type | Minimum level | Low-risk merge possible | Human gate required | Context read set | Notes |
|---|---:|---:|---:|---|---|
| typo / formatting in docs | `fast_basic` | yes | no | `docs_only` | Must stay inside allowed paths. |
| small docs extraction or inventory | `fast_basic` | no PR unless output committed | no | `docs_only` | Avoid policy interpretation. |
| handoff status update | `standard` | yes | no | `docs_only` | Update only named status files. |
| quickstart / onboarding docs | `standard` | yes | no | `docs_only` | No policy semantics change. |
| document map or registry update | `standard` | yes | maybe | `control_policy` | Canonical ownership changes may escalate. |
| context budget policy update | `standard` | maybe | maybe | `control_policy` | Loosening read limits requires review. |
| task packet example/template update | `standard` | yes | no | `docs_only` | Must match schema and task format. |
| issue or PR template wording update | `standard` | maybe | maybe | `tooling_or_validation` | Required-field or merge-field changes escalate. |
| report format update | `standard` | maybe | no if clarifying | `control_policy` | Removing required evidence escalates. |
| validation docs or negative-test plan | `standard` | yes if docs-only | no | `tooling_or_validation` | Executable fixtures are separate validation work. |
| target ASGK adoption or material-upgrade assessment | `frontier` | not applicable; assessment is read-only | no for assessment; only for an exact existing gate triggered by proposed implementation | `control_policy` | Skill guides the assessment; the evaluator judges fit, depth, minimum change, or no change from target evidence. |
| validator or governance script change | `advanced` | maybe | maybe | `tooling_or_validation` | Must include test evidence. |
| GitHub Actions workflow change | `advanced` | maybe | maybe | `tooling_or_validation` | Permission or external action expansion is gated. |
| schema or contract clarification | `advanced` | maybe | no if non-semantic | `schema_or_contract` | Align examples and checks. |
| schema breaking change | `frontier` | no | yes | `schema_or_contract` | Migration and rollback required. |
| storage or runtime artifact policy change | `advanced` | maybe | maybe | `security_or_storage` | Boundary expansion is human-gated. |
| qualified program-scoped reversible protected source change | `frontier` | yes only under canonical policy plus exact current-issue authority | no only when current-head evidence proves no Human-Gated Operations item applies | `merge_decision` | Requires an OWNER-approved exact scope source, a child issue no broader than that source, tracked source only, no external side effect beyond routine issue/PR metadata, ordinary revert, independent review, CI, and strict `check-pr`; never describe the program grant as current-head human review. |
| other protected path, human-gate, program-eligibility, merge-policy, or merge-authority change | `frontier` | no | yes | `merge_decision` | Never solo auto-merge. A PR changing the program path cannot use the path it changes. |
| dependency, cloud/API, MCP, or model-call enablement | `frontier` | no | yes | `promotion_or_output_readiness` | Requires explicit gate and rollback. |
| release/publication decision | `frontier` | no | yes | `promotion_or_output_readiness` | Human-gated. |

## Frontier-Guided Adoption And Upgrade Assessment

For target adoption and material upgrade work:

- ASGK does not select, route, schedule, switch, price-tier, or orchestrate the
  evaluator.
- The assessment is read-only. Its recommendation is not implementation,
  approval, merge, or release authority.
- The Skill guides target discovery, evidence comparison, universal safety
  boundaries, alternatives, confidence, unknowns, and safe-stop behavior.
- The evaluator judges target fit, governance depth, minimum sufficient
  adaptation, and whether retaining the current target state is preferable.
- Deterministic tools provide bounded observations and invariant or concrete
  claim checks. They do not decide semantic completeness or target shape.
- Results belong in the target's existing issue, PR, or handoff lineage. Any
  later write requires a separately authorized target-owned work unit.
- Human approval is required only when the proposed implementation crosses a
  concrete existing human-gated operation.

## Escalation Rules

Escalate or stop when the actual work:

- crosses unrelated top-level areas;
- changes validation behavior, merge authority, human gates, storage/security
  boundaries, schema semantics, dependencies, external actions, or runtime
  capabilities;
- needs context outside the issue or PR allowed scope;
- has missing rollback expectations for a proposed implementation.

Ambiguous tradeoffs in a read-only frontier assessment do not by themselves
create a human gate. Record alternatives, confidence, unknowns, and the evidence
that could change the recommendation. Stop only when the evaluator cannot make
a responsible recommendation or the next action crosses a concrete existing
gate.

Downscope instead when the risky portion is separable, and list deferred work in
the PR `Known Gaps`.

## Review Checklist

Before completion, verify:

1. The issue or PR authorized the actual files changed.
2. The minimum level still matches the work performed.
3. The required context read set was used or an override was recorded.
4. Human-gated operations are not being merged without approval.
5. Low-risk merge is allowed by this matrix and the merge policies.
6. Adoption or material-upgrade assessments preserve model judgment and do not
   turn a Skill or deterministic result into target architecture authority.
7. Any `next_action_gate` names a concrete existing gate and the exact action
   that must wait without blocking completion of the read-only assessment.
