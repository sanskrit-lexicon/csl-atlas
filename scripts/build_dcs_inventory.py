#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H1336 Phase 4a — build the authoritative DCS target inventory.

Combines three VisualDCS artifacts into one table keyed by full IAST title,
which is the join axis to the PD siglum side (§4 of the handoff):

  * per_text_token_delta.csv  -> token mass in BOTH snapshots (tok_2021, tok_2026)
                                 and the 2026-renamed title. The master list.
  * Files.csv (DCS-data-2021) -> confirms 2021 membership (246 texts).
  * DCS-abbreviation-list.txt  -> full_title -> DCS compact siglum, for chapter
                                 grading via capters.csv later.

A `norm` key (lowercase, diacritics folded, non-alpha stripped) is emitted for
fuzzy matching against decoded PD titles. Output: data/pd/dcs_text_inventory.tsv.
"""
import sys, os, csv, unicodedata, re

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

GH = r"C:\Users\user\Documents\GitHub"
DELTA = os.path.join(GH, "VisualDCS", "derived-data", "Corpus-Delta-2021-2026", "per_text_token_delta.csv")
FILES = os.path.join(GH, "VisualDCS", "src", "DCS-data-2021", "Files.csv")
ABBR  = os.path.join(GH, "DCS", "DCS-abbreviation-list.txt")
OUT   = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "pd", "dcs_text_inventory.tsv")


def norm(s: str) -> str:
    """Fold to a diacritic-free lowercase alpha key for fuzzy title matching."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z]", "", s)
    return s


def main() -> int:
    # 1. token mass from the delta table (master list of titles)
    inv = {}  # canonical title (2026 name) -> row dict
    with open(DELTA, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            title = (r["text_2026"] or r["text_2021"]).strip()
            tok21 = int(r["tok_2021"] or 0)
            tok26 = int(r["tok_2026"] or 0)
            inv[title] = {
                "title": title,
                "title_2021": (r["text_2021"] or "").strip(),
                "tok_2021": tok21,
                "tok_2026": tok26,
                "in_2021": "1" if tok21 > 0 else "0",
                "in_2026": "1" if tok26 > 0 else "0",
                "dcs_siglum": "",
            }

    # 2. Files.csv 2021 membership — add any title not already present (tok unknown -> 0)
    files_titles = set()
    with open(FILES, encoding="utf-8") as f:
        for line in f:
            m = re.match(r'\s*\d+\s+"(.+)"\s*$', line.rstrip("\n"))
            if m:
                t = m.group(1).replace('\\"', '"').strip()
                files_titles.add(t)
                if t not in inv:
                    inv[t] = {"title": t, "title_2021": t, "tok_2021": 0, "tok_2026": 0,
                              "in_2021": "1", "in_2026": "0", "dcs_siglum": ""}
                else:
                    inv[t]["in_2021"] = "1"

    # 3. abbreviation list: full_title -> compact siglum, matched by norm key
    norm2title = {}
    for t in inv:
        norm2title.setdefault(norm(t), t)
    n_sig = 0
    with open(ABBR, encoding="utf-8") as f:
        for line in f:
            if "\t" not in line:
                continue
            full, sig = line.rstrip("\n").split("\t", 1)
            full, sig = full.strip(), sig.strip()
            if not sig:
                continue
            t = norm2title.get(norm(full))
            if t:
                inv[t]["dcs_siglum"] = sig
                n_sig += 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cols = ["title", "norm", "dcs_siglum", "tok_2021", "tok_2026", "in_2021", "in_2026", "title_2021"]
    with open(OUT, "w", encoding="utf-8", newline="") as out:
        w = csv.writer(out, delimiter="\t")
        w.writerow(cols)
        for t in sorted(inv, key=lambda x: -inv[x]["tok_2026"]):
            row = inv[t]
            w.writerow([row["title"], norm(t), row["dcs_siglum"], row["tok_2021"],
                        row["tok_2026"], row["in_2021"], row["in_2026"], row["title_2021"]])

    tok21 = sum(r["tok_2021"] for r in inv.values())
    tok26 = sum(r["tok_2026"] for r in inv.values())
    print(f"DCS texts (union 2021/2026): {len(inv)}", file=sys.stderr)
    print(f"  with compact siglum matched: {n_sig}", file=sys.stderr)
    print(f"  total tokens 2021: {tok21:,}   2026: {tok26:,}", file=sys.stderr)
    print(f"  in 2021: {sum(1 for r in inv.values() if r['in_2021']=='1')}   "
          f"in 2026: {sum(1 for r in inv.values() if r['in_2026']=='1')}", file=sys.stderr)
    print(f"wrote {OUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
