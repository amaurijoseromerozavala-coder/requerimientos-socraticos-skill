"""Check one historical RDD record's identity, not reviewer authenticity."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'docs/skill-audit/supervisor-pre-reap'
COMMIT = '3656381fb2ee299d543d5f798ebe079bb62812de'
PARENT = 'f51afa8fa04e8d4f687e8d88512c3a336b95e2eb'
TREE = 'eea8c615b5669c528f9d032e556f1b36897eaaae'
TARGET = 'sha256:f40b29c06a666f84009ae10333e966dcd63ff68835a4e6342d4cb6dc7425e364'
LINEAGE = 'review-d0f2c9baf4452a8e'
RESULT_HASH = 'sha256:ceb3635e71935b9707a4a90c7cee74159537de2788fa872910d9c9aa477d81d2'


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _pairs(items):
    result = {}
    for key, value in items:
        _require(key not in result, 'DUPLICATE_KEY')
        result[key] = value
    return result


def _read_json(path):
    raw = path.read_bytes()
    _require(len(raw) <= 16384, 'RECORD_SIZE_LIMIT')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs), raw


def verify_structure(record, marker):
    expected = {
        'schema': 'supervisor-pre-reap-rdd-closure/v1',
        'commit': COMMIT,
        'parent': PARENT,
        'candidate_tree': TREE,
        'target_identity': TARGET,
        'lineage': LINEAGE,
        'review_lens': 'review-reliability',
        'review_result_hash': RESULT_HASH,
        'review_findings': 0,
        'review_status': 'APPROVED',
        'acknowledgement': 'ACKNOWLEDGED',
        'reviewer_execution': 'NOT_INDEPENDENTLY_REPRODUCED',
        'record_provenance': 'AGENT_TRANSCRIPTION_OF_NATIVE_OUTPUT',
        'public_authentication': 'NOT_ESTABLISHED',
        'marker_sha256': '4a2b4fe06455ebedf5ba3d590cfdef23e7f2d6f859c77be2380c4a3aec0f40db',
    }
    _require(record == expected, 'RDD_RECORD_MISMATCH')
    _require(marker == {
        'schema': 'gentle-ai.review-terminal-consumption/v1',
        'repository': 'sha256:5eaf48f4b3eccf2cf14fb6fd223cdf4c6a521b058f5c6ef6dd36b308b6a1d00a',
        'target': TARGET,
        'lineage': LINEAGE,
    }, 'RDD_MARKER_MISMATCH')


def verify_git(root, record):
    _require(isinstance(root, Path), 'ROOT_PATH_REQUIRED')
    run = subprocess.run(
        ['git', 'show', '-s', '--format=%H %T %P', record['commit']],
        cwd=root, text=True, capture_output=True, timeout=5, check=True)
    _require(run.stdout.strip() == ' '.join((COMMIT, TREE, PARENT)),
             'RDD_COMMIT_TREE_MISMATCH')


def main():
    record, _ = _read_json(AUDIT / 'RDD-CIERRE.json')
    marker, raw = _read_json(AUDIT / 'terminal-consumption.json')
    verify_structure(record, marker)
    _require(hashlib.sha256(raw).hexdigest() == record['marker_sha256'],
             'RDD_MARKER_BYTES_MISMATCH')
    verify_git(ROOT, record)
    print('RDD_RECORD_COHERENT_AUTHENTICITY_NOT_ESTABLISHED')


if __name__ == '__main__':
    main()
