# Cache And State Policy

Runtime cache and live state must not leak into the code repo or Artifact Root.

Use `docs/architecture/LOG_AND_RECORD_RETENTION_POLICY.md` for the canonical
Local State Root directory structure and naming conventions for live DBs,
preview caches, model caches, temporary jobs, scratch files, and session state.

## Local-only state

```yaml
local_only:
  - sqlite_live_db
  - preview_render_cache
  - model_cache
  - temporary_jobs
  - browser_session_state
```

## Artifact Root allowed state

Artifact Root may contain durable reviewed outputs, provenance packages, export manifests, and review state that is intended to be portable.

## Forbidden

```yaml
forbidden:
  - SQLite live DB in Artifact Root
  - model cache in Artifact Root
  - preview render cache in Artifact Root
  - runtime scratch in repo
```
