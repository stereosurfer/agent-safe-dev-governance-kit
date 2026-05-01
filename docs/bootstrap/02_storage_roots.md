# 02 Storage Roots

## Rule

Code repo, Artifact Root, and Local State Root are separate.

```yaml
code_repo:
  purpose: source code, tests, contracts, schemas, docs, CI, sanitized fixtures
  must_not_contain:
    - runtime outputs
    - private source files
    - live SQLite DB
    - model cache
    - preview cache

artifact_root:
  purpose: immutable source copies, Markdown, JSON, assets, provenance, review state, approved exports
  selected_by_user: true
  allowed_modes:
    - local_workspace
    - google_drive_sync_folder
  app_managed_drive_api: false

local_state_root:
  purpose: SQLite live DB, preview cache, model cache, job scratch, temporary jobs
  per_machine: true
  cloud_sync_allowed: false
```

## Cache policy

```yaml
cache_policy:
  page_renders: local_only
  model_cache: local_only
  sqlite_live_db: local_only
  temporary_jobs: local_only
```

## Sync policy

Google Drive sync-folder mode is filesystem sync only. It is not Google Drive API integration.

## Review state

Reviewed export state may live in Artifact Root only when intentionally portable. Live review queues and local UI state belong in Local State Root.
