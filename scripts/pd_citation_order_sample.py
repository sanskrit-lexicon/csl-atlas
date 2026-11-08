#!/usr/bin/env python3
"""PD citation order within the smallest division (H6943).

Samples 100 letter-a PD entries that carry at least two datable citations
inside one sense division and judges the citation sequence against three
chronologies:

  PD/SWC  work dates extracted from PD/SWC.md (Subject-wise Classification)
  DCS     middle dates of the DCS texts (VisualDCS dcs_texts_clean.json)
  DM      Dharmamitra postMedian dates (src/data/external/dharmamitra-chronology.json)

The handoff named data/compound-depth/typography-probe-2026-10-17.json as the
"Dharmamitra-derived data".  That file is a ByT5 compound-segmentation probe: it
has surfaces, marker counts and API segment counts, but no work title and no
date.  It cannot date a citation.  The Dharmamitra chronology actually used here
is src/data/external/dharmamitra-chronology.json (1,618 works, postMedian).

Usage:
    python scripts/pd_citation_order_sample.py --pd-txt /path/to/pd.txt
    python scripts/pd_citation_order_sample.py --check

pd.txt is the Cologne PD digital edition (PDScan 2020, pdtxt.zip), read-only and
not committed.  The committed artefacts are the TSV and the report.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "pd"
OUT_TSV = DATA / "pd_citation_order_sample.tsv"
DCS_TEXTS = REPO / "test" / "_h6943_dcs_texts_clean.json"
SWC_MD = REPO / "test" / "_h6943_swc.md"
DM_JSON = REPO / "src" / "data" / "external" / "dharmamitra-chronology.json"

SEED = 20261018
SAMPLE_N = 100

# ------------------------------------------------------------------ helpers


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    return re.sub(r"[^a-z0-9]+", "", text)


def bigrams(text: str) -> set[str]:
    return {text[i:i + 2] for i in range(len(text) - 1)} or {text}


def dice(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    ba, bb = bigrams(a), bigrams(b)
    return 2.0 * len(ba & bb) / (len(ba) + len(bb))


def year_from_swc(text: str) -> int | None:
    """Turn an SWC date expression into a signed year (BC negative)."""
    text = text.replace("–", "-")
    m = re.search(r"(\d{1,4})(?:\s*-\s*(\d{1,4}))?", text)
    if not m:
        return None
    first = int(m.group(1))
    second = int(m.group(2)) if m.group(2) else None
    century = bool(re.search(r"(\d{1,2})\s*(?:st|nd|rd|th)\s*(?:c\.?|century)", text, re.I))
    if century:
        first = (first - 1) * 100 + 50
        if second:
            second = (second - 1) * 100 + 50
    bc = bool(re.search(r"B\.?\s*C\.?", text, re.I)) or "बी" in text
    ad = bool(re.search(r"A\.?\s*D\.?", text, re.I)) or bool(re.search(r"\bC\.", text))
    if bc:
        val = -first if second is None else -(first + second) // 2
    elif ad:
        val = first if second is None else (first + second) // 2
    else:
        return None
    # Saka dates are often followed by the AD equivalent in brackets; prefer AD.
    if not bc and not ad:
        return None
    return val


def parse_swc(path: Path) -> dict[str, int]:
    """Return normalized work-name -> approximate year from SWC.md.

    The OCR is a two-column table, so a candidate name is the text immediately
    before a date on the same line; the match is later confirmed by Dice
    similarity against the PD display title.  No candidate is trusted by itself.
    """
    out: dict[str, int] = {}
    if not path.exists():
        return out
    date_re = re.compile(
        r"(\d{1,4}(?:\s*[-–]\s*\d{1,4})?(?:\s*(?:st|nd|rd|th)\s*c\.?)?"
        r"\s*(?:B\.?\s*C\.?|A\.?\s*D\.?|c\.\s*A\.?\s*D\.?|C\.))",
        re.I,
    )
    for line in path.read_text(encoding="utf-8").splitlines():
        for m in date_re.finditer(line):
            year = year_from_swc(m.group(1))
            if year is None:
                continue
            before = line[:m.start()]
            # strip class numbers and OCR punctuation; keep the last phrase
            before = re.sub(r"^[\s\d.,;:'\"()\[\]_*—–-]+", "", before)
            before = before.strip(" .,;:'\"()[]_*—–-")
            if len(norm(before)) < 4:
                continue
            out[norm(before)] = year
    return out


def load_dcs(path: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    if not path.exists():
        return out
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else data.get("texts", [])
    for row in rows:
        name = row.get("name") or row.get("title")
        date = row.get("date")
        if name and isinstance(date, (int, float)):
            out[norm(name)] = int(date)
    return out


def load_dharmamitra(path: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    if not path.exists():
        return out
    data = json.loads(path.read_text(encoding="utf-8"))
    groups: dict[str, list[int]] = {}
    for work in data.get("works", []):
        title = work.get("title") or work.get("work") or ""
        date = work.get("postMedian")
        if not title or not isinstance(date, (int, float)):
            continue
        base = re.split(r"[:—–]", title)[0]
        groups.setdefault(norm(base), []).append(int(date))
    for key, dates in groups.items():
        out[key] = min(dates)
    return out


def best_match(title: str, table: dict[str, int], threshold: float) -> tuple[str, int, float] | None:
    key = norm(title)
    if not key:
        return None
    if key in table:
        return key, table[key], 1.0
    best = None
    for cand, year in table.items():
        if len(cand) < 4:
            continue
        score = dice(key, cand)
        if score >= threshold and (best is None or score > best[2]):
            best = (cand, year, score)
    return best


# ------------------------------------------------------------------ PD parsing

SIGLUM_TOKEN = re.compile(r"[A-ZĀĪŪṚṜṢṬḌṆṄÑŚ][\wĀ-ž'’.\-]{1,24}\.")
SENSE_MARK = re.compile(r"\{@([^{}]{1,8})@\}")
SENSE_LABEL = re.compile(r"^(?:\d{1,2}[A-Za-z]?|[ivxlcdm]{1,5}|[A-Z]{1,2}|[A-Za-z]{1,3}\d?)$")
ENTRY_RE = re.compile(
    r"<L>(\d+)<pc>([^<]*)<k1>([^<]*)<k2>([^<]*)(?:<h>(\d+))?\n(.*?)<LEND>",
    re.S,
)


def load_sigla(path: Path) -> dict[str, dict]:
    sig: dict[str, dict] = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row.get("class") != "primary":
                continue
            s = (row.get("siglum") or "").strip()
            if len(re.sub(r"[^\w]", "", s)) < 3:
                continue
            sig[s] = row
    return sig


def split_divisions(body: str) -> list[tuple[str, str]]:
    """Split an entry body into sense divisions.

    A {@n@} marker opens the division labelled n.  Text before the first marker
    is the headword/preamble chunk (label "0"); an entry without markers is one
    division (label "whole").
    """
    marks = [m for m in SENSE_MARK.finditer(body) if SENSE_LABEL.match(m.group(1))]
    if not marks:
        return [(body, "whole")]
    parts: list[tuple[str, str]] = [(body[:marks[0].start()], "0")]
    for i, m in enumerate(marks):
        stop = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        parts.append((body[m.end():stop], m.group(1)))
    return parts


def citations(text: str, sigla: dict[str, dict]) -> list[str]:
    return [m.group(0) for m in SIGLUM_TOKEN.finditer(text) if m.group(0) in sigla]


def dated_sequence(cites: list[str], date_by_siglum: dict[str, int]) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    for c in cites:
        if c in date_by_siglum:
            out.append((c, date_by_siglum[c]))
    # collapse consecutive repeats of the same source (same work, same date)
    dedup: list[tuple[str, int]] = []
    for item in out:
        if dedup and dedup[-1][0] == item[0]:
            continue
        dedup.append(item)
    return dedup


def verdict(seq: list[tuple[str, int]]) -> str:
    """Monotone = one chronological direction (ascending or descending).

    A mixed sequence is the only evidence of an order violation inside the
    division, so it is the "inverted" class.  Direction is reported separately.
    """
    if len(seq) < 2:
        return "undecidable"
    years = [y for _, y in seq]
    asc = all(years[i + 1] >= years[i] for i in range(len(years) - 1))
    desc = all(years[i + 1] <= years[i] for i in range(len(years) - 1))
    return "monotone" if (asc or desc) else "inverted"


def direction(seq: list[tuple[str, int]]) -> str:
    if len(seq) < 2:
        return ""
    years = [y for _, y in seq]
    if all(years[i + 1] >= years[i] for i in range(len(years) - 1)):
        return "ascending"
    if all(years[i + 1] <= years[i] for i in range(len(years) - 1)):
        return "descending"
    return "mixed"


# ------------------------------------------------------------------ exact CI


def _binom_cdf(k: int, n: int, p: float) -> float:
    if p <= 0:
        return 1.0
    if p >= 1:
        return 1.0 if k >= n else 0.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact (Clopper-Pearson) binomial CI, no scipy."""
    if n == 0:
        return 0.0, 1.0
    lo, hi = 0.0, 1.0
    if k > 0:
        a, b = 0.0, 1.0
        for _ in range(80):
            mid = (a + b) / 2
            if _binom_cdf(k - 1, n, mid) > 1 - alpha / 2:
                a = mid
            else:
                b = mid
        lo = (a + b) / 2
    if k < n:
        a, b = 0.0, 1.0
        for _ in range(80):
            mid = (a + b) / 2
            if _binom_cdf(k, n, mid) < alpha / 2:
                b = mid
            else:
                a = mid
        hi = (a + b) / 2
    return lo, hi


