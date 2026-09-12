#!/usr/bin/env python3
"""Run Scriptorium's WFL test suites."""

import argparse
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def positive_seconds(value):
    try:
        seconds = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be a positive number") from exc
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("timeout must be finite and greater than zero")
    return seconds


def run_suite(executable, suite, directory, timeout, label):
    print(f"\n=== {label} ===", flush=True)
    try:
        result = subprocess.run(
            [executable, "--test", str(suite)],
            cwd=directory,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"FAIL {label}: timeout after {timeout:g} seconds", file=sys.stderr, flush=True)
        return False
    except OSError as exc:
        print(f"FAIL {label}: {exc}", file=sys.stderr, flush=True)
        return False
    if result.returncode != 0:
        print(f"FAIL {label}: exit {result.returncode}", file=sys.stderr, flush=True)
        return False
    print(f"PASS {label}", flush=True)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wfl", default="wfl", help="WFL executable (default: wfl on PATH)")
    parser.add_argument("--include-scribe", action="store_true",
                        help="also run the pinned Scribe suite in a temporary copy")
    parser.add_argument("--timeout", type=positive_seconds, default=120,
                        help="maximum seconds per suite (default: 120)")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    suites = sorted(path for path in (root / "TestPrograms").rglob("*.test.wfl")
                    if path.is_file())
    if not suites:
        parser.error("no WFL test suites found under TestPrograms/")
    executable = shutil.which(args.wfl)
    if executable is None:
        parser.error(f"WFL executable not found: {args.wfl}")
    executable = str(Path(executable).resolve())
    scribe = root / "lib" / "scribe"
    if args.include_scribe:
        for required in (scribe / "src" / "scribe.wfl", scribe / "tests" / "scribe.test.wfl"):
            if not required.is_file():
                parser.error(f"missing Scribe file: {required}; initialize the pinned submodule")

    results = []
    try:
        for suite in suites:
            label = suite.relative_to(root).as_posix()
            results.append(run_suite(executable, suite, root, args.timeout, label))
        if args.include_scribe:
            # Upstream tests write build/ fixtures. Never write those into the
            # dependency checkout or carry stale output into a test run.
            with tempfile.TemporaryDirectory(prefix="scriptorium-scribe-tests-") as temporary:
                copy = Path(temporary) / "scribe"
                shutil.copytree(scribe, copy, ignore=shutil.ignore_patterns(".git", "build", "__pycache__"))
                (copy / "build").mkdir()
                results.append(run_suite(
                    executable, copy / "tests" / "scribe.test.wfl", copy, args.timeout,
                    "lib/scribe/tests/scribe.test.wfl (temporary copy)",
                ))
    except OSError as exc:
        print(f"Test setup or cleanup failed: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Test run interrupted", file=sys.stderr)
        return 130
    failures = len(results) - sum(results)
    print(f"\n{len(results)} suites: {sum(results)} passed, {failures} failed", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
