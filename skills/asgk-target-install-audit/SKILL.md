---
name: asgk-target-install-audit
description: Use when a repository is considering ASGK adoption; guides a read-only frontier-capability assessment of target fit, governance depth, evidence, uncertainty, and the next safe plan without prescribing a universal target shape.
---

# ASGK Target Adoption Assessment

Use this skill before introducing ASGK into a target repository. It guides
read-only assessment and planning. It is not an installer, a
target-architecture selector, or adoption approval.

## Capability Boundary

ASGK adoption is normally an infrequent, high-impact, context-sensitive task
performed by a human-selected frontier-capability model. ASGK does not select,
route, schedule, switch, price-tier, or orchestrate the evaluator.

The Skill guides attention, evidence gathering, comparison, universal safety
boundaries, alternatives, confidence, unknowns, and stop behavior. The
evaluator judges target fit, governance depth, minimum sufficient adaptation,
and whether any target change should be recommended.

## Authority And Safety Boundary

The assessment is read-only and creates no target write, adoption, approval, or
merge authority. Record its result in the target repository's existing issue,
PR, or handoff lineage. A target-owned issue or PR with bounded allowed paths is
required before implementation.

The target repository owns its governance state. Do not overwrite or
reinterpret target-owned status, instructions, document navigation, license
decisions, protected paths, storage boundaries, validation, or repository
history from ASGK source-repository assumptions.

The assessment adds no human approval layer. Existing human gates apply only
when a recommended implementation touches a concrete high-risk operation
already defined by the target repository or
`docs/control/HUMAN_GATED_OPERATIONS.md`. Name the exact operation and policy;
do not create or report a gate merely because the assessment involves semantic
judgment.

## Minimum Reads

Read `docs/INSTALL_SURFACE.md` and the target's smallest authoritative entry set
sufficient to identify its purpose, current state, constraints, and durable
assessment destination. Follow target references only when a material question
requires more evidence.

Use `docs/control/TARGET_INSTALL_CHECKLIST.md` when assessment questions need
expansion and `docs/control/VALIDATION_STRATEGY.md` plus command help when
deterministic claims or proof limits matter. Never use an ASGK donor file list
as a required target shape.

## Assessment Procedure

### 1. Establish The Assessment Boundary

Identify the target repository, the decision the assessment must inform, the
ASGK source reference being considered, the read-only scope, and the
target-owned durable destination for the result. Separate assessment authority
from later implementation authority.

### 2. Discover The Actual Target Context

Use direct target evidence to understand:

- repository purpose and material risks;
- who or what makes changes and how work is authorized;
- existing issue, PR, review, validation, merge, and handoff practices;
- protected paths, security and storage boundaries, dependencies, external
  services, license constraints, publication or release behavior, and other
  concrete high-risk boundaries when relevant;
- current governance strengths, recurring failures, and recovery needs.

Do not infer that a mechanism is absent from a missing ASGK-named file. Find the
target's actual equivalent before describing a gap.

### 3. Gather Evidence And Compare Responsibilities

Cite only claims that could change the recommendation. Combine related
observations when useful, and distinguish observation, inference, and material
proof limit. Compare the target's actual mechanisms with relevant ASGK
capabilities and universal safety invariants.

The comparison must identify target mechanisms that already satisfy the need,
material gaps that create real target risk, and ASGK concepts that are not
relevant to this target. File presence alone is not semantic evidence.

### 4. Use Deterministic Tools Only As Bounded Evidence

Use `target-evidence-check` only after the assessment produces an explicit,
mechanically testable path or literal-text claim. The evaluator supplies every
claim; the command does not select target files, decide whether the claim set is
sufficient, or form a recommendation. Use command help for the exact four claim
types, apply `docs/control/VALIDATION_STRATEGY.md`, and record both what matched
and what remained unchecked. ASGK retains no target install planner, fixed-shape
checker, or compact target-upgrade manifest.

### 5. Exercise Frontier Judgment

Judge, from the target evidence:

- whether ASGK concepts materially improve this repository;
- the governance depth proportionate to the target's risks and operating model;
- the minimum sufficient adaptation, if any;
- which target-owned strengths and local conventions must be preserved;
- viable alternatives, including retaining the current approach;
- tradeoffs, downstream effects, and evidence that could change the
  recommendation.

Do not choose from a module menu, fixed install bundle, file-classification
scheme, or two-path adoption choice. The recommendation may conclude that no
change is warranted.

### 6. State Confidence And Unknowns

Give a plain-language confidence statement with its basis. List material
unknowns, why they matter, what evidence would resolve them, and whether a safe
recommendation can still be made. Keep unknown or unverifiable claims unknown;
do not convert them into a pass.

### 7. Produce The Next Safe Plan

Record the recommendation in the target's existing issue, PR, or handoff
lineage. If changes are recommended, use the target's own issue-scoping policy
to draft a complete target-owned issue or PR; do not invent a smaller parallel
field set in this Skill. For an ASGK-governed target, that means all 13
canonical fields from `AGENTS.md` plus separate `context_read_set` and
`project_specific_validation` gates. Allowed paths must come from target
evidence, and any exact existing human-gate trigger must be named. Do not
perform target writes under this assessment.

If no change is recommended, record the rationale, evidence limits, and the
future condition that would justify reassessment. Do not create work only to
make the target resemble the ASGK source repository.

## Durable Record

Adapt the assessment to the target's existing issue, PR, or handoff format. Do
not create a separate schema, manifest, or declaration. Leave a concise,
traceable record of:

- recommendation and rationale;
- material evidence, inference, and proof limits;
- minimum change or no-change conclusion and target state to preserve;
- confidence, unknowns, alternatives, and tradeoffs;
- next authorized action and any exact existing gate that applies to it.

End with one compact assessment state: `assessment_complete` or `blocked`.
Record any exact existing gate separately as `next_action_gate`; it blocks only
the named implementation action.

Use `assessment_complete` when evidence supports a target-specific
recommendation, including no change. It does not approve adoption. Use
`blocked` only when missing authority, access, or material evidence prevents a
responsible recommendation; state exactly what would unblock it.
