# 13 Artifact Promotion Policy

Traceability is required, but traceability alone is not enough.

## Promotion chain

```text
raw_or_prepared_input
  -> candidate_artifact
  -> validated_artifact
  -> promoted_artifact
  -> output_eligible_artifact
```

## Required promotion fields

```yaml
promotion_record:
  artifact_id:
  source_or_input_class:
  claim_or_use_type:
  context_signals:
  allowed_downstream_uses:
  blocked_downstream_uses:
  validation_status:
  promotion_status:
  reason:
```

## Status values

```yaml
promotion_status:
  - promoted
  - blocked_thin_context
  - blocked_route_audit_only
  - blocked_class_use_mismatch
  - blocked_variant_scope_missing
  - blocked_unvalidated_input
  - blocked_human_gate_required
```

Use `docs/bootstrap/15_source_or_input_class_matrix.md` and `docs/bootstrap/16_downstream_promotion_matrix.md` for the matrix.
