# Scriptorium — instructions for Claude

Scriptorium is a WordPress-style CMS written entirely in **WFL**, rendering
through the **Scribe** template engine (a git submodule at `lib/scribe`) and
persisting to SQLite. Start with [`README.md`](README.md), then
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

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
- **Scribe is a submodule.** Don't edit `lib/scribe/` in place; changes go
  upstream to WebFirstLanguage/Scribe, then bump via
  `scripts/update-scribe.sh`.
- **Tests:** `wfl --test TestPrograms/<name>.test.wfl`. There is no test workflow
  in CI today — the only workflow is `update-scribe.yml`.
- **`data_dir` is an application convention, not a WFL runtime feature.**
  `main.wfl` reads `.wflcfg` itself at boot and parses the key via
  `config_value_from` in `app/util.wfl`. The runtime ignores it.

## Known gaps worth knowing before you touch rendering

- **`render_public` hardcodes `themes/base/templates/`** (`app/render.wfl:36`).
  Every deployed site with a custom theme therefore runs a *patched clone* —
  `news.starnet` among them — and the patch is erased by the next `git pull`.
  Making that prefix configurable is the single change that fixes theme
  selection, region-aware template paths, and out-of-tree themes at once. See
  `docs/PROJECT-LAYOUT.md` §6.1.
- **Body template names are a contract.** `home.html`, `post.html`, `page.html`,
  and `notfound.html` are named as string literals inside the handlers in
  `main.wfl`. Adding a new body template requires a new handler.

## Deployed instances

Live Scriptorium sites (news.starnet and others) are Starnet infrastructure.
Follow the workspace instructions in the `starnet` folder for those: load the
`starnet-devops` and `knowledge-mcp-dev` skills, check the knowledge base before
acting, and record what changed afterward. Use `git-safe-commit` for any git
write operation.
