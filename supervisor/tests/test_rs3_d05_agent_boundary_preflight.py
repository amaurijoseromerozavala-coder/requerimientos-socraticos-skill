"""Synthetic and local checks for the non-authorizing D05 agent probe."""

import os
import io
import json
from pathlib import Path
import socket
import stat
import tempfile
from contextlib import redirect_stdout
from types import SimpleNamespace
import unittest
from unittest import mock

from supervisor.rs3_d05_agent_boundary_preflight import (
    _other_windows_mount_write, main, observe_agent_host_exposure,
    probe_agent_boundary,
)


class AgentBoundaryPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'authority'
        patcher = mock.patch(
            'supervisor.rs3_d05_agent_boundary_preflight.observe_agent_host_exposure',
            return_value={'checks': {'docker_socket': 'NOT_ASSESSED',
                                     'wsl_interop': 'NOT_ASSESSED',
                                     'windows_mount_write': 'NOT_ASSESSED'},
                          'host_status': 'NOT_ASSESSED',
                          'privilege_escalation': 'NOT_ASSESSED',
                          'windows_host_control': 'NOT_ASSESSED'})
        patcher.start()
        self.addCleanup(patcher.stop)

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

    def test_observed_host_exposure_blocks_local_profile(self):
        self.root.mkdir(mode=0o700)
        with mock.patch(
            'supervisor.rs3_d05_agent_boundary_preflight.observe_agent_host_exposure',
            return_value={'checks': {'docker_socket': 'EXPOSED'},
                          'host_status': 'EXPOSURE_OBSERVED',
                          'privilege_escalation': 'DOCKER_SOCKET_WRITE_PERMISSION_OBSERVED',
                          'windows_host_control': 'NOT_ASSESSED'}):
            result = probe_agent_boundary(self.root, os.getuid() + 1)
        self.assertEqual(result['local_status'], 'FAIL')
        self.assertEqual(result['host_exposure']['host_status'],
                         'EXPOSURE_OBSERVED')
        self.assertIs(result['execution_authorized'], False)


class HostExposureTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch(
            'supervisor.rs3_d05_agent_boundary_preflight._other_windows_mount_write',
            return_value='NOT_ASSESSED')
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_accessible_docker_socket_and_enabled_interop_are_exposures(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docker = root / 'docker.sock'
            interop = root / 'WSLInterop'
            interop.write_text('enabled\ninterpreter /init\n')
            with socket.socket(socket.AF_UNIX) as sock:
                sock.bind(str(docker))
                with (mock.patch('supervisor.rs3_d05_agent_boundary_preflight._is_windows_mount',
                                 return_value=True),
                      mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.access',
                                 return_value=True)):
                    result = observe_agent_host_exposure(
                        docker_socket=docker, interop_path=interop,
                        windows_mount=root)
            self.assertEqual(result['checks']['docker_socket'], 'EXPOSED')
            self.assertEqual(result['checks']['wsl_interop'], 'EXPOSED')
            self.assertEqual(result['checks']['windows_mount_write'], 'EXPOSED')
            self.assertEqual(result['checks']['other_windows_mount_write'],
                             'NOT_ASSESSED')
            self.assertEqual(result['host_status'], 'EXPOSURE_OBSERVED')
            self.assertIs(result['execution_authorized'], False)

    def test_missing_signals_do_not_prove_isolation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with (mock.patch('supervisor.rs3_d05_agent_boundary_preflight._effective_caps',
                             return_value='ZERO'),
                  mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.getuid',
                             return_value=1001),
                  mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.geteuid',
                             return_value=1001)):
                result = observe_agent_host_exposure(
                    docker_socket=root / 'missing.sock',
                    interop_path=root / 'missing-interop', windows_mount=root)
            self.assertEqual(result['host_status'], 'NOT_ASSESSED')
            self.assertNotIn('PASS', str(result))
            self.assertIs(result['execution_authorized'], False)

    def test_regular_file_or_non_windows_mount_is_not_exposure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docker = root / 'docker.sock'
            docker.write_text('ordinary file')
            interop = root / 'WSLInterop'
            interop.write_text('disabled\n')
            with (mock.patch('supervisor.rs3_d05_agent_boundary_preflight._effective_caps',
                             return_value='ZERO'),
                  mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.getuid',
                             return_value=1001),
                  mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.geteuid',
                             return_value=1001),
                  mock.patch('supervisor.rs3_d05_agent_boundary_preflight._is_windows_mount',
                             return_value=False),
                  mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.access',
                             return_value=True)):
                result = observe_agent_host_exposure(
                    docker_socket=docker, interop_path=interop,
                    windows_mount=root)
            self.assertEqual(result['checks']['docker_socket'], 'NOT_ASSESSED')
            self.assertEqual(result['checks']['wsl_interop'], 'DISABLED_OBSERVED')
            self.assertEqual(result['checks']['windows_mount_write'], 'NOT_ASSESSED')
            self.assertNotEqual(result['host_status'], 'EXPOSURE_OBSERVED')

    def test_nonzero_effective_capabilities_are_exposure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with mock.patch('supervisor.rs3_d05_agent_boundary_preflight._effective_caps',
                            return_value='NONZERO'):
                result = observe_agent_host_exposure(
                    docker_socket=root / 'missing.sock',
                    interop_path=root / 'missing-interop', windows_mount=root)
        self.assertEqual(result['host_status'], 'EXPOSURE_OBSERVED')
        self.assertEqual(result['privilege_escalation'], 'ELEVATED_PROCESS_OBSERVED')
        self.assertIs(result['execution_authorized'], False)

    def test_other_windows_mount_exposure_propagates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            interop = root / 'WSLInterop'
            interop.write_text('disabled\n')
            with mock.patch(
                'supervisor.rs3_d05_agent_boundary_preflight._other_windows_mount_write',
                return_value='EXPOSED'):
                result = observe_agent_host_exposure(
                    docker_socket=root / 'missing.sock', interop_path=interop,
                    windows_mount=root)
        self.assertEqual(result['host_status'], 'EXPOSURE_OBSERVED')
        self.assertEqual(result['windows_host_control'],
                         'WINDOWS_MOUNT_WRITE_OBSERVED')
        self.assertIs(result['execution_authorized'], False)


    def test_other_drive_is_detected_without_default_drive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mountpoint = root / 'd drive'
            mountpoint.mkdir()
            inventory = root / 'mountinfo'
            encoded = str(mountpoint).replace(' ', r'\040')
            inventory.write_text(
                f'101 80 0:33 / {encoded} rw - 9p D: rw,aname=drvfs\n')
            with mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.access',
                            side_effect=lambda path, mode: path == mountpoint and mode == os.W_OK):
                result = _other_windows_mount_write(inventory, excluded=Path('/mnt/c'))
        self.assertEqual(result, 'EXPOSED')

    def test_non_windows_mount_and_oversized_inventory_do_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory = root / 'mountinfo'
            inventory.write_text(
                f'101 80 0:33 / {root} rw - ext4 drvfs rw\n'
                f'102 80 0:34 / {root} rw - 9p D: rw,aname=other\n')
            with mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.access',
                            return_value=True):
                self.assertEqual(_other_windows_mount_write(inventory), 'NOT_ASSESSED')
            inventory.write_bytes(b'x' * (1024 * 1024 + 1))
            self.assertEqual(_other_windows_mount_write(inventory), 'NOT_ASSESSED')

    def test_write_only_socket_permission_remains_exposed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docker = root / 'docker.sock'
            with socket.socket(socket.AF_UNIX) as sock:
                sock.bind(str(docker))
                def write_only(path, mode):
                    return path == docker and mode == os.W_OK
                with mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.access',
                                side_effect=write_only):
                    result = observe_agent_host_exposure(
                        docker_socket=docker, interop_path=root / 'missing',
                        windows_mount=root)
            self.assertEqual(result['checks']['docker_socket'], 'EXPOSED')
            self.assertEqual(result['host_status'], 'EXPOSURE_OBSERVED')

    def test_writeable_windows_mount_is_reflected_in_host_control(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            interop = root / 'WSLInterop'
            interop.write_text('disabled\n')
            with (mock.patch('supervisor.rs3_d05_agent_boundary_preflight._is_windows_mount',
                             return_value=True),
                  mock.patch('supervisor.rs3_d05_agent_boundary_preflight.os.access',
                             return_value=True)):
                result = observe_agent_host_exposure(
                    docker_socket=root / 'missing.sock', interop_path=interop,
                    windows_mount=root)
            self.assertEqual(result['checks']['windows_mount_write'], 'EXPOSED')
            self.assertEqual(result['windows_host_control'],
                             'WINDOWS_MOUNT_WRITE_OBSERVED')

    def test_agent_only_cli_requires_no_guardian(self):
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(['--agent-only'])
        result = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(result['schema'], 'rs3-d05-agent-host-exposure/v1')
        self.assertEqual(result['authority_verification'], 'NOT_ESTABLISHED')
        self.assertIs(result['execution_authorized'], False)


if __name__ == '__main__':
    unittest.main()
