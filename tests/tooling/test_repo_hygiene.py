"""Exercise the hygiene command against isolated Git checkouts, never this index."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest


PROJECT = Path(__file__).resolve().parents[2]
CHECKER = PROJECT / "scripts/check_repo_hygiene.py"
PROFILE = PROJECT / ".repo-hygiene.toml"


@unittest.skipUnless(shutil.which("git"), "Git is required for fixture checkouts")
class RepositoryHygieneTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="scriptorium-hygiene-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "--quiet")
        self.profile_text = PROFILE.read_text("utf-8")
        profile = tomllib.loads(self.profile_text)
        for name in profile["required"]["files"]:
            self.write(name, "Fixture file.\n")
        self.write(".repo-hygiene.toml", self.profile_text)
        self.write(".gitignore", "*.db\n*.private\n.env\n__pycache__/\n")
        self.write("README.md", "[Architecture](docs/ARCHITECTURE.md)\n")
        self.write("static/uploads/.gitkeep", "")
        self.write("app/source.wfl", "display \"fixture\"\n")
        self.git("add", ".")
        # A gitlink records a commit object name. No remote, nested checkout, or
        # object download is needed to test that the parent treats it opaquely.
        self.git("update-index", "--add", "--cacheinfo", "160000", "1" * 40, "lib/scribe")

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.root), *args], capture_output=True, check=True
        )

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def run_checker(self):
        return subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(self.root)],
            capture_output=True, text=True, check=False,
        )

    def assert_result(self, code, fragment=None):
        result = self.run_checker()
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, code, output)
        if fragment is not None:
            self.assertIn(fragment, output)
        return output

    def test_clean_checkout_and_uninitialized_submodule_pass(self):
        self.assert_result(0, "Repository hygiene passed")

    def test_new_untracked_root_file_is_checked_before_staging(self):
        self.write("scratch.md", "Unapproved root note\n")
        self.assert_result(1, "HYGIENE: root: scratch.md")

    def test_new_untracked_root_directory_is_rejected(self):
        self.write("notes/design.md", "An unapproved root directory\n")
        self.assert_result(1, "HYGIENE: root: notes/design.md")

    def test_legitimate_new_docs_and_binary_source_assets_pass(self):
        self.write("docs/new-guide.md", "Maintained guide\n")
        self.write("static/fonts/new.woff2", b"wOF2\x00fixture")
        self.write("docs/screenshots/new.png", b"\x89PNG\r\n\x1a\n\x00fixture")
        self.assert_result(0)

    def test_ignored_untracked_runtime_data_is_left_alone(self):
        database = self.write("scriptorium.db", b"private runtime fixture")
        self.write(".env", "TOKEN=fixture\n")
        self.assert_result(0)
        self.assertEqual(database.read_bytes(), b"private runtime fixture")

    def test_force_tracked_ignored_database_is_rejected(self):
        self.write("app/fixture.db", b"runtime fixture")
        self.git("add", "--force", "app/fixture.db")
        self.assert_result(1, "HYGIENE: artifact: app/fixture.db")

    def test_case_variants_and_nested_cache_are_rejected(self):
        # Windows Git may ignore __PyCache__ under the lowercase ignore rule.
        # Make these candidates visible on every platform for this check.
        self.write(".gitignore", "# No ignores in this test.\n")
        for name in ["app/site.SQLITE3-WAL", "docs/server.LOG", "scripts/__PyCache__/bad.txt"]:
            with self.subTest(name=name):
                self.write(name, "fixture\n")
                self.assert_result(1, f"HYGIENE: artifact: {name}")
                (self.root / name).unlink()

    def test_secret_names_are_rejected_at_any_depth(self):
        for name in ["app/.env.production", "docs/id_rsa", "app/secret.KEY"]:
            with self.subTest(name=name):
                self.write(name, "fixture\n")
                self.assert_result(1, f"HYGIENE: artifact: {name}")
                (self.root / name).unlink()

    def test_upload_image_cannot_use_source_asset_exception(self):
        self.write("static/uploads/photo.png", b"\x89PNG\x00runtime fixture")
        self.assert_result(1, "HYGIENE: runtime-state: static/uploads/photo.png")

    def test_only_empty_declared_upload_placeholder_is_allowed(self):
        self.write("static/uploads/.gitkeep", "runtime bytes\n")
        self.assert_result(1, "HYGIENE: runtime-state: static/uploads/.gitkeep")

    def test_removed_and_empty_required_policy_fail(self):
        (self.root / "GOVERNANCE.md").unlink()
        self.assert_result(1, "HYGIENE: required: GOVERNANCE.md")
        self.write("GOVERNANCE.md", "")
        self.assert_result(1, "required file is empty")

    def test_ignored_required_policy_cannot_pass_by_existing_locally(self):
        self.git("rm", "--cached", "--force", "GOVERNANCE.md")
        self.write(".gitignore", "GOVERNANCE.md\n")
        self.assert_result(1, "HYGIENE: required: GOVERNANCE.md")

    def test_worktree_link_changes_are_checked_without_staging(self):
        self.write("README.md", "[Missing](docs/does-not-exist.md)\n")
        self.assert_result(1, "local link is missing from candidate tree")

    def test_link_to_ignored_local_file_cannot_hide_broken_clone(self):
        self.write("docs/local.private", "private fixture\n")
        self.write("README.md", "[Local](docs/local.private)\n")
        self.assert_result(1, "local link is missing from candidate tree")

    def test_links_to_new_candidates_directories_and_encoded_paths_pass(self):
        self.write("docs/new file.md", "New guide\n")
        self.write("README.md", "[Guide](docs/new%20file.md#title)\n[Docs](docs/)\n"
                   "[Spaced](<docs/new file.md>)\n[Ref][guide]\n"
                   "[guide]: docs/new%20file.md \"A guide\"\n")
        self.assert_result(0)

    def test_reference_and_image_link_destinations_are_checked(self):
        self.write("README.md", "![Image](docs/missing.png)\n[ref]: docs/missing.md\n")
        output = self.assert_result(1)
        self.assertIn("docs/missing.png", output)
        self.assertIn("docs/missing.md", output)

    def test_anchors_urls_fences_and_submodule_links_are_skipped(self):
        self.write("README.md", "[Anchor](#unknown)\n[Web](https://example.invalid/nope)\n"
                   "[Mail](mailto:test@example.invalid)\n"
                   "[Scribe](lib/scribe/uninitialized.md)\n"
                   "```md\n[Example](missing.md)\n```\n"
                   "~~~md\n[Example](missing-too.md)\n~~~\n")
        self.assert_result(0)

    def test_links_cannot_escape_checkout(self):
        self.write("README.md", "[Outside](../outside.md)\n")
        self.assert_result(1, "local link leaves checkout")

    def test_submodule_contents_are_not_recursively_inspected(self):
        self.write("lib/scribe/private.db", "upstream runtime fixture\n")
        self.write("lib/scribe/.env", "upstream fixture\n")
        self.assert_result(0)

    def test_scribe_cannot_be_replaced_with_copied_files(self):
        self.git("update-index", "--force-remove", "lib/scribe")
        self.write("lib/scribe/src/scribe.wfl", "copied upstream fixture\n")
        self.assert_result(1, "required Git gitlink is missing")

    def test_another_gitlink_cannot_bypass_artifact_inspection(self):
        self.git("update-index", "--add", "--cacheinfo", "160000", "2" * 40, "lib/other")
        self.assert_result(1, "HYGIENE: submodule: lib/other: unapproved gitlink")

    def test_indexed_symlink_is_rejected_even_when_checked_out_as_text(self):
        target = self.write("app/linked.wfl", "../README.md")
        blob = self.git("hash-object", "-w", str(target)).stdout.decode().strip()
        self.git("update-index", "--add", "--cacheinfo", "120000", blob, "app/linked.wfl")
        self.assert_result(1, "HYGIENE: file-type: app/linked.wfl")

    def test_malformed_profile_fails_closed(self):
        self.write(".repo-hygiene.toml", "schema = [\n")
        self.assert_result(2, "HYGIENE-ERROR")

    def test_missing_profile_fails_closed(self):
        (self.root / ".repo-hygiene.toml").unlink()
        self.assert_result(2, "cannot read .repo-hygiene.toml")

    def test_unknown_profile_key_fails_closed(self):
        self.write(".repo-hygiene.toml", self.profile_text.replace(
            "allowed-dirs =", "allowed-directories ="
        ))
        self.assert_result(2, "missing or unknown keys")

    def test_profile_cannot_use_escape_paths(self):
        self.write(".repo-hygiene.toml", self.profile_text.replace(
            '"docs/ARCHITECTURE.md"', '"../ARCHITECTURE.md"'
        ))
        self.assert_result(2, "non-relative path")

    def test_git_failure_fails_closed(self):
        # Rename only this fixture's .git, without touching the actual checkout.
        (self.root / ".git").rename(self.root / "fixture-index-away")
        self.assert_result(2, "HYGIENE-ERROR: git")


if __name__ == "__main__":
    unittest.main()
