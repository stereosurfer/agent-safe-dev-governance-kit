# 15 Source or Input Class Matrix

This matrix prevents agents from treating every traceable input as equally strong.

| Class | May support | Must not support alone |
|---|---|---|
| official | identity, specs, release facts, official positioning | user experience, market consensus |
| technical_expert | repair, measurement, technical interpretation | official intent unless cited |
| community | usage context, recurring reports, cultural memory | hard technical claims, measured performance, official revision history |
| market | price snapshot, availability, ownership cost | circuit design, components, measured performance |
| prepared_private_note | curated context with provenance | publication-ready proof without review |
| route_only | planning, backlog, acquisition target | evidence or claim promotion |
| audit_metadata | validation and governance | reader-facing material density |

## Required fields

```yaml
source_or_input_class:
allowed_claim_types:
blocked_claim_types:
context_required:
review_required:
```
