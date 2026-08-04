# Low-Risk Autonomous Merge Policy

Agents may perform low-risk merge flow only when all explicit gates pass.

## Necessary operations allowed

When required for the active work unit:

- `git fetch`, branch creation, fast-forward sync;
- staging intended files;
- committing and pushing;
- opening/updating a PR;
- editing PR body;
- posting issue/PR comments;
- checking PR status;
- rerunning checks when supported and no scope changes occur;
- closing a completed issue only when current `main` or merged PR clearly satisfies it.

## Prohibited without human approval

- `git reset --hard`;
- force push;
- deleting branches;
- reverting user work;
- broad issue/label churn unrelated to the active work unit;
- closing milestone controller issues;
- source fetching, live web search, model/API calls, raw retention, publication, cloud, MCP write capability, or externalized responsibility changes.

## Low-risk merge gates

All must pass:

1. PR belongs to current authorized work unit.
2. PR is open, non-draft, mergeable, and current with base.
3. Required GitHub checks pass.
4. Required local checks pass, or PR is docs-only and CI proves repo gate is green.
5. No unresolved P1/P2 review comments, requested changes, merge conflicts, or human hold.
6. Scope is low-risk: docs-only, governance-only, test-only, issue/status hygiene, or narrow deterministic change with tests.
7. PR does not enable restricted capabilities.
8. Runtime artifact hygiene is clean.
9. PR includes scope-boundary disclosures and Merge Decision Record.
10. Handoff/state update is included when state changes.

## Program-Scoped Reversible Merge Path

An OWNER-approved program may authorize autonomous merge of a repo-local source
work unit that is already named and bounded, including an explicitly authorized
protected governance path. This is not a general low-risk classification and is
not human approval of the current head.

All low-risk merge gates above still apply, plus:

1. `docs/control/HUMAN_GATED_OPERATIONS.md` defines the canonical program
   execution boundary.
2. The program issue contains durable OWNER execution authorization.
3. A durable OWNER-approved scope source predates the child issue and names the
   exact work-unit path/action set.
4. The current child issue explicitly invokes that authorization, is equal to
   or narrower than the scope source, and names exact allowed paths.
5. The PR records a complete `program_execution_authorization` block bound to
   the current head and diff.
6. The change touches tracked source only, has no external side effect beyond
   routine issue/PR metadata, and is recoverable completely by ordinary Git
   revert.
7. Independent current-head evidence confirms semantic scope match, reviewer
   separation, and that no Human-Gated Operations item applies.
8. Required current-head checks, CI, and strict `check-pr` pass before merge.

Close-out remains mandatory after merge.

Scope drift, an unlisted path, uncertain rollback, a missing independent review,
or any human-gated operation makes this path ineligible. Program authorization
must not be rewritten as current-head OWNER review. `doctor`, PR-body
validation, CI, and `check-pr` do not infer that the path applies.

The program grant may remain valid across commits. The scope/no-gate reviews,
CI, and `check-pr` must be refreshed for every current head.

A PR that changes this program path, Human-Gated Operations, merge authority,
or enforcement/non-inference semantics—including by creating, removing,
loosening, tightening, or reclassifying them—cannot use the path it changes.
Evaluate it under the stricter baseline or proposed policy and require
current-head human approval.

After merge, update the linked issue/handoff and stop.
