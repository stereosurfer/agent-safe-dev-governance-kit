# ASGK Skill Pack

Status: source-distributed v0 skill pack.

ASGK skills are reusable operating procedures for agents working in an
ASGK-governed repository. They reduce repeated rule reading and after-the-fact
reasoning, but they do not become a new authority layer.

```yaml
skill_pack_rule:
  skills_do_not_add_new_gates: true
  skills_select_and_sequence_existing_gates: true
  final_authority:
    - GitHub issues
    - GitHub pull requests
    - repository files
    - ASGK validators
    - human gates where required
```

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
skill installation because `AGENTS.md`, GitHub issues, PRs, repository docs, and
validators remain authoritative.

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

when_adopting_asgk_elsewhere:
  - target_install_audit

when_updating_existing_asgk_adoption:
  - upgrade_audit

weekly_or_milestone_review:
  - governance_health_check
```

## Design Constraints

- A skill may draft or route work, but durable scope must live in GitHub or repo
  files.
- A skill must stop when required inputs, allowed paths, validation, or human
  approval are missing.
- A skill should call existing validators instead of creating parallel checks.
- A skill should output `blocked`, `eligible`, or `requires_human`, not
  `approved`.
- If a skill conflicts with `AGENTS.md`, a GitHub issue or PR, or a control
  document, the skill loses.

## Maintenance Touchpoints

Architecture is canonical. Skills are downstream procedures. Validators check
artifacts.

Do not add a separate skill-compliance checker. Keep skills synchronized by
making architecture, policy, template, or validator PRs declare whether they
affect the skill pack.

```yaml
maintenance_rule:
  architecture_is_canonical: true
  skills_are_downstream: true
  validators_check_artifacts: true
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

  docs/control/HUMAN_GATED_OPERATIONS.md:
    affected_skills:
      - asgk-issue-scoping
      - asgk-gatekeeper
      - asgk-pr-evidence-merge-decision
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

  docs/control/TARGET_INSTALL_CHECKLIST.md:
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
      - asgk-target-install-audit
      - asgk-upgrade-audit
      - asgk-governance-health-check

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
  -> adoption readiness report
  -> bounded adoption issue
  -> adoption PR plan
```

Use this sequence for existing ASGK adoption upgrades:

```text
upgrade_audit
  -> upgrade audit report
  -> bounded upgrade issue
  -> manual merge or safe reusable-surface update plan
```
