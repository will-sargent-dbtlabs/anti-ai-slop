#!/usr/bin/env python3
"""Offline tests for the Ringer grader; no model, credentials, or dependencies."""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
GRADE = SCRIPTS / "grade.py"
VALIDATOR = SCRIPTS / "validate_review.py"


def finding(line=1, quote="The team shipped it."):
    return {"line": line, "issue": "unsupported wording", "quote": quote, "fix": "revise"}


def verdict(value="PASS"):
    return {"verdict": value, "blocking": [], "fix": [], "note": [], "unverifiable": []}


class GradeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.original = self.root / "original.md"
        self.rewrite = self.root / "rewrite.md"
        self.original.write_text("A source sentence.\n")
        self.rewrite.write_text("The team shipped it.\n")
        self.fake = self.root / "ringer"
        self.fake.write_text(textwrap.dedent(f'''\
            #!/usr/bin/env python3
            import json, os, pathlib, sys
            args = sys.argv[1:]
            if args == ["--help"]: print("usage: ringer [lint] [run]"); raise SystemExit(0)
            if args[0] == "lint": raise SystemExit(0)
            if args[0] != "run": raise SystemExit(3)
            manifest = json.load(open(args[1]))
            pathlib.Path(os.environ["MANIFEST_CAPTURE"]).write_text(json.dumps(manifest))
            if os.environ.get("MUTATE_REWRITE"):
                pathlib.Path(os.environ["MUTATE_REWRITE"]).write_text("Forged replacement text.\\n")
            for task in manifest["tasks"]:
                td = pathlib.Path(manifest["workdir"]) / task["key"]
                td.mkdir(parents=True, exist_ok=True)
                mode = os.environ.get("FAKE_MODE")
                if mode == "missing" and task["key"] == "reviewer_2": continue
                if mode == "sleep": import time; time.sleep(10)
                raw = os.environ.get("FAKE_VERDICT", '{{"verdict":"PASS","blocking":[],"fix":[],"note":[],"unverifiable":[]}}')
                if mode == "malformed": raw = '{{"verdict":"PASS"}}'
                payload = json.loads(raw)
                (td / "verdict.json").write_text(json.dumps(payload))
            raise SystemExit(int(os.environ.get("FAKE_EXIT", "0")))
        '''))
        self.fake.chmod(0o700)
        self.env = dict(os.environ, RINGER_BIN=str(self.fake), MANIFEST_CAPTURE=str(self.root / "manifest.json"))

    def tearDown(self):
        self.temp.cleanup()

    def run_grade(self, *args, env=None):
        return subprocess.run([sys.executable, str(GRADE), str(self.original), str(self.rewrite), *args],
                              text=True, capture_output=True, env=env or self.env, timeout=20)

    def test_consent_is_required_before_draft_read_or_ringer(self):
        self.original.unlink()
        proc = subprocess.run([sys.executable, str(GRADE), str(self.original), str(self.rewrite)],
                              capture_output=True, text=True, env=self.env)
        self.assertEqual(proc.returncode, 2)
        self.assertFalse((self.root / "manifest.json").exists())
        self.assertIn("--allow-model-review", proc.stderr)

    def test_manifest_and_private_artifacts_for_two_reviewers(self):
        proc = self.run_grade("--allow-model-review", "--reviewer", "codex:gpt-6-luna",
                              "--reviewer", "codex:gpt-6-terra", "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        m = json.loads((self.root / "manifest.json").read_text())
        self.assertEqual(len(m["tasks"]), 2)
        for task in m["tasks"]:
            self.assertEqual(task["max_attempts"], 1)
            self.assertFalse(task["full_access"])
            self.assertEqual(task["task_type"], "code-review")
            self.assertTrue(task["redact_spec"])
            self.assertEqual(task["expect_files"], ["verdict.json"])
            self.assertIn("validate_review.py", task["check"])
            self.assertIn("When reviewing a work document", task["spec"])
            self.assertIn("each paragraph one main idea", task["spec"].lower())
            self.assertIn("Selected document type: comment", task["spec"])
        run_dir = pathlib.Path(json.loads(proc.stdout)["run_dir"])
        self.assertEqual(run_dir.stat().st_mode & 0o777, 0o700)
        for name in ("manifest.json", "original.snapshot", "rewrite.snapshot",
                     "lint.out", "lint.err", "run.out", "run.err"):
            self.assertEqual((run_dir / name).stat().st_mode & 0o777, 0o600, name)
        self.assertEqual((run_dir / "original.snapshot").stat().st_mode & 0o777, 0o600)
        self.assertEqual((run_dir / "rewrite.snapshot").stat().st_mode & 0o777, 0o600)
        self.assertEqual((run_dir / "run.out").stat().st_mode & 0o777, 0o600)
        self.assertEqual((run_dir / "lint.out").stat().st_mode & 0o777, 0o600)
        self.assertEqual((run_dir / "lint.err").stat().st_mode & 0o777, 0o600)
        self.assertEqual((run_dir / "run.err").stat().st_mode & 0o777, 0o600)

    def test_document_type_selection_and_policy(self):
        # Auto uses original length, even when the rewrite is much shorter.
        self.original.write_text(" ".join(["source"] * 81))
        self.rewrite.write_text("Short rewrite.\n")
        proc = self.run_grade("--allow-model-review", "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["document_type"], "report")
        task = json.loads((self.root / "manifest.json").read_text())["tasks"][0]
        self.assertIn("Selected document type: report", task["spec"])

    def test_auto_comment_and_prose_do_not_force_tldr(self):
        self.original.write_text("Short source.")
        for args, selected in (([], "comment"), (["--document-type", "comment"], "comment"),
                               (["--document-type", "prose"], "prose")):
            proc = self.run_grade("--allow-model-review", "--json", *args)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["document_type"], selected)
            task = json.loads((self.root / "manifest.json").read_text())["tasks"][0]
            self.assertIn("Selected document type: " + selected, task["spec"])
            if selected in ("comment", "prose"):
                self.assertIn("Do not require a TL;DR heading", task["spec"])

    def test_invalid_document_type_fails_before_ringer(self):
        proc = self.run_grade("--allow-model-review", "--document-type", "memo")
        self.assertEqual(proc.returncode, 2)
        self.assertFalse((self.root / "manifest.json").exists())

    def test_missing_bundled_policy_fails_before_ringer(self):
        sys.path.insert(0, str(SCRIPTS))
        import grade
        from unittest.mock import patch
        with patch.object(grade, "WORK_WRITING", self.root / "missing-work-writing.md"):
            result = grade.main([str(self.original), str(self.rewrite), "--allow-model-review"])
        self.assertEqual(result, 2)
        self.assertFalse((self.root / "manifest.json").exists())

    def test_valid_fail_is_exit_one(self):
        env = dict(self.env, FAKE_VERDICT=json.dumps(verdict("FAIL")))
        proc = self.run_grade("--allow-model-review", env=env)
        self.assertEqual(proc.returncode, 1)

    def test_end_to_end_pass_with_blocking_finding_is_malformed(self):
        env = dict(self.env, FAKE_VERDICT=json.dumps({**verdict("PASS"), "blocking": [finding()]}))
        proc = self.run_grade("--allow-model-review", env=env)
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)

    def test_end_to_end_pass_with_fix_or_unverifiable_is_malformed(self):
        for section, value in (("fix", [finding()]), ("unverifiable", ["claim not evidenced"])):
            with self.subTest(section=section):
                env = dict(self.env, FAKE_VERDICT=json.dumps({**verdict("PASS"), section: value}))
                proc = self.run_grade("--allow-model-review", env=env)
                self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)

    def test_rewrite_mutation_after_manifest_does_not_break_snapshot_evidence(self):
        # Worker changes the caller's path after manifest creation. Findings must bind
        # to the private startup snapshot that was also included in the task prompt.
        env = dict(self.env, MUTATE_REWRITE=str(self.rewrite),
                   FAKE_VERDICT=json.dumps({**verdict("FAIL"), "blocking": [finding()]}))
        proc = self.run_grade("--allow-model-review", "--json", env=env)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        manifest = json.loads((self.root / "manifest.json").read_text())
        self.assertIn("The team shipped it.", manifest["tasks"][0]["spec"])
        self.assertEqual(self.rewrite.read_text(), "Forged replacement text.\n")

    def test_prompt_requires_exact_task_verdict_file_and_single_file_write(self):
        self.run_grade("--allow-model-review")
        task = json.loads((self.root / "manifest.json").read_text())["tasks"][0]
        spec = task["spec"]
        self.assertIn("stdout-only output is invalid", spec.lower())
        self.assertIn("verdict.json", spec)
        self.assertIn("no actions are allowed except one file write", spec.lower())
        self.assertIn("write", spec.lower())
        self.assertIn(str(pathlib.Path(json.loads((self.root / "manifest.json").read_text())["workdir"]) / "reviewer_1" / "verdict.json"), spec)

    def test_lint_failure_stops_before_ringer_workers(self):
        self.rewrite.write_text((HERE / "fixtures" / "slop.md").read_text())
        proc = self.run_grade("--allow-model-review")
        self.assertEqual(proc.returncode, 1)
        self.assertFalse((self.root / "manifest.json").exists())

    def test_nonzero_ringer_fails_closed(self):
        proc = self.run_grade("--allow-model-review", env=dict(self.env, FAKE_EXIT="9"))
        self.assertEqual(proc.returncode, 2)

    def test_malformed_verdict_fails_closed(self):
        proc = self.run_grade("--allow-model-review", env=dict(self.env, FAKE_MODE="malformed"))
        self.assertEqual(proc.returncode, 2)

    def test_timeout_fails_closed(self):
        proc = self.run_grade("--allow-model-review", "--timeout", "3",
                              env=dict(self.env, FAKE_MODE="sleep"))
        self.assertEqual(proc.returncode, 2)

    def test_missing_ringer_fails_without_credentials(self):
        env = dict(self.env, RINGER_BIN=str(self.root / "missing"))
        proc = self.run_grade("--allow-model-review", env=env)
        self.assertEqual(proc.returncode, 2)

    def test_shell_metacharacters_in_input_path_are_quoted_as_data(self):
        odd = self.root / "draft ; $(echo nope).md"
        odd.write_text("The team shipped it.\n")
        self.rewrite = odd
        proc = self.run_grade("--allow-model-review")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        manifest = json.loads((self.root / "manifest.json").read_text())
        self.assertIn("rewrite.snapshot", manifest["tasks"][0]["check"])
        self.assertNotIn(str(odd.resolve()), manifest["tasks"][0]["check"])

    def test_consent_gate_does_not_resolve_or_open_inputs(self):
        sys.path.insert(0, str(SCRIPTS))
        import grade
        from unittest.mock import patch
        with patch.object(grade, "resolve_ringer", side_effect=AssertionError("spawn resolution")), \
                patch.object(grade, "safe_regular_file", side_effect=AssertionError("input access")):
            self.assertEqual(grade.main([str(self.original), str(self.rewrite)]), 2)

    def test_missing_one_reviewer_fails_closed(self):
        proc = self.run_grade("--allow-model-review", "--reviewer", "codex:a", "--reviewer", "codex:b",
                              env=dict(self.env, FAKE_MODE="missing"))
        self.assertEqual(proc.returncode, 2)

    def test_validator_rejects_wrong_quote_and_bool_line(self):
        result = self.root / "result.json"
        for item in (finding(quote="not present"), finding(line=True)):
            result.write_text(json.dumps({**verdict("FAIL"), "blocking": [item]}))
            proc = subprocess.run([sys.executable, str(VALIDATOR), "--rewrite", str(self.rewrite),
                                   "--verdict", str(result)], capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)

    def test_validator_rejects_duplicate_json_keys(self):
        result = self.root / "result.json"
        result.write_text('{"verdict":"PASS","verdict":"FAIL","blocking":[],"fix":[],"note":[],"unverifiable":[]}')
        proc = subprocess.run([sys.executable, str(VALIDATOR), "--rewrite", str(self.rewrite),
                               "--verdict", str(result)], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)

    def test_validator_accepts_valid_findings_even_when_verdict_fails(self):
        result = self.root / "result.json"
        result.write_text(json.dumps({**verdict("FAIL"), "blocking": [finding()]}))
        proc = subprocess.run([sys.executable, str(VALIDATOR), "--rewrite", str(self.rewrite),
                               "--verdict", str(result)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_check_setup_is_read_only(self):
        proc = subprocess.run([sys.executable, str(GRADE), "--check-setup", "--ringer", str(self.fake)],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse((self.root / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
