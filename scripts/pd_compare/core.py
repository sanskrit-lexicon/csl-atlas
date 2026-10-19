"""Constants, text normalisation, date instruments and the citation resolver.

Shared by the PD-vs-control sense-order measurement (H7116).  The date joins and
the abbreviation resolution are the only place a threshold lives, so they are
kept together and imported, never re-spelled in a caller.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CSL_ORIG = ROOT.parent / "csl-orig" / "v02"
GUIDES_ABBR = ROOT.parent / "csl-guides" / "src" / "data" / "abbreviations.json"
MW_ABBR = ROOT / "data" / "citations" / "mw-source-abbreviations.tsv"
DCS_JSON = ROOT / "test" / "_h6943_dcs_texts_clean.json"
DM_JSON = ROOT / "src" / "data" / "external" / "dharmamitra-chronology.json"
PD_TSV = ROOT / "data" / "pd" / "pd_citation_order_full.tsv"
PD_JSON = ROOT / "data" / "pd" / "pd_sense_order_summary.json"
OUT_JSON = ROOT / "data" / "pd" / "pd_sense_order_compare_summary.json"
REPORT = ROOT / "reports" / "PD_SENSE_ORDER_COMPARE_2026.md"

DICTS = ("pwg", "pw", "mw", "ap")
DICT_NAMES = {"pwg": "PWG (Böhtlingk, 1855–1875)", "pw": "PW (Böhtlingk, 1879–1889)",
              "mw": "MW (Monier-Williams, 1899)", "ap": "AP (Apte, 1890)"}
CLOCKS = ("dcs", "dm")
PRIMARY_CLOCK = "dm"
DICE = {"dcs": 0.90, "dm": 0.82}
EFFECT_FLOOR = 0.10
ALPHA = 0.05
MIN_POWER = 30
BORROW = {"ap": "ap90"}          # documented in build_ls_citation_graph.py (H213)
# MW `<div>` marks a root's "to …" senses (n="to") and verbal-prefix notes
# (n="vp"/"P"); f10's validated convention splits on to|P|1 and leaves vp alone.
MW_DIV = re.compile(r'<div n="(?:to|P|1)"\s*/?>')
AP_BULLET = "∙"                  # the AP sense bullet (f10 convention)
# PWG/PW numbered Bedeutung marker: "— 12〉", "3〉", "4)".  Lettered markers
# ("a〉", "— β〉") are sub-senses and merge into their parent (see sense_chunks).
NUMBERED_SENSE = re.compile(r"^[—–-]?\s*\d+\s*[〉\)\.]")
LS = re.compile(r"<ls\b[^>]*>(.*?)</ls>", re.DOTALL)
REC_HEADER = re.compile(r"<(\w+)>([^<]*)")

REPORT_DATE = "2026-10-19"
HANDOFF = "H7116"


# ------------------------------------------------------------------ text helpers
def norm(text: str) -> str:
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "", t)


def _bigrams(t: str) -> set[str]:
    return {t[i:i + 2] for i in range(len(t) - 1)} or {t}


def dice(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    ba, bb = _bigrams(a), _bigrams(b)
    return 2.0 * len(ba & bb) / (len(ba) + len(bb))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------ date tables
def load_dcs() -> dict[str, int]:
    data = json.loads(DCS_JSON.read_text(encoding="utf-8"))
    out = {}
    for row in data:
        name = row.get("name") or row.get("title")
        date = row.get("date")
        if name and isinstance(date, (int, float)):
            out[norm(name)] = int(date)
    return out


def load_dm() -> dict[str, int]:
    data = json.loads(DM_JSON.read_text(encoding="utf-8"))
    groups: dict[str, list[int]] = {}
    for work in data.get("works", []):
        title = work.get("title") or work.get("work") or ""
        date = work.get("postMedian")
        if title and isinstance(date, (int, float)):
            base = re.split(r"[:—–]", title)[0]
            groups.setdefault(norm(base), []).append(int(date))
    return {k: min(v) for k, v in groups.items()}


def best_match(title: str, table: dict[str, int], threshold: float):
    """The H7093 join: exact normalised hit, else best Dice ≥ threshold."""
    key = norm(title)
    if not key:
        return None
    if key in table:
        return table[key], 1.0
    best = None
    for cand, year in table.items():
        if len(cand) < 4:
            continue
        score = dice(key, cand)
        if score >= threshold and (best is None or score > best[1]):
            best = (year, score)
    return best


# ------------------------------------------------------------------ citation resolver
def norm_abbr(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).rstrip(" .,;:")


def canonical_node(expansion: str) -> str:
    e = re.sub(r"[\[{]\s*Cologne [Aa]ddition\s*[\]}]", " ", expansion).replace("?", " ")
    e = re.sub(r"\s+", " ", e).strip()
    if not e:
        return ""
    e = re.split(r"[.,(]| ed\.| nach | in der | in the | im ", e)[0].strip()
    e = re.sub(r"^(the|die|der|das|den)\s+", "", e, flags=re.I)
    return re.sub(r"\s+", " ", e).strip(" .;:'")


def load_abbrev_tables() -> dict[str, dict[str, str]]:
    ab = json.loads(GUIDES_ABBR.read_text(encoding="utf-8"))
    guides: dict[str, dict[str, str]] = {}
    for x in ab["dicts"]:
        m: dict[str, str] = {}
        for src in (x.get("works") or []) + (x.get("mixed") or []):
            a = norm_abbr(src.get("abbr", ""))
            if a:
                m.setdefault(a, (src.get("expansion") or "").strip())
        if m:
            guides[x["code"].lower()] = m
    for borrower, lender in BORROW.items():
        if borrower not in guides and lender in guides:
            guides[borrower] = guides[lender]
    mw: dict[str, str] = {}
    if MW_ABBR.exists():
        import csv
        with MW_ABBR.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                a = norm_abbr(row.get("abbreviation") or "")
                if a:
                    mw.setdefault(a, (row.get("expansion_iast") or "").strip())
    if mw:
        base = mw
        for k, v in (guides.get("mw") or {}).items():
            base.setdefault(k, v)          # vendored MW table wins on conflict
        guides["mw"] = base
    return guides


def make_resolver(table: dict[str, str]):
    if not table:
        return lambda content: None
    ci = {a.casefold(): a for a in table}
    maxt = max(len(a.split(" ")) for a in table)

    def resolve(content: str):
        c = re.sub(r"<[^>]+>", "", content)
        c = re.sub(r"\s+", " ", c).strip()
        toks = c.split(" ")
        for n in range(min(maxt, len(toks)), 0, -1):
            cand = norm_abbr(" ".join(toks[:n]))
            if not cand:
                continue
            if cand in table:
                node = canonical_node(table[cand])
                if node:
                    return node
                continue
            cf = cand.casefold()
            if cf in ci:
                node = canonical_node(table[ci[cf]])
                if node:
                    return node
        return None

    return resolve

