"""Read-only agent-side observations for the unverified RS3 D05 boundary.

This process cannot prove that the agent lacks sudo, Windows host control or
terminal control. No result from this module enables human authority.
"""

import argparse
import json
import os
from pathlib import Path
import stat


def _effective_caps():
    try:
        with open('/proc/self/status', 'rb') as stream:
            raw = stream.read(65537)
        if len(raw) > 65536:
            return 'NOT_ASSESSED'
        values = [line.split(b':', 1)[1].strip() for line in raw.splitlines()
                  if line.startswith(b'CapEff:')]
        if len(values) != 1:
            return 'NOT_ASSESSED'
        return 'ZERO' if int(values[0], 16) == 0 else 'NONZERO'
    except (OSError, ValueError, IndexError):
        return 'NOT_ASSESSED'


def _is_windows_mount(mount):
    """Identify a WSL Windows drive mount; an ordinary /mnt/c is insufficient."""
    try:
        with open('/proc/self/mountinfo', 'rb') as stream:
            raw = stream.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            return False
        wanted = os.fsencode(mount)
        for line in raw.splitlines():
            fields = line.split(b' - ', 1)
            if len(fields) != 2:
                continue
            left, right = fields[0].split(), fields[1].split()
            if (len(left) > 4 and left[4] == wanted and len(right) > 2
                    and (right[0] == b'drvfs'
                         or (right[0] == b'9p' and b'aname=drvfs' in right[2]))):
                return True
    except OSError:
        pass
    return False


def observe_agent_host_exposure(*, docker_socket=Path('/var/run/docker.sock'),
                                interop_path=Path('/proc/sys/fs/binfmt_misc/WSLInterop'),
                                windows_mount=Path('/mnt/c')):
    """Passive exposure observations; absence never proves isolation."""
    checks = {'docker_socket': 'NOT_ASSESSED',
              'wsl_interop': 'NOT_ASSESSED',
              'windows_mount_write': 'NOT_ASSESSED'}
    agent_uid, effective_uid = os.getuid(), os.geteuid()
    caps = _effective_caps()
    try:
        if docker_socket.is_socket():
            checks['docker_socket'] = (
                'EXPOSED' if os.access(docker_socket, os.W_OK)
                else 'ACCESS_DENIED_OBSERVED')
    except OSError:
        pass
    try:
        with interop_path.open('rb') as stream:
            raw = stream.read(4097)
        if len(raw) <= 4096:
            lines = raw.splitlines()
            if b'enabled' in lines:
                checks['wsl_interop'] = 'EXPOSED'
            elif b'disabled' in lines:
                checks['wsl_interop'] = 'DISABLED_OBSERVED'
    except OSError:
        pass
    if _is_windows_mount(windows_mount):
        checks['windows_mount_write'] = (
            'EXPOSED' if os.access(windows_mount, os.W_OK)
            else 'WRITE_DENIED_OBSERVED')
    exposed = ('EXPOSED' in checks.values() or caps == 'NONZERO'
               or agent_uid != effective_uid)
    return {
        'schema': 'rs3-d05-agent-host-exposure/v1',
        'agent_uid': agent_uid, 'effective_uid': effective_uid,
        'effective_capabilities': caps,
        'checks': checks,
        'host_status': ('EXPOSURE_OBSERVED' if exposed
                        else 'NOT_ASSESSED'),
        'privilege_escalation': ('ELEVATED_PROCESS_OBSERVED'
                                 if caps == 'NONZERO' or agent_uid != effective_uid
                                 else 'DOCKER_SOCKET_WRITE_PERMISSION_OBSERVED'
                                 if checks['docker_socket'] == 'EXPOSED'
                                 else 'NOT_ASSESSED'),
        'windows_host_control': ('INTEROP_EXPOSED_UNVERIFIED'
                                 if checks['wsl_interop'] == 'EXPOSED'
                                 else 'WINDOWS_MOUNT_WRITE_OBSERVED'
                                 if checks['windows_mount_write'] == 'EXPOSED'
                                 else 'NOT_ASSESSED'),
        'authority_verification': 'NOT_ESTABLISHED',
        'execution_authorized': False,
    }


