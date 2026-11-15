"""Synthetic NSS and Varlink oracles; never invokes real account tools."""
import importlib.util
import json
import os
from pathlib import Path
import socket
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("bootstrap_nss", Path(__file__).with_name("rs3_bootstrap.py"))
b = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(b)


class NssSystemdTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for d in ("etc", "home", "var/lib/dpkg", "proc/sys/kernel", "run/systemd/userdb"):
            (self.root / d).mkdir(parents=True, exist_ok=True)
        files = {"etc/os-release": 'ID=ubuntu\nVERSION_ID="24.04"\n',
                 "etc/wsl.conf": "[boot]\nsystemd=true\n",
                 "etc/nsswitch.conf": "passwd: files systemd\ngroup: files systemd\ngshadow: files systemd\n",
                 "etc/passwd": "root:x:0:0:root:/root:/bin/bash\n",
                 "etc/group": "root:x:0:\n", "etc/gshadow": "root:*::\n",
                 "var/lib/dpkg/status": "Package: libnss-systemd\nStatus: install ok installed\nVersion: 255.4-1ubuntu8.17\n",
                 "proc/sys/kernel/osrelease": "microsoft-standard-WSL2"}
        for name, text in files.items():
            (self.root / name).write_text(text)
        self.users = {}
        self.creations = []
        self.commands = []
        self.after_first = lambda: None
        self.before_group = lambda: None
        def account(name):
            if name not in self.users:
                raise KeyError(name)
            return self.users[name]
        patches = [patch.object(b.os, "geteuid", return_value=0),
                   patch.object(b.os, "environ", {"WSL_DISTRO_NAME": "rs3-agent"}),
                   patch.object(b, "trusted_parent"), patch.object(b.pwd, "getpwnam", side_effect=account),
                   patch.object(b.pwd, "getpwuid", side_effect=KeyError),
                   patch.object(b.grp, "getgrnam", side_effect=KeyError),
                   patch.object(b.grp, "getgrgid", side_effect=KeyError),
                   patch.object(b.os, "getgrouplist", side_effect=lambda n, g: [g]),
                   patch.object(b.os, "chown"), patch.object(b, "run", side_effect=self.fake_run)]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        # Tests run as the ordinary test user; only the trust identity is substituted.
        if hasattr(b, "nss"):
            p = patch.object(b.nss, "TRUSTED_UID", os.getuid())
            p.start()
            self.addCleanup(p.stop)
        self.stop = threading.Event()
        self.addCleanup(self.stop.set)

    def fake_run(self, argv):
        self.commands.append(argv)
        name = argv[-1]
        uid = dict((n, u) for n, u, _ in b.ACCOUNTS)[name]
        if argv[0].endswith("groupadd"):
            self.before_group()
            for f, row in (("group", f"{name}:x:{uid}:\n"), ("gshadow", f"{name}:!::\n")):
                with (self.root / "etc" / f).open("a") as out:
                    out.write(row)
        else:
            shell = next(s for n, _, s in b.ACCOUNTS if n == name)
            with (self.root / "etc/passwd").open("a") as out:
                out.write(f"{name}:x:{uid}:{uid}::/home/{name}:{shell}\n")
            self.users[name] = SimpleNamespace(pw_uid=uid, pw_gid=uid)
            self.creations.append(name)
            if len(self.creations) == 1:
                self.after_first()

    def provider(self, response, name="io.systemd.DynamicUser"):
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        path = self.root / "run/systemd/userdb" / name
        server.bind(str(path))
        server.listen()
        server.settimeout(.05)
        self.addCleanup(server.close)
        def serve():
            while not self.stop.is_set():
                try:
                    client, _ = server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    return
                with client:
                    try:
                        data = b""
                        while b"\0" not in data:
                            data += client.recv(4096)
                        req = json.loads(data.split(b"\0")[0])
                        result = response(req) if callable(response) else response
                        if result is None:
                            time.sleep(.25)
                        else:
                            client.sendall(result)
                    except (OSError, ValueError):
                        pass
        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        self.addCleanup(lambda: thread.join(.5))
        return path

    @staticmethod
    def empty():
        return b'{"error":"io.systemd.UserDatabase.NoRecordFound","parameters":{}}\0'

    def blocked(self):
        with self.assertRaises(b.Blocked):
            b.apply(self.root)
        self.assertEqual(self.creations, [])
        self.assertEqual(self.commands, [])
        self.assertEqual((self.root / "etc/wsl.conf").read_bytes(), b.ORIGINAL)

    def test_complete_known_profile_can_continue(self):
        self.provider(self.empty())
        self.assertEqual(b.preflight(self.root), b.ORIGINAL)
        b.apply(self.root)
        self.assertEqual(self.creations, ["rs3agent", "rs3guardian"])

    def test_membership_from_provider_blocks_each_reserved_name(self):
        for target, _, _ in b.ACCOUNTS:
            with self.subTest(target=target):
                path = self.provider(lambda req: (json.dumps({"parameters": {
                    "userName": target, "groupName": "sudo"}}).encode() + b"\0")
                    if req["parameters"]["userName"] == target else self.empty())
                self.blocked()
                path.unlink()

    def test_unknown_second_provider_blocks(self):
        self.provider(self.empty())
        self.provider(self.empty(), "unknown.provider")
        self.blocked()

    def test_partial_and_unavailable_provider_block(self):
        path = self.provider(b'{"parameters":')
        self.blocked()
        path.unlink()
        self.provider(b'{"error":"io.systemd.UserDatabase.ServiceNotAvailable"}\0')
        self.blocked()

    def test_timeout_blocks(self):
        self.provider(None)
        if hasattr(b, "nss"):
            with patch.object(b.nss, "QUERY_SECONDS", .05):
                self.blocked()
        else:
            self.blocked()

    def test_dropin_or_unproved_version_blocks(self):
        self.provider(self.empty())
        p = self.root / "etc/userdb"
        p.mkdir()
        self.blocked()
        p.rmdir()
        (self.root / "var/lib/dpkg/status").write_text("unproved")
        self.blocked()

    def test_local_latent_membership_still_blocks(self):
        self.provider(self.empty())
        for name, _, _ in b.ACCOUNTS:
            for file, text in (("group", f"sudo:x:27:{name}\n"),
                               ("gshadow", f"docker:*::{name}\n")):
                p = self.root / "etc" / file
                old = p.read_bytes()
                p.write_text(text)
                self.blocked()
                p.write_bytes(old)

    def test_source_change_before_mutation_creates_nothing(self):
        # The observed profile passes, then the source set changes before apply.
        self.provider(self.empty())
        b.preflight(self.root)
        (self.root / "etc/nsswitch.conf").write_text("group: sss\n")
        self.blocked()

    def test_change_after_first_creation_preserves_partial_state(self):
        self.provider(self.empty())
        self.after_first = lambda: (self.root / "etc/nsswitch.conf").write_text("group: sss\n")
        with self.assertRaises(b.Blocked):
            b.apply(self.root)
        self.assertEqual(self.creations, ["rs3agent"])
        self.assertTrue((self.root / "etc/wsl.conf.rs3-original").exists())
        self.assertEqual((self.root / "etc/wsl.conf").read_bytes(), b.ORIGINAL)

    def test_arbitrary_local_delta_is_not_rebaselined(self):
        self.provider(self.empty())
        self.after_first = lambda: (self.root / "etc/group").write_text("changed:x:55:\n")
        with self.assertRaises(b.Blocked):
            b.apply(self.root)
        self.assertEqual(self.creations, ["rs3agent"])
        self.assertEqual((self.root / "etc/wsl.conf").read_bytes(), b.ORIGINAL)

    def test_valid_source_change_during_preflight_blocks_all_commands(self):
        self.provider(self.empty())
        original = b.preflight
        def changed(root):
            result = original(root)
            with (root / "etc/passwd").open("a") as stream:
                stream.write("unexpected:x:55:55::/nonexistent:/usr/sbin/nologin\n")
            return result
        with patch.object(b, "preflight", side_effect=changed):
            self.blocked()
        self.assertFalse((self.root / "etc/wsl.conf.rs3-original").exists())

    def test_provider_change_after_first_creation_stops_second(self):
        self.provider(self.empty())
        self.after_first = lambda: self.provider(self.empty(), "unexpected.provider")
        with self.assertRaises(b.Blocked):
            b.apply(self.root)
        self.assertEqual(self.creations, ["rs3agent"])
        self.assertEqual((self.root / "etc/wsl.conf").read_bytes(), b.ORIGINAL)

    def test_duplicate_or_extra_varlink_frames_block(self):
        for data in (b'{"error":"io.systemd.UserDatabase.NoRecordFound","error":"other"}\0',
                     self.empty() + self.empty()):
            path = self.provider(data)
            self.blocked()
            path.unlink()

    def test_peer_credential_mismatch_blocks(self):
        self.provider(self.empty())
        with patch.object(b.nss, "TRUSTED_UID", os.getuid() + 1):
            with self.assertRaises(b.Blocked):
                b.nss.query(self.root, self.root / "run/systemd/userdb/io.systemd.DynamicUser",
                            "rs3agent")
