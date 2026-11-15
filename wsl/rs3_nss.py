"""Bounded membership coverage for the explicit files/systemd-255 profile.

Trusted host/root only. Rechecks detect observed changes, not hostile-root races.
"""
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import struct
import time

TRUSTED_UID = 0
QUERY_SECONDS = 2.0
PROVIDER = "io.systemd.DynamicUser"
DROPINS = ("etc/userdb", "run/userdb", "run/host/userdb", "usr/lib/userdb")
LOCAL = ("nsswitch.conf", "passwd", "group", "gshadow")


class Blocked(RuntimeError):
    pass


def metadata(root, path):
    identities = []
    for p in (path, *path.parents):
        if p == root.parent:
            break
        st = p.lstat()
        if stat.S_ISLNK(st.st_mode) or st.st_uid != TRUSTED_UID:
            raise Blocked("untrusted coverage path")
        if st.st_mode & 0o022 and not stat.S_ISSOCK(st.st_mode):
            raise Blocked("writable coverage path")
        identities.append((st.st_dev, st.st_ino, st.st_uid, st.st_gid, st.st_mode))
        if p == root:
            break
    return tuple(identities)


def read_source(root, path):
    metadata(root, path)
    a = path.stat()
    if not stat.S_ISREG(a.st_mode):
        raise Blocked("coverage source is not a regular file")
    data = path.read_bytes()
    z = path.stat()
    if (a.st_dev, a.st_ino, a.st_mtime_ns, a.st_ctime_ns, a.st_size) != (
            z.st_dev, z.st_ino, z.st_mtime_ns, z.st_ctime_ns, z.st_size):
        raise Blocked("source changed while reading")
    return data


def query(root, path, user):
    before = path.lstat()
    deadline = time.monotonic() + QUERY_SECONDS
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(QUERY_SECONDS)
        client.connect(str(path))
        _, uid, _ = struct.unpack("3i", client.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
        if uid != TRUSTED_UID:
            raise Blocked("untrusted userdb peer")
        request = {"method": "io.systemd.UserDatabase.GetMemberships",
                   "parameters": {"userName": user, "service": path.name}, "more": True}
        client.sendall(json.dumps(request).encode() + b"\0")
        data = b""
        while b"\0" not in data:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise Blocked("userdb timeout")
            client.settimeout(remaining)
            chunk = client.recv(4096)
            if not chunk:
                raise Blocked("partial userdb response")
            data += chunk
            if len(data) > 16384:
                raise Blocked("oversized userdb response")
        frame, rest = data.split(b"\0", 1)
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise Blocked("duplicate userdb JSON field")
                result[key] = value
            return result
        reply = json.loads(frame.decode("utf-8"), object_pairs_hook=unique)
        if (rest or not isinstance(reply, dict) or
                reply.get("error") != "io.systemd.UserDatabase.NoRecordFound" or
                reply.get("parameters", {}) != {} or
                reply.get("continues", False) is not False or
                set(reply) - {"error", "parameters", "continues"}):
            raise Blocked("membership or incomplete/unproved userdb reply")
    after = path.lstat()
    if (before.st_dev, before.st_ino, before.st_ctime_ns) != (
            after.st_dev, after.st_ino, after.st_ctime_ns):
        raise Blocked("userdb endpoint changed")


def profile(data):
    sources = {}
    for line in data.decode().splitlines():
        key, sep, value = line.split("#", 1)[0].partition(":")
        key = key.strip()
        if key in ("passwd", "group", "gshadow", "initgroups"):
            if not sep or key in sources:
                raise Blocked("ambiguous NSS source")
            sources[key] = value.split()
    if not {"passwd", "group", "gshadow"} <= sources.keys():
        raise Blocked("incomplete NSS profile")
    selected = sources["group"]
    if selected not in (["files"], ["files", "systemd"]):
        raise Blocked("unsupported NSS profile")
    if any(value != selected for value in sources.values()):
        raise Blocked("inconsistent NSS coverage")
    return "systemd" in selected


def snapshot(root, names):
    try:
        files = {name: read_source(root, root / "etc" / name) for name in LOCAL}
        dynamic = profile(files["nsswitch.conf"])
        for file in ("group", "gshadow"):
            seen = set()
            for line in files[file].decode().splitlines():
                fields = line.split(":")
                if len(fields) != 4 or not fields[0] or fields[0] in seen:
                    raise Blocked("malformed or duplicate membership source")
                seen.add(fields[0])
                if file == "group" and not fields[2].isdigit():
                    raise Blocked("malformed group ID")
                members = fields[3].split(",")
                if file == "gshadow":
                    members += fields[2].split(",")
                if any(x != x.strip() for x in members) or set(names).intersection(members):
                    raise Blocked("reserved username has pre-existing membership")
        fixed = {}
        if dynamic:
            status = read_source(root, root / "var/lib/dpkg/status")
            packages = [dict(line.split(": ", 1) for line in block.splitlines() if ": " in line)
                        for block in status.decode().split("\n\n")]
            if not any(p.get("Package") == "libnss-systemd" and
                       p.get("Status") == "install ok installed" and
                       p.get("Version") == "255.4-1ubuntu8.17" for p in packages):
                raise Blocked("unproved nss-systemd version")
            fixed["package"] = hashlib.sha256(status).digest()
            for name in DROPINS:
                p = root / name
                if os.path.lexists(p):
                    raise Blocked("uncovered userdb drop-ins")
                parent = p.parent
                while not parent.exists():
                    if parent.is_symlink():
                        raise Blocked("untrusted drop-in parent")
                    parent = parent.parent
                fixed[name] = metadata(root, parent)
            directory = root / "run/systemd/userdb"
            metadata(root, directory)
            entries = sorted(directory.iterdir())
            if [p.name for p in entries] != [PROVIDER]:
                raise Blocked("unknown or unavailable userdb provider")
            st = entries[0].lstat()
            if not stat.S_ISSOCK(st.st_mode) or st.st_uid != TRUSTED_UID:
                raise Blocked("untrusted userdb endpoint")
            fixed["endpoint"] = (st.st_dev, st.st_ino, st.st_ctime_ns)
            for user in names:
                query(root, entries[0], user)
            if sorted(p.name for p in directory.iterdir()) != [PROVIDER]:
                raise Blocked("provider set changed")
        # Catch file changes during provider calls too.
        if any(read_source(root, root / "etc" / name) != data for name, data in files.items()):
            raise Blocked("local source changed during query")
        return files, fixed
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        raise Blocked("membership coverage cannot be verified") from exc


class Guard:
    def __init__(self, root, names):
        self.root, self.names = root, names
        self.baseline = snapshot(root, names)

    def before(self):
        if snapshot(self.root, self.names) != self.baseline:
            raise Blocked("coverage changed; preserve partial state")

    def after(self, kind, name, uid, shell):
        expected = dict(self.baseline[0])
        if kind == "group":
            expected["group"] += f"{name}:x:{uid}:\n".encode()
            expected["gshadow"] += f"{name}:!::\n".encode()
        else:
            expected["passwd"] += f"{name}:x:{uid}:{uid}::/home/{name}:{shell}\n".encode()
        current = snapshot(self.root, self.names)
        if current != (expected, self.baseline[1]):
            raise Blocked("unexpected mutation delta; preserve partial state")
        # Accept only the exact command-specific append, never an arbitrary baseline.
        self.baseline = current
