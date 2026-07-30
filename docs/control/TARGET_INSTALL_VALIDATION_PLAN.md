# Target Install Validation Plan

Status: active mechanical proof-boundary contract with documented legacy-tool
limitations.

This document defines what deterministic target-install tooling may and may not
prove.

It does not define target governance architecture, required target files,
adoption depth, module selection, evaluator choice, or approval authority.

## Core Boundary

```text
Frontier evaluation owns target-specific fit and depth.
Deterministic tooling owns observations, universal invariants, and concrete claim checks.
```

A deterministic command must not convert source-repository structure into a
universal target requirement.

## Responsibility Split

```yaml
responsibility_split:
  frontier_assessment:
    owns:
      - target fit
      - minimum sufficient adaptation
      - governance depth
      - comparison and alternatives
      - semantic interpretation
      - confidence and uncertainty
  deterministic_tooling:
    owns:
      - bounded repository observations
      - no-write confirmation
      - concrete path or text checks
      - universal invariant checks
      - verification of explicitly stated mechanically testable claims
      - accurate proof-boundary reporting
    does_not_own:
      - target architecture
      - semantic completeness
      - required governance weight
      - evaluator selection
      - approval or human-gate creation
```

## Permitted Mechanical Checks

A current or future read-only tool may check facts such as:

- whether a named path exists;
- whether a named target surface contains a cited marker or reference;
- whether a source-only path or donor-state reference is present;
- whether the command wrote files;
- whether a cited validation command was recorded as run and has available
  output;
- whether a claimed evidence pointer resolves;
- whether explicitly named target-owned paths changed;
- whether copied/adapted material has an observable license or notice surface;
- whether a proposed claim contradicts available repository state.

These checks are useful only when their inputs and assumptions are explicit.

## Forbidden Mechanical Conclusions

A deterministic tool must not claim:

- that every target needs a particular ASGK file or directory;
- that matching the ASGK source tree proves adoption readiness;
- that a missing source-shaped surface is necessarily a governance defect;
- that a fixed copy/template/customize category is the right target action;
- that the target's governance depth is sufficient;
- that the target is semantically safe, secure, private, or complete;
- that a model or provider should be selected;
- that a new approval is required beyond existing policy;
- that a tool pass authorizes implementation or merge.

## Required Output Boundary

Mechanical output should separate:

```yaml
mechanically_checked:
  - check performed
  - observed result
  - input or evidence location
  - command/version when relevant

not_checked:
  - semantic or unavailable question
  - reason it was not mechanically checked

existing_human_gate:
  - concrete proposed action
  - existing policy source
```

`existing_human_gate` reports an already-defined gate. It must not invent a new
approval requirement.

Tool output should also state `writes_performed: false` for read-only
assessment commands and avoid an aggregate label that can be mistaken for
semantic adoption completion.

## Current Command Limitations

### `target-install-check`

Current implementation uses a legacy hard-coded required-file list and fixed
document-map/registry expectations. Missing legacy surfaces can produce
blocking failures.

Therefore:

- its findings may be used as path-presence or source-state-leakage
  observations;
- its aggregate pass/fail result is not target-fit, adoption-readiness, or
  governance-depth evidence;
- a blocking legacy fixed-shape finding must not override a frontier
  assessment;
- the mismatch must be reported until a separately scoped tooling change
  corrects it.

### `target-install-plan`

Current implementation accepts repository location and emits a deterministic
legacy `copy_as_is`, `template_then_customize`, `customize_required`, and
`do_not_copy` plan.

Therefore:

- it does not assess target risk, workflow, existing equivalent controls, or
  minimum sufficient depth;
- its file categories are not a recommendation;
- its output may contribute source/target path observations only;
- it must not be described as a complete or target-specific adoption plan.

### `compact-target-upgrade-check`

Current implementation validates a legacy fixed manifest, fixed preserved-path
set, and manual-merge/never-overwrite buckets.

Therefore:

- it may detect some overwrite or no-write contradictions;
- it does not prove upgrade fit, appropriate depth, or completeness;
- its fixed path requirements remain a known limitation pending separate
  tooling work.

### `doctor`

Source-repository `doctor` validates currently encoded ASGK source checks. It
does not prove target adoption or frontier-assessment quality.

## Assessment Validation

The semantic assessment is reviewed through evidence, not reduced to a script
pass.

Review should confirm that:

- observations have target evidence;
- facts and judgment are separated;
- alternatives and depth tradeoffs are explained;
- confidence and unknowns are visible;
- current tool limitations are not hidden;
- the recommendation preserves target ownership and read-only boundaries;
- next work is bounded in existing issue/PR governance;
- no unsupported completion, portability, security, or approval claim is made.

## Future Tooling Direction

A future separately authorized tooling issue may replace fixed-shape behavior
with:

- read-only target observation collection;
- evidence-pointer validation;
- source-only reference and donor-state scans;
- universal invariant checks;
- comparison between explicit assessment claims and observable target state;
- accurate `mechanically_checked` and `not_checked` reporting.

Future tooling must not encode the frontier evaluator's expected conclusion or
recreate a universal target bundle under a new name.

## License Boundary

Tools may observe whether a license or notice surface exists and may flag
copied ASGK material without visible notice handling.

They cannot decide the target repository's overall license or provide legal
approval. A concrete proposed license change remains subject to existing target
policy.

## Stop Conditions

Stop a mechanical check or report it as incomplete when:

- inputs or repository root are ambiguous;
- a check would require writes;
- required evidence is unavailable;
- private or protected content is outside scope;
- a requested conclusion is semantic rather than mechanical;
- current legacy assumptions conflict with the target assessment;
- the tool would need to infer target architecture or approval authority.

## Tool Change Boundary

Documentation does not change current script or fixture behavior. Any checker,
planner, compact-upgrade, fixture, CLI-help, or exit-code change requires
separately authorized tooling work with positive and negative evidence.
