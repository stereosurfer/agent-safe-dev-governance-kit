# Target Install Validation Plan

Status: active mechanical proof-boundary contract with a caller-supplied claim
interface and documented legacy-tool limitations.

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

`target-evidence-check` uses the common validation envelope and separates:

```yaml
result: pass | fail | blocked
domain_result: claims_match | claims_mismatch | incomplete
derived_state: claims_match | claims_mismatch | incomplete
writes_performed: false
mechanically_checked:
  - checks actually completed for this invocation
not_checked:
  - unnamed, semantic, unavailable, or otherwise unchecked state
human_gate:
  status: not_checked
  reason: mechanical target evidence does not establish human approval
proof_boundary: exact claim limit
findings:
  - stable code, one field or path, material reason, and blocking state
```

An assessment may separately name an already-defined gate for a proposed next
action. Mechanical target evidence must not invent that gate or report it as
approved.

## Current Caller-Supplied Claim Interface

```text
python3 scripts/asgk.py target-evidence-check \
  --repo-root <target> \
  [--expect-path <path>]... \
  [--forbid-path <path>]... \
  [--expect-text <path> <literal>]... \
  [--forbid-text <path> <literal>]... \
  --json
```

The caller owns every claim. The command has no built-in target required-file
set and accepts an arbitrary directory layout. Paths must be exact normalized
target-relative paths and must remain inside the resolved root. Text claims use
case-sensitive literal containment in in-root UTF-8 regular files.
Each claim flag consumes its fixed one or two following values before later
options are parsed, so an exact path or literal may begin with `-`; place a
later `--json` after all values for that claim.

Claim meaning:

- `expect-path` matches when the named path is present.
- `forbid-path` matches when the named path is absent.
- `expect-text` matches when the named readable file contains the literal.
- `forbid-text` matches when the path is absent or the named readable file does
  not contain the literal. Pair it with `expect-path` when existence is also
  required.

Accepted claims are evaluated independently. A contradictory set does not gain
authority or become a recommendation; any complete observable disagreement is
reported as `claims_mismatch`. The evaluator remains responsible for whether
the claim set is coherent and sufficient for its assessment question.

At least one claim is required. Complete all-match evidence produces
`claims_match`, common `pass`, and exit `0`. Complete observable disagreement
produces `claims_mismatch`, common `fail`, one stable blocking finding per
mismatched claim, and exit `1`. Missing, unsafe, unreadable, undecodable, or
otherwise unevaluable input produces `incomplete`, common `blocked`, and exit
`1`.

Literal values and target contents are never emitted. Text claim records expose
only the literal length and SHA-256 digest. That digest is an evidence
fingerprint, not a secrecy guarantee; do not publish it when even equality or
dictionary confirmation would expose sensitive information. Exit `0` proves
only that accepted caller claims matched named observable paths or text during
a read-only run. It does
not inspect unnamed state or prove claim sufficiency, semantic correctness,
security, privacy, license sufficiency, target fit, architecture or layout,
governance depth, minimum adaptation, readiness, completeness,
recommendation, approval, implementation authority, PR readiness, or merge
authority.

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
- the mismatch must be reported until separately scoped clean-cutover work
  removes or corrects the command.

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

## Legacy Cutover Boundary

The caller-supplied claim interface replaces fixed target shape as the retained
mechanical direction. Separately authorized cleanup may remove the three legacy
commands and their fixed fixtures. Unless another issue explicitly changes the
contract, cleanup preserves only the implemented `target-evidence-check`
boundary: read-only execution, caller-owned claims, root containment, explicit
checked/unchecked evidence, and no fit, depth, recommendation, approval, or
readiness inference. It need not preserve legacy required shapes, planners,
categories, or manifests.

Cleanup must not turn any source-repository surface into a target requirement,
encode the frontier evaluator's expected conclusion, or recreate a universal
target bundle under a new name. Evidence-pointer tooling, donor-state scans, or
other new claim types require their own durable authorization.

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
