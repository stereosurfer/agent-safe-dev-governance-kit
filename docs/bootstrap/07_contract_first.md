# 07 Contract First

Every feature that creates, transforms, promotes, exports, or merges artifacts needs a contract first.

Each contract must define:

```yaml
name:
version:
input:
output:
required_fields:
validation_rules:
examples:
failure_modes:
promotion_rules:
```

Do not allow prose-only contracts for machine-validated artifacts.
