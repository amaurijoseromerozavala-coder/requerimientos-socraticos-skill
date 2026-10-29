"""Controlled allocation-failure branches; no large data or host pressure."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import logic_engine


class LogicWorkerMemoryTests(unittest.TestCase):
    def test_observed_memory_error_returns_inconclusive_without_results(self):
        with patch.object(sys, 'argv', ['logic_engine.py', 'unused.json']), \
                patch.object(logic_engine, 'read_regular', side_effect=MemoryError), \
                patch.object(os, 'write') as write:
            code = logic_engine.main()
        self.assertEqual(code, 3)
        result = json.loads(write.call_args.args[1])
        self.assertEqual(result['status'], 'INCONCLUSIVE')
        self.assertEqual(result['error']['code'], 'MEMORY_BUDGET_EXCEEDED')
        self.assertNotIn('queries', result)
        self.assertNotIn('table', result)
        self.assertNotIn('coverage', result)

    def test_non_memory_input_failure_retains_invalid_input(self):
        output = io.StringIO()
        with patch.object(sys, 'argv', ['logic_engine.py', 'unused.json']), \
                patch.object(logic_engine, 'read_regular', side_effect=ValueError('FILE_SIZE_LIMIT')), \
                patch.object(os, 'write') as write, contextlib.redirect_stdout(output):
            code = logic_engine.main()
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())['error']['code'], 'INVALID_INPUT')
        write.assert_not_called()


if __name__ == '__main__':
    unittest.main()
