"""Phase L0.6 / M4 (PROTOTYPE) — indigenous verbal microstructure (SKD/VCP).

The counterpart to m1. m1 counts the European <ab> apparatus and is structurally
blind to SKD/VCP, which carry ZERO <ab>/<div>/<s> markup (see MICROSTRUCTURE_ZERO_MEANING.md)
yet hold thousands of verbal roots, marked the INDIGENOUS way — in romanized-Sanskrit
prose, dhātupāṭha-style. This prototype recovers that layer.

ROOT DETECTION (high-confidence signal): an entry is a verbal-root entry if its body
cites a dhātupāṭha / dhātu-commentary. The Kavikalpadruma (Vopadeva's verb-list) is
purely a root list, so `iti kavikalpadrumaH` (SKD, 2,135x) ⟹ root entry; likewise
Durgādāsa's commentary, the Mādhavīya-dhātuvṛtti (VCP), and generic `iti …dhātu…`.

FEATURES inside a root entry (the clean, low-ambiguity indigenous markers):
  - causative   `preraRe` (preraṇe, "in the sense of impelling") / `Rijanta` / `RyantaH`
  - seṭ / aniṭ  `sew` / `aniw`  (whether the root takes the iṭ augment)
  - class-1     `BvAdi` (bhvādi) — the ONE gaṇa name safe to string-match; adādi/svādi/…
                collide with the ubiquitous `-ādi` ("etc.") compound suffix, so are skipped.
  - gloss       the raw snippet between `¦` and the dhātupāṭha citation (the locative
                meaning + it-markers); kept verbatim, not parsed.

PROTOTYPE limitations (documented, not hidden): VCP cites its dhātupāṭha source by name
far less than SKD, so VCP's root count here is a LOWER BOUND (its 1,980 `seṭ` markers
imply a much larger root layer); meaning is a raw snippet; pada/transitivity are usually
abbreviated (para/saka) and ambiguous, so omitted. This is a feasibility proof, not a
finished parser.

Reads csl-orig via parse_cslorig. Run from repo root:
    python scripts/lexico/m4_indigenous.py --probe aka
    python scripts/lexico/m4_indigenous.py --all
    python scripts/lexico/m4_indigenous.py --dicts skd vcp
Outputs (data/lexico/):
    indigenous_roots.csv       per root entry: dict, L, k1, source, causative, set, anit, bhvadi, gloss
    indigenous_by_dict.json    per-dict root counts + feature tallies + m1-blindness comparison
    m4_report.json
"""

import os
import re
import sys
import csv
import glob
import json

sys.path.insert(0, os.path.abspath("scripts/forensic"))
from parse_cslorig import iter_entries, CSL_ORIG

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OUT_DIR = "data/lexico"

_DHATU_SRC = re.compile(r"kavikalpadrum|durgAdAs|mAdhavIya|iti\s+\S*DAtu")
_CAUS = re.compile(r"preraRe|Rijanta|RyantaH")
_SET = re.compile(r"(?<![A-Za-z])sew(?![A-Za-z])")
_ANIT = re.compile(r"(?<![A-Za-z])aniw(?![A-Za-z])")
_BHVADI = re.compile(r"(?<![A-Za-z])BvAdi")


def analyze_entry(body):
    """Return root-entry features, or None if the entry isn't a dhātupāṭha-cited root."""
    if not _DHATU_SRC.search(body):
        return None
    if "kavikalpadrum" in body:
        src = "kavikalpadruma"
    elif "mAdhavIya" in body:
        src = "madhaviya"
    elif "durgAdAs" in body:
        src = "durgadasa"
    else:
        src = "dhatupatha"
    snip = ""
    if "¦" in body:                       # ¦ closes the headword
        after = body.split("¦", 1)[1]
        snip = " ".join(after.split(" iti ", 1)[0].split())[:60]
    return {
        "dhatupatha_source": src,
        "causative": int(bool(_CAUS.search(body))),
        "set": int(bool(_SET.search(body))),
        "anit": int(bool(_ANIT.search(body))),
        "bhvadi": int(bool(_BHVADI.search(body))),
        "gloss_snippet": snip,
    }


def discover_dicts():
    return sorted(os.path.basename(os.path.dirname(p))
                  for p in glob.glob(os.path.join(CSL_ORIG, "*", "*.txt"))
                  if os.path.basename(p)[:-4] == os.path.basename(os.path.dirname(p)))


def src_path(code):
    return os.path.join(CSL_ORIG, code, f"{code}.txt")


