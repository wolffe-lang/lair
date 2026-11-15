#!/usr/bin/env python3
"""Capture-all diagnostics: real pty children, no compiler or game required."""
import ast
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent


def runner_module():
    loader = importlib.machinery.SourceFileLoader("pty_runner", str(ROOT / "tools/pty"))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


# The row deliberately returns the LAST session, as multi-session game rows
# do, while reporting a problem in the FIRST. No signal or user's shell.
FIXTURE = '''import sys, time

def earlier_failure(bin, ctx):
    first = ctx.Session([bin, "-I", "-c", "import os; os.write(1,b'FIRST'); os.write(2,b'FIRSTERR'); raise SystemExit(3)"],
                        24, 80, ctx.env_for(), settle=0)
    first.finish()
    code = "import os,termios; a=termios.tcgetattr(0); b=termios.tcgetattr(0); b[3]&=~(termios.ICANON|termios.ECHO); b[6][termios.VMIN]=1; b[6][termios.VTIME]=0; termios.tcsetattr(0,termios.TCSANOW,b); os.write(1,b'READY'); k=os.read(0,1); os.write(1,b'SECOND:'+k); os.write(2,b'SECONDERR:'+k); termios.tcsetattr(0,termios.TCSANOW,a)"
    last = ctx.Session([bin, "-I", "-c", code], 24, 80, ctx.env_for(), settle=0)
    deadline = time.monotonic() + 5
    while b"READY" not in last.out and time.monotonic() < deadline:
        last.pump(0.02)
    if b"READY" not in last.out:
        raise RuntimeError("fixture child never ready")
    last.type(b"z", settle=0)
    last.finish()
    return last, ["earlier child exited %d" % first.status]

def green(bin, ctx):
    session = ctx.Session([bin, "-I", "-c", "import os; os.write(1,b'GREEN')"],
                          24, 80, ctx.env_for(), settle=0)
    session.finish()
    return session, []

def exceptional(bin, ctx):
    green(bin, ctx)
    raise RuntimeError("fixture row exception")

ROWS = {"earlier-failure": earlier_failure, "green": green, "exceptional": exceptional}
'''


