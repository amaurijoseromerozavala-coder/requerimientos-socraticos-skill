# WU-RS3-BOOTSTRAP-001 — Candidate only

## Human request and objective
Prepare a reproducible bootstrap restricted to the new rs3-agent WSL2 distro.
The control Ubuntu must not be configured, stopped, or used as agent authority.

## Scope and acceptance
- Require root, exact WSL_DISTRO_NAME=rs3-agent, Ubuntu 24.04 and WSL2.
  This is accidental-target protection, not authentication against a hostile root/host.
- Accept only the observed boot/systemd=true configuration; reject extra settings.
- Reject existing account/group names, reserved UID/GID collisions, homes, guardian
  directory, backup or staging file, and symlink/untrusted parent directories.
- Preserve systemd=true; disable interop, Windows PATH append and automount.
- Create locked rs3agent/rs3guardian with distinct reserved UIDs and primary groups,
  no supplementary groups; create guardian-owned /var/lib/rs3guardian mode 0700.
- Preserve the original recognized config in an exclusive backup. Failures retain
  partial evidence and are not retried or rolled back automatically.
- No passwords, codes, keys, HUMAN_CONFIRMED, production activation or D05 claim.
- Native exact-candidate RDD approval is required before any real configuration.

## Tasks and oracle
1. Record this ODD before writing implementation.
2. Add isolated tests for accepted/rejected preflight and bounded application.
3. Capture actual RED before implementation; capture GREEN and affected regression.
4. Parent obtains exact-candidate Gentle AI receipt; currently BLOCKED at
   intended_untracked_selection, external.select_intended_untracked unavailable.
5. Only after approval, parent rechecks resources, applies once, terminates only
   rs3-agent, then independently verifies as rs3agent after a new boot.
6. Parent must run Pi/Codex really as rs3agent; shell probes alone cannot prove its
   future authority boundary. Host/root control and shared-kernel risks remain.

## Evidence and rollback boundary
Test evidence is retained outside the candidate in a newly allocated /tmp directory.
Tests use only their own temporary fixtures and mock account commands.
Real runtime: NOT_RUN; RDD: BLOCKED; unit remains open, no commit/push.
Rollback boundary is these candidate files only. Runtime rollback is not automatic:
preserve partial state for a separate authorized recovery, never delete accounts
or evidence to force retry.

## Primary reference
https://learn.microsoft.com/en-us/windows/wsl/wsl-config
Per-distro wsl.conf applies on restart; automount=false does not prevent privileged
manual mounts. Disabling interop is not a host/root security boundary.

## Candidate progress
RED: exit 1, missing implementation; GREEN: 9 isolated tests; regression: 18 boundary tests.
Real apply and post-restart probes remain NOT_RUN; RDD has no approved receipt.

## Bounded correction R3-supplementary-membership
Native correction plan captured before edits: 145 lines forecast, 149 hard maximum.
Reject latent memberships before mutation; verify effective groups after creation.
Only verifiable files-only group/gshadow/initgroups NSS sources are supported.
Observed rs3-agent files+systemd sources remain BLOCKED: coverage is not established.
Tests use synthetic accounts/groups only; no real bootstrap or account creation.
