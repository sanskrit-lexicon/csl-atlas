#!/usr/bin/env python3
"""Generate src/sitemap.xml from the page list in observablehq.config.js.

Parses every `path: "/..."` route out of the (nested) pages array, prepends the
root page, de-duplicates, and writes a sitemap for the GitHub Pages origin.
Re-run whenever pages are added or removed.

    python scripts/make_sitemap.py
"""
import re
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ORIGIN = "https://sanskrit-lexicon.github.io/csl-atlas"
SITE = Path(__file__).resolve().parent.parent
config = (SITE / "observablehq.config.js").read_text(encoding="utf-8")

paths = re.findall(r'path:\s*"(/[^"]*)"', config)

routes = ["/"] + [p for p in paths if p not in ("/", "/index")]
seen, ordered = set(), []
for r in routes:
    if r not in seen:
        seen.add(r)
        ordered.append(r)

today = date.today().isoformat()
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for r in ordered:
    loc = ORIGIN + ("/" if r == "/" else r)
    priority = "1.0" if r == "/" else "0.7"
    lines.append("  <url>")
    lines.append(f"    <loc>{loc}</loc>")
    lines.append(f"    <lastmod>{today}</lastmod>")
    lines.append(f"    <priority>{priority}</priority>")
    lines.append("  </url>")
lines.append("</urlset>")

out = SITE / "src" / "sitemap.xml"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {out} ({len(ordered)} urls)")