# ------------------------------------------------------------------ main


def build(pd_txt: Path) -> list[dict]:
    sigla = load_sigla(DATA / "pd_siglum_families.tsv")
    swc = parse_swc(SWC_MD)
    dcs = load_dcs(DCS_TEXTS)
    dm = load_dharmamitra(DM_JSON)

    def dated_by_siglum(table: dict[str, int], threshold: float) -> dict[str, int]:
        cache: dict[str, int | None] = {}
        out: dict[str, int] = {}
        for siglum, row in sigla.items():
            title = row.get("display_title") or ""
            if not title:
                continue
            if title not in cache:
                hit = best_match(title, table, threshold)
                cache[title] = hit[1] if hit else None
            year = cache[title]
            if year is not None:
                out[siglum] = year
        return out

    pd_dates = dated_by_siglum(swc, 0.80)
    dcs_dates = dated_by_siglum(dcs, 0.90)
    dm_dates = dated_by_siglum(dm, 0.82)

    text = pd_txt.read_text(encoding="utf-8")
    stats = {"entries": 0, "with_sense_markers": 0, "ge2_citations": 0, "ge2_datable": 0}
    records = []
    for L, pc, k1, k2, h, body in ENTRY_RE.findall(text):
        stats["entries"] += 1
        divisions = split_divisions(body)
        if len(divisions) > 1:
            stats["with_sense_markers"] += 1
        if any(len(citations(d, sigla)) >= 2 for d, lab in divisions if lab not in ("0", "whole")):
            stats["ge2_citations"] += 1
        best = None
        for div_text, label in divisions:
            if label in ("0", "whole"):
                continue
            cites = citations(div_text, sigla)
            if len(cites) < 2:
                continue
            pdseq = dated_sequence(cites, pd_dates)
            dcsseq = dated_sequence(cites, dcs_dates)
            dmseq = dated_sequence(cites, dm_dates)
            datable = max(len(pdseq), len(dcsseq), len(dmseq))
            if datable < 2:
                continue
            score = (datable, len(cites))
            if best is None or score > best[0]:
                best = (score, label, cites, pdseq, dcsseq, dmseq)
        if best is None:
            continue
        stats["ge2_datable"] += 1
        _, label, cites, pdseq, dcsseq, dmseq = best
        v_pd, v_dcs, v_dm = verdict(pdseq), verdict(dcsseq), verdict(dmseq)
        decidable = [v for v in (v_pd, v_dcs, v_dm) if v != "undecidable"]
        overall = "undecidable" if not decidable else ("inverted" if "inverted" in decidable else "monotone")
        records.append({
            "L": int(L),
            "headword": k1,
            "homonym": h or "",
            "sense": label,
            "n_citations": len(cites),
            "citation_sequence": " ".join(cites),
            "pd_seq": " ".join(f"{s}@{y}" for s, y in pdseq),
            "pd_n": len(pdseq),
            "pd_verdict": v_pd,
            "pd_direction": direction(pdseq),
            "dcs_seq": " ".join(f"{s}@{y}" for s, y in dcsseq),
            "dcs_n": len(dcsseq),
            "dcs_verdict": v_dcs,
            "dcs_direction": direction(dcsseq),
            "dm_seq": " ".join(f"{s}@{y}" for s, y in dmseq),
            "dm_n": len(dmseq),
            "dm_verdict": v_dm,
            "dm_direction": direction(dmseq),
            "overall_verdict": overall,
        })
    records.sort(key=lambda r: (r["headword"], r["L"], r["sense"]))
    rng = random.Random(SEED)
    picked = rng.sample(records, min(SAMPLE_N, len(records)))
    picked.sort(key=lambda r: (r["headword"], r["L"]))
    return picked, stats


