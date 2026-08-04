---
name: asgk-upgrade-audit
description: Use when an ASGK-adopted repository is considering a material update; guides a read-only frontier-capability comparison of source changes and target state, preserving target ownership while judging fit, minimum sufficient adaptation, uncertainty, and the next safe plan.
---

# ASGK Material Upgrade Assessment

Use this skill when a repository already uses ASGK-derived governance and is
considering materially newer guidance, templates, Skills, policies, or tooling.
It guides read-only assessment and planning. It is not an auto-upgrader, version
synchronizer, or approval mechanism.

## Capability Boundary

A material ASGK upgrade is normally an infrequent, high-impact,
context-sensitive task performed by a human-selected frontier-capability model.
ASGK does not select, route, schedule, switch, price-tier, or orchestrate the
evaluator.

The Skill guides source-delta discovery, target evidence, comparison, universal
safety boundaries, alternatives, confidence, unknowns, and stop behavior. The
evaluator judges which source changes matter to the target, the governance
depth that remains appropriate, the minimum sufficient adaptation, and whether
any upgrade should be recommended.

## Authority And Safety Boundary

The assessment is read-only and creates no target write, upgrade, approval, or
merge authority. Durable implementation scope must live in a target-owned
GitHub issue or PR with bounded allowed paths.

The target repository owns its current status, instructions, document
navigation, project boundaries, storage roots, protected paths, validation,
license decisions, local conventions, and history. Preserve those meanings. A
source file, newer version, or donor layout is evidence for comparison, not
authority to overwrite target state.

The assessment adds no human approval layer. Existing human gates apply only
when a recommended implementation touches a concrete high-risk operation
already defined by the target repository or
`docs/control/HUMAN_GATED_OPERATIONS.md`. Name the exact operation and policy;
do not create or report a gate merely because the comparison requires semantic
judgment or manual adaptation.

## Minimum Reads

Read `docs/INSTALL_SURFACE.md`, the target's smallest authoritative entry set,
and enough source-delta evidence to identify the baseline, material changes,
target equivalents, and durable assessment destination. Follow references only
when a material comparison requires more evidence.

Use `docs/control/TARGET_INSTALL_CHECKLIST.md` when comparison questions need
expansion and `docs/control/VALIDATION_STRATEGY.md` plus command help when
deterministic claims or proof limits matter. Read a human-gate policy only when
a proposed action could trigger it. Do not read or copy the full source tree by
default.

## Assessment Procedure

### 1. Establish The Comparison Boundary

Identify the target repository, the decision the assessment must inform, the
best evidenced target ASGK baseline, the source reference being considered, the
read-only scope, and the target-owned durable destination for the result. If
the baseline is uncertain, record how that limits the comparison instead of
inventing version certainty.

### 2. Discover Target-Owned State And ASGK Lineage

Use direct target evidence to find governance mechanisms that are ASGK-derived,
locally adapted, or functionally equivalent. Record local behavior and
customization that must be preserved. Do not classify the target into a fixed
adoption type, and do not infer that a missing ASGK-named file means a missing
capability.

Include only target surfaces made relevant by repository navigation, history,
references, validation, recurring failures, or the material source delta.

### 3. Compare Material Source Changes With Target Evidence

Cite only source changes that could alter the recommendation. Combine related
deltas when useful, and distinguish source evidence, target equivalent,
relevance judgment, material effect, and proof limit.

A newer source file, renamed path, or version difference is not by itself a
target gap. The comparison must reason about responsibilities and effects, not
source-tree conformity. Do not create a fixed completeness matrix or require
every source surface to appear in the target.

### 4. Use Deterministic Tools Only As Bounded Evidence

Use `target-evidence-check` only for explicit path or literal-text claims
derived from the source-delta comparison and target evidence. The evaluator
supplies every claim; the command does not select relevant source changes,
decide claim sufficiency, or form an upgrade recommendation. Use command help
for the exact four claim types, apply
`docs/control/VALIDATION_STRATEGY.md`, and record both what matched and what
remained unchecked. ASGK retains no target install planner, fixed-shape checker,
or compact target-upgrade manifest.

### 5. Exercise Frontier Judgment

Judge, from the source comparison and target evidence:

- whether the source changes materially improve the target;
- whether the target already satisfies the responsibility through an
  equivalent or stronger local mechanism;
- the governance depth proportionate to current target risks;
- the minimum sufficient change, if any;
- target-owned behavior and local conventions that must be preserved;
- alternatives, tradeoffs, downstream compatibility, and rollback needs;
- whether retaining the current target state is the better recommendation.

Do not choose from fixed target classifications, safe/manual/never-overwrite
buckets, a module menu, a two-path Skill choice, or a preset completion label.
The recommendation may conclude that no upgrade is warranted.

### 6. State Confidence And Unknowns

Give a plain-language confidence statement with its basis. List material
unknowns, why they matter, what evidence would resolve them, and whether a safe
recommendation can still be made. Keep unknown or unverifiable compatibility,
lineage, and validation claims unknown.

### 7. Produce The Next Safe Plan

Record the assessment in the target repository's existing issue, PR, or handoff
lineage. If changes are recommended, use the target's own issue-scoping policy
to draft the minimum complete target-owned issue or PR; do not invent a smaller
parallel field set in this Skill. For an ASGK-governed target, that means all 13
canonical fields from `AGENTS.md` plus separate `context_read_set` and
`project_specific_validation` gates. Allowed paths must come from target
evidence, and any exact existing human-gate trigger must be named. Separate a
tooling correction or unrelated high-risk action when the current durable
scope does not authorize it.

If no change is recommended, record the rationale, evidence limits, and the
future condition that would justify reassessment. Do not create work merely to
match a source version or source file shape.

## Durable Record

Adapt the assessment to the target's existing issue, PR, or handoff format. Do
not create a separate schema, manifest, or declaration. Leave a concise,
traceable record of:

- recommendation and rationale;
- material source/target evidence and proof limits;
- minimum change or no-change conclusion and target state to preserve;
- confidence, unknowns, alternatives, compatibility, tradeoffs, and rollback;
- next authorized action and any exact existing gate that applies to it.

End with one compact assessment state: `assessment_complete` or `blocked`.
Record any exact existing gate separately as `next_action_gate`; it blocks only
the named implementation action.

Use `assessment_complete` when evidence supports a target-specific
recommendation, including no change. It does not approve an upgrade. Use
`blocked` only when missing authority, access, source boundary, or material
evidence prevents a responsible recommendation; state exactly what would
unblock it.
