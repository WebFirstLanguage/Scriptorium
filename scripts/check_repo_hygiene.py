#!/usr/bin/env python3
"""Check Scriptorium's candidate tree against .repo-hygiene.toml.

Uses indexed paths (even ignored ones) plus nonignored untracked paths, reading
their working-tree contents so new changes can be checked before staging.
Python 3.11+ standard library only. Exit: 0 clean, 1 violations, 2 setup error.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tomllib
from urllib.parse import unquote, urlsplit


class SetupError(Exception):
    """The checkout or policy cannot be inspected reliably."""


def git(root: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, check=False
        )
    except OSError as exc:
        raise SetupError(f"cannot execute git: {exc}") from exc
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise SetupError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def load_profile(root: Path) -> dict:
    try:
        profile = tomllib.loads((root / ".repo-hygiene.toml").read_text("utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise SetupError(f"cannot read .repo-hygiene.toml: {exc}") from exc
    expected = {
        "root": {"allowed-files", "allowed-dirs"},
        "required": {"files", "gitlinks"},
        "forbidden": {"dirs", "names", "patterns", "paths", "allowed-placeholders"},
        "links": {"files"},
    }
    if type(profile.get("schema")) is not int or profile["schema"] != 1:
        raise SetupError("profile schema must be 1")
    if set(profile) != {"schema", *expected}:
        raise SetupError("profile has missing or unknown sections")
    for section, keys in expected.items():
        table = profile.get(section)
        if not isinstance(table, dict) or set(table) != keys:
            raise SetupError(f"profile [{section}] has missing or unknown keys")
        for key, values in table.items():
            if not isinstance(values, list) or not all(
                isinstance(value, str) and value for value in values
            ) or len(values) != len(set(values)):
                raise SetupError(f"profile {section}.{key} must be unique nonempty strings")
            if section in {"root", "required", "links"} or key in {
                "paths", "allowed-placeholders"
            }:
                for value in values:
                    parts = PurePosixPath(value).parts
                    if (value.startswith("/") or "\\" in value or ":" in value
                            or ".." in parts or "." in value.split("/")
                            or str(PurePosixPath(value)) != value):
                        raise SetupError(f"profile contains non-relative path: {value}")
                    if section == "root" and len(parts) != 1:
                        raise SetupError(f"root allowlist entry must be a base name: {value}")
    return profile


def candidate_files(root: Path) -> dict[str, str]:
    """Index modes distinguish symlinks and gitlinks, including on Windows."""
    checkout = os.fsdecode(git(root, "rev-parse", "--show-toplevel")).strip()
    if Path(checkout).resolve() != root:
        raise SetupError(f"--root must be the checkout root ({checkout})")
    entries: dict[str, str] = {}
    for record in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not record:
            continue
        metadata, name = record.split(b"\t", 1)
        mode, _, stage = metadata.split()
        if stage != b"0":
            raise SetupError(f"unresolved merge in {os.fsdecode(name)}")
        entries[os.fsdecode(name)] = mode.decode("ascii")
    for name in git(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0"):
        if name:
            entries.setdefault(os.fsdecode(name), "untracked")
    return entries


def under(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix + "/")


def markdown_destinations(source: str):
    """The policy docs use simple inline links and reference definitions.

    This deliberately isn't a complete Markdown parser. Destinations with spaces
    use angle brackets. Anchors and reference-label resolution aren't validated.
    """
    source = re.sub(r"(?ms)^ {0,3}(`{3,}|~{3,})[^\n]*\n.*?^ {0,3}\1\s*$", "", source)
    pattern = r"\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+[\"'][^\n]*?[\"'])?\s*\)"
    for match in re.finditer(pattern, source):
        yield match.group(1).strip("<>")
    for match in re.finditer(r"(?m)^ {0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)", source):
        yield match.group(1).strip("<>")


def check(root: Path, profile: dict, entries: dict[str, str]) -> list[str]:
    violations: list[str] = []

    def fail(rule: str, name: str, detail: str):
        violations.append(f"HYGIENE: {rule}: {name}: {detail}")

    gitlinks = set(profile["required"]["gitlinks"])
    forbidden = profile["forbidden"]
    for name, mode in sorted(entries.items()):
        parts = PurePosixPath(name).parts
        path = root / name
        if (len(parts) == 1 and name not in profile["root"]["allowed-files"]) or (
            len(parts) > 1 and parts[0] not in profile["root"]["allowed-dirs"]
        ):
            fail("root", name, "root entry is not in .repo-hygiene.toml")
        if mode == "160000":
            if name not in gitlinks:
                fail("submodule", name, "unapproved gitlink")
            continue
        if any(under(name, link) for link in gitlinks):
            fail("submodule", name, "Scribe must be an opaque gitlink, not copied files")
        if mode == "120000" or path.is_symlink() or not path.resolve().is_relative_to(root):
            fail("file-type", name, "first-party symlinks and paths outside the checkout are not allowed")
            continue
        if not path.is_file():
            fail("file-type", name, "candidate is missing or is not a regular file")
            continue
        lower_parts = [part.lower() for part in parts]
        if any(part in {item.lower() for item in forbidden["dirs"]} for part in lower_parts[:-1]):
            fail("artifact", name, "cache or generated-output directory")
        if lower_parts[-1] in {item.lower() for item in forbidden["names"]} or any(
            fnmatch.fnmatchcase(lower_parts[-1], pattern.lower())
            for pattern in forbidden["patterns"]
        ):
            fail("artifact", name, "runtime, secret, cache, or generated-output filename")
        if any(under(name.lower(), prefix.lower()) for prefix in forbidden["paths"]):
            if name not in forbidden["allowed-placeholders"] or path.stat().st_size != 0:
                fail("runtime-state", name, "runtime paths allow only declared empty .gitkeep files")

    for name in profile["required"]["files"]:
        path = root / name
        if name not in entries or not path.is_file() or path.is_symlink():
            fail("required", name, "required file is absent from the candidate tree")
        elif path.stat().st_size == 0:
            fail("required", name, "required file is empty")
    for name in sorted(gitlinks):
        if entries.get(name) != "160000":
            fail("submodule", name, "required Git gitlink is missing")

    for name in profile["links"]["files"]:
        path = root / name
        if name not in entries or not path.is_file() or path.is_symlink():
            continue
        try:
            source = path.read_text("utf-8")
        except (OSError, UnicodeError) as exc:
            fail("links", name, f"cannot read Markdown as UTF-8: {exc}")
            continue
        for destination in markdown_destinations(source):
            url = urlsplit(destination)
            if url.scheme or url.netloc or not url.path:
                continue
            relative = unquote(url.path)
            target = path.parent / relative
            resolved = target.resolve()
            if not resolved.is_relative_to(root):
                fail("links", name, f"local link leaves checkout: {destination}")
                continue
            relative_target = resolved.relative_to(root).as_posix()
            if any(under(relative_target, link) for link in gitlinks):
                continue
            # Existence alone would let ignored, private local files hide a broken
            # link in a fresh clone. Require an actual candidate or directory.
            known = relative_target == "." or relative_target in entries or any(
                under(candidate, relative_target) for candidate in entries
            )
            if not target.exists() or not known:
                fail("links", name, f"local link is missing from candidate tree: {destination}")
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        profile = load_profile(root)
        entries = candidate_files(root)
        violations = check(root, profile, entries)
    except (SetupError, OSError, ValueError) as exc:
        print(f"HYGIENE-ERROR: {exc}", file=sys.stderr)
        return 2
    for violation in violations:
        print(violation)
    if not violations:
        print(f"Repository hygiene passed ({len(entries)} candidate paths).")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
