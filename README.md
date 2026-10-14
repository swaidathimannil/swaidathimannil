# Swaid Athimannil

Personal website for Swaid Athimannil — Muslim entrepreneur and AI automation builder.

## Website

- `index.html`: the uploaded website, preserving its content, responsive layout, navigation, and embedded fonts.
- `photo.jpg`: the original uploaded logo, used in the navigation and retained as the source for icon generation.
- `favicon.svg`: a clean vector tracing of the logo, without the photograph’s shadows for readability at small sizes.
- `favicon.ico`: 16, 32, and 48 px browser icons in one file.
- `favicon-{16,32,48}x{16,32,48}.png`: PNG browser fallbacks (matching width and height).
- `apple-touch-icon.png`: 180 px Apple touch icon.
- `android-chrome-192x192.png` and `android-chrome-512x512.png`: Android icons.
- `android-chrome-maskable-512x512.png`: padded Android icon for adaptive masks.
- `site.webmanifest`: site metadata and Android icon references.

The old inline favicon and inline navigation image have been replaced with these local assets. Asset paths are relative, so the website also works under a GitHub Pages repository path. The manifest supplies icons and metadata; this is not an offline app.

## Preview

No website build step or runtime dependencies are required:

```sh
python3 -m http.server 8000 --bind 0.0.0.0
```

## Regenerate and check icons

The generator traces the pale-blue logo in `photo.jpg`; it is tailored to this image, not an arbitrary-photo converter. It preserves the original file and produces flat, crisp icons without adding rounded corners.

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements-icons.txt
.venv/bin/python scripts/generate_icons.py
.venv/bin/python scripts/check_site.py
```

The checks cover local asset paths, section anchors, embedded font encoding, icon dimensions, and the manifest. They do not check availability of external social links.

## GitHub status

Work is on `arena/86c2c365-swaidathimannil`, in [pull request #3](https://github.com/swaidathimannil/swaidathimannil/pull/3). Pushing this branch does not merge it into `main` or configure GitHub Pages. The previous upload placeholder has been replaced by the original website.