def probe(lemma, codes):
    print(f"\n--probe {lemma}: indigenous root entries per dict\n" + "-" * 64)
    for code in codes:
        path = src_path(code)
        if not os.path.exists(path):
            continue
        for e in iter_entries(path):
            if e["k1"] != lemma:
                continue
            a = analyze_entry(e["body"])
            if not a:
                continue
            feats = ",".join(f for f in ("causative", "set", "anit", "bhvadi") if a[f])
            print(f"  {code.upper():5s} L{e['L']:<7s} src={a['dhatupatha_source']:<14s} "
                  f"[{feats or '-'}]  {a['gloss_snippet']!r}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    if "--dicts" in args:
        i = args.index("--dicts")
        codes = [a for a in args[i + 1:] if not a.startswith("--")]
    else:
        codes = discover_dicts()
    if "--probe" in args:
        probe(args[args.index("--probe") + 1], codes)
        return
    if "--all" not in args and "--dicts" not in args:
        print("Specify --all, --dicts <codes>, or --probe <lemma>.", file=sys.stderr)
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    print("=" * 64)
    print(f"M4 (prototype) — indigenous verbal roots  ({len(codes)} dicts)")
    print("=" * 64)

    by_dict = {}
    csv_path = os.path.join(OUT_DIR, "indigenous_roots.csv")
    fields = ["dict", "L", "k1", "dhatupatha_source", "causative", "set", "anit", "bhvadi", "gloss_snippet"]
    n_rows = 0
    with open(csv_path, "w", encoding="utf-8", newline="") as fcsv:
        w = csv.DictWriter(fcsv, fieldnames=fields)
        w.writeheader()
        for code in codes:
            path = src_path(code)
            if not os.path.exists(path):
                continue
            agg = {"entries": 0, "root_entries": 0, "causative": 0, "set": 0, "anit": 0,
                   "bhvadi": 0, "by_source": {}}
            for e in iter_entries(path):
                agg["entries"] += 1
                a = analyze_entry(e["body"])
                if not a:
                    continue
                agg["root_entries"] += 1
                for f in ("causative", "set", "anit", "bhvadi"):
                    agg[f] += a[f]
                agg["by_source"][a["dhatupatha_source"]] = agg["by_source"].get(a["dhatupatha_source"], 0) + 1
                w.writerow({"dict": code, "L": e["L"], "k1": e["k1"] or "", **a})
                n_rows += 1
            if agg["root_entries"]:
                by_dict[code] = agg
                print(f"  {code:6s} entries={agg['entries']:>7,} roots={agg['root_entries']:>6,} "
                      f"caus={agg['causative']:>5,} seṭ={agg['set']:>5,} aniṭ={agg['anit']:>4,} "
                      f"bhvādi={agg['bhvadi']:>4,}  src={agg['by_source']}")

    by_dict_path = os.path.join(OUT_DIR, "indigenous_by_dict.json")
    with open(by_dict_path, "w", encoding="utf-8") as f:
        json.dump({"dicts": by_dict}, f, indent=2, ensure_ascii=False)

    report = {
        "prototype": True,
        "csv_rows": n_rows,
        "dicts_with_roots": list(by_dict.keys()),
        "headline": {c: {"indigenous_roots_m4": a["root_entries"], "ab_markers_m1": 0}
                     for c, a in by_dict.items() if c in ("skd", "vcp")},
        "method": ("Root entry = body cites a dhātupāṭha (kavikalpadruma/durgādāsa/mādhavīya/…). "
                   "Features: preraṇe/ṇijanta=causative, sew/aniw=seṭ/aniṭ, BvAdi=class-1. The other "
                   "gaṇa names collide with the -ādi suffix and are excluded."),
        "caveats": ("PROTOTYPE. SKD cites kavikalpadruma consistently (clean ~2.1k roots); VCP cites "
                    "its source by name far less, so VCP roots here are a LOWER BOUND (cf. 1,980 seṭ "
                    "markers). The point: SKD/VCP read 0 under m1's <ab> apparatus but carry thousands "
                    "of roots — the 0 was detector blindness (MICROSTRUCTURE_ZERO_MEANING.md)."),
    }
    with open(os.path.join(OUT_DIR, "m4_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nHeadline: " + "; ".join(
        f"{c.upper()} {a['root_entries']:,} indigenous roots (m1 <ab> = 0)"
        for c, a in by_dict.items() if c in ("skd", "vcp")))
    print(f"Wrote {csv_path} ({n_rows:,} rows), {os.path.basename(by_dict_path)}, m4_report.json")
    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source(csv_path, "m4_indigenous.py", 6)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
