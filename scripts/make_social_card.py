#!/usr/bin/env python3
"""Generate the 1200x630 Open Graph / Twitter social card for the CSL Atlas.

Output: src/atlas-card.png (committed; referenced as og:image/twitter:image in
observablehq.config.js). Re-run if the tagline or branding changes.

    python scripts/make_social_card.py
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

W, H = 1200, 630
BG_TOP = (18, 46, 74)        # deep blue
BG_BOTTOM = (31, 120, 180)   # #1f78b4 theme-color
INK = (245, 249, 252)
MUTED = (188, 210, 228)
ACCENT = (126, 190, 232)

FONTS = Path("C:/Windows/Fonts")
title_font = ImageFont.truetype(str(FONTS / "georgiab.ttf"), 76)
tag_font = ImageFont.truetype(str(FONTS / "georgia.ttf"), 38)
foot_font = ImageFont.truetype(str(FONTS / "arial.ttf"), 27)
url_font = ImageFont.truetype(str(FONTS / "arial.ttf"), 26)

img = Image.new("RGB", (W, H), BG_TOP)
draw = ImageDraw.Draw(img)

for y in range(H):
    t = y / (H - 1)
    r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
    g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
    b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

draw.rectangle([80, 150, 84, 470], fill=ACCENT)

x = 130
draw.text((x, 150), "Atlas of the Cologne", font=title_font, fill=INK)
draw.text((x, 236), "Digital Sanskrit Lexicons", font=title_font, fill=INK)
draw.text((x, 350), "Compare, trace, and explore historical", font=tag_font, fill=MUTED)
draw.text((x, 398), "Sanskrit dictionaries — MW, PWG, the koshas", font=tag_font, fill=MUTED)

draw.text((x, 480),
          "coverage  ·  overlap  ·  genealogy  ·  sense structure  ·  citation apparatus",
          font=foot_font, fill=ACCENT)

url = "sanskrit-lexicon.github.io/csl-atlas"
draw.text((x, H - 70), url, font=url_font, fill=MUTED)

out = Path(__file__).resolve().parent.parent / "src" / "atlas-card.png"
img.save(out, "PNG", optimize=True)
print(f"wrote {out} ({out.stat().st_size} bytes, {W}x{H})")
