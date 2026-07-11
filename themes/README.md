# Themes

A Scriptorium theme is a swappable set of templates + a `theme.css` layer over
the shared **WFL Design System**. `base/` is the default (and reference) theme.

**Every theme must render three regions, in this order, on every page:**

1. **Header** — `partials/header.html` → `<header class="site-header">`
2. **Body** — `{% block content %}` inside `<main class="site-body">`
3. **Footer** — `partials/footer.html` → `<footer class="site-footer">`

These three are non‑negotiable; a theme may add more, never fewer. The full
contract — the composition templates, the `site.*` context, the styling rules,
and a new‑theme checklist — is in [`../docs/THEMING.md`](../docs/THEMING.md).

```
base/
  templates/
    skeleton.html   <html> shell — links ds/styles.css then theme.css
    layout.html     header → body → footer (the region shell)
    home.html       post feed        }
    post.html       single post      }  extend layout.html,
    page.html       single page      }  fill {% block content %} only
    notfound.html   404              }
  partials/
    header.html     the header region (site identity + nav)
    footer.html     the footer region (colophon + links)
```
