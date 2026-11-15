import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

SPEC = importlib.util.spec_from_file_location(
    "bootstrap", Path(__file__).with_name("rs3_bootstrap.py"))
b = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(b)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in ("etc", "home", "var/lib", "proc/sys/kernel"):
            (self.root / name).mkdir(parents=True, exist_ok=True)
        (self.root / "etc/wsl.conf").write_text("[boot]\nsystemd=true\n")
        (self.root / "etc/os-release").write_text('ID=ubuntu\nVERSION_ID="24.04"\n')
        (self.root / "proc/sys/kernel/osrelease").write_text("microsoft-standard-WSL2")
        (self.root / "etc/nsswitch.conf").write_text("group: files\ngshadow: files\n")
        (self.root / "etc/group").write_text("root:x:0:\n")
        (self.root / "etc/gshadow").write_text("root:*::\n")
        self.patches = [
            patch.object(b.os, "geteuid", return_value=0),
            patch.object(b.os, "environ", {"WSL_DISTRO_NAME": "rs3-agent"}),
            patch.object(b.pwd, "getpwnam", side_effect=KeyError),
            patch.object(b.pwd, "getpwuid", side_effect=KeyError),
            patch.object(b.grp, "getgrnam", side_effect=KeyError),
            patch.object(b.grp, "getgrgid", side_effect=KeyError),
            patch.object(b, "trusted_parent", return_value=None),
        ]
        for p in self.patches:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in reversed(self.patches)])
        self.addCleanup(self.tmp.cleanup)

    def test_preflight_accepts_only_observed_config(self):
        self.assertEqual(b.preflight(self.root), b.ORIGINAL)

    def test_wrong_distro_and_nonroot_rejected(self):
        for env, uid in [("Ubuntu", 0), ("rs3-agent", 1000)]:
            with patch.dict(b.os.environ, WSL_DISTRO_NAME=env), patch.object(
                    b.os, "geteuid", return_value=uid):
                with self.assertRaises(b.Blocked):
                    b.preflight(self.root)

    def test_non_wsl_and_unexpected_os_rejected(self):
        for path, text in [("proc/sys/kernel/osrelease", "Linux"),
                           ("etc/os-release", 'ID=debian\nVERSION_ID="24.04"')]:
            p = self.root / path
            old = p.read_text()
            p.write_text(text)
            with self.assertRaises(b.Blocked):
                b.preflight(self.root)
            p.write_text(old)

    def test_unexpected_config_and_symlink_rejected(self):
        p = self.root / "etc/wsl.conf"
        p.write_text("[boot]\nsystemd=true\n[interop]\nenabled=true\n")
        with self.assertRaises(b.Blocked):
            b.preflight(self.root)
        p.unlink()
        p.symlink_to(self.root / "etc/os-release")
        with self.assertRaises(b.Blocked):
            b.preflight(self.root)

    def test_existing_names_and_ids_rejected(self):
        for owner, fn in [(b.pwd, "getpwnam"), (b.pwd, "getpwuid"),
                          (b.grp, "getgrnam"), (b.grp, "getgrgid")]:
            with patch.object(owner, fn, return_value=object()):
                with self.assertRaises(b.Blocked):
                    b.preflight(self.root)

    def test_existing_paths_rejected_without_overwrite(self):
        for name in b.NEW_PATHS:
            p = self.root / name
            p.write_text("preserve")
            with self.assertRaises(b.Blocked):
                b.preflight(self.root)
            self.assertEqual(p.read_text(), "preserve")
            p.unlink()

    def test_apply_orders_commands_and_preserves_original(self):
        run = Mock()
        with patch.object(b, "preflight", return_value=b.ORIGINAL), patch.object(
                b.os, "chown"), patch.object(b, "run", run), patch.object(
                b.pwd, "getpwnam", side_effect=lambda n: Mock(
                    pw_uid=dict((n, u) for n, u, _ in b.ACCOUNTS)[n],
                    pw_gid=dict((n, u) for n, u, _ in b.ACCOUNTS)[n])), patch.object(
                b.os, "getgrouplist", side_effect=lambda n, g: [g]):
            b.apply(self.root)
        calls = [c.args[0] for c in run.call_args_list]
        self.assertEqual(len(calls), 4)
        self.assertEqual(calls[0], ["/usr/sbin/groupadd", "--gid", "21001", "rs3agent"])
        self.assertEqual(calls[1][calls[1].index("--password") + 1], "!")
        self.assertEqual(calls[3][calls[3].index("--password") + 1], "!")
        self.assertEqual(calls[1][calls[1].index("--uid") + 1], "21001")
        self.assertEqual(calls[3][calls[3].index("--uid") + 1], "21002")
        self.assertEqual(calls[1][-1], "rs3agent")
        self.assertNotIn("--groups", str(calls))
        self.assertEqual((self.root / "etc/wsl.conf").read_text(),
                         "[boot]\nsystemd=true\n[interop]\nenabled=false\n"
                         "appendWindowsPath=false\n[automount]\nenabled=false\n"
                         "mountFsTab=false\n")
        self.assertEqual((self.root / "etc/wsl.conf.rs3-original").read_bytes(), b.ORIGINAL)
        self.assertEqual((self.root / "var/lib/rs3guardian").stat().st_mode & 0o777, 0o700)

    def test_failure_retains_backup_and_does_not_change_config(self):
        with patch.object(b, "preflight", return_value=b.ORIGINAL), patch.object(
                b, "run", side_effect=RuntimeError("command failed")):
            with self.assertRaises(RuntimeError):
                b.apply(self.root)
        self.assertEqual((self.root / "etc/wsl.conf").read_bytes(), b.ORIGINAL)
        self.assertTrue((self.root / "etc/wsl.conf.rs3-original").exists())

    def test_latent_membership_rejected_before_any_mutation(self):
        for name, _, _ in b.ACCOUNTS:
            for file, entry in (("group", f"sudo:x:27:{name}\n"),
                                ("gshadow", f"docker:*::{name}\n"),
                                ("gshadow", f"docker:*:{name}:\n")):
                with self.subTest(name=name, file=file, entry=entry):
                    p = self.root / "etc" / file
                    original = p.read_text()
                    p.write_text(entry)
                    with patch.object(b, "run") as run, patch.object(b.os, "chown"):
                        with self.assertRaises(b.Blocked):
                            b.apply(self.root)
                        run.assert_not_called()
                    self.assertFalse((self.root / b.NEW_PATHS[3]).exists())
                    self.assertEqual((self.root / "etc/wsl.conf").read_bytes(), b.ORIGINAL)
                    p.write_text(original)

    def test_unverified_nss_and_malformed_membership_sources_rejected(self):
        p = self.root / "etc/nsswitch.conf"
        for text in ("group: files systemd\ngshadow: files\n",
                     "group: files\ngshadow: files\ninitgroups: sss\n",
                     "group: files\ngroup: files\ngshadow: files\n"):
            p.write_text(text)
            with self.assertRaises(b.Blocked):
                b.preflight(self.root)
        p.write_text("group: files\ngshadow: files\n")
        (self.root / "etc/group").write_text("malformed")
        with self.assertRaises(b.Blocked):
            b.preflight(self.root)

    def test_missing_membership_source_blocks_before_mutation(self):
        for file in ("nsswitch.conf", "group", "gshadow"):
            p = self.root / "etc" / file
            original = p.read_text()
            p.unlink()
            with patch.object(b, "run") as run:
                with self.assertRaises(b.Blocked):
                    b.apply(self.root)
                run.assert_not_called()
            self.assertFalse((self.root / b.NEW_PATHS[3]).exists())
            p.write_text(original)

    def test_effective_groups_checked_before_config_replace(self):
        for target, _, _ in b.ACCOUNTS:
            for extra, wrong_primary in ((True, False), (False, True)):
                def account(name):
                    uid = dict((n, u) for n, u, _ in b.ACCOUNTS)[name]
                    return Mock(pw_uid=uid, pw_gid=27 if wrong_primary and name == target else uid)
                with patch.object(b, "preflight", return_value=b.ORIGINAL), patch.object(
                        b, "run"), patch.object(b.pwd, "getpwnam", side_effect=account), patch.object(
                        b.os, "getgrouplist", side_effect=lambda n, g:
                        [g, 27] if extra and n == target else [g]), patch.object(b.os, "chown"):
                    with self.assertRaises(b.Blocked):
                        b.apply(self.root)
                self.assertEqual((self.root / "etc/wsl.conf").read_bytes(), b.ORIGINAL)
                (self.root / "etc/wsl.conf.rs3-original").unlink()

    def test_trusted_parent_rejects_symlink_and_writable_parent(self):
        # Exercise the real validator, not the setUp mock.
        self.patches[-1].stop()
        p = self.root / "home"
        p.chmod(0o777)
        with self.assertRaises(b.Blocked):
            b.trusted_parent(p)
        p.chmod(0o700)
        p.rmdir()
        p.symlink_to(self.root / "etc")
        with self.assertRaises(b.Blocked):
            b.trusted_parent(p)


if __name__ == "__main__":
    unittest.main()
