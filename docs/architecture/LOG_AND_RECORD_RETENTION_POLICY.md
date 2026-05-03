# Log And Record Retention Policy

Status: active architecture policy.

This policy defines where logs, records, artifacts, caches, and runtime state
belong across GitHub, the code repository, Artifact Root, and Local State Root.
It exists to prevent ad hoc local file sprawl, duplicated GitHub history, and
accidental commits of runtime or private material.

## Core Rule

```text
Every record class has one primary home.
Do not copy records into another root unless this policy explicitly allows it.
```

The repository is not a dumping ground for runtime outputs. Artifact Root is not
a dumping ground for live state. Local State Root is not durable evidence.

## Storage Surfaces

```yaml
storage_surfaces:
  github_durable_history:
    purpose: task authority, PR evidence, review discussion, closeout evidence
    examples:
      - GitHub issue bodies
      - pull request bodies
      - PR comments
      - issue result comments
      - merge commits
    retention: platform_durable

  code_repo:
    purpose: source code, governance docs, tests, contracts, schemas, fixtures
    examples:
      - docs/
      - scripts/
      - examples/
      - tests/fixtures/
    retention: version_controlled

  artifact_root:
    purpose: portable reviewed outputs, provenance packages, manifests, approved exports
    selected_by_user: true
    may_be_google_drive_sync_folder: true
    retention: durable_user_selected

  local_state_root:
    purpose: live state, cache, temporary jobs, scratch files
    per_machine: true
    may_be_google_drive_sync_folder: false
    retention: ephemeral_or_machine_local
```

## Record Retention Matrix

| Record class | Primary home | Retention | Repo copy | Artifact Root copy | Local State copy | Naming / structure |
|---|---|---|---|---|---|---|
| Issue body | GitHub issue | durable | forbidden except template examples | no | no | GitHub issue number owns identity |
| PR body and MDR | GitHub PR | durable | forbidden except template examples | no | no | GitHub PR number owns identity |
| PR review comments | GitHub PR comments | durable | forbidden | no | no | GitHub PR thread owns identity |
| Issue closeout comment | GitHub issue comment | durable | forbidden | no | no | GitHub issue comment owns identity |
| Merge commit | Git commit history | durable | native git history | no | no | commit SHA owns identity |
| Raw CI logs | GitHub Actions | platform-managed | forbidden | only if explicitly exported for audit | no | use workflow/run ID if exported |
| Agent report | GitHub comment preferred; compact repo log optional | durable or compact append | compact link only in `AGENT_LOG.md` | no | no | issue/PR number plus UTC timestamp |
| Decision entry | `docs/handoff/DECISIONS.md` | compact append | allowed, compact only | no | no | date + decision id or issue/PR reference |
| Current repo status | `docs/handoff/CURRENT_STATUS.md` | overwritten | allowed, compact only | no | no | single current status file |
| Lane status | `docs/control/LANE_STATUS.md` | overwritten | allowed, compact only | no | no | single lane status table |
| Small fixture | `examples/` or `tests/fixtures/` | version-controlled | allowed if sanitized and intentional | no | no | descriptive name, no private data |
| Raw source capture | Artifact Root | durable if authorized | forbidden | allowed if source/input class permits | temporary copy only | `sources/<source_class>/<artifact_id>/` |
| Prepared markdown / JSON | Artifact Root | durable if reviewed | forbidden unless fixture | allowed | temporary copy only | `prepared/<artifact_id>/` |
| Candidate artifact | Artifact Root | review pending | forbidden | allowed | temporary working copy allowed | `artifacts/candidate/<artifact_id>/` |
| Validated artifact | Artifact Root | durable | forbidden unless small fixture | allowed | temporary working copy discouraged | `artifacts/validated/<artifact_id>/` |
| Promoted/exportable artifact | Artifact Root | durable/exportable | forbidden unless release fixture | allowed | no | `exports/<export_id>/` |
| Export manifest | Artifact Root | durable | forbidden unless example | allowed | no | `exports/<export_id>/manifest.yaml` |
| Provenance package | Artifact Root | durable | forbidden unless example | allowed | no | `provenance/<artifact_id>/` |
| Review state intended to be portable | Artifact Root | durable | forbidden unless example | allowed | no | `reviews/<artifact_id>/` |
| SQLite live DB | Local State Root | local live state | forbidden | forbidden | required local-only | `db/<project_or_run>.sqlite` |
| Preview render cache | Local State Root | ephemeral | forbidden | forbidden | required local-only | `cache/preview/<run_id>/` |
| Model cache | Local State Root | ephemeral/local | forbidden | forbidden | required local-only | `cache/model/<provider_or_model>/` |
| Temporary jobs | Local State Root | ephemeral | forbidden | forbidden | required local-only | `jobs/<run_id>/` |
| Job scratch | Local State Root | ephemeral | forbidden | forbidden | required local-only | `scratch/<run_id>/` |
| Browser/session state | Local State Root | ephemeral/local | forbidden | forbidden | required local-only | `session/<tool_or_browser>/` |
| Private source document | User-selected secure location or authorized Artifact Root | user-controlled | forbidden | only if explicitly authorized | temporary copy only if needed | keep original filename plus source id when captured |

## Artifact Root Structure

