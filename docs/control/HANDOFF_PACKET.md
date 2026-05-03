# Handoff Packet

Status: active control specification.

This document defines the generic, runtime-agnostic handoff packet used when a
human, AI agent, model, IDE, browser session, or automation runner must stop and
another actor must safely continue.

## Purpose

A handoff packet prevents work from being trapped in chat, local memory, or an
agent-specific runtime. It makes the next safe action recoverable from durable
repository and GitHub state.

```text
A new actor should be able to resume from the handoff packet without reading the
previous chat transcript.
```

## Scope

This is a v1.x generic handoff mechanism. It is not a Codex, OpenGoat, Claude
Code, Cursor, Copilot, or ChatGPT-specific adapter.

Runtime-specific adapters may optimize how a tool consumes this packet in v2.0,
but they must not bypass the fields, stop conditions, validation, or merge gates
specified here.

## Recommended Flow

Use this sequence:

```text
handoff-template
  -> AI fills judgment-heavy fields
  -> handoff-check
  -> human or next agent reads packet
```

The template command creates a safe draft. It does not claim final judgment and
it does not write files automatically.

```bash
python3 scripts/asgk.py handoff-template \
  --issue "#40 [TOOLS] Add handoff-template command" \
  --pr "none; PR not opened yet" \
  --branch "codex/add-handoff-template" \
  --objective "Add an AI-fillable handoff packet template command."
```

After AI or a human fills the TODO fields, validate the result:

```bash
python3 scripts/asgk.py handoff-check --file handoff.yaml
```

## Required Handoff Packet

```yaml
handoff_packet:
  active_issue:
  active_pr:
  branch:
  objective:
  current_state:
  completed:
  remaining:
  allowed_paths:
  modified_files:
  validation_status:
  blockers:
  next_safe_action:
  must_read:
  must_not_do:
  decisions:
  open_questions:
```

## Field Requirements

| Field | Required | Meaning | Block when |
|---|---:|---|---|
| `active_issue` | yes | GitHub issue number/title or durable repo document. | missing, empty, or `see chat` |
| `active_pr` | yes | Active PR number/title, or `none` with reason. | missing or ambiguous |
| `branch` | yes | Current branch for the work unit, or `none` with reason. | missing or unknown |
| `objective` | yes | One concrete result for the active work unit. | missing, vague, or chat-only |
| `current_state` | yes | Current repo/task state in one compact paragraph or YAML object. | missing |
| `completed` | yes | Completed steps or outputs. | missing |
| `remaining` | yes | Remaining bounded work. | missing |
| `allowed_paths` | yes | Paths the next actor may touch. | missing, empty, or too broad |
| `modified_files` | yes | Files already modified in the active branch/PR. | missing or unknown when PR exists |
| `validation_status` | yes | Pass/fail/blocked/not-run plus command evidence. | missing, `unknown`, or ungrounded |
| `blockers` | yes | Current blockers or `none`. | missing |
| `next_safe_action` | yes | The next single safe action. | missing, empty, or multiple ambiguous actions |
| `must_read` | yes | Minimal read set for the next actor. | missing or too broad |
| `must_not_do` | yes | Actions forbidden for the next actor. | missing |
| `decisions` | yes | Durable decisions already made. | missing |
| `open_questions` | yes | Questions requiring human/reviewer judgment, or `none`. | missing |

## Minimal Valid Example

