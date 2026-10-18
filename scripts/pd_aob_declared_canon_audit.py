#!/usr/bin/env python3
"""H6923 -- PD declared-canon denominator audit (1,419 vs 1,118).

Three numbers circulate for the AOB declared canon of PD (*An Encyclopaedic
Dictionary of Sanskrit on Historical Principles*, Deccan College):

  * **1,419** -- the "edition-level rows" denominator behind metric 2
    (118 / N = 8.32 %), recorded in ``data/pd/pd_dcs_metrics.json``;
  * **1,118** -- the edition rows actually carried by the published artifact
    ``data/pd/pd_aob_declared_works.tsv`` (1,112 work groups, sum(n_editions));
  * **1,464** -- the printed census («1 464 книг») quoted in the press.

They are not the same quantity. This audit measures what each one is, from the
two committed sources (the OCR of the official KoshaSHRI AOB PDF in the PD repo
and the landed TSVs here), and states the denominator as a band instead of a
point that no committed parser reproduces.

Measurements (all deterministic, no network):

  R1  entry-like printed lines -- a backticked line whose token starts with a
      capital Latin letter AND carries a bibliographic tail (>= 6 letters or a
      1850-2029 year, or a merged ``Siglum Title`` token).  A printed AOB entry
      begins with its siglum at the left margin, so this counts entries, not
      physical lines.
  R2  garbled-start dated lines -- lines whose token was OCR-mangled past a
      leading capital (``(क्प).``, ``2१०६8.``) but which carry a year and a
      title.  An UPPER BOUND on entries R1 misses: carry-over fragments of the
      previous row also qualify, so R2 is reported, never added to R1.
  R3  merged siglum+title tokens -- ``AllaU. Allopanisad``: one OCR line, one
      printed entry, but the pass-2 clean filter (no space in the siglum) threw
      these away.  This is the mechanism that turned 1,419 into 1,118.

Run:
  python3 scripts/pd_aob_declared_canon_audit.py            # measure + write JSON
  python3 scripts/pd_aob_declared_canon_audit.py --check    # verify the committed JSON
  python3 scripts/pd_aob_declared_canon_audit.py --aob /path/to/AOB.md

Exit codes: 0 ok / measured, 1 drift under --check, 2 input missing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# --- tunables (deliberately blunt: every one of them is documented above) ----
ENTRY_MIN_TAIL_LETTERS = 6      # R1: title/author tail must carry this many letters
GARBLED_MIN_TAIL_LETTERS = 8    # R2: stricter, because R2 is an upper bound
YEAR_RE = re.compile(r"\b(1[89]\d\d|20[0-2]\d)\b")
LETTER_RE = re.compile(r"[A-Za-z\u00c0-\u024f]")
UPPER_START_RE = re.compile(r"^[A-Z\u00c0-\u024f]")
TOKEN_RE = re.compile(r"^\s*`([^`]*)`(.*)$")
PAGE_RE = re.compile(r"^## Page (\d+)$")
# a first word that can be a printed siglum: starts upper-case, no whitespace
SIGLUM_WORD_RE = re.compile(r"^[A-Z\u00c0-\u024f][^\s]{0,24}$")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def letters(s: str) -> int:
    return len(LETTER_RE.findall(s))


def count_lines(lines):
    """R1/R2/R3 over the OCR of the printed AOB."""
    page = 0
    pages = set()
    backtick_lines = 0
    first_tokens = []
    r1 = 0
    r2 = 0
    merged = 0
    prev_token = None
    consecutive_dups = 0

    for line in lines:
        m = PAGE_RE.match(line)
        if m:
            page = int(m.group(1))
            pages.add(page)
            continue
        m = TOKEN_RE.match(line)
        if not m:
            continue
        backtick_lines += 1
        token = m.group(1).strip()
        rest = m.group(2).strip()
        first_tokens.append(token)
        tail_letters = letters(rest)
        has_year = bool(YEAR_RE.search(rest))
        words = token.split()
        token_letters = letters(token)

        if UPPER_START_RE.match(token):
            merged_here = len(words) > 1 and bool(SIGLUM_WORD_RE.match(words[0])) \
                and token_letters >= 10
            if tail_letters >= ENTRY_MIN_TAIL_LETTERS or has_year or merged_here:
                r1 += 1
                if merged_here:
                    merged += 1
                if token == prev_token:
                    consecutive_dups += 1
                prev_token = token
            continue
        # non-uppercase start: only a strong bibliographic tail counts (R2)
        if has_year and tail_letters >= GARBLED_MIN_TAIL_LETTERS and token_letters >= 6:
            r2 += 1

    return {
        "pages": len(pages),
        "backtick_start_lines": backtick_lines,
        "distinct_first_tokens": len(set(first_tokens)),
        "entry_like_lines_r1": r1,
        "merged_siglum_title_tokens_r3": merged,
        "consecutive_duplicate_sigla": consecutive_dups,
        "garbled_start_dated_r2_upper_bound": r2,
    }


def read_tsv_rows(path: Path):
    with open(path, encoding="utf-8", newline="") as f:
        header = f.readline()
        rows = [ln for ln in f.read().splitlines() if ln.strip()]
    return header.rstrip("\n").split("\t"), rows


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def measure(atlas: Path, aob: Path) -> dict:
    metrics_path = atlas / "data/pd/pd_dcs_metrics.json"
    works_path = atlas / "data/pd/pd_aob_declared_works.tsv"

    metrics = json.loads(read_text(metrics_path))
    n_covered = int(metrics["n_covered_dcs_titles"])

    cols, rows = read_tsv_rows(works_path)
    if "n_editions" not in cols:
        raise SystemExit(f"[FAIL] {works_path} has no n_editions column")
    i_ed = cols.index("n_editions")
    edition_rows = sum(int(r.split("\t")[i_ed]) for r in rows)
    work_rows = len(rows)

    lines = read_text(aob).splitlines()
    census = count_lines(lines)

    # the pass-1 point is a HISTORICAL value and must not be read off the live
    # n_declared_aob_rows_edition_level field: since H6932 (18-10-2026) that field carries the
    # ruled denominator (1,423 usable inventory entries), not the pass-1 parse (1,419)
    recorded_pass1 = int(metrics.get("n_declared_aob_rows_edition_level_pass1_point",
                                    metrics.get("n_declared_aob_rows_edition_level", 0)))
    print_census = 1464  # «1 464 книг», Indian Express, quoted at pass-1
    reparse_raw = 1517   # scripts-h6707/parse_aob.py on the same OCR (Uprava papers/A68)
    structural = census["entry_like_lines_r1"]

    band_lo = min(recorded_pass1 or reparse_raw, structural)
    band_hi = max(reparse_raw, structural)
    if recorded_pass1:
        band_lo = min(band_lo, recorded_pass1)

    at = {}
    for label, n in (("published_tsv_edition_rows", edition_rows),
                     ("print_census", print_census),
                     ("pass1_recorded", recorded_pass1),
                     ("structural_r1", structural),
                     ("reparse_raw", reparse_raw)):
        if n:
            at[label] = {"n": n, "pct": round(100.0 * n_covered / n, 2)}

    return {
        "generated_by": "H6923 scripts/pd_aob_declared_canon_audit.py "
                        "(DeepSeek Flash, deepseek-flash)",
        "audited_on": "2026-10-17",
        "method": "R1 entry-like printed lines; R2 garbled-start dated lines (upper bound, "
                  "never added); R3 merged siglum+title tokens (the clean-filter loss class)",
        "source_aob": {
            "path": "PD/AOB.md (sanskrit-lexicon/PD, OCR of the official KoshaSHRI AOB PDF)",
            "sha256": sha256_of(aob),
            "lines_total": len(lines),
            "pages": census["pages"],
        },
        "line_census": {
            "backtick_start_lines": census["backtick_start_lines"],
            "distinct_first_tokens": census["distinct_first_tokens"],
        },
        "entry_estimates": {
            "entry_like_lines_r1": census["entry_like_lines_r1"],
            "merged_siglum_title_tokens_r3": census["merged_siglum_title_tokens_r3"],
            "consecutive_duplicate_sigla": census["consecutive_duplicate_sigla"],
            "garbled_start_dated_r2_upper_bound":
                census["garbled_start_dated_r2_upper_bound"],
        },
        "published_artifact": {
            "file": "data/pd/pd_aob_declared_works.tsv",
            "work_rows": work_rows,
            "edition_rows": edition_rows,
            "is": "clean-subset FLOOR (every row survived the pass-2 filter), not the canon",
        },
        "recorded_numbers": {
            "pass1_loose_entries": recorded_pass1,
            "pass1_reproducible": False,
            "reparse_raw_entries": reparse_raw,
            "print_census": print_census,
        },
        "denominator": {
            "n_covered_dcs_titles": n_covered,
            "band_lo": band_lo,
            "band_hi": band_hi,
            "structural_estimate": structural,
        },
        "metric_title_level_declared_pct_at": at,
        "verdict": (
            "1,419 is an ENTRY-level parse count (loose entry-start rule) with no committed "
            "parser behind it: the committed re-parse yields %d raw entries and the printed "
            "OCR supports %d entry-like lines, so the reproducible statement is the band "
            "[%d, %d] and 118/N = %.2f-%.2f %%. The published TSV's %d edition rows are a "
            "clean-subset FLOOR, not the canon: %d of %d entry lines carry an OCR-merged "
            "'Siglum Title' token that the pass-2 filter discarded, so 118/1,118 = %.2f %% "
            "overstates coverage and must never be quoted as the declared canon."
            % (reparse_raw, structural, band_lo, band_hi,
               at["reparse_raw"]["pct"],
               at["pass1_recorded"]["pct"] if "pass1_recorded" in at
               else at["structural_r1"]["pct"],
               edition_rows,
               census["merged_siglum_title_tokens_r3"], structural,
               at["published_tsv_edition_rows"]["pct"])
        ),
    }


def print_report(result: dict) -> None:
    d = result["denominator"]
    print("PD declared-canon denominator audit (H6923)\n")
    print("source: %s  (%d lines, %d pages)"
          % (result["source_aob"]["path"], result["source_aob"]["lines_total"],
             result["source_aob"]["pages"]))
    print("  backtick-start lines        %6d" % result["line_census"]["backtick_start_lines"])
    print("  R1 entry-like lines         %6d" % d["structural_estimate"])
    print("  R3 merged siglum+title      %6d"
          % result["entry_estimates"]["merged_siglum_title_tokens_r3"])
    print("  R2 garbled-start (bound)    %6d"
          % result["entry_estimates"]["garbled_start_dated_r2_upper_bound"])
    print("\ndenominator candidates (n covered = %d):" % d["n_covered_dcs_titles"])
    for label, cell in result["metric_title_level_declared_pct_at"].items():
        print("  %-32s N=%-6d  118/N = %5.2f %%" % (label, cell["n"], cell["pct"]))
    print("\nband: [%d, %d]  structural estimate %d"
          % (d["band_lo"], d["band_hi"], d["structural_estimate"]))
    print("published artifact: %s -- %d works / %d edition rows"
          % (result["published_artifact"]["file"],
             result["published_artifact"]["work_rows"],
             result["published_artifact"]["edition_rows"]))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--aob", default=str(Path.home() / "Documents/GitHub/PD/AOB.md"),
                    help="path to PD/AOB.md (OCR of the official AOB PDF)")
    ap.add_argument("--atlas", default=str(Path(__file__).resolve().parent.parent),
                    help="csl-atlas root (default: the repo this script lives in)")
    ap.add_argument("--out", default="data/pd/pd_aob_declared_canon_audit.json")
    ap.add_argument("--check", action="store_true",
                    help="recompute and compare with the committed JSON; exit 1 on drift")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    atlas = Path(args.atlas).resolve()
    aob = Path(args.aob)
    out = atlas / args.out
    if not aob.is_file():
        print("[FAIL] AOB.md not found: %s (pass --aob)" % aob, file=sys.stderr)
        return 2
    if not (atlas / "data/pd/pd_dcs_metrics.json").is_file():
        print("[FAIL] not a csl-atlas root: %s" % atlas, file=sys.stderr)
        return 2

    result = measure(atlas, aob)
    if not args.quiet:
        print_report(result)

    if args.check:
        if not out.is_file():
            print("[FAIL] committed audit JSON missing: %s" % out, file=sys.stderr)
            return 2
        committed = json.loads(read_text(out))
        drift = [k for k in ("entry_estimates", "published_artifact", "denominator",
                             "metric_title_level_declared_pct_at")
                 if committed.get(k) != result.get(k)]
        if drift:
            print("[FAIL] audit JSON is stale, drifting keys: %s\n"
                  "       re-run without --check and commit the result." % ", ".join(drift),
                  file=sys.stderr)
            return 1
        print("[OK ] committed audit JSON matches a fresh measurement")
        return 0

    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    if not args.quiet:
        print("\nwrote %s" % out.relative_to(atlas))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
