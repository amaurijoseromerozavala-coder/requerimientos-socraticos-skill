#!/usr/bin/env python3
"""Validate PRD structure and its hash-bound interview/design dependencies."""
import argparse
from document_source import FilesystemSource
import hashlib
import json
from pathlib import Path, PurePosixPath
from validate_interview import ROOT, Invalid, need, safe_file, structural, validate, validate_design

def validate_prd(path, source=None):
    source = source if source is not None else FilesystemSource(path.parent)
    prd = json.loads(source.read(path.name).decode('utf-8'))
    structural(prd, 'prd.schema.json')
    candidate = prd['candidate']
    actual = hashlib.sha256(json.dumps(candidate, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    need(actual == prd['assurance']['candidate_sha256'], 'STALE_CANDIDATE', path.name)
    if prd['schema_version'] == '1.0.0':
        return {'status': prd['status'], 'legacy': True, 'warning': 'No v2 interrogation proven; migrate before READY.'}
    documents = {}
    for key in ['interview_ref', 'design_proposals_ref']:
        ref = candidate[key]
        raw = source.read(ref['path'])
        need(hashlib.sha256(raw).hexdigest() == ref['sha256'], 'STALE_DEPENDENCY', key)
        documents[key] = json.loads(raw)
    interview, design = documents['interview_ref'], documents['design_proposals_ref']
    need(interview['project'] == prd['project'], 'PROJECT_MISMATCH', 'PRD and interview projects differ')
    validate(interview, source=source.scope(PurePosixPath(candidate['interview_ref']['path']).parent))
    validate_design(design, interview, [r['id'] for r in candidate['requirements']])
    if prd['status'] == 'READY':
        need(interview['status'] == 'COMPLETE' and design['status'] == 'REVIEWED', 'INTERROGATION_INCOMPLETE', prd['status'])
        need(not any(p['status'] == 'EVIDENCE_PENDING' for p in design['proposals']), 'DESIGN_EVIDENCE_PENDING', prd['status'])
    return {'status': prd['status'], 'interview': interview['status'], 'design': design['status'], 'limits': 'Validates declared records and retained files, not truth or LLM compliance.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prd', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(validate_prd(args.prd), ensure_ascii=False))
        return 0
    except (Invalid, OSError, ValueError, KeyError) as err:
        print(json.dumps({'status': 'INVALID', 'error': str(err)}, ensure_ascii=False))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
