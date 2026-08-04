# ASGK Skill Pack

Status: source-distributed v0 skill pack.

ASGK skills are reusable operating procedures for agents working in an
ASGK-governed repository. They reduce repeated rule reading and after-the-fact
reasoning, but they do not become a new authority layer.

```yaml
skill_pack_rule:
  skills_do_not_add_new_gates: true
  skills_guide_reasoning_and_existing_boundaries: true
  skills_do_not_predetermine_assessment_outcomes: true
  durable_authority:
    current_work:
      - selected durable GitHub issue or qualifying pull request
    rules_and_contracts:
      - applicable canonical repository rules, contracts, and decision records
    gated_decisions:
      - explicit durable human decision when an existing gate requires one
  mechanical_evidence_and_enforcement:
    - ASGK validators
  model_judgment:
    - interprets evidence and makes semantic recommendations within the durable work unit
    - does not create task authority or satisfy an existing human gate
  validator_limits:
    - validators do not create scope or decision authority
    - validators do not approve work or satisfy a human gate
    - a pass proves only the named checks at their stated proof boundary
```

## Frontier-Guided Assessment Contract

Introducing ASGK into another repository, or materially upgrading an existing
adoption, is a read-only, context-sensitive assessment normally performed by a
human-selected frontier-capability model. ASGK does not choose, route,
schedule, switch, price-tier, or orchestrate that evaluator.

For these assessments, the Skill guides:

- bounded target discovery and evidence gathering;
- comparison of target responsibilities with relevant ASGK capabilities;
- universal safety invariants and existing high-risk boundaries;
- alternatives, tradeoffs, confidence, unknowns, and stop behavior;
- recording the recommendation in existing issue, PR, or handoff lineage.

The evaluator uses target evidence and its reasoning to judge fit, appropriate
governance depth, minimum sufficient adaptation, and whether any change should
be recommended. A Skill must not replace that judgment with a universal file
shape, fixed install bundle, module picker, adopter configuration, adoption
declaration, predetermined recommendation, or new approval layer.

Deterministic tools may collect observations, check universal invariants, and
test concrete mechanically verifiable claims. They must state what was checked
and what remains unproved. A command result does not decide target
architecture, adoption fit, or semantic completeness.

The read-only assessment adds no human gate. Existing human gates apply only
when a proposed implementation touches a concrete operation already defined as
human-gated.

## Usage Modes

### Client-installed mode

Copy one or more directories under `skills/` into the user's agent client skill
location, such as a Codex skills directory or an equivalent client-specific
skill mechanism.

Use this mode when the agent client supports native skill discovery. The skill
metadata can trigger at the right moment without loading all ASGK rules into the
conversation.

### Repository-reference mode

Keep `skills/` in the repository as source-distributed procedures. Agents that
do not have native skill installation can read a specific `SKILL.md` only when a
work unit needs that procedure.

Use this mode for portability. The repository still works without client-native
skill installation because durable task and decision authority remains in the
selected durable GitHub issue or qualifying pull request, applicable canonical
repository rules, contracts, and decision records, and explicit durable human
decisions when an existing gate requires one. Validators continue to produce
bounded mechanical evidence and enforce only their declared contracts.

## Included Skills

```yaml
core_skills:
  startup: skills/asgk-startup/SKILL.md
  issue_scoping: skills/asgk-issue-scoping/SKILL.md
  pr_evidence_merge_decision: skills/asgk-pr-evidence-merge-decision/SKILL.md
  gatekeeper: skills/asgk-gatekeeper/SKILL.md
  post_merge_closeout: skills/asgk-post-merge-closeout/SKILL.md
  current_status_handoff: skills/asgk-current-status-handoff/SKILL.md
  evidence_audit: skills/asgk-evidence-audit/SKILL.md
release_skills:
  release_prep: skills/asgk-release-prep/SKILL.md
assessment_and_transfer_skills:
  target_install_audit: skills/asgk-target-install-audit/SKILL.md
  upgrade_audit: skills/asgk-upgrade-audit/SKILL.md
  governance_health_check: skills/asgk-governance-health-check/SKILL.md
```

## When To Use Each Skill

```yaml
every_session:
  - startup

before_work:
  - issue_scoping

opening_or_updating_pr:
  - pr_evidence_merge_decision
  - gatekeeper

after_merge:
  - post_merge_closeout
  - current_status_handoff

when_claims_matter:
  - evidence_audit

when_planning_or_executing_release:
  - release_prep
  - evidence_audit

when_adopting_asgk_elsewhere:
  - target_install_audit

when_updating_existing_asgk_adoption:
  - upgrade_audit

weekly_or_milestone_review:
  - governance_health_check
```

## Design Constraints

- A skill may guide or draft work, but executable scope normally lives in a
  current GitHub issue or already-open PR. Repo files may own explicitly
  docs-only planning/control work. Task packets are only issue refinements or,
  during verified GitHub unavailability, complete fallbacks for bounded local
  work that must be transferred to an issue before PR or merge.
- A read-only assessment does not need implementation allowed paths or a new
  approval. Any later write still needs target-owned issue or PR authority,
  allowed paths, validation, and any explicit human approval required by an
  existing gate.
- A skill must stop when the authority, evidence, validation, or exact existing
  human gate required for its current action is missing.
- A skill may call existing validators only at their documented proof boundary.
  A validator result is evidence about the named checks, not task scope,
  approval, semantic correctness, or merge authority.
- Assessment skills should output `assessment_complete` or `blocked`, never
  `approved`. Record an exact existing gate separately as `next_action_gate`;
  semantic judgment alone does not trigger it.
