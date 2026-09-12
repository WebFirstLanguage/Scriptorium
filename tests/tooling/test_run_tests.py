"""Exercise the test runner as a process with a controlled interpreter."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


RUNNER = Path(__file__).resolve().parents[2] / "scripts" / "run_tests.py"


class RunTestsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="scriptorium-runner-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        shutil.copy2(RUNNER, self.root / "scripts" / "run_tests.py")
        (self.root / "TestPrograms").mkdir()
        fake = self.root / "fake_wfl.py"
        fake.write_text(
            "import json, pathlib, sys, time\n"
            "suite = pathlib.Path(sys.argv[2])\n"
            "case = json.loads(suite.read_text())\n"
            "print('RUN ' + json.dumps({'suite': str(suite), "
            "'cwd': str(pathlib.Path.cwd()), 'build_exists': pathlib.Path('build').is_dir()}), flush=True)\n"
            "if case.get('stderr'): print(case['stderr'], file=sys.stderr, flush=True)\n"
            "time.sleep(case.get('sleep', 0))\n"
            "sys.exit(case.get('exit', 0))\n",
            encoding="utf-8",
        )
        if os.name == "nt":
            self.interpreter = self.root / "fake-wfl.cmd"
            self.interpreter.write_text(
                f'@echo off\n"{sys.executable}" "{fake}" %*\n', encoding="utf-8"
            )
        else:
            self.interpreter = self.root / "fake-wfl"
            self.interpreter.write_text(
                f"#!{sys.executable}\n" + fake.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            self.interpreter.chmod(0o755)

    def suite(self, name="one.test.wfl", **behavior):
        path = self.root / "TestPrograms" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(behavior), encoding="utf-8")
        return path

    def run_runner(self, *args):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / "run_tests.py"),
             "--wfl", str(self.interpreter), *args],
            cwd=self.root.parent,
            text=True,
            capture_output=True,
            timeout=15,
        )

    @staticmethod
    def runs(result):
        return [json.loads(line[4:]) for line in result.stdout.splitlines()
                if line.startswith("RUN ")]

    def test_discovers_nested_suites_in_order_and_uses_repository_cwd(self):
        self.suite("z.test.wfl")
        self.suite("nested/a.test.wfl")
        (self.root / "TestPrograms" / "example.wfl").write_text("not a suite")
        result = self.run_runner()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        runs = self.runs(result)
        self.assertEqual([Path(run["suite"]).name for run in runs],
                         ["a.test.wfl", "z.test.wfl"])
        self.assertTrue(all(Path(run["cwd"]) == self.root for run in runs))

    def test_failing_suite_preserves_diagnostics_and_later_suite_runs(self):
        self.suite("a.test.wfl", exit=7, stderr="intentional fixture failure")
        self.suite("b.test.wfl")
        result = self.run_runner()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(len(self.runs(result)), 2)
        self.assertIn("intentional fixture failure", result.stderr)
        self.assertIn("a.test.wfl", result.stdout + result.stderr)

    def test_timeout_fails_and_later_suite_still_runs(self):
        self.suite("a.test.wfl", sleep=2)
        self.suite("b.test.wfl")
        result = self.run_runner("--timeout", "1")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(len(self.runs(result)), 2)
        self.assertIn("timeout", (result.stdout + result.stderr).lower())

    def test_empty_suite_set_is_an_error(self):
        result = self.run_runner()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no", (result.stdout + result.stderr).lower())

    def test_missing_interpreter_is_an_error(self):
        self.suite()
        result = self.run_runner("--wfl", str(self.root / "absent-wfl"))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.runs(result), [])

    def test_nonpositive_and_nonfinite_timeout_are_rejected(self):
        self.suite()
        for value in ("0", "-1", "nan", "inf"):
            with self.subTest(value=value):
                result = self.run_runner("--timeout", value)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.runs(result), [])

    def test_missing_scribe_source_is_an_error(self):
        self.suite()
        result = self.run_runner("--include-scribe")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("scribe", (result.stdout + result.stderr).lower())

    def test_upstream_suite_runs_in_disposable_copy_with_build_directory(self):
        self.suite()
        scribe = self.root / "lib" / "scribe"
        (scribe / "src").mkdir(parents=True)
        (scribe / "src" / "scribe.wfl").write_text("fixture")
        (scribe / "tests").mkdir()
        (scribe / "tests" / "scribe.test.wfl").write_text("{}")
        (scribe / "build").mkdir()
        (scribe / "build" / "existing.txt").write_text("preserve")
        result = self.run_runner("--include-scribe")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        runs = self.runs(result)
        self.assertEqual(len(runs), 2)
        upstream = Path(runs[-1]["cwd"])
        self.assertNotEqual(upstream, scribe)
        self.assertTrue(runs[-1]["build_exists"])
        self.assertFalse(upstream.exists(), "temporary Scribe copy was not removed")
        self.assertEqual((scribe / "build" / "existing.txt").read_text(), "preserve")


if __name__ == "__main__":
    unittest.main()
