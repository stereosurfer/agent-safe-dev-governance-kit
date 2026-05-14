# Autonomous Multi-agent Runbook

This runbook allows multiple agent windows or sub-agents to work without requiring the user to manually shuttle instructions.

## Controller duties

The controller owns:

- `docs/control/`
- `docs/handoff/`
- `CURRENT_STATUS.md`
- merge order
- lane status
- validation before commit/push
- worker assignment packets
- failure thresholds and notification conditions

Before spawning a worker for executable work, the controller must create or
select a GitHub issue or already-open pull request with objective, plan,
checklist, acceptance sheet, allowed paths, expected output, non-goals, stop
conditions, and rollback expectations. Task packets may narrow and route that
GitHub scope; they must not replace it when GitHub is available.

## Worker duties

Each worker owns one lane packet from `agent/task_packets/`.

A worker must:

- read `AGENTS.md`;
- read its lane packet;
- read the durable GitHub issue or PR;
- stay inside allowed paths;
- avoid reverting unrelated changes;
- run relevant validation;
- produce an Agent Report;
- stop at the stop condition.

## First autonomous batch pattern

Use disjoint write paths:

```text
L01 Architecture / docs only
L02 Schema / contracts only
L03 Backend pipeline only
L04 UI skeleton only
L05 Security / path hygiene only
L06 CI / GitHub governance only
```

## Integration loop

1. Spawn lane workers only after durable packets exist.
2. Controller maintains `LANE_STATUS.md`.
3. Review worker changes by file scope.
4. Resolve conflicts without overwriting unrelated lane work.
5. Run validation.
6. Commit one coherent batch or split commits by lane.
7. Push and open/update PR.
8. Update handoff.
9. Stop unless the next lane is explicitly unlocked.

## Stop conditions

Stop the autonomous run when a lane needs:

- new parser/model dependency;
- new cloud egress;
- Google Drive API;
- MCP tool or MCP write capability;
- schema breaking change;
- database migration beyond additive draft work;
- broader filesystem permission;
- destructive operation;
- private source documents.
