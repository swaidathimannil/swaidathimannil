# Swaid Athimannil

My personal corner of the internet. A lightweight, responsive website built with HTML, CSS, and vanilla JavaScript. No framework, build step, analytics, or third-party font requests.

## Local preview

```sh
python3 -m http.server 3000 --bind 0.0.0.0
```

Open `http://localhost:3000` locally. All asset paths are relative, so the site also works under a GitHub Pages repository subpath.

## Features

- Responsive personal homepage with about, project, and GitHub sections
- Light and dark themes that follow the system preference until manually selected
- Persistent theme selection, with graceful fallback if storage is blocked
- Keyboard focus indicators, a skip link, reduced-motion support, and a copy-link status announcement
- Core content and navigation work without JavaScript
- Original S monogram favicon set: SVG, multi-resolution ICO, 16/32/48px PNGs, 180px Apple touch icon, 192/512px Android icons, and a full-bleed 512px maskable icon
- Web app manifest (no offline support is claimed)

## Customize

Edit the content and profile links in `index.html`, the colors and layout in `styles.css`, and the copy-profile URL in `script.js`. Keep the name and colors in `site.webmanifest` in sync.

To regenerate the icons after editing `scripts/generate_icons.py`:

```sh
python3 -m venv .venv
.venv/bin/pip install Pillow
.venv/bin/python scripts/generate_icons.py
```

## Checks

```sh
python3 -m unittest discover -s tests -v
node --check script.js
node --test tests/site.test.cjs
```

## Publish on GitHub Pages

1. Merge the website pull request into `main`.
2. In repository **Settings → Pages → Build and deployment**, set **Source** to **GitHub Actions**.
3. The `Deploy website to GitHub Pages` workflow runs on pushes to `main`. If Pages was enabled after the merge, run the workflow manually from the Actions tab on `main`.

Expected project URL after successful deployment: `https://swaidathimannil.github.io/swaidathimannil/`.

The workflow publishes only the site files and assets, not the development scripts or tests. Pushing a feature branch alone does not deploy the site.
