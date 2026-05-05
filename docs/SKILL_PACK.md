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
