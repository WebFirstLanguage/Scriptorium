# Contributing to Scriptorium

Scriptorium welcomes fixes, tests, documentation, themes, accessibility work,
and improvements to the CMS. You can contribute through a fork and pull request
without a formal project role. AI-assisted contributions are welcome; the author
remains responsible for understanding and checking the result.

| Document | Purpose |
|---|---|
| [GOVERNANCE.md](GOVERNANCE.md) | Roles, decisions, compatibility, and project authority |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards and reporting |
| [AI_POLICY.md](AI_POLICY.md) | Responsibilities when using AI tools |
| [SECURITY.md](SECURITY.md) | Private vulnerability reporting |
| [testing.md](testing.md) | Required tests, risk assessment, and change evidence |
| [REPOSITORY_HYGIENE.md](REPOSITORY_HYGIENE.md) | File placement and generated output |
| [CLAUDE.md](CLAUDE.md) | Shared agent instructions and development constraints |

Participation is subject to these policies. Report suspected vulnerabilities
privately through [SECURITY.md](SECURITY.md), rather than a public issue or PR.

## Report a bug

Choose **Bug report** when opening a GitHub issue. The canonical form is
[.github/ISSUE_TEMPLATE/bug_report.yml](.github/ISSUE_TEMPLATE/bug_report.yml).
Use a title that names the failing behavior and describe one problem per report;
link an existing report when relevant.

Include the problem and impact, versions and environment, reproduction steps,
expected and actual behavior, and how often it occurs. When available, add the
last working revision, recent changes, a sanitized log or screenshot, and a
workaround. The form explains how to identify the Scriptorium, WFL, and Scribe
versions. Use `Unknown` for unavailable details; you do not need a diagnosis,
failing test, or proposed fix to report a bug.

Reports created through a CLI, API, or agent should include the same information.
Use synthetic examples and inspect attachments for secrets and private site
data. Suspected vulnerabilities follow [SECURITY.md](SECURITY.md) privately.
Blank issues remain available for Contributor applications and other topics.

## Get a working checkout

Install WFL and Git. Python 3.11 or newer runs the repository's development
checks; it is not an application runtime dependency. Clone your fork with the
pinned Scribe submodule:

```sh
git clone --recurse-submodules https://github.com/YOUR-USERNAME/Scriptorium.git
cd Scriptorium
git switch -c fix/describe-the-change
```

For an existing clone, use `git submodule update --init --recursive`. Read
[README.md](README.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), then run
the baseline suites:

```sh
wfl --version
python scripts/run_tests.py
```

Use `--wfl /absolute/path/to/wfl` if the interpreter is not on `PATH`; use
`python3` in environments where that is the Python 3 command. The test profile
records current verification limits; a successful local run does not establish
support for an untested platform or runtime version.

Start a disposable local site with `wfl main.wfl` from the repository root and
open `http://127.0.0.1:8080/`. First run creates a database and presents the
installer. Use synthetic users and content. Set `data_dir` in a disposable
checkout's `.wflcfg` to a temporary directory when exercising persistent state;
keep the database and uploads out of commits. Stop the server when finished.

## Make a focused change

1. Describe the problem and observable acceptance criteria. Seek Maintainer
   agreement for substantial or breaking changes to public routes, schema or
   storage conventions, theme or extension contracts, or the repository layout.
2. For behavior changes, add the smallest useful regression test and run it
   against the old behavior. Keep the expected failure as Red evidence. Fix the
   implementation, verify Green, and exercise affected boundaries as required
   by [testing.md](testing.md).
3. Preserve existing installs and defaults. Include documentation and any
   migration or recovery instructions in the same PR.
4. Run the applicable checks, inspect the final diff, and open a PR with the
   evidence below. Draft PRs are welcome for early review.

Scriptorium's layout is deliberately grandfathered. Keep WFL suites in
`TestPrograms/`, the shared router and handlers in `main.wfl`, and the base
theme's existing `sections/` and `templates/` arrangement. The standard in
[docs/PROJECT-LAYOUT.md](docs/PROJECT-LAYOUT.md) applies to new projects; moving
this repository to it requires a separate, agreed migration.

Read the architecture notes before editing `main.wfl` or `app/`. WFL includes
form a tree; preserve the `util ← db ← auth ← render ← site_ext ← main` chain
and avoid duplicate include paths. Use descriptive qualified names where WFL
reserves common words such as `content`, `status`, `file`, and `count`.

