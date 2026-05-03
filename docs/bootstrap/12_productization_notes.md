# 12 Productization Notes

Status: reference-only productization framing.

Boundary:

- Use this file for stable product-positioning notes and v1.x/v2.0 scope framing.
- Do not use it as a release diary, roadmap queue, or status log.
- Productization decisions and release-preparation history belong in GitHub issues, PRs, comments, merge commits, or a dedicated release-preparation document.

This kit is easier to productize as:

```text
repo template -> validation CLI -> runtime-specific profiles -> managed service
```

Avoid presenting it as a generic architect agent, agent team, CEO/CTO/Engineer role bundle, multi-agent runtime, or task chat UI. More accurate positioning:

```text
Agent-safe development governance scaffold
AI development governance layer for GitHub workflows
Contract-first AI coding workflow
```

## Product boundary

The sellable unit is not the model and not the runtime. The durable asset is the control layer: task packets, gates, schemas, validators, merge policy, and handoff discipline.

ASGK v1.x should stay runtime-agnostic and operate through a generic repo-agent profile. A human, Codex, ChatGPT Web, OpenGoat, Claude Code, Cursor, or another runtime may perform the work, but repo changes still pass through the same ASGK governance layer.

Runtime-specific governance profiles are planned for v2.0. They should be based on vendor documentation and observed behavior, and they should optimize execution surfaces without replacing the generic v1.x governance core.

## Positioning statement

```text
Agent runtimes will commoditize. Repo governance is the durable layer.
```

Traditional Chinese:

```text
Agent 執行層會快速商品化；真正長期有價值的是 repo 治理層。
```

## v1.x scope

```yaml
v1_x:
  profile: generic_repo_agent
  owns:
    - task packet schema
    - issue and PR templates
    - validation scripts
    - context budget policy
    - negative test suite
    - merge decision record
    - handoff discipline
  does_not_own:
    - agent runtime implementation
    - multi-agent chat UI
    - runtime-specific optimization profiles
```

## v2.0 planned scope

```yaml
v2_0:
  planned:
    - profiles/codex-app/
    - profiles/chatgpt-web-github-connector/
    - profiles/opengoat/
    - profiles/claude-code/
    - profiles/cursor/
  rule:
    - profiles are optimization adapters
    - profiles must not bypass ASGK core governance
    - profiles require vendor docs and observed tests
```
