#!/usr/bin/env python3
"""Offline tests for safe sanitizer writes."""
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

SANITIZE = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "sanitize.py"


class SanitizeTests(unittest.TestCase):
    def test_fix_refuses_symlink_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            target = root / "target.md"
            link = root / "link.md"
            target.write_text("smart\u2019 quote")
            link.symlink_to(target)
            proc = subprocess.run([sys.executable, str(SANITIZE), str(link), "--fix"],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(target.read_text(), "smart\u2019 quote")

    def test_fix_preserves_existing_permissions_and_cleans_content(self):
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "draft.md"
            path.write_text("smart\u2019 quote")
            path.chmod(0o640)
            proc = subprocess.run([sys.executable, str(SANITIZE), str(path), "--fix"],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(path.read_text(), "smart' quote")
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)


if __name__ == "__main__":
    unittest.main()
