# Themes

A Scriptorium site is built from **sections** and **assembled** into pages. A
theme is that section library + a page assembler + a `theme.css` layer over the
shared **WFL Design System**. `base/` is the default (and reference) theme.

**Every page is assembled from three sections, in this order:**

1. **header** — `sections/header.html` (site identity + navbar) → `<header class="site-header">`
2. **body** — this page's content, in `<main class="site-body">`
3. **footer** — `sections/footer.html` (colophon + links) → `<footer class="site-footer">`

Header, body, and footer are non‑negotiable; a theme may add more sections,
never fewer. The full contract — the assembler, the `site.*` context, the
styling rules, and a new‑theme checklist — is in
[`../docs/THEMING.md`](../docs/THEMING.md).

Themes in a **new** project use literal `header/`, `body/`, and `footer/`
directories instead of `sections/` + `templates/` — see
[`../docs/PROJECT-LAYOUT.md`](../docs/PROJECT-LAYOUT.md) §2. Themes here keep
the shape below.

```
base/
  sections/               ← reusable section library
    header.html   site identity + navbar
    footer.html   colophon + links
  templates/
    skeleton.html   <html> shell — links ds/styles.css then theme.css
    layout.html     THE ASSEMBLER — header → body → footer
    home.html       body: post feed     }
    post.html       body: single post   }  extend layout.html,
    page.html       body: single page   }  fill {% block content %} only
    notfound.html   body: 404           }
```
