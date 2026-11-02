#!/usr/bin/env python3
"""tools/perf must retain perf-idle diagnostics AND its failing status.

The executable passes every render bar, then exits before its first key.
This is the original stale-save failure without touching any real save.
Run inside the Linux test container (the real latency row uses a pty).
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class PerfStatus(unittest.TestCase):
    def test_latency_failure_reaches_perf_exit(self):
        with tempfile.TemporaryDirectory(prefix="lair-perf-") as temp:
            root = Path(temp)
            (root / "tools").mkdir()
            (root / "src").mkdir()
            (root / "src/lair.lu").touch()
            for name in ("perf", "perf-idle", "pty", "memgate.py", "lib-root.sh", "lib-mem.sh"):
                shutil.copy2(ROOT / "tools" / name, root / "tools" / name)
            binary = root / "failed-game"
            binary.write_text('#!/bin/sh\nif [ "$1" = --bench ]; then echo "avg_us 1 p99_us 1 max_us 1"; exit 0; fi\necho "lair: synthetic_latency_failure" >&2\nexit 2\n')
            binary.chmod(0o755)
            result = subprocess.run(["sh", str(root / "tools/perf"), "--bin", str(binary)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            summary = (root / "target/perf/summary.txt").read_text()
            self.assertIn("latency FAILED", summary, result.stdout + result.stderr)
            self.assertIn("synthetic_latency_failure", summary)
            self.assertEqual(summary.count("avg 1 us <"), 4)
            self.assertNotEqual(result.returncode, 0, "perf swallowed the latency failure after four passing render bars")


if __name__ == "__main__":
    unittest.main(verbosity=2)
