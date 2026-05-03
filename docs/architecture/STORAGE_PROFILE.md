# Storage Profile

## Three roots

```yaml
code_repo:
  purpose: source code, docs, tests, contracts, schemas, fixtures

artifact_root:
  purpose: immutable source copies, Markdown, JSON, assets, provenance, review state, approved exports
  selected_by_user: true
  may_be_google_drive_sync_folder: true

local_state_root:
  purpose: SQLite live DB, preview cache, model cache, temporary jobs, job scratch
  per_machine: true
  may_be_google_drive_sync_folder: false
```

## Record retention

Use `docs/architecture/LOG_AND_RECORD_RETENTION_POLICY.md` for the canonical
record-class matrix, Artifact Root directory structure, Local State Root
directory structure, retention rules, and filename conventions.

## Google Drive sync-folder mode

A Google Drive sync folder is treated as a normal filesystem path. This does not authorize Google Drive API usage.