Use [docs/THEMING.md](docs/THEMING.md) for theme work. Preserve body-template
names and fallback behavior. Site-specific routes and boot work belong behind
the contract documented in [app/site_ext.wfl](app/site_ext.wfl); changes to that
contract need tests of both an extension handling a request and stock fallback.

## Check and submit

Run these from the repository root, using the interpreter version recorded on
the PR:

```sh
python scripts/check_repo_hygiene.py
python -m unittest discover -s tests/tooling -v
python scripts/run_tests.py
```

For a Scribe pin, rendering, or template-engine integration change, also run:

```sh
python scripts/run_tests.py --include-scribe
```

The extra suite runs the pinned Scribe tests in a temporary copy because they
write fixtures. Follow [testing.md](testing.md) for HTTP, UI, security, migration,
and recovery checks triggered by the change. Prose-only changes need relevant
link, command, and hygiene checks; they do not need invented application tests.

Keep PRs focused and use conventional commit subjects such as `fix:`, `feat:`,
`docs:`, `test:`, `refactor:`, and `chore:`. Follow the PR format below.

Do not include passwords, session cookies, tokens, user databases, or personal
content in logs or fixtures. A review must resolve blocking findings before
merge. A bot-created dependency PR needs the same evidence as a human-authored
PR; approve any pending workflow run or run the Governance workflow manually on
the proposed branch, then verify the tested revision and runtime results.

GitHub review and branch-protection settings are maintained on the repository
host. Adding these documents or workflows does not configure those settings.

## Pull request format

Use [.github/pull_request_template.md](.github/pull_request_template.md) as the
canonical body format for every PR, including those created through a CLI,
API, agent, or dependency updater. Copy it explicitly when your tool does not
load it. Template completion is a review requirement; it does not replace tests
or Maintainer approval.

Titles use `<type>(<optional scope>): <imperative summary>`, for example
`fix(auth): reject expired sessions` or `docs: clarify theme fallback`.
Describe the final change in the title and body, updating both when scope changes.

Keep these sections in order:

1. **Summary** — the concrete problem, resulting behavior, observable acceptance
   criteria, and related issue when one exists.
2. **Changes** — material implementation changes and reasons a reviewer needs.
3. **Compatibility and risk** — the R0–R3 classification from
   [testing.md](testing.md#change-risk), affected contracts, upgrade/recovery
   steps, and remaining risks or approved exceptions.
4. **Validation** — tested revision and environment, regression evidence, exact
   commands and actual results, and checks of affected user or data boundaries.
5. **Checklist** — confirmations made by the author or reviewing Maintainer
   after inspecting the proposed change.

Replace prompts with evidence and keep details proportional to the change.
Use `N/A — reason` for inapplicable fields and `Not run — reason` for unavailable
checks. Drafts and automated proposals may mark evidence pending; resolve it
under [testing.md](testing.md) before merge. Never pre-check a confirmation or
invent a passing result.
AI disclosure remains optional under [AI_POLICY.md](AI_POLICY.md).

## Scribe changes

`lib/scribe` records an exact upstream commit. Make engine fixes in the upstream
[Scribe repository](https://github.com/WebFirstLanguage/Scribe), then update the
pin here with `scripts/update-scribe.sh` from Bash. Inspect the upstream diff and
run the Scriptorium and pinned Scribe suites before proposing the update.
Do not leave an uncommitted engine patch inside the submodule as the CMS fix.

## Becoming a Contributor

Contributor is an optional trusted role with explicitly delegated access; it is
not required to submit issues or PRs and does not automatically grant merge or
release authority. Maintainers consider care for existing sites, quality of
tests and reviews, respectful communication, and sustained interest. There is
no fixed PR count or credential requirement.

Apply with a public issue titled `Scriptorium Contributor Application` in the
[Scriptorium repository](https://github.com/WebFirstLanguage/Scriptorium), or
email `info@logbie.com` with that subject when private contact details are
needed. Maintainers may also invite contributors. Use this outline:

```text
Preferred name or handle:
GitHub username:
Why you want the role:
Links to contributions, reviews, or relevant work:
Areas of interest (CMS, themes, documentation, tests, security, etc.):
Requested access and intended responsibilities:
Confirmation that you have read the governance, conduct, AI, security,
testing, and repository-hygiene policies:
Private contact details (email applications only):
```

Public issues are public: omit private addresses, phone numbers, and other
non-public personal details. Maintainers review applications and explain the
scope of any granted access. Access can be adjusted or revoked under
[GOVERNANCE.md](GOVERNANCE.md); role status does not transfer project or trademark
ownership. There is no guaranteed application response deadline.
