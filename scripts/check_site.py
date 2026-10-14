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
assert 'href="favicon.svg?v=rounded-2"' in html
assert '<meta name="robots" content="noindex">' not in html
svg = ET.parse(ROOT / "favicon.svg").getroot()
ns = {"svg": "http://www.w3.org/2000/svg"}
assert svg.tag.endswith("svg")
rect = svg.find("svg:rect", ns)
assert rect is not None and rect.attrib["rx"] == "20"
# Every traced vertex must fit within the rounded background, not be clipped.
for path in svg.findall("svg:path", ns):
    for x, y in re.findall(r"([0-9.]+),([0-9.]+)", path.attrib["d"]):
        dx, dy = max(abs(float(x) - 50) - 30, 0), max(abs(float(y) - 50) - 30, 0)
        assert dx * dx + dy * dy <= 20 * 20, "Logo clips a rounded corner"


def check_rounded(im):
    assert im.mode == "RGBA", "Rounded icons need an alpha channel"
    alpha = im.getchannel("A")
    w, h = im.size
    assert all(alpha.getpixel(p) == 0 for p in [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)])
    assert alpha.getpixel((w // 2, h // 2)) == 255
    assert alpha.getpixel((w // 2, 0)) == 255
    assert any(0 < a < 255 for a in alpha.get_flattened_data()), "Edges should be antialiased"

for name, size in [(f"favicon-{n}x{n}.png", n) for n in (16, 32, 48)] + [
    ("apple-touch-icon.png", 180),
    ("android-chrome-192x192.png", 192),
    ("android-chrome-512x512.png", 512),
    ("android-chrome-maskable-512x512.png", 512),
]:
    with Image.open(ROOT / name) as im:
        assert im.size == (size, size), f"Wrong size: {name}"
        if name.startswith("favicon-"):
            check_rounded(im)
        else:
            assert im.mode == "RGB", f"Expected opaque platform icon: {name}"
        im.load()
with Image.open(ROOT / "favicon.ico") as im:
    assert im.ico.sizes() == {(16, 16), (32, 32), (48, 48)}
    for size in im.ico.sizes():
        check_rounded(im.ico.getimage(size))
manifest = json.loads((ROOT / "site.webmanifest").read_text())
assert manifest["start_url"] == manifest["scope"] == "./"
for icon in manifest["icons"]:
    with Image.open(ROOT / icon["src"]) as im:
        assert icon["sizes"] == f"{im.width}x{im.height}"
        assert im.format == "PNG"
print("PASS: local assets, section anchors, embedded fonts, SVG, ICO, PNG sizes, transparent rounded corners, unclipped logo, and manifest.")
