---
name: asgk-startup
description: Resume a selected GitHub-governed work unit or receive a bounded handoff; do not load the full kit for each worker.
---

# Startup and receiving work

Use the candidate design in v3/DESIGN.md; repository AGENTS and live issue/PR remain authority.
Do not install this candidate alongside another version of the same Skill.

For the controller, inspect the relevant open PR before its issue, reconcile repo recovery,
and select one authorized work unit. An unrelated open PR is not the assigned task.
Use the existing work-unit authority check when available; unavailable tooling is a
reported limit, not permission to invent a second task identity.

For a receiver, begin with its GitHub issue, packet, referenced context and prior handoff.
Verify current issue/body, PR head, actor/run, allowed paths, non-goals, forbidden actions,
remaining work and next gate. A packet narrows authority, never replaces it. Fresh Bot
memory or a message acknowledgment is not authority or completion. Request bounded
context expansion when evidence is insufficient.

If the receiver only has a controller-supplied snapshot or card draft, label those facts
as a projection, not as a live issue read. Tool discovery, a URL in the card, and a
model-written assertion are not read receipts. When no permitted observable path can
recheck the live issue, leave a partial handoff with unknowns and block before repo
mutation; do not switch to a broader tool merely to evade that boundary.

When a Hermes Kanban card is used, it owns that run's queue/lease state, not the issue's
write authority. Check the card's exact issue link and completion contract; `done` is
not PR merge or issue closeout. If blocked for missing live authority, post the bounded
partial handoff as a card comment before blocking, so the next receiver sees the reason.
See v3/KANBAN_BRIDGE.md only for a Kanban run. For a
capability task, use the relevant domain index to discover a few pointers, then open
only selected full lessons/ledgers; see v3/CAPABILITY_EVOLUTION.md only when needed.

If evidence changed, return the durable MDR to merge_blocked before continuing the PR.
An abandoned unmerged attempt stays preserved; restart under the issue and applicable
repository policy, without transferring its approval. Outage handling uses the existing
canonical fallback only; a saved snapshot is not outage evidence.

Return the current work link, next safe action and exact blocker, if any. Do not start
another unit or repeat generic governance mechanics in chat.
