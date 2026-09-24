# Log And Record Retention Policy

Status: active ASGK source-repository record policy.

This document owns the placement of ASGK governance records. It does not
prescribe a target application's storage layout. A target may have no artifact
root, local-state root, database, cache, or workspace lock; those choices need
target-owned authority and validation when relevant.

## One primary home per record class

| Record class | Primary home | Source-repo treatment |
|---|---|---|
| Task scope, acceptance, allowed paths, and decisions | Current GitHub issue or qualifying PR | Link, do not duplicate full bodies in a ledger. |
| PR evidence, review, Merge Decision Record, and CI | GitHub PR, review threads, Actions, and Git history | Keep bounded references and commit SHA. |
| Issue close-out and accepted/rejected decision branches | GitHub issue comments | Keep a short pointer in current status only if needed for recovery. |
| Current repo recovery snapshot | `docs/handoff/CURRENT_STATUS.md` | Compact, replaceable snapshot; not a decision-history copy. |
| ASGK source, policies, Skills, contracts, schemas, tests, and sanitized fixtures | Version-controlled source repo | Review through an issue/PR and retain in Git history. |
| Task-owned delivery package, Lesson, benchmark, or other durable work output | Location explicitly selected by the task/target delivery contract | May enter source control only when intentionally reviewed as versioned source; never becomes merge authority by location alone. |
| Raw capture, private source, generated runtime output, live database, cache, or scratch | Authorized location appropriate to the task and data class | Do not commit to the ASGK source repo. A task-specific policy governs retention and cleanup. |

GitHub is the governance ledger, not a place to paste raw private sources or
unbounded runtime output. Bot memory and Kanban cards may point to durable
records, but neither replaces GitHub issue/PR authority or a task-owned
delivery contract. A task package's question/evidence graph is its delivery
state, not a second ASGK approval record.

## Placement and retention decisions

Before a task writes outside the source repo, its live issue must authorize the
action and exact destination. A target-owned delivery contract may refine the
data class, owner, intended retention, cleanup/rollback, and whether private
material or external sync is involved; it cannot independently grant write or
human-gate authority. Do not infer permission from a folder name or a prior
project's layout. Cloud/API/MCP access, external-system writes, raw-source
retention, publication, and private material remain subject to
`docs/control/HUMAN_GATED_OPERATIONS.md`.

For field tests, state which evidence remains in GitHub, which deliverables are
task-owned, what transient state may be discarded, and who controls any
private input. `none` is a valid answer for a storage class that the task does
not need. Do not create directories or copy material merely to fill a template.

Source-repo fixtures must be small, sanitized, intentional, and reviewable.
Generated examples do not qualify automatically. Keep secrets, user-private
names, raw URLs, and private source content out of filenames and commits.
Use stable issue/PR, commit, and task artifact identifiers where useful; no
universal run-ID or directory tree is imposed.

See `docs/architecture/RUNTIME_ARTIFACT_POLICY.md` for the source commit
boundary and `docs/control/HUMAN_GATED_OPERATIONS.md` for operations requiring
human authorization. Workflow-specific promotion rules apply only when the
task explicitly invokes that workflow; they do not govern every ASGK record.
