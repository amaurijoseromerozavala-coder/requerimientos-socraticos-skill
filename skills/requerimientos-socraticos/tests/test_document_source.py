"""Synthetic byte-bound document sources; no real dialogue or approval evidence."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import document_source as sources
import validate_interview as interview_validator
import validate_prd as prd_validator
import test_interview as fixtures


def oid(raw):
    return hashlib.sha256(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def memory(mapping):
    return sources.MemorySource(mapping, {name: oid(raw) for name, raw in mapping.items()})


def documents():
    """Reuse the established synthetic PRD oracle, then retain only its bytes."""
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        fixtures.ContractTests().stage_prd(base)
        return {path.name: path.read_bytes() for path in base.iterdir()}


def rebind_candidate(mapping, prd):
    prd['assurance']['candidate_sha256'] = hashlib.sha256(json.dumps(
        prd['candidate'], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    mapping['prd.json'] = json.dumps(prd).encode()


class SourceTests(unittest.TestCase):
    def test_memory_copies_both_mappings(self):
        data = {'x.txt': b'original'}
        ids = {'x.txt': oid(data['x.txt'])}
        source = sources.MemorySource(data, ids)
        data['x.txt'] = b'changed'
        ids['x.txt'] = '0' * 64
        self.assertEqual(source.read('x.txt'), b'original')

    def test_values_must_be_immutable_bytes(self):
        with self.assertRaises((TypeError, ValueError)):
            sources.MemorySource({'x': bytearray(b'x')}, {'x': oid(b'x')})

    def test_blob_oid_is_git_sha256_not_content_sha256(self):
        raw = b'synthetic'
        source = sources.MemorySource({'x': raw}, {'x': hashlib.sha256(raw).hexdigest()})
        with self.assertRaises(sources.Invalid) as err:
            source.read('x')
        self.assertEqual(err.exception.code, 'BLOB_OID_MISMATCH')
        self.assertEqual(memory({'x': raw}).read('x'), raw)

    def test_missing_or_surplus_oid_is_rejected(self):
        for data, ids in [({'x': b'x'}, {}), ({}, {'x': oid(b'x')})]:
            with self.subTest(data=data), self.assertRaises(sources.Invalid):
                sources.MemorySource(data, ids)

    def test_missing_document_has_filesystem_compatible_exception(self):
        with self.assertRaises(FileNotFoundError):
            memory({}).read('missing')

    def test_canonical_posix_paths_at_all_entrypoints(self):
        invalid = ['', '/x', '../x', 'a/../x', './x', 'a//x', 'a/./x', 'a\\x', 'x/', 'x\0y']
        source = memory({'x': b'x'})
        for name in invalid:
            with self.subTest(name=name):
                for operation in [lambda: source.read(name), lambda: source.scope(name),
                                  lambda: sources.MemorySource({name: b'x'}, {name: oid(b'x')})]:
                    with self.assertRaises(sources.Invalid) as err:
                        operation()
                    self.assertEqual(err.exception.code, 'UNSAFE_PATH')
        self.assertEqual(source.scope(PurePosixPath('.')).read('x'), b'x')

    def test_scopes_are_relative_and_keep_byte_identity(self):
        source = memory({'docs/receipts/x': b'x'})
        scoped = source.scope('docs').scope('receipts')
        self.assertEqual(scoped.read('x'), b'x')
        with self.assertRaises(FileNotFoundError):
            source.read('x')

    def test_consumed_files_are_verified_shared_scoped_and_copied(self):
        source = memory({'docs/b': b'b', 'a': b'a'})
        self.assertEqual(source.consumed_files, [])
        source.scope('docs').read('b')
        source.read('a')
        source.read('a')
        expected = [{'path': name, 'git_oid': oid(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                    for name, raw in [('a', b'a'), ('docs/b', b'b')]]
        self.assertEqual(source.consumed_files, expected)
        copied = source.consumed_files
        copied[0]['path'] = 'mutated'
        copied.clear()
        self.assertEqual(source.consumed_files, expected)
        rejected = sources.MemorySource({'x': b'x'}, {'x': '0' * 64})
        with self.assertRaises(sources.Invalid):
            rejected.read('x')
        self.assertEqual(rejected.consumed_files, [])

    def test_memory_read_preserves_file_size_limit(self):
        source = memory({'x': b'12345'})
        with patch.object(sources, 'MAX_FILE_BYTES', 4), self.assertRaisesRegex(ValueError, 'FILE_SIZE_LIMIT'):
            source.read('x')

    def test_filesystem_source_scope_and_rejected_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'docs').mkdir()
            (base / 'docs/x').write_bytes(b'x')
            (base / 'link').symlink_to(base / 'docs/x')
            source = sources.FilesystemSource(base)
            self.assertEqual(source.scope('docs').read('x'), b'x')
            with self.assertRaises(sources.Invalid) as err:
                source.read('link')
            self.assertEqual(err.exception.code, 'UNSAFE_PATH')


class DependencyTests(unittest.TestCase):
    def assert_invalid(self, code, call):
        with self.assertRaises(sources.Invalid) as err:
            call()
        self.assertEqual(err.exception.code, code, str(err.exception))

    def test_memory_prd_reads_only_installed_schemas_from_filesystem(self):
        mapping = documents()
        original_read = interview_validator.read_regular

        def installed_only(base, name, *args):
            self.assertEqual(Path(base), ROOT / 'assets')
            return original_read(base, name, *args)

        with patch.object(interview_validator, 'read_regular', side_effect=installed_only), \
                patch.object(sources, 'read_regular', side_effect=AssertionError('Candidate filesystem read')):
            result = prd_validator.validate_prd(Path('/absent/prd.json'), source=memory(mapping))
        self.assertEqual(result['interview'], 'COMPLETE')

    def test_prd_scopes_interview_receipts_to_its_subdirectory(self):
        mapping = documents()
        prd = json.loads(mapping['prd.json'])
        for name in list(mapping):
            if name != 'prd.json':
                mapping['interviews/' + name] = mapping.pop(name)
        for key in ['interview_ref', 'design_proposals_ref']:
            prd['candidate'][key]['path'] = 'interviews/' + prd['candidate'][key]['path']
        rebind_candidate(mapping, prd)
        nested = {'project/' + name: raw for name, raw in mapping.items()}
        result = prd_validator.validate_prd(Path('project/prd.json'), source=memory(nested).scope('project'))
        self.assertEqual(result['design'], 'REVIEWED')

    def test_each_dependency_and_receipt_is_oid_checked(self):
        mapping = documents()
        for name in ['prd.json', 'interview.json', 'design.json', 'q1.txt', 'a1.txt', 'research-1.txt']:
            ids = {path: oid(raw) for path, raw in mapping.items()}
            ids[name] = '0' * 64
            with self.subTest(name=name):
                self.assert_invalid('BLOB_OID_MISMATCH', lambda: prd_validator.validate_prd(
                    Path('prd.json'), source=sources.MemorySource(mapping, ids)))

    def test_existing_dependency_and_receipt_diagnostics_are_preserved(self):
        cases = [('interview.json', b'{}', 'STALE_DEPENDENCY'),
                 ('design.json', b'{}', 'STALE_DEPENDENCY'),
                 ('q1.txt', b'changed', 'RECEIPT_MISMATCH'),
                 ('research-1.txt', b'changed', 'RESEARCH_RECEIPT_MISMATCH'),
                 ('a1.txt', None, 'RECEIPT_MISSING'),
                 ('research-1.txt', None, 'RESEARCH_RECEIPT_MISSING')]
        for name, replacement, code in cases:
            mapping = documents()
            if replacement is None:
                del mapping[name]
            else:
                mapping[name] = replacement
            with self.subTest(name=name, code=code):
                self.assert_invalid(code, lambda: prd_validator.validate_prd(Path('prd.json'), source=memory(mapping)))

    def test_interview_source_without_base_checks_receipts(self):
        mapping = documents()
        del mapping['q1.txt']
        doc = json.loads(mapping['interview.json'])
        self.assert_invalid('RECEIPT_MISSING', lambda: interview_validator.validate(doc, source=memory(mapping)))

    def test_memory_dependency_escape_rejected(self):
        mapping = documents()
        prd = json.loads(mapping['prd.json'])
        prd['candidate']['interview_ref']['path'] = '../interview.json'
        rebind_candidate(mapping, prd)
        self.assert_invalid('UNSAFE_PATH', lambda: prd_validator.validate_prd(Path('prd.json'), source=memory(mapping)))

    def test_direct_receipt_api_accepts_source(self):
        raw = b'synthetic answer'
        entry = {'path': 'answer', 'format': 'PLAIN_TEXT', 'sha256': hashlib.sha256(raw).hexdigest()}
        interview_validator.receipt(None, entry, raw.decode(), source=memory({'answer': raw}))

    def test_nonregular_receipt_preserves_missing_diagnostic(self):
        for name, code in [('q1.txt', 'RECEIPT_MISSING'), ('research-1.txt', 'RESEARCH_RECEIPT_MISSING')]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                path = fixtures.ContractTests().stage_prd(base)
                (base / name).unlink()
                (base / name).mkdir()
                self.assert_invalid(code, lambda: prd_validator.validate_prd(path))


if __name__ == '__main__':
    unittest.main(verbosity=2)
