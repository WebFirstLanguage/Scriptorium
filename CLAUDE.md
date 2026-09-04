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
