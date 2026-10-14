"""Trace the supplied pale-blue logo and export a consistent favicon family.

Run from any directory with the dependencies in requirements-icons.txt installed.
The original photo.jpg is never modified.
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
IMAGE = np.array(Image.open(ROOT / "photo.jpg").convert("RGB"))
# Separate the light logo face from the blue background and soft drop shadow.
MASK = ((IMAGE[:, :, 0] > 160) & (IMAGE[:, :, 1] > 215)
        & (IMAGE[:, :, 2] > 230)).astype(np.uint8) * 255
contours, _ = cv2.findContours(MASK, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted((c for c in contours if cv2.contourArea(c) > 1000),
                  key=cv2.contourArea, reverse=True)
if len(contours) != 3:
    raise ValueError("Expected the logo body, dot, and vertical bar; inspect photo.jpg.")
points = np.concatenate(contours).reshape(-1, 2)
minimum, maximum = points.min(axis=0), points.max(axis=0)
center = (minimum + maximum) / 2
extent = max(maximum - minimum)
background = "#48c3ef"
foreground = "#c5f0ff"


def svg(mark_size=80):
    """Keep the complete logo inside a rounded square with transparent corners."""
    paths = []
    for contour in contours:
        simplified = cv2.approxPolyDP(contour, 0.7, True).reshape(-1, 2)
        coords = (simplified - center) * mark_size / extent + 50
        paths.append("M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in coords) + " Z")
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">\n'
            '  <title>Swaid Athimannil logo</title>\n'
            f'  <rect width="100" height="100" rx="20" fill="{background}"/>\n'
            f'  <path fill="{foreground}" d="{" ".join(paths)}"/>\n'
            '</svg>\n')


def raster(mark_size, size, rounded=False):
    # Supersample the same vector contours for antialiased small icons.
    im = Image.new("RGB", (size * 4, size * 4), background)
    draw = ImageDraw.Draw(im)
    for contour in contours:
        simplified = cv2.approxPolyDP(contour, 0.7, True).reshape(-1, 2)
        coords = ((simplified - center) * mark_size / extent + 50) * size * 4 / 100
        draw.polygon([tuple(point) for point in coords], fill=foreground)
    if rounded:
        # Apply the mask at 4x resolution for smooth transparent edges.
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, im.width - 1, im.height - 1), radius=size * 4 * 0.20, fill=255)
        im.putalpha(mask)
    im = im.resize((size, size), Image.Resampling.LANCZOS)
    if rounded:
        # Remove tiny Lanczos halos at the transparent extremes.
        im.putalpha(im.getchannel("A").point(lambda a: 0 if a < 4 else (255 if a > 251 else a)))
    return im


source = svg()
(ROOT / "favicon.svg").write_text(source)
for size in (16, 32, 48):
    raster(80, size, rounded=True).save(ROOT / f"favicon-{size}x{size}.png", optimize=True)
raster(80, 48, rounded=True).save(
    ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)],
    append_images=[raster(80, n, rounded=True) for n in (16, 32)])
# Touch icons have a little more breathing room; no pre-rounded corners.
for name, size in (("apple-touch-icon.png", 180),
                   ("android-chrome-192x192.png", 192),
                   ("android-chrome-512x512.png", 512)):
    raster(76, size).save(ROOT / name, optimize=True)
# A 54% square lies entirely inside the central 80%-diameter safe circle.
raster(54, 512).save(ROOT / "android-chrome-maskable-512x512.png", optimize=True)
print("Generated SVG, multi-resolution ICO, and seven PNG icons from photo.jpg.")
