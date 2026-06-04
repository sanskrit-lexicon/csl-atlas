"""Phase L0.6 / M1 — dictionary microstructure: subentry inventory.

Counts the DERIVATIVE-SUBENTRY structure inside each entry — the secondary
conjugations (Caus./Pass./Desid./Intens./Den./Periphr.) and compound blocks
(Comp.) that the European-tradition dicts mark with <ab>…</ab> abbreviation
tags. Feeds the "verb-derivation matrix" (METALEXICOGRAPHY/MICROSTRUCTURE docs,
Article 9).

DETECTION (first pass = uniform, conservative, cross-dict):
  The only signal reliable across 44 heterogeneous dicts is the <ab> token. We
  match it CASE-INSENSITIVELY — MW writes <ab>Caus.</ab>, PWG writes the same
  lemma's causative as lowercase <ab>caus.</ab> (capital-only would undercount
  PWG ~365x). Tokens are lowercased + dot-stripped + matched against an exact
  set, so `compar.` (comparative degree) is NOT mistaken for `comp.` (compound).
  A single tag holding two markers (MW `<ab>Desid. Caus.</ab>`) flags depth >= 2.

  Validated against the MW `gam` ground truth (MICROSTRUCTURE-MACROSTRUCTURE.md
  §1.1): MW gam shows Caus./Desid./Intens./Pass. — run `--probe gam` to confirm.

THE "0 != STRUCTURELESS" CAVEAT (mirrors data/forensic/CITATION_TAGGING.md):
  n_subentries = 0 means "no <ab>-tagged secondary-conjugation marker in THIS
  dict's convention", NOT "flat entry". Indigenous (SKD/VCP) and specialised
  name/plant/epigraphy dicts (INM/SNP/PGN/PE) read near-0 because they hold few
  verb roots and/or don't use the <ab> apparatus. Counts are comparable WITHIN a
  dict's convention; the per-dict aggregate is what reveals which dicts use it.

DEFERRED (need per-dict structural parsing, not a uniform marker):
  - preverb subentries (PWG dash/parenthetical convention) — `n_dash_segments`
    is shipped as an EXPERIMENTAL structural proxy only, not folded into the
    headline count;
  - participle/infinitive AS subentry vs. mere paradigm mention (<ab>p.p.</ab>,
    <ab>inf.</ab> fire for every verb) — excluded to keep the signal clean;
  - object+verb idiom subentries (MW prose, no tag).

Reads csl-orig bodies directly via parse_cslorig.iter_entries (bodies aren't
cached). Run from repo root:
    python scripts/lexico/m1_subentries.py --probe gam          # eyeball one lemma
    python scripts/lexico/m1_subentries.py --sample k           # one letter-band, all dicts
    python scripts/lexico/m1_subentries.py --all                # every dict, every entry
    python scripts/lexico/m1_subentries.py --dicts mw pwg ap    # explicit subset
Outputs (data/lexico/; sample runs get a `.<letter>` infix):
    microstructure_subentries[.<letter>].csv   per-entry rows where n_subentries>0
    microstructure_by_dict[.<letter>].json     compact per-dict aggregate
    m1_report[.<letter>].json                  run metadata + caveats + marker table
"""

import os
import re
import sys
import csv
import glob
import json
import collections

sys.path.insert(0, os.path.abspath("scripts/forensic"))
from parse_cslorig import iter_entries, CSL_ORIG

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OUT_DIR = "data/lexico"

# token (lowercase, dot-stripped) -> category. `compar` deliberately absent so the
# comparative degree is never counted as a compound. Multi-token tags ("desid. caus.")
# split on whitespace and match each part.
CAT_TOKENS = {
    "caus": "caus",
    "pass": "pass",
    "desid": "desid", "desider": "desid",
    "intens": "intens", "frequent": "intens", "freq": "intens",
    "den": "den", "denom": "den",
    "periphr": "periphr", "periph": "periphr",
    "comp": "comp", "compp": "comp",
}
CATEGORIES = ["caus", "pass", "desid", "intens", "den", "periphr", "comp"]
# secondary conjugations OF A VERB ROOT — the meaningful "derivative depth per verb".
# den (noun->verb) attaches to nominal headwords and comp is largely nominal, so both
# are kept in by_category/n_subentries but EXCLUDED from the per-verb ratio.
VERBAL_DERIV = ["caus", "pass", "desid", "intens", "periphr"]

_AB = re.compile(r"<ab>(.*?)</ab>", re.DOTALL)
_DIV_N = re.compile(r'<div n="([^"]*)"')  # CDSL <div> = flat, self-delimiting TYPE marker (no nesting)
_CL = re.compile(r"<ab>\s*cl\s*\.?\s*</ab>", re.IGNORECASE)
_INFO_VERB = re.compile(r'<info[^>]*\bverb=')
_DASH_SEG = re.compile(r"—")            # PWG em-dash structural segment delimiter
_TOK_STRIP = re.compile(r"^[^a-z]+|[^a-z]+$")  # trim surrounding punctuation from a lowercased token


