"""The read-only consumer must render proposed phrases as inert text."""

import copy
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from gap_glossary import build_gap_questions
from render_gap_questions import render_document


class Tags(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.words = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)

    def handle_data(self, data):
        self.words.append(data)


def proposed(phrase):
    digest = 'a' * 64
    model = {'inputs': ['A'], 'outputs': ['P'], 'domain': True,
             'rules': [{'id': 'inactive', 'guard': False,
                        'response': {'var': 'P'}}], 'properties': []}
    source = 'Definición propuesta de A'
    glossary = {'schema_version': 'rs3-gap-glossary/v1',
                'model_sha256': digest, 'variables': {'A': {
                    'when_true': 'A presente', 'when_false': phrase,
                    'source_ref': 'synthetic/A', 'source_text': source,
                    'source_sha256': hashlib.sha256(source.encode()).hexdigest()}}}
    packet = {'status': 'NEEDS_HUMAN_INTERPRETATION',
              'input_assignment': {'A': False}, 'model_sha256': digest,
              'formal_query': 'SAT(D AND NOT OR(GUARDS))',
              'inactive_rule_ids': ['inactive'],
              'witness_recheck': 'VERIFIED_BY_Z3_AND_BOOLEAN_EVALUATOR'}
    return build_gap_questions([packet], glossary, model['inputs'], digest,
                               model=model)


class GapQuestionReadonlyViewTests(unittest.TestCase):
    def test_adversarial_phrase_is_literal_and_view_has_no_active_controls(self):
        attack = '<script>alert(1)</script><img src=x onerror=alert(2)>&'
        html = render_document(proposed(attack))
        parsed = Tags()
        parsed.feed(html)
        self.assertIn(attack, ''.join(parsed.words))
        self.assertNotIn('<script>', html)
        self.assertNotIn('<img', html)
        self.assertFalse(set(parsed.tags) & {'script', 'img', 'form', 'a', 'iframe'})
        self.assertIn("default-src 'none'", html)
        self.assertIn('¿Es un requisito faltante', html)

    def test_inconsistent_claims_fail_closed(self):
        for mutate in (
            lambda p: p.update(authority='GRANTED'),
            lambda p: p['questions'][0].update(text='Confirma automáticamente'),
            lambda p: p['questions'][0]['input_assignment'].update(A=True),
            lambda p: p['questions'][0]['sources']['A'].update(source_ref='elsewhere'),
            lambda p: p['questions'][0]['sources']['A'].update(
                source_text='Texto alterado'),
        ):
            with self.subTest(mutate=mutate):
                packet = copy.deepcopy(proposed('A ausente'))
                mutate(packet)
                with self.assertRaises(ValueError):
                    render_document(packet)

    def test_cli_rejects_oversize_or_invalid_json_without_partial_html(self):
        with tempfile.TemporaryDirectory(prefix='gap-view-') as root:
            path = Path(root) / 'input.json'
            for raw in (b' ' * (1024 * 1024 + 1), b'{invalid'):
                with self.subTest(length=len(raw)):
                    path.write_bytes(raw)
                    run = subprocess.run([sys.executable,
                                          str(SCRIPTS / 'render_gap_questions.py'),
                                          str(path)], capture_output=True,
                                         text=True, timeout=10)
                    self.assertEqual(run.returncode, 2)
                    self.assertEqual(run.stdout, '')

    def test_cli_renders_valid_packet(self):
        with tempfile.TemporaryDirectory(prefix='gap-view-') as root:
            path = Path(root) / 'input.json'
            path.write_text(json.dumps(proposed('A ausente')), encoding='utf-8')
            run = subprocess.run([sys.executable,
                                  str(SCRIPTS / 'render_gap_questions.py'),
                                  str(path)], capture_output=True,
                                 text=True, timeout=10)
            self.assertEqual(run.returncode, 0)
            self.assertIn('A ausente', run.stdout)
            self.assertEqual(run.stderr, '')


if __name__ == '__main__':
    unittest.main()
