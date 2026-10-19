#!/usr/bin/env python3
"""PD citation order on the full letter-a population (H7093).

H6943 sampled 100 entries.  This script measures every real `{@n@}` sense
division of the Cologne PDScan 2020 text that carries at least two citations
datable by at least one clock, adds the AOB imprint clock, and compares the
observed mixed rate with a pooled within-division permutation null.

Clocks are never blended:

  pd_swc     PD/SWC work dates (Dice >= 0.80 to the PD display title)
  dcs        DCS middle dates (Dice >= 0.90 through the siglum's dcs_title)
  dm         Dharmamitra postMedian (base title, earliest stratum, Dice >= 0.82)
  imprint    AOB declared-entry imprint year for the citation siglum

The `any` composite is the H6943 rule: a division is mixed if any clock that
can decide it is mixed.  It is a decision rule, not a dating clock.

Usage:
    python scripts/pd_citation_order_full.py --pd-txt /path/to/pd.txt --build
    python scripts/pd_citation_order_full.py --check
    python scripts/pd_citation_order_full.py --refresh

pd.txt is the read-only PDScan 2020 text (pdtxt.zip) and is not committed.
Committed artefacts: the TSV, the adjudication sheet, the summary JSON and the
report.  `--check` recomputes every committed number from the TSV and the same
pooled-permutation seed.  `--refresh` re-derives the summary JSON and the
report from the committed TSV when only the derived blocks have to move.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "pd"
OUT_TSV = DATA / "pd_citation_order_full.tsv"
OUT_ADJ = DATA / "pd_citation_order_adjudication.tsv"
OUT_JSON = DATA / "pd_citation_order_full_summary.json"
REPORT = REPO / "reports" / "PD_CITATION_ORDER_FULL_2026.md"

DCS_TEXTS = REPO / "test" / "_h6943_dcs_texts_clean.json"
SWC_MD = REPO / "test" / "_h6943_swc.md"
DM_JSON = REPO / "src" / "data" / "external" / "dharmamitra-chronology.json"
SIGLA_TSV = DATA / "pd_siglum_families.tsv"
AOB_ENTRIES = DATA / "pd_aob_declared_entries.tsv"

SEED = 20261019
NULL_SEED = 20261019
NULL_REPS = 10000
H6943_ANCHOR = 2118
ADJ_PER_ARM = 100
CLOCKS = ("pd_swc", "dcs", "dm", "imprint")

# ------------------------------------------------------------------ text helpers


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
        return -first if second is None else -(first + second) // 2
    if ad:
        return first if second is None else (first + second) // 2
    return None


def parse_swc(path: Path) -> dict[str, int]:
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
            before = re.sub(r"^[\s\d.,;:'\"()\[\]_*—–-]+", "", before)
            before = before.strip(" .,;:'\"()[]_*—–-")
            if len(norm(before)) < 4:
                continue
            out[norm(before)] = year
    return out


def load_dcs(path: Path) -> tuple[dict[str, int], dict[str, str]]:
    out: dict[str, int] = {}
    genres: dict[str, str] = {}
    if not path.exists():
        return out, genres
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else data.get("texts", [])
    for row in rows:
        name = row.get("name") or row.get("title")
        date = row.get("date")
        if name and isinstance(date, (int, float)):
            key = norm(name)
            out[key] = int(date)
            if row.get("genre"):
                genres[key] = row["genre"]
    return out, genres


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


def load_imprint(path: Path) -> dict[str, int]:
    """Siglum -> earliest datable imprint year from the AOB declared entries.

    The handoff names `pd_aob_declared_works.tsv`, but that aggregate carries no
    year column; the per-entry file does (`year` + `harvested_sigla`).  Using the
    per-entry file is the only way to attach an imprint year to a citation.
    """
    out: dict[str, list[int]] = defaultdict(list)
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            year = (row.get("year") or "").strip()
            if not re.fullmatch(r"-?\d{1,4}", year):
                continue
            y = int(year)
            sigla = [s.strip() for s in (row.get("harvested_sigla") or "").split(";")]
            sigla.append((row.get("siglum") or "").strip().rstrip(","))
            for s in sigla:
                if s:
                    out[s].append(y)
    return {s: min(ys) for s, ys in out.items()}


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
    dedup: list[tuple[str, int]] = []
    for item in out:
        if dedup and dedup[-1][0] == item[0]:
            continue
        dedup.append(item)
    return dedup


def verdict(seq: list[tuple[str, int]]) -> str:
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


def kendall_tau(seq: list[tuple[str, int]]) -> float:
    """Kendall tau-a (ties count as neither concordant nor discordant)."""
    n = len(seq)
    if n < 2:
        return 0.0
    years = [y for _, y in seq]
    conc = disc = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            if years[j] > years[i]:
                conc += 1
            elif years[j] < years[i]:
                disc += 1
    denom = n * (n - 1) / 2
    return (conc - disc) / denom if denom else 0.0


def adjacent_rate(seq: list[tuple[str, int]]) -> float:
    """Fraction of adjacent pairs that move forward in time (later >= earlier)."""
    if len(seq) < 2:
        return 0.0
    years = [y for _, y in seq]
    return sum(1 for i in range(len(years) - 1) if years[i + 1] > years[i]) / (len(years) - 1)


# ------------------------------------------------------------------ exact CI


def _binom_cdf(k: int, n: int, p: float) -> float:
    """Binomial CDF via log-space terms; safe for the 9,689-division base."""
    if p <= 0:
        return 1.0
    if p >= 1:
        return 1.0 if k >= n else 0.0
    k = min(k, n)
    lgamma = math.lgamma
    log_p, log_q = math.log(p), math.log1p(-p)
    logs = [
        lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) + i * log_p + (n - i) * log_q
        for i in range(0, k + 1)
    ]
    top = max(logs)
    return math.exp(top) * sum(math.exp(x - top) for x in logs)


CI_DP = 10
"""Decimals the published Clopper-Pearson bounds are rounded to.

