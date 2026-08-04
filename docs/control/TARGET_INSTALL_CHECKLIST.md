# Target Install Assessment Checklist

Status: active frontier-assessment question and evidence guide.

This checklist helps a frontier-capability evaluator perform a read-only,
target-specific ASGK adoption or material-upgrade assessment.

It is not a required-file checklist, target architecture, module menu,
configuration form, adoption declaration, approval record, or deterministic
validator contract.

## Core Rule

```text
Judge fit and depth from target evidence. Do not infer correctness from source-shape similarity.
```

The relevant ASGK Skill guides the assessment procedure. This checklist defines
questions that should be answered or explicitly marked unresolved. It does not
predetermine the answer.

## 1. Target Context And Authority

- What repository or checkout is being assessed?
- What issue, PR, repository rule, or user request defines the read-only scope?
- Which target files and GitHub surfaces currently own work authorization,
  boundaries, validation, decisions, closeout, and handoff?
- Is current state recoverable without prior chat?
- Are authority conflicts or stale status already visible?
- Which evidence was inspected, and which expected evidence was unavailable?

## 2. Current Work And Handoff Risk

- How do humans and Agents currently determine the active work unit?
- Can a different provider, lower-cost Agent, or human resume safely?
- Are allowed paths, non-goals, stop conditions, validation, and next actions
  durable and discoverable?
- Where can a later maintainer trace material decisions and evidence?
- Which failures would cause the largest reconstruction or blast-radius cost?

## 3. Existing Governance And Actual Gaps

- Which useful governance behaviors already exist, regardless of filename?
- Which observed failures are process gaps, tooling gaps, stale-state problems,
  or merely documentation differences?
- Does the target already have equivalent controls under target-owned names?
- Would importing an ASGK source surface duplicate or conflict with those
  controls?
- Which gaps are material enough to justify adaptation?
- Which apparent gaps are unsupported assumptions and require more context?

## 4. Fit And Minimum Sufficient Depth

The evaluator should explain:

- whether ASGK adaptation is useful for this target;
- which observed risks the recommendation addresses;
- the minimum sufficient governance depth for those risks;
- why a lighter approach would be insufficient;
- why a heavier approach would add unnecessary cost or duplication;
- which source capabilities are relevant as implementation input;
- which source capabilities are irrelevant, excessive, or incompatible;
- what alternative approaches were considered.

Do not answer this section by matching the target against a universal ASGK file
list.

## 5. Target Ownership And Source-State Safety

- Which target-owned status, policies, paths, history, templates, and license
  surfaces must remain untouched?
- Does any proposed source material contain donor-repository state, ASGK
  history, stale paths, or source-only validation assumptions?
- Could a copied surface silently become competing authority?
- Is the proposed adaptation compatible with target terminology and workflow?
- Are source-derived and target-authored portions distinguishable where that
  distinction matters?

## 6. Evidence And Validation

For every material recommendation:

- identify the target evidence supporting it;
- distinguish observed fact from evaluator judgment;
- name any deterministic output used;
- state exactly what the output proves;
- state what was not checked;
- record confidence and unresolved questions;
- avoid claiming security, semantic correctness, privacy, API freshness, or
  completion unless separately evidenced.

Use `target-evidence-check` only for explicit path or literal-text claims
derived from the assessment. Its exit `0` means those accepted claims matched;
it does not establish that the claim set is sufficient or decide fit, depth,
adaptation, recommendation, approval, or completion.

The legacy `target-install-check`, `target-install-plan`, compact-upgrade check,
and source `doctor` remain supporting evidence only at their narrower
documented boundaries. Never weaken a target-specific recommendation merely to
make a fixed-shape legacy command pass.

## 7. License And External Boundaries

- Would proposed implementation copy or adapt Apache-2.0 ASGK material?
- Where could applicable notice handling live without replacing target-owned
  license policy?
- Does implementation touch dependencies, workflows, external services,
  credentials, visibility, publication, private material, or runtime adapters?
- Which existing human gates would those concrete actions trigger?

The assessment itself does not create a new human gate.

## 8. Recommendation And Next Safe Work

The durable assessment result should state:

- the fit/depth conclusion and rationale;
- target evidence and comparison;
- target-owned state to preserve;
- relevant ASGK source inputs, if any;
- alternatives considered;
- confidence, unknowns, and proof limits;
- the smallest coherent next implementation work unit;
- paths or actions that must remain excluded;
- existing human gates triggered by that proposed work, if any;
- or a clear conclusion that no implementation is currently justified.

Use an existing issue, PR, or handoff surface. Do not create a separate adoption
declaration or manifest.

## Completion Quality

An assessment is sufficiently complete when a later human or Agent can:

- understand what was inspected;
- reproduce the evidence trail;
- distinguish fact, tool result, evaluator judgment, and unknowns;
- understand why the recommended depth fits this target;
- continue with a bounded work unit without relying on the evaluator's chat;
- see what the assessment does not prove.

There is no required target file count or universal completion shape.

## Stop Conditions

Use `blocked` only if:

- target evidence is too thin for a defensible fit/depth judgment;
- scope or authority is unclear;
- private or protected context is required but unavailable;
- source and target rules conflict;
- the evaluator would otherwise need to guess.

A legacy tool conflict is a proof-limit finding, not an assessment blocker when
a responsible recommendation remains possible. A protected next action is
recorded under its exact existing gate; it does not block the read-only
assessment.
