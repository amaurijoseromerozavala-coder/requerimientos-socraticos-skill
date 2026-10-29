"""Bounded structural checks before decoding JSON."""
import importlib.util
import json
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/json_preflight.py'
spec = importlib.util.spec_from_file_location('json_preflight', SCRIPT)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


class PreflightTests(unittest.TestCase):
    def test_depth_boundary_and_large_adversarial_input(self):
        preflight.preflight_json(b'[' * 96 + b']' * 96)
        with self.assertRaisesRegex(ValueError, 'depth'):
            preflight.preflight_json(b'[' * 97 + b']' * 97)
        with self.assertRaisesRegex(ValueError, 'depth'):
            preflight.preflight_json(b'[' * 100000 + b']' * 100000)

    def test_strings_escapes_and_multibyte(self):
        raw = json.dumps({'text': 'á } ] { [ " \\ end'}, ensure_ascii=False).encode()
        preflight.preflight_json(raw)
        self.assertEqual(json.loads(raw)['text'], 'á } ] { [ " \\ end')

    def test_malformed_structure(self):
        for raw in (b'[}', b']', b'[[', b'{]', b'"unterminated', b'"trailing\\'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                preflight.preflight_json(raw)

    def test_root_primitives_and_empty_array(self):
        for raw in (b'0', b'null', b'"text"', b'[]', b'{}'):
            with self.subTest(raw=raw):
                preflight.preflight_json(raw)

    def test_size_and_configurable_limits(self):
        preflight.preflight_json(b'[]', max_bytes=2, max_depth=1)
        with self.assertRaisesRegex(ValueError, 'bytes'):
            preflight.preflight_json(b'[] ', max_bytes=2)
        with self.assertRaisesRegex(ValueError, 'depth'):
            preflight.preflight_json(b'[[]]', max_depth=1)
        for kwargs in ({'max_bytes': 0}, {'max_depth': 0}, {'max_bytes': -1}, {'max_depth': -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                preflight.preflight_json(b'[]', **kwargs)

    def test_not_a_json_grammar_validator(self):
        raw = b'{"a": 1, "a": NaN,}'
        preflight.preflight_json(raw)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(raw)


if __name__ == '__main__':
    unittest.main()