def probe_agent_boundary(authority_root, authority_uid):
    """Observe local Linux guards from the agent UID; always deny authority."""
    agent_uid, effective_uid = os.getuid(), os.geteuid()
    checks = {
        'distinct_unprivileged_uid': 'NOT_ASSESSED',
        'agent_real_effective_uid': 'FAIL' if agent_uid != effective_uid else 'OBSERVED',
        'effective_capabilities': 'NOT_ASSESSED',
        'private_root_metadata': 'NOT_ASSESSED',
        'agent_root_access': 'NOT_ASSESSED',
        'ancestor_write_access': 'NOT_ASSESSED',
    }
    if type(authority_uid) is not int or authority_uid <= 0:
        checks['distinct_unprivileged_uid'] = 'FAIL'
    else:
        checks['distinct_unprivileged_uid'] = (
            'FAIL' if authority_uid in (agent_uid, effective_uid) else 'OBSERVED')
    caps = _effective_caps()
    checks['effective_capabilities'] = (
        'OBSERVED' if caps == 'ZERO' else
        'FAIL' if caps == 'NONZERO' else 'NOT_ASSESSED')
    try:
        root = Path(authority_root)
        if not root.is_absolute() or os.path.realpath(root) != os.path.abspath(root):
            checks['private_root_metadata'] = 'FAIL'
        else:
            info = root.lstat()
            checks['private_root_metadata'] = (
                'OBSERVED' if stat.S_ISDIR(info.st_mode)
                and info.st_uid == authority_uid
                and stat.S_IMODE(info.st_mode) == 0o700 else 'FAIL')
            checks['agent_root_access'] = (
                'FAIL' if any(os.access(root, mode)
                              for mode in (os.R_OK, os.W_OK, os.X_OK))
                else 'OBSERVED')
            checks['ancestor_write_access'] = (
                'FAIL' if any(os.access(parent, os.W_OK)
                              for parent in root.parents)
                else 'OBSERVED')
    except (OSError, TypeError, ValueError):
        pass
    exposure = observe_agent_host_exposure()
    local_status = ('FAIL' if 'FAIL' in checks.values()
                    or exposure['host_status'] == 'EXPOSURE_OBSERVED' else
                    'NOT_ASSESSED' if 'NOT_ASSESSED' in checks.values() else
                    'OBSERVED_LOCAL_GUARDS')
    return {
        'schema': 'rs3-d05-agent-boundary-observation/v1',
        'agent_uid': agent_uid, 'authority_uid': authority_uid,
        'checks': checks, 'local_status': local_status,
        'host_exposure': exposure,
        'privilege_escalation': exposure['privilege_escalation'],
        'human_terminal_control': 'NOT_ASSESSED',
        'windows_host_control': exposure['windows_host_control'],
        'real_authority_gate': 'SECURITY_BOUNDARY_UNMET',
        'authority_verification': 'NOT_ESTABLISHED',
        'execution_authorized': False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description='Sondeo D05 local de solo lectura')
    parser.add_argument('--agent-only', action='store_true')
    parser.add_argument('--authority-uid', type=int)
    parser.add_argument('--authority-root')
    args = parser.parse_args(argv)
    if args.agent_only:
        if args.authority_uid is not None or args.authority_root is not None:
            parser.error('--agent-only excludes guardian arguments')
        report = observe_agent_host_exposure()
    else:
        if args.authority_uid is None or args.authority_root is None:
            parser.error('both guardian arguments are required without --agent-only')
        report = probe_agent_boundary(args.authority_root, args.authority_uid)
    print(json.dumps(report,
                     sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
