---
name: asgk-gatekeeper
description: Check a scoped GitHub PR's readiness through existing validators, reviews and current-head evidence; never approve by role name.
---

# Gatekeeper

This Skill sequences existing checks; it creates neither an approval role nor a new gate.
Use the current issue, PR head, changed paths, canonical merge policy and human-gate
evidence. The source implementation is body-coherence → merge-decision → live check-pr.
In a target without those commands, report the limit and use its actual equivalent.

Check latest unambiguous CI observations, not any historical success. Preserve check
identity/provider and current-head review. A role alias is not independent review;
record actual actors and compare to the author where separation is required.

Missing issue acceptance evidence, failed tests, scope drift or unresolved non-human
conditions block readiness. Only an exact existing human-gated operation warrants
requires_human. Semantic judgment does not create a universal extra human gate.

Report blocked, requires_human or eligible with evidence and limits. Eligible never
means approved or low-risk by inference. Do not close, merge or publish from a green
candidate snapshot; recheck live state through the canonical flow immediately before
any separately authorized mutation.
