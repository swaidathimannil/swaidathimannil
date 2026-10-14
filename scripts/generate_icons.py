"""Regenerate the original S monogram icon set. Requires Pillow (pip install Pillow)."""
from pathlib import Path
from PIL import Image, ImageDraw

DEST = Path(__file__).resolve().parents[1] / 'assets' / 'icons'
DEST.mkdir(parents=True, exist_ok=True)
BG, FG = '#151714', '#d5f58a'
SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#151714"/>
  <path d="M43 19H23V32H41V45H21" fill="none" stroke="#d5f58a" stroke-width="7" stroke-linejoin="round"/>
</svg>
'''
(DEST / 'favicon.svg').write_text(SVG)

def icon(size, maskable=False):
    scale = 16
    image = Image.new('RGBA', (64 * scale, 64 * scale), BG if maskable else (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    if not maskable:
        draw.rounded_rectangle((0, 0, 64 * scale - 1, 64 * scale - 1), radius=14 * scale, fill=BG)
    points = [(x * scale, y * scale) for x, y in [(43, 19), (23, 19), (23, 32), (41, 32), (41, 45), (21, 45)]]
    draw.line(points, fill=FG, width=7 * scale, joint='curve')
    return image.resize((size, size), Image.Resampling.LANCZOS)

for size in (16, 32, 48):
    icon(size).save(DEST / f'favicon-{size}x{size}.png')
# Apple supplies its own corner mask, so use an opaque, full-bleed background.
icon(180, maskable=True).save(DEST / 'apple-touch-icon.png')
for size in (192, 512):
    icon(size).save(DEST / f'android-chrome-{size}x{size}.png')
icon(512, maskable=True).save(DEST / 'maskable-512x512.png')
icon(256).save(DEST / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
print(f'Generated 9 icons in {DEST}')
