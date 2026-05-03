# Evolution Model

Status: active governance model.

This document explains how ASGK evolves from written rules into repeatable
validation, runtime control, and productized governance. It also records the
current maturity of PR auto-validation, framework self-consistency validation,
and negative defense testing.

## Core Thesis

```text
Agent runtimes will commoditize. Repo governance is the durable layer.
```

ASGK v1.x focuses on a runtime-agnostic generic repo-agent governance core.
Runtime-specific profiles are deferred to v2.0 as optimization adapters.

## What Documentation-driven Evolution Means

Documentation-driven evolution means that new governance behavior begins as a
clear, durable rule in the repository before it becomes automation.

The expected path is:

```text
policy statement
  -> checklist or template field
  -> validation script or CI gate
  -> CLI/runtime control
  -> reusable product capability
```

This is intentionally conservative. It prevents agents from inventing runtime
behavior before the policy boundary is explicit.

## What Self-governance Means

Self-governance means this repository uses its own rules to change itself.

A valid self-governed change should use:

```text
GitHub issue
  -> branch
  -> allowed-path change
  -> PR template
  -> validation evidence
  -> Merge Decision Record
  -> low-risk merge or human gate
  -> issue result comment
  -> issue close
```

The repository has already used this pattern repeatedly for docs, control
policies, negative fixtures, validation script hardening, and CI workflow
hardening.

## What Self-validation Means

Self-validation means repository rules are checked by repository-owned tools and
GitHub Actions.

Current self-validation includes:

```text
scripts/check_project.py
scripts/validate_bootstrap.py
scripts/governance_hygiene.py
.github/workflows/bootstrap-validation.yml
examples/negative/changed-path fixtures
```

Self-validation is not the same as full semantic proof. It checks specific
invariants that have been encoded into scripts, templates, fixtures, or CI.

## Current Maturity Summary

| Area | Current state | Meaning |
|---|---|---|
| PR auto-validation | core complete | PRs run scaffold, bootstrap, whitespace, and changed-path negative checks. |
| Framework logical self-consistency validation | partial | Required files/terms/templates/JSON/storage invariants are checked, but full semantic contradiction detection is not automated. |
| Negative defense testing | partial | Changed-path negative cases are wired into CI; PR-body/task-packet/textual policy cases are planned but not automated. |
| Runtime control | early | Scripts exist; no full `asgk` CLI wrapper yet. |
| Productized install/upgrade flow | early | Quickstart and scaffold exist; package/installer/upgrade workflow not complete. |

## Stage Model

### Stage 0 — Docs-as-policy

Rules are first captured as repository documents.

Examples:

```text
docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md
docs/control/HUMAN_GATED_OPERATIONS.md
docs/control/CONTEXT_BUDGET_POLICY.md
docs/control/AGENT_CAPABILITY_MATRIX.md
docs/control/NEGATIVE_TEST_PLAN.md
```

Success condition:

```text
A new agent session can read the rule without relying on chat history.
```

Risk:

```text
Rules may still be advisory unless connected to templates or validators.
```

### Stage 1 — Policy-as-checklist

Policies become required issue fields, PR sections, handoff sections, review
checklists, or task packet fields.

Examples:

```text
.github/ISSUE_TEMPLATE/agent_task.yml
.github/PULL_REQUEST_TEMPLATE.md
docs/control/PR_REVIEW_CHECKLIST.md
docs/control/MERGE_DECISION_RECORD.md
docs/control/TASK_PACKET_FORMAT.md
```

Success condition:

```text
A reviewer can tell whether a PR attempted to satisfy the policy.
```

Risk:

```text
Humans or agents can still fill checklist fields incorrectly or incompletely.
```

### Stage 2 — Policy-as-validation

Policies become executable checks.

Examples:

```text
scripts/check_project.py
scripts/validate_bootstrap.py
scripts/governance_hygiene.py
.github/workflows/bootstrap-validation.yml
examples/negative/
```

Current Stage 2 coverage:

