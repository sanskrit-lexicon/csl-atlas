"""Phase L0.6 / M2 — preverb (upasarga) subentries: the PWG signature.

m1 measures the secondary-conjugation subentries that the European dicts tag with
<ab>…</ab>. It is BLIND to preverb subentries (cats 7-10 of MICROSTRUCTURE §2.2 —
anu-/abhi-/ati-/vi-/sam-… + verb), which the Petersburg dicts encode structurally,
NOT with <ab>, as a `<div n="p">` block:

    <div n="p">— {#vi#} {%theilen, brechen…%}: {#SaktiM vyaMsitAM…#}
    <div n="p">— {#sam#} {%durchgehen, durchwandern%}: …

i.e. an em-dash, the preverb in SLP1 {#…#}, then a gloss. This is the dash-preverb
convention named in MICROSTRUCTURE §2.2. Discovered via m1's div-type tally:
`<div n="p">` is used by PWG (~9.2k), PW (~8.4k), WIL (~700); MW does NOT use it
(MW lists preverb-verbs as separate headwords — the macrostructure/microstructure
trade-off of MICROSTRUCTURE §3.2), so MW reads 0 here BY DESIGN, not structurelessly.
NB the sibling `<div n="v">` is Vgl./cross-reference (cat 24), `<div n="1/2/3">` and
MW `<div n="to"/>` are sense blocks — none are preverb subentries.

Output rows JOIN to m1 on (dict, L). Reads csl-orig bodies via parse_cslorig.
Run from repo root:
    python scripts/lexico/m2_preverbs.py --probe gam
    python scripts/lexico/m2_preverbs.py --all
    python scripts/lexico/m2_preverbs.py --sample k --dicts pwg pw wil
Outputs (data/lexico/; sample runs get a `.<letter>` infix):
    preverb_subentries[.<letter>].csv     per-entry rows with >=1 preverb subentry
    preverb_by_dict[.<letter>].json       per-dict totals + preverb-frequency profile
    m2_report[.<letter>].json             run metadata + corpus-wide preverb ranking
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

# <div n="p"> opens a preverb block; the preverb is the first {#…#} after the em-dash.
# Tolerates self-closing (MW-style "/>") though MW does not actually use n="p".
_PREVERB = re.compile(r'<div n="p"\s*/?>[^{]*\{#([^#}]*)#\}')


def analyze_entry(body):
    """List the preverbs of each <div n='p'> subentry in one entry body (SLP1)."""
    return [pv.strip() for pv in _PREVERB.findall(body) if pv.strip()]


def discover_dicts():
    return sorted(os.path.basename(os.path.dirname(p))
                  for p in glob.glob(os.path.join(CSL_ORIG, "*", "*.txt"))
                  if os.path.basename(p)[:-4] == os.path.basename(os.path.dirname(p)))


def src_path(code):
    return os.path.join(CSL_ORIG, code, f"{code}.txt")


def probe(lemma, codes):
    print(f"\n--probe {lemma}: preverb subentries per dict\n" + "-" * 64)
    for code in codes:
        path = src_path(code)
        if not os.path.exists(path):
            continue
        for e in iter_entries(path):
            if e["k1"] != lemma:
                continue
            pvs = analyze_entry(e["body"])
            if not pvs:
                continue
            uniq = ", ".join(dict.fromkeys(pvs))   # preserve order, dedupe
            print(f"  {code.upper():6s} L{e['L']:<8s} h={e['h'] or '-':3s} "
                  f"n_preverb={len(pvs):<3d} [{uniq}]")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    letter = None
    if "--sample" in args:
        letter = args[args.index("--sample") + 1]
    if "--dicts" in args:
        i = args.index("--dicts")
        codes = [a for a in args[i + 1:] if not a.startswith("--")]
    else:
        codes = discover_dicts()

    if "--probe" in args:
        probe(args[args.index("--probe") + 1], codes)
        return
    if "--sample" not in args and "--all" not in args:
        print("Specify --sample <letter>, --all, or --probe <lemma>.", file=sys.stderr)
        return

    infix = f".{letter}" if letter else ""
    os.makedirs(OUT_DIR, exist_ok=True)
    print("=" * 64)
    print(f"M2 — preverb subentries  ({'sample ' + letter if letter else 'ALL entries'}; "
          f"{len(codes)} dicts)")
    print("=" * 64)

    by_dict = {}
    corpus_pv = collections.Counter()
    csv_path = os.path.join(OUT_DIR, f"preverb_subentries{infix}.csv")
    n_rows = 0
    with open(csv_path, "w", encoding="utf-8", newline="") as fcsv:
        w = csv.DictWriter(fcsv, fieldnames=["dict", "L", "k1", "n_preverb_sub", "preverbs"])
        w.writeheader()
        for code in codes:
            path = src_path(code)
            if not os.path.exists(path):
                continue
            freq = collections.Counter()
            n_entries = n_with = 0
            for e in iter_entries(path):
                k1 = e["k1"] or ""
                if letter and not k1.startswith(letter):
                    continue
                n_entries += 1
                pvs = analyze_entry(e["body"])
                if not pvs:
                    continue
                n_with += 1
                freq.update(pvs)
                w.writerow({"dict": code, "L": e["L"], "k1": k1,
                            "n_preverb_sub": len(pvs), "preverbs": "|".join(pvs)})
                n_rows += 1
            total = sum(freq.values())
            corpus_pv.update(freq)
            by_dict[code] = {
                "entries_scanned": n_entries,
                "entries_with_preverb_sub": n_with,
                "preverb_subentries_total": total,
                "distinct_preverbs": len(freq),
                "top_preverbs": dict(freq.most_common(25)),
            }
            if total:
                print(f"  {code:8s} scanned={n_entries:>7,} with_preverb={n_with:>6,} "
                      f"preverb_sub={total:>7,} distinct={len(freq):>4,} "
                      f"top={', '.join(k for k, _ in freq.most_common(5))}")

    by_dict_path = os.path.join(OUT_DIR, f"preverb_by_dict{infix}.json")
    with open(by_dict_path, "w", encoding="utf-8") as f:
        json.dump({"mode": f"sample:{letter}" if letter else "all", "dicts": by_dict},
                  f, indent=2, ensure_ascii=False)

    report = {
        "mode": f"sample:{letter}" if letter else "all",
        "letter": letter,
        "csv_rows_emitted": n_rows,
        "dicts_using_preverb_div": [c for c, a in by_dict.items() if a["preverb_subentries_total"]],
        "corpus_preverb_ranking": dict(corpus_pv.most_common(40)),
        "join": "rows join to microstructure_subentries.csv on (dict, L)",
        "caveats": ("Preverb subentries are the <div n='p'> dash convention (PWG/PW/WIL). MW = 0 "
                    "BY DESIGN: it promotes preverb-verbs to separate headwords (macro/micro "
                    "trade-off), so absence here is not structurelessness. Preverb = the first SLP1 "
                    "{#..#} token after the em-dash; compound/rare preverbs (vyapa, aBy-A, upA) "
                    "captured verbatim. Indigenous + name/plant dicts do not use this div."),
    }
    report_path = os.path.join(OUT_DIR, f"m2_report{infix}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nCorpus-wide top preverbs: "
          f"{', '.join(f'{k}({v:,})' for k, v in corpus_pv.most_common(12))}")
    print(f"Wrote {csv_path} ({n_rows:,} rows), "
          f"{os.path.basename(by_dict_path)}, {os.path.basename(report_path)}")
    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source(csv_path, "m2_preverbs.py", 6)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
