"""Bounded falsifier for this report's controlled limitations vocabulary."""
import copy
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
checker = runpy.run_path(str(HERE / 'check_evidence.py'), run_name='negative_control')
verify = checker['verify']
data = json.loads((HERE / 'observation.json').read_text(encoding='utf-8'))
readme = (HERE.parents[2] / 'README.md').read_text(encoding='utf-8')
mutant = copy.deepcopy(data)
original = 'No cause is assigned to pre/post changes in Windows free memory or PSI I/O.'
assert original in mutant['limitations']
mutant['limitations'][mutant['limitations'].index(original)] = (
    'The test suite caused the observed change in Windows free memory and PSI I/O.')
try:
    verify(mutant, readme)
except AssertionError:
    print('CAUSAL_ATTRIBUTION_REJECTED_EXPECTED')
else:
    raise AssertionError('CAUSAL_ATTRIBUTION_ACCEPTED_UNEXPECTED')
