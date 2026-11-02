#!/usr/bin/env bash
set -euo pipefail

# One bounded worker; no load generators or access to privileged resources.
ulimit -v 1048576
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 TZ=UTC

python3 -B ci/check_rdd_record.py
ci_scratch_dir=$(mktemp -d -t ci-quality-XXXXXXXX)
trap 'rm -rf -- "$ci_scratch_dir"' EXIT

run_suite() {
  local label=$1 suite=$2 exit_code
  if timeout --signal=TERM --kill-after=5s 90s \
      python3 -B -m unittest discover -s "$suite" -q \
      > "$ci_scratch_dir/$label.stdout" 2> "$ci_scratch_dir/$label.stderr"; then
    printf '%s: ' "$label"
    sed -n '/^Ran [0-9][0-9]* tests /p; /^OK$/p' "$ci_scratch_dir/$label.stderr" | tr '\n' ' '
    printf '\n'
  else
    exit_code=$?
    printf '%s: FAILED exit=%s\n' "$label" "$exit_code" >&2
    tail -c 8192 "$ci_scratch_dir/$label.stderr" >&2
    head -c 2048 "$ci_scratch_dir/$label.stdout" >&2
    return "$exit_code"
  fi
}

run_suite ci ci/tests
run_suite supervisor supervisor/tests
run_suite qa skills/qa-inquisidor/tests
run_suite requirements skills/requerimientos-socraticos/tests
