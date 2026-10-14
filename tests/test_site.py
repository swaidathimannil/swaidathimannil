"""Dependency-free checks for the static site and generated favicon files."""
import json
import struct
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.tags = [], [], []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])

class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = Document()
        cls.doc.feed((ROOT / 'index.html').read_text())
        cls.manifest = json.loads((ROOT / 'site.webmanifest').read_text())

    def test_unique_ids(self):
        self.assertEqual(len(self.doc.ids), len(set(self.doc.ids)))

    def test_local_links_and_fragments(self):
        for link in self.doc.links:
            with self.subTest(link=link):
                url = urlsplit(link)
                if url.scheme or url.netloc:
                    continue
                if url.path:
                    self.assertFalse(url.path.startswith('/'), 'Asset paths must support repository subpaths')
                    self.assertTrue((ROOT / url.path).is_file())
                if url.fragment:
                    self.assertIn(url.fragment, self.doc.ids)

    def test_semantics(self):
        for tag in ('h1', 'main', 'nav', 'footer'):
            self.assertEqual(sum(t == tag for t, _ in self.doc.tags), 1)
        self.assertTrue(any(t == 'html' and a.get('lang') == 'en' for t, a in self.doc.tags))
        for t, attrs in self.doc.tags:
            if t == 'img':
                self.assertIn('alt', attrs)

    def test_manifest(self):
        self.assertEqual(self.manifest['start_url'], './')
        self.assertEqual(self.manifest['scope'], './')
        self.assertTrue(any(i.get('purpose') == 'maskable' for i in self.manifest['icons']))
        for icon in self.manifest['icons']:
            with self.subTest(icon=icon['src']):
                width, height = map(int, icon['sizes'].split('x'))
                self.assert_png(ROOT / icon['src'], width, height)

    def assert_png(self, path, width, height):
        data = path.read_bytes()
        self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
        self.assertEqual(struct.unpack('>II', data[16:24]), (width, height))

    def test_png_sizes(self):
        for size in (16, 32, 48):
            self.assert_png(ROOT / f'assets/icons/favicon-{size}x{size}.png', size, size)
        self.assert_png(ROOT / 'assets/icons/apple-touch-icon.png', 180, 180)

    def test_ico_contains_three_sizes(self):
        data = (ROOT / 'assets/icons/favicon.ico').read_bytes()
        self.assertEqual(struct.unpack('<HHH', data[:6]), (0, 1, 3))
        self.assertEqual({(data[6 + i * 16], data[7 + i * 16]) for i in range(3)}, {(16,16), (32,32), (48,48)})

if __name__ == '__main__':
    unittest.main()
