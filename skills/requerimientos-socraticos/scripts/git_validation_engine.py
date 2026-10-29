#!/usr/bin/env python3
"""Validate a bounded complete documentation commit by full OID, never HEAD/worktree."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from process_supervision import run_supervised
from git_bundle import encode_bundle, canonical_path
import time
from memory_budget import memory_policy, observe_process_memory

MEMORY_FAILURE = b'{"status":"BLOCKED","error":"MEMORY_BUDGET_EXCEEDED"}\n'

class InvalidGit(ValueError):
    pass

class Objects:
    def __init__(self, repo, seconds, policy=None, lease_fd=None):
        if not 0 < seconds <= 300:
            raise InvalidGit('INVALID_TIMEOUT')
        self.policy = policy if policy is not None else memory_policy()
        self.pass_fds = (lease_fd,) if lease_fd is not None else ()
        self.repo = repo.resolve(strict=True)
        self.deadline = time.monotonic() + seconds
        self.env = {k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
        self.env.update(GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0', GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)

    def run(self, *args, limit=2*1024*1024):
        command = ['git','--no-replace-objects','-c','protocol.allow=never','-C',str(self.repo),*args]
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise InvalidGit('GIT_DEADLINE')
        result = run_supervised(command, remaining, env=self.env, output_limit_bytes=limit,
                                pass_fds=self.pass_fds,
                                address_space_limit=(self.policy['roles_bytes']['git'],)*2)
        if result['timed_out']:
            raise InvalidGit('GIT_DEADLINE')
        if result['output_limit']:
            raise InvalidGit('GIT_OUTPUT_LIMIT')
        if result['cleanup_status'] == 'INCOMPLETE':
            raise InvalidGit('GIT_CLEANUP_INCOMPLETE')
        if result['returncode'] != 0:
            raise InvalidGit('GIT_COMMAND_FAILED')
        return result['stdout_bytes']

    def object(self, kind, oid, limit):
        raw = self.run('cat-file',kind,oid,limit=limit)
        if not re.fullmatch(r'[0-9a-f]{64}', oid):
            raise InvalidGit('SHA256_REQUIRED')
        actual = hashlib.sha256(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if actual != oid:
            raise InvalidGit('CORRUPT_GIT_OBJECT')
        return raw

def validate_local(repo, commit, prd, timeout=60, policy=None, lease_fd=None):
    policy = policy if policy is not None else memory_policy()
    if not re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})',commit):
        raise InvalidGit('FULL_COMMIT_OID_REQUIRED')
    if len(commit) != 64:
        raise InvalidGit('SHA256_REQUIRED')
    obj = Objects(repo,timeout,policy,lease_fd)
    if obj.run('rev-parse','--show-object-format=storage').strip() != b'sha256':
        raise InvalidGit('SHA256_REQUIRED')
    if obj.run('cat-file','-t',commit).strip() != b'commit':
        raise InvalidGit('COMMIT_REQUIRED')
    raw = obj.object('commit',commit,1024*1024)
    first = raw.split(b'\n',1)[0]
    if not re.fullmatch(b'tree [0-9a-f]{'+str(len(commit)).encode()+b'}',first):
        raise InvalidGit('INVALID_COMMIT_TREE')
    tree = first[5:].decode('ascii')
    obj.object('tree',tree,2*1024*1024)
    listing = obj.run('ls-tree','-r','-t','-z','--full-tree',tree)
    entries = [row for row in listing.split(b'\0') if row]
    if len(entries)>4096:
        raise InvalidGit('ENTRY_LIMIT')
    manifest = []; total = 0; seen = set()
    files, oids = {}, {}
    for row in entries:
        header, name = row.split(b'\t', 1)
        mode, kind, oid = header.decode('ascii').split(' ')
        name = name.decode('utf-8')
        canonical_path(name)
        if name in seen:
            raise InvalidGit('UNSAFE_TREE_PATH')
        seen.add(name)
        if kind == 'tree' and mode == '040000':
            obj.object('tree', oid, 2*1024*1024)
        elif kind == 'blob' and mode in ['100644', '100755']:
            data = obj.object('blob', oid, 8*1024*1024)
            total += len(data)
            if total > 32*1024*1024:
                raise InvalidGit('BYTE_LIMIT')
            files[name], oids[name] = data, oid
            manifest.append({'path': name, 'git_oid': oid, 'sha256': hashlib.sha256(data).hexdigest()})
        else:
            raise InvalidGit('UNSUPPORTED_GIT_ENTRY')
    relative = PurePosixPath(prd)
    try:
        canonical_path(prd)
    except ValueError as error:
        raise InvalidGit('UNSAFE_PRD_PATH') from error
    payload = encode_bundle(prd, files, oids)
    # Transfer only verified content, never execute code from the candidate.
    # Every dependent document/receipt is resolved in the same in-memory bundle.
    remaining = obj.deadline-time.monotonic()
    if remaining <= 0:
        raise InvalidGit('GIT_DEADLINE')
    command = [os.path.abspath(sys.executable), '-B', str(Path(__file__).with_name('git_document_worker.py'))]
    result = run_supervised(command, remaining, input_data=payload,
                            pass_fds=obj.pass_fds,
                            address_space_limit=(policy['roles_bytes']['consumer'],)*2)
    if result['timed_out']:
        raise InvalidGit('DOCUMENT_DEADLINE')
    if result['output_limit']:
        raise InvalidGit('DOCUMENT_OUTPUT_LIMIT')
    if result['cleanup_status'] == 'INCOMPLETE':
        raise InvalidGit('DOCUMENT_CLEANUP_INCOMPLETE')
    if result['returncode']:
        try:
            failure = json.loads(result['stdout'])
        except ValueError:
            failure = {}
        if failure.get('error') == 'MEMORY_BUDGET_EXCEEDED':
            raise InvalidGit('MEMORY_BUDGET_EXCEEDED')
        raise InvalidGit('DOCUMENT_INVALID:'+result['stdout'])
    document = json.loads(result['stdout'])
    consumed = document['consumed_files']
    expected = {entry['path']: entry for entry in manifest}
    if (not isinstance(consumed, list) or not consumed or
            any(not isinstance(entry, dict) or entry != expected.get(entry.get('path')) for entry in consumed) or
            len({entry['path'] for entry in consumed}) != len(consumed) or
            prd not in {entry['path'] for entry in consumed}):
        raise InvalidGit('CONSUMED_CONTENT_MISMATCH')
    return {'status': 'DOCUMENT_VALIDATED_GIT', 'commit_oid': commit, 'tree_oid': tree,
            'files': manifest, 'document_validation': document['document_validation'],
            'document_transport': 'VERIFIED_BYTES_STDIN', 'consumed_files': consumed,
            'memory_budget': {'policy': policy, 'coordinator': observe_process_memory(),
                              'consumer': document['memory_observation'],
                              'rss_quota_enforced': False, 'aggregate_kernel_quota': False},
            'supervision': {key: result[key] for key in ['parent_death_policy', 'cleanup_status', 'elapsed_seconds']},
            'advance': 'BLOCKED_GLOBAL_ENFORCEMENT',
            'limits': ['Pinned objects, not signature or trusted authorship.',
                       'Trusted installed engine/kernel/account; no same-UID isolation guarantee.',
                       'Bounded in-memory blobs and supervised stdin; no candidate scratch files or leases.',
                       'Linux parent-death coupling covers direct children; not real-time or arbitrary descendants.',
                       'Complete bounded documentation commit; no production authorization.']}

def main():
    parser = argparse.ArgumentParser(description='Internal memory-bounded Git coordinator')
    parser.add_argument('repo', type=Path)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--prd', required=True)
    parser.add_argument('--timeout', type=float, default=60)
    parser.add_argument('--memory-budget-mib', type=int, required=True)
    parser.add_argument('--lease-fd', type=int, required=True)
    args = parser.parse_args()
    try:
        policy = memory_policy(args.memory_budget_mib)
        actual = observe_process_memory()
        if actual['as_soft_bytes'] != policy['roles_bytes']['coordinator']:
            raise InvalidGit('COORDINATOR_MEMORY_LIMIT_NOT_ESTABLISHED')
        os.fstat(args.lease_fd)
        result = validate_local(args.repo, args.commit, args.prd, args.timeout, policy, args.lease_fd)
        print(json.dumps(result, ensure_ascii=True))
        return 0
    except MemoryError:
        os.write(1, MEMORY_FAILURE)
        return 1
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        print(json.dumps({'status': 'BLOCKED', 'error': str(error)}, ensure_ascii=True))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