def write_tsv(rows: list[dict], path: Path) -> None:
    cols = [
        "sample_no", "L", "homonym", "headword", "sense", "n_citations",
        "citation_sequence",
        "pd_n", "pd_seq", "pd_verdict", "pd_direction",
        "dcs_n", "dcs_seq", "dcs_verdict", "dcs_direction",
        "dm_n", "dm_seq", "dm_verdict", "dm_direction", "overall_verdict",
    ]
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for i, row in enumerate(rows, 1):
            out = dict(row)
            out["sample_no"] = i
            w.writerow(out)


def summarize(rows: list[dict]) -> dict:
    summary = {}
    for clock, col in (("pd_swc", "pd_verdict"), ("dcs", "dcs_verdict"), ("dharmamitra", "dm_verdict"), ("overall", "overall_verdict")):
        dec = [r for r in rows if r[col] != "undecidable"]
        inv = [r for r in dec if r[col] == "inverted"]
        k, n = len(inv), len(dec)
        lo, hi = clopper_pearson(k, n) if n else (0.0, 1.0)
        summary[clock] = {
            "n_sample": len(rows),
            "n_decidable": n,
            "n_inverted": k,
            "rate": (k / n) if n else None,
            "ci95": [lo, hi],
            "n_ascending": sum(1 for r in dec if r.get(col.replace("verdict", "direction")) == "ascending"),
            "n_descending": sum(1 for r in dec if r.get(col.replace("verdict", "direction")) == "descending"),
            "n_mixed": sum(1 for r in dec if r.get(col.replace("verdict", "direction")) == "mixed"),
            "n_not_ascending": sum(
                1 for r in dec
                if r.get(col.replace("verdict", "direction")) in ("descending", "mixed")
            ),
        }
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pd-txt", type=Path, required=False)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        if not OUT_TSV.exists():
            print("FAIL: missing", OUT_TSV, file=sys.stderr)
            return 1
        with OUT_TSV.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh, delimiter="\t"))
        need = {"sample_no", "headword", "sense", "pd_verdict", "dcs_verdict",
                "dm_verdict", "overall_verdict"}
        if not need.issubset(rows[0].keys() if rows else set()):
            print("FAIL: committed TSV lacks required columns", file=sys.stderr)
            return 1
        if len(rows) != SAMPLE_N:
            print(f"FAIL: committed TSV has {len(rows)} rows, expected {SAMPLE_N}", file=sys.stderr)
            return 1
        print(f"OK: committed sample present ({len(rows)} rows); run without --check to regenerate")
        return 0
    if not args.pd_txt or not args.pd_txt.exists():
        print("FAIL: --pd-txt is required (Cologne PDScan pdtxt.zip pd.txt)", file=sys.stderr)
        return 2
    rows, stats = build(args.pd_txt)
    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    write_tsv(rows, OUT_TSV)
    summary = summarize(rows)
    summary["population"] = stats
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
