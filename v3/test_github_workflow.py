import contextlib
import copy
import io
import json
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

    def observe(self):
        return w.observe_work(self.snapshot, self.packet, self.report, self.root)

    def test_issue_projection_positive(self):
        self.assertEqual(self.packet, self.project())
        self.assertIn(self.packet['issue'], w.work_text(self.packet))
        self.assertNotIn('merge_allowed', w.work_text(self.packet))

    def test_missing_issue(self):
        self.snapshot['issue'] = None
        self.fails('ISSUE_REQUIRED', self.project)

    def test_wrong_repository(self):
        self.snapshot['repository'] = 'other/repo'
        self.fails('ISSUE_ID', self.project)

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
        failed['pr']['body'] = 'Rejected first approach; replacement follows.'
        self.final['prs'].insert(0, failed)
        result, text = w.closeout_draft(self.final, self.packet, self.report, self.root, 'completed')
        self.assertEqual('pass', result['result'])
        self.assertIn(failed['pr']['html_url'], text)
        self.assertIn('"merge_commit": null', text)

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
        self.assertEqual(1, len(result['matches']))
        self.assertIn('#issuecomment-', result['matches'][0]['url'])

    def test_cross_issue_trace_handles_cycles(self):
        result = w.trace([self.indexed_final, self.prior], self.packet['issue'])
        self.assertTrue(any(n['url'] == self.prior['issue']['html_url'] for n in result['nodes']))
        self.assertEqual(len(result['nodes']), len({n['url'] for n in result['nodes']}))

    def test_unresolved_trace_is_honest(self):
        result = w.trace([self.indexed_final], self.prior['issue']['html_url'])
        self.assertEqual('warning', result['result'])
        self.assertEqual([self.prior['issue']['html_url']], result['unresolved'])

    def test_hops_bounded(self):
        self.fails('HOP_LIMIT', lambda: w.trace([self.final], self.packet['issue'], 6))

    def test_conflicting_snapshots(self):
        other = copy.deepcopy(self.indexed_final)
        other['issue']['body'] = 'Conflicting current body'
        self.fails('SNAPSHOT_CONFLICT', lambda: w.search([self.indexed_final, other], 'GitHub'))

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


if __name__ == '__main__':
    unittest.main()