def payload_categories(payload):
    """Return the set of subentry categories a single <ab> payload signals."""
    cats = set()
    for tok in payload.lower().split():
        tok = _TOK_STRIP.sub("", tok)
        cat = CAT_TOKENS.get(tok)
        if cat:
            cats.add(cat)
    return cats


def analyze_entry(body):
    """Per-entry microstructure metrics from a raw csl-orig body string."""
    per_cat = collections.Counter()
    positions = []          # start index of each tag matching >=1 category
    n_markers = 0           # number of <ab> tags matching >=1 category
    multi_marker = False    # a single tag carrying >=2 categories => depth >= 2

    for m in _AB.finditer(body):
        cats = payload_categories(m.group(1))
        if not cats:
            continue
        n_markers += 1
        positions.append(m.start())
        for c in cats:
            per_cat[c] += 1
        if len(cats) >= 2:
            multi_marker = True

    # total chars "governed by" derivative markers: span from each matching tag to
    # the next matching tag (or entry end). A segmentation proxy, not curated.
    total_chars = 0
    if positions:
        positions.sort()
        ends = positions[1:] + [len(body)]
        total_chars = sum(e - s for s, e in zip(positions, ends))

    # max_depth: a coarse 0/1/2 derivative-nesting flag. CDSL <div> tags are flat,
    # self-delimiting TYPE markers (113k opens / 0 closes in PWG), so there is no XML
    # nesting to read; the one clean uniform nesting signal is a single <ab> tag
    # carrying two markers (MW "Desid. Caus." = causative-of-desiderative). Deeper true
    # nesting (a preverb-verb with its own Caus.) needs per-dict structural parsing.
    if multi_marker:
        max_depth = 2
    elif n_markers:
        max_depth = 1
    else:
        max_depth = 0

    verbal = bool(_CL.search(body) or _INFO_VERB.search(body)
                  or any(per_cat[c] for c in ("caus", "pass", "desid", "intens", "periphr")))

    return {
        "is_verbal": int(verbal),
        "n_subentries": n_markers,
        "subentry_categories": ",".join(c for c in CATEGORIES if per_cat[c]),
        **{f"n_{c}": per_cat[c] for c in CATEGORIES},
        "n_dash_segments": len(_DASH_SEG.findall(body)),   # EXPERIMENTAL structural proxy
        "max_depth": max_depth,
        "total_chars_subentries": total_chars,
    }


def discover_dicts():
    """Every <code>/<code>.txt under csl-orig (same rule as parse_cslorig --all)."""
    return sorted(os.path.basename(os.path.dirname(p))
                  for p in glob.glob(os.path.join(CSL_ORIG, "*", "*.txt"))
                  if os.path.basename(p)[:-4] == os.path.basename(os.path.dirname(p)))


def src_path(code):
    return os.path.join(CSL_ORIG, code, f"{code}.txt")


CSV_FIELDS = (["dict", "L", "k1", "is_verbal", "n_subentries", "subentry_categories"]
              + [f"n_{c}" for c in CATEGORIES]
              + ["n_dash_segments", "max_depth", "total_chars_subentries"])