``_binom_cdf`` evaluates the binomial CDF in log space through ``math.lgamma``,
whose last bit depends on the platform's libm; the 80-step bisection then
amplifies that one-ULP difference into a ~1e-14 spread of the bound.  The
bound is reported at 0.1 % (1e-3 of a probability), so rounding to 1e-10 keeps
seven orders of magnitude of head-room and makes the committed summary JSON
byte-identical on every platform -- which is what the ``--check`` gate needs.
"""


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
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
    return round(lo, CI_DP), round(hi, CI_DP)


# ------------------------------------------------------------------ build


def build(pd_txt: Path) -> tuple[list[dict], dict]:
    sigla = load_sigla(SIGLA_TSV)
    swc = parse_swc(SWC_MD)
    dcs, dcs_genres = load_dcs(DCS_TEXTS)
    dm = load_dharmamitra(DM_JSON)
    imprint = load_imprint(AOB_ENTRIES)

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

    clock_dates = {
        "pd_swc": dated_by_siglum(swc, 0.80),
        "dcs": dated_by_siglum(dcs, 0.90),
        "dm": dated_by_siglum(dm, 0.82),
        "imprint": {s: y for s, y in imprint.items() if s in sigla},
    }

    dcs_genre_by_siglum: dict[str, str] = {}
    for siglum, row in sigla.items():
        title = norm(row.get("dcs_title") or "")
        for key, genre in dcs_genres.items():
            if title and dice(title, key) >= 0.90:
                dcs_genre_by_siglum[siglum] = genre
                break

    text = pd_txt.read_text(encoding="utf-8")
    stats = {
        "entries": 0,
        "entries_with_sense_markers": 0,
        "divisions_total": 0,
        "divisions_ge2_citations": 0,
        "h6943_eligible_entries": 0,
        "eligible_divisions_3clock": 0,
        "eligible_divisions_4clock": 0,
    }
    records: list[dict] = []
    for L, pc, k1, k2, h, body in ENTRY_RE.findall(text):
        stats["entries"] += 1
        divisions = split_divisions(body)
        if len(divisions) > 1:
            stats["entries_with_sense_markers"] += 1
        best_entry = None
        for div_text, label in divisions:
            if label in ("0", "whole"):
                continue
            stats["divisions_total"] += 1
            cites_list = citations(div_text, sigla)
            if len(cites_list) < 2:
                continue
            stats["divisions_ge2_citations"] += 1
            seqs = {clock: dated_sequence(cites_list, dates) for clock, dates in clock_dates.items()}
            n3 = max(len(seqs["pd_swc"]), len(seqs["dcs"]), len(seqs["dm"]))
            n4 = max(len(seqs[c]) for c in CLOCKS)
            if n3 >= 2:
                stats["eligible_divisions_3clock"] += 1
            if n4 < 2:
                continue
            stats["eligible_divisions_4clock"] += 1
            if n3 >= 2 and (best_entry is None or (n3, len(cites_list)) > best_entry[0]):
                best_entry = ((n3, len(cites_list)), label)
            verdicts = {clock: verdict(seq) for clock, seq in seqs.items()}
            directions = {clock: direction(seq) for clock, seq in seqs.items()}
            taus = {clock: kendall_tau(seq) for clock, seq in seqs.items()}
            rates = {clock: adjacent_rate(seq) for clock, seq in seqs.items()}
            decidable = [v for v in verdicts.values() if v != "undecidable"]
            if not decidable:
                continue
            composite = "inverted" if "inverted" in decidable else "monotone"
            composite_dirs = [directions[c] for c in CLOCKS if verdicts[c] != "undecidable"]
            composite_dir = (
                "mixed" if composite == "inverted"
                else ("ascending" if composite_dirs and all(d == "ascending" for d in composite_dirs) else "descending")
            )
            used = [c for c in CLOCKS if verdicts[c] != "undecidable"]
            n_max = max(len(seqs[c]) for c in used)
            tau_src = max(used, key=lambda c: len(seqs[c]))
            genre_counts = Counter(
                dcs_genre_by_siglum[s] for s, _ in seqs["dcs"] if s in dcs_genre_by_siglum
            )
            genre = genre_counts.most_common(1)[0][0] if genre_counts else "undetermined"
            row = {
                "L": int(L),
                "headword": k1,
                "homonym": h or "",
                "division": label,
                "n_citations": len(cites_list),
                "citation_sequence": " ".join(cites_list),
                "n_datable": n4,
                "genre": genre,
                "decidable_clocks": "+".join(used),
                "monotone": composite == "monotone",
                "verdict": composite,
                "direction": composite_dir,
                "tau": f"{kendall_tau(seqs[tau_src]):.4f}",
                "adjacent_rate": f"{adjacent_rate(seqs[tau_src]):.4f}",
                "n_for_tau": len(seqs[tau_src]),
            }
            for clock in CLOCKS:
                row[f"{clock}_n"] = len(seqs[clock])
                row[f"{clock}_seq"] = " ".join(f"{s}@{y}" for s, y in seqs[clock])
                row[f"{clock}_verdict"] = verdicts[clock]
                row[f"{clock}_direction"] = directions[clock]
                row[f"{clock}_tau"] = f"{taus[clock]:.4f}"
                row[f"{clock}_adjacent_rate"] = f"{rates[clock]:.4f}"
            records.append(row)
        if best_entry is not None:
            stats["h6943_eligible_entries"] += 1

    records.sort(key=lambda r: (r["L"], r["division"]))
    return records, stats


# ------------------------------------------------------------------ summaries


def summarize(rows: list[dict]) -> dict:
    summary: dict[str, dict] = {}
    for clock in CLOCKS + ("any",):
        vcol = "verdict" if clock == "any" else f"{clock}_verdict"
        dcol = "direction" if clock == "any" else f"{clock}_direction"
        tcol = "tau" if clock == "any" else f"{clock}_tau"
        acol = "adjacent_rate" if clock == "any" else f"{clock}_adjacent_rate"
        dec = [r for r in rows if r[vcol] != "undecidable"]
        inv = [r for r in dec if r[vcol] == "inverted"]
        k, n = len(inv), len(dec)
        lo, hi = clopper_pearson(k, n) if n else (0.0, 1.0)
        summary[clock] = {
            "n_decidable": n,
            "n_inverted": k,
            "mixed_rate": (k / n) if n else None,
            "ci95_mixed": [lo, hi],
            "n_ascending": sum(1 for r in dec if r[dcol] == "ascending"),
            "n_descending": sum(1 for r in dec if r[dcol] == "descending"),
            "n_mixed": sum(1 for r in dec if r[dcol] == "mixed"),
            "mean_tau": round(sum(float(r[tcol]) for r in dec) / n, CI_DP) if n else None,
            "mean_adjacent_rate": round(sum(float(r[acol]) for r in dec) / n, CI_DP) if n else None,
            "n_not_ascending": sum(1 for r in dec if r[dcol] in ("descending", "mixed")),
        }
    return summary


def null_model(rows: list[dict], reps: int = NULL_REPS, seed: int = NULL_SEED) -> dict:
    """Pooled within-division permutation null.

    One replicate shuffles every datable citation sequence of every division and
    records, per clock and for the `any` rule, whether the division is mixed.
    The 10,000 replicate mixed rates form the null distribution.
    """
    packed = []
    for r in rows:
        clocks = []
        for clock in CLOCKS:
            seq = [int(x.split("@")[1]) for x in r[f"{clock}_seq"].split()] if r[f"{clock}_seq"] else []
            clocks.append(seq)
        packed.append(clocks)
    rng = random.Random(seed)
    null_counts = {c: [] for c in CLOCKS + ("any",)}
    for _ in range(reps):
        counts = {c: 0 for c in CLOCKS + ("any",)}
        for clocks in packed:
            any_mixed = False
            for ci, years in enumerate(clocks):
                if len(years) < 2:
                    continue
                s = years[:]
                rng.shuffle(s)
                asc = all(s[i + 1] >= s[i] for i in range(len(s) - 1))
                desc = all(s[i + 1] <= s[i] for i in range(len(s) - 1))
                mixed = not (asc or desc)
                if mixed:
                    counts[CLOCKS[ci]] += 1
                    any_mixed = True
            if any_mixed:
                counts["any"] += 1
        for c in counts:
            null_counts[c].append(counts[c])
    obs = {}
    for clock in CLOCKS + ("any",):
        vcol = "verdict" if clock == "any" else f"{clock}_verdict"
        n = sum(1 for r in rows if r[vcol] != "undecidable")
        k = sum(1 for r in rows if r[vcol] == "inverted")
        obs_rate = k / n if n else 0.0
        dist = sorted(x / n for x in null_counts[clock]) if n else [0.0]
        mean = sum(dist) / len(dist)
        lo = dist[int(0.025 * (len(dist) - 1))]
        hi = dist[int(0.975 * (len(dist) - 1))]
        ge = sum(1 for x in dist if x >= obs_rate) / len(dist)
        le = sum(1 for x in dist if x <= obs_rate) / len(dist)
        null_mean_count = sum(null_counts[clock]) / len(null_counts[clock])
        p_lower = (sum(1 for x in null_counts[clock] if x <= k) + 1) / (len(null_counts[clock]) + 1)
        obs[clock] = {
            "n_decidable": n,
            "observed_mixed": k,
            "observed_rate": obs_rate,
            "null_mean_rate": mean,
            "null_mean_count": null_mean_count,
            "null_rate_p2_5": lo,
            "null_rate_p97_5": hi,
            "percentile_of_observed": ge,
            "p_null_ge_observed": ge,
            "p_null_le_observed": p_lower,
        }
    return {"reps": reps, "seed": seed, "clocks": obs}


# ------------------------------------------------------------------ adjudication sheet


def draw_adjudication(rows: list[dict]) -> list[dict]:
    """100 mixed + 100 monotone controls, stratified and seeded."""
    rng = random.Random(SEED + 1)
    flagged = [r for r in rows if r["verdict"] == "inverted"]
    controls = [r for r in rows if r["verdict"] == "monotone"]
    max_l = max((r["L"] for r in rows), default=1)

    def stratum(r: dict) -> tuple:
        size = r["n_citations"]
        size_bucket = "2-3" if size <= 3 else ("4-7" if size <= 7 else "8+")
        pos = r["L"] / max_l
        pos_bucket = "a1" if pos < 0.25 else ("a2" if pos < 0.5 else ("a3" if pos < 0.75 else "a4"))
        return (r["decidable_clocks"], r["genre"], size_bucket, pos_bucket)

    def pick(pool: list[dict], n: int) -> list[dict]:
        groups: dict[tuple, list[dict]] = defaultdict(list)
        for r in pool:
            groups[stratum(r)].append(r)
        keys = sorted(groups)
        for g in keys:
            groups[g].sort(key=lambda r: r["L"])
            rng.shuffle(groups[g])
        chosen: list[dict] = []
        i = 0
        while len(chosen) < n and keys:
            key = keys[i % len(keys)]
            if groups[key]:
                chosen.append(groups[key].pop())
            if not any(groups[k] for k in keys):
                break
            i += 1
        return chosen[:n]

    chosen = [("flagged", r) for r in pick(flagged, ADJ_PER_ARM)]
    chosen += [("control", r) for r in pick(controls, ADJ_PER_ARM)]
    out = []
    for i, (arm, r) in enumerate(chosen, 1):
        out.append({
            "adjudication_no": i,
            "arm": arm,
            "stratum_clock": r["decidable_clocks"],
            "stratum_genre": r["genre"],
            "stratum_size": "2-3" if r["n_citations"] <= 3 else ("4-7" if r["n_citations"] <= 7 else "8+"),
            "L": r["L"],
            "headword": r["headword"],
            "homonym": r["homonym"],
            "division": r["division"],
            "n_citations": r["n_citations"],
            "citation_sequence": r["citation_sequence"],
            "verdict": r["verdict"],
            "direction": r["direction"],
            "decidable_clocks": r["decidable_clocks"],
            "annotator_1": "",
            "annotator_1_note": "",
            "annotator_2": "",
            "annotator_2_note": "",
            "adjudicated_class": "",
            "page_image": "",
        })
    return out


# ------------------------------------------------------------------ writers


TSV_COLS = [
    "L", "headword", "homonym", "division", "n_citations", "citation_sequence",
    "n_datable", "genre", "decidable_clocks", "monotone", "verdict", "direction",
    "tau", "adjacent_rate", "n_for_tau",
] + [
    f"{clock}_{field}"
    for clock in CLOCKS
    for field in ("n", "seq", "verdict", "direction", "tau", "adjacent_rate")
]

ADJ_COLS = [
    "adjudication_no", "arm", "stratum_clock", "stratum_genre", "stratum_size",
    "L", "headword", "homonym", "division", "n_citations", "citation_sequence",
    "verdict", "direction", "decidable_clocks", "annotator_1", "annotator_1_note",
    "annotator_2", "annotator_2_note", "adjudicated_class", "page_image",
]


def write_tsv(rows: list[dict], path: Path, cols: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def input_pins(pd_txt: Path | None) -> dict:
    pins = {}
    for label, path in (
        ("pd_txt", pd_txt),
        ("swc", SWC_MD),
        ("dcs_texts_clean", DCS_TEXTS),
        ("dharmamitra", DM_JSON),
        ("aob_declared_entries", AOB_ENTRIES),
        ("pd_siglum_families", SIGLA_TSV),
    ):
        if path and path.exists():
            pins[label] = {"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size}
    return pins


def pct(x: float | None) -> str:
    return "—" if x is None else f"{100 * x:.1f} %"


def rate_ci(d: dict, key: str = "mixed_rate", ci_key: str = "ci95_mixed") -> str:
    if d.get(key) is None:
        return "—"
    lo, hi = d[ci_key]
    return f"{pct(d[key])} ({100 * lo:.1f}–{100 * hi:.1f})"


def write_report(summary: dict, null: dict, stats: dict, pins: dict, adj_note: str) -> None:
    lines: list[str] = []
    add = lines.append
    add("# PD citation order on the full letter-*a* population (H7093)")
    add("")
    add("_Created: 19-10-2026 · Executor: DeepSeek v4.1 Flash (`deepseek/deepseek-flash`)_")
    add("")
    add("## Question")
    add("")
    add("PD's Preface claims strict chronological order **within the smallest division**. "
        "H6943 sampled 100 entries and found 49 % mixed (exact 95 % CI 38.9–59.2). "
        "This report tests the claim on every real `{@n@}` division of the letter-*a* "
        "text, adds an imprint clock, and asks whether the observed order is better or "
        "worse than random.")
    add("")
    add("## Inputs (hash-pinned)")
    add("")
    add("| Input | SHA-256 | Bytes |")
    add("|---|---|--:|")
    for label, pin in pins.items():
        add(f"| `{label}` (`{pin['path']}`) | `{pin['sha256']}` | {pin['bytes']:,} |")
    add("")
    add("## Population funnel")
    add("")
    add(f"* `<L>` entries parsed: **{stats['entries']:,}**")
    add(f"* entries with at least one real `{{@n@}}` marker: **{stats['entries_with_sense_markers']:,}**")
    add(f"* real sense divisions (preamble and whole-entry chunks excluded): **{stats['divisions_total']:,}**")
    add(f"* divisions with at least two citation sigla: **{stats['divisions_ge2_citations']:,}**")
    add(f"* divisions with at least two citations datable by ≥1 of the three H6943 clocks: **{stats['eligible_divisions_3clock']:,}**")
    add(f"* divisions with at least two citations datable by ≥1 of the four clocks (imprint included): **{stats['eligible_divisions_4clock']:,}**")
    add(f"* **H6943 reconciliation anchor:** entries with at least two datable citations in their best real division = **{stats['h6943_eligible_entries']:,}** (target {H6943_ANCHOR:,}; {'MATCH' if stats['h6943_eligible_entries'] == H6943_ANCHOR else 'MISMATCH'}).")
    add("")
    add("H6943 picked one division per entry, so its 2,118 is an **entry** count. "
        "The full-population unit here is the division; the two counts differ by "
        "construction and the entry count is the reconciliation anchor.")
    add("")
    add("## Method")
    add("")
    add("* **Unit.** Smallest numbered sense division; `{@n@}`, `{@1B@}`, `{@ii@}` … are labels. "
        "The preamble (`0`) and marker-less whole entries are excluded.")
    add("* **Sequence.** Citation sigla in order of appearance; consecutive repeats of the same siglum collapsed.")
    add("* **Binary.** `monotone` = non-decreasing **or** non-increasing; `inverted` = at least one direction change. "
        "Ascending, descending and mixed are reported separately, because a wholly newest-first division is monotone.")
    add("* **Continuous.** Kendall τ-a and the adjacent-pair forward rate per division.")
    add("* **Clocks.** PD/SWC (Dice ≥ 0.80), DCS (Dice ≥ 0.90), Dharmamitra (Dice ≥ 0.82, earliest stratum per base title), "
        "AOB imprint (earliest declared imprint year per harvested siglum). Clocks are never blended; `any` is the H6943 decision rule, not a clock.")
    add("* **Null.** For each of 10,000 pooled permutations, every datable sequence of every division is shuffled "
        "uniformly and the mixed indicators are recomputed. The null distribution is the resulting mixed rate per clock and for `any`.")
    add("* **CI.** Clopper–Pearson exact intervals at 95 %.")
    add("")
    add("## Results")
    add("")
    add("| Clock / rule | Decidable divisions | Mixed (inverted) | Mixed rate, exact 95 % CI | Asc / desc / mixed | Mean τ | Mean adjacent-forward rate |")
    add("|---|--:|--:|---|---|--:|--:|")
    for clock in CLOCKS + ("any",):
        d = summary[clock]
        label = {"pd_swc": "PD/SWC", "dcs": "DCS", "dm": "Dharmamitra", "imprint": "AOB imprint", "any": "Any clock (H6943 rule)"}[clock]
        add(f"| {label} | {d['n_decidable']:,} | {d['n_inverted']:,} | {rate_ci(d)} | "
            f"{d['n_ascending']:,} / {d['n_descending']:,} / {d['n_mixed']:,} | "
            f"{d['mean_tau']:.3f} | {pct(d['mean_adjacent_rate'])} |")
    add("")
    add("The `any` row is the composite decision rule used by H6943 and is therefore "
        "the closest like-for-like continuation of the sample.")
    add("")
    add("## Null model")
    add("")
    add("Observed mixed rate versus 10,000 pooled within-division permutations. "
        "`P(null ≥ observed)` is the share of null replicates at or above the observed rate; "
        "a small value means the observed order is more chronological than random. "
        "`P(null ≤ observed)` is the one-sided test that the observed order is no worse than random.")
    add("")
    add("| Clock / rule | Observed | Null mean | Null 2.5–97.5 % | P(null ≥ observed) | P(null ≤ observed) |")
    add("|---|---|---|---|--:|--:|")
    for clock in CLOCKS + ("any",):
        o = null["clocks"][clock]
        label = {"pd_swc": "PD/SWC", "dcs": "DCS", "dm": "Dharmamitra", "imprint": "AOB imprint", "any": "Any clock"}[clock]
        add(f"| {label} | {pct(o['observed_rate'])} | {pct(o['null_mean_rate'])} | "
            f"{pct(o['null_rate_p2_5'])}–{pct(o['null_rate_p97_5'])} | "
            f"{pct(o['percentile_of_observed'])} | {o['p_null_le_observed']:.4g} |")
    add("")
    add("## Verdict")
    add("")
    any_obs = summary["any"]["mixed_rate"]
    any_null = null["clocks"]["any"]
    strong_ok = all(
        summary[c]["n_ascending"] == summary[c]["n_decidable"] for c in CLOCKS if summary[c]["n_decidable"]
    )
    add(f"* **Strong form (strict ascending in every division):** {'not refuted' if strong_ok else 'refuted'}. "
        f"Under the `any` rule, {summary['any']['n_decidable'] - summary['any']['n_ascending']:,} of "
        f"{summary['any']['n_decidable']:,} decidable divisions are not ascending "
        f"({pct(1 - summary['any']['n_ascending'] / summary['any']['n_decidable']) if summary['any']['n_decidable'] else '—'}).")
    add("")
    add("The weak form has to be read clock by clock, because the `any` rule is dominated by "
        "the imprint clock (9,501 of 9,689 decidable divisions) and the work-date clocks pull "
        "in different directions:")
    add("")
    add("| Work-date clock | Mixed vs null | Mean τ | Adjacent-forward rate | Weak chronological tendency? |")
    add("|---|---|--:|--:|---|")
    for clock in ("pd_swc", "dcs", "dm"):
        s, o = summary[clock], null["clocks"][clock]
        label = {"pd_swc": "PD/SWC", "dcs": "DCS", "dm": "Dharmamitra"}[clock]
        tendency = s["mean_tau"] > 0 and s["mean_adjacent_rate"] > 0.5 and s["mixed_rate"] < o["null_mean_rate"]
        add(f"| {label} | {pct(s['mixed_rate'])} vs {pct(o['null_mean_rate'])} | {s['mean_tau']:.3f} | "
            f"{pct(s['mean_adjacent_rate'])} | {'yes' if tendency else 'no'} |")
    add("")
    add(f"* **Weak form (a chronological tendency):** survives for the work-date clocks DCS "
        f"(τ = {summary['dcs']['mean_tau']:.3f}) and Dharmamitra (τ = {summary['dm']['mean_tau']:.3f}), "
        f"both well below the random-order mixed rate. It does **not** survive for PD's own SWC "
        f"clock (τ = {summary['pd_swc']['mean_tau']:.3f}; mixed rate {pct(summary['pd_swc']['mixed_rate'])} "
        f"against a null mean of {pct(null['clocks']['pd_swc']['null_mean_rate'])}), which leans "
        f"descending rather than ascending.")
    add(f"* **Composite caveat.** The H6943 `any` rule gives {pct(any_obs)} against a null mean of "
        f"{pct(any_null['null_mean_rate'])} (P(null ≤ observed) = {any_null['p_null_le_observed']:.3g}). "
        f"That marginal difference is carried by the imprint clock, which is structurally unable to "
        f"speak about work chronology; it must not be read as support for the Preface claim.")
    add("* **What does not follow.** A mixed sequence is not by itself an editorial error. "
        "The adjudication sheet separates real inversions from date-proxy artefacts, "
        "edition mismatch, non-chronological ordering principles and OCR-siglum errors.")
    add("")
    add("## Adjudication")
    add("")
    add(adj_note)
    add("")
    add("The sheet `data/pd/pd_citation_order_adjudication.tsv` contains 100 flagged "
        "(mixed) and 100 monotone controls drawn with a seeded RNG, stratified by "
        "deciding clock, DCS genre (or `undetermined`), citation-count bucket and "
        "position in *a-*. Annotators fill `annotator_1`, `annotator_2` and "
        "`adjudicated_class` with one of: `real inversion`, `date-proxy error`, "
        "`edition mismatch`, `non-chronological ordering principle`, `OCR-siglum error`. "
        "Cohen's κ is computed on the two independent annotator columns; precision of "
        "inversion is `real inversion / all flagged rows` after adjudication.")
    add("")
    add("## Confounds and unknowns")
    add("")
    add("* Citations may be ordered by grammatical construction, text type or relevance, not date.")
    add("* Runs of one siglum are collapsed; the raw run count is still a grouping signature, not chronology.")
    add("* PD/SWC dates are coarse and OCR-noisy; DCS is structurally sparse (120 of 4,988 primary sigla have a coverage row); "
        "Dharmamitra is work-level, not edition-level; imprint years date the editor's copy, not the work.")
    add("* The eligible base is itself a selection: divisions with ≥2 datable citations are better-cited and may be atypical. "
        "The funnel above reports the eligible/ineligible contrast.")
    add("* Missing edition years (325 of 1,437 AOB declared rows), SWC OCR noise, sparse DCS coverage and eligible-base selection are named, not corrected.")
    add("")
    add("## Refutation condition (stated in advance)")
    add("")
    add("* If the adjudicated precision of `inversion` as a claim about editorial practice falls below 50 %, the negative result is withdrawn.")
    add("* If the null comparison reverses (observed mixed rate at or above the random-order mean), the weak-form survival is withdrawn.")
    add("* If the H6943 entry anchor does not reconcile to 2,118, the parser is wrong and no verdict is valid.")
    add("")
    add("## Reproduce")
    add("")
    add("```bash")
    add("curl -L -o pdtxt.zip https://www.sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/downloads/pdtxt.zip")
    add("unzip pdtxt.zip")
    add("python scripts/pd_citation_order_full.py --pd-txt txt/pd.txt --build")
    add("python scripts/pd_citation_order_full.py --check")
    add("```")
    add("")
    add("_Dr. Mārcis Gasūns_")
    add("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


# ------------------------------------------------------------------ check


def check() -> int:
    if not OUT_TSV.exists() or not OUT_JSON.exists() or not OUT_ADJ.exists():
        print("FAIL: missing committed artefacts", file=sys.stderr)
        return 1
    with OUT_TSV.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    with OUT_ADJ.open(encoding="utf-8", newline="") as fh:
        adj = list(csv.DictReader(fh, delimiter="\t"))
    committed = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    if rows and not set(TSV_COLS).issubset(rows[0].keys()):
        print("FAIL: committed TSV lacks required columns", file=sys.stderr)
        return 1
    if len(adj) != 2 * ADJ_PER_ARM:
        print(f"FAIL: adjudication sheet has {len(adj)} rows, expected {2 * ADJ_PER_ARM}", file=sys.stderr)
        return 1
    if committed["population"]["h6943_eligible_entries"] != H6943_ANCHOR:
        print("FAIL: H6943 anchor does not reconcile", file=sys.stderr)
        return 1
    summary = summarize(rows)
    if summary != committed["summary"]:
        print("FAIL: summary recomputed from TSV differs from committed summary", file=sys.stderr)
        return 1
    null = null_model(rows, reps=committed["null"]["reps"], seed=committed["null"]["seed"])
    if null != committed["null"]:
        print("FAIL: null model recomputed from TSV differs from committed null", file=sys.stderr)
        return 1
    if len(rows) != committed["population"]["eligible_divisions_4clock"]:
        print("FAIL: TSV row count differs from population funnel", file=sys.stderr)
        return 1
    if committed["population"]["h6943_eligible_entries"] != H6943_ANCHOR:
        print("FAIL: anchor mismatch", file=sys.stderr)
        return 1
    report = REPORT.read_text(encoding="utf-8")
    for needle in (
        f"{committed['population']['eligible_divisions_4clock']:,}",
        rate_ci(summary["any"]),
        pct(null["clocks"]["any"]["observed_rate"]),
    ):
        if needle not in report:
            print(f"FAIL: report lacks recomputed number {needle!r}", file=sys.stderr)
            return 1
    print(f"OK: {len(rows):,} division rows; {len(adj)} adjudication rows; "
          f"H6943 anchor {H6943_ANCHOR:,} reconciled; null {committed['null']['reps']:,} reps reproduced")
    return 0


# ------------------------------------------------------------------ main


ADJ_NOTE = (
    "**Status: sheet drawn, human annotation outstanding.** The 200 rows in "
    "`data/pd/pd_citation_order_adjudication.tsv` are the seeded adjudication frame. "
    "No human annotator has filled it in this run, so no κ and no adjudicated "
    "precision are reported, and the verdict above is a verdict about the dating "
    "clocks, not yet about editorial practice."
)


def refresh() -> int:
    """Recompute the derived blocks from the committed TSV and rewrite them.

    The TSV is the committed source of truth for every number in the summary
    JSON and the report; the 55 MB PDScan text is not committed and is not
    needed to re-derive them.  ``--refresh`` therefore rewrites the summary
    block, the null block and the report from the committed TSV plus the
    committed population/inputs blocks, leaving the row-level TSV and the
    adjudication sheet untouched.
    """
    if not OUT_TSV.exists() or not OUT_JSON.exists():
        print("FAIL: missing committed artefacts", file=sys.stderr)
        return 1
    with OUT_TSV.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    committed = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    print("recomputing summary from the committed TSV ...", file=sys.stderr)
    summary = summarize(rows)
    print("running pooled permutation null ...", file=sys.stderr)
    null = null_model(rows, reps=committed["null"]["reps"], seed=committed["null"]["seed"])
    payload = {
        "handoff": committed.get("handoff", "H7093"),
        "generated": committed.get("generated", "2026-10-19"),
        "population": committed["population"],
        "summary": summary,
        "null": null,
        "inputs": committed["inputs"],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(summary, null, committed["population"], committed["inputs"], ADJ_NOTE)
    print("rewrote data/pd/pd_citation_order_full_summary.json and "
          "reports/PD_CITATION_ORDER_FULL_2026.md", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pd-txt", type=Path)
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--refresh", action="store_true",
                    help="recompute the summary JSON and the report from the "
                         "committed TSV (no --pd-txt needed)")
    args = ap.parse_args()
    if args.check:
        return check()
    if args.refresh:
        return refresh()
    if not args.build:
        ap.error("choose --build, --check or --refresh")
    if not args.pd_txt or not args.pd_txt.exists():
        print("FAIL: --pd-txt is required (Cologne PDScan pdtxt.zip pd.txt)", file=sys.stderr)
        return 2

    print("parsing population ...", file=sys.stderr)
    rows, stats = build(args.pd_txt)
    print(f"  divisions={len(rows):,} entries={stats['entries']:,} "
          f"anchor={stats['h6943_eligible_entries']:,}", file=sys.stderr)
    summary = summarize(rows)
    print("running pooled permutation null ...", file=sys.stderr)
    null = null_model(rows)
    adj = draw_adjudication(rows)
    pins = input_pins(args.pd_txt)
    payload = {
        "handoff": "H7093",
        "generated": "2026-10-19",
        "population": stats,
        "summary": summary,
        "null": null,
        "inputs": pins,
    }
    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    write_tsv(rows, OUT_TSV, TSV_COLS)
    write_tsv(adj, OUT_ADJ, ADJ_COLS)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    write_report(summary, null, stats, pins, ADJ_NOTE)
    print(json.dumps({"population": stats, "any": summary["any"],
                      "null_any": null["clocks"]["any"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
