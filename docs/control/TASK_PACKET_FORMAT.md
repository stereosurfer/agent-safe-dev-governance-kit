# Task Packet Format

Status: canonical owner of task-packet modes and projection semantics.

A task packet is optional. It is never a work router, independent task
identity, issue-completion record, PR authority, or merge authority. When
GitHub is available, the live GitHub issue or PR owns executable
authorization. The only outage exception is the bounded local-work fallback
defined below.

No field may say `see chat`.

## Visible and unambiguous task fields

A work unit or source issue may expose its 13 canonical fields and two
execution gates in exactly one form:

1. unique visible recognized task-field headings, using an ATX level such as
   the H3 headings emitted by GitHub issue forms or visible Setext syntax; or
2. one exact visible ATX H2 `## Required Task Fields` section containing the
   dependency-free YAML subset. Exact means the displayed label has that
   spelling, spacing, punctuation, and case.

The canonical section may contain raw YAML, or one sole fenced record. A fence
must be unlabeled, `yaml`, or `yml`; a second fence makes the section
ambiguous. Duplicate individual headings, multiple canonical sections, mixed
heading/YAML representations, and duplicate top-level YAML keys all fail
closed. A differently leveled or Setext `Required Task Fields` heading is
ambiguous rather than canonical. Within an individual field, a lower-level
heading remains part of that field until the next heading at the same or a
higher level. A Setext underline is syntax and never becomes field data. No
first or last occurrence wins.

Headings and YAML shown in fenced examples outside the canonical section are
non-authoritative and are ignored. A raw YAML task packet likewise rejects
duplicate top-level keys and quoted top-level keys. YAML quoted scalars remain
strings, while unquoted null, boolean, and numeric tokens retain their
corresponding types so runtime checks match the schema. JSON decoding is a
separate input path; duplicate-key detection is not claimed for JSON.

A file-backed YAML packet is either the raw packet or one top-level
`bad_input` or `task_packet` fixture wrapper. Raw packet fields plus a wrapper,
nested wrappers, competing wrappers, or a wrapper accompanied by unrelated
top-level fields are ambiguous. The JSON loader likewise rejects both wrapper
keys or a wrapper accompanied by unrelated top-level fields.

The `--json-file` fixture-bundle interface may carry its named fixture
metadata, but `task_packet` cannot coexist with `bad_input` or any top-level
raw task-packet field. Such a second candidate is
`TP_TASK_FIELD_AMBIGUOUS`; no packet projection or temporary authority is
emitted.

Stable ambiguity findings are:

- `WU_TASK_FIELD_AMBIGUOUS` for work-unit authority;
- `TP_ISSUE_TASK_FIELD_AMBIGUOUS` for a source issue used by
  `issue_refinement`;
- `TP_TASK_FIELD_AMBIGUOUS` for a raw YAML task packet.

When source issue fields are ambiguous, task-packet scope, read-set, and
validation non-expansion comparisons are not performed.

A source issue containing the legacy `intelligence_level_reason` field fails
with `TP_ISSUE_REASON_ALIAS_FORBIDDEN`, even when canonical `reason` is also
present. Comparisons that depend on a valid source issue are not performed.

## Mode 1: issue_refinement

Use this mode only to narrow one live GitHub issue:

```yaml
mode: issue_refinement
durable_source_of_truth: "GitHub issue #123"
allowed_paths:
  - "one/exact/path/already/authorized/by/the/issue"
context_read_set:
  - "AGENTS.md"
  - "current GitHub issue"
project_specific_validation:
  - "one exact check already required by issue #123"
```

The three list fields must stay within the issue:

- `allowed_paths` uses path containment;
- `context_read_set` uses case-sensitive exact-item comparison;
- `project_specific_validation` uses case-sensitive exact-item comparison.

