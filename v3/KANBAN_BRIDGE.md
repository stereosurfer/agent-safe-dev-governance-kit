# Kanban is the run plane, not a replacement decision ledger

This is a preview.1 mapping for a future adapter, not a live Hermes configuration or
new generic ASGK requirement. A human may choose a Bot, model, provider, reviewer and
Kanban board. ASGK does not route or grade them automatically.

Hermes Kanban already persists cards, comments, handoffs, runs and workspaces. Its
database is authoritative for **that runtime's** card state and lease ownership.
GitHub issue/qualifying PR and versioned repository files remain authoritative for
ASGK work scope, capability changes, merge decisions and closeout. Neither surface
should pretend to be the other: Kanban `done` is not GitHub issue acceptance or PR
merge approval, and a GitHub comment is not proof the worker's Kanban run completed.

## One bounded card

| At card creation | At worker start | At review/finish |
| --- | --- | --- |
| Link the exact live issue/PR, selected scope, explicit completion contract and output destination. Choose preserved worktree or declared artifact retention when needed. | Re-read the card and linked GitHub authority; verify actor/run/head and selected paths. The card can narrow, never expand, the issue. | Worker reports work and limits; existing mechanical checks run; independent semantic review is requested for material capability/policy promotion or other applicable gate. Record actual reviewer identity. |

For coding PR cards, Hermes's PR completion contract is explicit; prose PR URLs do not
set it, and its local-only default must not be misreported as remote acceptance. Its
own exact-head/required-check guard is useful runtime evidence, not ASGK's MDR or
human-gate decision. In the candidate, `capture`, `packet`, `handoff` and `closeout`
remain read-only/draft-producing; no automatic Kanban or GitHub mutation is present.

The first durable link from the card must point to the GitHub work unit. GitHub need
not duplicate every heartbeat or retry. Promote only material results: changed scope,
decision and rejected path, reviewer finding, final evidence/limit, PR link, blocker,
handoff pointer, or closeout. Record the Kanban card/run identifier alongside that
link so a later reader can return to runtime detail if it still exists.

## Review without a permanent police Bot

Routine execution: worker self-check + deterministic validation + bounded evidence.
At a capability-promotion, protected-path or other existing material gate: request
an **independent** reviewer or the required human. A review by the same actor under a
different profile label is not independent. An optional persistent reviewer Bot can
serve multiple cards, but is not a universal policy authority or a mandatory middleman.
Hermes review dispatch can spawn a reviewer automatically, so an operator must verify
the board's actual reviewer assignment and configuration; ASGK never infers that
independence from a `review` column.

If review rejects a change, keep the card, branch, failed PR, comments and evidence.
The worker may iterate inside the same authorization or obtain a new bounded issue for
expanded scope. Do not erase the rejected route from the eventual closeout decision
tree. If the Kanban database disappears, recover the *governed work* from GitHub issue,
PR, commits and closeout; runtime heartbeats that were never promoted may be lost.

## Failure boundaries to test before an adapter

- Card without live issue: cannot authorize repo mutation merely because it is `ready`.
- Issue narrows or closes after card creation: stop and reproject; a cached packet is not
  a lease against new instructions.
- Scratch workspace completes: undeclared files may be deleted by Hermes; persist
  needed artifacts or use a preserved worktree before marking done.
- Card says done while PR is unmerged or closeout absent: report the two states
  separately; never synthesize acceptance.
- Reviewer is actually the author, required check is stale, or policy is unreadable:
  retain blocked/review state and report the exact missing evidence.
- Lesson volume grows: card comments are not the retrieval index; use the reviewed
  capability metadata and load only selected full records (see CAPABILITY_EVOLUTION).

The [Hermes Kanban reference](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban)
and [worker-lane reference](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban-worker-lanes)
describe current platform behavior. Verify the installed version before writing an
adapter; this document does not claim Hermes has been configured or end-to-end tested.
