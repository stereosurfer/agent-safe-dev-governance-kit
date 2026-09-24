# ASGK Evolution Model

Status: current document-driven self-evolution model. The optional 3.0
metadata catalog is a public CLI projection, not a released product contract
or a default read requirement.

This document defines how ASGK improves itself as a document-driven system. It
is a durable model, not a progress log, release plan, maturity ledger, or
runtime-specific design.

## Core Thesis

ASGK evolves when a durable rule or observed failure becomes a bounded work
unit, is projected into the repository, checked with explicit evidence, used
independently later, and closed out with a traceable decision. The model must
remain understandable to a new person or a different AI without access to the
author’s prior conversation. This source repository must demonstrate that loop
on itself; a good-looking proposal or synthetic test is not later-use proof.

## The Self-Evolution Loop

```text
durable rule
  -> bounded issue/PR
  -> checked projection
  -> decision and rejected paths in issue closeout
  -> independent later use
  -> target evidence when applicable
  -> release closeout
```

When experience suggests a reusable method, a related but distinct loop is:

```text
run / incident
  -> observed Lesson or ledger entry with provenance and competing explanations
  -> bounded improvement issue and proposal
  -> branch / PR, regression and independent review
  -> applicable existing gate and versioned Skill or knowledge change
  -> later-use evidence for the version actually loaded
```

Either loop can stop at an observation or reject a proposal. A Lesson is not a
rule merely because it is indexed; a merged Skill edit is not later-use proof.
Accepted, rejected, blocked and reverted branches remain in GitHub issues,
PRs, commits and closeout comments rather than a new permanent migration log.

### 1. Durable rule

The rule has one canonical owner and a clearly stated boundary. It says what
the repository promises, what it does not promise, and which evidence can
support the claim. A rule is not authoritative merely because a validator,
Skill, example, or model repeats it.

### 2. Bounded issue or PR

An executable work unit names its objective, plan, acceptance, allowed paths,
expected output, non-goals, stop conditions, rollback expectation, bounded
context read set, and project-specific validation. The live issue or a
self-contained qualifying PR is the authority for that work unit. A task
packet can narrow scope but cannot replace the issue or add authority.

### 3. Checked projection

The rule is projected into the smallest necessary document, template, schema,
validator, fixture, or CLI surface. Mechanical checks report the exact claim
they checked, what they did not check, findings, human-gate state, and proof
boundary. A pass proves only the named mechanical claim; it does not prove
semantic fit, approval, release readiness, or merge authority.

### 4. Independent later use

The repository must be resumable by a person or a different agent/provider
using durable state rather than a remembered conversation. A later user should
be able to recover what to do, where to work, what is forbidden, which evidence
exists, and what remains unknown. A cold reader or replacement agent is
evidence of handoff quality, not a source of authority.

For reusable methods, later use must identify the version actually loaded and
its new result. The originating Bot or agent may propose and implement a
change, but its favorable self-test is not independent semantic confirmation.
Apply a separate reviewer and the *existing* human gate when the concrete
Skill, policy, security or publication change requires one; do not invent a
universal police Bot or extra human checkpoint for every Lesson.

### 5. Target evidence

When ASGK is assessed in another repository, the assessment is read-only and
target-owned. Mechanical tools check only caller-supplied path or text claims;
frontier judgment decides fit, depth, and minimum sufficient change. ASGK does
not impose a universal target layout, adoption declaration, or completion
algorithm.

### 6. Release closeout

Source-only release preparation records the exact checked state and its proof
limits. Release, tag, publication, and distribution decisions remain separate
human-gated operations. Closeout records the decision and evidence in GitHub;
CURRENT_STATUS keeps only the current recovery snapshot.

## What Counts As Improvement

An ASGK change should make at least one of these durable improvements:

```yaml
improvement_modes:
  clarify_rule: make the product boundary or canonical owner unambiguous
  bound_work: make scope, forbidden paths, rollback, or context explicit
  improve_evidence: make a mechanical claim, finding, or proof limit exact
  improve_handoff: reduce the context needed for a safe replacement handoff
  prove_transfer: demonstrate independent later use or a cold-start recovery
  prove_target_claim: record caller-supplied target evidence without overclaiming
  close_out: preserve a compact decision tree and current recovery state
  remove_residue: delete or reclassify superseded material under its own scope
  promote_capability: move a reproducible, reviewed Lesson into a versioned method
```

