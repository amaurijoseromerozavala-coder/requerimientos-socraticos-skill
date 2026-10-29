#!/usr/bin/env python3
"""Read-only validation of interrogation records; never infers human intent."""
import argparse
from safe_io import read_regular
from document_source import FilesystemSource, Invalid, safe_file
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

def need(condition, code, detail):
    if not condition:
        raise Invalid(code, detail)

def structural(data, filename):
    schema = json.loads(read_regular(ROOT / 'assets', filename).decode('utf-8'))
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: str(list(e.path)))
    need(not errors, 'SCHEMA', str(errors[0]) if errors else '')

def unique(items, key='id'):
    ids = [item[key] for item in items]
    need(len(ids) == len(set(ids)), 'DUPLICATE_ID', ids)

def _receipt_bytes(source, relative, missing_code, detail):
    try:
        return source.read(relative)
    except (FileNotFoundError, NotADirectoryError, IsADirectoryError):
        raise Invalid(missing_code, detail) from None
    except ValueError as err:
        if str(err) == 'NOT_REGULAR_FILE':
            raise Invalid(missing_code, detail) from None
        raise

def receipt(base, entry, expected, source=None):
    source = source if source is not None else FilesystemSource(base)
    raw = _receipt_bytes(source, entry['path'], 'RECEIPT_MISSING', entry['path'])
    text = raw.decode('utf-8') if entry['format'] == 'PLAIN_TEXT' else json.loads(raw)['question']
    need(hashlib.sha256(raw).hexdigest() == entry['sha256'] and text == expected, 'RECEIPT_MISMATCH', entry['path'])

