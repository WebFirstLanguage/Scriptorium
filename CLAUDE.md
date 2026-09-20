# Scriptorium — shared agent instructions

Scriptorium is a WordPress-style CMS written entirely in **WFL**, rendering
through the **Scribe** template engine (a git submodule at `lib/scribe`) and
persisting to SQLite. Start with [`README.md`](README.md), then
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Project governance

Scriptorium is maintainer-led; Brad is the primary Maintainer. The binding
policies live at the repository root:

| Document | Purpose |
|---|---|
| [GOVERNANCE.md](GOVERNANCE.md) | Roles, decisions, compatibility, releases, and amendments |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution workflow and Contributor applications |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community conduct and reporting |
| [AI_POLICY.md](AI_POLICY.md) | AI-assisted work is welcome; authors remain accountable |
| [SECURITY.md](SECURITY.md) | Private vulnerability reporting and security scope |
| [testing.md](testing.md) | Required test evidence, risk triggers, and current gaps |
| [REPOSITORY_HYGIENE.md](REPOSITORY_HYGIENE.md) | Content placement, runtime data, and the enforced hygiene profile |

Protect existing databases, uploads, URLs, theme contracts, and extension
hooks. Behavioral changes need failing-then-passing test evidence and updated
docs in the same change. Documentation-only changes need relevant validation,
not artificial application tests. Do not log or commit secrets or real site
data. Maintainers own merges, releases, access grants, and policy exceptions;
AI assistance does not change that authority or the quality bar.

`AGENTS.md` points here so agent guidance has one canonical home. Keep this
section and the root policies aligned when changing contribution workflow.

## The one rule that catches everyone

**[`docs/PROJECT-LAYOUT.md`](docs/PROJECT-LAYOUT.md) is the house standard for
NEW WFL projects. This repository does not follow it, and that is deliberate.**

Scriptorium predates the policy. Its `main.wfl` is one 51 KB file, its themes use
`sections/` + `templates/`, and its tests live in `TestPrograms/`. All three
violate the standard.

- **Do not "fix" this repo to match the policy as a drive-by.** Retrofitting it
  is a separate, deliberate migration that has not been approved.
- **Do apply the policy in full** when scaffolding a new project, or when asked
  what shape something new should take.
- If a change here would move the repo toward the standard anyway, say so and let
  Brad decide — don't fold it silently into unrelated work.

## Working in this repo

- **Read `docs/ARCHITECTURE.md` before changing `main.wfl` or `app/`.** It
  catalogues the WFL constraints that shaped the design. The structure looks odd
  until you know which limitation forced it. Most importantly: **includes form a
  tree, not a flat namespace — diamonds break.** The library chain
  `util ← db ← auth ← render` is load-bearing, and the router plus every handler
  live in `main.wfl` because they must share one scope.
- **Reserved words.** `store`, `count`, `data`, `content`, `status`, `header`,
  `file`, `port`, `error`, `find`, `one` and friends are WFL keywords. Qualify
  identifiers instead: `the_status`, `media_row`, `db_path`.
- **Run from the repo root.** Template and asset paths resolve relative to the
  working directory.
- **Bug reports:** follow [CONTRIBUTING.md](CONTRIBUTING.md#report-a-bug) and
  [.github/ISSUE_TEMPLATE/bug_report.yml](.github/ISSUE_TEMPLATE/bug_report.yml),
  including for reports created through a CLI or API. Record observed behavior,
  reproduction steps, expected/actual results, and known versions; mark unknown
  details honestly. Use sanitized evidence and the private security channel
  for suspected vulnerabilities.
- **Pull requests:** follow the title convention and body format in
  [CONTRIBUTING.md](CONTRIBUTING.md#pull-request-format), using
  [.github/pull_request_template.md](.github/pull_request_template.md) even when
  creating a PR through a CLI or API. Keep all five sections, scale the detail
  to the change, and update the title and body to match the final diff. Record
  actual check results and explain inapplicable or unavailable evidence.
- **Scribe is a submodule.** Don't edit `lib/scribe/` in place; changes go
  upstream to WebFirstLanguage/Scribe, then bump via
  `scripts/update-scribe.sh`.
- **Checks:** `wfl --execution-timeout 1200 scripts/run_tests.wfl` runs the complete suite: application,
  ORM/migrations/recovery, HTTP integration, tooling, executable examples, and
  pinned Scribe. `--group tooling` or `--group application` selects a focused
  run. Run `python scripts/check_repo_hygiene.py` for the repository hygiene gate.
  Every test, fixture, assertion, helper and driver is WFL. Python 3.11+ and Git
  are required only for the hygiene checker's implementation subject. The runner
  uses the WFL executable that launched it, with an optional `--wfl` override.
  It needs the owned-process completion and `current_executable` runtime APIs.
  Governance provisions WFL and runs tooling and hygiene on Blacksmith Linux
  and GitHub-hosted Windows. WFL tests runs the complete suite on Blacksmith
  using a freshly pulled `bsbyrdwfl/wfl:nightly` image;
  its summary records the resolved image digest, runtime version, and source
  revisions. See
  [testing.md](testing.md) for commands, coverage limits, and merge evidence.
- **`data_dir` and `web_server_port` are application configuration.**
  `main.wfl` reads `.wflcfg` itself at boot using helpers in `app/util.wfl`;
  the runtime does not apply these keys. The HTTP port accepts whole numbers
  from 1 to 65535 and defaults to 8080 for a missing file or setting, or an
  empty, malformed, fractional, or out-of-range value. Restart after changing it.

## Known gaps worth knowing before you touch rendering

- **Theme selection is configurable now.** `render_public` resolves
  `<theme_root>/<theme>/body/<name>.html`, then `.../templates/<name>.html`,
  then the base theme, where `theme` and `theme_root` come from `.wflcfg`.
  `main.wfl` applies them at boot via `set_public_theme`; a module-level `store`
  is used because `main.wfl` cannot assign to a variable defined in an included
  file, only call an action that does. This closes the gap
  `docs/PROJECT-LAYOUT.md` §6.1 describes — a site with a custom theme no longer
  needs a patched clone. Unset keys keep the exact legacy behaviour.
- **`app/site_ext.wfl` is the site-extension seam**, and it is why `main.wfl`
  includes it rather than `render.wfl`. A deployment replaces that one file to
  add its own routes, tables and boot work; the stock copy is inert. It has to
  be a whole file at the tail of the chain because includes form a tree —
  a sibling include cannot see `render.wfl`'s definitions at all. It is
  consulted **first** in `dispatch_public`, so a site can own `/` and still
  inherit `/post/:slug`, `/page/:slug` and the 404. See the header comment in
  the file, and `website/` in LogbieLLC/logbie for a real one.
- **Body template names are a contract.** `home.html`, `post.html`, `page.html`,
  and `notfound.html` are named as string literals inside the handlers in
  `main.wfl`. Adding a new body template requires a new handler.

## Deployed instances

Live Scriptorium sites (news.starnet and others) are Starnet infrastructure.
Follow the workspace instructions in the `starnet` folder for those: load the
`starnet-devops` and `knowledge-mcp-dev` skills, check the knowledge base before
acting, and record what changed afterward. Use `git-safe-commit` for any git
write operation.
