import contextlib
import copy
import io
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import asgk3 as a


class PrototypeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / 'demo'
        a.demo(self.out)
        self.source = a.load(self.out / 'input.json')
        self.packet = a.load(self.out / 'packet.json')
        self.report = a.load(self.out / 'report.json')
        self.root = self.out / 'workspace'

    def failcode(self, code, fn):
        with self.assertRaises(a.Invalid) as caught:
            fn()
        self.assertEqual(code, caught.exception.finding['code'])

    def verify(self):
        return a.verify_report(self.source, self.packet, self.report, self.root)

    def test_positive_demo(self):
        self.assertEqual('ready_for_review', self.verify()['handoff_state'])
        self.assertTrue((self.out / 'review/CLOSEOUT.md').is_file())

    def test_deterministic(self):
        self.assertEqual(self.packet, a.compile_packet(copy.deepcopy(self.source)))

    def test_unknown_key(self):
        self.source['auto_approve'] = True
        self.failcode('SHAPE', lambda: a.compile_packet(self.source))

    def test_missing_key(self):
        del self.source['non_goals']
        self.failcode('SHAPE', lambda: a.compile_packet(self.source))

    def test_expired(self):
        self.failcode('EXPIRED', lambda: a.compile_packet(self.source, datetime(2099, 1, 1, tzinfo=timezone.utc)))

    def test_not_yet_valid(self):
        self.failcode('EXPIRED', lambda: a.compile_packet(self.source, datetime(2000, 1, 1, tzinfo=timezone.utc)))

    def test_revoked(self):
        self.source['authority']['revoked'] = True
        self.failcode('REVOKED', lambda: a.compile_packet(self.source))

    def test_fake_revoked_boolean(self):
        self.source['authority']['revoked'] = 'false'
        self.failcode('SHAPE', lambda: a.compile_packet(self.source))

    def test_each_scope_ceiling(self):
        for layer in ('role', 'repo', 'environment'):
            changed = copy.deepcopy(self.source)
            changed['ceilings'][layer]['write'] = []
            with self.subTest(layer=layer):
                self.failcode('SCOPE_DENIED', lambda: a.compile_packet(changed))

    def test_tool_scope(self):
        self.source['request']['tools'] = ['publish']
        self.failcode('SCOPE_DENIED', lambda: a.compile_packet(self.source))

    def test_inplace_edit_has_explicit_limit(self):
        self.source['request']['write'].append('brief.txt')
        self.failcode('INPLACE_UNSUPPORTED', lambda: a.compile_packet(self.source))

    def test_forbidden_overrides_all(self):
        self.source['forbidden_paths'].append('answer.txt')
        self.failcode('FORBIDDEN', lambda: a.compile_packet(self.source))

    def test_bad_paths(self):
        for value in ('../secret', '/etc/passwd', 'a/../b', 'a//b', './a', 'a\\b', 'a/*', 'a\nX', 'C:/x'):
            with self.subTest(value=value):
                self.failcode('PATH', lambda: a.path_name(value, 'path'))

    def test_context_scope(self):
        self.source['context'].append(dict(path='extra.txt', reason='Unneeded', sha256='0' * 64))
        self.failcode('CONTEXT_SCOPE', lambda: a.compile_packet(self.source))

    def test_actor_change_invalidates(self):
        self.source['actor_id'] = 'receiver-B'
        self.failcode('STALE_PACKET', lambda: a.check_packet(self.source, self.packet))
        self.assertNotEqual(self.packet['packet_id'], a.compile_packet(self.source)['packet_id'])

    def test_rehashed_forgery(self):
        self.packet['effective_scope']['write'] = ['secrets.txt']
        self.packet['packet_id'] = a.digest({k: v for k, v in self.packet.items() if k != 'packet_id'})
        self.failcode('STALE_PACKET', lambda: a.check_packet(self.source, self.packet))

    def test_report_wrong_run(self):
        self.report['run_id'] = 'other'
        self.failcode('REPORT_BINDING', self.verify)

    def test_altered_file(self):
        (self.root / 'answer.txt').write_text('tampered', encoding='utf-8')
        self.failcode('EVIDENCE_HASH', self.verify)

    def test_changed_read_even_with_updated_receipt(self):
        (self.root / 'brief.txt').write_text('new brief', encoding='utf-8')
        self.report['receipts'][0]['sha256'] = a.file_hash(self.root, 'brief.txt')
        self.failcode('CONTEXT_HASH', self.verify)

    def test_symlink_file(self):
        (self.root / 'answer.txt').unlink()
        (self.root / 'answer.txt').symlink_to(self.root / 'brief.txt')
        self.failcode('SYMLINK', self.verify)

    def test_symlink_directory(self):
        (self.root / 'linked').symlink_to(self.root, target_is_directory=True)
        self.failcode('SYMLINK', lambda: a.file_hash(self.root, 'linked/brief.txt'))

    def test_missing_receipt(self):
        self.report['receipts'].pop()
        self.failcode('MISSING_RECEIPT', self.verify)

    def test_receipt_outside_scope(self):
        self.report['receipts'].append(dict(path='secrets.txt', sha256='0' * 64))
        self.failcode('EVIDENCE_SCOPE', self.verify)

    def test_duplicate_receipt(self):
        self.report['receipts'].append(self.report['receipts'][0])
        self.failcode('DUPLICATE', self.verify)

    def test_fake_status(self):
        self.report['validations'][0]['status'] = 'approved'
        self.failcode('STATUS', self.verify)

    def test_pass_without_evidence(self):
        self.report['validations'][0]['evidence'] = []
        self.failcode('LIST', self.verify)

    def test_validation_set(self):
        self.report['validations'] = []
        self.failcode('VALIDATION_SET', self.verify)

    def test_nonpass_blocks(self):
        for value in ('fail', 'blocked', 'not_run'):
            self.report['validations'][0]['status'] = value
            self.assertEqual('blocked', self.verify()['handoff_state'])

    def test_gaps_block(self):
        self.report['known_gaps'] = ['Independent receiver has not reviewed output']
        self.assertEqual('blocked', self.verify()['handoff_state'])

    def test_missing_decision(self):
        self.report['decisions'] = []
        self.failcode('DECISIONS', self.verify)

    def test_decision_cycle(self):
        self.report['decisions'][0]['parent'] = 'D1'
        self.failcode('DECISION_PARENT', self.verify)

    def test_valid_decision_branch(self):
        child = dict(self.report['decisions'][0], id='D2', parent='D1', choice='Ask a human to test')
        self.report['decisions'].append(child)
        self.assertEqual('pass', self.verify()['result'])

    def test_duplicate_json_keys(self):
        path = Path(self.temp.name) / 'duplicate.json'
        path.write_text('{"version":3,"version":2}', encoding='utf-8')
        self.failcode('DUPLICATE_KEY', lambda: a.load(path))

    def test_output_no_overwrite(self):
        self.failcode('OUTPUT_EXISTS', lambda: a.demo(self.out))

    def test_readonly_scope(self):
        self.source['request']['write'] = []
        self.packet = a.compile_packet(self.source)
        self.report['packet_id'] = self.packet['packet_id']
        self.report['receipts'] = self.report['receipts'][:1]
        self.report['validations'][0]['evidence'] = ['brief.txt']
        self.report['decisions'][0]['evidence'] = ['brief.txt']
        self.assertEqual('pass', self.verify()['result'])

    def test_cli_all_commands(self):
        base = ['--input', str(self.out / 'input.json')]
        bound = base + ['--packet', str(self.out / 'packet.json')]
        reported = bound + ['--report', str(self.out / 'report.json'), '--repo-root', str(self.root)]
        commands = [['compile'] + base + ['--out', str(self.out / 'compiled')],
                    ['check'] + bound, ['verify'] + reported,
                    ['handoff'] + reported + ['--out', str(self.out / 'handoff')],
                    ['closeout'] + reported + ['--out', str(self.out / 'closeout')]]
        for args in commands:
            with self.subTest(command=args[0]), contextlib.redirect_stdout(io.StringIO()) as stream:
                self.assertEqual(0, a.main(args))
                self.assertEqual('pass', json.loads(stream.getvalue())['result'])

    def test_cli_blocked_exit_two(self):
        self.report['validations'][0]['status'] = 'not_run'
        (self.out / 'report.json').write_text(json.dumps(self.report), encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(2, a.main(['verify', '--input', str(self.out / 'input.json'),
                '--packet', str(self.out / 'packet.json'), '--report', str(self.out / 'report.json'),
                '--repo-root', str(self.root)]))

    def test_cli_malformed_failure(self):
        path = Path(self.temp.name) / 'bad.json'
        path.write_text('[]', encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()) as stream:
            self.assertEqual(1, a.main(['compile', '--input', str(path), '--out', str(self.out / 'bad')]))
            self.assertEqual('SHAPE', json.loads(stream.getvalue())['findings'][0]['code'])


if __name__ == '__main__':
    unittest.main()
