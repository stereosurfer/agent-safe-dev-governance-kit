# AGENTS.md — Agent Operating Guide

This repository uses GitHub issues, pull requests, repository files, and handoff documents as the durable source of truth for agent tasks.

Agents must not depend on prior chat history. A new session must be able to continue from the repository state, the current GitHub issue or PR, and the compact handoff surface.

## Product boundary

ASGK uses a generic repo-agent governance core.

Runtime-specific adapters, runtime-specific profiles, custom-agent tuning,
subagent orchestration, goal workflows, vendor-specific instructions, and
platform-specific optimizations are not part of the default operating profile.
Superseded roadmap material gives them no current product authority. Any such
specialized work requires explicit durable scope and must not bypass the generic
repository governance flow.

## Default startup set

Read only the smallest sufficient startup set unless the current issue, PR, handoff packet, validation failure, or `docs/DOCUMENT_MAP.md` points to more context:

1. `AGENTS.md`
2. `README.md`
3. `docs/handoff/CURRENT_STATUS.md`
4. Current GitHub issue or PR

Do not read all bootstrap, control, architecture, schema, contract, example, profile, or adapter files by default.

Use `docs/DOCUMENT_MAP.md` when a work unit needs context expansion, canonical-owner lookup, or document-role clarification.

## Source of truth rule

Task objectives, plans, checklists, acceptance sheets, allowed paths, expected outputs, and merge decisions must live in a GitHub issue, PR, or repository document.

```text
The phrase "see chat" is not acceptable for task scope, acceptance, handoff, or merge authority.
```

## Issue-first rule

When GitHub is available, every executable implementation, validation, UI/test,
runtime, storage-boundary, or handoff-changing work unit must start from a
GitHub issue or an already-open pull request before file edits.

A task packet is optional and has only two modes:

- `issue_refinement` may narrow one live issue's allowed paths, context read
  set, and project-specific validation. It cannot route work, add authority, or
  replace the issue.
- `github_unavailable_fallback` may temporarily record the complete task while
  GitHub is verifiably unavailable. During that outage it is bounded authority
  only for local work inside its recorded scope and only when no escalation
  trigger applies; it never authorizes a PR, merge, publication, or other
  external action. It must record
  `github_issue_status: pending_unavailable`, and the agent must create the
  GitHub issue before PR creation or merge.

A repository document may remain the durable source for explicitly docs-only
planning/control work. An `issue_refinement` packet does not turn that document
into executable authority; the outage fallback above is the sole temporary
local-work exception.

## Chat Output Hygiene

Routine governance mechanics must be silent in chat.

Only blockers, material decisions, validation failures, human gates, scope
conflicts, and final results should be user-visible.

Full evidence, command logs, validation details, changed-file lists, and merge
rationale belong in PR bodies, issue comments, CI logs, or handoff artifacts.

Do not narrate routine steps such as creating branches, checking files, running
ordinary validators, counting tool calls, or restating why repo-native
governance exists unless that information changes the user's next decision.

## Generic Operating Profile

Use this generic profile by default for all repository work.

1. Read the default startup set.
2. Identify one current work unit.
3. Confirm durable source of truth.
4. Confirm allowed paths.
5. Confirm the canonical task fields, bounded `context_read_set`,
   `project_specific_validation`, expected output, non-goals, and stop
   conditions. When available, run:

   ```bash
   python3 scripts/asgk.py work-unit-check --issue <number> --authority-only --json
   ```

6. Create or use a task branch.
7. Modify only files allowed by the current issue or PR; an
   `issue_refinement` packet may narrow those paths but must not expand or
   replace them. During the verified-outage exception, modify only the complete
   fallback's allowed paths and stop before any PR, merge, or external action.
8. Run the required validation.
9. Before opening or updating a pull request body, write the body to a file and
   run local PR body governance preflight:

   ```bash
   python3 scripts/pr_governance_preflight.py check --body-file <body-file>
   ```

   Use the same wrapper for PR body create/edit when possible. Do not submit
   inline PR bodies or bypass local PR body preflight.
10. Open or update a pull request.
11. Wait for CI when CI applies.
12. Update the Merge Decision Record before merge eligibility.
13. Merge only when the issue, policy, validation, CI, and merge boundary permit it.
14. Comment on and close the issue after merge when closeout is authorized.

## Generic Purity Rule

