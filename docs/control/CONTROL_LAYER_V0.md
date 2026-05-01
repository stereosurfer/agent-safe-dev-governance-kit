# Control Layer v0

Status: active governance template.

This document defines how agents, GitHub issues, pull requests, repository artifacts, and handoff documents coordinate so the project does not depend on chat history as the control mechanism.

## Purpose

Every significant project change should be:

- stateful;
- inspectable;
- resumable;
- reviewable;
- traceable;
- convertible into the next agent task.

## Durable Control Surfaces

| Surface | Role |
|---|---|
| `AGENTS.md` | Repository operating rules and required checks. |
| `README.md` | Project mission and discoverability. |
| `docs/handoff/CURRENT_STATUS.md` | Canonical current state for new sessions. |
| `docs/control/` | Durable control documents. |
| `agent/` | Role, lane, and task-packet definitions. |
| GitHub issues | Work contracts, assignment scope, acceptance, stop conditions. |
| GitHub PRs | Proposed changes, validation evidence, review state, merge boundary. |
| GitHub comments | Agent reports, blockers, smoke-test evidence, controller notes. |

Chat logs can guide work, but they are not authoritative.

## Work Unit State Model

```text
idea -> task_packet_ready -> agent_working -> pr_open -> needs_review -> needs_revision | blocked | accepted -> merged
```

A work unit must not jump from `idea` to `merged` without a review checkpoint.

## Label Vocabulary

Suggested labels:

```yaml
type:
  - type:control-layer
  - type:runtime
  - type:schema
  - type:test
  - type:docs
state:
  - state:task-packet-ready
  - state:agent-working
  - state:needs-review
  - state:needs-revision
  - state:blocked
  - state:accepted
risk:
  - risk:product-drift
  - risk:schema-instability
  - risk:no-validation
  - risk:large-diff
  - risk:missing-tests
priority:
  - priority:p0-control
  - priority:p1-mvp
  - priority:p2-later
```

Do not assume labels exist until a setup task creates them.

## Task Packet Format

Use `docs/control/TASK_PACKET_FORMAT.md` and `examples/task_packet.example.yaml`.

Required fields:

- task_id
- lane
- intelligence_level
- durable_source_of_truth
- objective
- product_context
- current_context
- files_to_inspect_first
- allowed_paths
- expected_changes
- expected_output
- non_goals
- constraints
- plan
- checklist
- acceptance_sheet
- validation_commands
- stop_conditions
- rollback_expectations

## Agent Report Format

Use `docs/control/AGENT_REPORT_FORMAT.md` and `examples/agent_report.example.md`.

## Operating Loop

1. Human gives direction or a durable issue exists.
2. Agent checks repo/GitHub state.
3. Architect compiles or confirms task packet.
4. Work unit enters task-packet-ready.
5. Worker executes only the packet.
6. Worker opens or updates one PR.
7. Worker posts Agent Report.
8. Reviewer evaluates report, diff, tests, and boundaries.
9. Work returns accepted, needs revision, or blocked.
10. Low-risk merge policy or human gate decides merge.
11. Handoff is updated.
12. Agent stops unless explicitly authorized to continue.

## Anti-drift Rules

1. Do not rely on chat memory as project memory.
2. Do not implement future capabilities from roadmap text alone.
3. Do not treat traceability as promotion eligibility.
4. Do not collapse source material, research context, and validation metadata.
5. Do not bypass storage boundaries for convenience.
6. Do not expand external calls, cloud, MCP, parser/model dependencies, or publication without a scoped gate.
7. Do not accept PRs without validation notes.

## Human Gates

Human approval is required for:

- destructive git operations;
- security boundary changes;
- storage boundary changes;
- schema major version changes;
- database migrations;
- new dependencies;
- new cloud egress;
- API/model calls enabled by default;
- MCP write capability;
- publication or release decisions;
- milestone closure when not explicitly delegated.

## First control tasks

1. Create or customize this control layer.
2. Add issue and PR templates.
3. Audit and update `docs/handoff/CURRENT_STATUS.md`.
4. Run `scripts/validate_bootstrap.py`.

## Definition of Done

The control layer is minimally operational when:

- durable control documents exist;
- task packet and agent report formats exist;
- GitHub issue and PR templates enforce required fields;
- agent rules define roles, lanes, intelligence levels, stop conditions;
- validation scripts check required files and terms;
- the next task can be generated without re-explaining the entire project in chat.
