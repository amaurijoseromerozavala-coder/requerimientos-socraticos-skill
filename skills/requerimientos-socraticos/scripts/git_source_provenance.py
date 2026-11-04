"""Read bounded source excerpts from a full Git commit OID, never the worktree."""

import hashlib
import os
from pathlib import Path
import re
import subprocess
import time

from git_bundle import canonical_path
from gap_glossary import glossary_state


MAX_BLOB = 65536
V2_FIELDS = {'when_true', 'when_false', 'source_ref', 'source_text',
             'source_sha256', 'source_start_byte', 'source_end_byte'}
V1_FIELDS = V2_FIELDS - {'source_start_byte', 'source_end_byte'}


class GitSourceReader:
    def __init__(self, repo, commit, deadline):
        self.repo = Path(repo).resolve(strict=True)
        if not self.repo.is_dir():
            raise ValueError('SOURCE_REPO_NOT_DIRECTORY')
        self.deadline = deadline
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith('GIT_')}
        self.env.update(GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1',
                        GIT_TERMINAL_PROMPT='0', GIT_CONFIG_NOSYSTEM='1',
                        GIT_CONFIG_GLOBAL=os.devnull)
        self.object_format = self.run('rev-parse', '--show-object-format=storage').strip().decode()
        length = {'sha1': 40, 'sha256': 64}.get(self.object_format)
        if length is None or type(commit) is not str or not re.fullmatch('[0-9a-f]{%d}' % length, commit):
            raise ValueError('FULL_SOURCE_COMMIT_OID_REQUIRED')
        if self.run('cat-file', '-t', commit).strip() != b'commit':
            raise ValueError('SOURCE_COMMIT_REQUIRED')
        self.commit = commit
        self.cache = {}

    def run(self, *args):
        remaining = self.deadline - time.monotonic()
        if remaining < .001:
            raise ValueError('SOURCE_DEADLINE')
        command = ['git', '--no-replace-objects', '-c', 'protocol.allow=never',
                   '-C', str(self.repo), *args]
        try:
            completed = subprocess.run(command, capture_output=True,
                                       env=self.env, timeout=min(2, remaining))
        except subprocess.TimeoutExpired as error:
            raise ValueError('SOURCE_DEADLINE') from error
        if completed.returncode != 0 or time.monotonic() >= self.deadline:
            raise ValueError('SOURCE_GIT_FAILED')
        return completed.stdout

    def blob(self, path):
        canonical_path(path)
        if any(ord(char) < 32 for char in path) or len(path) > 512:
            raise ValueError('UNSAFE_SOURCE_PATH')
        if path in self.cache:
            return self.cache[path]
        listing = self.run('ls-tree', '-z', '--full-tree', self.commit,
                           '--', ':(literal)' + path)
        rows = [row for row in listing.split(b'\0') if row]
        if len(rows) != 1:
            raise ValueError('SOURCE_PATH_NOT_REGULAR')
        try:
            header, listed_path = rows[0].split(b'\t', 1)
            mode, kind, oid = header.decode('ascii').split(' ')
            if (listed_path.decode('utf-8') != path or mode not in ('100644', '100755')
                    or kind != 'blob'):
                raise ValueError('SOURCE_PATH_NOT_REGULAR')
            size = int(self.run('cat-file', '-s', oid).strip())
        except (UnicodeError, ValueError) as error:
            raise ValueError('SOURCE_TREE_ENTRY_INVALID') from error
        if not 0 <= size <= MAX_BLOB:
            raise ValueError('SOURCE_BLOB_SIZE_LIMIT')
        raw = self.run('cat-file', 'blob', oid)
        if len(raw) != size:
            raise ValueError('SOURCE_BLOB_SIZE_CHANGED')
        hash_name = self.object_format
        actual_oid = hashlib.new(hash_name, b'blob ' + str(len(raw)).encode()
                                 + b'\0' + raw).hexdigest()
        if actual_oid != oid:
            raise ValueError('SOURCE_BLOB_OID_MISMATCH')
        result = raw, oid, hashlib.sha256(raw).hexdigest()
        self.cache[path] = result
        return result


def prepare_pinned_glossary(glossary, inputs, model_sha256, repo, commit, deadline):
    """Validate v2 entries first, then optionally verify them against Git bytes."""
    if (type(glossary) is not dict
            or set(glossary) != {'schema_version', 'model_sha256', 'variables'}
            or glossary.get('schema_version') != 'rs3-gap-glossary/v2'
            or type(glossary.get('variables')) is not dict):
        raise ValueError('INVALID_PINNED_GLOSSARY')
    converted = {'schema_version': 'rs3-gap-glossary/v1',
                 'model_sha256': glossary['model_sha256'], 'variables': {}}
    offsets = {}
    for name, item in glossary['variables'].items():
        if type(item) is not dict or set(item) != V2_FIELDS:
            raise ValueError('INVALID_PINNED_GLOSSARY_ENTRY')
        start, end = item['source_start_byte'], item['source_end_byte']
        if (type(start) is not int or type(end) is not int
                or not 0 <= start < end <= MAX_BLOB):
            raise ValueError('INVALID_SOURCE_BYTE_RANGE')
        canonical_path(item['source_ref'])
        offsets[name] = start, end
        converted['variables'][name] = {field: item[field] for field in V1_FIELDS}
    state = glossary_state(converted, inputs, model_sha256)
    if state != 'READY_PROPOSED':
        return state, converted, None
    if repo is None or commit is None:
        return 'NEEDS_SOURCE_SNAPSHOT', converted, None
    reader = GitSourceReader(repo, commit, deadline)
    provenance = {}
    for name in inputs:
        entry = converted['variables'][name]
        raw, oid, digest = reader.blob(entry['source_ref'])
        start, end = offsets[name]
        if end > len(raw):
            raise ValueError('SOURCE_BYTE_RANGE_OUTSIDE_BLOB')
        if raw[start:end] != entry['source_text'].encode('utf-8'):
            raise ValueError('SOURCE_GIT_SLICE_MISMATCH')
        provenance[name] = {'source_commit_oid': reader.commit,
                            'git_blob_oid': oid, 'source_blob_sha256': digest,
                            'source_start_byte': start, 'source_end_byte': end}
    return 'PINNED_BYTES_VERIFIED', converted, {
        'variables': provenance, 'commit': reader.commit,
        'object_format': reader.object_format}
