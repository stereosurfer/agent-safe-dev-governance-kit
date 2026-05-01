# Workspace Lock Policy

## Purpose

Prevent two agents or app instances from mutating the same Artifact Root at the same time.

## Required behavior

```yaml
workspace_lock:
  required_for_artifact_root_writes: true
  lock_file: ".workspace.lock"
  stale_lock_policy: manual_review
  google_drive_sync_warning: true
```

## Agent boundary

Repo tasks must not create or override workspace locks unless explicitly authorized as a runtime validation task.
