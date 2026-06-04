"""Phase L0.6 / M4 (PROTOTYPE) — indigenous verbal microstructure (SKD/VCP).

The counterpart to m1. m1 counts the European <ab> apparatus and is structurally
blind to SKD/VCP, which carry ZERO <ab>/<div>/<s> markup (see MICROSTRUCTURE_ZERO_MEANING.md)
yet hold thousands of verbal roots, marked the INDIGENOUS way — in romanized-Sanskrit
prose, dhātupāṭha-style. This prototype recovers that layer.

ROOT DETECTION — two complementary signals (union), recorded per row in `root_signal`:
  (1) CITATION: the entry cites a dhātupāṭha/dhātu-commentary — the Kavikalpadruma
      (`iti kavikalpadrumaH`, SKD 2,135×, a pure verb-list ⟹ root), Durgādāsa, the
      Mādhavīya-dhātuvṛtti, or generic `iti …dhātu…`. This carries SKD (cites consistently).
  (2) ANNOTATION: the dhātupāṭha grammatical annotation itself — the seṭ/aniṭ token
      (`sew`/`aniw`) WITH a pada/transitivity abbreviation (`para0`/`Atma0`/`saka0`/…).
      VCP names its source rarely but annotates its roots this way, so (2) is what recovers
      VCP (43 → ~2,230). The pada/transitivity co-requirement keeps it from firing on a stray
      SLP1 substring in a European `{#…#}` body — verified: European dicts stay ≈0.
The three indigenous/root dicts then converge on ~the dhātupāṭha's size: SKD 2,544, VCP 2,230,
KRM 1,757 (KRM is a dedicated root dictionary), plus SHS 463 (Wilson tradition).

FEATURES emitted per root entry (the dhātupāṭha annotation, as real columns):
  - gana          bhvādi…curādi — the 10 conjugation classes. VCP's `0`-marked forms
                  (`BvA0`/`BvAdi0`, `curA0`/`cu0`, `tu0`, `ju0`, …) carry the abbreviation
                  marker, which disambiguates them from the ubiquitous `-ādi` ("etc.")
                  suffix; SKD's visarga form (`curAdiH`) is also matched. (Ambiguous short
                  forms `di0`/`sO0` are held out pending maintainer review.)
  - pada          parasmaipada / ātmanepada / ubhayapada  (`para0` / `Atma0` / `uBa(ya)0`)
  - transitivity  sakarmaka / akarmaka  (`saka0` / `aka0`, plus the prose stems
                  `sakarmmak`/`akarmmak` for SKD/Durgādāsa; `aka0` is lookbehind-guarded
                  so it does not match inside `saka0`)
  - causative     `preraRe` (preraṇe) / `Rijanta` / `RyantaH`
  - seṭ / aniṭ / veṭ  `sew` / `aniw` / `vew`  (iṭ-augment behavior; veṭ = optionally seṭ,
                  a lossless refinement — `sew … vew` ⟹ set=1 AND vet=1)
  - gloss         raw snippet between `¦` and the citation (locative meaning + it-markers).

PROTOTYPE limitations (documented, not hidden): meaning is a raw snippet; the abbreviated gaṇa
forms (`adA0`, `svA0`) carry mild noise; pada/transitivity/gaṇa take the FIRST match in the entry.
SKD encodes PADA mostly via Vopadeva/Kavikalpadruma anubandhas (it-letters); a proposed decode key
exists (docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md, validated by the SKD∩VCP cross-walk) but is HELD
pending the maintainer's verification, so this script does NOT yet infer SKD pada from anubandhas —
SKD pada/trans here come only from prose. A feasibility proof, deliberately conservative.

Reads csl-orig via parse_cslorig. Run from repo root:
    python scripts/lexico/m4_indigenous.py --probe aka
    python scripts/lexico/m4_indigenous.py --all
    python scripts/lexico/m4_indigenous.py --dicts skd vcp
Outputs (data/lexico/):
    indigenous_roots.csv       per root entry: dict, L, k1, signal, source, gana, pada, transitivity,
                               causative, set, anit, vet, gloss
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

# TWO root signals (union). (1) CITATION — a dhātupāṭha source is named; consistent in SKD.
# (2) ANNOTATION — the dhātupāṭha grammatical annotation itself is present, i.e. the seṭ/aniṭ
# token (`sew`/`aniw`), which in the indigenous dicts only ever appears in the root cluster
# `…gaṇa-ādi0 pada0 transitivity0 sew .`. VCP names its source rarely but annotates ~2,277
# roots, so this is what recovers VCP's root layer. To stay root-specific (and not fire on a
# stray SLP1 substring in a European {#…#} body) the annotation requires a pada/transitivity
# abbreviation to accompany the seṭ/aniṭ.
_DHATU_SRC = re.compile(r"kavikalpadrum|durgAdAs|mAdhavIya|iti\s+\S*DAtu")
_ANNOT = re.compile(r"(?<![A-Za-z])(sew|aniw)(?![A-Za-z])")
_PADA_TRANS = re.compile(r"(?<![A-Za-z])(para|Atmane?|uBaya?|saka|akarmma|sakarmma|aka)0?(?![A-Za-z])")
_CAUS = re.compile(r"preraRe|Rijanta|RyantaH")
_SET = re.compile(r"(?<![A-Za-z])sew(?![A-Za-z])")
_ANIT = re.compile(r"(?<![A-Za-z])aniw(?![A-Za-z])")
# veṭ (optionally seṭ) — VCP marks it explicitly as `vew` (98 entries), often as
# `sew … ktvA vew` (generally seṭ, veṭ before ktvā). Per decision round 2 #7 this gets
# its OWN column: `sew … vew` ⟹ set=1 AND vet=1 (a lossless refinement, not an override).
# SKD marks veṭ via the `U`/ūdit anubandha, but that decode is HELD pending the maintainer's
# Kavikalpadruma check (MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md), so SKD `vet` stays 0 for now.
_VET = re.compile(r"(?<![A-Za-z])vew(?![A-Za-z])")

# Feature tables: (canonical label, regex). VCP marks each with a trailing `0` abbreviation
# (`para0`, `saka0`, `BvA0`/`BvAdi0`) — the `0` disambiguates the gaṇa names from the ubiquitous
# `-ādi` suffix; SKD states them with a visarga (`curAdiH`) or via anubandhas (not decoded here).
# Boundaries matter: `aka0` (akarmaka) is a substring of `saka0` (sakarmaka), so it is lookbehind-
# guarded. `_first` returns the first label whose pattern hits (ubhaya before para/ātma; gaṇa 1→10).
# Surface forms (verified against VCP): ubhaya `uBa0`/`uBaya0`; parasmaipada `para0`/`pa0`;
# ātmanepada `Atma0` (NOT `Atman0`). Check ubhaya first (it subsumes the others).
_PADA = (
    ("ubhayapada",   re.compile(r"(?<![A-Za-z])(?:uBa(?:ya)?0|uBayapad)")),
    ("parasmaipada", re.compile(r"(?<![A-Za-z])(?:para0|pa0|parasmEpad)")),
    ("atmanepada",   re.compile(r"(?<![A-Za-z])(?:Atma0|Atmanepad)")),
)
# Transitivity. VCP uses the `saka0`/`aka0` abbreviations; SKD/Durgādāsa state it in
# PROSE — and in sandhi (`akarmmako'yaM`, `sakarmmakaH`), so we match the STEM
# `sakarmmak`/`akarmmak` (not the full `…ka`) to catch -ka/-ko/-kaH (decision round 3 #10).
# `aka0`/`akarmmak` stay lookbehind-guarded so they never fire inside `saka0`/`sakarmmak`.
_TRANS = (
    ("sakarmaka", re.compile(r"(?<![A-Za-z])(?:saka0|sakarmmak|sakarmak)")),
    ("akarmaka",  re.compile(r"(?<![A-Za-z])(?:aka0|akarmmak|akarmak)")),
)
# Per gaṇa, the explicit surface forms. The base `{stem}A(?:di)?0|{stem}AdiH` is kept;
# VCP also uses ultra-short forms (`cu0`/`tu0`/`ju0`) that the base misses — added here
# (decision round 2). They are collision-safe. DELIBERATELY EXCLUDED pending maintainer
# review (round 4): `di0` (collides with the `-Adi0` suffix inside BvAdi0/curAdi0/…) and
# `sO0` (unclear expansion — svādi? sautra?). `ada0` (lowercase) is likewise left out.
_GANA = tuple(
    (label, re.compile(rf"(?<![A-Za-z])(?:{'|'.join(forms)})"))
    for label, forms in (
        ("bhvadi",    (r"BvA(?:di)?0", r"BvAdiH")),
        ("adadi",     (r"adA(?:di)?0", r"adAdiH")),
        ("juhotyadi", (r"juhotyA(?:di)?0", r"juhotyAdiH", r"ju0")),
        ("divadi",    (r"divA(?:di)?0", r"divAdiH")),
        ("svadi",     (r"svA(?:di)?0", r"svAdiH")),
        ("tudadi",    (r"tudA(?:di)?0", r"tudAdiH", r"tu0")),
        ("rudhadi",   (r"ruDA(?:di)?0", r"ruDAdiH")),
        ("tanadi",    (r"tanA(?:di)?0", r"tanAdiH")),
        ("kryadi",    (r"kryA(?:di)?0", r"kryAdiH")),
        ("curadi",    (r"curA(?:di)?0", r"curAdiH", r"cu0")),
    )
)
GANA_LABELS = {g for g, _ in _GANA}
PADA_LABELS = {p for p, _ in _PADA}
TRANS_LABELS = {t for t, _ in _TRANS}


def _first(body, table):
    """First canonical label in `table` whose pattern matches `body`, else ''."""
    for label, rx in table:
        if rx.search(body):
            return label
    return ""


def analyze_entry(body):
    """Return root-entry features, or None if the entry is not a verbal root."""
    cite = bool(_DHATU_SRC.search(body))
    annot = bool(_ANNOT.search(body)) and bool(_PADA_TRANS.search(body))
    if not (cite or annot):
        return None
    if "kavikalpadrum" in body:
        src = "kavikalpadruma"
    elif "mAdhavIya" in body:
        src = "madhaviya"
    elif "durgAdAs" in body:
        src = "durgadasa"
    elif cite:
        src = "dhatupatha"
    else:
        src = "(annotation-only)"
    signal = "both" if (cite and annot) else ("citation" if cite else "annotation")
    snip = ""
    if "¦" in body:                       # ¦ closes the headword
        after = body.split("¦", 1)[1]
        snip = " ".join(after.split(" iti ", 1)[0].split())[:60].strip()
    return {
        "root_signal": signal,
        "dhatupatha_source": src,
        "gana": _first(body, _GANA),
        "pada": _first(body, _PADA),
        "transitivity": _first(body, _TRANS),
        "causative": int(bool(_CAUS.search(body))),
        "set": int(bool(_SET.search(body))),
        "anit": int(bool(_ANIT.search(body))),
        "vet": int(bool(_VET.search(body))),
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
            tags = [a["gana"], a["pada"], a["transitivity"]] + [f for f in ("causative", "set", "anit") if a[f]]
            tags = ", ".join(t for t in tags if t)
            print(f"  {code.upper():5s} L{e['L']:<7s} sig={a['root_signal']:<10s} [{tags or '-'}]  {a['gloss_snippet']!r}")


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
    fields = ["dict", "L", "k1", "root_signal", "dhatupatha_source",
              "gana", "pada", "transitivity", "causative", "set", "anit", "vet", "gloss_snippet"]
    n_rows = 0
    with open(csv_path, "w", encoding="utf-8", newline="") as fcsv:
        w = csv.DictWriter(fcsv, fieldnames=fields)
        w.writeheader()
        for code in codes:
            path = src_path(code)
            if not os.path.exists(path):
                continue
            agg = {"entries": 0, "root_entries": 0, "causative": 0, "set": 0, "anit": 0, "vet": 0,
                   "by_source": {}, "by_signal": {}, "by_gana": {}, "by_pada": {}, "by_transitivity": {}}
            for e in iter_entries(path):
                agg["entries"] += 1
                a = analyze_entry(e["body"])
                if not a:
                    continue
                agg["root_entries"] += 1
                for f in ("causative", "set", "anit", "vet"):
                    agg[f] += a[f]
                agg["by_source"][a["dhatupatha_source"]] = agg["by_source"].get(a["dhatupatha_source"], 0) + 1
                agg["by_signal"][a["root_signal"]] = agg["by_signal"].get(a["root_signal"], 0) + 1
                for col in ("gana", "pada", "transitivity"):
                    if a[col]:
                        agg["by_" + col][a[col]] = agg["by_" + col].get(a[col], 0) + 1
                w.writerow({"dict": code, "L": e["L"], "k1": e["k1"] or "", **a})
                n_rows += 1
            if agg["root_entries"]:
                by_dict[code] = agg
                tg = max(agg["by_gana"], key=agg["by_gana"].get) if agg["by_gana"] else "-"
                print(f"  {code:6s} roots={agg['root_entries']:>6,} caus={agg['causative']:>4,} "
                      f"seṭ={agg['set']:>5,} aniṭ={agg['anit']:>4,} veṭ={agg['vet']:>4,} "
                      f"pada={sum(agg['by_pada'].values()):>5,} trans={sum(agg['by_transitivity'].values()):>5,} "
                      f"gaṇa={sum(agg['by_gana'].values()):>5,}(top {tg})")

    by_dict_path = os.path.join(OUT_DIR, "indigenous_by_dict.json")
    with open(by_dict_path, "w", encoding="utf-8") as f:
        json.dump({"dicts": by_dict}, f, indent=2, ensure_ascii=False)

    report = {
        "prototype": True,
        "csv_rows": n_rows,
        "dicts_with_roots": list(by_dict.keys()),
        "headline": {c: {"indigenous_roots_m4": a["root_entries"], "ab_markers_m1": 0}
                     for c, a in by_dict.items() if c in ("skd", "vcp")},
        "method": ("Root = (1) dhātupāṭha citation OR (2) the seṭ/aniṭ + pada/transitivity annotation "
                   "(recorded in root_signal). Emitted columns: gaṇa (bhvādi…curādi, via VCP's 0-marked "
                   "forms BvA0/curA0/…), pada (parasmaipada/ātmanepada/ubhayapada), transitivity "
                   "(sakarmaka/akarmaka), causative (preraṇe/ṇijanta), seṭ/aniṭ."),
        "caveats": ("PROTOTYPE. SKD/VCP read 0 under m1's <ab> apparatus but carry ~2k roots each — the "
                    "0 was detector blindness (MICROSTRUCTURE_ZERO_MEANING.md). SKD encodes PADA via "
                    "Vopadeva/Kavikalpadruma anubandhas; a cross-walk-validated decode key exists "
                    "(MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md) but is HELD pending maintainer verification, so "
                    "SKD pada/trans here are prose-only and lower than VCP's. gaṇa/pada/transitivity take "
                    "the first match; abbreviated gaṇa forms (adA0/svA0) carry mild noise; veṭ (vew) now "
                    "split into its own column. Sanity-checked: VCP pada parasmaipada>ubhaya>ātmane and "
                    "gaṇa bhvādi≫rest are linguistically correct."),
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
