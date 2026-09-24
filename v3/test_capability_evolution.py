import copy
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import asgk3
import capability_evolution as c
from asgk_lib.validation_result import validation_result_errors


FIXTURE = Path(__file__).parent / 'examples' / 'capability_index.json'
LIVE_LESSON_INDEX = Path(__file__).parent / 'capabilities' / 'index.json'


class CapabilityIndexTests(unittest.TestCase):
    def setUp(self):
        self.index = asgk3.load(FIXTURE)

    def fails(self, code, callback):
        with self.assertRaises(asgk3.Invalid) as error:
            callback()
        self.assertEqual(code, error.exception.finding['code'])

    def test_three_domain_example_is_only_metadata(self):
        self.assertEqual(3, len(c.validate_index(self.index)['records']))
        self.assertEqual('capability_catalog', self.index['purpose'])
        for domain in ('research', 'video', 'translation'):
            result = c.select(self.index, domain, 'handoff')
            self.assertEqual('capability_catalog', result['projection'])
            self.assertEqual(1, len(result['pointers']))
            self.assertNotIn('applies_when', result['pointers'][0])
            self.assertIn('current task authority', result['not_checked'])
            self.assertIn('delivery question graph', result['not_checked'])
            self.assertIn('per-work question completion', result['not_checked'])
            self.assertIn('not applicability recommendations', result['proof_boundary'])
            self.assertEqual([], validation_result_errors(result))

    def test_delivery_question_graph_cannot_masquerade_as_catalog(self):
        self.index['purpose'] = 'delivery_question_graph'
        self.fails('INDEX_PURPOSE', lambda: c.validate_index(self.index))

    def test_synthetic_cases_do_not_claim_real_evidence(self):
        self.assertTrue(all(not item['evidence_refs'] for item in self.index['records']))

    def test_verified_claim_needs_an_evidence_pointer(self):
        self.index['records'][0]['state'] = 'verified'
        self.fails('EVIDENCE_PROVENANCE', lambda: c.validate_index(self.index))

    def test_observation_is_not_mislabeled_as_promoted(self):
        result = c.select(self.index, 'research', 'handoff')
        self.assertEqual('observed', result['pointers'][0]['state'])
        self.assertIsNone(result['pointers'][0]['decision_ref'])

    def test_no_match_is_incomplete_not_false_success(self):
        result = c.select(self.index, 'research', 'unfindable-needle')
        self.assertEqual('warning', result['result'])
        self.assertEqual('incomplete', result['domain_result'])
        self.assertEqual('CATALOG_NO_MATCH', result['findings'][0]['code'])
        self.assertEqual([], validation_result_errors(result))

    def test_browse_reveals_only_one_branch_at_a_time(self):
        root = c.browse(self.index, 'research')
        self.assertEqual([{'branch': ['source-context'], 'record_count': 1}], root['children'])
        self.assertEqual([], root['pointers'])
        second = c.browse(self.index, 'research', ['source-context'])
        self.assertEqual(['source-context', 'long-discussion'], second['children'][0]['branch'])
        leaf = c.browse(self.index, 'research', ['source-context', 'long-discussion'])
        self.assertEqual(1, len(leaf['pointers']))
        self.assertEqual([], leaf['children'])

    def test_branch_filters_search_without_loading_other_topics(self):
        self.assertEqual('warning', c.select(self.index, 'research', 'handoff',
                                            branch=['other-topic'])['result'])

    def test_rejected_and_superseded_not_default_instructions(self):
        for state in ('rejected', 'superseded'):
            item = copy.deepcopy(self.index['records'][0])
            item['id'] = 'retired-' + state
            item['state'] = state
            self.index['records'].append(item)
        result = c.select(self.index, 'research', 'handoff')
        self.assertEqual(1, result['total_matches'])

    def test_promoted_record_needs_decision_and_version(self):
        self.index['records'][0]['state'] = 'promoted'
        self.fails('PROMOTION_PROVENANCE', lambda: c.validate_index(self.index))

    def test_duplicate_and_broken_supersession_fail(self):
        duplicate = copy.deepcopy(self.index['records'][0])
        self.index['records'].append(duplicate)
        self.fails('DUPLICATE_ID', lambda: c.validate_index(self.index))
        self.index['records'].pop()
        self.index['records'][0]['supersedes'] = ['missing-record']
        self.fails('SUPERSESSION_REF', lambda: c.validate_index(self.index))

    def test_cross_index_supersession_uses_durable_link(self):
        self.index['records'][0]['supersedes'] = [
            'https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/359']
        self.assertEqual(3, len(c.validate_index(self.index)['records']))

    def test_same_actor_review_is_rejected_without_false_independence_claim(self):
        same = c.review_separation('researcher-bot', 'researcher-bot')
        self.assertEqual('blocked', same['result'])
        self.assertEqual('same_actor_self_review', same['finding'])
        renamed = c.review_separation('researcher-bot', 'reviewer-profile')
        self.assertEqual('warning', renamed['result'])
        self.assertIn('actor identity', renamed['not_checked'])

    def test_large_ledger_returns_bounded_pointers_not_bodies(self):
        template = self.index['records'][0]
        self.index['records'] = []
        for number in range(500):
            item = copy.deepcopy(template)
            item['id'] = f'lesson-{number:04d}'
            item['summary'] = f'Handoff context example {number}'
            item['content_ref'] = f'lessons/example-{number:04d}.md'
            self.index['records'].append(item)
        result = c.select(self.index, 'research', 'handoff', limit=7)
        self.assertEqual(500, result['total_matches'])
        self.assertEqual(7, len(result['pointers']))
        self.assertEqual(493, result['omitted'])
        self.assertEqual('warning', result['result'])
        self.assertEqual('incomplete', result['domain_result'])
        self.assertEqual('CATALOG_RESULTS_OMITTED', result['findings'][0]['code'])
        self.assertLess(len(json.dumps(result)), 6500)

    def test_branch_limit_is_partial_not_complete(self):
        for number in range(3):
            item = copy.deepcopy(self.index['records'][0])
            item['id'] = f'extra-{number}'
            item['tree_path'] = [f'extra-{number}']
            self.index['records'].append(item)
        result = c.browse(self.index, 'research', limit=2)
        self.assertEqual('warning', result['result'])
        self.assertEqual('incomplete', result['domain_result'])
        self.assertEqual('CATALOG_RESULTS_OMITTED', result['findings'][0]['code'])
        self.assertEqual(2, len(result['children']))

    def test_cli_does_not_open_content_ref(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'index.json'
            path.write_text(json.dumps(self.index), encoding='utf-8')
            # The example's content_ref paths are intentionally not materialized.
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(0, c.main(['check', '--index', str(path)]))
            result = json.loads(output.getvalue())
            self.assertIn('reference syntax', result['mechanically_checked'])
            self.assertNotIn('local references', result['mechanically_checked'])
            self.assertIn('content_ref file existence', result['not_checked'])
            for projection in (c.browse(self.index, 'research'), c.select(self.index, 'research', 'handoff')):
                self.assertIn('content_ref file existence', projection['not_checked'])

    def test_first_live_lesson_is_only_a_bounded_observed_pointer(self):
        catalog = asgk3.load(LIVE_LESSON_INDEX)
        self.assertEqual(1, len(c.validate_index(catalog)['records']))
        item = catalog['records'][0]
        self.assertEqual('github-nondefault-base-closeout-368', item['id'])
        self.assertEqual('observed', item['state'])
        self.assertEqual('v3/lessons/github-nondefault-base-closeout.md', item['content_ref'])
        self.assertIsNone(item['decision_ref'])
        self.assertIsNone(item['capability_version'])
        root = c.browse(catalog, 'governance')
        self.assertEqual([], root['pointers'])
        self.assertEqual([{'branch': ['github'], 'record_count': 1}], root['children'])
        leaf = c.browse(catalog, 'governance', ['github', 'nondefault-base', 'closeout'])
        self.assertEqual([item['id']], [pointer['id'] for pointer in leaf['pointers']])
        result = c.select(catalog, 'governance', 'closeout', branch=['github'])
        self.assertEqual([item['id']], [pointer['id'] for pointer in result['pointers']])
        self.assertNotIn('applies_when', result['pointers'][0])
        self.assertIn('record content', result['not_checked'])

    def test_first_live_lesson_cannot_claim_promotion_without_provenance(self):
        catalog = asgk3.load(LIVE_LESSON_INDEX)
        catalog['records'][0]['state'] = 'promoted'
        self.fails('PROMOTION_PROVENANCE', lambda: c.validate_index(catalog))

    def test_negative_applicability_text_is_not_a_recommendation(self):
        self.assertIn('verified', self.index['records'][0]['does_not_apply_when'])
        result = c.select(self.index, 'research', 'verified')
        self.assertEqual('pass', result['result'])
        self.assertIn('negative applicability phrases', result['proof_boundary'])
        self.assertNotIn('recommendation', result['pointers'][0])

    def test_oversized_pointer_metadata_fails_before_output(self):
        item = self.index['records'][0]
        for field, value in (
            ('content_ref', 'x' * 257),
            ('source_ref', 'https://github.com/example/repo/issues/' + '1' * 513),
            ('capability_version', 'v' * 65),
        ):
            original = item[field]
            item[field] = value
            with self.subTest(field=field):
                self.fails('DURABLE_URL' if field == 'source_ref' else 'METADATA_LENGTH'
                           if field == 'content_ref' else 'CAPABILITY_VERSION',
                           lambda: c.validate_index(self.index))
            item[field] = original

    def test_query_length_is_bounded(self):
        self.fails('QUERY_LENGTH', lambda: c.select(self.index, 'research', 'x' * 321))

    def test_observed_version_and_active_supersession_fail(self):
        item = self.index['records'][0]
        item['capability_version'] = 'v1'
        self.fails('STATE_PROVENANCE', lambda: c.validate_index(self.index))
        item['capability_version'] = None
        other = copy.deepcopy(item)
        other['id'] = 'another-active'
        other['supersedes'] = [item['id']]
        self.index['records'].append(other)
        self.fails('ACTIVE_SUPERSESSION', lambda: c.validate_index(self.index))

    def test_duplicate_json_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'index.json'
            path.write_text('{"version":1,"version":1}', encoding='utf-8')
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(1, c.main(['check', '--index', str(path)]))
            result = json.loads(output.getvalue())
            self.assertEqual('fail', result['result'])
            self.assertEqual('DUPLICATE_KEY', result['findings'][0]['code'])
            self.assertEqual([], validation_result_errors(result))

    def test_deep_json_fails_in_common_envelope_with_wrapper_parity(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'index.json'
            path.write_text('[' * 2000 + ']' * 2000, encoding='utf-8')
            commands = (
                [sys.executable, str(root / 'scripts/asgk.py'), 'catalog', 'check'],
                [sys.executable, str(root / 'v3/capability_evolution.py'), 'check'],
            )
            outputs = []
            for command in commands:
                completed = subprocess.run([*command, '--index', str(path), '--json'],
                                           cwd=root, capture_output=True, text=True, check=False)
                self.assertEqual(1, completed.returncode)
                self.assertNotIn('Traceback', completed.stderr)
                result = json.loads(completed.stdout)
                self.assertEqual('fail', result['result'])
                self.assertEqual('INDEX_DEPTH', result['findings'][0]['code'])
                self.assertEqual('index', result['findings'][0]['field'])
                self.assertEqual(['index JSON nesting depth limit'], result['mechanically_checked'])
                self.assertEqual('Index JSON nesting exceeds the supported depth.',
                                 result['findings'][0]['reason'])
                self.assertEqual([], validation_result_errors(result))
                outputs.append(completed.stdout)
            self.assertEqual(outputs[0], outputs[1])

    def test_depth_limit_is_independent_of_json_parser_version(self):
        nested = 0
        for _ in range(c.MAX_INDEX_DEPTH + 1):
            nested = [nested]
        self.fails('INDEX_DEPTH', lambda: c.validate_index(nested))
        output = io.StringIO()
        with mock.patch('asgk_lib.capability_evolution.load', return_value=nested):
            with contextlib.redirect_stdout(output):
                self.assertEqual(1, c.main(['check', '--index', 'synthetic-index.json']))
        result = json.loads(output.getvalue())
        self.assertEqual('INDEX_DEPTH', result['findings'][0]['code'])
        self.assertEqual('Index JSON nesting exceeds the supported depth.',
                         result['findings'][0]['reason'])
        self.assertEqual(['index JSON nesting depth limit'], result['mechanically_checked'])
        self.assertEqual([], validation_result_errors(result))

    def test_max_length_pointer_output_is_bounded(self):
        template = self.index['records'][0]
        template['title'] = 'T' * 120
        template['summary'] = 'S' * 320
        template['content_ref'] = 'p/' + 'x' * 254
        template['source_ref'] = 'https://github.com/a/b/issues/' + '1' * 460
        self.index['records'] = []
        for number in range(100):
            item = copy.deepcopy(template)
            item['id'] = f'max-{number}'
            self.index['records'].append(item)
        result = c.select(self.index, 'research', 'T', limit=20)
        self.assertEqual('warning', result['result'])
        self.assertEqual(80, result['omitted'])
        self.assertLess(len(json.dumps(result)), 65000)
        self.assertEqual([], validation_result_errors(result))


if __name__ == '__main__':
    unittest.main()