- Assessment skills must expose evidence limits, confidence, and material
  unknowns.
- If a skill conflicts with `AGENTS.md`, a GitHub issue or PR, or a control
  document, the skill loses.

## Maintenance Touchpoints

Architecture is canonical. Skills are downstream procedures. Validators check
artifacts and enforce configured mechanical contracts; they do not own task
scope or decision authority.

Do not add a separate skill-compliance checker. Keep skills synchronized by
making architecture, policy, template, or validator PRs declare whether they
affect the skill pack.

```yaml
maintenance_rule:
  architecture_is_canonical: true
  skills_are_downstream: true
  validators_check_artifacts: true
  validators_create_authority: false
  no_skill_compliance_checker: true
```

### Touchpoint Map

```yaml
architecture_touchpoints:
  AGENTS.md:
    affected_skills:
      - asgk-startup
      - asgk-issue-scoping
      - asgk-gatekeeper
      - asgk-upgrade-audit

  docs/control/CURRENT_STATUS_POLICY.md:
    affected_skills:
      - asgk-current-status-handoff
      - asgk-post-merge-closeout
      - asgk-upgrade-audit

  docs/control/SOURCE_ONLY_RELEASE_POLICY.md:
    affected_skills:
      - asgk-release-prep
      - asgk-current-status-handoff
      - asgk-post-merge-closeout

  docs/control/HUMAN_GATED_OPERATIONS.md:
    affected_skills:
      - asgk-issue-scoping
      - asgk-gatekeeper
      - asgk-pr-evidence-merge-decision
      - asgk-release-prep
      - asgk-upgrade-audit

  docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md:
    affected_skills:
      - asgk-gatekeeper
      - asgk-pr-evidence-merge-decision

  docs/control/MERGE_DECISION_RECORD.md:
    affected_skills:
      - asgk-pr-evidence-merge-decision
      - asgk-gatekeeper

  docs/control/TASK_PACKET_FORMAT.md:
    affected_skills:
      - asgk-issue-scoping
      - asgk-startup
      - asgk-target-install-audit
      - asgk-upgrade-audit

  docs/control/TARGET_INSTALL_CHECKLIST.md:
    affected_skills:
      - asgk-target-install-audit
      - asgk-upgrade-audit

  docs/control/AGENT_CAPABILITY_MATRIX.md:
    affected_skills:
      - asgk-target-install-audit
      - asgk-upgrade-audit

  docs/INSTALL_SURFACE.md:
    affected_skills:
      - asgk-target-install-audit
      - asgk-upgrade-audit

  scripts/asgk.py:
    affected_skills:
      - asgk-gatekeeper
      - asgk-post-merge-closeout
      - asgk-current-status-handoff
      - asgk-evidence-audit
      - asgk-release-prep
      - asgk-target-install-audit
      - asgk-upgrade-audit
      - asgk-governance-health-check

  scripts/pr_governance_preflight.py:
    affected_skills:
      - asgk-pr-evidence-merge-decision
      - asgk-gatekeeper
      - asgk-upgrade-audit

  .github/PULL_REQUEST_TEMPLATE.md:
    affected_skills:
      - asgk-pr-evidence-merge-decision
      - asgk-gatekeeper
      - asgk-upgrade-audit

  .github/ISSUE_TEMPLATE/agent_task.yml:
    affected_skills:
      - asgk-issue-scoping
      - asgk-upgrade-audit

  docs/handoff/CURRENT_STATUS.md:
    affected_skills:
      - asgk-startup
      - asgk-current-status-handoff
      - asgk-post-merge-closeout
      - asgk-release-prep
      - asgk-governance-health-check
```

### Impact Guidance

```yaml
skill_pack_impact:
  not_required_when:
    - wording-only changes do not alter procedure, command names, required fields, or stop conditions
    - fixture-only changes preserve existing validator behavior
    - product docs change without affecting ASGK workflow

  review_required_when:
    - AGENTS.md changes
    - docs/control/** policy changes
    - scripts/asgk.py validator behavior changes
    - .github issue or PR templates change
    - docs/INSTALL_SURFACE.md changes
    - current-status policy meaning changes

  update_required_when:
    - a command used by a skill is renamed or removed
    - required artifact fields change
    - procedure order changes
    - stop conditions change
    - a canonical document path moves
    - a skill repeats old rule text instead of pointing to the canonical source
```

When skill impact is reviewed, record it in the PR evidence or Merge Decision
context. Use existing PR surfaces; do not create a new required PR template
section unless a later dedicated issue explicitly chooses that path.

## Field-Test Sequence

Use this sequence for the first real example:

```text
startup
  -> issue_scoping
  -> bounded implementation
  -> pr_evidence_merge_decision
  -> gatekeeper
  -> merge
  -> post_merge_closeout
  -> current_status_handoff
  -> governance_health_check
```

Use this sequence for adoption testing:

```text
target_install_audit
  -> read-only target discovery and frontier judgment
  -> evidence-backed assessment in existing target issue, PR, or handoff lineage
  -> bounded target-owned implementation issue or PR only if change is recommended
```

Use this sequence for existing ASGK adoption upgrades:

```text
upgrade_audit
  -> read-only source-delta and target-state comparison
  -> frontier judgment in existing target issue, PR, or handoff lineage
  -> bounded target-owned implementation issue or PR only if change is recommended
```

Use this sequence for source-only release work:

```text
release_prep
  -> evidence_audit
  -> gatekeeper
  -> release execution only after explicit human approval
  -> release_prep closeout
  -> current_status_handoff
```
