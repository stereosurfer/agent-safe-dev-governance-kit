# 09 Safety Checks

Status: short summary; `AGENTS.md` and the named canonical policies own the
actual gates. This file does not grant execution or merge authority.

Before a source PR, confirm the current issue's allowed paths, absence of
private/secret/runtime material, relevant project tests, honest evidence and
proof limits, CI, and the Merge Decision Record. Run:

```bash
python3 scripts/asgk.py doctor
python3 scripts/asgk.py negative all
git diff --check
git diff --check origin/main..HEAD
```

For a live external/API/model/cloud/MCP action, target write, raw-source
retention, or publication, the current work unit must explicitly authorize
the action and the applicable `docs/control/HUMAN_GATED_OPERATIONS.md` gate
must be satisfied. A schedule, provider configuration, prior successful run,
Kanban status, local readiness note, or green validator is never permission.
Do not treat a deterministic structural fallback as production or
human-facing quality evidence without the task's specific proof.
