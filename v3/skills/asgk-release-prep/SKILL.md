---
name: asgk-release-prep
description: Prepare, execute when separately approved, or close out a source release; never invoked as routine worker governance.
---

# Source release preparation

Source-maintainer responsibility. Use the canonical SOURCE_ONLY_RELEASE_POLICY and
current release issue; packet, role, program execution authorization and Skill are not
publication approval.

Preparation freezes tag, title, exact commit, distribution, release notes and rollback.
Execution requires the separate durable human approval required by repository policy.
Changed head/notes/metadata require the applicable refreshed approval. Do not move v1
tags, edit published history or hide a failed release attempt.

Validate README, CURRENT_STATUS and SOURCE_ONLY_RELEASE_POLICY using the existing
release-state-check and required source/project checks. Local document checks do not
prove remote tag or release existence. Verify actual GitHub release provenance separately.

Closeout links release issue, tag, commit, checks, content PRs and required decision review.
Refresh recovery documents only inside their authorized scope. Remind about source vs
installed Skill versions; no global synchronization by default. Candidate branch testing
is not release preparation approval, and no candidate CLI performs publication.
