# AGENTS.md — Agent Operating Guide

This repository uses GitHub issues, pull request comments, repository files, and handoff documents as the source of truth for agent tasks.

Agents must not depend on prior chat history. A new session must be able to continue by reading this file, `README.md`, `docs/handoff/CURRENT_STATUS.md`, open pull requests, and open issues.

## Startup read order

1. `AGENTS.md`
2. `README.md`
3. `docs/bootstrap/00_project_brief.md`
4. `docs/bootstrap/01_physical_boundaries.md`
5. `docs/bootstrap/02_storage_roots.md`
6. `agent/agent_rules.yaml`
7. `docs/control/CONTROL_LAYER_V0.md`
8. `docs/handoff/CURRENT_STATUS.md`
9. Open PRs first; then open issues.

## Source of truth rule

Task objectives, plans, checklists, acceptance sheets, allowed paths, expected outputs, and merge decisions must live in a GitHub issue, PR, or repository document.

```text
The phrase "see chat" is not acceptable for task scope, acceptance, handoff, or merge authority.
```

## Issue Hygiene Gate

Before starting a ready issue:

1. Check whether the issue is already satisfied by current `main` or a merged PR.
2. If completed, do not reimplement it.
3. Comment with evidence and recommended closure or relabeling.
4. Stop unless a human explicitly instructs further work.
5. Prefer a new issue for follow-up work instead of expanding an old issue.

## Work unit rule

Do one work unit at a time.

A work unit is one of:

- one existing PR that needs review-comment fixes;
- one approved issue;
- one smoke-test or validation instruction;
- one controller/lane assignment packet.

Do not start another issue after completing a PR unless a durable GitHub issue/comment explicitly instructs it.

## Architect routing rule

Before implementation, PR hardening, smoke-test execution, or capability planning, produce or preserve an Architect Routing Decision:

```yaml
architect_routing_decision:
  work_unit:
  task_type:
  selected_mode: solo | builder_plus_reviewer | full_cell
  selected_roles:
  intelligence_level: fast_basic | standard | advanced | frontier
  reason:
  durable_source_of_truth:
  allowed_paths:
  expected_output:
  stop_condition:
```

Use the smallest capable agent mode and intelligence level. Do not use routing as a reason to expand scope.

## Required task fields

Every agent task must have:

- lane
- intelligence_level
- reason
- durable_source_of_truth
- objective
- plan
- checklist
- acceptance_sheet
- allowed_paths
- expected_output
- non_goals
- stop_conditions
- rollback_expectations

## Stop conditions

Stop and report when work requires:

- protected path changes;
- Artifact Root writes from repo tasks;
- Local State Root writes from repo tasks;
- new dependency;
- schema breaking change;
- database migration;
- new cloud egress;
- new API/model call lane;
- new MCP tool or MCP write capability;
- broader filesystem permission;
- destructive operation;
- private source documents;
- unresolved conflict between docs, issue, PR, and code;
- insufficient context.

## Low-risk merge boundary

Low-risk autonomous merge is allowed only when `docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md` and `docs/bootstrap/11_auto_merge_policy.md` both pass. High-risk operations remain human-gated under `docs/control/HUMAN_GATED_OPERATIONS.md`.

## Required checks

For governance/scaffold changes:

```bash
python3 scripts/check_project.py
python3 scripts/validate_bootstrap.py
git diff --check
```

For code changes, run the project-specific tests named in the issue or acceptance criteria.

## Runtime artifact rule

Do not commit real runtime outputs, private files, raw captures, raw source dumps, model cache files, SQLite live DBs, preview render caches, or external material-preparation outputs.
