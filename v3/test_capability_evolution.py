import copy
import json
import tempfile
import unittest
from pathlib import Path

import asgk3
import capability_evolution as c


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
            self.assertIn('not a delivery question graph', result['proof_boundary'])

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
        self.assertEqual('incomplete', result['result'])

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
        self.assertEqual('incomplete', c.select(self.index, 'research', 'handoff',
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
        self.assertLess(len(json.dumps(result)), 6500)

    def test_cli_does_not_open_content_ref(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'index.json'
            path.write_text(json.dumps(self.index), encoding='utf-8')
            # The example's content_ref paths are intentionally not materialized.
            self.assertEqual(0, c.main(['check', '--index', str(path)]))

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


if __name__ == '__main__':
    unittest.main()
