"""Render a provisional Spanish EARS universal sentence from checked RS3 IR.

The wording communicates an explicit Boolean relation. It does not infer the
human meaning of the source text or grant an operational permission.
"""
from candidate_ir import check_candidate


def _label(name):
    if name == 'production_ready':
        return 'elegible para revisión documental'
    return name


def render_draft(candidate):
    checked = check_candidate(candidate)
    result = {'status': checked['status'], 'authority': 'NOT_GRANTED',
              'execution_authorized': False, 'scope': 'DOCUMENTARY_ONLY',
              'source_ref': checked['source_ref'],
              'source_sha256': checked['source_sha256'],
              'meaning': ('REVIEW_ELIGIBLE_DOCUMENTARY_ONLY'
                          if 'production_ready' in (candidate['subject'], candidate['condition'])
                          else None),
              'pattern': None, 'text': None, 'ast': checked['ast']}
    if checked['status'] != 'PROPOSED' or checked['ast'] is None:
        return result
    subject, condition = _label(candidate['subject']), _label(candidate['condition'])
    if candidate['kind'] == 'NECESSARY_CONDITION':
        meaning = f'si «{subject}» es verdadero, entonces «{condition}» es verdadero.'
    elif candidate['kind'] == 'SUFFICIENT_CONDITION':
        meaning = f'si «{condition}» es verdadero, entonces «{subject}» es verdadero.'
    else:
        meaning = f'«{subject}» y «{condition}» tienen el mismo valor de verdad.'
    result['pattern'] = 'UNIVERSAL'
    result['text'] = 'El sistema deberá cumplir: ' + meaning
    return result
