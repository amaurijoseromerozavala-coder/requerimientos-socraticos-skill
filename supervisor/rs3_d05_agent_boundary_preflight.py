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
    local_status = ('FAIL' if 'FAIL' in checks.values() else
                    'NOT_ASSESSED' if 'NOT_ASSESSED' in checks.values() else
                    'OBSERVED_LOCAL_GUARDS')
    return {
        'schema': 'rs3-d05-agent-boundary-observation/v1',
        'agent_uid': agent_uid, 'authority_uid': authority_uid,
        'checks': checks, 'local_status': local_status,
        'privilege_escalation': 'NOT_ASSESSED',
        'human_terminal_control': 'NOT_ASSESSED',
        'windows_host_control': 'NOT_ASSESSED',
        'real_authority_gate': 'SECURITY_BOUNDARY_UNMET',
        'authority_verification': 'NOT_ESTABLISHED',
        'execution_authorized': False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description='Sondeo D05 local de solo lectura')
    parser.add_argument('--authority-uid', required=True, type=int)
    parser.add_argument('--authority-root', required=True)
    args = parser.parse_args(argv)
    print(json.dumps(probe_agent_boundary(args.authority_root, args.authority_uid),
                     sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
