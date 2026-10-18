#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H6949 — PD quotation-level unit: parse the Poona Dictionary at the quotation,
not the {#...#} block.

Reads the external, read-only PDScan 2020 machine text (``txt/pd.txt`` inside
``pdtxt.zip``, https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/downloads/pdtxt.zip,
© 2014 The Sanskrit Library / Thomas Malten, CC BY-NC-SA 3.0) and writes a
per-entry count table.

    python scripts/pd_quotation_units.py --pd /path/to/pd.txt

Unit (full definition: reports/PD_QUOTATION_UNIT_2026-10-18.md):

  * ``{#...#}`` block — one SLP1 payload. NOT the unit. It counts the headword,
    morphemes inside an etymology, and cross-referenced forms, and one printed
    quotation is routinely split across two or more blocks at a line wrap. The
    worst entry (``anya``, L=97714) holds 3,904 blocks while carrying far fewer
    quotations.
  * quotation — a maximal run of consecutive blocks separated only by
    whitespace, immediately followed by a citation locus. This is the unit.
  * attestation — one siglum+locus, plus each further reference carried by a
    bare locus after a ``;`` in the same citation tail (Reader's Guide X.v: only
    a limited number of citations is given from a book and further references
    are added). This is the unit comparable with PWG's ``<ls>`` tag.

Block 1 of every entry is the printed headword (99.87 % literally equal to
``<k1>``/``<k2>``; the residue are OCR/variant forms such as ``agnikarzu,
agnikarzU``). It is excluded from quotation candidacy and a boundary is forced
after it.

Stdlib only; no network.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import quotation_units  # shared unit rule, H6949

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "pd")
OUT_TSV = os.path.join(OUT_DIR, "pd_quotations_by_entry.tsv")
OUT_JSON = os.path.join(OUT_DIR, "pd_quotations_summary.json")

DEFAULT_PD = os.environ.get(
    "PD_TXT",
    os.path.join(os.path.expanduser("~"), "Documents", "GitHub", "SanskritSpellCheck",
                 "external_src", "pd", "pd.txt"),
)

RE_HDR = re.compile(r"^<L>([\d.]+)<pc>([^<]*)<k1>([^<\s]*)<k2>([^<\s]*)")
RE_TAG = re.compile(r"<[^>]*>")
RE_ITAL = re.compile(r"\{%.*?%\}")
# A citation siglum: a letter-run ending in '.'. Two qualifier shapes occur and
# both belong to the siglum, not to a separate token: inside the period
# (PāñcaRā(Nā.)) and after it (VīraMi. (Saṃskāra.)).
RE_SIG = re.compile(r"(?<![\w])([^\W\d_][^\W\d_.]*)(\.|\([^)]*\))(\s*\([^)]*\))?")
# Lowercase roman numerals are locus numbers, not sigla (i. / iii(3). / vii (1).).
# Uppercase ones are left alone: M. / V. / X. are real abbreviations.
RE_ROMAN = re.compile(r"^[ivxlcdm]+$")

COLUMNS = [
    "lid", "pc", "k1", "k2", "printed_lines", "slp1_blocks",
    "quotations", "blocks_in_quotations", "headword_block",
    "siglum_loci", "continuation_loci", "attestations",
    "distinct_sigla", "chars",
]


def iter_entries(path):
    """Yield (header_line, [body lines]) per <L>…<LEND> record."""
    cur = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("<L>"):
                if cur is not None:
                    yield cur[0], cur[1]
                cur = [line, []]
            elif cur is not None:
                if line.startswith("<LEND>"):
                    yield cur[0], cur[1]
                    cur = None
                else:
                    cur[1].append(line)
    if cur is not None:
        yield cur[0], cur[1]


def is_siglum(tok):
    """True unless the token is a lowercase roman numeral locus number."""
    t = tok.rstrip(".")
    t = re.sub(r"\([^)]*\)$", "", t).strip()
    if not t:
        return False
    return not (t.islower() and RE_ROMAN.match(t))


def sigla_in(seg):
    """Every citation siglum in one citation segment."""
    out = []
    for m in RE_SIG.finditer(seg):
        name, sep = m.group(1), m.group(2)
        # a siglum ends in a period, either bare (ManuSm.) or inside its
        # qualifier (PāñcaRā(Nā.)); a bare (3) is a locus parenthetical
        if sep != "." and not sep.endswith(".)"):
            continue
        tok = name + sep
        if is_siglum(tok):
            out.append(tok)
    return out


def citation_tail(tail):
    """Return (siglum_loci, continuation_loci, sigla) for one citation tail."""
    # a sense marker ends the tail: what follows is the next sense, not this citation
    tail = tail.split("{@", 1)[0]
    # tags and italic glosses are not citations
    plain = RE_ITAL.sub(" ", RE_TAG.sub(" ", tail))
    segs = plain.split(";")
    sigla = []
    cont = 0
    for seg in segs:
        hits = sigla_in(seg)
        if hits:
            sigla.extend(hits)
        elif seg.strip() and re.search(r"\d", seg):
            # a further reference inheriting the preceding siglum (RG X.v)
            cont += 1
    return len(sigla), cont, sigla


def analyse(body_lines):
    """Count blocks, quotations, and attestations for one entry body."""
    body = " ".join(body_lines).replace('<div n="lb">', " ")
    u = quotation_units.count_units(body, citation_tail)
    return {
        "printed_lines": len(body_lines),
        "slp1_blocks": u["slp1_blocks"],
        "quotations": u["quotations"],
        "blocks_in_quotations": u["blocks_in_quotations"],
        "headword_block": u["headword_block"],
        "siglum_loci": u["loci"],
        "continuation_loci": u["continuation_loci"],
        "attestations": u["attestations"],
        "distinct_sigla": len(set(u["tokens"])),
        "chars": len(body),
    }


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pd", default=DEFAULT_PD, help="path to PDScan 2020 txt/pd.txt")
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--limit", type=int, default=0, help="debug: stop after N entries")
    args = ap.parse_args(argv)

    if not os.path.exists(args.pd):
        sys.exit(f"pd.txt not found: {args.pd}\n"
                 "re-stage it with SanskritSpellCheck's detectors/get_external_source.py PD, "
                 "or pass --pd")

    os.makedirs(args.out_dir, exist_ok=True)
    out_tsv = os.path.join(args.out_dir, os.path.basename(OUT_TSV))
    out_json = os.path.join(args.out_dir, os.path.basename(OUT_JSON))

    rows = []
    seen_lid = set()
    dup_lid = 0
    unmatched_hdr = 0
    for n, (hdr, body) in enumerate(iter_entries(args.pd), 1):
        m = RE_HDR.match(hdr)
        if not m:
            unmatched_hdr += 1
            continue
        lid, pc, k1, k2 = m.groups()
        if lid in seen_lid:
            dup_lid += 1
        seen_lid.add(lid)
        rec = {"lid": lid, "pc": pc, "k1": k1, "k2": k2}
        rec.update(analyse(body))
        rows.append(rec)
        if args.limit and n >= args.limit:
            break

    with open(out_tsv, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[c]) for c in COLUMNS) + "\n")

    qs = sorted(r["quotations"] for r in rows)
    atts = sorted(r["attestations"] for r in rows)
    tot = {c: sum(r[c] for r in rows) for c in COLUMNS if c not in ("lid", "pc", "k1", "k2")}
    tot["entries"] = len(rows)

    def pct(sorted_vals, p):
        if not sorted_vals:
            return 0
        idx = min(len(sorted_vals) - 1, round((p / 100.0) * (len(sorted_vals) - 1)))
        return sorted_vals[idx]

    top = sorted(rows, key=lambda r: (-r["quotations"], r["lid"]))[:20]
    summary = {
        "dataset": "pd_quotations",
        "handoff": "H6949",
        "generated_by": "python scripts/pd_quotation_units.py",
        "generated_on": "2026-10-18",
        "unit": "quotation = maximal run of consecutive {#...#} blocks separated only by "
                "whitespace, immediately followed by a citation locus (siglum + locus); "
                "attestation = siglum locus + each bare further reference after ';'",
        "source": {
            "path": args.pd,
            "bytes": os.path.getsize(args.pd),
            "sha256": sha256(args.pd),
            "url": "https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/downloads/pdtxt.zip",
            "licence": "© 2014 The Sanskrit Library / Thomas Malten, CC BY-NC-SA 3.0",
        },
        "scope_caveat": "letter-a canon only, up to ~apaca- (fascicles 1976-2009); "
                        "the printed record has since reached Vol. 35 / 6,056 pp, still inside a-",
        "totals": tot,
        "distribution": {
            "quotations": {
                "median": statistics.median(qs) if qs else 0,
                "p90": pct(qs, 90), "p99": pct(qs, 99),
                "max": qs[-1] if qs else 0,
                "zero_entries": sum(1 for v in qs if v == 0),
                "mean": round(sum(qs) / len(qs), 3) if qs else 0,
            },
            "attestations": {
                "median": statistics.median(atts) if atts else 0,
                "p90": pct(atts, 90), "p99": pct(atts, 99),
                "max": atts[-1] if atts else 0,
                "mean": round(sum(atts) / len(atts), 3) if atts else 0,
            },
        },
        "blocks_vs_quotations": {
            "slp1_blocks": tot["slp1_blocks"],
            "quotations": tot["quotations"],
            "blocks_per_quotation": round(tot["slp1_blocks"] / tot["quotations"], 4)
            if tot["quotations"] else 0,
            "share_of_blocks_inside_quotations": round(
                100.0 * tot["blocks_in_quotations"] / tot["slp1_blocks"], 2)
            if tot["slp1_blocks"] else 0,
        },
        "cross_checks": {
            "siglum_loci_vs_h1336": {
                "h1336_citation_occurrences": 398359,
                "this_pass_siglum_loci": tot["siglum_loci"],
                "agreement_pct": round(100.0 * tot["siglum_loci"] / 398359, 2),
                "why_they_differ": "H1336 counts every siglum token anywhere in the entry; "
                                   "this pass counts only loci that close a quotation. The "
                                   "shortfall is sigla attached to a bare reference or to an "
                                   "entry with no quotation at all.",
            },
        },
        "integrity": {
            "entries_written": len(rows),
            "unmatched_headers": unmatched_hdr,
            "duplicate_lids": dup_lid,
        },
        "top20_by_quotations": [
            {k: r[k] for k in ("lid", "pc", "k1", "quotations", "blocks_in_quotations",
                               "attestations", "printed_lines")}
            for r in top
        ],
    }
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    print(f"entries={len(rows)} quotations={tot['quotations']:,} "
          f"attestations={tot['attestations']:,} blocks={tot['slp1_blocks']:,} "
          f"blocks/quote={summary['blocks_vs_quotations']['blocks_per_quotation']}")
    print(f"  unevaluable headers={unmatched_hdr} duplicate lids={dup_lid}")
    print(f"wrote {out_tsv}\nwrote {out_json}")


if __name__ == "__main__":
    main()
