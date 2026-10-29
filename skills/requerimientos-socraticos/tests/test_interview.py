"""Synthetic contract fixtures, never evidence of a real agent conversation."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

def fixture():
    sources = [
        {'id': 'E1', 'kind': 'LOCAL', 'locator': 'synthetic source', 'verbatim_or_observation': 'Synthetic evidence; not actual execution.', 'observed_at': 'synthetic'},
        {'id': 'E2', 'kind': 'WEB_PRIMARY', 'locator': 'https://example.invalid/fixture', 'verbatim_or_observation': 'Synthetic source.', 'observed_at': 'synthetic'},
        {'id': 'E3', 'kind': 'HUMAN', 'locator': 'synthetic owner message', 'verbatim_or_observation': 'El alcance es reparar la skill.', 'observed_at': 'synthetic'},
    ]
    x = {'schema_version': '2.0.0', 'project': 'synthetic-contract-test', 'mode': 'INDEPENDENT_ASSISTANT_INTERVIEW', 'status': 'COMPLETE',
         'actors': [{'id': 'ARCH', 'role': 'INTERROGATOR', 'runtime_refs': ['synthetic-interrogator']}, {'id': 'ASST', 'role': 'ASSISTANT_RESPONDER', 'runtime_refs': ['synthetic-responder']}, {'id': 'HUMAN', 'role': 'HUMAN_OWNER', 'runtime_refs': []}],
         'sources': sources, 'topics': [], 'exchanges': [], 'research': [], 'active_question_id': None,
         'budget': {'max_exchanges_this_session': 4, 'stop_action': 'PAUSE_WITH_OPEN_TOPICS'}, 'limitations': ['Synthetic unit fixture; no real dialogue.']}
    for i in [1, 2]:
        q = {'id': f'Q{i}', 'by_actor': 'ARCH', 'to_actor': 'ASST', 'topic_id': f'D{i}', 'text': f'¿Qué evidencia resuelve la dimensión {i}?', 'dimension': f'dimensión {i}', 'answer_kind': 'EVIDENCE', 'required_evidence': ['Evidencia verificable']}
        a = {'id': f'A{i}', 'by_actor': 'ASST', 'question_id': q['id'], 'text': f'Respuesta sintética {i}; no diálogo real.', 'classification': 'FACT', 'source_ids': ['E1'], 'authoritative_quote': None}
        def rec(name, text): return {'path': name, 'format': 'PLAIN_TEXT', 'sha256': hashlib.sha256(text.encode()).hexdigest()}
        x['exchanges'].append({'question': q, 'answer': a, 'assessment': {'verdict': 'ANSWERED', 'rationale': 'Synthetic oracle.', 'remaining_gaps': [], 'resolved_by': None}, 'question_receipt': rec(f'q{i}.txt', q['text']), 'answer_receipt': rec(f'a{i}.txt', a['text'])})
        x['topics'].append({'id': f'D{i}', 'dimension': q['dimension'], 'material': True, 'applicable': True, 'status': 'COVERED', 'rationale': 'Synthetic evidence.', 'question_ids': [q['id']], 'source_ids': ['E1']})
    for n, kind in enumerate(['SKILL_DISCOVERY', 'SKILL_READ', 'MCP_DISCOVERY', 'MCP_QUERY', 'WEB_SEARCH', 'WEB_OPEN'], 1):
        x['research'].append({'id': f'RES{n}', 'kind': kind, 'status': 'OK', 'tool': 'synthetic', 'query_or_action': 'synthetic query', 'source_ids': ['E2' if kind == 'WEB_OPEN' else 'E1'], 'receipt_locator': f'research-{n}.txt', 'receipt_sha256': hashlib.sha256(b'synthetic receipt').hexdigest(), 'reason': 'Contract test only.'})
    return x

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('interview_validator', ROOT / 'scripts/validate_interview.py')
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def reject(self, change, code, data=None):
        x = copy.deepcopy(data or fixture()); change(x)
        with self.assertRaises(self.module.Invalid) as out:
            self.module.validate(x)
        self.assertEqual(code, out.exception.code, str(out.exception))

    def test_valid_bounded_interview(self): self.module.validate(fixture())
    def test_one_answer_is_not_total_coverage(self):
        def change(x): x['exchanges'].pop(); x['topics'][1].update(status='OPEN', question_ids=[])
        self.reject(change, 'UNCOVERED_MATERIAL_TOPIC')
    def test_unanswered_blocks_complete(self):
        self.reject(lambda x: x['exchanges'][1].update(answer=None, assessment=None, answer_receipt=None), 'UNANSWERED')
    def test_no_next_question_before_answer(self):
        self.reject(lambda x: x['exchanges'][0].update(answer=None, assessment=None, answer_receipt=None), 'ADVANCED_WITHOUT_ANSWER')
    def test_no_next_question_before_assessment(self):
        self.reject(lambda x: x['exchanges'][0].update(assessment=None), 'ADVANCED_WITHOUT_ASSESSMENT')
    def test_unknown_is_not_answered(self):
        self.reject(lambda x: x['exchanges'][0]['answer'].update(classification='UNKNOWN'), 'UNSUPPORTED_CLOSURE')
    def test_inference_is_not_confirmed_fact(self):
        self.reject(lambda x: x['exchanges'][0]['answer'].update(classification='INFERENCE'), 'UNSUPPORTED_CLOSURE')
    def test_assistant_cannot_invent_policy(self):
        self.reject(lambda x: x['exchanges'][0]['answer'].update(classification='USER_DECISION'), 'HUMAN_AUTHORITY_MISSING')
    def test_existing_literal_human_decision_can_be_cited(self):
        x=fixture();x['exchanges'][0]['question']['answer_kind']='HUMAN_DECISION';x['exchanges'][0]['answer'].update(classification='USER_DECISION',source_ids=['E3'],authoritative_quote='El alcance es reparar la skill.')
        self.module.validate(x)
    def test_false_quote_rejected(self):
        self.reject(lambda x: x['exchanges'][0]['answer'].update(classification='USER_DECISION',source_ids=['E3'],authoritative_quote='Autoriza instalar QA.'), 'HUMAN_AUTHORITY_MISSING')
    def test_duplicate_ids_rejected_before_index(self):
        self.reject(lambda x: x['sources'].append(dict(x['sources'][0])), 'DUPLICATE_ID')
    def test_dangling_source(self):
        self.reject(lambda x: x['exchanges'][0]['answer'].update(source_ids=['missing']), 'DANGLING_REFERENCE')
    def test_wrong_respondent(self):
        self.reject(lambda x: x['exchanges'][0]['answer'].update(by_actor='ARCH'), 'WRONG_RESPONDENT')
    def test_fake_independent_runtime(self):
        self.reject(lambda x: x['actors'][1].update(runtime_refs=['synthetic-interrogator']), 'INDEPENDENCE_MISSING')
    def test_unresolved_followup_rejected(self):
        self.reject(lambda x: x['exchanges'][0]['assessment'].update(verdict='INCOMPLETE',remaining_gaps=['budget'],resolved_by=None), 'UNRESOLVED_ANSWER')
    def test_followup_cannot_resolve_different_topic(self):
        self.reject(lambda x: x['exchanges'][0]['assessment'].update(verdict='INCOMPLETE',remaining_gaps=['gap'],resolved_by='Q2'), 'INVALID_RESOLUTION')
    def test_fake_covered_topic(self):
        self.reject(lambda x: x['topics'][0].update(question_ids=[],source_ids=[]), 'COVERAGE_WITHOUT_EVIDENCE')
    def test_web_requires_discovery_first(self):
        self.reject(lambda x: x['research'].insert(0,dict(x['research'][-1],id='EARLY_WEB')), 'RESEARCH_ORDER')
    def test_missing_web_exploration_blocks_complete(self):
        self.reject(lambda x: x.update(research=[r for r in x['research'] if not r['kind'].startswith('WEB_')]), 'RESEARCH_INCOMPLETE')
    def test_tool_unavailability_is_not_success(self):
        self.reject(lambda x: x['research'][-1].update(status='UNAVAILABLE'), 'RESEARCH_INCOMPLETE')
    def test_pause_remains_incomplete_but_valid(self):
        x=fixture();x['status']='PAUSED';x['topics'][1]['status']='OPEN';self.module.validate(x)
    def test_wait_state_matches_active_recipient(self):
        x=fixture();x['status']='WAITING_ASSISTANT';x['active_question_id']='Q2';x['exchanges'][1].update(answer=None,assessment=None,answer_receipt=None);self.module.validate(x)
        self.reject(lambda d:d.update(status='WAITING_USER'), 'WAIT_STATE_MISMATCH',x)
    def test_receipts_checked_not_just_declared(self):
        x=fixture()
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            for e in x['exchanges']:
                (base/e['question_receipt']['path']).write_text(e['question']['text'])
                (base/e['answer_receipt']['path']).write_text(e['answer']['text'])
            for event in x['research']:(base/event['receipt_locator']).write_text('synthetic receipt')
            self.module.validate(x,base)
            (base/'a1.txt').write_text('tampered')
            with self.assertRaises(self.module.Invalid) as err:self.module.validate(x,base)
            self.assertEqual(err.exception.code,'RECEIPT_MISMATCH')
    def test_research_receipt_missing_is_not_success(self):
        x=fixture()
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            for e in x['exchanges']:
                (base/e['question_receipt']['path']).write_text(e['question']['text'])
                (base/e['answer_receipt']['path']).write_text(e['answer']['text'])
            with self.assertRaises(self.module.Invalid) as err:self.module.validate(x,base)
            self.assertEqual(err.exception.code,'RESEARCH_RECEIPT_MISSING')

    def test_receipt_path_escape(self):
        x=fixture();x['exchanges'][0]['question_receipt']['path']='../outside.txt'
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(self.module.Invalid) as err:self.module.validate(x,Path(td))
            self.assertEqual(err.exception.code,'UNSAFE_PATH')
    def test_legacy_draft_still_valid_and_ready_loophole_closed(self):
        from jsonschema import Draft202012Validator
        s=json.loads((ROOT/'assets/prd.schema.json').read_text());d=json.loads((ROOT/'assets/example.prd.json').read_text());Draft202012Validator(s).validate(d)
        d['status']='READY';d['assurance']['formal_status']='PASS_BOUNDED';d['assurance']['checks']={k:'PASS' for k in d['assurance']['checks']}
        d['assurance']['rdd']={'mode':'ON','status':'NATIVE_PASS','receipt_locator':'SYNTHETIC-ONLY','candidate_identity':'SYNTHETIC-ONLY','independent_reviewer':'SYNTHETIC-ONLY'}
        d['assurance']['evidence']=[{'id':'E-test','candidate_sha256':d['assurance']['candidate_sha256'],'command_or_tool':'synthetic schema test','version':'1','cwd_or_url':'in-memory','observed_at':'synthetic','exit_code':0,'result':'PASS','output_locator':'synthetic only','scope_and_limits':'Not native evidence.'}]
        for f in d['candidate']['falsifiers']:f.update(status='NOT_REFUTED_UNDER_TEST',evidence_ids=['E-test'])
        errors=list(Draft202012Validator(s).iter_errors(d));self.assertTrue(errors)
        self.assertTrue(any('READY' in e.message for e in errors),errors)
    def stage_prd(self, base, paused=False):
        interview=fixture()
        if paused:interview['status']='PAUSED'
        for e in interview['exchanges']:
            (base/e['question_receipt']['path']).write_text(e['question']['text'])
            (base/e['answer_receipt']['path']).write_text(e['answer']['text'])
        design={'schema_version':'2.0.0','project':'synthetic-contract-test','status':'REVIEWED','proposals':[],'no_change_reason':'Synthetic fixture baseline needs no change.','source_ids':['E1'],'limitations':['Synthetic only.']}
        for event in interview['research']:(base/event['receipt_locator']).write_text('synthetic receipt')
        for name,obj in [('interview.json',interview),('design.json',design)]:
            (base/name).write_text(json.dumps(obj))
        prd=json.loads((ROOT/'assets/example.prd.json').read_text());prd['schema_version']='2.0.0';prd['project']=interview['project']
        for key,name in [('interview_ref','interview.json'),('design_proposals_ref','design.json')]:
            prd['candidate'][key]={'path':name,'sha256':hashlib.sha256((base/name).read_bytes()).hexdigest()}
        prd['assurance']['candidate_sha256']=hashlib.sha256(json.dumps(prd['candidate'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        (base/'prd.json').write_text(json.dumps(prd));return base/'prd.json'

    def prd_validator(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        import validate_prd
        return validate_prd

    def test_v2_dependency_hashes_and_receipts(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.stage_prd(Path(td));result=self.prd_validator().validate_prd(path);self.assertEqual(result['interview'],'COMPLETE')

    def test_changed_interview_invalidates_bound_prd(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.stage_prd(Path(td));(Path(td)/'interview.json').write_text('{}')
            with self.assertRaises(self.prd_validator().Invalid) as err:self.prd_validator().validate_prd(path)
            self.assertEqual(err.exception.code,'STALE_DEPENDENCY')

    def test_prd_ref_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.stage_prd(Path(td));x=json.loads(path.read_text());x['candidate']['interview_ref']['path']='../outside.json'
            x['assurance']['candidate_sha256']=hashlib.sha256(json.dumps(x['candidate'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();path.write_text(json.dumps(x))
            with self.assertRaises(self.prd_validator().Invalid) as err:self.prd_validator().validate_prd(path)
            self.assertEqual(err.exception.code,'UNSAFE_PATH')

    def test_stale_candidate_hash_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.stage_prd(Path(td));x=json.loads(path.read_text());x['candidate']['scope']='Changed without revalidation';path.write_text(json.dumps(x))
            with self.assertRaises(self.prd_validator().Invalid) as err:self.prd_validator().validate_prd(path)
            self.assertEqual(err.exception.code,'STALE_CANDIDATE')

    def set_synthetic_ready(self,path):
        x=json.loads(path.read_text());x['status']='READY';a=x['assurance'];a['formal_status']='PASS_BOUNDED';a['checks']={k:'PASS' for k in a['checks']}
        a['rdd']={'mode':'ON','status':'NATIVE_PASS','receipt_locator':'SYNTHETIC-NOT-REAL-APPROVAL','candidate_identity':'SYNTHETIC','independent_reviewer':'SYNTHETIC'}
        a['evidence']=[{'id':'E-test','candidate_sha256':a['candidate_sha256'],'command_or_tool':'synthetic contract fixture','version':'1','cwd_or_url':'in-memory','observed_at':'synthetic','exit_code':0,'result':'PASS','output_locator':'synthetic only','scope_and_limits':'Not an actual native RDD receipt.'}]
        for f in x['candidate']['falsifiers']:f.update(status='NOT_REFUTED_UNDER_TEST',evidence_ids=['E-test'])
        a['candidate_sha256']=hashlib.sha256(json.dumps(x['candidate'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        for evidence in a['evidence']:evidence['candidate_sha256']=a['candidate_sha256']
        path.write_text(json.dumps(x))

    def test_cli_rejects_ready_with_paused_interview(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.stage_prd(Path(td),paused=True);self.set_synthetic_ready(path)
            p=subprocess.run([sys.executable,str(ROOT/'scripts/validate_prd.py'),str(path)],capture_output=True,text=True)
            self.assertEqual(p.returncode,1,p.stdout);self.assertIn('INTERROGATION_INCOMPLETE',p.stdout)

    def test_cli_complete_record_is_positive_integrity_control(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.stage_prd(Path(td));self.set_synthetic_ready(path)
            p=subprocess.run([sys.executable,str(ROOT/'scripts/validate_prd.py'),str(path)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout);self.assertEqual(json.loads(p.stdout)['interview'],'COMPLETE')

    def test_unanswered_question_cannot_be_addressed_to_self(self):
        x=fixture();x['status']='WAITING_ASSISTANT';x['active_question_id']='Q2';x['exchanges'][1].update(answer=None,assessment=None,answer_receipt=None);x['exchanges'][1]['question']['to_actor']='ARCH'
        with self.assertRaises(self.module.Invalid) as err:self.module.validate(x)
        self.assertEqual(err.exception.code,'WRONG_RESPONDENT')

    def test_material_scope_cannot_be_dismissed_without_owner(self):
        self.reject(lambda x:x['topics'][1].update(status='NOT_APPLICABLE',applicable=False,question_ids=[],source_ids=['E1']), 'HUMAN_AUTHORITY_MISSING')

    def test_false_applicability_cannot_hide_open_material_topic(self):
        self.reject(lambda x:x['topics'][1].update(applicable=False,status='OPEN'), 'APPLICABILITY_STATUS_MISMATCH')

    def test_false_applicability_cannot_keep_covered_status(self):
        self.reject(lambda x:x['topics'][1].update(applicable=False,status='COVERED'), 'APPLICABILITY_STATUS_MISMATCH')

    def test_prd_cannot_use_foreign_project_interview(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.stage_prd(Path(td));x=json.loads(path.read_text());x['project']='foreign-project';path.write_text(json.dumps(x))
            with self.assertRaises(self.prd_validator().Invalid) as err:self.prd_validator().validate_prd(path)
            self.assertEqual(err.exception.code,'PROJECT_MISMATCH')

    def test_design_cannot_use_foreign_project_sources(self):
        d={'schema_version':'2.0.0','project':'foreign-project','status':'PENDING','proposals':[],'no_change_reason':None,'source_ids':['E1'],'limitations':['synthetic']}
        with self.assertRaises(self.module.Invalid) as err:self.module.validate_design(d,fixture())
        self.assertEqual(err.exception.code,'PROJECT_MISMATCH')

    def followup_fixture(self):
        x=fixture();x['topics']=x['topics'][:1];x['topics'][0]['question_ids']=['Q1','Q2'];x['exchanges'][1]['question']['topic_id']='D1'
        x['exchanges'][0]['assessment'].update(verdict='INCOMPLETE',remaining_gaps=['dimension 1'],resolved_by='Q2')
        return x

    def test_same_topic_different_dimension_does_not_resolve(self):
        with self.assertRaises(self.module.Invalid) as err:self.module.validate(self.followup_fixture())
        self.assertEqual(err.exception.code,'INVALID_RESOLUTION')

    def test_same_topic_same_dimension_can_resolve(self):
        x=self.followup_fixture();x['exchanges'][1]['question']['dimension']=x['exchanges'][0]['question']['dimension'];x['exchanges'][1]['question']['text']=x['exchanges'][0]['question']['text'];x['exchanges'][1]['question_receipt']['sha256']=hashlib.sha256(x['exchanges'][1]['question']['text'].encode()).hexdigest();self.module.validate(x)

    def test_prd_design_can_reference_its_requirement(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.stage_prd(Path(td));base=Path(td);design=json.loads((base/'design.json').read_text());design['no_change_reason']=None
            design['proposals']=[{'id':'P1','problem':'synthetic','requirement_or_topic_ids':['R1'],'alternatives':[{'id':'B','description':'baseline','source_ids':['E1'],'tradeoffs':['x']},{'id':'A','description':'alternative','source_ids':['E1'],'tradeoffs':['y']}],'criteria':['cost'],'hypothesis':'improves clarity','falsifier':'counterexample','status':'PROPOSED','decision_source_ids':[]}]
            (base/'design.json').write_text(json.dumps(design));prd=json.loads(path.read_text());prd['candidate']['design_proposals_ref']['sha256']=hashlib.sha256((base/'design.json').read_bytes()).hexdigest();prd['assurance']['candidate_sha256']=hashlib.sha256(json.dumps(prd['candidate'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();path.write_text(json.dumps(prd))
            result=self.prd_validator().validate_prd(path);self.assertEqual(result['design'],'REVIEWED')

    def test_no_empty_design_review(self):
        d={'schema_version':'2.0.0','project':'synthetic-contract-test','status':'REVIEWED','proposals':[],'no_change_reason':None,'source_ids':[],'limitations':['synthetic']}
        with self.assertRaises(self.module.Invalid) as err:self.module.validate_design(d,fixture())
        self.assertEqual(err.exception.code,'EMPTY_DESIGN_REVIEW')
    def test_design_acceptance_needs_human_source(self):
        d={'schema_version':'2.0.0','project':'synthetic-contract-test','status':'REVIEWED','proposals':[{'id':'P1','problem':'synthetic','requirement_or_topic_ids':['D1'],'alternatives':[{'id':'B','description':'baseline','source_ids':['E1'],'tradeoffs':['x']},{'id':'A','description':'alternative','source_ids':['E1'],'tradeoffs':['y']}],'criteria':['cost'],'hypothesis':'reduces cost','falsifier':'observed increase','status':'ACCEPTED','decision_source_ids':['E1']}],'no_change_reason':None,'source_ids':['E1'],'limitations':['synthetic']}
        with self.assertRaises(self.module.Invalid) as err:self.module.validate_design(d,fixture())
        self.assertEqual(err.exception.code,'HUMAN_AUTHORITY_MISSING')

if __name__=='__main__': unittest.main(verbosity=2)
