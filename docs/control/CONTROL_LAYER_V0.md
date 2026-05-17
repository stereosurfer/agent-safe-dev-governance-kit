# Control Layer v0

Status: active governance template.

This document defines how agents, GitHub issues, pull requests, repository
artifacts, and handoff documents coordinate so the project does not depend on
chat history as the control mechanism.

## Purpose

Every significant project change should be:

- stateful;
- inspectable;
- resumable;
- reviewable;
- traceable;
- convertible into the next bounded work unit.

## Durable Control Surfaces

| Surface | Role |
|---|---|
| `AGENTS.md` | Repository operating rules and required checks. |
| `README.md` | Project mission and discoverability. |
| `docs/handoff/CURRENT_STATUS.md` | Compact current state for new sessions. |
| `docs/control/` | Durable control documents. |
| `templates/` | Non-authoritative starter material for target repos or task packets. |
| GitHub issues | Work contracts, scope, acceptance, stop conditions. |
| GitHub PRs | Proposed changes, validation evidence, review state, merge boundary. |
| GitHub comments | Blockers, smoke-test evidence, issue closeout, handoff notes. |

Chat logs can guide work, but they are not authoritative.

When GitHub is available, executable work starts from a GitHub issue or an
already-open PR. A repo task packet may narrow or route that scope, but it must
not replace the issue or PR as primary authorization.

## Work Unit State Model

```text
idea -> scoped -> in_progress -> pr_open -> needs_review -> needs_revision | blocked | accepted -> merged -> closed
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
  - state:scoped
  - state:in-progress
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

Use `docs/control/TASK_PACKET_FORMAT.md`,
`templates/task_packet.template.yaml`, and
`examples/task_packet.example.yaml`.

Task packets are optional refinements for an issue or PR. They may narrow scope,
record read sets, or preserve handoff detail, but they are not executable
authority by themselves when GitHub is available.

## Agent Report Format

Use `docs/control/AGENT_REPORT_FORMAT.md` and
`examples/agent_report.example.md`.

## Operating Loop

1. Human gives direction or a durable issue/PR exists.
2. Agent checks repo and live GitHub state.
3. Agent confirms one current work unit, allowed paths, validation, and stop
   conditions.
4. Agent implements only the authorized scope.
5. Agent opens or updates one PR with validation evidence and merge decision
   state.
6. Reviewer evaluates diff, tests, evidence, and boundaries.
7. Work returns accepted, needs revision, or blocked.
8. Low-risk merge policy or human gate decides merge.
9. Issue closeout and handoff are updated when authorized.
10. Agent stops unless explicitly authorized to continue.

## Anti-drift Rules

1. Do not rely on chat memory as project memory.
2. Do not implement future capabilities from roadmap text alone.
3. Do not treat traceability as promotion eligibility.
4. Do not collapse source material, research context, and validation metadata.
5. Do not bypass storage boundaries for convenience.
6. Do not expand external calls, cloud, MCP, parser/model dependencies, or
   publication without a scoped gate.
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

## First Control Tasks

1. Create or customize this control layer.
2. Add issue and PR templates.
3. Audit and update `docs/handoff/CURRENT_STATUS.md`.
4. Run `scripts/validate_bootstrap.py`.

## Definition of Done

The control layer is minimally operational when:

- durable control documents exist;
- task packet and agent report formats exist;
- GitHub issue and PR templates enforce required fields;
- validation scripts check required files and terms;
- the next task can be generated without re-explaining the entire project in
  chat.
