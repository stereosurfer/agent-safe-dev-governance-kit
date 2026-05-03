# Lane Status

Status: current snapshot.

This file is overwritten, not appended. It is a compact lane-level status board,
not a lane history log. Lane movement history belongs in GitHub issues, PRs,
comments, and merge commits.

| Lane | Status | Owner | Durable source | Allowed paths | Blocker | Next action |
|---|---|---|---|---|---|---|
| lane_00_controller | active | controller | docs/control/AUTONOMOUS_RUNBOOK.md | docs/control/, docs/handoff/ | none | maintain queue |
| lane_01_architecture | queued | unassigned | agent/task_packets/lane_01_architecture.yaml | docs/architecture/ | none | assign when needed |
| lane_02_schema_contracts | queued | unassigned | agent/task_packets/lane_02_schema_contracts.yaml | contracts/, schemas/ | none | assign when needed |

## Allowed lane statuses

```text
queued
unlocked
active
blocked
needs_review
complete
merged
```
