#!/usr/bin/env bash
set -euo pipefail

# One bounded worker; no load generators or access to privileged resources.
ulimit -v 1048576
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 TZ=UTC

python3 -B ci/check_history_markers.py
python3 -B ci/check_rdd_record.py
# This records the runner's visible admission facts if a later suite closes.
# It does not override the skill's fail-closed resource policy.
PYTHONPATH=skills/requerimientos-socraticos/scripts python3 -B -c '
import json, probe_environment
m = probe_environment.memory_observation()
c = probe_environment.cgroup_observation()
print("CI_ADMISSION_OBSERVATION " + json.dumps({"memory_status": m["status"], "cgroup_status": c["status"], "memory_limit_states": [row["memory"] for row in c["limit_states"]]}, sort_keys=True))
'
ci_scratch_dir=$(mktemp -d -t ci-quality-XXXXXXXX)
trap 'rm -rf -- "$ci_scratch_dir"' EXIT

run_suite() {
  local label=$1 suite=$2 exit_code
  if python3 -B ci/safe_suite_capture.py \
      "$ci_scratch_dir/$label.stdout" "$ci_scratch_dir/$label.stderr" -- \
      python3 -B -m unittest discover -s "$suite" -q; then
    printf '%s: ' "$label"
    sed -n '/^Ran [0-9][0-9]* tests /p; /^OK$/p' "$ci_scratch_dir/$label.stderr" | tr '\n' ' '
    printf '\n'
  else
    exit_code=$?
    printf '%s: FAILED exit=%s\n' "$label" "$exit_code" >&2
    if [[ -f "$ci_scratch_dir/$label.stderr" && -f "$ci_scratch_dir/$label.stdout" ]]; then
      tail -c 8192 "$ci_scratch_dir/$label.stderr" >&2
      head -c 2048 "$ci_scratch_dir/$label.stdout" >&2
    else
      printf '%s\n' 'CI_CAPTURE_UNAVAILABLE' >&2
    fi
    return "$exit_code"
  fi
}

run_suite ci ci/tests
run_suite supervisor supervisor/tests
run_suite qa skills/qa-inquisidor/tests
run_suite requirements skills/requerimientos-socraticos/tests
