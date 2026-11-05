"""Private records bind a TTY write, never a human decision."""

import hashlib
import json
import os
from pathlib import Path
import pty
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import private_interrogation_store as store


class PrivateInterrogationCustodyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='private-history-')
        base = Path(self.temp.name)
        self.root = base / 'custody'
        self.root.mkdir(mode=0o700)
        model = {'inputs': ['A'], 'outputs': ['P'], 'domain': True,
                 'rules': [{'id': 'inactive', 'guard': False,
                            'response': {'var': 'P'}}], 'properties': []}
        raw = json.dumps(model, sort_keys=True).encode()
        model_file = base / 'model.json'
        model_file.write_bytes(raw)
        source = 'Definición propuesta de A'
        glossary = {'schema_version': 'rs3-gap-glossary/v1',
                    'model_sha256': hashlib.sha256(raw).hexdigest(),
                    'variables': {'A': {'when_true': 'A presente',
                                        'when_false': 'A ausente',
                                        'source_ref': 'synthetic/A',
                                        'source_text': source,
                                        'source_sha256': hashlib.sha256(
                                            source.encode()).hexdigest()}}}
        glossary_file = base / 'glossary.json'
        glossary_file.write_text(json.dumps(glossary), encoding='utf-8')
        run = subprocess.run([sys.executable, str(SCRIPTS / 'analyze_to_view.py'),
                              str(model_file), '--glossary', str(glossary_file),
                              '--format', 'question-json'], capture_output=True,
                             text=True, timeout=15)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.handoff = json.loads(run.stdout)

    def tearDown(self):
        self.temp.cleanup()

    def test_private_create_tty_delivery_and_unverified_response(self):
        sid = store.create(self.root, self.handoff)
        path = self.root / ('session-' + sid + '.json')
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(store.load(self.root, sid)['state'], 'WAITING_USER')
        master, slave = pty.openpty()
        try:
            receipt = store.deliver(self.root, sid, slave)
            transmitted = os.read(master, 8192)
        finally:
            os.close(master)
            os.close(slave)
        self.assertEqual(receipt['status'], 'TTY_WRITE_COMPLETED')
        self.assertEqual(receipt['bytes_sha256'],
                         hashlib.sha256(transmitted.replace(b'\r\n', b'\n')).hexdigest())
        self.assertEqual(receipt['question_sha256'], self.handoff['question_sha256'])
        self.assertEqual(receipt['human_viewed'], False)
        literal = 'Quiero reformular la excepción.\n'
        updated = store.record_response(self.root, sid, literal)
        self.assertEqual(updated['state'], 'INTERPRETATION_REVIEW')
        self.assertEqual(updated['events'][1]['text'], literal)
        self.assertEqual(updated['events'][1]['origin'], 'UNVERIFIED_RELAY')
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(ValueError):
            store.record_response(self.root, sid, literal)

    def test_rejects_repo_root_loose_mode_and_symlink(self):
        self.root.chmod(0o755)
        with self.assertRaises(ValueError):
            store.create(self.root, self.handoff)
        self.root.chmod(0o700)
        link = Path(self.temp.name) / 'link'
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            store.create(link, self.handoff)
        repo = Path(self.temp.name) / 'repo'
        repo.mkdir(mode=0o700)
        subprocess.run(['git', 'init', '-q', str(repo)], check=True)
        with self.assertRaises(ValueError):
            store.create(repo, self.handoff)
        nested = repo / 'custody'
        nested.mkdir(mode=0o700)
        with patch.dict(os.environ, {'GIT_CEILING_DIRECTORIES': str(repo)}):
            with self.assertRaises(ValueError):
                store.create(nested, self.handoff)
        broken = Path(self.temp.name) / 'broken-repo'
        broken.mkdir(mode=0o700)
        (broken / '.git').write_text('invalid git marker', encoding='utf-8')
        with self.assertRaises(ValueError):
            store.create(broken, self.handoff)

    def test_non_tty_and_response_before_delivery_fail_closed(self):
        sid = store.create(self.root, self.handoff)
        with self.assertRaises(ValueError):
            store.record_response(self.root, sid, 'texto')
        reader, writer = os.pipe()
        try:
            with self.assertRaises(ValueError):
                store.deliver(self.root, sid, writer)
        finally:
            os.close(reader)
            os.close(writer)
        self.assertFalse((self.root / ('delivery-' + sid + '.json')).exists())

    def test_concurrent_response_attempts_do_not_overwrite(self):
        sid = store.create(self.root, self.handoff)
        master, slave = pty.openpty()
        try:
            store.deliver(self.root, sid, slave)
            os.read(master, 8192)
        finally:
            os.close(master)
            os.close(slave)
        results = []
        def attempt(text):
            try:
                store.record_response(self.root, sid, text)
                results.append('SAVED')
            except ValueError:
                results.append('REJECTED')
        threads = [threading.Thread(target=attempt, args=(text,))
                   for text in ('uno', 'dos')]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=5)
        self.assertEqual(sorted(results), ['REJECTED', 'SAVED'])

    def test_extra_authority_fields_and_boolean_substitution_are_rejected(self):
        sid = store.create(self.root, self.handoff)
        path = self.root / ('session-' + sid + '.json')
        history = json.loads(path.read_text(encoding='utf-8'))
        history['execution_authorized'] = 0
        path.write_text(json.dumps(history), encoding='utf-8')
        with self.assertRaises(ValueError):
            store.load(self.root, sid)
        history['execution_authorized'] = False
        path.write_text(json.dumps(history), encoding='utf-8')
        master, slave = pty.openpty()
        try:
            store.deliver(self.root, sid, slave)
            os.read(master, 8192)
        finally:
            os.close(master)
            os.close(slave)
        receipt_path = self.root / ('delivery-' + sid + '.json')
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
        receipt['execution_authorized'] = True
        receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
        with self.assertRaises(ValueError):
            store.record_response(self.root, sid, 'texto')

    def test_tty_write_failure_leaves_no_delivery_receipt(self):
        sid = store.create(self.root, self.handoff)
        master, slave = pty.openpty()
        try:
            with patch.object(store, '_write_tty', side_effect=TimeoutError):
                with self.assertRaises(TimeoutError):
                    store.deliver(self.root, sid, slave)
        finally:
            os.close(master)
            os.close(slave)
        self.assertFalse((self.root / ('delivery-' + sid + '.json')).exists())

    def test_bidi_control_is_visible_as_escape_on_tty(self):
        forged = json.loads(json.dumps(self.handoff))
        forged['question']['scenario_clauses'][0]['proposed_phrase'] = 'A\u202eB'
        binding = {key: forged[key] for key in
                   ('model_sha256', 'glossary_sha256', 'question')}
        canonical = json.dumps(binding, ensure_ascii=False, sort_keys=True,
                               separators=(',', ':')).encode()
        forged['question_sha256'] = hashlib.sha256(
            b'rs3-question-handoff/v1\n' + canonical).hexdigest()
        sid = store.create(self.root, forged)
        master, slave = pty.openpty()
        try:
            store.deliver(self.root, sid, slave)
            displayed = os.read(master, 8192)
        finally:
            os.close(master)
            os.close(slave)
        self.assertNotIn('\u202e'.encode(), displayed)
        self.assertIn(b'\\u202e', displayed)

    def test_failed_replace_preserves_waiting_state_without_orphan_temp(self):
        sid = store.create(self.root, self.handoff)
        master, slave = pty.openpty()
        try:
            store.deliver(self.root, sid, slave)
            os.read(master, 8192)
        finally:
            os.close(master)
            os.close(slave)
        with patch.object(store.os, 'replace', side_effect=OSError):
            with self.assertRaises(OSError):
                store.record_response(self.root, sid, 'texto')
        self.assertEqual(store.load(self.root, sid)['state'], 'WAITING_USER')
        self.assertEqual(list(self.root.glob('update-*.json')), [])

    def test_cli_real_tty_flow_exposes_only_status_metadata(self):
        handoff_file = Path(self.temp.name) / 'handoff.json'
        handoff_file.write_text(json.dumps(self.handoff), encoding='utf-8')
        cli = SCRIPTS / 'private_interrogation_store.py'
        created = subprocess.run([sys.executable, str(cli), 'create',
                                  str(self.root), str(handoff_file)],
                                 capture_output=True, text=True, timeout=5)
        self.assertEqual(created.returncode, 0, created.stderr)
        sid = json.loads(created.stdout)['session_id']
        master, slave = pty.openpty()
        try:
            presented = subprocess.run([sys.executable, str(cli), 'present',
                                        str(self.root), sid], stdout=slave,
                                       stderr=subprocess.PIPE, timeout=5)
            displayed = os.read(master, 8192)
        finally:
            os.close(master)
            os.close(slave)
        self.assertEqual(presented.returncode, 0, presented.stderr)
        self.assertIn(b'Escenario propuesto', displayed)
        response = Path(self.temp.name) / 'response.txt'
        response.write_text('Mi texto literal', encoding='utf-8')
        replied = subprocess.run([sys.executable, str(cli), 'respond',
                                  str(self.root), sid, '--response-file',
                                  str(response)], capture_output=True,
                                 text=True, timeout=5)
        self.assertEqual(replied.returncode, 0, replied.stderr)
        self.assertEqual(json.loads(replied.stdout)['status'],
                         'INTERPRETATION_REVIEW')
        self.assertNotIn('Mi texto literal', replied.stdout)

    def test_replaced_session_fifo_does_not_block_reader(self):
        sid = store.create(self.root, self.handoff)
        path = self.root / ('session-' + sid + '.json')
        path.unlink()
        os.mkfifo(path, 0o600)
        probe = ('import sys; sys.path.insert(0, sys.argv[1]); '
                 'import private_interrogation_store as s; '
                 's.load(sys.argv[2], sys.argv[3])')
        run = subprocess.run([sys.executable, '-c', probe, str(SCRIPTS),
                              str(self.root), sid], capture_output=True,
                             timeout=1)
        self.assertNotEqual(run.returncode, 0)

    def test_delivery_fifo_does_not_block_root_lock_or_tty_deadline(self):
        sid = store.create(self.root, self.handoff)
        receipt = self.root / ('delivery-' + sid + '.json')
        os.mkfifo(receipt, 0o600)
        cli = SCRIPTS / 'private_interrogation_store.py'
        run = subprocess.run([sys.executable, str(cli), 'present',
                              str(self.root), sid], capture_output=True,
                             timeout=1)
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(store.load(self.root, sid)['state'], 'WAITING_USER')

    def test_receipt_publication_failure_keeps_session_retryable(self):
        sid = store.create(self.root, self.handoff)
        master, slave = pty.openpty()
        try:
            with patch.object(store.os, 'link', side_effect=OSError):
                with self.assertRaises(OSError):
                    store.deliver(self.root, sid, slave)
            os.read(master, 8192)
            self.assertFalse((self.root / ('delivery-' + sid + '.json')).exists())
            result = store.deliver(self.root, sid, slave)
            os.read(master, 8192)
        finally:
            os.close(master)
            os.close(slave)
        self.assertEqual(result['status'], 'TTY_WRITE_COMPLETED')

    def test_partial_tty_write_and_backpressure_stop_without_receipt(self):
        sid = store.create(self.root, self.handoff)
        master, slave = pty.openpty()
        calls = []
        def readiness(_read, writable, _error, remaining):
            calls.append(remaining)
            if len(calls) == 1:
                return [], writable, []
            time.sleep(min(remaining, 0.05))
            return [], [], []
        try:
            with patch.object(store, 'WRITE_DEADLINE_SECONDS', 0.05), patch.object(
                    store.select, 'select', side_effect=readiness), patch.object(
                    store.os, 'write', return_value=1):
                with self.assertRaises(TimeoutError):
                    store.deliver(self.root, sid, slave)
        finally:
            os.close(master)
            os.close(slave)
        self.assertGreaterEqual(len(calls), 2)
        self.assertFalse((self.root / ('delivery-' + sid + '.json')).exists())
        self.assertEqual(store.load(self.root, sid)['state'], 'WAITING_USER')

    def test_interrupted_after_link_recovers_complete_receipt(self):
        sid = store.create(self.root, self.handoff)
        master, slave = pty.openpty()
        try:
            store.deliver(self.root, sid, slave)
            os.read(master, 8192)
        finally:
            os.close(master)
            os.close(slave)
        receipt = self.root / ('delivery-' + sid + '.json')
        staging = self.root / ('stage-' + sid + '.json')
        os.link(receipt, staging)
        self.assertEqual(receipt.stat().st_nlink, 2)
        updated = store.record_response(self.root, sid, 'respuesta')
        self.assertEqual(updated['state'], 'INTERPRETATION_REVIEW')
        self.assertFalse(staging.exists())
        self.assertEqual(receipt.stat().st_nlink, 1)

    def test_interrupted_before_link_drops_partial_stage_and_retries(self):
        sid = store.create(self.root, self.handoff)
        staging = self.root / ('stage-' + sid + '.json')
        staging.write_bytes(b'{partial')
        staging.chmod(0o600)
        master, slave = pty.openpty()
        try:
            receipt = store.deliver(self.root, sid, slave)
            os.read(master, 8192)
        finally:
            os.close(master)
            os.close(slave)
        self.assertEqual(receipt['status'], 'TTY_WRITE_COMPLETED')
        self.assertFalse(staging.exists())


if __name__ == '__main__':
    unittest.main()
