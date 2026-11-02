#!/usr/bin/env python3
"""Run both engine check entrypoints with stand-in tools, no compiler needed."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class CheckPlanner(unittest.TestCase):
    def test_planner_runs_and_stops_both_engine_gates(self):
        for entry in ("check", "check-linux"):
            for fail in (False, True):
                with self.subTest(entry=entry, fail=fail), tempfile.TemporaryDirectory(prefix="lair-check-") as temp:
                    root = Path(temp)
                    for folder in ("tools", "src", "ci", "bin", "target/native", "target/release"):
                        (root / folder).mkdir(parents=True, exist_ok=True)
                    (root / "src/lair.lu").touch()
                    for name in (entry, "lib-root.sh"):
                        shutil.copy2(ROOT / "tools" / name, root / "tools" / name)
                    for name in ("check-fmt", "test", "build"):
                        path = root / "tools" / name
                        path.write_text('#!/bin/sh\necho "' + name + '" >> "$CALLS"\n')
                        path.chmod(0o755)
                    for tier in ("native", "release"):
                        path = root / "target" / tier / "lair"
                        path.write_text('#!/bin/sh\necho selftest >> "$CALLS"\n')
                        path.chmod(0o755)
                    python = root / "bin/python3"
                    python.write_text('#!/bin/sh\necho "python $*" >> "$CALLS"\ncase "$*" in *tiers-test.py*) exit "$FAIL_PLANNER" ;; esac\n')
                    python.chmod(0o755)
                    calls = root / "calls"
                    env = dict(os.environ, PATH=str(root / "bin") + ":" + os.environ["PATH"],
                               CALLS=str(calls), FAIL_PLANNER="7" if fail else "0")
                    result = subprocess.run(["sh", str(root / "tools" / entry)], cwd=root,
                                            env=env, capture_output=True, text=True)
                    log = calls.read_text()
                    self.assertIn("tiers-test.py", log)
                    if fail:
                        self.assertEqual(result.returncode, 7)
                        self.assertNotIn("build", log)
                        self.assertNotIn("selftest", log)
                    else:
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertIn("memgate-test.py", log)
                        self.assertIn("build", log)


if __name__ == "__main__":
    unittest.main(verbosity=2)