def validate(doc, base=None, source=None):
    if source is None and base is not None:
        source = FilesystemSource(base)
    structural(doc, 'interview.schema.json')
    questions = [e['question'] for e in doc['exchanges']]
    answers = [e['answer'] for e in doc['exchanges'] if e['answer'] is not None]
    for collection in [doc['actors'], doc['sources'], doc['topics'], questions, answers, doc['research']]:
        unique(collection)
    all_ids = [item['id'] for collection in [doc['actors'], doc['sources'], doc['topics'], questions, answers, doc['research']] for item in collection]
    need(len(all_ids) == len(set(all_ids)), 'DUPLICATE_ID', 'IDs collide between collections')
    actors = {a['id']: a for a in doc['actors']}
    sources = {s['id']: s for s in doc['sources']}
    topics = {t['id']: t for t in doc['topics']}
    question_index = {q['id']: i for i, q in enumerate(questions)}
    closed = doc['status'] == 'COMPLETE'
    def source_refs(ids):
        need(set(ids) <= set(sources), 'DANGLING_REFERENCE', sorted(set(ids) - set(sources)))
    if doc['mode'] == 'INDEPENDENT_ASSISTANT_INTERVIEW':
        interrogators = [a for a in doc['actors'] if a['role'] == 'INTERROGATOR']
        responders = [a for a in doc['actors'] if a['role'] == 'ASSISTANT_RESPONDER']
        need(len(interrogators) == 1 and len(responders) == 1, 'INDEPENDENCE_MISSING', 'Two distinct roles required')
        i, r = interrogators[0], responders[0]
        need(i['runtime_refs'] and r['runtime_refs'] and not set(i['runtime_refs']) & set(r['runtime_refs']), 'INDEPENDENCE_MISSING', 'Runtime references missing or shared')
    pending = []
    for i, exchange in enumerate(doc['exchanges']):
        q, a, assessment = exchange['question'], exchange['answer'], exchange['assessment']
        need(q['by_actor'] in actors and q['to_actor'] in actors and q['topic_id'] in topics, 'DANGLING_REFERENCE', q['id'])
        need(actors[q['by_actor']]['role'] == 'INTERROGATOR', 'WRONG_INTERROGATOR', q['id'])
        need(actors[q['to_actor']]['role'] in ['ASSISTANT_RESPONDER', 'HUMAN_OWNER'], 'WRONG_RESPONDENT', q['id'])
        if doc['mode'] == 'SINGLE_ASSISTANT_USER_INTERVIEW':
            need(actors[q['to_actor']]['role'] == 'HUMAN_OWNER', 'WRONG_RESPONDENT', q['id'])
        if a is None:
            need(i == len(doc['exchanges']) - 1, 'ADVANCED_WITHOUT_ANSWER', q['id'])
            need(assessment is None and exchange['answer_receipt'] is None, 'ASSESSMENT_BEFORE_ANSWER', q['id'])
            pending.append(q['id'])
        else:
            need(a['by_actor'] == q['to_actor'] and a['question_id'] == q['id'], 'WRONG_RESPONDENT', q['id'])
            need(actors[a['by_actor']]['role'] in ['ASSISTANT_RESPONDER', 'HUMAN_OWNER'], 'WRONG_RESPONDENT', q['id'])
            source_refs(a['source_ids'])
            if a['classification'] == 'USER_DECISION':
                quote = a['authoritative_quote']
                need(quote and any(sources[s]['kind'] == 'HUMAN' and quote in sources[s]['verbatim_or_observation'] for s in a['source_ids']), 'HUMAN_AUTHORITY_MISSING', q['id'])
            if assessment is None:
                need(i == len(doc['exchanges']) - 1, 'ADVANCED_WITHOUT_ASSESSMENT', q['id'])
                need(not closed, 'UNASSESSED', q['id'])
            else:
                if assessment['verdict'] == 'ANSWERED':
                    need(not assessment['remaining_gaps'], 'UNRESOLVED_ANSWER', q['id'])
                    allowed = ['FACT', 'CONSTRAINT', 'USER_DECISION'] if q['answer_kind'] == 'EVIDENCE' else ['USER_DECISION'] if q['answer_kind'] == 'HUMAN_DECISION' else ['FACT', 'CONSTRAINT', 'USER_DECISION', 'INFERENCE', 'HYPOTHESIS']
                    need(a['classification'] in allowed and a['source_ids'], 'UNSUPPORTED_CLOSURE', q['id'])
                elif assessment['resolved_by'] is not None:
                    later = assessment['resolved_by']
                    need(later in question_index and question_index[later] > i, 'INVALID_RESOLUTION', q['id'])
                    successor = doc['exchanges'][question_index[later]]
                    need(successor['question']['topic_id'] == q['topic_id'] and successor['question']['dimension'] == q['dimension'] and successor['assessment'] and successor['assessment']['verdict'] == 'ANSWERED', 'INVALID_RESOLUTION', q['id'])
                else:
                    need(not closed, 'UNRESOLVED_ANSWER', q['id'])
            need(exchange['answer_receipt'] is not None, 'RECEIPT_MISSING', q['id'])
        if source is not None:
            receipt(base, exchange['question_receipt'], q['text'], source=source)
            if a is not None:
                receipt(base, exchange['answer_receipt'], a['text'], source=source)
    need(not closed or not pending, 'UNANSWERED', pending)
    if pending:
        need(doc['active_question_id'] == pending[0], 'ACTIVE_QUESTION_MISMATCH', pending)
    else:
        need(doc['active_question_id'] is None, 'ACTIVE_QUESTION_MISMATCH', doc['active_question_id'])
    if doc['status'] in ['WAITING_USER', 'WAITING_ASSISTANT']:
        need(len(pending) == 1, 'WAIT_STATE_MISMATCH', 'No single pending question')
        target = actors[questions[-1]['to_actor']]['role']
        need((doc['status'] == 'WAITING_USER') == (target == 'HUMAN_OWNER'), 'WAIT_STATE_MISMATCH', target)
    for topic in doc['topics']:
        need(topic['applicable'] == (topic['status'] != 'NOT_APPLICABLE'), 'APPLICABILITY_STATUS_MISMATCH', topic['id'])
        source_refs(topic['source_ids'])
        need(set(topic['question_ids']) <= set(question_index), 'DANGLING_REFERENCE', topic['id'])
        need(all(questions[question_index[q]]['topic_id'] == topic['id'] for q in topic['question_ids']), 'TOPIC_MISMATCH', topic['id'])
        if closed and topic['material'] and topic['applicable']:
            need(topic['status'] == 'COVERED', 'UNCOVERED_MATERIAL_TOPIC', topic['id'])
        if topic['status'] in ['COVERED', 'NOT_APPLICABLE']:
            need(topic['question_ids'] or topic['source_ids'], 'COVERAGE_WITHOUT_EVIDENCE', topic['id'])
        if topic['status'] == 'NOT_APPLICABLE':
            need(not topic['applicable'] and topic['source_ids'], 'COVERAGE_WITHOUT_EVIDENCE', topic['id'])
            if topic['material']:
                need(any(sources[s]['kind'] == 'HUMAN' for s in topic['source_ids']), 'HUMAN_AUTHORITY_MISSING', topic['id'])
        if closed and topic['status'] == 'COVERED':
            for qid in topic['question_ids']:
                e = doc['exchanges'][question_index[qid]]
                need(e['answer'] is not None and e['assessment'] is not None, 'COVERAGE_WITHOUT_EVIDENCE', topic['id'])
    kinds = []
    for event in doc['research']:
        source_refs(event['source_ids'])
        if event['kind'] in ['WEB_SEARCH', 'WEB_OPEN']:
            need('SKILL_DISCOVERY' in kinds and 'SKILL_READ' in kinds and 'MCP_DISCOVERY' in kinds, 'RESEARCH_ORDER', event['id'])
        if event['kind'] == 'MCP_QUERY':
            need('MCP_DISCOVERY' in kinds, 'RESEARCH_ORDER', event['id'])
        if event['kind'] == 'WEB_OPEN' and event['status'] == 'OK':
            need(any(sources[s]['kind'] == 'WEB_PRIMARY' for s in event['source_ids']), 'RESEARCH_INCOMPLETE', 'Web read lacks primary source binding')
        if source is not None:
            raw = _receipt_bytes(source, event['receipt_locator'], 'RESEARCH_RECEIPT_MISSING', event['id'])
            need(hashlib.sha256(raw).hexdigest() == event['receipt_sha256'], 'RESEARCH_RECEIPT_MISMATCH', event['id'])
        if event['status'] == 'OK':
            kinds.append(event['kind'])
    if closed:
        need({'SKILL_DISCOVERY', 'SKILL_READ', 'MCP_DISCOVERY', 'MCP_QUERY', 'WEB_SEARCH', 'WEB_OPEN'} <= set(kinds), 'RESEARCH_INCOMPLETE', kinds)
        need(any(s['kind'] == 'WEB_PRIMARY' for s in sources.values()), 'RESEARCH_INCOMPLETE', 'No primary web source')
    return {'status': doc['status'], 'questions': len(questions), 'pending': pending, 'semantic_validation': 'PASS_WITHIN_DECLARED_RECORD', 'receipt_files_checked': source is not None}

