# Adapter Template

Status: v2.0 template; do not use as an implemented runtime-specific adapter until completed with vendor documentation and observed tests.

## Runtime Identity

```yaml
runtime_name:
runtime_type:
version_or_date_checked:
vendor_docs:
observed_tests:
```

## Startup Read Set

```yaml
startup_read_set:
  always_read:
    - AGENTS.md
    - README.md
    - docs/handoff/CURRENT_STATUS.md
    - current GitHub issue or PR
  optional_read:
    - docs/DOCUMENT_MAP.md
    - docs/control/CONTEXT_BUDGET_POLICY.md
```

## Handoff Recovery Read Set

```yaml
handoff_recovery_read_set:
  always_read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - active issue
    - active PR if one exists
    - docs/control/HANDOFF_PACKET.md
    - docs/DOCUMENT_MAP.md
  read_from_packet:
    - must_read
    - modified_files
    - allowed_paths
```

## How To Run Validation

```yaml
validation_commands:
  baseline:
    - python3 scripts/asgk.py doctor
  hygiene:
    - python3 scripts/asgk.py hygiene --paths-file changed-paths.txt
  handoff:
    - python3 scripts/asgk.py handoff-check --file handoff.yaml
```

## How To Update Handoff

```yaml
handoff_update:
  update_surfaces:
    - docs/handoff/CURRENT_STATUS.md
    - active PR body or comment
    - active GitHub issue comment
  required_fields:
    - active_issue
    - active_pr
    - branch
    - objective
    - current_state
    - completed
    - remaining
    - allowed_paths
    - modified_files
    - validation_status
    - blockers
    - next_safe_action
    - must_read
    - must_not_do
    - decisions
    - open_questions
```

## Capabilities Not To Assume

```yaml
capabilities_not_to_assume:
  - can run shell commands
  - can access local filesystem
  - can push branches
  - can open pull requests
  - can read private repository content
  - can see GitHub Actions result
  - can preserve long context
  - can use paid/API quota
```

## Failure Exit Behavior

```yaml
failure_exit_behavior:
  on_missing_context: create handoff packet and stop
  on_validation_failure: record command and output, do not claim pass
  on_forbidden_path: stop and report
  on_human_gate: stop until durable approval exists
  on_runtime_limit: update handoff and stop
```

## Required ASGK Controls

```yaml
required_asgk_controls:
  - GitHub issue or durable repo document as source of truth
  - allowed paths
  - context profile
  - validation evidence
  - Merge Decision Record
  - Handoff Packet when interrupted or switching tools
```

## Adapter Completion Criteria

A runtime-specific adapter is complete only when:

- vendor documentation is cited or recorded;
- observed behavior tests are listed;
- unsupported capabilities are explicitly named;
- startup and handoff recovery behavior is tested;
- it does not bypass ASGK v1.x governance core.
