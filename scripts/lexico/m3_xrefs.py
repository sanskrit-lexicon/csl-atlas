"""Phase L0.6 / M3 — cross-reference subentries (cat 24): the internal link graph.

Cross-references ("see / cf. / vergleiche X") are microstructure dimension 24 and a
lineage signal (LEXICOGRAPHY_ROADMAP §3.1, "shared cross-reference patterns"). The
two traditions encode them differently, both with an SLP1 target so they are
directly comparable:

  - German/Petersburg (PWG): `<div n="v">— <ab>Vgl.</ab> {#target#}`
  - English MW:               `<ab>cf.</ab> [also] [√] <s>target</s>`
  - Apte (AP/AP90):           `<ab>cf.</ab> {#target#}`  — SLP1 in {#…#}, NOT <s>

We emit a directed edge (source headword -> referenced lemma) per cross-reference.
`cf.` followed by `<lang>` (a Western cognate) or `<hom>` (a homonym pointer) is
skipped — only Sanskrit-lemma targets are captured. The Apte `cf. {#…#}` slot is
ambiguous (lemma pointers, multi-word quotes, glued fragments); the round-7 rule keeps
a {#…#} as an EDGE only if lemma-like (no space/period, each /,-split atom a SLP1 word
≤24 chars) and routes everything else to the cf-quote side file. BEN's cf. is purely
cognate/citation → 0 lemma edges. PW/MW72/WIL/indigenous use none (convention gap, per
the m1 "0 != structureless" rule). Targets are RAW SLP1; the cross-dict join (hwnorm1-
style) is done downstream by m6.

Reads csl-orig bodies via parse_cslorig. Run from repo root:
    python scripts/lexico/m3_xrefs.py --probe gam        # MW gam cf. -> kzam; PWG gam Vgl. targets
    python scripts/lexico/m3_xrefs.py --all
Outputs (data/lexico/; sample runs get a `.<letter>` infix):
    xref_edges[.<letter>].csv      one row per (dict, source_L, source_k1, kind, target)
    xref_cf_quotes[.<letter>].csv  AP/AP90 multi-word {#…#} after cf. (sub-citations, not edges)
    xref_by_dict[.<letter>].json   per-dict density + in-degree leaderboard (hub lemmas)
    m3_report[.<letter>].json      run metadata + corpus-wide most-referenced targets
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

_VGL = re.compile(r'<div n="v">[^{<]*<ab>[vV]gl\.?</ab>\s*\{#([^#}]*)#\}')
_CF = re.compile(r'<ab>[cC]f\.?</ab>\s*(?:also\s+|and\s+|or\s+)?(?:√\s*)?<s>([^<]*)</s>')
_SPLIT = re.compile(r",| und | and | oder | or ")  # a single Vgl./cf. may list several targets
# AP/AP90 put the cf. target in {#…#} (SLP1), not <s> — a mix of clean lemma pointers,
# multi-word quotes, cognates and citations (BEN's cf. is purely cognate/citation → 0 lemmas).
# Disambiguation (decision round 7): a {#…#} after cf. yields cross-ref EDGES only if it is
# lemma-like — no space/period and each /,-split atom a single SLP1 word ≤ 24 chars; anything
# else (phrases, glued quote-fragments) goes to the cf-quote SIDE FILE, not the graph.
_CF_BRACE = re.compile(r'<ab>[cC]f\.?</ab>\s*(?:also\s+|and\s+|or\s+)?(?:√\s*)?\{#([^#}]*)#\}')
_BRACE_SPLIT = re.compile(r"/|,")
_LEMMA_TOK = re.compile(r"^[A-Za-z][A-Za-z'~]*$")
_LEMMA_MAX = 24


def analyze_entry(body):
    """Return (edges, quotes): atomic (kind, target) cross-reference edges, plus cf-quote
    strings (multi-word {#…#} after cf. that are sub-citations, not lemma pointers).

    A capture span may group several lemmas (Vgl. {#a, b, c#} / cf. <s>x</s> and <s>y</s>);
    each is split into its own directed edge. AP/AP90 cf-{#…#} are sorted lemma→edge,
    phrase→quote by the round-7 rule.
    """
    edges = []
    for kind, rx in (("vgl", _VGL), ("cf", _CF)):
        for cap in rx.findall(body):
            for t in _SPLIT.split(cap):
                t = t.strip()
                if t:
                    edges.append((kind, t))
    quotes = []
    for cap in _CF_BRACE.findall(body):
        cap = cap.strip()
        if not cap:
            continue
        if " " in cap or "." in cap:                 # a multi-word quote / sentence
            quotes.append(cap)
            continue
        toks = [t.strip() for t in _BRACE_SPLIT.split(cap) if t.strip()]
        if toks and all(_LEMMA_TOK.match(t) and len(t) <= _LEMMA_MAX for t in toks):
            edges.extend(("cf", t) for t in toks)    # clean lemma pointer(s)
        else:
            quotes.append(cap)                       # glued / non-lemma → side file
    return edges, quotes


def discover_dicts():
    return sorted(os.path.basename(os.path.dirname(p))
                  for p in glob.glob(os.path.join(CSL_ORIG, "*", "*.txt"))
                  if os.path.basename(p)[:-4] == os.path.basename(os.path.dirname(p)))


def src_path(code):
    return os.path.join(CSL_ORIG, code, f"{code}.txt")


def probe(lemma, codes):
    print(f"\n--probe {lemma}: cross-references per dict\n" + "-" * 64)
    for code in codes:
        path = src_path(code)
        if not os.path.exists(path):
            continue
        for e in iter_entries(path):
            if e["k1"] != lemma:
                continue
            edges, quotes = analyze_entry(e["body"])
            if not edges and not quotes:
                continue
            shown = ", ".join(f"{k}:{t}" for k, t in edges[:12])
            qn = f" +{len(quotes)} cf-quote(s)" if quotes else ""
            print(f"  {code.upper():6s} L{e['L']:<8s} h={e['h'] or '-':3s} n_xref={len(edges):<3d} [{shown}]{qn}")


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
    print(f"M3 — cross-reference edges  ({'sample ' + letter if letter else 'ALL entries'}; "
          f"{len(codes)} dicts)")
    print("=" * 64)

    by_dict = {}
    corpus_targets = collections.Counter()
    quote_rows = []
    quotes_by = collections.Counter()
    csv_path = os.path.join(OUT_DIR, f"xref_edges{infix}.csv")
    n_rows = 0
    with open(csv_path, "w", encoding="utf-8", newline="") as fcsv:
        w = csv.DictWriter(fcsv, fieldnames=["dict", "L", "k1", "kind", "target"])
        w.writeheader()
        for code in codes:
            path = src_path(code)
            if not os.path.exists(path):
                continue
            tgt = collections.Counter()
            kind = collections.Counter()
            n_entries = n_with = n_edges = n_q = 0
            for e in iter_entries(path):
                k1 = e["k1"] or ""
                if letter and not k1.startswith(letter):
                    continue
                n_entries += 1
                edges, quotes = analyze_entry(e["body"])
                for q in quotes:
                    quote_rows.append({"dict": code, "L": e["L"], "k1": k1, "quote": q})
                    n_q += 1
                if not edges:
                    continue
                n_with += 1
                for k, t in edges:
                    w.writerow({"dict": code, "L": e["L"], "k1": k1, "kind": k, "target": t})
                    tgt[t] += 1
                    kind[k] += 1
                    n_edges += 1
                    n_rows += 1
            quotes_by[code] = n_q
            if n_edges:
                corpus_targets.update(tgt)
                by_dict[code] = {
                    "entries_scanned": n_entries,
                    "entries_with_xref": n_with,
                    "xref_edges": n_edges,
                    "by_kind": dict(kind),
                    "distinct_targets": len(tgt),
                    "cf_quotes": n_q,
                    "top_referenced_targets": dict(tgt.most_common(20)),
                }
                print(f"  {code:8s} scanned={n_entries:>7,} with_xref={n_with:>6,} "
                      f"edges={n_edges:>7,} ({'/'.join(f'{k}:{v:,}' for k, v in kind.items())}) "
                      f"distinct_targets={len(tgt):>6,} cf_quotes={n_q:>4,}")

    quotes_path = os.path.join(OUT_DIR, f"xref_cf_quotes{infix}.csv")
    with open(quotes_path, "w", encoding="utf-8", newline="") as fq:
        wq = csv.DictWriter(fq, fieldnames=["dict", "L", "k1", "quote"])
        wq.writeheader()
        wq.writerows(quote_rows)

    by_dict_path = os.path.join(OUT_DIR, f"xref_by_dict{infix}.json")
    with open(by_dict_path, "w", encoding="utf-8") as f:
        json.dump({"mode": f"sample:{letter}" if letter else "all", "dicts": by_dict},
                  f, indent=2, ensure_ascii=False)

    report = {
        "mode": f"sample:{letter}" if letter else "all",
        "letter": letter,
        "csv_rows_emitted": n_rows,
        "dicts_with_xref": list(by_dict.keys()),
        "cf_quotes_total": len(quote_rows),
        "cf_quotes_by_dict": {c: n for c, n in quotes_by.most_common() if n},
        "corpus_most_referenced_targets": dict(corpus_targets.most_common(40)),
        "caveats": ("Three lemma-edge formats, all SLP1: PWG <div n=v> Vgl. {#t#}; English MW "
                    "<ab>cf.</ab> <s>t</s>; AP/AP90 <ab>cf.</ab> {#t#} (round 7: lemma-like {#…#} → edge, "
                    "multi-word/glued {#…#} → cf-quote side file xref_cf_quotes.csv). cf.+<lang> cognate / "
                    "+<hom> homonym skipped; BEN cf. is purely cognate/citation → 0 lemma edges. "
                    "PW/MW72/WIL/indigenous use none (convention gap, not absence). Targets RAW SLP1; "
                    "cross-dict join (hwnorm1-style) is done downstream by m6."),
    }
    report_path = os.path.join(OUT_DIR, f"m3_report{infix}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nCorpus-wide most-referenced targets (hub lemmas): "
          f"{', '.join(f'{t}({n})' for t, n in corpus_targets.most_common(10))}")
    print(f"cf-quotes (AP/AP90 multi-word {{#…#}} after cf.): {len(quote_rows):,} "
          f"({', '.join(f'{c}:{n}' for c, n in quotes_by.most_common(4) if n)})")
    print(f"Wrote {csv_path} ({n_rows:,} rows), {os.path.basename(quotes_path)} "
          f"({len(quote_rows):,} cf-quotes), {os.path.basename(by_dict_path)}, {os.path.basename(report_path)}")
    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source(csv_path, "m3_xrefs.py", 6)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