All list items are non-empty strings. Paths must be repository-relative, may
not contain `.` or `..` segments, and must resolve inside the repository root.
Context items may also be durable issue/PR/URL references, but whole-repo
requests, prose instructions, nonexistent paths, directories, and globs are not
bounded read items. Issue/PR/URL references must occupy the whole item; an
issue or URL prefix cannot hide an appended broad-read instruction. Because the
validator does not implement general glob-set algebra, a packet glob is within
issue scope only when the normalized glob text exactly equals an issue glob.

The packet may equal or narrow the issue values. It must never add a path,
read-set item, validation item, non-goal exception, completion claim, or
permission that the issue does not contain. Semantic equivalence is not
mechanically proven.

Run the canonical comparison:

```bash
python3 scripts/asgk.py task-packet-check \
  --issue <number> \
  --file <task-packet> \
  --json
```

`compact-task-packet-check` is a compatibility command that invokes the same
loader, evaluator, finding codes, and proof boundary. It is not a second
comparison oracle.

## Mode 2: github_unavailable_fallback

Use this mode only while GitHub is actually unavailable:

```yaml
mode: github_unavailable_fallback
github_issue_status: pending_unavailable
lane: validation_tooling
intelligence_level: frontier
reason: "Why this intelligence level and task scope are sufficient."
durable_source_of_truth: "This repository task packet pending GitHub recovery."
objective: "One concrete result."
plan:
  - "Step 1"
checklist:
  - "[ ] Check item"
acceptance_sheet:
  - "[ ] Acceptance condition"
allowed_paths:
  - "one/exact/path"
context_read_set:
  - "AGENTS.md"
  - "this task packet"
project_specific_validation:
  - "one concrete project check"
expected_output: "Observable output."
non_goals:
  - "Do not expand scope."
stop_conditions:
  - "GitHub authority remains unavailable before PR creation."
rollback_expectations: "Revert only this task's bounded changes."
```

The fallback carries the complete 13 canonical fields from `AGENTS.md` plus the
two execution gates. `reason` is the only formal name. The status must be the
exact token `pending_unavailable`.

The validator cannot prove that GitHub was unavailable. An agent must retry
issue creation and transfer the full scope to a GitHub issue before creating a
PR or requesting merge. A fallback packet cannot authorize either action.

While GitHub unavailability is independently known, the complete fallback is
temporary authority only for local work inside its recorded allowed paths,
read set, validation, non-goals, and stop conditions. It grants no external
action, protected-path exception, human approval, or low-risk status. If
availability is unknown, or any recorded boundary is insufficient, stop.

The machine-readable local-authority state is therefore conditional on both
verified GitHub unavailability and a separate determination that no escalation
trigger applies. Structural validation alone never activates that state.

`task-packet-check` fails a fallback when its `allowed_paths` overlap a
mechanically recognizable escalation boundary such as agent instructions,
`.github/**`, control documents, schemas, or contracts. This is only a
fail-closed subset of the escalation policy. Dependencies, credentials,
external services, private material, policy meaning, and other non-path
triggers still require human judgment.

## Forbidden legacy shape

The v2 contract rejects these v1 packet fields because they duplicate authority
or create misleading routing/context concepts:

```text
task_id
intelligence_level_reason
product_context
current_repository_context
files_to_inspect_first
expected_changes
constraints
validation_commands
work_unit_kind
```

Versioned v1 tags and Git history preserve the old format when historical
recovery is required.

## Mechanical proof boundary

Exit `0` from `task-packet-check` proves only:

- the supplied packet has one supported shape;
- the checked YAML or source-issue task fields have one visible,
  unambiguous representation;
- legacy fields, unsafe paths, schema/runtime type drift, and overbroad or
  invalid, nonexistent, or outside-root context references were not accepted;
- for `issue_refinement`, the supplied packet does not mechanically expand the
  supplied issue's paths or exact read/validation items.

It does not prove implementation correctness, semantic equivalence, GitHub
availability, every escalation trigger, project-validation sufficiency, PR
readiness, human approval, merge authority, or issue completion.
