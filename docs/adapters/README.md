# Adapters

Status: v1.x adapter mechanism and v2.0 runtime-profile placeholder.

Adapters describe how a person, tool, or runtime should consume ASGK governance
surfaces. In v1.x this directory provides only generic adapter mechanics and a
template. Runtime-specific adapters are deferred to v2.0.

## v1.x Rule

```text
Use the generic ASGK governance core.
Do not implement runtime-specific adapter behavior in v1.x.
```

A human, AI model, IDE assistant, browser connector, or automation tool may use
ASGK in v1.x when it follows the same generic governance surfaces:

```text
issue -> branch -> allowed-path change -> PR -> validation -> Merge Decision -> handoff
```

## v2.0 Planned Runtime Adapters

Runtime-specific adapter files may be added in v2.0, after vendor documentation
and observed tests are available.

Planned examples:

```text
docs/adapters/CODEX.md
docs/adapters/CHATGPT_WEB_GITHUB_CONNECTOR.md
docs/adapters/CLAUDE_CODE.md
docs/adapters/CURSOR.md
docs/adapters/COPILOT.md
docs/adapters/OPENGOAT.md
docs/adapters/HUMAN.md
```

These are optimization adapters, not replacements for ASGK core governance.

## Adapter Requirements

Each future adapter must answer:

```yaml
adapter:
  runtime_name:
  runtime_type:
  startup_read_set:
  handoff_recovery_read_set:
  validation_commands:
  how_to_update_handoff:
  capabilities_not_to_assume:
  failure_exit_behavior:
  required_asgk_controls:
  vendor_docs:
  observed_tests:
```

## Current Template

Use `docs/adapters/ADAPTER_TEMPLATE.md` as the structure for future v2.0 adapter
work. Do not fill it with vendor-specific claims until the relevant runtime is
researched and tested.
