"""Check the CI's executable gate and bounded GitHub permissions."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github/workflows/quality.yml'
RUNNER = ROOT / 'ci/run_quality.sh'
README = ROOT / 'README.md'
AGENTS = ROOT / 'AGENTS.md'


class WorkflowTests(unittest.TestCase):
    def test_ci_covers_all_three_components_with_read_only_token(self):
        workflow_text = WORKFLOW.read_text(encoding='utf-8')
        doc = yaml.safe_load(workflow_text)
        events = doc.get('on', doc.get(True))  # YAML 1.1 parses `on` as boolean.
        self.assertEqual(set(events), {'push', 'pull_request'})
        self.assertEqual(doc['permissions'], {'contents': 'read'})
        self.assertNotIn('secrets.', workflow_text)
        jobs = doc['jobs']
        self.assertEqual(list(jobs), ['quality'])
        job = jobs['quality']
        self.assertEqual(job['runs-on'], 'ubuntu-24.04')
        self.assertLessEqual(job['timeout-minutes'], 5)
        self.assertTrue(any(step.get('run') == 'bash ci/run_quality.sh'
                            for step in job['steps']))
        runner = RUNNER.read_text(encoding='utf-8')
        for suite in ('supervisor/tests', 'skills/qa-inquisidor/tests',
                      'skills/requerimientos-socraticos/tests'):
            self.assertIn(suite, runner)
        self.assertIn('ci/check_rdd_record.py', runner)

    def test_public_status_matches_ci_activation(self):
        readme = README.read_text(encoding='utf-8')
        agents = AGENTS.read_text(encoding='utf-8')
        self.assertIn('CI activado', readme)
        self.assertIn('RDD-CIERRE.md', readme)
        self.assertNotIn('CI y producción permanecen diferidos', readme)
        self.assertNotIn('No se incorporan workflows de GitHub Actions.', readme)
        self.assertIn('CI activado por solicitud del propietario', agents)
        self.assertNotIn('CI permanece diferido', agents)
        self.assertNotIn('Esta autorización no habilita CI', agents)


if __name__ == '__main__':
    unittest.main()
