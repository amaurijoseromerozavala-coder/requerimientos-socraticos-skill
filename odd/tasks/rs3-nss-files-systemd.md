# WU-RS3-NSS-002 — Verify files/systemd membership coverage

Status: candidate implemented; synthetic RED/GREEN and regression observed; runtime NOT_RUN and native RDD pending.
Base: 4fcb0baa601c76b087b057cf8c8425eaf8b3a1e4.

## Human objective
Admit only a demonstrably covered files/systemd profile in the rs3-agent bootstrap.
Do not change NSS, apply the real bootstrap, create real accounts, or weaken fail-closed behavior.

## Frozen acceptance oracles
1. A verified profile with no reserved memberships may pass preflight.
2. Either reserved name in local files or ANY active provider blocks before the first account creation.
3. An unknown provider, partial reply, timeout or unproved coverage blocks before the first account creation.
4. A source change detected before mutation permits zero account creations. A change detected after
   the first account creation preserves evidence and partial state, prevents the second account
   creation and prevents wsl.conf replacement. Never call this zero mutations.
5. Effective primary and supplementary group verification after creation remains mandatory.

## Capability gate before implementation
- Determine whether userdbctl 255 exposes completion versus partial results for all active sources.
- If it is unavailable or insufficient, evaluate bounded direct Varlink queries against primary
  systemd 255 source/API documentation and read-only observations of the actual distribution.
- NoRecordFound from one provider is not evidence of global coverage. Incomplete enumeration is UNKNOWN.
- If neither route establishes the required coverage, stop BLOCKED_NSS_COVERAGE with
  membership_sources unchanged; record the exact missing guarantee.

## Bounded design to investigate
- Require an exact supported NSS source profile and account for effective initgroups behavior.
- Enumerate every source used by that profile, including local files, providers and static drop-ins.
  Unimplemented sources must block; do not silently skip them.
- Consume complete bounded membership replies for both reserved names; verify trusted endpoints,
  provider identity and completion, and reject membership or ambiguous results.
- Revalidate coverage before each mutation boundary. Distinguish expected writes by this bootstrap
  from external source changes without blindly accepting a new baseline.
- Preserve partial state on failure; no automatic cleanup, account deletion or retry.
- Environment distro identity prevents accidental targeting; it is not authentication against host/root.

## Planned synthetic tests and evidence
- Positive supported profile and empty complete replies from all sources.
- Membership in files or a second provider for each reserved name.
- Partial/truncated reply, timeout, unknown provider, unreadable source and source-set changes.
- Source changes before the first creation and after the first creation; assert the correct
  zero-creation or partial-state oracle and unchanged wsl.conf.
- Retain effective group postcheck negatives.
- Observe a genuine target-defect RED before implementation, then GREEN and affected regression.
- Use only isolated fixtures and synthetic sockets. Never execute host account tools in tests.
- Keep sanitized test evidence outside the reviewed files; native RDD and delivery records
  must identify the exact candidate and not approve themselves.

## Delivery and rollback boundary
Parent obtains native exact-candidate RDD consent/approval/acknowledgement before WU-BACKUP.
No commit/push before closure. No real bootstrap application in this unit.
Rollback boundary: this unit's code/tests/ODD only, not real account or NSS state.
D05=NOT_ESTABLISHED; execution_authorized=false.

## Tasks
- [x] Record ODD before implementation/test edits.
- [x] Establish capability evidence and bounded coverage assumptions.
- [x] Parent accepts feasibility/design handoff.
- [x] Observe RED, implement minimal fix, GREEN and regression.
- [ ] Complete native RDD and backup after approved acknowledgement.

## Capability evidence (read-only; implementation not authorized yet)
- Live target: glibc 2.39-0ubuntu8.8, libnss-systemd/systemd 255.4-1ubuntu8.17;
  userdbctl is not installed. No software was installed.
- Upstream systemd v255 userdb_start_query ignores failed connections when another
  service connected; membershipdb_iterator_get can convert later errors to end-of-results.
  Therefore merged CLI success/output cannot prove every provider completed.
- Direct Varlink permits per-provider completion checks without that merged-error policy.
  Live snapshot: only io.systemd.DynamicUser, root-owned socket with root peer UID/GID;
  both reserved names returned terminal NoRecordFound, not a continues reply.
- The four documented userdb drop-in directories were absent. This is a snapshot,
  not permanent absence or proof from one provider alone.
- A viable narrow profile must reject unknown providers, any drop-in directory present,
  unexpected NSS rules/actions, source instability and incomplete/untrusted replies.
  It must enumerate the full provider directory and query every accepted endpoint;
  a missing, inaccessible or newly appearing provider is a blocking coverage change.
- Coverage is bounded to a checked stable snapshot under a trusted host/root assumption.
  No claim of atomic exclusion of hostile root changes between a check and a syscall.

Primary sources:
- https://raw.githubusercontent.com/systemd/systemd/v255/src/shared/userdb.c
- https://raw.githubusercontent.com/systemd/systemd/v255/src/userdb/userdbctl.c
- https://raw.githubusercontent.com/systemd/systemd/v255/src/nss-systemd/nss-systemd.c
- https://systemd.io/USER_GROUP_API/

Handoff: bounded direct-Varlink design is feasible for the observed explicit profile,
subject to synthetic proof of complete replies and mutation-boundary handling.
Implementation and synthetic checks are complete below; native RDD and real runtime remain pending.

## Candidate implementation and observed evidence
- Separate rs3_nss module accepts exact all-files or all-files-systemd NSS rules;
  the latter pins libnss-systemd 255.4-1ubuntu8.17 and only the DynamicUser endpoint.
- Absent drop-in directories are part of the bounded profile; any present directory,
  extra provider, untrusted peer, malformed/partial reply or timeout blocks.
- Snapshot rechecks surround groupadd/useradd and configuration replacement. Own writes
  must match exact expected group/gshadow/passwd appends, never arbitrary new baselines.
- Existing effective-group checks remain; tests never invoke real account tools.
- RED: 10 initial synthetic tests, exit 1 on the original implementation; two failures
  and two errors reflected the unsupported positive profile and unreachable partial-state cases.
  A prior test-generation syntax issue was fixed before this semantic RED and is not counted.
- GREEN: 27 isolated tests, exit 0. Boundary regression: 18 tests, exit 0.
- Raw logs and exit codes: user-local state directory rs3-nss-002-evidence, outside this candidate.
- Legacy fixtures now include passwd and model expected account-tool file writes. Existing
  assertions remain; the effective-group loop resets local account files between subcases.
- No actual bootstrap application, accounts, packages or NSS configuration changes occurred.
