# 17 Readiness Audit Policy

A readiness audit runs before prompt generation, external API calls, import, publication, export, or merge decisions that rely on generated artifacts.

## Required readiness artifact

```yaml
readiness_audit:
  run_id:
  lane:
  upstream_artifacts_checked:
  promotion_gate_status:
  unresolved_backlog_count:
  blocked_rows_count:
  live_external_call:
  provider:
  model:
  audit_logs:
  status: ready | blocked
  reason:
```

## Blocking conditions

- unresolved required backlog rows;
- no promotable artifact rows;
- output relies on blocked promotion evidence;
- deterministic fallback presented as production success;
- provider/model not configured for API lane;
- allow-live-call flag missing for live lane;
- audit metadata path missing.

## Logging expectations

```text
logs/model-calls.jsonl          # only simulations or live provider calls
logs/agent-operated-events.jsonl # codex/import/operator events
logs/readiness-audits.jsonl      # readiness audit events
```