Artifact Root is user-selected and portable. It may be inside a sync folder only
when the user knowingly selected that path. Agents must not create public cloud
sharing links by default.

Recommended structure:

```text
<artifact-root>/
  .workspace.lock
  sources/
    <source_class>/
      <artifact_id>/
        original/
        normalized/
        source_manifest.yaml
  prepared/
    <artifact_id>/
      markdown/
      json/
      assets/
      preparation_manifest.yaml
  artifacts/
    candidate/
      <artifact_id>/
    validated/
      <artifact_id>/
  reviews/
    <artifact_id>/
      review_state.yaml
      findings.md
  provenance/
    <artifact_id>/
      provenance.yaml
      checksums.txt
  exports/
    <export_id>/
      manifest.yaml
      payload/
```

Rules:

```yaml
artifact_root_rules:
  require_workspace_lock_for_writes: true
  allowed_to_sync: user_selected_only
  forbidden:
    - SQLite live DB
    - model cache
    - preview render cache
    - temporary job scratch
    - unreviewed runtime dump folders
  must_include_manifest_when:
    - source capture is durable
    - artifact is promoted
    - export is produced
```

## Local State Root Structure

Local State Root is per-machine and must not be a Google Drive sync folder. It is
for live state, cache, scratch, and temporary execution material only.

Recommended structure:

```text
<local-state-root>/
  db/
    <project_or_run>.sqlite
  cache/
    preview/
      <run_id>/
    model/
      <provider_or_model>/
    http/
      <run_id>/
  jobs/
    <run_id>/
      job.yaml
      stdout.log
      stderr.log
      work/
  scratch/
    <run_id>/
  session/
    <tool_or_browser>/
```

Rules:

```yaml
local_state_root_rules:
  sync_folder_allowed: false
  commit_allowed: false
  durable_evidence_allowed: false
  may_be_deleted_after_review: true
  may_contain_private_or_transient_state: true
  must_not_be_used_for:
    - canonical policy
    - durable closeout evidence
    - promoted artifacts
```

## Naming Conventions

Use filename-safe UTC timestamps when a run or record needs time identity:

```text
YYYYMMDDTHHMMSSZ
```

Recommended identifiers:

```yaml
identifiers:
  run_id: "run-YYYYMMDDTHHMMSSZ-<short-slug>"
  artifact_id: "art-YYYYMMDDTHHMMSSZ-<short-slug>"
  export_id: "export-YYYYMMDDTHHMMSSZ-<short-slug>"
  source_id: "src-YYYYMMDDTHHMMSSZ-<short-slug>"
```

Rules:

```yaml
naming_rules:
  - use lowercase slugs where practical
  - avoid spaces in generated directory names
  - preserve original source filenames inside `original/` when needed
  - never encode secrets, API keys, user private names, or raw URLs into filenames
  - use manifests for metadata instead of overloaded filenames
```

## Promotion And Retention

Traceability alone is not enough. Durable artifacts must still pass the relevant
promotion policy before downstream use.

```yaml
retention_by_promotion_status:
  raw_or_prepared_input:
    home: artifact_root_when_authorized
    downstream_use: blocked_until_validated
  candidate_artifact:
    home: artifact_root
    downstream_use: review_only
  validated_artifact:
    home: artifact_root
    downstream_use: allowed_by_manifest
  promoted_artifact:
    home: artifact_root
    downstream_use: allowed_by_promotion_record
  local_scratch:
    home: local_state_root
    downstream_use: forbidden
```

## GitHub Versus Local Records

GitHub is the durable governance ledger. Local files are not a replacement for
issue and PR evidence.

```yaml
do_not_duplicate_github_history_into_local_files:
  - full issue bodies
  - full PR bodies
  - full review threads
  - raw CI logs
  - full chat transcripts

allowed_local_references:
  - issue number
  - PR number
  - commit SHA
  - artifact id
  - short manifest references
```

## Before Field Tests

Before running a real-world field test, the task issue should explicitly state:

```yaml
field_test_storage_plan:
  artifact_root: "<user-selected path or none>"
  local_state_root: "<machine-local path or none>"
  expected_artifacts:
    - "<artifact class>"
  expected_local_state:
    - "<state/cache/scratch class>"
  cleanup_expectation:
    - "what can be deleted"
    - "what must be retained"
```

If the field test does not need Artifact Root or Local State Root writes, say so
explicitly in the issue and PR.

## Non-goals

This policy does not authorize:

```yaml
non_goals:
  - creating Artifact Root directories from repo tasks
  - creating Local State Root directories from repo tasks
  - migrating existing user files
  - enabling cloud/API/storage integration
  - committing generated runtime outputs
  - retaining private source material in the code repo
```

## Relationship To Other Policies

```yaml
related_policies:
  storage_profile: docs/architecture/STORAGE_PROFILE.md
  runtime_artifacts: docs/architecture/RUNTIME_ARTIFACT_POLICY.md
  cache_and_state: docs/architecture/CACHE_AND_STATE_POLICY.md
  workspace_lock: docs/architecture/WORKSPACE_LOCK_POLICY.md
  naming_versioning: docs/bootstrap/06_naming_versioning.md
  artifact_promotion: docs/bootstrap/13_artifact_promotion_policy.md
```