The Generic Operating Profile contains only repository-wide safety workflow.

Do not add runtime-specific, platform-specific, vendor-specific, domain-specific, subagent-specific, goal-workflow-specific, or optimization-specific behavior to the generic profile.

Specialized material may exist only as an explicitly scoped non-default
reference or policy. It must not be read by default and must not change the
generic governance flow.

## Escalation triggers

Escalate before writing, before PR closeout, or before merge if a work unit touches or requires:

- `AGENTS.md`, `CLAUDE.md`, or other agent/tool instruction files;
- `.github/**`;
- `.codex/**`;
- `.claude/**`;
- `docs/control/**`;
- `schemas/**` or `contracts/**`;
- dependency files or new dependencies;
- credentials, secrets, MCP, external services, cloud egress, or API/model call lanes;
- merge policy, permissions, storage roots, runtime artifact boundaries, or protected paths;
- destructive operations;
- private source documents;
- unclear or missing allowed paths;
- multiple unrelated work areas;
- unresolved conflict between docs, issue, PR, and code;
- insufficient context.

Escalation means:

1. Require explicit GitHub issue or PR authorization.
2. Record the trigger in the PR.
3. Do not auto-merge.
4. Run stricter validation when available.
5. Stop if authorization is missing or the boundary is unclear.

## Stop conditions

Stop and report instead of continuing when escalation authorization is missing, allowed paths are missing or unclear, protected paths are required, validation cannot be run, required context is unavailable, or instructions conflict on scope, source of truth, permissions, runtime artifacts, human gates, or merge behavior.

## Conflict rule

If instructions conflict on scope, permissions, source of truth, validation, protected paths, runtime artifacts, human gates, or merge behavior, stop and report the conflict.

Do not silently reconcile conflicts between chat instructions, tool settings, issue scope, PR text, `AGENTS.md`, `docs/DOCUMENT_MAP.md`, control documents, scripts, or CI results.

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
- one smoke-test or validation instruction.

Do not start another issue after completing a PR unless a durable GitHub issue/comment explicitly instructs it.

## Required task fields

The selected durable work-unit authority must have:

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

`reason` is the only formal field name. Do not substitute
`intelligence_level_reason`.

The 13 fields and the execution gates must use exactly one visible,
unambiguous representation: individual recognized Markdown task-field
headings, including the ATX heading levels emitted by GitHub issue forms and
visible Setext headings, or one exact ATX H2 `## Required Task Fields` section
with that exact spelling and case containing the supported YAML subset. A
Setext underline is heading syntax, never field data. A lower-level heading
inside an individual field remains part of that field until the next heading
at the same or a higher level. Do not mix the two forms, repeat a task-field
heading, repeat a top-level YAML key, or place multiple fenced records in the
canonical section. Fenced examples outside that section are not authority.

## Required execution gates

The selected durable authority for executable work must additionally have:

- `context_read_set`: the smallest exact paths and durable pseudo-references
  required for the work;
- `project_specific_validation`: the concrete project checks required in
  addition to ASGK governance checks, or `not_applicable` with a material
  reason.

These two gates constrain execution. They are not additional task-identity
fields and do not create another source of authority.

Normally the linked open issue carries the complete 13 fields and two gates for
both implementation and later PR follow-up. An open PR qualifies as the selected
authority only when its body itself visibly carries the complete set. Ordinary
PR bodies do not need to duplicate a valid linked issue.

## Low-risk merge boundary

Low-risk autonomous merge is allowed only when `docs/control/LOW_RISK_AUTONOMOUS_MERGE_POLICY.md` and `docs/bootstrap/11_auto_merge_policy.md` both pass. High-risk operations remain human-gated under `docs/control/HUMAN_GATED_OPERATIONS.md`.

Escalated work is not auto-merge eligible unless a canonical policy and the current GitHub issue explicitly allow it.

## Required checks

For governance/scaffold changes:

```bash
python3 scripts/asgk.py doctor
```

For PR body create/edit preflight:

```bash
python3 scripts/pr_governance_preflight.py check --body-file <body-file>
```

For code changes, run the project-specific tests named in the issue or acceptance criteria.

## Runtime artifact rule

Do not commit real runtime outputs, private files, raw captures, raw source dumps, model cache files, SQLite live DBs, preview render caches, or external material-preparation outputs.
