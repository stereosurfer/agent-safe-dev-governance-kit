import contextlib
import copy
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import asgk3 as a
import github_workflow as w


class GithubWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / 'demo'
        w.workflow_demo(self.out)
        self.root = self.out / 'workspace'
        artifacts = self.out / 'artifacts'
        self.snapshot = a.load(artifacts / 'snapshot.json')
        self.final = a.load(artifacts / 'pre-closeout-snapshot.json')
        self.indexed_final = a.load(artifacts / 'final-snapshot.json')
        self.prior = a.load(artifacts / 'prior-snapshot.json')
        self.assignment = a.load(artifacts / 'assignment.json')
        self.packet = a.load(artifacts / 'packet.json')
        self.report = a.load(artifacts / 'report.json')

    def fails(self, code, callback):
        with self.assertRaises(a.Invalid) as error:
            callback()
        self.assertEqual(code, error.exception.finding['code'])

    def project(self):
        return w.project(self.snapshot, self.assignment, self.root)

    def observed_packet(self, source='gh_api'):
        snapshot = copy.deepcopy(self.snapshot)
        snapshot['source'] = source
        w.git(self.root, 'remote', 'add', 'upstream',
              'git@github.com:example/asgk-synthetic.git')
        return snapshot, w.project(snapshot, self.assignment, self.root)

    def observe(self):
        return w.observe_work(self.snapshot, self.packet, self.report, self.root)

    def canonical_yaml_closeout(self):
        return ('Completed.\n\n```yaml\nissue_closeout_review:\n  issue: "#1"\n'
                '  status: completed\n'
                '  decision_analysis:\n'
                '    decision_made: "Keep trace"\n'
                '    why_this_path: "The next worker needs the GitHub decision trail."\n'
                '    rejected_paths:\n'
                '      - path: "Use a chat-only summary"\n'
                '        reason: "It cannot be independently recovered."\n'
                '    reusable_signal:\n'
                '      applies_later: true\n'
                '      reason: "Keep bounded closeout evidence for later handoff."\n'
                '  decisions:\n'
                '    - decision: "Keep trace"\n'
                '      reason: "The issue and PR evidence stays linked."\n'
                '      evidence:\n'
                '        - "#1"\n'
                '```\n')

    def test_issue_projection_positive(self):
        self.assertEqual(self.packet, self.project())
        self.assertEqual('not_checked_fixture_without_remote', self.packet['checkout_identity'])
        self.assertIn(self.packet['issue'], w.work_text(self.packet))
        self.assertNotIn('merge_allowed', w.work_text(self.packet))
        self.assertIn('not a worker-verified live issue read', w.work_text(self.packet))

    def test_card_draft_labels_controller_projection(self):
        snapshot, packet = self.observed_packet()
        metadata, body = w.card_draft(snapshot, packet, self.root)
        self.assertEqual('controller_supplied_snapshot', metadata['evidence_class'])
        self.assertEqual('gh_api', metadata['snapshot_source'])
        self.assertEqual('not_checked', metadata['worker_live_issue_read'])
        self.assertEqual(packet['packet_id'], metadata['packet_id'])
        projected = json.loads(body.split('## Bounded work projection\n\n```json\n', 1)[1]
                               .split('\n```', 1)[0])
        self.assertEqual(packet['canonical_fields']['objective'], projected['objective'])
        self.assertEqual(packet['assignment']['selected_paths'], projected['selected_paths'])
        self.assertIn('first add a Kanban comment containing a partial handoff', body)
        self.assertIn('then block the card', body)
        self.assertIn('do not attempt a terminal command first', body)
        self.assertIn('Kanban status is runtime state', body)
        self.assertIn('`none` authorizes no repository file changes', body)

    def test_card_draft_rejects_fixture_stale_closed_and_tampered(self):
        self.fails('CARD_SOURCE', lambda: w.card_draft(self.snapshot, self.packet, self.root))
        snapshot, packet = self.observed_packet()
        stale = copy.deepcopy(snapshot); stale['captured_at'] = '2000-01-01T00:00:00Z'
        self.fails('STALE_SNAPSHOT', lambda: w.card_draft(stale, packet, self.root))
        closed = copy.deepcopy(snapshot); closed['issue']['state'] = 'closed'
        self.fails('ISSUE_CLOSED', lambda: w.card_draft(closed, packet, self.root))
        tampered = copy.deepcopy(packet); tampered['canonical_fields']['objective'] = ['Do anything']
        self.fails('STALE_PACKET', lambda: w.card_draft(snapshot, tampered, self.root))

    def test_card_draft_connector_source_is_explicit(self):
        snapshot, packet = self.observed_packet('connector_export')
        metadata, body = w.card_draft(snapshot, packet, self.root)
        self.assertEqual('connector_export', metadata['snapshot_source'])
        self.assertIn('"snapshot_source": "connector_export"', body)

    def test_missing_issue(self):
        self.snapshot['issue'] = None
        self.fails('ISSUE_REQUIRED', self.project)

    def test_wrong_repository(self):
        self.snapshot['repository'] = 'other/repo'
        self.fails('ISSUE_ID', self.project)

    def test_real_snapshot_requires_matching_checkout_remote(self):
        self.snapshot['source'] = 'gh_api'
        self.fails('REPO_IDENTITY', self.project)
        w.git(self.root, 'remote', 'add', 'upstream', 'https://github.com/other/repo.git')
        self.fails('REPO_IDENTITY', self.project)

    def test_matching_non_origin_remote_binds_real_snapshot(self):
        self.snapshot['source'] = 'connector_export'
        w.git(self.root, 'remote', 'add', 'upstream', 'ssh://git@github.com/example/asgk-synthetic.git')
        self.assertEqual('matching_configured_github_remote', self.project()['checkout_identity'])

    def test_fixture_with_wrong_configured_remote_is_rejected(self):
        w.git(self.root, 'remote', 'add', 'upstream', 'https://github.com/other/repo.git')
        self.fails('REPO_IDENTITY', self.project)

    def test_closed_issue_no_new_work(self):
        self.snapshot['issue']['state'] = 'closed'
        self.fails('ISSUE_CLOSED', self.project)

    def test_missing_canonical_field(self):
        self.snapshot['issue']['body'] = self.snapshot['issue']['body'].replace('### reason', '### omitted')
        self.fails('TP_ISSUE_SCOPE_INVALID', self.project)

    def test_duplicate_canonical_field(self):
        self.snapshot['issue']['body'] += '\n### objective\nDifferent work\n'
        self.fails('TP_ISSUE_TASK_FIELD_AMBIGUOUS', self.project)

    def test_expanded_write(self):
        self.assignment['selected_paths'].append('outside.txt')
        self.fails('REFINEMENT', self.project)

    def test_expanded_context(self):
        self.assignment['selected_context'].append('https://github.com/example/asgk-synthetic/issues/999')
        self.fails('REFINEMENT', self.project)

    def test_forbidden(self):
        self.assignment['forbidden_paths'] = ['README.md']
        self.fails('FORBIDDEN', self.project)

    def test_role_ceiling(self):
        self.assignment['role_ceiling'] = ['other.txt']
        self.assignment['role_ref'] = self.packet['issue']
        self.fails('ROLE_CEILING', self.project)

    def test_role_does_not_grant_more_than_issue(self):
        self.assignment['selected_paths'] = ['other.txt']
        self.assignment['role_ceiling'] = ['other.txt']
        self.assignment['role_ref'] = self.packet['issue']
        self.fails('REFINEMENT', self.project)

    def test_stale_snapshot(self):
        self.snapshot['captured_at'] = '2000-01-01T00:00:00Z'
        self.fails('STALE_SNAPSHOT', self.project)

    def test_issue_changed(self):
        self.snapshot['issue']['body'] += '\nNew stop condition applies.\n'
        self.fails('STALE_PACKET', lambda: w.check_packet(self.snapshot, self.packet, self.root))

    def test_comment_changed(self):
        self.snapshot['comments'] = [dict(html_url=self.packet['issue'] + '#issuecomment-99', body='New material instruction')]
        self.fails('STALE_PACKET', lambda: w.check_packet(self.snapshot, self.packet, self.root))

    def test_new_material_comment_blocks_stale_closeout(self):
        self.final['comments'] = [dict(html_url=self.packet['issue'] + '#issuecomment-99',
                                       body='Owner correction: do not close yet.')]
        self.fails('STALE_PACKET', lambda: w.closeout_draft(
            self.final, self.packet, self.report, self.root, 'completed'))

    def test_rehashed_fake_scope(self):
        self.packet['refinement']['allowed_paths'] = ['other.txt']
        self.packet['packet_id'] = a.digest({k: v for k, v in self.packet.items() if k != 'packet_id'})
        self.fails('STALE_PACKET', lambda: w.check_packet(self.snapshot, self.packet, self.root))

    def test_actor_binding(self):
        self.report['actor_id'] = 'another-person'
        self.fails('REPORT_BINDING', self.observe)

    def test_run_binding(self):
        self.report['run_id'] = 'run-B'
        self.fails('REPORT_BINDING', self.observe)

    def test_inplace_commit_supported(self):
        result = self.observe()
        self.assertEqual('pass', result['result'])
        self.assertEqual(['README.md'], result['changed_paths'])
        self.assertEqual('not_checked', result['human_gate']['status'])

    def test_dirty_is_blocked_not_lost(self):
        (self.root / 'README.md').write_text('uncommitted', encoding='utf-8')
        result, draft = w.handoff_draft(self.snapshot, self.packet, self.report, self.root)
        self.assertEqual('blocked', result['result'])
        self.assertIn('DIRTY_WORKTREE', draft)

    def test_out_of_scope_committed_file(self):
        (self.root / 'outside.txt').write_text('outside scope', encoding='utf-8')
        w.git(self.root, 'add', 'outside.txt')
        w.git(self.root, '-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'Synthetic out-of-scope mutation')
        self.report['head_sha'] = w.git(self.root, 'rev-parse', 'HEAD').decode().strip()
        self.fails('DIFF_SCOPE', self.observe)
        report_file = self.out / 'out-of-scope-report.json'
        report_file.write_text(json.dumps(self.report), encoding='utf-8')
        output = self.out / 'out-of-scope-handoff'
        source_root = Path(__file__).resolve().parents[1]
        completed = subprocess.run(
            [sys.executable, str(source_root / 'scripts/asgk.py'), 'workflow', 'handoff',
             '--snapshot', str(self.out / 'artifacts/snapshot.json'),
             '--packet', str(self.out / 'artifacts/packet.json'),
             '--report', str(report_file), '--repo-root', str(self.root),
             '--out', str(output)],
            cwd=source_root, capture_output=True, text=True, check=False,
        )
        self.assertEqual(1, completed.returncode)
        self.assertFalse(completed.stderr, completed.stderr)
        self.assertEqual('DIFF_SCOPE', json.loads(completed.stdout)['findings'][0]['code'])
        self.assertFalse(output.exists())

    def test_symlink_committed_output(self):
        (self.root / 'README.md').unlink()
        (self.root / 'README.md').symlink_to('.git/HEAD')
        w.git(self.root, 'add', 'README.md')
        w.git(self.root, '-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'Synthetic symlink')
        self.report['head_sha'] = w.git(self.root, 'rev-parse', 'HEAD').decode().strip()
        self.fails('UNSUPPORTED_FILE_MODE', self.observe)

    def test_current_head_mismatch(self):
        self.report['head_sha'] = self.assignment['base_sha']
        self.fails('LOCAL_HEAD', self.observe)

    def test_missing_validation_produces_partial_handoff(self):
        self.report['validations'] = []
        self.report['state'] = 'partial'
        self.report['remaining'] = ['Validation not run']
        result, draft = w.handoff_draft(self.snapshot, self.packet, self.report, self.root)
        self.assertEqual('blocked', result['result'])
        self.assertIn('Validation not run', draft)
        self.assertIn('VALIDATION_INCOMPLETE', draft)

    def test_false_pass(self):
        self.report['validations'][0]['source'] = 'not_run'
        self.fails('FALSE_PASS', self.observe)

    def test_invalid_validation_status(self):
        self.report['validations'][0]['status'] = 'approved'
        self.fails('STATUS', self.observe)

    def test_missing_alternatives(self):
        self.report['decisions'][0]['rejected_paths'] = []
        self.fails('REJECTED_PATHS', self.observe)

    def test_missing_applicability(self):
        self.report['decisions'][0]['does_not_apply_when'] = []
        self.fails('LIST', self.observe)

    def test_decision_cycle(self):
        self.report['decisions'][0]['parent'] = 'D1'
        self.fails('DECISION_PARENT', self.observe)

    def test_relation_self_cycle(self):
        self.report['relations'][0]['target'] = self.packet['issue']
        self.fails('RELATION_CYCLE', self.observe)

    def test_completed_requires_merge(self):
        self.fails('MERGE_REQUIRED', lambda: w.closeout_draft(self.snapshot, self.packet, self.report, self.root, 'completed'))

    def test_partial_cannot_complete(self):
        self.report['remaining'] = ['Waiting for project check']
        self.fails('INCOMPLETE_CLOSEOUT', lambda: w.closeout_draft(self.final, self.packet, self.report, self.root, 'completed'))

    def test_completed_has_full_closeout(self):
        result, text = w.closeout_draft(self.final, self.packet, self.report, self.root, 'completed')
        self.assertEqual('pass', result['result'])
        for field in ('issue_closeout_review', 'rejected_paths', 'applies_when', 'does_not_apply_when', 'known_limits', 'relations', 'merge_commit'):
            self.assertIn(field, text)
        self.assertIn('DRAFT', text)

    def test_failed_pr_attempt_remains_in_completed_lineage(self):
        failed = copy.deepcopy(self.final['prs'][0])
        failed['pr']['number'] = 2
        failed['pr']['html_url'] = self.packet['issue'].replace('/issues/1', '/pull/2')
        failed['pr']['head']['sha'] = self.assignment['base_sha']
        failed['pr']['merged'] = False
        failed['pr']['merge_commit_sha'] = None
        failed['pr']['body'] = ('References ' + self.packet['issue'] +
                                '#issuecomment-99. Rejected first approach; replacement follows.')
        self.final['prs'].insert(0, failed)
        result, text = w.closeout_draft(self.final, self.packet, self.report, self.root, 'completed')
        self.assertEqual('pass', result['result'])
        self.assertIn(failed['pr']['html_url'], text)
        self.assertIn('pr_body_issue_reference', text)
        self.assertIn('"merge_commit": null', text)

    def test_unrelated_selected_pr_cannot_join_closeout(self):
        unrelated = copy.deepcopy(self.final['prs'][0])
        unrelated['pr']['number'] = 2
        unrelated['pr']['html_url'] = self.packet['issue'].replace('/issues/1', '/pull/2')
        unrelated['pr']['head']['sha'] = self.assignment['base_sha']
        unrelated['pr']['merged'] = False
        unrelated['pr']['merge_commit_sha'] = None
        unrelated['pr']['body'] = 'Unrelated change with no issue reference.'
        self.final['prs'].insert(0, unrelated)
        self.fails('UNRELATED_PR', lambda: w.closeout_draft(
            self.final, self.packet, self.report, self.root, 'completed'))

    def test_issue_comment_backlink_preserves_failed_attempt(self):
        failed = copy.deepcopy(self.final['prs'][0])
        failed['pr']['number'] = 2
        failed['pr']['html_url'] = self.packet['issue'].replace('/issues/1', '/pull/2')
        failed['pr']['head']['sha'] = self.assignment['base_sha']
        failed['pr']['merged'] = False
        failed['pr']['merge_commit_sha'] = None
        failed['pr']['body'] = 'Rejected attempt.'
        self.final['prs'].insert(0, failed)
        self.final['comments'] = [dict(html_url=self.packet['issue'] + '#issuecomment-99',
                                       body='Rejected attempt: ' + failed['pr']['html_url'])]
        refreshed = w.project(self.final, self.assignment, self.root, review=True)
        self.report['packet_id'] = refreshed['packet_id']
        _, text = w.closeout_draft(self.final, refreshed, self.report, self.root, 'completed')
        self.assertIn('issue_comment_pr_reference', text)

    def test_open_failed_attempt_blocks_completed_closeout(self):
        failed = copy.deepcopy(self.final['prs'][0])
        failed['pr']['number'] = 2
        failed['pr']['html_url'] = self.packet['issue'].replace('/issues/1', '/pull/2')
        failed['pr']['head']['sha'] = self.assignment['base_sha']
        failed['pr']['state'] = 'open'
        failed['pr']['merged'] = False
        failed['pr']['merge_commit_sha'] = None
        self.final['prs'].insert(0, failed)
        self.fails('UNRESOLVED_PR_ATTEMPT', lambda: w.closeout_draft(
            self.final, self.packet, self.report, self.root, 'completed'))

    def test_closed_issue_review_is_not_new_work(self):
        self.final['issue']['state'] = 'closed'
        self.assertEqual('pass', w.closeout_draft(self.final, self.packet, self.report, self.root, 'completed')[0]['result'])

    def test_missing_closing_reference(self):
        self.final['prs'][0]['pr']['body'] = 'Unrelated PR'
        self.fails('CLOSING_REFERENCE', lambda: w.closeout_draft(self.final, self.packet, self.report, self.root, 'completed'))

    def test_wrong_pr_head(self):
        self.final['prs'][0]['pr']['head']['sha'] = self.assignment['base_sha']
        self.fails('STALE_HEAD', lambda: w.closeout_draft(self.final, self.packet, self.report, self.root, 'completed'))

    def test_abandoned_closeout_without_fake_merge(self):
        self.report['state'] = 'blocked'
        result, draft = w.closeout_draft(self.snapshot, self.packet, self.report, self.root, 'closed_not_done')
        self.assertEqual('blocked', result['result'])
        self.assertIn('closed_not_done', draft)

    def test_superseded_needs_relation(self):
        self.report['relations'] = []
        self.fails('RELATION_REQUIRED', lambda: w.closeout_draft(self.snapshot, self.packet, self.report, self.root, 'superseded'))

    def test_supersession_direction(self):
        self.report['relations'][0]['kind'] = 'superseded_by'
        result, draft = w.closeout_draft(self.snapshot, self.packet, self.report, self.root, 'superseded')
        self.assertEqual('pass', result['result'])
        self.assertIn('superseded_by', draft)

    def test_exact_recorded_pr_head_drift(self):
        observed = copy.deepcopy(self.final)
        observed['prs'][0]['pr']['state'] = 'open'
        observed['prs'][0]['pr']['merged'] = False
        packet = w.project(observed, self.assignment, self.root)
        observed['prs'][0]['pr']['head']['sha'] = self.assignment['base_sha']
        self.fails('STALE_HEAD', lambda: w.check_packet(observed, packet, self.root, review=True))

    def test_no_silent_decision_truncation(self):
        first = self.report['decisions'][0]
        self.report['decisions'] = [dict(first, id=f'D{i}') for i in range(6)]
        self.fails('REVIEW_LIMIT', lambda: w.closeout_draft(self.final, self.packet, self.report, self.root, 'completed'))

    def test_no_silent_word_truncation(self):
        self.report['decisions'][0]['reason'] = 'material ' * 450
        self.fails('REVIEW_LIMIT', lambda: w.closeout_draft(self.final, self.packet, self.report, self.root, 'completed'))

    def test_search_closeouts_not_repo(self):
        result = w.search([self.indexed_final, self.prior], 'Keep GitHub as work ledger')
        self.assertEqual('pass', result['result'])
        self.assertEqual(1, len(result['matches']))
        self.assertIn('#issuecomment-', result['matches'][0]['url'])
        self.assertEqual('json_shape_checked', result['matches'][0]['evidence_class'])
        self.assertEqual([], result['candidates'])

    def test_canonical_yaml_is_shape_checked_edge(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        comment_url = self.packet['issue'] + '#issuecomment-50'
        snapshot['comments'] = [dict(html_url=comment_url, body=self.canonical_yaml_closeout())]
        result = w.search([snapshot], 'Keep trace')
        self.assertEqual('pass', result['result'])
        self.assertEqual([comment_url], [item['url'] for item in result['matches']])
        self.assertEqual('yaml_subset_shape_checked', result['matches'][0]['evidence_class'])
        self.assertEqual([], result['candidates'])
        self.assertIn('semantic correctness', result['not_checked'])
        traced = w.trace([snapshot], self.packet['issue'])
        issue_node = next(node for node in traced['nodes'] if node['url'] == self.packet['issue'])
        self.assertIn(comment_url, issue_node['links'])
        comment_node = next(node for node in traced['nodes'] if node['url'] == comment_url)
        self.assertEqual('yaml_subset_shape_checked', comment_node['evidence_class'])
        self.assertEqual([], traced['candidates'])
        self.assertEqual('pass', traced['result'])

    def test_draft_banner_never_promotes_yaml_to_checked_edge(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        comment_url = self.packet['issue'] + '#issuecomment-93'
        for banner in ('DRAFT — do not post or close issue.',
                       'DRAFT closeout — pending review',
                       'DRAFT closeout — not posted',
                       'Status: DRAFT — do not post or close issue.',
                       '**Status:** DRAFT — do not post or close issue.',
                       'This is a DRAFT — do not post or close issue.'):
            with self.subTest(banner=banner):
                snapshot['comments'] = [dict(
                    html_url=comment_url,
                    body=banner + '\n\n' + self.canonical_yaml_closeout(),
                )]
                searched = w.search([snapshot], 'Keep trace')
                self.assertEqual([], searched['matches'])
                traced = w.trace([snapshot], self.packet['issue'])
                issue_node = next(node for node in traced['nodes'] if node['url'] == self.packet['issue'])
                self.assertNotIn(comment_url, issue_node['links'])
                self.assertIn('WF_CLOSEOUT_NOT_FOUND', [item['code'] for item in traced['findings']])

    def test_draft_inside_yaml_never_promotes_closeout(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        comment_url = self.packet['issue'] + '#issuecomment-97'
        canonical = self.canonical_yaml_closeout()
        bodies = (
            canonical.replace('issue_closeout_review:', '# DRAFT — do not post\nissue_closeout_review:', 1),
            canonical.replace('    decision_made: "Keep trace"',
                              '    decision_made: "DRAFT — do not post or close issue"'),
        )
        for body in bodies:
            with self.subTest(body=body):
                snapshot['comments'] = [dict(html_url=comment_url, body=body)]
                searched = w.search([snapshot], 'issue_closeout_review')
                self.assertEqual([], searched['matches'])
                self.assertEqual([], searched['candidates'])
                traced = w.trace([snapshot], self.packet['issue'])
                issue_node = next(node for node in traced['nodes'] if node['url'] == self.packet['issue'])
                self.assertNotIn(comment_url, issue_node['links'])
                self.assertIn('WF_CLOSEOUT_NOT_FOUND', [item['code'] for item in traced['findings']])

    def test_rejected_draft_option_is_valid_yaml_decision_evidence(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        comment_url = self.packet['issue'] + '#issuecomment-98'
        closeout = self.canonical_yaml_closeout().replace(
            'Use a chat-only summary', 'Draft chat-only summary')
        snapshot['comments'] = [dict(
            html_url=comment_url,
            body='The draft design was rejected.\n\n' + closeout,
        )]
        searched = w.search([snapshot], 'Draft chat-only summary')
        self.assertEqual([comment_url], [item['url'] for item in searched['matches']])
        self.assertEqual('yaml_subset_shape_checked', searched['matches'][0]['evidence_class'])
        traced = w.trace([snapshot], self.packet['issue'])
        issue_node = next(node for node in traced['nodes'] if node['url'] == self.packet['issue'])
        self.assertIn(comment_url, issue_node['links'])

    def test_rejected_draft_closeout_automation_is_final_decision_text(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        comment_url = self.packet['issue'] + '#issuecomment-99'
        closeout = self.canonical_yaml_closeout().replace(
            'decision_made: "Keep trace"',
            'decision_made: "Draft closeout automation was rejected."')
        snapshot['comments'] = [dict(html_url=comment_url, body=closeout)]
        searched = w.search([snapshot], 'Draft closeout automation was rejected.')
        self.assertEqual([comment_url], [item['url'] for item in searched['matches']])
        self.assertEqual('yaml_subset_shape_checked', searched['matches'][0]['evidence_class'])
        traced = w.trace([snapshot], self.packet['issue'])
        issue_node = next(node for node in traced['nodes'] if node['url'] == self.packet['issue'])
        self.assertIn(comment_url, issue_node['links'])

    def test_explicit_draft_label_in_rejected_path_does_not_discard_final_closeout(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        comment_url = self.packet['issue'] + '#issuecomment-100'
        closeout = self.canonical_yaml_closeout().replace(
            'Use a chat-only summary', 'DRAFT closeout — do not post')
        snapshot['comments'] = [dict(html_url=comment_url, body=closeout)]
        searched = w.search([snapshot], 'DRAFT closeout — do not post')
        self.assertEqual([comment_url], [item['url'] for item in searched['matches']])
        self.assertEqual('yaml_subset_shape_checked', searched['matches'][0]['evidence_class'])
        traced = w.trace([snapshot], self.packet['issue'])
        issue_node = next(node for node in traced['nodes'] if node['url'] == self.packet['issue'])
        self.assertIn(comment_url, issue_node['links'])

    def test_yaml_search_does_not_promote_prose_only_query(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        comment_url = self.packet['issue'] + '#issuecomment-94'
        snapshot['comments'] = [dict(
            html_url=comment_url,
            body='Bulk-copy appears only in this unverified introduction.\n\n'
                 + self.canonical_yaml_closeout(),
        )]
        searched = w.search([snapshot], 'Bulk-copy')
        self.assertEqual('pass', searched['result'])
        self.assertEqual([], searched['matches'])
        checked = w.search([snapshot], 'Keep trace')
        self.assertEqual([comment_url], [item['url'] for item in checked['matches']])
        self.assertEqual('yaml_subset_shape_checked', checked['matches'][0]['evidence_class'])

    def test_yaml_search_ignores_non_substantive_comment_query(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        comment_url = self.packet['issue'] + '#issuecomment-96'
        snapshot['comments'] = [dict(
            html_url=comment_url,
            body=self.canonical_yaml_closeout().replace(
                'issue_closeout_review:', '# Bulk-copy appears only in a YAML comment\nissue_closeout_review:', 1),
        )]
        searched = w.search([snapshot], 'Bulk-copy')
        self.assertEqual('pass', searched['result'])
        self.assertEqual([], searched['matches'])
        self.assertEqual([], searched['candidates'])
        checked = w.search([snapshot], 'Keep trace')
        self.assertEqual('yaml_subset_shape_checked', checked['matches'][0]['evidence_class'])

        snapshot['comments'] = [dict(
            html_url=comment_url,
            body=self.canonical_yaml_closeout().replace(
                '  status: completed', '  status: completed\n  unrelated_label: "Bulk-copy"', 1),
        )]
        unrelated = w.search([snapshot], 'Bulk-copy')
        self.assertEqual([], unrelated['matches'])
        self.assertEqual([], unrelated['candidates'])

    def test_nested_markdown_yaml_example_never_forms_closeout_edge(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        comment_url = self.packet['issue'] + '#issuecomment-95'
        for opening, closing in (('````markdown', '````'), ('~~~~markdown', '~~~~'),
                                 ('<!--', '-->'), ('<pre>', '</pre>'),
                                 ('<code>', '</code>'), ('<blockquote>', '</blockquote>'),
                                 ('<![CDATA[', ']]>'), ('<?render', '?>')):
            with self.subTest(opening=opening):
                snapshot['comments'] = [dict(
                    html_url=comment_url,
                    body=opening + '\n' + self.canonical_yaml_closeout() + '\n' + closing,
                )]
                searched = w.search([snapshot], 'Keep trace')
                self.assertEqual([], searched['matches'])
                self.assertEqual([], searched['candidates'])
                traced = w.trace([snapshot], self.packet['issue'])
                issue_node = next(node for node in traced['nodes'] if node['url'] == self.packet['issue'])
                self.assertNotIn(comment_url, issue_node['links'])
                self.assertIn('WF_CLOSEOUT_NOT_FOUND', [item['code'] for item in traced['findings']])

    def test_malformed_and_wrong_issue_yaml_remain_candidates_not_proof(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        canonical = self.canonical_yaml_closeout()
        bodies = [
            '```yaml\nissue_closeout_review:\n  issue: "#1"\n  decision_analysis: {}\n```',
            canonical.replace('\n```\n', '\n  decision_analysis: {}\n  decisions: []\n```\n'),
            canonical.replace('    decision_made: "Keep trace"', '    decision_made:"Keep trace"'),
            canonical.replace('  issue: "#1"', '  issue: "#999"'),
            canonical.replace('    decision_made: "Keep trace"', '    decision_made: &bad "Keep trace"'),
            canonical.replace('    decision_made: "Keep trace"', '    decision_made: *bad'),
            canonical.replace('    decision_made: "Keep trace"', '    decision_made: !tag "Keep trace"'),
            canonical.replace('    decision_made: "Keep trace"', '    decision_made: |'),
            canonical.replace('    decision_made: "Keep trace"', '    <<: *bad\n    decision_made: "Keep trace"'),
            canonical.replace('  status: completed', '  status: completed\n  status: completed'),
            canonical.replace('        reason: "It cannot be independently recovered."',
                              '        reason: "It cannot be independently recovered."\n        reason: "duplicate"'),
            canonical.replace('      reason: "The issue and PR evidence stays linked."',
                              '        reason: "The issue and PR evidence stays linked."'),
            canonical.replace('      evidence:\n        - "#1"', '      evidence: []'),
            canonical.replace('      applies_later: true', '      applies_later: yes'),
            canonical.replace('      reason: "Keep bounded closeout evidence for later handoff."',
                              '      reason: ""'),
            canonical.replace('    decision_made: "Keep trace"', '    decision_made: .nan'),
            canonical.replace('    decision_made: "Keep trace"', '    decision_made: .inf'),
            canonical.replace('    decision_made: "Keep trace"', '    decision_made: True'),
            canonical.replace('    decision_made: "Keep trace"', '    decision_made: 2026-09-25'),
            canonical.replace('\n```\n', '\n---\n```\n'),
            canonical + canonical,
        ]
        for body in bodies:
            with self.subTest(body=body):
                comment_url = self.packet['issue'] + '#issuecomment-51'
                snapshot['comments'] = [dict(html_url=comment_url, body=body)]
                searched = w.search([snapshot], 'issue_closeout_review')
                self.assertEqual([], searched['matches'])
                self.assertEqual([comment_url], [item['url'] for item in searched['candidates']])
                self.assertEqual('warning', searched['result'])
                self.assertEqual('incomplete', searched['domain_result'])
                traced = w.trace([snapshot], self.packet['issue'])
                issue_node = next(node for node in traced['nodes']
                                  if node['url'] == self.packet['issue'])
                self.assertNotIn(comment_url, issue_node['links'])
                self.assertEqual([comment_url], [item['url'] for item in traced['candidates']])
                self.assertEqual('warning', traced['result'])
                self.assertEqual('incomplete', traced['domain_result'])

    def test_valid_and_invalid_yaml_comments_remain_separate(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        valid = self.canonical_yaml_closeout()
        good_url = self.packet['issue'] + '#issuecomment-91'
        bad_url = self.packet['issue'] + '#issuecomment-92'
        snapshot['comments'] = [dict(html_url=good_url, body=valid),
                                dict(html_url=bad_url, body=valid.replace('"#1"', '"#999"', 1))]
        searched = w.search([snapshot], 'Keep trace')
        self.assertEqual('warning', searched['result'])
        self.assertEqual([good_url], [x['url'] for x in searched['matches']])
        self.assertEqual([bad_url], [x['url'] for x in searched['candidates']])
        traced = w.trace([snapshot], self.packet['issue'])
        issue_node = next(x for x in traced['nodes'] if x['url'] == self.packet['issue'])
        self.assertIn(good_url, issue_node['links'])
        self.assertNotIn(bad_url, issue_node['links'])
        self.assertEqual('incomplete', traced['domain_result'])


    def test_json_closeout_survives_ordinary_draft_prose(self):
        snapshot = copy.deepcopy(self.indexed_final)
        issue_url = snapshot['issue']['html_url']
        target = next(comment for comment in snapshot['comments']
                      if w.json_closeout_shape(comment['body'], issue_url))
        original = target['body']
        for prose in ('Note: the draft design was rejected.',
                      'Draft design was rejected.',
                      'Draft closeout automation was rejected.',
                      'The draft design was not final, so we rejected it.',
                      'The draft decision did not close the issue; this review is final.',
                      'The unfinalized draft design was rejected in favor of the shipped approach.',
                      'The unposted draft announcement was rejected; this is the final closeout.',
                      'Unfinalized draft design was rejected in favor of the shipped approach.',
                      'Unposted draft announcement was rejected; this is the final closeout.',
                      'We do not post draft artifacts publicly; this final closeout records why.',
                      'The draft proposal was rejected; do not publish its private source, but this review is final.'):
            with self.subTest(prose=prose):
                target['body'] = prose + '\n\n' + original
                searched = w.search([snapshot], 'Keep GitHub as work ledger')
                self.assertEqual('pass', searched['result'])
                self.assertEqual('json_shape_checked', searched['matches'][0]['evidence_class'])
                traced = w.trace([snapshot], issue_url)
                issue_node = next(node for node in traced['nodes'] if node['url'] == issue_url)
                self.assertIn(target['html_url'], issue_node['links'])

    def test_json_closeout_inside_example_container_is_not_checked(self):
        snapshot = copy.deepcopy(self.indexed_final)
        issue_url = snapshot['issue']['html_url']
        target = next(comment for comment in snapshot['comments']
                      if w.json_closeout_shape(comment['body'], issue_url))
        original = target['body']
        for opening, closing in (('<!--', '-->'),
                                 ('~~~~markdown', '~~~~'),
                                 ('````markdown', '````'),
                                 ('<details><summary>Example, not final</summary>', '</details>'),
                                 ('<pre>', '</pre>')):
            with self.subTest(opening=opening):
                target['body'] = opening + '\n' + original + '\n' + closing
                self.assertFalse(w.json_closeout_shape(target['body'], issue_url))
                searched = w.search([snapshot], 'Keep GitHub as work ledger')
                self.assertEqual([], searched['matches'])
                traced = w.trace([snapshot], issue_url)
                issue_node = next(node for node in traced['nodes']
                                  if node['url'] == issue_url)
                self.assertNotIn(target['html_url'], issue_node['links'])
                self.assertIn('WF_CLOSEOUT_NOT_FOUND',
                              [finding['code'] for finding in traced['findings']])

        target['body'] = 'Earlier example omitted.\n\n' + original
        self.assertTrue(w.json_closeout_shape(target['body'], issue_url))
        checked = w.search([snapshot], 'Keep GitHub as work ledger')
        self.assertEqual('json_shape_checked', checked['matches'][0]['evidence_class'])

        target['body'] = '<!-- Hidden contrary proposal. -->\n\n' + original
        self.assertFalse(w.json_closeout_shape(target['body'], issue_url))
        self.assertEqual([], w.search([snapshot], 'Hidden contrary proposal')['matches'])

        target['body'] = 'Unrelated preamble only.\n\n' + original
        self.assertTrue(w.json_closeout_shape(target['body'], issue_url))
        self.assertEqual([], w.search([snapshot], 'Unrelated preamble only')['matches'])

    def test_multiple_json_closeouts_in_one_comment_are_not_checked(self):
        snapshot = copy.deepcopy(self.indexed_final)
        issue_url = snapshot['issue']['html_url']
        target = next(comment for comment in snapshot['comments']
                      if w.json_closeout_shape(comment['body'], issue_url))
        original = target['body']
        self.assertIn('Keep GitHub as work ledger', original)
        conflicting = original.replace('Keep GitHub as work ledger',
                                       'Reject GitHub as work ledger', 1)
        variants = (conflicting,
                    conflicting.replace('```json', '```JSON', 1),
                    conflicting.replace('```json', '~~~json', 1).replace('\n```', '\n~~~', 1))
        for second in variants:
            with self.subTest(second=second[:20]):
                target['body'] = original + '\n' + second
                self.assertFalse(w.json_closeout_shape(target['body'], issue_url))
                searched = w.search([snapshot], 'Keep GitHub as work ledger')
                self.assertEqual([], searched['matches'])
                traced = w.trace([snapshot], issue_url)
                issue_node = next(node for node in traced['nodes'] if node['url'] == issue_url)
                self.assertNotIn(target['html_url'], issue_node['links'])
                self.assertIn('WF_CLOSEOUT_NOT_FOUND',
                              [finding['code'] for finding in traced['findings']])

        target['body'] = original
        self.assertTrue(w.json_closeout_shape(target['body'], issue_url))
        checked = w.search([snapshot], 'Keep GitHub as work ledger')
        self.assertEqual('json_shape_checked', checked['matches'][0]['evidence_class'])

    def test_explicit_draft_banner_never_promotes_json_closeout(self):
        snapshot = copy.deepcopy(self.indexed_final)
        issue_url = snapshot['issue']['html_url']
        target = next(comment for comment in snapshot['comments']
                      if w.json_closeout_shape(comment['body'], issue_url))
        original = target['body']
        for banner in ('DRAFT — do not post or close issue.',
                       'DRAFT closeout — pending review',
                       'DRAFT closeout — not posted',
                       'Status: DRAFT — do not post or close issue.',
                       '**Status:** DRAFT — do not post or close issue.',
                       'This is a DRAFT — do not post or close issue.',
                       '# Issue Closeout Review DRAFT',
                       '**DRAFT** — do not post or close issue.',
                       '## DRAFT — do not post or close issue.',
                       '⚠️ DRAFT — do not post or close issue.',
                       'DRAFT - do not post or close issue.',
                       '> DRAFT — do not post or close issue.',
                       '- DRAFT — do not post or close issue.',
                       '***DRAFT*** — do not post or close issue.',
                       '[DRAFT] — do not post or close issue.',
                       'Status — DRAFT — do not post or close issue.',
                       'DRAFT (do not post or close issue)',
                       'DRAFT / do not post or close issue',
                       'WIP — DRAFT — do not post',
                       'Unposted DRAFT — do not post or close issue.',
                       'Unfinalized DRAFT — do not post or close issue.',
                       'Unfinalized DRAFT closeout.',
                       'This closeout is a DRAFT — do not post.',
                       'This closeout is a DRAFT.',
                       'DRAFT closeout — do not post.',
                       'Draft closeout review — do not post.',
                       'This is a DRAFT closeout.',
                       'Do not post — DRAFT closeout.'):
            with self.subTest(banner=banner):
                target['body'] = banner + '\n\n' + original
                searched = w.search([snapshot], 'Keep GitHub as work ledger')
                self.assertEqual([], searched['matches'])
                traced = w.trace([snapshot], issue_url)
                issue_node = next(node for node in traced['nodes'] if node['url'] == issue_url)
                self.assertNotIn(target['html_url'], issue_node['links'])

    def test_empty_or_partial_json_closeout_shapes_are_not_indexed(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        bodies = [
            '```json\n{"issue_closeout_review":{"issue":"' + self.packet['issue']
            + '","status":"completed","decision_analysis":{}}}\n```',
            '```json\n' + json.dumps({'issue_closeout_review': {
                'issue': self.packet['issue'], 'status': 'completed',
                'decision_analysis': {
                    'decision_made': 'Keep trace',
                    'why_this_path': 'The next worker needs it.',
                    'rejected_paths': [{'path': 'Chat-only summary', 'reason': 'Not recoverable.'}],
                    'reusable_signal': {'applies_later': True, 'reason': 'Bounded recovery.'}},
                'decisions': [{'decision': 'Keep trace', 'reason': 'Recoverable trail.',
                               'evidence': []}]}}) + '\n```',
        ]
        snapshot['comments'] = [
            dict(html_url=self.packet['issue'] + f'#issuecomment-{index + 60}', body=body)
            for index, body in enumerate(bodies)
        ]
        searched = w.search([snapshot], 'Keep trace')
        self.assertEqual([], searched['matches'])
        self.assertEqual([], searched['candidates'])
        issue_node = next(node for node in w.trace([snapshot], self.packet['issue'])['nodes']
                          if node['url'] == self.packet['issue'])
        self.assertFalse(any(comment['html_url'] in issue_node['links']
                             for comment in snapshot['comments']))

    def test_duplicate_json_closeout_key_is_not_indexed(self):
        snapshot = copy.deepcopy(self.indexed_final)
        body = snapshot['comments'][0]['body']
        self.assertIn('"decision_analysis": {', body)
        snapshot['comments'][0]['body'] = body.replace(
            '"decision_analysis": {',
            '"decision_analysis": {},\n    "decision_analysis": {', 1)
        self.assertEqual([], w.search([snapshot], 'Keep GitHub')['matches'])
        issue_node = next(node for node in w.trace([snapshot], self.packet['issue'])['nodes']
                          if node['url'] == self.packet['issue'])
        self.assertNotIn(snapshot['comments'][0]['html_url'], issue_node['links'])

    def test_nonstandard_json_constant_is_not_a_checked_closeout(self):
        snapshot = copy.deepcopy(self.indexed_final)
        body = snapshot['comments'][0]['body']
        self.assertIn('"issue_closeout_review": {', body)
        snapshot['comments'][0]['body'] = body.replace(
            '"issue_closeout_review": {', '"extra": NaN, "issue_closeout_review": {', 1)
        result = w.search([snapshot], 'Keep GitHub')
        self.assertEqual([], result['matches'])
        self.assertEqual([], result['candidates'])
        issue_node = next(node for node in w.trace([snapshot], self.packet['issue'])['nodes']
                          if node['url'] == self.packet['issue'])
        self.assertNotIn(snapshot['comments'][0]['html_url'], issue_node['links'])

    def test_marker_quote_and_wrong_issue_json_do_not_create_closeout_edges(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        bodies = [
            'I object to issue_closeout_review as proof of completion.',
            '> ```yaml\n> issue_closeout_review:\n>   issue: "#1"\n>   status: completed\n> ```',
            '```json\n{"issue_closeout_review":{"issue":"https://github.com/example/asgk-synthetic/issues/999",'
            '"status":"completed","decision_analysis":{}}}\n```',
        ]
        snapshot['comments'] = [dict(html_url=self.packet['issue'] + f'#issuecomment-{n+50}', body=body)
                                for n, body in enumerate(bodies)]
        searched = w.search([snapshot], 'issue_closeout_review')
        self.assertEqual([], searched['matches'])
        self.assertEqual([], searched['candidates'])
        issue_node = next(x for x in w.trace([snapshot], self.packet['issue'])['nodes']
                          if x['url'] == self.packet['issue'])
        self.assertFalse(any(comment['html_url'] in issue_node['links'] for comment in snapshot['comments']))

    def test_open_issue_does_not_index_premature_closeout(self):
        snapshot = copy.deepcopy(self.indexed_final)
        snapshot['issue']['state'] = 'open'
        self.assertEqual([], w.search([snapshot], 'Keep GitHub as work ledger')['matches'])
        issue_node = next(x for x in w.trace([snapshot], self.packet['issue'])['nodes']
                          if x['url'] == self.packet['issue'])
        self.assertNotIn(snapshot['comments'][0]['html_url'], issue_node['links'])

    def test_open_or_draft_yaml_is_not_a_closeout_candidate(self):
        snapshot = copy.deepcopy(self.final)
        comment_url = self.packet['issue'] + '#issuecomment-71'
        snapshot['comments'] = [dict(html_url=comment_url, body=self.canonical_yaml_closeout())]
        self.assertEqual([], w.search([snapshot], 'Keep trace')['candidates'])
        snapshot['issue']['state'] = 'closed'
        snapshot['comments'][0]['body'] = '# Issue Closeout Review DRAFT\n\n' + self.canonical_yaml_closeout()
        self.assertEqual([], w.search([snapshot], 'Keep trace')['candidates'])
        self.assertEqual([], w.trace([snapshot], self.packet['issue'])['candidates'])

    def test_draft_banner_is_not_indexed_even_after_issue_closes(self):
        snapshot = copy.deepcopy(self.indexed_final)
        draft = (self.out / 'artifacts' / 'CLOSEOUT_DRAFT.md').read_text(encoding='utf-8')
        snapshot['comments'][0]['body'] = draft
        self.assertEqual([], w.search([snapshot], 'Keep GitHub as work ledger')['matches'])
        issue_node = next(x for x in w.trace([snapshot], self.packet['issue'])['nodes']
                          if x['url'] == self.packet['issue'])
        self.assertNotIn(snapshot['comments'][0]['html_url'], issue_node['links'])

    def test_cross_issue_trace_handles_cycles(self):
        result = w.trace([self.indexed_final, self.prior], self.packet['issue'])
        self.assertTrue(any(n['url'] == self.prior['issue']['html_url'] for n in result['nodes']))
        self.assertEqual(len(result['nodes']), len({n['url'] for n in result['nodes']}))

    def test_shorthand_pr_is_not_invented_as_issue(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['body'] += '\nCompared #3 with unresolved #999.\n'
        result = w.trace([snapshot], self.packet['issue'], 0)
        issue_node = result['nodes'][0]
        self.assertIn(snapshot['prs'][0]['pr']['html_url'], issue_node['links'])
        self.assertNotIn('https://github.com/example/asgk-synthetic/issues/3', issue_node['links'])
        self.assertIn('#999', issue_node['unresolved_shorthand_refs'])
        self.assertIn('#999', result['unresolved_shorthand_refs'])

    def test_unresolved_trace_is_honest(self):
        result = w.trace([self.indexed_final], self.prior['issue']['html_url'])
        self.assertEqual('warning', result['result'])
        self.assertEqual([self.prior['issue']['html_url']], result['unresolved'])
        self.assertEqual('incomplete', result['domain_result'])
        self.assertEqual(['WF_TRACE_INCOMPLETE'], [finding['code'] for finding in result['findings']])
        self.assertEqual([], w.validation_result_errors(result))

    def test_direct_workflow_results_keep_common_envelope(self):
        for result in (
            self.observe(),
            w.search([self.indexed_final], 'GitHub'),
            w.trace([self.indexed_final], self.packet['issue']),
        ):
            self.assertEqual([], w.validation_result_errors(result))

    def test_hops_bounded(self):
        self.fails('HOP_LIMIT', lambda: w.trace([self.final], self.packet['issue'], 6))

    def test_conflicting_snapshots(self):
        other = copy.deepcopy(self.indexed_final)
        other['issue']['body'] = 'Conflicting current body'
        self.fails('SNAPSHOT_CONFLICT', lambda: w.search([self.indexed_final, other], 'GitHub'))

    def test_repeated_issue_snapshots_fail_in_both_orders_even_when_body_matches(self):
        first = copy.deepcopy(self.final)
        second = copy.deepcopy(first)
        second['issue']['state'] = 'closed'
        second['comments'] = [dict(html_url=self.packet['issue'] + '#issuecomment-82',
                                   body=self.canonical_yaml_closeout())]
        for snapshots in ((first, second), (second, first), (first, copy.deepcopy(first))):
            with self.subTest(states=[snapshot['issue']['state'] for snapshot in snapshots]):
                self.fails('SNAPSHOT_CONFLICT', lambda: w.search(list(snapshots), 'Keep trace'))
                self.fails('SNAPSHOT_CONFLICT', lambda: w.trace(list(snapshots), self.packet['issue']))

    def test_repeated_pr_observations_across_issues_fail_in_both_orders(self):
        first = copy.deepcopy(self.final)
        second = copy.deepcopy(self.prior)
        second['prs'] = copy.deepcopy(first['prs'])
        second['prs'][0]['pr'].update(state='open', merged=False, merge_commit_sha=None)
        self.assertNotEqual(first['issue']['number'], second['issue']['number'])
        self.assertEqual(first['prs'][0]['pr']['html_url'], second['prs'][0]['pr']['html_url'])
        for snapshots in ((first, second), (second, first),
                          (first, dict(second, prs=copy.deepcopy(first['prs'])))):
            with self.subTest(states=[snapshot['prs'][0]['pr']['state'] for snapshot in snapshots]):
                self.fails('SNAPSHOT_CONFLICT', lambda: w.search(list(snapshots), 'GitHub'))
                self.fails('SNAPSHOT_CONFLICT', lambda: w.trace(list(snapshots), self.packet['issue']))

    def test_other_issue_can_link_to_one_selected_pr_observation(self):
        other = copy.deepcopy(self.prior)
        pr_url = self.indexed_final['prs'][0]['pr']['html_url']
        other['issue']['body'] += '\nRelated PR: ' + pr_url
        result = w.trace([self.indexed_final, other], other['issue']['html_url'])
        self.assertTrue(any(node['url'] == pr_url and node['kind'] == 'pr'
                            for node in result['nodes']))

    def test_repository_case_alias_cannot_hide_issue_pr_number_collision(self):
        first = copy.deepcopy(self.final)
        other = copy.deepcopy(self.prior)
        other['repository'] = 'Example/ASGK-Synthetic'
        other['issue'].update(number=3, html_url='https://github.com/Example/ASGK-Synthetic/issues/3')
        other['comments'] = []
        for snapshots in ((first, other), (other, first)):
            self.fails('SNAPSHOT_CONFLICT', lambda: w.search(list(snapshots), 'GitHub'))

    def test_shorthand_links_across_repository_case_alias(self):
        first = copy.deepcopy(self.final)
        other = copy.deepcopy(self.prior)
        other['repository'] = 'Example/ASGK-Synthetic'
        other['issue']['html_url'] = 'https://github.com/Example/ASGK-Synthetic/issues/2'
        other['issue']['body'] = 'Related PR #3.'
        other['comments'] = []
        result = w.trace([first, other], other['issue']['html_url'])
        issue_node = next(node for node in result['nodes'] if node['url'] == other['issue']['html_url'])
        self.assertIn(first['prs'][0]['pr']['html_url'], issue_node['links'])
        self.assertNotIn('#3', issue_node['unresolved_shorthand_refs'])

    def test_closed_issue_without_supplied_closeout_is_incomplete(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        snapshot['issue']['body'] = 'No linked decision evidence.'
        snapshot['comments'] = []
        snapshot['prs'] = []
        for comments in ([], [dict(html_url=self.packet['issue'] + '#issuecomment-83',
                                  body='Older prose-only closeout; consult the issue.')]):
            with self.subTest(comments=comments):
                snapshot['comments'] = comments
                result = w.trace([snapshot], self.packet['issue'])
                self.assertEqual('warning', result['result'])
                self.assertEqual('incomplete', result['domain_result'])
                self.assertEqual([self.packet['issue']], result['closeout_not_found'])
                self.assertEqual([], result['candidates'])
                self.assertEqual(['WF_CLOSEOUT_NOT_FOUND'],
                                 [finding['code'] for finding in result['findings']])
                self.assertEqual([], w.validation_result_errors(result))

    def test_capture_get_only(self):
        response = type('Result', (), {'returncode': 0, 'stdout': '[]'})()
        with patch.object(w.subprocess, 'run', return_value=response) as mocked:
            w.gh_get('repos/example/test/issues/1')
            command = mocked.call_args.args[0]
            self.assertEqual('GET', command[command.index('--method') + 1])
            self.assertNotIn('POST', command)

    def test_capture_failure_no_mutation_fallback(self):
        response = type('Result', (), {'returncode': 1, 'stdout': ''})()
        with patch.object(w.subprocess, 'run', return_value=response) as mocked:
            self.fails('GITHUB_UNAVAILABLE', lambda: w.gh_get('repos/example/test/issues/1'))
            self.assertEqual(1, mocked.call_count)

    def test_cli_packet_and_check(self):
        artifacts = self.out / 'artifacts'
        output = self.out / 'packet-command'
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, a.main(['packet', '--snapshot', str(artifacts / 'snapshot.json'),
                '--repo-root', str(self.root), '--actor', 'human-B', '--run', 'run-B', '--out', str(output)]))
            self.assertEqual(0, a.main(['check', '--snapshot', str(artifacts / 'snapshot.json'),
                '--packet', str(output / 'packet.json'), '--repo-root', str(self.root)]))

    def test_root_workflow_entry_full_fixture_chain(self):
        source_root = Path(__file__).resolve().parents[1]
        artifacts = self.out / 'artifacts'

        def root_cli(*args):
            completed = subprocess.run(
                [sys.executable, str(source_root / 'scripts/asgk.py'), 'workflow', *map(str, args)],
                cwd=source_root, capture_output=True, text=True, check=False,
            )
            self.assertFalse(completed.stderr, completed.stderr)
            return completed.returncode, json.loads(completed.stdout)

        packet_out = self.out / 'root-packet'
        code, result = root_cli('packet', '--snapshot', artifacts / 'snapshot.json',
            '--repo-root', self.root, '--actor', 'human-B', '--run', 'run-B',
            '--out', packet_out)
        self.assertEqual(0, code)
        self.assertEqual('pass', result['result'])
        self.assertEqual('not_checked', result['human_gate']['status'])
        self.assertTrue(result['human_gate']['reason'])
        code, result = root_cli('check', '--snapshot', artifacts / 'snapshot.json',
            '--packet', packet_out / 'packet.json', '--repo-root', self.root)
        self.assertEqual(0, code)
        self.assertEqual('pass', result['result'])

        partial = copy.deepcopy(self.report)
        partial['state'] = 'partial'
        partial['remaining'] = ['Run the required project check']
        partial_file = self.out / 'partial.json'
        partial_file.write_text(json.dumps(partial), encoding='utf-8')
        handoff_out = self.out / 'root-handoff'
        code, result = root_cli('handoff', '--snapshot', artifacts / 'snapshot.json',
            '--packet', artifacts / 'packet.json', '--repo-root', self.root,
            '--report', partial_file, '--out', handoff_out)
        self.assertEqual(1, code)
        self.assertEqual('blocked', result['result'])
        self.assertEqual(['WORK_INCOMPLETE'],
                         [finding['code'] for finding in result['findings']])
        self.assertTrue((handoff_out / 'HANDOFF_DRAFT.md').is_file())

        closeout_out = self.out / 'root-closeout'
        code, result = root_cli('closeout', '--snapshot', artifacts / 'pre-closeout-snapshot.json',
            '--packet', artifacts / 'packet.json', '--repo-root', self.root,
            '--report', artifacts / 'report.json', '--status', 'completed',
            '--out', closeout_out)
        self.assertEqual(0, code)
        self.assertEqual('pass', result['result'])
        self.assertTrue((closeout_out / 'CLOSEOUT_DRAFT.md').is_file())

        code, result = root_cli('search', '--snapshot', artifacts / 'final-snapshot.json',
            '--query', 'GitHub')
        self.assertEqual(0, code)
        self.assertEqual(1, len(result['matches']))
        code, result = root_cli('trace', '--snapshot', artifacts / 'final-snapshot.json',
            '--snapshot', artifacts / 'prior-snapshot.json',
            '--start', self.packet['issue'])
        self.assertIn(code, (0, 1))
        self.assertTrue(result['nodes'])
        self.assertIn(result['result'], ('pass', 'warning'))

    def test_root_workflow_yaml_candidate_never_exits_zero(self):
        snapshot = copy.deepcopy(self.final)
        snapshot['issue']['state'] = 'closed'
        comment_url = self.packet['issue'] + '#issuecomment-80'
        snapshot['comments'] = [dict(html_url=comment_url,
                                     body=self.canonical_yaml_closeout().replace('  issue: "#1"', '  issue: "#999"'))]
        candidate_file = self.out / 'yaml-candidate.json'
        candidate_file.write_text(json.dumps(snapshot), encoding='utf-8')
        source_root = Path(__file__).resolve().parents[1]
        for command, option, value in (
            ('search', '--query', 'Keep trace'),
            ('trace', '--start', self.packet['issue']),
        ):
            with self.subTest(command=command):
                completed = subprocess.run(
                    [sys.executable, str(source_root / 'scripts/asgk.py'), 'workflow', command,
                     '--snapshot', str(candidate_file), option, value, '--json'],
                    cwd=source_root, capture_output=True, text=True, check=False)
                self.assertEqual(1, completed.returncode)
                self.assertFalse(completed.stderr, completed.stderr)
                result = json.loads(completed.stdout)
                self.assertEqual('warning', result['result'])
                self.assertEqual('incomplete', result['domain_result'])
                self.assertEqual([comment_url], [item['url'] for item in result['candidates']])
                self.assertEqual('supplied_snapshots', result['evidence_source'])
                self.assertIn('WF_YAML_CANDIDATE_UNVERIFIED',
                              [finding['code'] for finding in result['findings']])

    def test_root_workflow_rejects_invalid_without_writing(self):
        source_root = Path(__file__).resolve().parents[1]
        artifacts = self.out / 'artifacts'
        invalid = self.out / 'rejected-card'
        def rejected(*args):
            completed = subprocess.run(
                [sys.executable, str(source_root / 'scripts/asgk.py'), 'workflow', *map(str, args)],
                cwd=source_root, capture_output=True, text=True, check=False,
            )
            self.assertEqual(1, completed.returncode)
            self.assertFalse(completed.stderr, completed.stderr)
            return json.loads(completed.stdout)

        result = rejected('card-draft', '--snapshot', artifacts / 'snapshot.json',
            '--packet', artifacts / 'packet.json', '--repo-root', self.root,
            '--out', invalid)
        self.assertEqual('CARD_SOURCE', result['findings'][0]['code'])
        self.assertFalse(invalid.exists())

        stale = copy.deepcopy(self.snapshot)
        stale['captured_at'] = '2000-01-01T00:00:00Z'
        stale_file = self.out / 'stale.json'
        stale_file.write_text(json.dumps(stale), encoding='utf-8')
        stale_output = self.out / 'stale-packet'
        result = rejected('packet', '--snapshot', stale_file, '--repo-root', self.root,
            '--actor', 'synthetic-bot-A', '--run', 'run-A', '--out', stale_output)
        self.assertEqual('STALE_SNAPSHOT', result['findings'][0]['code'])
        self.assertFalse(stale_output.exists())

        forged = copy.deepcopy(self.snapshot)
        forged['source'] = 'gh_api'
        forged_file = self.out / 'forged.json'
        forged_file.write_text(json.dumps(forged), encoding='utf-8')
        forged_output = self.out / 'forged-packet'
        result = rejected('packet', '--snapshot', forged_file, '--repo-root', self.root,
            '--actor', 'synthetic-bot-A', '--run', 'run-A', '--out', forged_output)
        self.assertEqual('REPO_IDENTITY', result['findings'][0]['code'])
        self.assertFalse(forged_output.exists())

        changed = copy.deepcopy(self.snapshot)
        changed['issue']['body'] += '\n\nNew scope objection.'
        changed_file = self.out / 'changed-issue.json'
        changed_file.write_text(json.dumps(changed), encoding='utf-8')
        result = rejected('check', '--snapshot', changed_file,
            '--packet', artifacts / 'packet.json', '--repo-root', self.root)
        self.assertEqual('STALE_PACKET', result['findings'][0]['code'])

    def test_cli_card_draft_writes_only_after_validation(self):
        snapshot, packet = self.observed_packet()
        inputs = self.out / 'card-inputs'
        inputs.mkdir()
        (inputs / 'snapshot.json').write_text(json.dumps(snapshot), encoding='utf-8')
        (inputs / 'packet.json').write_text(json.dumps(packet), encoding='utf-8')
        output = self.out / 'card-output'
        args = ['card-draft', '--snapshot', str(inputs / 'snapshot.json'),
                '--packet', str(inputs / 'packet.json'), '--repo-root', str(self.root),
                '--out', str(output)]
        with contextlib.redirect_stdout(io.StringIO()) as stream:
            self.assertEqual(0, a.main(args))
        result = json.loads(stream.getvalue())
        self.assertEqual('pass', result['result'])
        self.assertIn('actual origin or authenticity of the supplied snapshot', result['not_checked'])
        self.assertIn('supplied snapshot shape, freshness and declared non-fixture source label',
                      result['mechanically_checked'])
        metadata = a.load(output / 'CARD.json')
        body = (output / 'CARD.md').read_text(encoding='utf-8')
        self.assertEqual(metadata['body_sha256'], hashlib.sha256(body.encode()).hexdigest())
        self.assertEqual(packet['packet_id'], metadata['packet_id'])

        root_output = self.out / 'root-card-output'
        source_root = Path(__file__).resolve().parents[1]
        completed = subprocess.run(
            [sys.executable, str(source_root / 'scripts/asgk.py'), 'workflow', *args[:-1],
             str(root_output), '--json'],
            cwd=source_root, capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertFalse(completed.stderr, completed.stderr)
        root_result = json.loads(completed.stdout)
        self.assertEqual('pass', root_result['result'])
        self.assertEqual(metadata['body_sha256'], a.load(root_output / 'CARD.json')['body_sha256'])
        self.assertIn('controller-supplied facts',
                      (root_output / 'CARD.md').read_text(encoding='utf-8'))

        invalid = self.out / 'invalid-card-output'
        w.git(self.root, 'remote', 'remove', 'upstream')
        fixture_args = ['card-draft', '--snapshot', str(self.out / 'artifacts' / 'snapshot.json'),
                        '--packet', str(self.out / 'artifacts' / 'packet.json'),
                        '--repo-root', str(self.root), '--out', str(invalid)]
        with contextlib.redirect_stdout(io.StringIO()) as stream:
            self.assertEqual(1, a.main(fixture_args))
        self.assertEqual('CARD_SOURCE', json.loads(stream.getvalue())['findings'][0]['code'])
        self.assertFalse(invalid.exists())


if __name__ == '__main__':
    unittest.main()
