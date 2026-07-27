# Install Surface

Status: active adoption-assessment boundary.

This document defines how ASGK source material may inform a target-repository
assessment. It is not a universal target layout, required-file manifest, module
picker, adopter configuration exercise, or installer specification.

Introducing ASGK, or materially upgrading an existing adoption, is an
infrequent and context-sensitive architecture assessment. It should normally be
performed by a human-selected frontier-capability evaluator using the
relevant ASGK Skill.

ASGK does not select, route, schedule, switch, price-tier, or orchestrate that
evaluator.

## Core Rule

```text
Assess the target in place. Use ASGK source as evidence and reference, not as a target blueprint.
```

The ASGK source repository is a reference collection of governance rules,
procedures, examples, and tools. A target repository does not become correctly
governed by reproducing the source repository's file tree.

The evaluator judges target fit, minimum sufficient adaptation, governance
depth, and the next safe implementation plan from the target repository's
actual state. The Skill guides evidence gathering, comparison, safety
boundaries, uncertainty, and stop behavior; it must not encode the expected
target outcome.

## Responsibility Boundary

```yaml
responsibility_boundary:
  frontier_evaluator:
    - inspect the target repository and its current work practices
    - identify material handoff, authority, evidence, scope, and recovery risks
    - compare those risks with relevant ASGK source capabilities
    - judge whether ASGK adaptation is useful and how deep it should be
    - explain evidence, alternatives, uncertainty, limits, and next safe work
  skill:
    - guide attention and evidence gathering
    - preserve universal safety boundaries
    - prompt comparison, uncertainty, and safe-stop behavior
    - avoid prescribing a universal file bundle or conclusion
  deterministic_tools:
    - collect observations
    - check universal invariants
    - check concrete claims when inputs make those claims mechanically testable
    - report what was not checked
  target_repository:
    - remains authoritative for its own state, policies, paths, history, and implementation
```

The evaluator's recommendation is not implementation authority. Any later file
change must use the target repository's existing issue/PR governance and
allowed paths.

The read-only assessment itself adds no human approval layer. Existing human
gates apply only when a proposed implementation touches an operation already
defined as human-gated.

## Universal Safety Invariants

Every assessment must preserve these boundaries regardless of its
target-specific conclusion:

- assessment is read-only unless a separate target work unit authorizes writes;
- target repository state must not be overwritten from ASGK source assumptions;
- source-repository current status, document maps, internal history, audits,
  release state, or examples must not become target-project truth merely
  because they exist in ASGK;
- chat, model memory, and Skill output are not durable implementation authority;
- observed facts, evaluator judgment, tool evidence, unknowns, and proposed
  work must remain distinguishable;
- a tool pass must not be presented as semantic adoption completeness;
- private material, unavailable context, or unresolved authority conflicts must
  trigger a bounded stop rather than guessing;
- later implementation must preserve applicable license and notice obligations.

These invariants do not require every target to use the same filenames,
documents, templates, validators, or governance depth.

## Assessment Entry

Use `skills/asgk-target-install-audit/SKILL.md` for a first adoption assessment.
Use `skills/asgk-upgrade-audit/SKILL.md` when the target already contains
ASGK-derived governance.

The Skills own procedure. Use `docs/control/TARGET_INSTALL_CHECKLIST.md` only
when questions or evidence quality need expansion, and
`docs/control/TARGET_INSTALL_VALIDATION_PLAN.md` when mechanical proof limits
matter.

## Assessment Result

Record the result in an existing durable target surface such as the relevant
issue, PR, or handoff lineage. Do not create a new adoption declaration,
manifest, module registry, migration ledger, or parallel authority document.

The result should make clear the recommendation and rationale, material evidence
and proof limits, minimum adaptation or no-change conclusion, target state to
preserve, confidence and unknowns, alternatives, and the next authorized action.

Different target repositories may receive different conclusions from the same
assessment method.

## Source Material Use

ASGK files may be inspected, quoted, adapted, or used as implementation input
when the evaluator finds them relevant. Their presence in the source repository
does not make them required target surfaces.

Consider material factors such as whether the source material:

- addresses an observed target need;
- conflicts with target-owned rules or terminology;
- contains ASGK repo-local state or donor-specific paths;
- assumes tooling or GitHub features unavailable in the target;
- would add more governance weight than the observed risk justifies;
- can be validated or reviewed at the claimed boundary.

File handling is therefore a result of target-specific assessment, not a
predefined `copy_as_is`, `template_then_customize`, or `customize_required`
catalog.

## License And Notice Boundary

ASGK source material is Apache-2.0 licensed. If an implementation later copies
or adapts ASGK-derived material, preserve applicable license, copyright, and
modification notices.

The assessment may identify likely notice handling and unresolved questions. It
does not decide the target repository's overall license and must not silently
replace the target `LICENSE`.

A proposed license change remains subject to the target repository's existing
human-gated policy. No additional approval gate is created by the assessment.

## Current Deterministic Tool Boundary

The current target-install checker, planner, and compact-upgrade checker retain
legacy fixed-shape assumptions. Their outputs may provide bounded observations;
their pass/fail result does not prove target fit, governance depth, adoption
readiness, or upgrade completeness. Use
`docs/control/TARGET_INSTALL_VALIDATION_PLAN.md` for the detailed proof boundary.

When tool output conflicts with target evidence, record the conflict and proof
limit. Continue the semantic assessment when a responsible recommendation can
still be made. Changing checker, planner, fixture, or exit-code behavior
requires separately authorized tooling work and its own validation evidence.

## Stop Conditions

Stop the assessment and report the exact gap when:

- target authority or assessment scope is unclear;
- required target evidence is unavailable;
- source and target instructions conflict;
- the evaluator cannot distinguish a universal safety invariant from a
  target-specific preference;
- private material would be required without authorization;
- the recommendation would depend on an unsupported tool, workflow, or policy;
- evidence is too limited for a responsible target-specific recommendation.

## Maintenance Rule

This document owns the adoption responsibility boundary. The checklist owns
assessment questions. The validation plan owns mechanical proof limits. Skills
own procedure.

Do not restore universal target file lists or duplicate the Skill procedure in
this document.
