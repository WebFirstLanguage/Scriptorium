# Repository hygiene

This is Scriptorium's binding placement and tracking policy, governed by
[GOVERNANCE.md](GOVERNANCE.md). The concrete checker configuration is
[.repo-hygiene.toml](.repo-hygiene.toml). Change policy, configuration, and relevant
tests together when an approved exception or a new repository component requires
them. Do not widen an allowlist solely to silence a violation.

## Preserve the current application layout

Scriptorium predates the new-project standard in
[docs/PROJECT-LAYOUT.md](docs/PROJECT-LAYOUT.md). That standard's proposed module
and theme migrations are not part of this policy. The existing include chain,
large `main.wfl`, `TestPrograms/`, and `sections/` / `templates/` themes remain
deliberate. A migration needs its own proposal and maintainer decision.

| Material | Home |
|---|---|
| Application boot, routing, handlers | `main.wfl` |
| Shared application actions | `app/` |
| Admin templates | `admin/templates/` |
| Public themes | `themes/` |
| Shipped CSS, fonts, logos, other source assets | `static/`, or the owning theme |
| WFL behavior tests | `TestPrograms/` |
| Python automation regression tests | `tests/tooling/` |
| Contributor and CI automation | `scripts/`, `.github/` |
| Maintained docs, designs, screenshots | `docs/` |
| Shared agent instructions | [CLAUDE.md](CLAUDE.md); [AGENTS.md](AGENTS.md) is its discovery adapter |
| Governance and contribution policies | The explicitly allowlisted root policy files |
| Scribe dependency | `lib/scribe`, pinned as a Git submodule |

Keep the root small. Its exhaustive file and directory allowlists are in the
profile. New documentation belongs under `docs/` unless it is an approved root
policy. Keep historical design notes identifiable as historical; they do not
override current policies or maintained architecture documentation. Use issues
for the live backlog and review records for accepted decisions.

## Track inputs; keep mutable state out

Track source, tests, maintained documentation, required configuration, and
purposeful shipped assets. Fonts, screenshots, logos, and other product source
assets are allowed; there is no blanket ban on binary files. Review their
purpose, provenance, licensing, and size.

Do not track site databases or sidecars, uploads, credentials, private keys,
logs, Python or dependency caches, debug dumps, compiled executables, merge
remnants, or temporary output. The only tracked upload entry is the empty
`static/uploads/.gitkeep`. Configure production `data_dir` outside the checkout;
the legacy local database and upload locations remain supported and ignored.
Tests and tools should write transient output to an OS temporary directory or
the ignored `target/` tree (`target/reports/` for local validation reports).
Ignored local runtime data is expected, and the checker does not delete it.

Keep `.wflcfg` a safe shared default; real deployment credentials and private
configuration stay outside tracked source. The checker catches recognizable
secret filenames, not arbitrary credentials hidden in source or configuration.
Contributors and reviewers remain responsible for inspecting contents.

Scribe is upstream-owned. Changes go to its upstream repository and arrive here
through a reviewed pin update using [scripts/update-scribe.sh](scripts/update-scribe.sh).
Do not replace the gitlink with copied files or introduce another submodule
without an explicit policy change. First-party tracked symlinks are disallowed
to keep checkout inspection portable and prevent reads outside the repository.

## Enforcement and its limits

Run from a checkout with Git and Python 3.11 or later:

```sh
python scripts/check_repo_hygiene.py
python -m unittest discover -s tests/tooling -p "test_*.py"
```

The [governance workflow](.github/workflows/governance.yml) runs the hygiene gate
and tooling tests. [testing.md](testing.md) covers the separate WFL test runner.

The checker inspects paths in the Git index **plus nonignored untracked files**,
using their current working-tree contents. This checks new work before staging.
An ignored file already tracked in Git remains subject to every rule. Ignored,
untracked runtime data is excluded. The check is not a staged-content audit or
a test for a clean working tree; run it again after staging changes that alter
which files Git tracks. Indexed files deleted only in the working tree are
reported until the deletion is staged.

It fails on:

- Root entries outside the case-sensitive allowlists; forbidden directory
  components, filenames, and suffix patterns listed in the profile (matched
  case-insensitively).
- Candidate files in declared runtime paths, except the named empty placeholder.
- Missing or empty required policies, documentation, and automation files.
- Missing or unapproved Git gitlinks, copied files under `lib/scribe`, and
  first-party symlinks or nonregular files. Gitlink contents are not traversed;
  Scribe need not be initialized for this check.
- Broken local inline links, image links, and reference-link destinations in
  the root files listed in `[links]`. Targets must exist in the candidate tree;
  links cannot depend on ignored local files or escape the checkout.

Link checking handles the simple Markdown syntax used by these documents;
angle brackets delimit destinations containing spaces. It skips fenced code,
external URLs, anchors, and destinations inside the Scribe gitlink. It does not
validate heading anchors, resolve reference labels, check remote URLs, or parse
every Markdown extension. Required-file checks establish presence, not that the
contents implement sound policy. Secret detection by content, asset provenance,
test adequacy, generated-file justification, compatibility, workflow semantics,
and policy exception approval remain review responsibilities.

The command exits `0` on success, `1` for policy violations, and `2` when the
profile or checkout cannot be inspected reliably. A missing profile, unknown
profile keys, malformed configuration, Git failure, or unresolved merge fails
closed. No check rewrites source, deletes runtime files, or changes Git history.
