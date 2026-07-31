# Handoff Packet

Status: active control specification.

This document defines the runtime-agnostic work-unit packet used when a human
or AI must stop and another actor must safely continue.

## Purpose

The packet makes six things immediately recoverable:

1. what to do;
2. where to work;
3. what is outside the work;
4. which actions or paths are forbidden;
5. what evidence currently exists;
6. the next safe action.

It does not replace the live issue or PR, repeat close-out history, or carry
authority from a previous chat.

```text
A new actor should be able to resume from durable repository and GitHub state
without reading the previous conversation.
```

## Canonical Shape

The machine-readable projection of this canonical contract is
`schemas/handoff_packet.schema.json`.

The following is an illustrative W3B self-use example, not current work
authority. Its issue, branch, state, and next action are example data and grant
no authority.

```yaml
handoff_packet:
  active_issue: "#333 ASGK 2.0 W3B"
  active_pr: "none; PR not opened yet"
  durable_source_of_truth:
    - "GitHub issue #333"
    - "GitHub issue #323 owner-approved program comment"
  branch: "codex/asgk-2-w3b-handoff-status-convergence"
  objective: "Converge typed handoff and recovery-only CURRENT_STATUS."
  current_state: "Issue authority passed; implementation is in progress."
  remaining:
    - "Complete the bounded implementation and validation."
    - "Open a protected PR and obtain current-head human approval."
  allowed_paths:
    - "docs/control/HANDOFF_PACKET.md"
    - "schemas/handoff_packet.schema.json"
  modified_files:
    - "docs/control/HANDOFF_PACKET.md"
    - "schemas/handoff_packet.schema.json"
  non_goals:
    - "Do not implement W3C's global validation envelope."
  must_not_do:
    - "Do not modify paths outside issue #333."
    - "Do not infer approval from validator success."
  must_read:
    - "AGENTS.md"
    - "docs/handoff/CURRENT_STATUS.md"
    - "GitHub issue #333"
  validation_status:
    status: "not_run"
    evidence:
      - "Validation is pending until the bounded diff is complete."
    reason: "The work unit has not reached its validation step."
  blockers:
    - "none; no known blocker at this snapshot"
  next_safe_action: "Complete the issue #333 diff, then run its validation set."
```

The compact projection uses the same core fields under `compact_handoff` and
adds only `current_status_impact`; see
`docs/control/COMPACT_HANDOFF_PROFILE.md`.

## Field Contract

| Field | Type | What it answers |
|---|---|---|
| `active_issue` | material string | Which live issue is the current work authority? |
| `active_pr` | material string | Which PR carries the current diff, or why is there none? |
| `durable_source_of_truth` | non-empty string list | Which durable issue, PR, comment, or repo document must be trusted? |
| `branch` | material string | Where should repository work continue? |
| `objective` | material string | What bounded result is being produced? |
| `current_state` | material string | What is true at this recovery snapshot? |
| `remaining` | non-empty string list | What bounded work remains? |
| `allowed_paths` | non-empty string list | Where may the next actor write? |
| `modified_files` | non-empty string list | What has changed, or why has nothing changed? |
| `non_goals` | non-empty string list | What work is explicitly outside this unit? |
| `must_not_do` | non-empty string list | Which actions or paths are forbidden? |
| `must_read` | non-empty string list | What is the smallest recovery read set? |
| `validation_status` | typed mapping | What mechanical evidence exists and why is its status accurate? |
| `blockers` | non-empty string list | What blocks progress, or why are there no known blockers? |
| `next_safe_action` | material string | What single bounded action should happen next? |

`completed`, `decisions`, and `open_questions` are not packet fields. Completed
work and decision history belong in GitHub issues, PRs, comments, commits, and
close-out reviews. A current unresolved question is either a blocker, remaining
work, or a human gate and should be stated in the corresponding current field.

## Validation Status

```yaml
validation_status:
  status: pass | fail | blocked | not_run
  evidence:
    - "<command result, durable link, or material reason no command ran>"
  reason: "<why the selected status is accurate>"
```

`unknown`, a scalar `evidence`, an empty evidence list, or an absent reason is
invalid. `pass` describes only the recorded validation boundary; it never means
human approval, issue completion, PR readiness, or merge authority.

## Commands

Create an AI-fillable draft:

```bash
python3 scripts/asgk.py handoff-template \
  --issue "#333 ASGK 2.0 W3B" \
  --pr "none; PR not opened yet" \
  --branch "codex/asgk-2-w3b-handoff-status-convergence" \
  --objective "Converge typed handoff and recovery-only CURRENT_STATUS."
```

After every TODO has been replaced:

```bash
python3 scripts/asgk.py handoff-check \
  --file handoff.yaml \
  --fail-on-todo \
  --json
```

Every handoff check rejects TODO and AI_TODO markers, case-insensitively.
`--fail-on-todo` is retained as an explicit compatibility spelling for existing
callers; it does not make draft markers optional when omitted.

The dependency-free checker supports the mapping, list, scalar, and indentation
subset emitted by `handoff-template`. It rejects ambiguous or advanced YAML
instead of guessing.

## Durable Placement

A validated packet must be left where the next actor can actually recover it:

- in the active issue or PR body/comment; or
- in an explicitly issue-authorized repository handoff path.

Do not leave the only copy in chat, an untracked local file, a temporary
directory, or a provider-specific session. The packet remains a recovery
projection; the live issue or PR remains the work authority.

## Recovery Read Set

Begin with:

1. `AGENTS.md`;
2. `README.md`;
3. `docs/handoff/CURRENT_STATUS.md`;
4. the packet's active issue and PR;
5. the packet's `must_read` entries.

Use `docs/DOCUMENT_MAP.md` only when one of those surfaces points to more
context. Do not read every governance document by default.

## Stop Conditions

Stop instead of guessing when:

- the expected packet root or any required field is missing;
- a required scalar, list, or nested validation field has the wrong type;
- the packet says `see chat`;
- any check finds TODO or AI_TODO markers;
- the active issue or PR conflicts with the packet;
- changed paths exceed `allowed_paths`;
- a forbidden path or human-gated action is required;
- supplied evidence cannot support the claimed validation status.

## Proof Boundary

`handoff-check` mechanically checks the expected root, required types, material
content, supported validation-status enum, and selected forbidden markers.

It does not check:

- whether statements or references are true;
- whether GitHub links, issues, PRs, or branches are live;
- whether paths are authorized or a diff stays within them;
- whether commands actually produced the stated evidence;
- whether work is complete;
- whether a human gate, Merge Decision Record, or merge boundary is satisfied.

## Automation Boundary

`handoff-template` prints a draft. It does not write repository files, call an
external service, invent decisions, choose an Agent, or claim validation.

`handoff-check` validates only the supplied local packet. Acceptance and
execution remain with the receiving human or Agent under the live issue, PR,
and repository policies.
