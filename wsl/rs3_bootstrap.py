"""Candidate only: apply on rs3-agent as trusted root after exact-candidate RDD.

Environment identity is an accidental-target guard, not authentication against root.
No automatic rollback/retry: preserve partial state for authorized recovery.
"""
import grp
import os
from pathlib import Path
import pwd
import subprocess

ORIGINAL = b"[boot]\nsystemd=true\n"
CONFIG = """[boot]
systemd=true
[interop]
enabled=false
appendWindowsPath=false
[automount]
enabled=false
mountFsTab=false
"""
ACCOUNTS = (("rs3agent", 21001, "/bin/bash"),
            ("rs3guardian", 21002, "/usr/sbin/nologin"))
NEW_PATHS = ("home/rs3agent", "home/rs3guardian", "var/lib/rs3guardian",
             "etc/wsl.conf.rs3-original", "etc/wsl.conf.rs3-new")


class Blocked(RuntimeError):
    pass


def trusted_parent(path):
    if path.is_symlink():
        raise Blocked("symlink parent")
    st = path.stat()
    if not path.is_dir() or st.st_uid != 0 or st.st_mode & 0o022:
        raise Blocked("parent is not root-owned and protected")


def absent(lookup, value):
    try:
        lookup(value)
    except KeyError:
        return
    raise Blocked("account/group name or numeric ID already exists")


def membership_sources(root):
    """Fail closed unless local files completely cover group membership."""
    try:
        sources = {}
        nss = root / "etc/nsswitch.conf"
        if nss.is_symlink():
            raise Blocked("untrusted NSS source")
        for line in nss.read_text().splitlines():
            key, _, value = line.split("#", 1)[0].partition(":")
            key = key.strip()
            if key in ("group", "gshadow", "initgroups"):
                if key in sources or value.split() != ["files"]:
                    raise Blocked("membership source coverage not established")
                sources[key] = value
        if not {"group", "gshadow"} <= sources.keys():
            raise Blocked("membership source coverage not established")
        names = {name for name, _, _ in ACCOUNTS}
        for file in ("group", "gshadow"):
            path = root / "etc" / file
            if path.is_symlink():
                raise Blocked("untrusted membership file")
            for line in path.read_text().splitlines():
                fields = line.split(":")
                if len(fields) != 4 or not fields[0]:
                    raise Blocked("malformed membership file")
                if file == "group" and not fields[2].isdigit():
                    raise Blocked("malformed group ID")
                members = fields[3].split(",")
                if file == "gshadow":
                    members += fields[2].split(",")
                if any(member != member.strip() for member in members):
                    raise Blocked("malformed member")
                if names.intersection(members):
                    raise Blocked("reserved username has pre-existing membership")
    except (OSError, UnicodeError) as exc:
        raise Blocked("membership coverage cannot be verified") from exc


def effective_memberships(root):
    membership_sources(root)
    for name, gid, _ in ACCOUNTS:
        user = pwd.getpwnam(name)
        if (user.pw_uid != gid or user.pw_gid != gid or
                set(os.getgrouplist(name, gid)) != {gid}):
            raise Blocked("unexpected effective account membership")


def preflight(root=Path("/")):
    if os.geteuid() != 0 or os.environ.get("WSL_DISTRO_NAME") != "rs3-agent":
        raise Blocked("requires root in exactly rs3-agent")
    kernel = (root / "proc/sys/kernel/osrelease").read_text().lower()
    release = dict(line.split("=", 1) for line in
                   (root / "etc/os-release").read_text().splitlines() if "=" in line)
    if "microsoft" not in kernel or "wsl2" not in kernel:
        raise Blocked("requires WSL2")
    if release.get("ID") != "ubuntu" or release.get("VERSION_ID", "").strip('"') != "24.04":
        raise Blocked("unexpected OS")
    for name in ("etc", "home", "var", "var/lib"):
        trusted_parent(root / name)
    conf = root / "etc/wsl.conf"
    if conf.is_symlink() or not conf.is_file() or conf.read_bytes() != ORIGINAL:
        raise Blocked("unexpected wsl.conf")
    if any((root / name).exists() or (root / name).is_symlink() for name in NEW_PATHS):
        raise Blocked("refusing pre-existing destination or previous attempt")
    membership_sources(root)
    for name, uid, shell in ACCOUNTS:
        for lookup, value in ((pwd.getpwnam, name), (pwd.getpwuid, uid),
                              (grp.getgrnam, name), (grp.getgrgid, uid)):
            absent(lookup, value)
        if not Path(shell).is_file():
            raise Blocked("required shell unavailable")
    for command in ("/usr/sbin/groupadd", "/usr/sbin/useradd"):
        if not os.access(command, os.X_OK):
            raise Blocked("required account tool unavailable")
    return ORIGINAL


def run(argv):
    subprocess.run(argv, check=True, stdin=subprocess.DEVNULL)


def exclusive_write(path, data, mode):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def apply(root=Path("/")):
    original = preflight(root)
    # A backup is also a fail-closed marker: partial attempts cannot auto-retry.
    exclusive_write(root / "etc/wsl.conf.rs3-original", original, 0o600)
    for name, uid, shell in ACCOUNTS:
        run(["/usr/sbin/groupadd", "--gid", str(uid), name])
        run(["/usr/sbin/useradd", "--uid", str(uid), "--gid", str(uid),
             "--no-user-group", "--create-home", "--shell", shell,
             "--password", "!", name])
    effective_memberships(root)
    guardian = root / "var/lib/rs3guardian"
    guardian.mkdir(mode=0o700)
    os.chown(guardian, 21002, 21002)
    guardian.chmod(0o700)
    conf = root / "etc/wsl.conf"
    if conf.is_symlink() or conf.read_bytes() != original:
        raise Blocked("configuration changed during apply; preserve partial state")
    staged = root / "etc/wsl.conf.rs3-new"
    exclusive_write(staged, CONFIG.encode(), 0o644)
    os.replace(staged, conf)
    print("BOOTSTRAP_WRITTEN; restart only rs3-agent; D05 NOT_ESTABLISHED")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        if args.apply:
            apply()
        else:
            preflight()
            print("PREFLIGHT_ONLY; no configuration applied")
    except Exception as exc:
        raise SystemExit("BLOCKED: " + str(exc))
