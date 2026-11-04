"""A supplied glossary must not turn a formal witness into ratified meaning."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'analyze_logic.py'


def run_case(glossary_kind):
    model = {'inputs': ['A', 'B'], 'outputs': ['P'],
             'domain': {'op': 'or', 'args': [{'var': 'A'}, {'var': 'B'}]},
             'rules': [{'id': 'only_A', 'guard': {'var': 'A'},
                        'response': {'var': 'P'}}], 'properties': []}
    raw = json.dumps(model, sort_keys=True).encode()
    digest = hashlib.sha256(raw).hexdigest()
    def item(name):
        source = 'Definición documentada de ' + name
        return {'when_true': name + ' está presente',
                'when_false': name + ' está ausente',
                'source_ref': 'synthetic/' + name,
                'source_text': source,
                'source_sha256': hashlib.sha256(source.encode()).hexdigest()}
    glossary = {'schema_version': 'rs3-gap-glossary/v1', 'model_sha256': digest,
                'variables': {'A': item('A'), 'B': item('B')}}
    if glossary_kind == 'missing':
        del glossary['variables']['B']
    if glossary_kind == 'stale':
        glossary['model_sha256'] = '0' * 64
    if glossary_kind == 'source_changed':
        glossary['variables']['B']['source_text'] += ' alterada'
    if glossary_kind == 'incomplete_corrupt':
        del glossary['variables']['B']
        glossary['variables']['A']['source_text'] += ' alterada'
    with tempfile.TemporaryDirectory(prefix='gap-glossary-') as root:
        source = Path(root) / 'model.json'
        source.write_bytes(raw)
        command = [sys.executable, str(SCRIPT), str(source), '--gap-samples', '1']
        if glossary_kind != 'none':
            mapping = Path(root) / 'glossary.json'
            mapping.write_text(json.dumps(glossary), encoding='utf-8')
            command += ['--glossary', str(mapping)]
        done = subprocess.run(command, capture_output=True, text=True, timeout=15)
    return done.returncode, json.loads(done.stdout)


class GapGlossaryGroundingTests(unittest.TestCase):
    def test_complete_glossary_yields_proposed_question_with_sources(self):
        code, result = run_case('complete')
        self.assertEqual(code, 0)
        packet = result['gap_questions']
        self.assertEqual(packet['status'], 'PROPOSED_UNVERIFIED')
        self.assertEqual(packet['authority'], 'NOT_GRANTED')
        self.assertEqual(packet['source_authenticity'], 'NOT_ESTABLISHED')
        self.assertEqual(len(packet['questions']), 1)
        question = packet['questions'][0]
        self.assertEqual(question['text_origin'], 'SYSTEM_TEMPLATE')
        self.assertEqual(question['scenario_clauses_origin'],
                         'UNTRUSTED_GLOSSARY_DATA')
        self.assertEqual([(item['variable'], item['value'], item['proposed_phrase'])
                          for item in question['scenario_clauses']],
                         [('A', False, 'A está ausente'),
                          ('B', True, 'B está presente')])
        self.assertEqual(set(question['sources']), {'A', 'B'})

    def test_missing_or_stale_glossary_yields_no_question(self):
        for kind, status in (('missing', 'NEEDS_GLOSSARY'),
                             ('stale', 'STALE_GLOSSARY'),
                             ('none', 'NEEDS_GLOSSARY')):
            with self.subTest(kind=kind):
                code, result = run_case(kind)
                self.assertEqual(code, 0)
                self.assertEqual(result['gap_questions']['status'], status)
                self.assertEqual(result['gap_questions']['questions'], [])

    def test_changed_source_text_rejects_glossary(self):
        for kind in ('source_changed', 'incomplete_corrupt'):
            with self.subTest(kind=kind):
                code, result = run_case(kind)
                self.assertEqual(code, 2)
                self.assertEqual(result['error']['code'], 'INVALID_INPUT')
                self.assertNotIn('gap_questions', result)


if __name__ == '__main__':
    unittest.main()