More documents are not automatically more governance. A new projection must
have one owner, one reason to exist, and a bounded consumer. Duplicate owners,
unbounded reading, and historical plans presented as current instructions are
regressions.

## Three Different State Owners

| State | Owner | Purpose and limit |
| --- | --- | --- |
| Governed change and decision tree | Live GitHub issue/qualifying PR, MDR, review, CI, commits and issue closeout | Grants bounded work and preserves why paths were accepted or rejected; a search index only points back to it. |
| Current delivery question/evidence graph | The particular target-owned research, video, translation or other task package, when needed | Routes a reader from a compact entry to the relevant question, observations, complete evidence units, gaps and next action; it cannot promote its own method or grant repo edits. |
| Reusable capability and experience | Versioned Skill/knowledge repository with a bounded Lesson/catalog index | Finds applicable prior cases and methods; an observed record is not an approved rule or the current task's question graph. |

Many Lessons and ledgers may accumulate without being loaded by default. A
reader starts from the current GitHub work unit and compact task entry, opens
one relevant question/evidence unit, then consults a narrow prior-method slice
only when useful. Full raw evidence stays at the task's appropriate home; Bot
memory keeps identity and pointers, not the entire method or audit corpus.
The research package's thought-tree shape is an example, not a mandatory ASGK
folder scheme. Small tasks may need only an issue/PR and compact handoff.

`python3 scripts/asgk.py catalog --help` exposes optional discovery over an
explicitly supplied metadata index. The `v3/` catalog entry is a compatibility
wrapper; the candidate Skills remain neither root-cut-over nor installed.
Catalog checks cannot prove a referenced file or GitHub link exists, a textual
hit is applicable, or a target's substantive conclusion is sound.

## Evidence And Judgment Boundaries

```yaml
durable_authority:
  - selected live GitHub issue or qualifying self-contained PR
  - canonical repository rule, contract, or decision record
  - explicit human decision where the applicable policy requires one
mechanical_evidence:
  - named validator, CI check, fixture, inventory, or reference scan
model_judgment:
  - interpret evidence
  - identify semantic risk or recommendation
  - choose a bounded next action within the live work unit
not_authorized_by_model_or_validator:
  - create authority
  - satisfy a human gate
  - approve a release, publication, merge, or target change
```

This separation is the protection against model or provider lock-in. A capable
agent can reason freely inside the work unit, while a replacement agent can
audit the durable scope and evidence without inheriting hidden assumptions.

## Current Implementation Map

```yaml
product_owner: README.md
operating_rules: AGENTS.md
navigation: docs/DOCUMENT_MAP.md
source_ownership: docs/DOCUMENT_REGISTRY.md
recovery_snapshot: docs/handoff/CURRENT_STATUS.md
work_unit_authority: live GitHub issue or qualifying PR
mechanical_entrypoints:
  - python3 scripts/asgk.py doctor
  - python3 scripts/asgk.py validate
  - python3 scripts/asgk.py negative all
  - python3 scripts/asgk.py check-pr --pr <number>
  - python3 scripts/asgk.py target-evidence-check ...
  - python3 scripts/asgk.py catalog --help
```

The map is a navigation aid. It does not create a second authority layer.
The root workflow and catalog implementations are canonical under
`scripts/asgk_lib/`; their named `v3/` compatibility wrappers and focused
tests support the public CLI and `doctor`. Uncut-over `v3/` templates, Skills
and design proposals remain non-default candidates under #372 until separately
reviewed. Optional Hermes/Kanban run state is
outside this map and never replaces GitHub work authority. A Codex+GitHub-only
recurring content job has no Kanban dependency; its schedule is a trigger, not
the current write or publication decision. Target assessment may also conclude
that no ASGK adaptation is needed.

## Change And Recovery Rule

Every evolution change is reversible through an ordinary Git revert unless an
applicable human-gated policy says otherwise. If a merged change is wrong, open
an authorized revert work unit; do not reset, force-push, or rewrite history.
If a proposed improvement needs an unlisted path, external capability, target
write, dependency, release, or publication, stop and obtain the required
durable scope or human decision before proceeding.

## Handoff Proof

The evolution model is successful when a later person or AI can use the current
startup set and canonical pointers to reconstruct the decision tree quickly:

```text
what -> where -> not what -> forbidden -> evidence -> unknowns -> next safe action
```

Completed-work history belongs in the issue, PR, merge commit, and bounded
close-out review. CURRENT_STATUS is overwritten as the recovery snapshot and is
never an append-only history ledger.