class CaptureDiagnostics(unittest.TestCase):
    def fixture_run(self, root, mode, row="earlier-failure"):
        for name in ("tools", "tests", "src", "home"):
            (root / name).mkdir()
        for name in ("pty", "memgate.py"):
            shutil.copy2(ROOT / "tools" / name, root / "tools" / name)
        (root / "src/demo.lu").touch()
        (root / "tests/pty_rows.py").write_text(FIXTURE)
        env = dict(os.environ, HOME=str(root / "home"), SHELL="/bin/sh",
                   LAIR_MEMORY_GATE="0", GITHUB_TOKEN="credential-sentinel")
        env.pop("LAIR_PTY_CAPTURE_ALL", None)
        args = [sys.executable, "-I", str(root / "tools/pty"),
                "--bin", sys.executable, "--rows", row]
        if mode == "option":
            args.append("--capture-all")
        elif mode == "environment":
            env["LAIR_PTY_CAPTURE_ALL"] = "1"
        return subprocess.run(args, env=env, cwd=root, capture_output=True,
                              text=True, timeout=20)

    def test_capture_all_preserves_earlier_failed_session(self):
        for mode in ("option", "environment"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(prefix="lair-pty-") as temp:
                root = Path(temp)
                result = self.fixture_run(root, mode)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("earlier child exited 3", result.stdout)
                runs = list((root / "target/pty/sessions").glob("run-*"))
                self.assertEqual(len(runs), 1)
                run = runs[0]
                records = sorted(run.glob("row-*/session-*.json"))
                self.assertEqual(len(records), 2, "retain the earlier failure, not just the returned session")
                first, last = [json.loads(path.read_text()) for path in records]
                self.assertEqual([first["exit_status"], last["exit_status"]], [3, 0])
                self.assertEqual([first["ordinal"], last["ordinal"]], [1, 2])
                self.assertEqual(first["row"], "earlier-failure")
                self.assertEqual((first["rows"], first["cols"]), (24, 80))
                self.assertEqual(first["argv"][0], sys.executable)
                self.assertEqual(records[0].with_suffix(".bin").read_bytes(), b"FIRST")
                self.assertEqual(records[0].with_suffix(".err").read_bytes(), b"FIRSTERR")
                self.assertEqual(records[1].with_suffix(".bin").read_bytes(), b"READYSECOND:z")
                self.assertEqual(records[1].with_suffix(".err").read_bytes(), b"SECONDERR:z")
                normalize = runner_module().termios_words
                self.assertEqual(normalize(ast.literal_eval(last["termios_before"])),
                                 normalize(ast.literal_eval(last["termios_after"])))
                events = last["events"]
                self.assertEqual([e["at_ns"] for e in events], sorted(e["at_ns"] for e in events))
                typed = [e for e in events if e["event"] == "type-before"]
                self.assertEqual(len(typed), 1)
                self.assertEqual(typed[0]["bytes_hex"], "7a")
                self.assertEqual(typed[0]["stdout_offset"], 5)
                self.assertEqual(typed[0]["stderr_offset"], 0)
                written = [e for e in events if e["event"] == "type-write"]
                self.assertEqual(written[0]["written"], 1)
                for stream, data in (("stdout", b"READYSECOND:z"), ("stderr", b"SECONDERR:z")):
                    chunks = [e for e in events if e["event"] == stream]
                    offset = 0
                    for chunk in chunks:
                        self.assertEqual(chunk["offset"], offset)
                        offset += chunk["size"]
                    self.assertEqual(offset, len(data))
                self.assertIn("finish", [e["event"] for e in events])
                environment = (run / "environment.json").read_text()
                self.assertNotIn("credential-sentinel", environment)
                self.assertNotIn("GITHUB_TOKEN", environment)
                self.assertNotIn(str(root / "home"), environment)

    def test_capture_all_is_opt_in_and_does_not_change_verdict(self):
        with tempfile.TemporaryDirectory(prefix="lair-pty-default-") as temp:
            root = Path(temp)
            result = self.fixture_run(root, "off")
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("earlier child exited 3", result.stdout)
            self.assertFalse((root / "target/pty/sessions").exists())
            self.assertEqual((root / "target/pty/earlier-failure.bin").read_bytes(), b"READYSECOND:z")

    def test_capture_all_keeps_green_session_and_environment(self):
        with tempfile.TemporaryDirectory(prefix="lair-pty-green-") as temp:
            root = Path(temp)
            result = self.fixture_run(root, "option", "green")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            runs = list((root / "target/pty/sessions").glob("run-*"))
            self.assertEqual(len(runs), 1)
            self.assertTrue((runs[0] / "environment.json").is_file())
            captures = list(runs[0].glob("row-*/*.bin"))
            self.assertEqual(len(captures), 1)
            self.assertEqual(captures[0].read_bytes(), b"GREEN")

    def test_row_exception_still_saves_finished_sessions(self):
        with tempfile.TemporaryDirectory(prefix="lair-pty-exception-") as temp:
            root = Path(temp)
            result = self.fixture_run(root, "option", "exceptional")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("fixture row exception", result.stdout)
            captures = list((root / "target/pty/sessions").glob("run-*/row-*/*.bin"))
            self.assertEqual(len(captures), 1)
            self.assertEqual(captures[0].read_bytes(), b"GREEN")

    def test_macos_capture_is_uploaded_on_green(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        job = workflow.split("\n  pack-macos:\n", 1)[1].split("\n  tier:\n", 1)[0]
        self.assertIn("LAIR_PTY_CAPTURE_ALL: '1'", job)
        upload = job.split("uses: actions/upload-artifact@v4", 1)[1]
        self.assertIn("if: ${{ !cancelled() }}", upload)
        self.assertIn("name: pack-macos-evidence", upload)
        self.assertIn("game/target/pty", upload)

    def test_environment_is_measured_and_allowlisted(self):
        runner = runner_module()
        answers = {
            ("/usr/sbin/sysctl", "-n", "hw.ncpu"): "3\n",
            ("/usr/sbin/sysctl", "-n", "hw.physicalcpu"): "3\n",
            ("/usr/sbin/sysctl", "-n", "hw.memsize"): "7516192768\n",
            ("/usr/bin/sw_vers", "-productVersion"): "26.7.2\n",
            ("/usr/bin/sw_vers", "-buildVersion"): "25G332\n",
        }
        def measured(argv, **kwargs):
            self.assertEqual(kwargs["timeout"], 5)
            return types.SimpleNamespace(returncode=0, stdout=answers[tuple(argv)])
        with mock.patch.object(runner.sys, "platform", "darwin"), \
                mock.patch.object(runner.subprocess, "run", side_effect=measured), \
                mock.patch.dict(os.environ, {"ImageOS": "macos26", "ImageVersion": "20261102.0473.1",
                                             "HOME": "private-home-sentinel", "TOKEN": "secret-sentinel"}):
            info = runner.capture_environment()
        self.assertEqual(info["measurements"]["logical_cpus"], "3")
        self.assertEqual(info["measurements"]["memory_bytes"], "7516192768")
        self.assertEqual(info["measurements"]["os_version"], "26.7.2")
        self.assertEqual(info["runner_image"]["ImageVersion"], "20261102.0473.1")
        serialized = json.dumps(info)
        self.assertNotIn("private-home-sentinel", serialized)
        self.assertNotIn("secret-sentinel", serialized)
        self.assertNotIn("hostname", serialized.lower())

    def test_failed_measurement_is_explicit(self):
        runner = runner_module()
        with mock.patch.object(runner.sys, "platform", "darwin"), \
                mock.patch.object(runner.subprocess, "run", side_effect=OSError("unavailable")):
            info = runner.capture_environment()
        self.assertEqual(info["measurements"]["logical_cpus"], {"error": "OSError"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
