"""Synthetic and local checks for the non-authorizing D05 agent probe."""

import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from supervisor.rs3_d05_agent_boundary_preflight import probe_agent_boundary


class AgentBoundaryPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'authority'

    def test_equal_or_privileged_uid_fails_closed(self):
        self.root.mkdir(mode=0o700)
        for authority_uid in (os.getuid(), 0):
            result = probe_agent_boundary(self.root, authority_uid)
            self.assertEqual(result['local_status'], 'FAIL')
            self.assertEqual(result['real_authority_gate'], 'SECURITY_BOUNDARY_UNMET')
            self.assertIs(result['execution_authorized'], False)

    def test_missing_root_or_symlink_is_not_accepted(self):
        with mock.patch('supervisor.rs3_d05_agent_boundary_preflight._effective_caps',
                        return_value='ZERO'):
            missing = probe_agent_boundary(self.root, os.getuid() + 1)
        self.assertEqual(missing['local_status'], 'NOT_ASSESSED')
        self.root.mkdir(mode=0o700)
        link = Path(self.tmp.name) / 'link'
        link.symlink_to(self.root, target_is_directory=True)
        with mock.patch('supervisor.rs3_d05_agent_boundary_preflight._effective_caps',
                        return_value='ZERO'):
            linked = probe_agent_boundary(link, os.getuid() + 1)
        self.assertEqual(linked['local_status'], 'FAIL')

    def test_agent_owned_root_is_rejected_without_leaking_path(self):
        self.root.mkdir(mode=0o700)
        result = probe_agent_boundary(self.root, os.getuid() + 1)
        self.assertEqual(result['local_status'], 'FAIL')
        self.assertNotIn(str(self.root), str(result))
        self.assertEqual(result['authority_verification'], 'NOT_ESTABLISHED')

    def test_elevated_effective_uid_blocks(self):
        self.root.mkdir(mode=0o700)
        with mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.geteuid',
                        return_value=os.getuid() + 2):
            result = probe_agent_boundary(self.root, os.getuid() + 1)
        self.assertEqual(result['local_status'], 'FAIL')

    def test_synthetic_favorable_local_checks_still_do_not_authorize(self):
        self.root.mkdir(mode=0o700)
        with (mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.getuid',
                         return_value=2001),
              mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.geteuid',
                         return_value=2001),
              mock.patch('supervisor.rs3_d05_agent_boundary_preflight.Path.lstat',
                         return_value=SimpleNamespace(st_mode=stat.S_IFDIR | 0o700,
                                                      st_uid=2002)),
              mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.access',
                         return_value=False),
              mock.patch('supervisor.rs3_d05_agent_boundary_preflight._effective_caps',
                         return_value='ZERO')):
            result = probe_agent_boundary(self.root, 2002)
        self.assertEqual(result['local_status'], 'OBSERVED_LOCAL_GUARDS')
        self.assertEqual(result['real_authority_gate'], 'SECURITY_BOUNDARY_UNMET')
        self.assertIs(result['execution_authorized'], False)


if __name__ == '__main__':
    unittest.main()
