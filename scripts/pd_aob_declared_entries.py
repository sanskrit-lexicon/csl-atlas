#!/usr/bin/env python3
"""H6932 -- reconcile the AOB declared-canon counts to one reproducible N.

Five numbers circulate for the declared canon of PD (*An Encyclopaedic
Dictionary of Sanskrit on Historical Principles*, Deccan College), the
denominator behind metric 2 (118 covered DCS titles / N):

  * **1,419** -- pass-1 loose entry parse, recorded in
    ``data/pd/pd_dcs_metrics.json``. No committed parser reproduces it (H6923).
  * **1,464** -- the printed census (press quote). External, not ours.
  * **1,476** -- R1 entry-like printed lines (``pd_aob_declared_canon_audit.py``).
  * **1,517** -- the pass-2 committed re-parse, raw.
  * **1,430 / 1,423** -- the landed entry inventory
    (``data/pd/pd_aob_entries.tsv``, H6720): 1,430 parsed rows, 1,423 usable
    after 7 OCR-noise rows the table itself flags ``junk``.

H6932's job is to stop treating these as a band and show which one is the same
quantity as the others. This script measures the line-level reconciliation that
ties R1 to the landed inventory, exactly:

    R1 entry-like lines                    1,476
    - dotless OCR wrap fragments            -165   (R1 reads a wrapped title
                                                    continuation as an entry)
    + printed entries R1 misses             +119   (stray-quote-prefixed sigla,
                                                    Devanagari/garble starts,
                                                    digit-prefixed starts)
    = parsed entries                       1,430   == rows of the landed TSV
    - junk (OCR noise, not entries)            7
    = usable inventory entries             1,423

The identity is asserted, not narrated: ``--selftest`` fails if either
sub-total drifts, so a change to either parser surfaces here instead of in a
silently wrong denominator.

Ruling (MG 18-10-2026, H6932 fork): the denominator is **1,423 usable inventory
entries**, so metric 2 is 118 / 1,423 = **8.29 % ≈ 8.3 %, one in twelve**.
1,476 was the previous central estimate; it is a line census, and the 165/119
error it carries is now measured rather than assumed. 1,464 stays an external
census, 1,517 a superseded raw re-parse, 1,419 unreproducible.

Run:
  python3 scripts/pd_aob_declared_entries.py            # measure + write artifacts
  python3 scripts/pd_aob_declared_entries.py --check    # verify committed artifacts + spine
  python3 scripts/pd_aob_declared_entries.py --selftest # assert the reconciliation identities
  python3 scripts/pd_aob_declared_entries.py --aob /path/to/AOB.md

Exit codes: 0 ok / measured, 1 drift under --check, 2 input missing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# the two parsers this reconciliation sits between -- imported, never copied, so
# there is exactly one definition of "an entry line" and "a parsed entry"
import pd_aob_declared_canon_audit as A  # noqa: E402
import pd_aob_sigla_reconciliation as P  # noqa: E402

ATLAS = SCRIPT_DIR.parent
ENTRIES_TSV = ATLAS / "data" / "pd" / "pd_aob_entries.tsv"
METRICS_JSON = ATLAS / "data" / "pd" / "pd_dcs_metrics.json"
OUT_JSON = ATLAS / "data" / "pd" / "pd_aob_denominator_reconciliation.json"
OUT_TSV = ATLAS / "data" / "pd" / "pd_aob_entry_line_classes.tsv"

N_COVERED_DCS_TITLES = 118
RULING_DATE = "18-10-2026"
RULING_BY = "MG 18-10-2026 (H6932 fork)"

#: every quoted N, and what it actually counts -- the thing this script exists to fix
COUNT_CLASSES = {
    "1419_pass1_loose_parse": {
        "n": 1419,
        "is": "pass-1 loose entry-start parse; no committed parser behind it",
        "reproducible": False,
    },
    "1423_usable_inventory_entries": {
        "n": 1423,
        "is": "landed entry inventory minus 7 OCR-junk rows (data/pd/pd_aob_entries.tsv)",
        "reproducible": True,
    },
    "1430_parsed_entries": {
        "n": 1430,
        "is": "landed entry inventory including the 7 junk rows",
        "reproducible": True,
    },
    "1362_wellformed_entries": {
        "n": 1362,
        "is": "inventory entries passing the well-formed tail test (NOT the denominator)",
        "reproducible": True,
    },
    "1464_print_census_books": {
        "n": 1464,
        "is": "printed census of books (external press quote)",
        "reproducible": False,
    },
    "1476_structural_r1_lines": {
        "n": 1476,
        "is": "R1 entry-like printed lines (a line census, over-counts by 165, misses 119)",
        "reproducible": True,
    },
    "1517_reparse_raw": {
        "n": 1517,
        "is": "pass-2 committed re-parse, raw before the clean filter",
        "reproducible": True,
    },
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pct(n: int, d: int) -> float:
    return round(100.0 * n / d, 2)


def load_inventory(path: Path) -> dict:
    """Count the landed inventory straight from the committed TSV."""
    lines = read_text(path).splitlines()
    header = lines[0].split("\t")
    idx = {name: i for i, name in enumerate(header)}
    n = junk = wellformed = 0
    for line in lines[1:]:
        if not line.strip():
            continue
        cells = line.split("\t")
        n += 1
        if cells[idx["junk"]] == "yes":
            junk += 1
        if cells[idx["wellformed"]] == "yes":
            wellformed += 1
    return {
        "path": str(path.relative_to(ATLAS)),
        "sha256": sha256_of(path),
        "entries_parsed": n,
        "junk": junk,
        "usable": n - junk,
        "wellformed": wellformed,
    }


def classify_lines(text: str) -> dict:
    """Line-level 2x2 between the R1 line census and the landed entry parser.

    Reads as: ``both``      line is an entry under both rules
              ``parser_only`` a real printed entry R1 does not count
              ``r1_only``     a dotless OCR wrap fragment R1 counts as an entry
              ``neither``     a continuation line, a page header, a bare token
    """
    page = 0
    counts = {"both": 0, "parser_only": 0, "r1_only": 0, "neither": 0}
    disputed = []

    for line in text.splitlines():
        page_match = A.PAGE_RE.match(line)
        if page_match:
            page = int(page_match.group(1))
            continue
        token_match = A.TOKEN_RE.match(line)
        if not token_match:
            continue

        token = token_match.group(1).strip()
        rest = token_match.group(2).strip()
        clean = token.lstrip("\u2018\u2019\u201c\u201d\"'`([{*")
        words = clean.split()
        tail_letters = A.letters(rest)
        has_year = bool(A.YEAR_RE.search(rest))

        # --- R1's view (pd_aob_declared_canon_audit.count_lines) -------------
        merged_r1 = (
            len(words) > 1
            and bool(A.SIGLUM_WORD_RE.match(words[0]))
            and A.letters(token) >= 10
        )
        r1 = bool(A.UPPER_START_RE.match(token)) and (
            tail_letters >= A.ENTRY_MIN_TAIL_LETTERS or has_year or merged_r1
        )

        # --- the landed parser's view (pd_aob_sigla_reconciliation.parse_aob) -
        merged = (
            len(words) > 1
            and bool(P.SIGLUM_WORD_RE.match(words[0]))
            and P.letters(token) >= 10
        )
        dotless = not merged and not (
            clean[-1:] in ".,;:*-" or any(ord(c) > 127 for c in clean)
        )
        if dotless:
            parsed = False
            class_of = "dotless_wrap_fragment"
        else:
            tail_ok = (
                P.letters(rest) >= P.ENTRY_MIN_TAIL_LETTERS
                or bool(P.YEAR_RE.search(rest))
                or merged
            )
            if P.UPPER_START_RE.match(clean):
                parsed = tail_ok
                class_of = "entry"
            else:
                latin = [w for w in words if P.SIGLUM_WORD_RE.match(w)]
                parsed = bool(latin) and tail_ok and P.letters(rest) >= P.ENTRY_MIN_TAIL_LETTERS
                class_of = "garbled_or_quote_prefixed_entry" if parsed else "continuation"
                if parsed and bool(P.UPPER_START_RE.match(token)):
                    class_of = "entry"

        if parsed and r1:
            kind = "both"
        elif parsed:
            kind = "parser_only"
        elif r1:
            kind = "r1_only"
        else:
            kind = "neither"
        counts[kind] += 1

        if kind in ("parser_only", "r1_only"):
            disputed.append(
                {
                    "kind": kind,
                    "class": class_of,
                    "page": page,
                    "token": token,
                    "tail": rest[:120],
                }
            )

    r1_total = counts["both"] + counts["r1_only"]
    parsed_total = counts["both"] + counts["parser_only"]
    return {
        "counts": counts,
        "r1_total": r1_total,
        "parsed_total": parsed_total,
        "disputed": disputed,
    }


def measure(aob: Path) -> dict:
    text = read_text(aob)
    inventory = load_inventory(ENTRIES_TSV)
    cls = classify_lines(text)

    # the line census must agree with the committed audit, and the parser with
    # the landed TSV -- otherwise this script is reconciling two stale numbers
    audit_census = A.count_lines(text.splitlines())
    parsed = P.parse_aob(text)

    counts = cls["counts"]
    usable = inventory["usable"]
    reported = {
        "source_aob": {
            "path": str(aob),
            "sha256": sha256_of(aob),
            "lines": len(text.splitlines()),
            "pages": audit_census["pages"],
        },
        "entry_inventory": inventory,
        "line_reconciliation": {
            "both": counts["both"],
            "parser_only_recovered": counts["parser_only"],
            "r1_only_wrap_fragments": counts["r1_only"],
            "neither": counts["neither"],
            "r1_entry_like_lines": cls["r1_total"],
            "parsed_entries": cls["parsed_total"],
            "r1_audit_census": audit_census["entry_like_lines_r1"],
            "parser_entry_count": len(parsed),
            "identity": "%d - %d + %d = %d"
            % (
                cls["r1_total"],
                counts["r1_only"],
                counts["parser_only"],
                cls["parsed_total"],
            ),
            "cross_checks": {
                "r1_matches_committed_audit": cls["r1_total"]
                == audit_census["entry_like_lines_r1"],
                "parser_matches_committed_tsv": cls["parsed_total"]
                == inventory["entries_parsed"]
                == len(parsed),
            },
        },
        "count_classes": COUNT_CLASSES,
        "denominator": {
            "n_covered_dcs_titles": N_COVERED_DCS_TITLES,
            "ruled_n": usable,
            "ruled_on": RULING_DATE,
            "ruled_by": RULING_BY,
            "pct": pct(N_COVERED_DCS_TITLES, usable),
            "display_pct": round(100.0 * N_COVERED_DCS_TITLES / usable, 1),
            "ratio": "one in %.1f" % (usable / N_COVERED_DCS_TITLES),
            "pct_by_class": {
                key: pct(N_COVERED_DCS_TITLES, val["n"]) for key, val in COUNT_CLASSES.items()
            },
            "provenance_band": [1419, 1517],
            "superseded_central_estimate": 1476,
        },
        "generated_by": "H6932 scripts/pd_aob_declared_entries.py (DeepSeek Flash, deepseek-flash)",
        "measured_on": RULING_DATE,
        # kept off the JSON below -- the disputed lines are the audit trail, not evidence to re-read
        "_disputed": cls["disputed"],
    }
    return reported


def render_tsv(rows) -> str:
    cols = ["kind", "class", "page", "token", "tail"]
    out = ["\t".join(cols)]
    for row in rows:
        out.append("\t".join(str(row.get(c, "")) for c in cols))
    return "\n".join(out) + "\n"


def write_artifacts(result: dict) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {k: v for k, v in result.items() if not k.startswith("_")}
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_TSV.write_text(render_tsv(result["_disputed"]), encoding="utf-8")


def selftest(aob: Path = None) -> int:
    aob = aob or default_aob()
    if not aob.exists():
        print("SELFTEST FAIL: AOB.md not found at %s" % aob)
        return 2
    result = measure(aob)
    lr = result["line_reconciliation"]
    inv = result["entry_inventory"]
    failures = []

    if not lr["cross_checks"]["r1_matches_committed_audit"]:
        failures.append("R1 total %d != committed audit %d" % (lr["r1_entry_like_lines"], lr["r1_audit_census"]))
    if not lr["cross_checks"]["parser_matches_committed_tsv"]:
        failures.append(
            "parsed %d != landed TSV %d rows" % (lr["parsed_entries"], inv["entries_parsed"])
        )
    if lr["r1_entry_like_lines"] - lr["r1_only_wrap_fragments"] + lr["parser_only_recovered"] != lr["parsed_entries"]:
        failures.append("reconciliation identity does not close: %s" % lr["identity"])
    if inv["entries_parsed"] - inv["junk"] != inv["usable"]:
        failures.append("inventory usable != parsed - junk")
    if result["denominator"]["ruled_n"] != inv["usable"]:
        failures.append("ruled N != usable inventory")

    if failures:
        for f in failures:
            print("SELFTEST FAIL: %s" % f)
        return 1
    print(
        "SELFTEST PASS: %d - %d + %d = %d parsed; %d - %d junk = %d usable; 118/%d = %.2f %% (%.1f %%)"
        % (
            lr["r1_entry_like_lines"],
            lr["r1_only_wrap_fragments"],
            lr["parser_only_recovered"],
            lr["parsed_entries"],
            inv["entries_parsed"],
            inv["junk"],
            inv["usable"],
            inv["usable"],
            result["denominator"]["pct"],
            result["denominator"]["display_pct"],
        )
    )
    return 0


def check(aob: Path) -> int:
    if not OUT_JSON.exists():
        print("CHECK FAIL: %s missing -- run without --check first" % OUT_JSON.name)
        return 1
    fresh = measure(aob)
    committed = json.loads(read_text(OUT_JSON))
    failures = []

    for key in ("source_aob", "entry_inventory", "line_reconciliation", "denominator"):
        if fresh[key] != committed.get(key):
            failures.append("committed %s drifted from a fresh measure" % key)

    # the fail condition this handoff was minted for: every quoted N must be
    # recomputable from a committed file, and the spine must quote the ruled one
    metrics = json.loads(read_text(METRICS_JSON))
    usable = fresh["entry_inventory"]["usable"]
    expected = {
        "n_declared_aob_rows_edition_level": usable,
        "metric_title_level_declared_pct_denominator": usable,
        "metric_title_level_declared_pct": fresh["denominator"]["pct"],
        "declared_canon_rows_reproducible": True,
    }
    for key, want in expected.items():
        got = metrics.get(key)
        if got != want:
            failures.append("spine %s = %r, expected %r" % (key, got, want))

    for key in ("n_declared_aob_print_census", "n_declared_aob_entry_lines_structural_r1"):
        if key in metrics:
            want = COUNT_CLASSES[
                "1464_print_census_books" if "print_census" in key else "1476_structural_r1_lines"
            ]["n"]
            if metrics[key] != want:
                failures.append("spine %s = %r, expected %r" % (key, metrics[key], want))

    if failures:
        for f in failures:
            print("CHECK FAIL: %s" % f)
        return 1
    print(
        "CHECK PASS: %d usable -> 118/%d = %.2f %% (%.1f %%), reproducible from %s"
        % (usable, usable, fresh["denominator"]["pct"], fresh["denominator"]["display_pct"], ENTRIES_TSV.name)
    )
    return 0


def default_aob() -> Path:
    return ATLAS.parent / "PD" / "AOB.md"


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--aob", default=None, help="path to PD/AOB.md (default: ../PD/AOB.md)")
    ap.add_argument("--check", action="store_true", help="recompute and compare with the committed artifacts + spine")
    ap.add_argument("--selftest", action="store_true", help="assert the reconciliation identities")
    args = ap.parse_args(argv)

    aob = Path(args.aob) if args.aob else default_aob()
    if args.selftest:
        return selftest(aob)
    if not aob.exists():
        print("input missing: %s" % aob, file=sys.stderr)
        return 2
    if args.check:
        return check(aob)

    result = measure(aob)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    write_artifacts(result)

    lr = result["line_reconciliation"]
    inv = result["entry_inventory"]
    den = result["denominator"]
    print("AOB declared-canon denominator reconciliation (H6932)")
    print("  source            %s (%d pages)" % (result["source_aob"]["path"], result["source_aob"]["pages"]))
    print("  R1 entry-like lines      %6d" % lr["r1_entry_like_lines"])
    print("  - dotless wrap fragments %6d" % lr["r1_only_wrap_fragments"])
    print("  + entries R1 misses      %6d" % lr["parser_only_recovered"])
    print("  = parsed entries         %6d  (== landed TSV rows)" % lr["parsed_entries"])
    print("  - junk                   %6d" % inv["junk"])
    print("  = usable inventory       %6d  (the ruled denominator)" % inv["usable"])
    print(
        "  metric 2                  118 / %d = %.2f %% (%.1f %%, %s)"
        % (den["ruled_n"], den["pct"], den["display_pct"], den["ratio"])
    )
    print("  wrote %s" % OUT_JSON.name)
    print("  wrote %s (%d disputed rows)" % (OUT_TSV.name, len(result["_disputed"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
