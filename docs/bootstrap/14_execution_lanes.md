# 14 Execution Lanes

Execution lanes define whether external calls, model calls, or human-operated steps are allowed.

```yaml
execution_lanes:
  deterministic:
    live_external_call: false
    model_call: false
    default: true

  codex_operated:
    live_external_call: false
    model_call_inside_runtime: false
    import_required: true

  api_provider:
    live_external_call: explicit_only
    requires_provider_model_config: true
    requires_allow_live_call_flag: true
    audit_required: true

  cloud_service:
    live_external_call: human_gated
    default: false

  future_only:
    implementation_allowed: false
```

## Readiness rule

No `api_provider` or `cloud_service` lane may run until `docs/bootstrap/17_readiness_audit_policy.md` passes.

## Fallback rule

Deterministic fallback may prove structure. It must not be treated as reader-quality, production-quality, or model-assisted success unless the acceptance criteria explicitly say so.
