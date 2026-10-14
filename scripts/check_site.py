"""Check local page links, embedded assets, and generated icon sizes."""
import base64
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate ID: {attrs['id']}"
            self.ids.add(attrs["id"])
        for key in ("src", "href"):
            if attrs.get(key):
                self.refs.append(attrs[key])


html = (ROOT / "index.html").read_text()
page = Page()
page.feed(html)
page.close()
page.refs.extend(re.findall(r'url\([\'\"]?([^\)\'\"]+)', html))
for ref in page.refs:
    if ref.startswith("data:"):
        if ";base64," in ref:
            base64.b64decode(ref.split(",", 1)[1], validate=True)
        continue
    url = urlsplit(ref)
    if url.scheme or url.netloc:
        continue  # External social links are not fetched by this offline check.
    if url.path:
        assert (ROOT / unquote(url.path)).is_file(), f"Missing asset: {ref}"
    elif url.fragment:
        assert unquote(url.fragment) in page.ids, f"Missing anchor: {ref}"

assert "data:image/" not in html, "Old embedded images remain"
assert 'href="site.webmanifest"' in html
assert 'href="favicon.svg"' in html
assert '<meta name="robots" content="noindex">' not in html
assert ET.parse(ROOT / "favicon.svg").getroot().tag.endswith("svg")
for name, size in [(f"favicon-{n}x{n}.png", n) for n in (16, 32, 48)] + [
    ("apple-touch-icon.png", 180),
    ("android-chrome-192x192.png", 192),
    ("android-chrome-512x512.png", 512),
    ("android-chrome-maskable-512x512.png", 512),
]:
    with Image.open(ROOT / name) as im:
        assert im.size == (size, size), f"Wrong size: {name}"
        assert im.mode == "RGB", f"Expected opaque icon: {name}"
        im.verify()
with Image.open(ROOT / "favicon.ico") as im:
    assert im.ico.sizes() == {(16, 16), (32, 32), (48, 48)}
manifest = json.loads((ROOT / "site.webmanifest").read_text())
assert manifest["start_url"] == manifest["scope"] == "./"
for icon in manifest["icons"]:
    with Image.open(ROOT / icon["src"]) as im:
        assert icon["sizes"] == f"{im.width}x{im.height}"
        assert im.format == "PNG"
print("PASS: local assets, section anchors, embedded fonts, SVG, ICO, PNG sizes, and manifest.")