```yaml
handoff_packet:
  active_issue: "#27 [TOOLS] Add cross-agent handoff and validation CLI core"
  active_pr: "none; PR not opened yet"
  branch: "codex/cross-agent-handoff-cli-core"
  objective: "Add generic handoff packet spec and minimal ASGK validation CLI."
  current_state: "Issue and branch created; implementation in progress."
  completed:
    - "Created issue."
    - "Created branch."
  remaining:
    - "Add docs/control/HANDOFF_PACKET.md."
    - "Add scripts/asgk.py."
    - "Open PR and wait for Actions."
  allowed_paths:
    - "scripts/asgk.py"
    - "docs/control/HANDOFF_PACKET.md"
    - "docs/control/CONTEXT_BUDGET_POLICY.md"
    - "docs/adapters/README.md"
    - "docs/adapters/ADAPTER_TEMPLATE.md"
    - "docs/DOCUMENT_MAP.md"
  modified_files:
    - "docs/control/HANDOFF_PACKET.md"
  validation_status:
    status: "not_run"
    reason: "PR not opened yet"
    commands:
      - "python3 scripts/check_project.py"
      - "python3 scripts/validate_bootstrap.py"
  blockers: "none"
  next_safe_action: "Add scripts/asgk.py, then open PR."
  must_read:
    - "AGENTS.md"
    - "docs/handoff/CURRENT_STATUS.md"
    - "GitHub issue #27"
    - "docs/control/HANDOFF_PACKET.md"
    - "docs/DOCUMENT_MAP.md"
  must_not_do:
    - "Do not implement runtime-specific adapters."
    - "Do not add dependencies."
    - "Do not modify CI unless explicitly required."
  decisions:
    - "v1.x remains generic/runtime-agnostic."
  open_questions: "none"
```

## Validation Status Values

```yaml
validation_status_values:
  pass:
    meaning: required validation commands passed
  fail:
    meaning: validation failed and output must be recorded
  blocked:
    meaning: validation cannot proceed because a gate or dependency is missing
  not_run:
    meaning: validation has not been run; reason required
```

`unknown` is not valid. If status is not known, write `not_run` or `blocked` and
explain why.

## Required Recovery Read Set

When recovering from a handoff, the next actor should use the
`handoff_recovery` context profile from `docs/control/CONTEXT_BUDGET_POLICY.md`.

Minimum read set:

```yaml
handoff_recovery:
  always_read:
    - AGENTS.md
    - docs/handoff/CURRENT_STATUS.md
    - active GitHub issue
    - active PR if one exists
    - docs/control/HANDOFF_PACKET.md
    - docs/DOCUMENT_MAP.md
  read_from_packet:
    - must_read
    - modified_files
    - allowed_paths
```

## Stop Conditions

The next actor must stop when:

- `active_issue` is missing or says `see chat`.
- `validation_status` is `unknown`.
- `next_safe_action` is empty.
- `allowed_paths` is missing or too broad.
- `must_read` is missing.
- The active PR changed files outside `allowed_paths`.
- The packet conflicts with the active issue or PR.
- A human-gated operation appears without durable approval.

## Relationship To Other Documents

```yaml
related_docs:
  current_status: docs/handoff/CURRENT_STATUS.md
  document_map: docs/DOCUMENT_MAP.md
  context_budget: docs/control/CONTEXT_BUDGET_POLICY.md
  issue_hygiene: docs/control/ISSUE_HYGIENE_GATE.md
  pr_review: docs/control/PR_REVIEW_CHECKLIST.md
  merge_decision: docs/control/MERGE_DECISION_RECORD.md
```

`CURRENT_STATUS.md` is the repo-level handoff surface. A handoff packet is the
work-unit-level recovery object.

## Automation Boundary

`handoff-template` may create a draft. It must not:

- invent final decisions;
- claim validation passed without evidence;
- replace human judgment;
- automatically write repository files;
- call GitHub or external APIs;
- fill runtime-specific adapter behavior.

The first stable pattern is:

```text
Generate draft -> AI fills TODOs -> run handoff-check -> human/reviewer accepts.
```

## Future Automation

The minimum CLI check is:

```bash
python3 scripts/asgk.py handoff-check --file <handoff-packet-file>
```

The check should block missing required fields, `see chat`, empty
`next_safe_action`, `validation_status: unknown`, missing `allowed_paths`, and
missing `must_read`.