def probe(lemma, codes):
    """Print the per-dict subentry breakdown for one headword (ground-truth check)."""
    print(f"\n--probe {lemma}: per-dict subentry breakdown\n" + "-" * 64)
    for code in codes:
        path = src_path(code)
        if not os.path.exists(path):
            continue
        for e in iter_entries(path):
            if e["k1"] != lemma:
                continue
            a = analyze_entry(e["body"])
            if a["n_subentries"] == 0 and not a["is_verbal"]:
                continue
            cats = a["subentry_categories"] or "-"
            print(f"  {code.upper():6s} L{e['L']:<8s} h={e['h'] or '-':3s} "
                  f"verbal={a['is_verbal']} n_sub={a['n_subentries']:<3d} depth={a['max_depth']:<2d} "
                  f"chars={a['total_chars_subentries']:<6d} [{cats}]")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    letter = None
    if "--sample" in args:
        i = args.index("--sample")
        letter = args[i + 1]
    if "--dicts" in args:
        i = args.index("--dicts")
        codes = [a for a in args[i + 1:] if not a.startswith("--")]
    else:
        codes = discover_dicts()

    if "--probe" in args:
        i = args.index("--probe")
        probe(args[i + 1], codes)
        return

    if "--sample" not in args and "--all" not in args:
        print("Specify --sample <letter>, --all, or --probe <lemma>.", file=sys.stderr)
        return

    infix = f".{letter}" if letter else ""
    os.makedirs(OUT_DIR, exist_ok=True)
    print("=" * 64)
    print(f"M1 — subentry inventory  ({'sample ' + letter if letter else 'ALL entries'}; "
          f"{len(codes)} dicts)")
    print("=" * 64)

    by_dict = {}
    csv_path = os.path.join(OUT_DIR, f"microstructure_subentries{infix}.csv")
    n_rows = 0
    with open(csv_path, "w", encoding="utf-8", newline="") as fcsv:
        w = csv.DictWriter(fcsv, fieldnames=CSV_FIELDS)
        w.writeheader()
        for code in codes:
            path = src_path(code)
            if not os.path.exists(path):
                print(f"  {code:8s} SOURCE MISSING", file=sys.stderr)
                continue
            agg = {"entries_scanned": 0, "verbal_entries": 0, "entries_with_subentries": 0,
                   "subentry_markers_total": 0, "by_category": collections.Counter(),
                   "max_depth_max": 0, "total_chars_subentries_sum": 0,
                   "div_type_codes": collections.Counter()}
            for e in iter_entries(path):
                k1 = e["k1"] or ""
                if letter and not k1.startswith(letter):
                    continue
                a = analyze_entry(e["body"])
                agg["div_type_codes"].update(_DIV_N.findall(e["body"]))  # lead for preverb/verb-phrase subentries (v2)
                agg["entries_scanned"] += 1
                agg["verbal_entries"] += a["is_verbal"]
                agg["subentry_markers_total"] += a["n_subentries"]
                agg["max_depth_max"] = max(agg["max_depth_max"], a["max_depth"])
                agg["total_chars_subentries_sum"] += a["total_chars_subentries"]
                for c in CATEGORIES:
                    agg["by_category"][c] += a[f"n_{c}"]
                if a["n_subentries"] > 0:
                    agg["entries_with_subentries"] += 1
                    w.writerow({"dict": code, "L": e["L"], "k1": k1, **a})
                    n_rows += 1
            agg["by_category"] = dict(agg["by_category"])
            agg["div_type_codes"] = dict(agg["div_type_codes"].most_common(12))
            agg["verbal_deriv_markers"] = sum(agg["by_category"].get(c, 0) for c in VERBAL_DERIV)
            agg["verbal_deriv_per_verbal"] = round(
                agg["verbal_deriv_markers"] / agg["verbal_entries"], 3) if agg["verbal_entries"] else 0.0
            by_dict[code] = agg
            print(f"  {code:8s} scanned={agg['entries_scanned']:>7,} "
                  f"verbal={agg['verbal_entries']:>6,} with_sub={agg['entries_with_subentries']:>6,} "
                  f"markers={agg['subentry_markers_total']:>7,} "
                  f"vderiv/v={agg['verbal_deriv_per_verbal']:>5}")

    by_dict_path = os.path.join(OUT_DIR, f"microstructure_by_dict{infix}.json")
    with open(by_dict_path, "w", encoding="utf-8") as f:
        json.dump({"mode": f"sample:{letter}" if letter else "all",
                   "letter": letter, "dicts": by_dict}, f, indent=2, ensure_ascii=False)

    # leaderboard: deepest-marked entries in this run
    leaders = sorted(by_dict.items(), key=lambda kv: -kv[1]["subentry_markers_total"])[:10]
    report = {
        "mode": f"sample:{letter}" if letter else "all",
        "letter": letter,
        "n_dicts": len([c for c in codes if os.path.exists(src_path(c))]),
        "csv_rows_emitted": n_rows,
        "categories": CATEGORIES,
        "marker_tokens": CAT_TOKENS,
        "row_threshold": "per-entry rows emitted only where n_subentries > 0; zeros live in the aggregate",
        "top_dicts_by_markers": [{"dict": c, **{k: v for k, v in a.items() if k != "by_category"},
                                  "by_category": a["by_category"]} for c, a in leaders],
        "caveats": ("Case-insensitive <ab> matching (PWG lowercases what MW capitalises). "
                    "n_subentries=0 means 'no <ab> secondary-conjugation marker in this dict's "
                    "convention', NOT a flat entry (cf. CITATION_TAGGING.md): SKD/VCP and "
                    "specialised name/plant dicts read near-0 by design. Comparable WITHIN a dict. "
                    "max_depth is a proxy (div-nesting where present, else multi-marker/binary). "
                    "n_dash_segments is an EXPERIMENTAL PWG-family structural proxy, NOT in "
                    "n_subentries. Preverb/participle/idiom subentries deferred to per-dict parsing."),
    }
    report_path = os.path.join(OUT_DIR, f"m1_report{infix}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {csv_path} ({n_rows:,} rows), "
          f"{os.path.basename(by_dict_path)}, {os.path.basename(report_path)}")
    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source(csv_path, "m1_subentries.py", 6)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
