# Document Map

Status: active ASGK repository-local navigation router.

This file is the compact routing surface for ASGK repository documents. It is
not the full document registry.

Use this file to decide where to look next. Do not read the whole repository by
default.

## Repo-local Scope

`DOCUMENT_MAP.md` is repo-local.

This file governs only the ASGK repository. A target repository may retain its
own equivalent navigation and ownership mechanisms. Templates under
`templates/` are optional references used only when a frontier-guided
assessment finds a real gap.

## Core Rule

```text
Read the smallest set of canonical documents required by the work unit.
```

If two documents appear to disagree, prefer the document marked `canonical` for
that topic in `docs/DOCUMENT_REGISTRY.md`. If a summary document disagrees with a
canonical document, the summary document is stale and should be fixed in a
separate issue.

## Progressive Disclosure Surfaces

```yaml
progressive_disclosure_surfaces:
  router:
    path: docs/DOCUMENT_MAP.md
    purpose: compact repo-local navigation router
    read_by_default: false
  registry:
    path: docs/DOCUMENT_REGISTRY.md
    purpose: complete repo-local document registry and canonical ownership table
    read_by_default: false
    read_when:
      - canonical ownership is unclear
      - current issue changes document ownership
      - current issue changes document-map or registry structure
      - validation or reviewer feedback points to registry mismatch
  policy:
    path: docs/control/DOCUMENT_MAP_POLICY.md
    purpose: document-map size limits, split ownership, and maintenance rules
    read_by_default: false
  read_sets:
    path: docs/control/CONTEXT_BUDGET_POLICY.md
    purpose: context read sets, expansion rules, and context reporting
    read_by_default: false
  install_surface:
    path: docs/INSTALL_SURFACE.md
    purpose: frontier-guided target assessment, responsibility boundaries, and minimum sufficient adaptation
    read_by_default: false
  skill_pack:
    path: docs/SKILL_PACK.md
    purpose: guided evidence and judgment procedures with source-distributed usage modes
    read_by_default: false
  issue_closeout_review_rules: {path: docs/handoff/ISSUE_CLOSEOUT_REVIEW_RULES.md, purpose: writing rules for mandatory issue closeout decision analysis in GitHub issue comments, read_by_default: false}
```

## Default Startup Set

Start every new agent session with this minimal set unless the current issue,
PR, or handoff packet points elsewhere:

```yaml
default_startup_set:
  - AGENTS.md
  - README.md
  - docs/handoff/CURRENT_STATUS.md
  - current GitHub issue or PR
```

Additional documents should be pulled by task type, not by habit.

## Document Roles

```yaml
roles:
  canonical: Primary source of truth for a topic.
  summary: Short orientation document that points to canonical sources.
  example: Non-authoritative sample for humans and agents.
  schema: Machine-readable structure contract.
  contract: Semantic rules and invariants.
  template: Reusable starting point for work units or GitHub surfaces.
  status: Current handoff or state surface.
  script: Executable validation or hygiene behavior.
  historical_evidence: Archived repo-local evidence; never current authority or target-project state.
```

## Default Entry Summary

```yaml
default_entry_summary:
  read_first:
    - AGENTS.md
    - README.md
    - docs/handoff/CURRENT_STATUS.md
    - current GitHub issue or PR
  full_registry: docs/DOCUMENT_REGISTRY.md
  context_read_sets: docs/control/CONTEXT_BUDGET_POLICY.md
  adoption_assessment: docs/INSTALL_SURFACE.md
  skill_pack: docs/SKILL_PACK.md
  map_policy: docs/control/DOCUMENT_MAP_POLICY.md
```

## Target Project Boundary

```yaml
target_project_rule:
  assessment_boundary: docs/INSTALL_SURFACE.md
  guided_procedure: skills/asgk-target-install-audit/SKILL.md
  reuse_target_owned_surfaces: true
  optional_references: document-map and registry templates under templates/
  never_copy_as_target_truth: ASGK repo-local maps, state, history, audits, or examples
```

The evaluator decides from target evidence whether either optional template
addresses a real gap. ASGK does not require universal target filenames, a fixed
document bundle, adoption declaration, module picker, or new approval gate.

## Maintenance Rules

1. Add full document rows to `docs/DOCUMENT_REGISTRY.md`, not this file.
2. Add context read-set definitions to `docs/control/CONTEXT_BUDGET_POLICY.md`,
   not this file.
3. Add target-assessment responsibilities, invariants, and optional-reference
   boundaries to `docs/INSTALL_SURFACE.md`, not this file.
4. Add skill-pack usage guidance to `docs/SKILL_PACK.md`, not this file.
5. Keep this file small enough to act as a router.
6. If this router exceeds the limits in `docs/control/DOCUMENT_MAP_POLICY.md`,
   stop and open a document-map maintenance issue.
