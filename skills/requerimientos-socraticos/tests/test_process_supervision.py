"""Small, owned fixtures for bounded full-duplex process supervision."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'analyze_logic.py'
SUPERVISION = SCRIPT.with_name('process_supervision.py')


def load():
    spec = importlib.util.spec_from_file_location('supervised_input_fixture', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_supervision():
    spec = importlib.util.spec_from_file_location('memory_supervision_fixture', SUPERVISION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(os.name == 'posix', 'POSIX supervision adapter')
class ProcessSupervisionTests(unittest.TestCase):
    def test_input_and_output_progress_without_pipe_deadlock(self):
        payload = bytes(range(256)) * 32
        code = ('import os,sys;os.write(1,b"o"*8192);os.write(2,b"e"*8192);'
                'data=sys.stdin.buffer.read();sys.stdout.buffer.write(data)')
        result = load().run_supervised([sys.executable, '-c', code], 2, input_data=payload)
        self.assertEqual(result['returncode'], 0)
        self.assertEqual(result['stdout_bytes'], b'o' * 8192 + payload)
        self.assertEqual(result['stderr_bytes'], b'e' * 8192)
        self.assertFalse(result['output_limit'])

    def test_stdin_write_obeys_total_deadline(self):
        started = time.monotonic()
        result = load().run_supervised(
            [sys.executable, '-c', 'import time;time.sleep(5)'], .12,
            input_data=b'x' * 65536)
        self.assertTrue(result['timed_out'])
        self.assertLess(time.monotonic() - started, 1.8)
        with self.assertRaises(ChildProcessError):
            os.waitpid(result['pid'], os.WNOHANG)

    def test_each_output_stream_is_bounded_and_worker_reaped(self):
        for fd, field in [(1, 'stdout_bytes'), (2, 'stderr_bytes')]:
            with self.subTest(fd=fd):
                result = load().run_supervised(
                    [sys.executable, '-c', f'import os,time;os.write({fd},b"x"*4096);time.sleep(5)'],
                    2, output_limit_bytes=1024)
                self.assertTrue(result['output_limit'])
                self.assertEqual(result['status'], 'OUTPUT_LIMIT')
                self.assertEqual(result[field], b'x' * 1024)
                self.assertLess(result['elapsed_seconds'], 1.8)
                with self.assertRaises(ChildProcessError):
                    os.waitpid(result['pid'], os.WNOHANG)

    def test_exact_output_limit_and_empty_input_succeed(self):
        result = load().run_supervised(
            [sys.executable, '-c', 'import sys;assert sys.stdin.buffer.read()==b"";sys.stdout.write("x"*1024)'],
            2, input_data=b'', output_limit_bytes=1024)
        self.assertFalse(result['output_limit'])
        self.assertEqual(result['returncode'], 0)
        self.assertEqual(len(result['stdout_bytes']), 1024)

    def test_explicit_descriptor_is_inherited(self):
        read_fd, write_fd = os.pipe()
        try:
            os.write(write_fd, b'owned descriptor')
            os.close(write_fd)
            write_fd = None
            result = load().run_supervised(
                [sys.executable, '-c', f'import os;os.write(1,os.read({read_fd},64))'],
                2, pass_fds=(read_fd,))
            self.assertEqual(result['returncode'], 0)
            self.assertEqual(result['stdout_bytes'], b'owned descriptor')
        finally:
            os.close(read_fd)
            if write_fd is not None:
                os.close(write_fd)

    def test_invalid_budget_or_input_starts_no_worker(self):
        module = load()
        # Never let an invalid-input test reach real signal APIs with a mock PID.
        with patch.object(module.subprocess, 'Popen', side_effect=AssertionError('invalid args must fail before spawn')) as spawn:
            for timeout in [0, -1, float('nan'), float('inf')]:
                with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                    module.run_supervised([sys.executable], timeout)
            with self.assertRaises(TypeError):
                module.run_supervised([sys.executable], 1, input_data='not bytes')
            with self.assertRaises(ValueError):
                module.run_supervised([sys.executable], 1, output_limit_bytes=0)
        spawn.assert_not_called()

    def test_output_budget_upper_bound_and_types_start_no_worker(self):
        module = load()
        with patch.object(module.subprocess, 'Popen', side_effect=AssertionError('invalid args must fail before spawn')) as spawn:
            for budget in [8 * 1024 * 1024 + 1, 1.5, True, float('inf')]:
                with self.subTest(budget=budget), self.assertRaises(ValueError):
                    module.run_supervised([sys.executable], 1, output_limit_bytes=budget)
            for data in [bytearray(b'x'), memoryview(b'x')]:
                with self.subTest(data=type(data)), self.assertRaises(TypeError):
                    module.run_supervised([sys.executable], 1, input_data=data)
        spawn.assert_not_called()

    def test_input_byte_ceiling_before_spawn_with_small_injected_budget(self):
        module = load()
        # Exercise the byte ceiling with a kilobyte fixture, without allocating
        # a production-sized 34 MiB payload in this shared test environment.
        with patch.dict(module.run_supervised.__globals__, {'MAX_INPUT_BYTES': 1024}):
            with patch.object(module.subprocess, 'Popen', side_effect=AssertionError('oversized input must fail before spawn')) as spawn:
                with self.assertRaises(ValueError):
                    module.run_supervised([sys.executable], 1, input_data=b'x' * 1025)
            spawn.assert_not_called()
            result = module.run_supervised(
                [sys.executable, '-c', 'import sys;sys.stdout.buffer.write(sys.stdin.buffer.read())'],
                2, input_data=b'x' * 1024)
        self.assertEqual(result['stdout_bytes'], b'x' * 1024)
        self.assertEqual(result['returncode'], 0)

    def test_explicit_environment_and_raw_non_utf8_output(self):
        result = load().run_supervised(
            [sys.executable, '-c', 'import os;os.write(1,os.environ["OWNED_FIXTURE"].encode()+b"\\xff")'],
            2, env=dict(os.environ, OWNED_FIXTURE='fixture'), output_limit_bytes=8 * 1024 * 1024)
        self.assertEqual(result['stdout_bytes'], b'fixture\xff')
        self.assertEqual(result['stdout'], 'fixture\ufffd')
        self.assertFalse(result['output_limit'])

    def test_invalid_address_space_limits_start_no_worker(self):
        module = load_supervision()
        malformed = [(), (1,), (1, 2, 3), [1, 2], '12', (True, 2),
                     (1, False), (1.0, 2), (1, float('inf')), (0, 2),
                     (-1, 2), (2, 1)]
        with patch.object(module.subprocess, 'Popen', side_effect=AssertionError('invalid limits must fail before spawn')) as spawn:
            for limits in malformed:
                with self.subTest(limits=limits), self.assertRaises(ValueError):
                    module.run_supervised([sys.executable], 1, address_space_limit=limits)
        spawn.assert_not_called()

    def test_requested_memory_adapter_fails_closed_on_unsupported_platform(self):
        module = load_supervision()
        with patch.object(module.sys, 'platform', 'darwin'), \
                patch.object(module.subprocess, 'Popen', side_effect=AssertionError('unsupported adapter must fail before spawn')) as spawn:
            with self.assertRaisesRegex(OSError, 'RESOURCE_CONTROL_UNSUPPORTED'):
                module.run_supervised([sys.executable], 1, address_space_limit=(1024, 1024))
        spawn.assert_not_called()

    def test_no_memory_request_preserves_other_posix_adapter(self):
        module = load_supervision()
        with patch.object(module.sys, 'platform', 'darwin'), \
                patch.object(module.subprocess, 'Popen', side_effect=RuntimeError('spawn reached safely')) as spawn:
            with self.assertRaisesRegex(RuntimeError, 'spawn reached safely'):
                module.run_supervised([sys.executable], 1)
        spawn.assert_called_once()
        self.assertIsNone(spawn.call_args.kwargs['preexec_fn'])

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux RLIMIT_AS adapter')
    def test_missing_memory_adapter_starts_no_worker(self):
        module = load_supervision()
        with patch.object(module, 'resource', None, create=True), \
                patch.object(module.subprocess, 'Popen', side_effect=AssertionError('missing adapter must fail before spawn')) as spawn:
            with self.assertRaisesRegex(OSError, 'RESOURCE_CONTROL_UNSUPPORTED'):
                module.run_supervised([sys.executable], 1, address_space_limit=(1024, 1024))
        spawn.assert_not_called()

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux RLIMIT_AS adapter')
    def test_requested_limit_cannot_raise_inherited_hard_limit(self):
        import resource
        module = load_supervision()
        with patch.object(resource, 'getrlimit', return_value=(1024, 2048)), \
                patch.object(module.subprocess, 'Popen', side_effect=AssertionError('inherited ceiling must fail before spawn')) as spawn:
            with self.assertRaisesRegex(ValueError, 'inherited hard'):
                module.run_supervised([sys.executable], 1, address_space_limit=(2048, 4096))
        spawn.assert_not_called()

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux RLIMIT_AS adapter')
    def test_child_observes_limits_with_small_headroom_and_caller_unchanged(self):
        import resource
        module = load_supervision()
        caller_limits = resource.getrlimit(resource.RLIMIT_AS)
        observe = ('import json,os,resource;'
                   'vm=int(open("/proc/self/statm").read().split()[0])*os.sysconf("SC_PAGE_SIZE");'
                   'print(json.dumps({"vm_bytes":vm,"actual":resource.getrlimit(resource.RLIMIT_AS)}))')
        baseline = module.run_supervised([sys.executable, '-c', observe], 2)
        self.assertEqual(baseline['returncode'], 0, baseline['stderr'])
        self.assertNotIn('address_space_limit', baseline)
        vm_bytes = json.loads(baseline['stdout'])['vm_bytes']
        # The test allocates only 1 MiB; its virtual ceiling follows this
        # interpreter's measured startup, with at most 8 MiB of headroom.
        ceiling = vm_bytes + 8 * 1024 * 1024
        if caller_limits[1] != resource.RLIM_INFINITY:
            ceiling = min(ceiling, caller_limits[1])
        requested = (ceiling - 1024 * 1024, ceiling)
        worker = ('import json,resource;payload=bytearray(1024*1024);'
                  'print(json.dumps({"actual":resource.getrlimit(resource.RLIMIT_AS),"bytes":len(payload)}))')
        # Only this owned launcher changes its own inherited limits. The test
        # runner's limits are never reduced, even when a check fails.
        launcher = ('import importlib.util,json,resource,sys;'
                    f'spec=importlib.util.spec_from_file_location("owned_supervisor",{str(SUPERVISION)!r});'
                    'm=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);'
                    f'resource.setrlimit(resource.RLIMIT_AS,({ceiling - 2 * 1024 * 1024},{ceiling}));'
                    'inherited=resource.getrlimit(resource.RLIMIT_AS);'
                    f'result=m.run_supervised([sys.executable,"-c",{worker!r}],2,address_space_limit={requested!r});'
                    'print(json.dumps({"inherited":inherited,"result":{k:v for k,v in result.items() if not isinstance(v,bytes)}}))')
        result = module.run_supervised([sys.executable, '-c', launcher], 4)
        self.assertEqual(result['returncode'], 0, result['stderr'])
        observed = json.loads(result['stdout'])
        self.assertEqual(observed['inherited'], [ceiling - 2 * 1024 * 1024, ceiling])
        child = observed['result']
        self.assertEqual(child['returncode'], 0, child['stderr'])
        self.assertEqual(json.loads(child['stdout']), {'actual': list(requested), 'bytes': 1024 * 1024})
        self.assertEqual(child['address_space_limit'], {
            'requested_soft_bytes': requested[0], 'requested_hard_bytes': requested[1],
            'scope': 'direct child RLIMIT_AS before exec'})
        self.assertEqual(resource.getrlimit(resource.RLIMIT_AS), caller_limits)
        print(json.dumps({'fixture': 'owned child virtual address space',
                          'baseline_vm_bytes': vm_bytes,
                          'inherited_limits_bytes': observed['inherited'],
                          'requested_limits_bytes': list(requested),
                          'observed_child_limits_bytes': json.loads(child['stdout'])['actual'],
                          'allocated_bytes': 1024 * 1024, 'caller_limits_unchanged': True}))


if __name__ == '__main__':
    unittest.main(verbosity=2)
