# Bootstrap Kit v2.1

Repo-native AI development governance scaffold for projects that allow humans, AI agents, Codex, sub-agents, or automation to modify a repository.

This version is designed against a specific failure mode: **AI over-simplification**. It does not only state principles. It turns the principles into required fields, stop conditions, promotion gates, validation scripts, examples, and merge records.

## Core principle

```text
Chat is not the control plane.
GitHub issues, pull requests, repository files, and handoff documents are the durable source of truth.
```

## Product boundary

ASGK v1.x is runtime-agnostic. It assumes a **generic repo agent profile**: any human or AI runtime may work on the repository, but every repo change must pass through the same issue, PR, validation, merge-decision, and handoff governance layer.

Runtime-specific profiles for Codex, ChatGPT Web/GitHub connector, OpenGoat, Claude Code, Cursor, or similar tools are planned for **v2.0**. They are optimization adapters, not the v1.x foundation.

```text
Agent runtimes will commoditize. Repo governance is the durable layer.
```

ASGK does not replace agent runtimes. It governs what they are allowed to change, how changes are validated, and when changes may merge.

## What v2.1 adds over v2

- Full Control Layer template with state model, operating loop, anti-drift rules, task/report formats, human gates, and definition of done.
- Low-risk autonomous merge policy separate from human-gated operations.
- Issue Hygiene Gate.
- Agent Report Format and Task Packet Format.
- Failure Thresholds and notification conditions.
- Externalized Responsibility Boundary for upstream/downstream ownership splits.
- Workspace Lock, Cache, State, and Storage Profile rules.
- Source/Input Class Matrix and Downstream Promotion Matrix.
- Readiness Audit Policy for API/model/provider lanes.
- Stronger schemas and examples for task packets, agent assignments, promotion gates, execution lanes, merge decisions, and agent reports.
- Stronger `validate_bootstrap.py` that checks required files, required terms, JSON validity, YAML-like required fields, PR headings, issue template fields, lane packet fields, examples, storage boundaries, and control-doc sections.

## Install

Copy the kit into a repo root. Customize the placeholders in:

```text
docs/bootstrap/00_project_brief.md
docs/bootstrap/01_physical_boundaries.md
docs/bootstrap/02_storage_roots.md
docs/bootstrap/03_tech_stack.md
agent/agent_rules.yaml
docs/handoff/CURRENT_STATUS.md
```

Run:

```bash
python3 scripts/check_project.py
python3 scripts/validate_bootstrap.py
```

## Operating loop

```text
Project Brief
  -> Physical / Storage Boundary
  -> Control Layer
  -> Agent Routing
  -> Work Unit State
  -> Task Packet
  -> Lane Assignment
  -> Implementation
  -> Validation
  -> Promotion Gate
  -> Readiness Audit
  -> Merge Decision Record
  -> Handoff Update
```

## Non-goal

This kit is not project architecture, not an agent runtime, not a multi-agent chat UI, and not a replacement for Codex, OpenGoat, Claude Code, Cursor, or any other execution layer. It is a governance layer. Each project still needs its own domain schemas, tests, product strategy, and data-quality rules.
