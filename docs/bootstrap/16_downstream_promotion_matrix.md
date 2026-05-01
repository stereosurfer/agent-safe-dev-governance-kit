# 16 Downstream Promotion Matrix

| From | To | Required gate |
|---|---|---|
| prepared input | candidate artifact | source/input contract |
| candidate artifact | validated artifact | schema validation |
| validated artifact | promoted artifact | promotion gate |
| promoted artifact | output-eligible artifact | readiness audit |
| output-eligible artifact | public/export artifact | human or release gate |

## Boundary

A row may be traceable and still blocked from promotion. Reasons include thin context, class/use mismatch, missing variant scope, audit-only route, unresolved human gate, or missing downstream readiness.
