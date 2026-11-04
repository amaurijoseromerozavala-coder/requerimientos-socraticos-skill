#!/usr/bin/env python3
"""Analyze a bounded, explicit Boolean model; never execute model content."""
import argparse
import itertools
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import time

from safe_io import read_regular
from json_preflight import preflight_json
from analyze_logic import artifact_identity
from memory_budget import observe_process_memory
from formal_queries import EquivalenceScope, QueryContext, QueryKind
from witness_validation import verify_assignment
from gap_scenario import build_gap_interpretation
from gap_region import sample_gap_region

MEMORY_FAILURE = b'{"status":"INCONCLUSIVE","error":{"code":"MEMORY_BUDGET_EXCEEDED","message":"Worker observed an allocation failure; no model results are reported."}}\n'

MAX_BYTES = 262144
MAX_NODES = 4096
MAX_DEPTH = 32
MAX_ITEMS = 128
NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_]{0,63}$')

class InputError(ValueError):
    pass

def unique_object(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise InputError('duplicate JSON key: ' + k)
        result[k] = v
    return result

def keys(obj, expected):
    if type(obj) is not dict or set(obj) != set(expected):
        raise InputError('unexpected or missing fields')

def name(value):
    if type(value) is not str or not NAME.fullmatch(value):
        raise InputError('invalid name or ID')
    return value

def validate(data):
    keys(data, ('inputs', 'outputs', 'domain', 'rules', 'properties'))
    for field in ('inputs', 'outputs', 'rules', 'properties'):
        if type(data[field]) is not list or len(data[field]) > MAX_ITEMS:
            raise InputError('invalid list or list limit: ' + field)
    variables = [name(n) for n in data['inputs'] + data['outputs']]
    if len(variables) > 32 or len(set(variables)) != len(variables):
        raise InputError('variables must be unique and total at most 32')
    ins, allvars = set(data['inputs']), set(variables)
    ids, count = set(), 0
    def expr(node, allowed, depth=1):
        nonlocal count
        count += 1
        if count > MAX_NODES or depth > MAX_DEPTH:
            raise InputError('expression node or depth limit')
        if type(node) is bool:
            return
        if type(node) is not dict:
            raise InputError('expression must be boolean or AST object')
        if set(node) == {'var'}:
            variable = name(node['var'])
            if variable not in allvars:
                raise InputError('UNKNOWN_VARIABLE')
            if variable not in allowed:
                raise InputError('WRONG_VARIABLE_ROLE')
            return
        keys(node, ('op', 'args'))
        op, args = node['op'], node['args']
        if type(op) is not str or type(args) is not list:
            raise InputError('invalid operator or arguments')
        if op not in ('and', 'or', 'not', 'implies', 'eq'):
            raise InputError('unsupported operator')
        if (op in ('not', 'implies', 'eq') and len(args) != {'not': 1, 'implies': 2, 'eq': 2}[op]) or (op in ('and', 'or') and not 2 <= len(args) <= MAX_ITEMS):
            raise InputError('invalid operator arity')
        for child in args:
            expr(child, allowed, depth + 1)
    expr(data['domain'], ins)
    for item in data['rules']:
        keys(item, ('id', 'guard', 'response'))
        ident = name(item['id'])
        if ident in ids: raise InputError('duplicate ID')
        ids.add(ident)
        expr(item['guard'], ins); expr(item['response'], allvars)
    for item in data['properties']:
        keys(item, ('id', 'expression'))
        ident = name(item['id'])
        if ident in ids: raise InputError('duplicate ID')
        ids.add(ident)
        expr(item['expression'], allvars)
    return count

def analyze(data, z3, seconds, want_table, deadline, comparison=None, gap_samples=0):
    nodes = validate(data)
    context = QueryContext(data, z3)
    variables = context.variables
    domain = context.domain
    obligations = context.obligations
    covered = context.covered
    feasible_output = context.feasible_output
    def check(formula, witness_names=()):
        remaining = deadline - time.monotonic()
        if remaining < .001:
            return {'status': 'UNKNOWN', 'reason': 'total time budget exhausted'}
        solver = z3.Solver()
        solver.set(timeout=max(1, min(1000, int(remaining * 1000))))
        solver.add(formula)
        answer = solver.check()
        if answer == z3.unknown:
            return {'status': 'UNKNOWN', 'reason': solver.reason_unknown()}
        result = {'status': str(answer).upper()}
        if answer == z3.sat and witness_names:
            model = solver.model()
            witness = {n: z3.is_true(model.eval(variables[n], model_completion=True))
                       for n in witness_names}
            witness_check = verify_assignment(formula, witness, witness_names,
                                              variables, z3, deadline)
            if witness_check != 'VERIFIED':
                return {'status': 'UNKNOWN', 'reason': 'witness recheck ' + witness_check}
            result['witness'] = witness
            result['witness_check'] = witness_check
            result['witness_origin'] = 'MODEL_COMPLETION_APPLIED'
        return result
    inputs = data['inputs']
    queries = {kind.value: check(context.formula(kind),
                                  list(variables) if kind is QueryKind.RULE_CONSISTENCY else inputs)
               for kind in QueryKind}
    validity = {'SAT': 'VALID', 'UNSAT': 'INVALID', 'UNKNOWN': 'UNKNOWN'}[queries['domain']['status']]
    props = []
    for p in data['properties']:
        counterexample = check(z3.And(domain, obligations,
                                      z3.Not(context.compile_expr(p['expression']))), list(variables))
        basis = queries['rule_consistency']['status']
        if basis == 'UNSAT': consequence = 'VACUOUS'
        elif basis == 'UNKNOWN' or counterexample['status'] == 'UNKNOWN': consequence = 'UNKNOWN'
        elif counterexample['status'] == 'SAT': consequence = 'NOT_ENTAILED'
        else: consequence = 'ENTAILED'
        props.append({'id': p['id'], 'interpretation': 'Consequence of model rules within domain; not implementation verification.',
                      'consequence': consequence, 'counterexample': counterexample})
    result = {'domain_validity': validity, 'queries': queries, 'properties': props,
              'limits': {'variables': len(variables), 'ast_nodes': nodes, 'max_variables': 32, 'max_ast_nodes': MAX_NODES,
                         'max_depth': MAX_DEPTH, 'max_input_bytes': MAX_BYTES, 'total_seconds': seconds, 'per_query_seconds': 1},
              'scope': 'Results concern the supplied Boolean model only; they do not verify implementation, hardware, or human meaning.'}
    result['gap_region'] = sample_gap_region(data, context, z3, deadline, gap_samples)
    if comparison is not None:
        left_id, right_id, scope = comparison
        basis = (check(context.equivalence_basis(left_id, right_id, scope))
                 if scope is EquivalenceScope.CONTEXTUAL else {'status': 'NOT_APPLICABLE'})
        if basis['status'] == 'UNSAT':
            query = {'status': 'NOT_RUN', 'reason': 'context has no feasible assignment'}
            interpretation = 'VACUOUS_CONTEXT'
        elif basis['status'] == 'UNKNOWN':
            query = {'status': 'NOT_RUN', 'reason': 'context basis unresolved'}
            interpretation = 'INCONCLUSIVE'
        else:
            query = check(context.equivalence_formula(left_id, right_id, scope),
                          list(variables))
            interpretation = ({'SAT': ('DIFFERENT_ABSOLUTELY' if scope is EquivalenceScope.ABSOLUTE
                                        else 'DIFFERENT_WITHIN_CONTEXT'),
                               'UNSAT': ('EQUIVALENT_ABSOLUTELY' if scope is EquivalenceScope.ABSOLUTE
                                         else 'EQUIVALENT_WITHIN_CONTEXT'),
                               'UNKNOWN': 'INCONCLUSIVE'}[query['status']])
        result['equivalence'] = {'left_id': left_id, 'right_id': right_id,
                                 'scope': scope.value, 'basis': basis, 'query': query,
                                 'interpretation': interpretation,
                                 'limitation': 'Equivalence concerns two supplied rule clauses within the stated Boolean scope only.'}
    if want_table:
        if len(inputs) > 12:
            result['table'] = {'status': 'NOT_RUN', 'reason': 'more than 12 inputs'}
        else:
            table = {'status': 'EXACT', 'possible_rows': 2 ** len(inputs), 'rows_examined': 0,
                     'feasible_inputs': 0, 'covered_inputs': 0, 'inputs_without_output': 0}
            for bits in itertools.product((False, True), repeat=len(inputs)):
                fixed = z3.And(*[variables[n] == b for n, b in zip(inputs, bits)])
                d = check(z3.And(domain, fixed))
                if d['status'] == 'UNKNOWN': table['status'] = 'INCOMPLETE'; break
                if d['status'] == 'SAT':
                    c = check(z3.And(domain, fixed, covered))
                    n = check(z3.And(domain, fixed, z3.Not(feasible_output)))
                    if 'UNKNOWN' in (c['status'], n['status']): table['status'] = 'INCOMPLETE'; break
                    table['feasible_inputs'] += 1
                    table['covered_inputs'] += c['status'] == 'SAT'
                    table['inputs_without_output'] += n['status'] == 'SAT'
                table['rows_examined'] += 1
            if table['status'] == 'EXACT' and table['feasible_inputs']:
                table['coverage'] = {'metric': 'GUARD_ACTIVATION_COVERAGE', 'numerator': table['covered_inputs'], 'denominator': table['feasible_inputs']}
            result['table'] = table
    return result

class Parser(argparse.ArgumentParser):
    def error(self, message): raise InputError(message)

def main():
    try:
        parser = Parser(description=__doc__)
        parser.add_argument('input'); parser.add_argument('--timeout', type=float, default=5.0)
        parser.add_argument('--table', action='store_true')
        parser.add_argument('--gap-samples', type=int, default=0)
        parser.add_argument('--compare-left')
        parser.add_argument('--compare-right')
        parser.add_argument('--compare-scope', choices=('absolute', 'contextual'))
        args = parser.parse_args()
        comparison_values = (args.compare_left, args.compare_right, args.compare_scope)
        if any(value is not None for value in comparison_values) and not all(
                value is not None for value in comparison_values):
            raise InputError('QUERY_TEMPLATE_MISMATCH')
        comparison = ((args.compare_left, args.compare_right,
                       EquivalenceScope(args.compare_scope))
                      if args.compare_scope is not None else None)
        if not math.isfinite(args.timeout) or not 0 < args.timeout <= 30:
            raise InputError('timeout must be greater than 0 and at most 30 seconds')
        if not 0 <= args.gap_samples <= 16:
            raise InputError('gap samples must be between 0 and 16')
        started = time.monotonic()
        deadline = started + args.timeout
        path = Path(args.input).absolute()
        raw = read_regular(path.parent, path.name, MAX_BYTES)
        preflight_json(raw, max_bytes=MAX_BYTES)
        data = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(InputError('non-finite JSON number')))
        validate(data)
        try:
            import z3
        except ImportError:
            print(json.dumps({'error': {'code': 'SOLVER_UNAVAILABLE', 'message': 'z3-solver is unavailable'}}))
            return 2
        try:
            result = analyze(data, z3, args.timeout, args.table, deadline,
                             comparison, args.gap_samples)
            result['provenance'] = {'model_sha256': hashlib.sha256(raw).hexdigest(),
                                    'z3_version': z3.get_version_string(),
                                    'z3_module': artifact_identity(z3.__file__),
                                    'elapsed_seconds': time.monotonic() - started,
                                    'note': 'Hash identifies supplied bytes; it does not establish semantic correctness.'}
            result['gap_interpretation'] = build_gap_interpretation(
                data, result['queries']['gap'], result['provenance']['model_sha256'])
            region = result['gap_region']
            packets = [build_gap_interpretation(
                data, sample, result['provenance']['model_sha256'])
                for sample in region['samples']]
            if any(packet['status'] != 'NEEDS_HUMAN_INTERPRETATION'
                   for packet in packets):
                region.update(status='INCONCLUSIVE', samples=[], remaining='UNKNOWN',
                              reason='BOOLEAN_RECHECK_FAILED')
            else:
                region['samples'] = packets
        except z3.Z3Exception as exc:
            print(json.dumps({'error': {'code': 'SOLVER_ERROR', 'message': str(exc)}}))
            return 2
        result['memory_observation'] = observe_process_memory()
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except MemoryError:
        os.write(1, MEMORY_FAILURE)
        return 3
    except (InputError, ValueError, OSError, UnicodeError, RecursionError) as exc:
        print(json.dumps({'error': {'code': 'INVALID_INPUT', 'message': str(exc)}}))
        return 2

if __name__ == '__main__':
    sys.exit(main())
