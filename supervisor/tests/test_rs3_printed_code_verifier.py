"""One-attempt synthetic code checks without human authority."""

from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest import mock

from supervisor.rs3_coordinate_ledger import CoordinateLedger, LedgerBlocked
from supervisor.rs3_printed_code_verifier import PrintedCodeVerifier, CodeVerifierBlocked


class PrintedCodeVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'ledger'
        CoordinateLedger.initialize(self.root, card_id='CARD-1',
                                    coordinates=['A1', 'A2'])
        self.codes = {'A1': 'a' * 32, 'A2': 'b' * 32}
        PrintedCodeVerifier.initialize(self.root, self.codes)
        self.digest = 'c' * 64

    def test_match_returns_only_after_durable_spend_and_no_authority(self):
        CoordinateLedger(self.root).reserve('A1', self.digest)
        result = PrintedCodeVerifier(self.root).check_and_spend('A1', self.digest,
                                                                self.codes['A1'])
        self.assertIs(result['code_match'], True)
        self.assertEqual(result['state'], 'SPENT')
        self.assertEqual(result['authority_verification'], 'NOT_ESTABLISHED')
        self.assertIs(result['execution_authorized'], False)
        self.assertNotIn('receipt', result)
        with self.assertRaises(CodeVerifierBlocked):
            PrintedCodeVerifier(self.root).check_and_spend('A1', self.digest,
                                                            self.codes['A1'])

    def test_wrong_or_malformed_code_burns_coordinate(self):
        for coordinate, wrong in (('A1', '0' * 32), ('A2', 'not-hex')):
            with self.subTest(coordinate=coordinate):
                CoordinateLedger(self.root).reserve(coordinate, self.digest)
                result = PrintedCodeVerifier(self.root).check_and_spend(
                    coordinate, self.digest, wrong)
                self.assertIs(result['code_match'], False)
                self.assertEqual(CoordinateLedger(self.root).snapshot()
                                 ['coordinates'][coordinate]['state'], 'SPENT')

    def test_mismatch_or_competing_checks_do_not_return_two_results(self):
        CoordinateLedger(self.root).reserve('A1', self.digest)
        with self.assertRaises(CodeVerifierBlocked):
            PrintedCodeVerifier(self.root).check_and_spend(
                'A1', 'd' * 64, self.codes['A1'])
        def attempt(_):
            try:
                return PrintedCodeVerifier(self.root).check_and_spend(
                    'A1', self.digest, self.codes['A1'])['code_match']
            except CodeVerifierBlocked:
                return 'BLOCKED'
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, range(2)))
        self.assertEqual(outcomes.count(True), 1)
        self.assertEqual(outcomes.count('BLOCKED'), 1)

    def test_verifier_file_private_and_corruption_blocks(self):
        verifier = self.root / 'verifiers.json'
        self.assertEqual(verifier.stat().st_mode & 0o777, 0o600)
        raw = verifier.read_text()
        for code in self.codes.values():
            self.assertNotIn(code, raw)
        CoordinateLedger(self.root).reserve('A1', self.digest)
        os.chmod(verifier, 0o644)
        with self.assertRaises(CodeVerifierBlocked):
            PrintedCodeVerifier(self.root).check_and_spend('A1', self.digest,
                                                            self.codes['A1'])
        os.chmod(verifier, 0o600)
        verifier.write_text('{}')
        with self.assertRaises(CodeVerifierBlocked):
            PrintedCodeVerifier(self.root).check_and_spend('A1', self.digest,
                                                            self.codes['A1'])
        self.assertEqual(CoordinateLedger(self.root).snapshot()['coordinates']['A1']['state'],
                         'PENDING')

    def test_spend_failure_cannot_return_match(self):
        CoordinateLedger(self.root).reserve('A1', self.digest)
        with mock.patch.object(CoordinateLedger, 'spend_pending',
                               side_effect=LedgerBlocked('synthetic')):
            with self.assertRaises(CodeVerifierBlocked):
                PrintedCodeVerifier(self.root).check_and_spend('A1', self.digest,
                                                                self.codes['A1'])
        self.assertEqual(CoordinateLedger(self.root).snapshot()['coordinates']['A1']['state'],
                         'PENDING')

    def test_not_pending_does_not_examine_code(self):
        with mock.patch('supervisor.rs3_printed_code_verifier.hmac.compare_digest',
                        side_effect=AssertionError('code examined before reservation')):
            with self.assertRaises(CodeVerifierBlocked):
                PrintedCodeVerifier(self.root).check_and_spend('A1', self.digest,
                                                                self.codes['A1'])

    def test_stage_or_symlink_blocks_without_spending(self):
        CoordinateLedger(self.root).reserve('A1', self.digest)
        stage = self.root / 'state.stage'
        stage.write_text('unfinished')
        os.chmod(stage, 0o600)
        with self.assertRaises(CodeVerifierBlocked):
            PrintedCodeVerifier(self.root).check_and_spend('A1', self.digest,
                                                            self.codes['A1'])
        CoordinateLedger(self.root).reconcile_stage()
        verifier = self.root / 'verifiers.json'
        target = self.root / 'saved-verifiers.json'
        verifier.rename(target)
        verifier.symlink_to(target)
        with self.assertRaises(CodeVerifierBlocked):
            PrintedCodeVerifier(self.root).check_and_spend('A1', self.digest,
                                                            self.codes['A1'])
        self.assertEqual(CoordinateLedger(self.root).snapshot()['coordinates']['A1']['state'],
                         'PENDING')

    def test_duplicate_code_cannot_be_provisioned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'ledger'
            CoordinateLedger.initialize(root, card_id='CARD-2',
                                        coordinates=['A1', 'A2'])
            with self.assertRaises(CodeVerifierBlocked):
                PrintedCodeVerifier.initialize(root, {'A1': 'a' * 32,
                                                      'A2': 'a' * 32})
            self.assertFalse((root / 'verifiers.json').exists())

    def test_uncertain_provisioning_blocks_verifier_use(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'ledger'
            CoordinateLedger.initialize(root, card_id='CARD-2', coordinates=['A1'])
            original = os.fsync
            directory_syncs = 0

            def fail_after_file_written(fd):
                nonlocal directory_syncs
                if stat.S_ISDIR(os.fstat(fd).st_mode):
                    directory_syncs += 1
                    if directory_syncs == 2:
                        raise OSError('synthetic directory sync failure')
                return original(fd)

            with mock.patch('supervisor.rs3_printed_code_verifier.os.fsync',
                            side_effect=fail_after_file_written):
                with self.assertRaises(CodeVerifierBlocked):
                    PrintedCodeVerifier.initialize(root, {'A1': 'a' * 32})
            self.assertTrue((root / 'verifiers.json').exists())
            CoordinateLedger(root).reserve('A1', self.digest)
            with self.assertRaises(CodeVerifierBlocked):
                PrintedCodeVerifier(root).check_and_spend('A1', self.digest,
                                                           'a' * 32)
            self.assertEqual(CoordinateLedger(root).snapshot()['coordinates']['A1']['state'],
                             'PENDING')


if __name__ == '__main__':
    unittest.main()