def validate_design(doc, interview, requirement_ids=()):
    structural(doc, 'design-proposals.schema.json')
    need(doc['project'] == interview['project'], 'PROJECT_MISMATCH', 'Design and interview projects differ')
    sources = {s['id']: s for s in interview['sources']}
    topics = {t['id'] for t in interview['topics']} | set(requirement_ids)
    unique(doc['proposals'])
    need(set(doc['source_ids']) <= set(sources), 'DANGLING_REFERENCE', 'design sources')
    if doc['status'] == 'REVIEWED' and not doc['proposals']:
        need(doc['no_change_reason'] and doc['source_ids'], 'EMPTY_DESIGN_REVIEW', 'No proposals or evidence-backed reason')
    for p in doc['proposals']:
        unique(p['alternatives'])
        need(set(p['requirement_or_topic_ids']) <= topics, 'DANGLING_REFERENCE', p['id'])
        ids = p['decision_source_ids'] + [s for alternative in p['alternatives'] for s in alternative['source_ids']]
        need(set(ids) <= set(sources), 'DANGLING_REFERENCE', p['id'])
        if p['status'] in ['ACCEPTED', 'REJECTED']:
            need(any(sources[s]['kind'] == 'HUMAN' for s in p['decision_source_ids']), 'HUMAN_AUTHORITY_MISSING', p['id'])
    return {'status': doc['status'], 'proposals': len(doc['proposals'])}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('interview', type=Path)
    parser.add_argument('--design', type=Path)
    args = parser.parse_args()
    try:
        doc = json.loads(read_regular(args.interview.parent, args.interview.name).decode('utf-8'))
        result = validate(doc, args.interview.parent)
        if args.design:
            result['design'] = validate_design(json.loads(read_regular(args.design.parent, args.design.name).decode('utf-8')), doc)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (Invalid, OSError, ValueError, KeyError) as err:
        print(json.dumps({'status': 'INVALID', 'error': str(err)}, ensure_ascii=False))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
