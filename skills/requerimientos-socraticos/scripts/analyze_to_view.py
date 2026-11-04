#!/usr/bin/env python3
"""Supervise Boolean analysis and render only a complete read-only view."""

import argparse
import json
import math
from pathlib import Path
import sys

from json_preflight import preflight_json
from process_supervision import run_supervised
from render_gap_questions import (MAX_INPUT_BYTES, _unique_object,
                                  render_analysis_report)


ANALYZER = Path(__file__).with_name('analyze_logic.py')
CONFIRMED_CLEANUP = 'DIRECT_WORKER_REAPED_AND_PIPES_DRAINED'


class PipelineError(ValueError):
    def __init__(self, code, exit_code=3):
        super().__init__(code)
        self.code = code
        self.exit_code = exit_code


def run_pipeline(model, glossary, *, timeout=5, samples=1,
                 source_repo=None, source_commit=None, analyzer_path=ANALYZER):
    """Return HTML only after a bounded child exits cleanly with a coherent report."""
    if (type(timeout) not in (int, float) or not math.isfinite(timeout)
            or not 0 < timeout <= 30 or type(samples) is not int
            or not 1 <= samples <= 16
            or (source_repo is None) != (source_commit is None)):
        raise PipelineError('INVALID_PIPELINE_ARGUMENTS', 2)
    analyzer = Path(analyzer_path).resolve(strict=True)
    command = [sys.executable, '-B', str(analyzer), model, '--glossary',
               glossary, '--timeout', str(timeout), '--gap-samples', str(samples)]
    if source_repo is not None:
        command += ['--source-repo', source_repo, '--source-commit', source_commit]
    observed = run_supervised(command, timeout + 2,
                              output_limit_bytes=MAX_INPUT_BYTES)
    if observed['cleanup_status'] != CONFIRMED_CLEANUP:
        raise PipelineError('ANALYZER_CLEANUP_UNCONFIRMED')
    if observed['output_limit']:
        raise PipelineError('ANALYZER_OUTPUT_LIMIT')
    if observed['timed_out']:
        raise PipelineError('ANALYZER_WALL_LIMIT')
    if observed['returncode'] != 0:
        raise PipelineError('ANALYZER_EXIT_FAILURE', 2)
    raw = observed['stdout_bytes']
    try:
        preflight_json(raw, max_depth=32, max_bytes=MAX_INPUT_BYTES)
        report = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object,
                            parse_constant=lambda _: (_ for _ in ()).throw(
                                ValueError('NONFINITE_JSON_NUMBER')))
        return render_analysis_report(report)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise PipelineError('ANALYZER_REPORT_INVALID', 2) from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', help='bounded Boolean model JSON path')
    parser.add_argument('--glossary', required=True,
                        help='proposed glossary JSON path')
    parser.add_argument('--timeout', type=float, default=5,
                        help='analyzer budget in seconds, greater than 0 and at most 30')
    parser.add_argument('--gap-samples', type=int, default=1)
    parser.add_argument('--source-repo')
    parser.add_argument('--source-commit')
    args = parser.parse_args()
    try:
        html = run_pipeline(args.model, args.glossary, timeout=args.timeout,
                            samples=args.gap_samples, source_repo=args.source_repo,
                            source_commit=args.source_commit)
    except PipelineError as error:
        print(error.code, file=sys.stderr)
        return error.exit_code
    except MemoryError:
        print('INFRA_FAILURE', file=sys.stderr)
        return 3
    except (ValueError, OSError, RecursionError):
        print('PIPELINE_INFRA_FAILURE', file=sys.stderr)
        return 3
    sys.stdout.write(html)
    return 0


if __name__ == '__main__':
    sys.exit(main())
