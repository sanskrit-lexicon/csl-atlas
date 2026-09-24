#!/usr/bin/env python3
"""Etymology component census — where and how each dictionary states etymology.

H5334. Complements (does NOT duplicate) two pieces of prior art:

  * ``data/etymology-oracle.json`` (``scripts/build-etymology-oracle.mjs``)
    consumes csl-orig's pre-built *_etymology.tsv extraction layer: it answers
    "which ROOT did each dictionary attribute" for the entries an extractor
    could parse.  It says nothing about how many entries carry etymology at
    all, which surface marker announces it, or where in the entry it sits.
  * ``src/data/witness/etymology_marker_preliminary.csv`` (vendored from
    csl-observatory, frozen, n=5) is an exploratory marker spike — five
    dictionaries, one hand-read style label each, no position and no
    shared-lemma comparison.

This builder measures the *component* directly on the csl-orig display text:
per dictionary, the share of entries that state an etymology, the marker that
announces it, the TYPE of statement, and its POSITION inside the entry; then
compares the European and the indigenous treatment on the shared-lemma set.

Types (mutually non-exclusive — one entry may carry several):

  root-reference  an explicit verbal-root / base attribution
                  (MW ``√``/``fr.``, PWG-PWK ``von {#…#}``/``Wurzel``)
  cognate         a comparative reference to a non-Sanskrit etymon
                  (MW ``<lang>``/``<etym>``, Apte ``<lang>``, MW72 ``<nsi>``)
  vyutpatti       an indigenous derivation formula — kāraka + kṛt affix, a
                  dhātu citation closed by ``iti`` (SKD, VCP, Apte's bracket)
  affix           morphological decomposition without a root attribution
                  (WIL's ``aff.``/``neg.`` Nirukta-style notation, caus./desid.)
  nirukta-citation a European dictionary *citing* the indigenous tradition
                  (``<ls>Nir.``) rather than deriving itself

Read-only over csl-orig: writes ONLY ``{src/,}data/etymology-census.json``.
Run ``npm run build-etymology-census`` (needs a csl-orig checkout; override
its location with ``CSL_ORIG_ROOT``).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
DEFAULT_ORIG = REPO.parent / "csl-orig" / "v02"
OUTPUTS = [REPO / "src" / "data" / "etymology-census.json", REPO / "data" / "etymology-census.json"]

TYPES = ["root-reference", "cognate", "vyutpatti", "affix", "nirukta-citation"]

# (label, type, regex) — the surface marker as it appears in the csl-orig
# display text.  Probed against the live files on 24-09-2026; a marker that
# scores 0 is kept only when its absence is itself the finding (PWG cognates).
MARKERS = {
    "mw": [
        ("√", "root-reference", r"√"),
        ("fr.", "root-reference", r"<ab>fr\.</ab>"),
        ("rt.", "root-reference", r"<ab>rt\.</ab>"),
        ("<lang>", "cognate", r"<lang>"),
        ("<etym>", "cognate", r"<etym>"),
        ("Nir.", "nirukta-citation", r"<ls>Nir\."),
    ],
    "mw72": [
        ("rt.", "root-reference", r"\brt\."),
        ("fr.", "root-reference", r"\bfr\."),
        ("<nsi>", "cognate", r"<nsi>"),
        ("<lang>", "cognate", r"<lang"),
    ],
    "pwg": [
        ("von {#…#}", "root-reference", r"\bvon \{#"),
        ("Wurzel", "root-reference", r"\bWurzel\b"),
        ("vgl.", "cognate", r"<ab>vgl\.</ab>\s*(?:<lang>|lat\.|griech\.|goth\.)"),
        ("Nir.", "nirukta-citation", r"<ls>NIR\.|<ls>Nir\."),
    ],
    "pw": [
        ("von {#…#}", "root-reference", r"\bvon \{#"),
        ("Wurzel", "root-reference", r"\bWurzel\b"),
        ("vgl.", "cognate", r"<ab>vgl\.</ab>\s*(?:<lang>|lat\.|griech\.|goth\.)"),
    ],
    "ap": [
        ("[{#…#}] bracket", "vyutpatti", r"\[\{#"),
        ("<lang>", "cognate", r"<lang>"),
        ("caus./desid./pass.", "affix", r"<ab>(?:caus|desid|pass)\.</ab>"),
    ],
    "ap90": [
        ("[{#…#}] bracket", "vyutpatti", r"\[\{#"),
        ("<lang>", "cognate", r"<lang>"),
        ("caus./desid./pass.", "affix", r"<ab>(?:caus|desid|pass)\.</ab>"),
    ],
    "wil": [
        ("aff.", "affix", r"<ab>aff\.</ab>"),
        ("neg./priv.", "affix", r"<ab>(?:neg|priv)\.</ab>"),
        ("caus./desid.", "affix", r"<ab>(?:caus|desid)\.</ab>"),
    ],
    "skd": [
        ("kāraka + kṛt", "vyutpatti", r"\b(?:karmmaRi|karmaRi|BAve|karaRe|kartari|aDikaraRe|apAdAne|sampradAne)\b"),
        ("dhātu", "root-reference", r"\bDAtu"),
        ("vyutpatti citation", "vyutpatti", r"\b(?:vyutpatti|nirukte|nirukta|DAtupAWe|DAtoH)\b"),
    ],
    "vcp": [
        ("kāraka + kṛt", "vyutpatti", r"\b(?:karmaRi|karmmaRi|BAve|karaRe|kartari|aDikaraRe|apAdAne|sampradAne)\b"),
        ("dhātu", "root-reference", r"\bDAtu"),
        ("vyutpatti citation", "vyutpatti", r"\b(?:vyutpatti|nirukte|nirukta|DAtupAWe|DAtoH)\b"),
    ],
}

DICTS = [
    # code, csl-orig dir, year, tradition family, display name
    ("WIL", "wil", 1832, "european", "Wilson, A Dictionary Sanscrit and English (2nd ed.)"),
    ("PWG", "pwg", 1875, "european", "Böhtlingk–Roth, Sanskrit-Wörterbuch (Großes PW)"),
    ("MW72", "mw72", 1872, "european", "Monier-Williams, Sanskrit-English Dictionary (1872)"),
    ("MW", "mw", 1899, "european", "Monier-Williams, Sanskrit-English Dictionary (1899)"),
    ("PWK", "pw", 1889, "european", "Böhtlingk, Sanskrit-Wörterbuch in kürzerer Fassung"),
    ("AP90", "ap90", 1890, "european", "Apte, The Practical Sanskrit-English Dictionary (1890)"),
    ("AP", "ap", 1957, "european", "Apte, Practical Sanskrit-English Dictionary (revised)"),
    ("SKD", "skd", 1886, "indigenous", "Rādhākāntadeva, Śabdakalpadruma"),
    ("VCP", "vcp", 1873, "indigenous", "Tārānātha, Vācaspatyam"),
]

L_RE = re.compile(r"<k1>([^<\r\n]*)")
ENTRY_START = "<L>"
ENTRY_END = "<LEND>"


def position_bucket(offset: int, length: int) -> str:
    """Where the first marker sits inside the entry body.

    ``initial`` = the etymology is stated before the gloss (the Apte bracket,
    MW's parenthesis right after ``¦``, the SKD formula); ``final`` = it is
    appended after the senses (MW's comparative block); ``medial`` otherwise.
    """
    if length <= 0:
        return "initial"
    ratio = offset / length
    if ratio <= 0.15 or offset <= 120:
        return "initial"
    if ratio >= 0.85:
        return "final"
    return "medial"


def iter_entries(path: Path):
    """Yield (headword_slp1, body) per <L>…<LEND> entry of a csl-orig .txt."""
    head = None
    buf: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith(ENTRY_START):
                m = L_RE.search(line)
                head = m.group(1).strip() if m else ""
                buf = []
                continue
            if head is None:
                continue
            if line.startswith(ENTRY_END):
                body = "".join(buf)
                # the ¦ divider separates the repeated headword from the article
                cut = body.find("¦")
                if cut != -1:
                    body = body[cut + 1:]
                yield head, body
                head = None
                buf = []
                continue
            buf.append(line)


def census_dict(code: str, directory: str, year: int, family: str, title: str, orig_root: Path,
                shared_wanted: set[str] | None):
    path = orig_root / directory / f"{directory}.txt"
    if not path.exists():
        return None, {}
    specs = [(label, typ, re.compile(rx)) for label, typ, rx in MARKERS[directory]]

    entries = 0
    with_etym = 0
    marker_entries = Counter()
    type_entries = Counter()
    type_positions = {t: Counter() for t in TYPES}
    per_lemma: dict[str, set[str]] = {}

    for head, body in iter_entries(path):
        entries += 1
        hit_types: dict[str, int] = {}
        for label, typ, rx in specs:
            m = rx.search(body)
            if m is None:
                continue
            marker_entries[label] += 1
            prev = hit_types.get(typ)
            if prev is None or m.start() < prev:
                hit_types[typ] = m.start()
        if not hit_types:
            continue
        with_etym += 1
        length = len(body)
        for typ, offset in hit_types.items():
            type_entries[typ] += 1
            type_positions[typ][position_bucket(offset, length)] += 1
        if shared_wanted is not None and head in shared_wanted:
            per_lemma.setdefault(head, set()).update(hit_types)

    by_type = {}
    for typ in TYPES:
        n = type_entries[typ]
        if n == 0 and not any(t == typ for _, t, _ in MARKERS[directory]):
            continue
        pos = type_positions[typ]
        by_type[typ] = {
            "entries": n,
            "rate": round(n / entries, 5) if entries else 0,
            "positions": {b: pos[b] for b in ("initial", "medial", "final")},
        }

    record = {
        "code": code,
        "dir": directory,
        "year": year,
        "family": family,
        "title": title,
        "entries": entries,
        "entriesWithEtymology": with_etym,
        "etymologyRate": round(with_etym / entries, 5) if entries else 0,
        "byType": by_type,
        "markers": [
            {"label": label, "type": typ, "entries": marker_entries[label]}
            for label, typ, _ in MARKERS[directory]
        ],
    }
    return record, per_lemma


def headword_set(path: Path) -> set[str]:
    heads: set[str] = set()
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith(ENTRY_START):
                m = L_RE.search(line)
                if m:
                    h = m.group(1).strip()
                    if h:
                        heads.add(h)
    return heads


SHARED_DICTS = ["MW", "PWG", "SKD", "VCP"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--orig-root", default=os.environ.get("CSL_ORIG_ROOT", str(DEFAULT_ORIG)))
    ap.add_argument("--sample", type=int, default=60, help="shared lemmas listed verbatim in the JSON")
    args = ap.parse_args()

    orig_root = Path(args.orig_root).resolve()
    if not orig_root.exists():
        print(f"csl-orig root not found: {orig_root}", file=sys.stderr)
        return 2

    by_dir = {d[1]: d for d in DICTS}
    # Pass 1 — the shared-lemma spine (headword keys only, no article text).
    shared: set[str] | None = None
    for code in SHARED_DICTS:
        directory = next(d[1] for d in DICTS if d[0] == code)
        heads = headword_set(orig_root / directory / f"{directory}.txt")
        shared = heads if shared is None else (shared & heads)
        print(f"  headwords {code}: {len(heads)} (shared so far {len(shared)})", file=sys.stderr)
    assert shared is not None

    # Pass 2 — the census proper; shared-lemma profiles ride along.
    dicts = []
    lemma_profiles: dict[str, dict[str, list[str]]] = {}
    for code, directory, year, family, title in DICTS:
        want = shared if code in SHARED_DICTS else None
        record, per_lemma = census_dict(code, directory, year, family, title, orig_root, want)
        if record is None:
            print(f"  SKIP {code}: no source text", file=sys.stderr)
            continue
        print(f"  {code}: {record['entries']} entries, "
              f"{record['entriesWithEtymology']} with etymology "
              f"({record['etymologyRate']:.1%})", file=sys.stderr)
        dicts.append(record)
        for lemma, types in per_lemma.items():
            lemma_profiles.setdefault(lemma, {})[code] = sorted(types)

    # Shared-lemma comparison: European (MW, PWG) vs indigenous (SKD, VCP).
    european = [c for c in SHARED_DICTS if by_dir[next(d[1] for d in DICTS if d[0] == c)][3] == "european"]
    indigenous = [c for c in SHARED_DICTS if c not in european]
    coverage = {c: 0 for c in SHARED_DICTS}
    both_sides = 0
    only_european = 0
    only_indigenous = 0
    neither = 0
    type_pairs = Counter()
    for lemma in shared:
        prof = lemma_profiles.get(lemma, {})
        for c in SHARED_DICTS:
            if prof.get(c):
                coverage[c] += 1
        eu = any(prof.get(c) for c in european)
        ind = any(prof.get(c) for c in indigenous)
        if eu and ind:
            both_sides += 1
        elif eu:
            only_european += 1
        elif ind:
            only_indigenous += 1
        else:
            neither += 1
        eu_types = sorted({t for c in european for t in prof.get(c, [])})
        ind_types = sorted({t for c in indigenous for t in prof.get(c, [])})
        type_pairs[("+".join(eu_types) or "none", "+".join(ind_types) or "none")] += 1

    sample = []
    for lemma in sorted(l for l in shared if lemma_profiles.get(l) and
                        len(lemma_profiles[l]) == len(SHARED_DICTS))[: args.sample]:
        row = {"lemma": lemma}
        row.update({c: lemma_profiles[lemma].get(c, []) for c in SHARED_DICTS})
        sample.append(row)

    payload = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "license": "CC BY-SA 4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "sourceRoot": "csl-orig/v02",
        "derivedFrom": "csl-orig <dict>/<dict>.txt display text (entry-level marker scan)",
        "provenance": "csl-atlas scripts/build-etymology-census.py (H5334)",
        "note": ("Entry-level marker census. A type is credited once per entry, at the "
                 "position of its FIRST marker. Types are not mutually exclusive, so per-type "
                 "counts may sum above entriesWithEtymology. Complements data/etymology-oracle.json "
                 "(root attribution on the extracted subset) and the frozen n=5 witness CSV."),
        "types": TYPES,
        "positionBuckets": {
            "initial": "first marker in the first 15% of the article body (or first 120 chars)",
            "medial": "between",
            "final": "first marker in the last 15% of the article body",
        },
        "dictionaryCount": len(dicts),
        "dicts": dicts,
        "sharedLemmas": {
            "dicts": SHARED_DICTS,
            "european": european,
            "indigenous": indigenous,
            "lemmaCount": len(shared),
            "withEtymology": coverage,
            "sides": {
                "both": both_sides,
                "europeanOnly": only_european,
                "indigenousOnly": only_indigenous,
                "neither": neither,
            },
            "typePairs": [
                {"european": eu, "indigenous": ind, "lemmas": n}
                for (eu, ind), n in type_pairs.most_common(25)
            ],
            "sample": sample,
        },
    }

    for out in OUTPUTS:
        out.parent.mkdir(parents=True, exist_ok=True)
        # newline="" keeps LF on Windows — the committed artefact must not churn on CRLF
        with out.open("w", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        print(f"wrote {out.relative_to(REPO)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