```yaml
stage_2_current:
  positive_checks:
    - required directory scaffold
    - required files
    - required terms
    - JSON parse validity for schemas/examples
    - YAML-like required task-packet fields
    - PR template required headings
    - issue template required fields
    - storage-profile invariants
    - whitespace diff check
  negative_checks:
    - runtime artifact changed-path fixture must be blocked
    - protected path changed-path fixture must be blocked
    - private/binary source-like changed-path fixture must be blocked
```

Known gaps:

```yaml
stage_2_gaps:
  - PR-body validation is not automated
  - Merge Decision Record field validation is not automated for actual PRs
  - task-packet parser validation is not automated as full YAML/schema validation
  - see-chat textual detection is not wired into CI
  - human-gated operation detection is mostly review-policy based
  - full semantic contradiction detection between documents is not automated
```

### Stage 3 — Policy-as-runtime-control

Policies are automatically applied through CLI, Skills, Codex goals, or runtime
profiles.

Planned examples:

```bash
asgk doctor
asgk validate
asgk hygiene --paths-file changed-paths.txt
asgk negative changed-paths
asgk check-pr <number>
asgk merge-record
asgk handoff-update
```

Stage 3 should not invent new policy. It should wrap stable Stage 2 behavior and
produce durable reports.

Current status:

```text
early; scripts exist, but the first `asgk` CLI wrapper is not implemented.
```

### Stage 4 — Governance-as-product

The governance layer becomes installable, reusable, upgradeable, and portable to
other repositories.

Expected capabilities:

```text
install scaffold
initialize repo-specific project brief
validate installation
run positive and negative test suite
upgrade governance package
generate task packets
generate merge decision records
generate handoff updates
```

Runtime-specific profiles belong after the core is stable:

```text
profiles/codex-app/
profiles/chatgpt-web-github-connector/
profiles/opengoat/
profiles/claude-code/
profiles/cursor/
```

These are v2.0 optimization adapters, not v1.x foundations.

## What Is Already Automated

```yaml
automated_now:
  - project scaffold check
  - bootstrap governance validation
  - JSON parse validation for schemas/examples
  - PR template heading presence through bootstrap validation
  - issue template field presence through bootstrap validation
  - storage profile invariant checks for positive example
  - changed-path governance hygiene checker
  - changed-path negative fixture checks in GitHub Actions
  - whitespace diff check
```

## What Still Requires Human Judgment

```yaml
requires_human_judgment:
  - deciding whether a policy change is semantically safe
  - deciding whether a runtime-specific profile is accurate
  - approving human-gated operations
  - resolving contradictions between canonical documents
  - assessing product positioning and release readiness
  - approving schema breaking changes
  - deciding whether a PR should split high-risk and low-risk work
  - reviewing ambiguous security/storage boundary changes
```

Human judgment should be durable. When used, it should be recorded in an issue,
PR comment, approval record, or handoff document.

## How Each PR Should Make The Framework Stronger

Each governance PR should do at least one of these:

```yaml
strengthening_modes:
  clarify_policy:
    example: add or tighten a control document
  improve_checklist:
    example: add required issue or PR fields
  add_validation:
    example: encode a rule in a script or CI step
  add_negative_case:
    example: add an expected-failure fixture
  improve_context_efficiency:
    example: reduce default read set or clarify canonical ownership
  improve_handoff:
    example: make current state easier for a new agent to resume
  narrow_scope:
    example: defer unstable runtime-specific work to v2.0
```

A PR that only adds more prose without improving clarity, enforceability, or
handoff quality should be questioned.

## Current Strategic Boundary

ASGK v1.x should continue hardening the generic governance core:

```text
task packet schema
issue and PR templates
validation scripts
context budget policy
negative test suite
merge decision record
handoff discipline
first CLI wrapper
PR-body/task-packet validation
```

ASGK v2.0 may add runtime-specific profiles, but only after the core is stable
and only with vendor documentation plus observed behavior.

## Open Evolution Questions

```yaml
open_questions:
  - Should PR-body validation be implemented before or after the first CLI wrapper?
  - Should task-packet parsing remain dependency-free or allow PyYAML later?
  - Should negative tests be grouped into one CI job or split by category?
  - Should handoff generation be a CLI command or template-first process?
  - What is the minimum v1.0 release checklist?
```
