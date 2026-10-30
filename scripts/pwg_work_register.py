#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7463 — Stage 0: the PWG work register, built from the exercised layer.

Rebuilds PWG's citation-source inventory at entry level from the exercised
``<ls>`` tags of the machine text — never from a whitespace crosswalk — under
pre-registration (e) of the PWG–NWS–PD–DCS protocol (report §8,
research/notes/final_report_pwg-nws-pd-dcs-8294e5.md):

  * attestation register  : the 729,719 quotation-linked tags (pre-reg (a));
  * extraction register   : the 801,788 raw ``<ls>`` tags;
  * deprecated registers  : 568,730 / 570,817 (never used here);
  * entry register        : 123,366 ``<L>`` entries.

A tag is quotation-linked iff it closes a run of one or more consecutive
``{#...#}`` SLP1 blocks separated only by whitespace — the same unit rule as
scripts/pd_quotations_vs_pwg.py (whose totals this script must reproduce
exactly: 801,788 raw, 729,719 quotation-linked).

Base-siglum normalization strips the locus payload from ``n`` values
("MBH. 3, 10620" -> "MBH."; "Spr. (II)" -> "Spr."), so the register counts
works, not work-locus pairs.

Outputs (all under data/pwg_dcs/):
  pwg_work_register.tsv        one row per base siglum, with mass + letters
  pwg_work_by_letter.tsv       base siglum x letter mass (for per-letter
                               dispersion and the alpha-frontier split)
  pwg_substrate_pins.json      sha pins + declared registers + boundaries

    python scripts/pwg_work_register.py [--pwg PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "pwg_dcs")
OUT_REGISTER = os.path.join(OUT_DIR, "pwg_work_register.tsv")
OUT_BY_LETTER = os.path.join(OUT_DIR, "pwg_work_by_letter.tsv")
OUT_PINS = os.path.join(OUT_DIR, "pwg_substrate_pins.json")

DEFAULT_PWG = os.environ.get(
    "PWG_TXT",
    os.path.join(os.path.expanduser("~"), "Documents", "GitHub", "csl-orig",
                 "v02", "pwg", "pwg.txt"),
)

# PD's letter-a frontier closes at k1 "apacaya" (last row of the committed
# data/pd/pd_quotations_by_entry.tsv; the A68 four-ledger table's "a-apaca").
PD_FRONTIER_LAST_K1 = "apacaya"

sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
import quotation_units  # noqa: E402  (RE_SLP1: the committed block splitter)

RE_HDR = re.compile(r"^<L>([\d.]+)<pc>([^<]*)<k1>([^<\s]*)<k2>([^<\s]*)")
RE_LS = re.compile(r"<ls([^>]*)>(.*?)</ls>", re.S)
RE_LS_N = re.compile(r'n="([^"]*)"')

# letter buckets in dictionary order (SLP1): two-char vowels first
_VOWELS = [
    ("RR", "ṝ"), ("lR", "ḷ"), ("ai", "ai"), ("au", "au"),
    ("a", "a"), ("A", "ā"), ("i", "i"), ("I", "ī"),
    ("u", "u"), ("U", "ū"), ("R", "ṛ"), ("e", "e"), ("o", "o"),
]


def letter_bucket(k1: str) -> str:
    for pref, label in _VOWELS:
        if k1.startswith(pref):
            return label
    return k1[0] if k1 else "?"


def base_siglum(n_value: str) -> str:
    """Strip the locus payload from an <ls n="..."> value."""
    s = n_value.strip()
    s = re.sub(r"\s*\(\s*[IVXLCDMivxlcdm]+\s*\)\s*$", "", s)  # " (II)"
    s = re.sub(r"\s+\d.*$", "", s)                            # " 3, 10620"
    s = re.sub(r"\s*,.*$", "", s)                             # trailing ", ..."
    return s.strip()


RE_DOTRUN = re.compile(r"^((?:[^\s\d,{}]+\.)+|[^\s\d,{}]+)")


def payload_siglum(payload: str) -> str:
    """Extract the leading siglum from an <ls>…</ls> payload.

    The dominant PWG form carries the siglum as payload text ("ṚV. 2,3,2"):
    take the maximal leading run of dot-terminated tokens, else the first
    word ("Padapāṭha"); the locus starts at the first digit-bearing token.
    """
    text = re.sub(r"<[^>]+>", " ", payload)
    m = RE_DOTRUN.match(text.strip())
    if not m:
        return text.strip().split()[0] if text.strip().split() else ""
    return m.group(1)


def canon_key(base: str) -> str:
    """Work-identity key: trailing roman-numeral volume tokens and dots off."""
    s = base.strip()
    s = re.sub(r"(?:\s+[IVXLCDM]+)+\s*$", "", s)
    s = re.sub(r"\.+$", "", s)
    return s.strip()


def iter_entries(path):
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


def walk_entry(body: str):
    """Yield (ls_n_or_None, quotation_linked) for every <ls> tag in order.

    Replicates scripts/lib/quotation_units.py count_units segmentation
    exactly: the body is split on {#...#} blocks (embedded payloads included
    — an <ls> may legitimately contain a block, e.g. "7,2263 ({#Elavila#})"),
    block 1 is the printed headword with a forced boundary after it, and every
    text segment after block j >= 2 is the tail of a maximal block-run whose
    complete <ls>...</ls> matches are the quotation-linked loci. Tags in the
    opening segment or the headword segment are references, not attestations.
    Reproduces 729,719 of 801,788 exactly.
    """
    segs = quotation_units.RE_SLP1.split(body)
    nblocks = (len(segs) - 1) // 2
    # segment segs[2*j] = text after block j; blocks 0 .. nblocks
    for j in range(0, nblocks + 1):
        tail = segs[2 * j]
        if "<ls" not in tail:
            continue
        linked = j >= 2
        for m in RE_LS.finditer(tail):
            nm = RE_LS_N.search(m.group(1))
            yield (nm.group(1) if nm else None, m.group(2)), linked
    # tags whose payload embeds a {#...#} block straddle the split points: the
    # marker never sees them complete inside one tail, so they are raw
    # references, never quotation-linked loci (e.g. "VS. KĀṆVA p. {#86#}")
    for m in RE_LS.finditer(body):
        if "{#" in m.group(0):
            nm = RE_LS_N.search(m.group(1))
            yield (nm.group(1) if nm else None, m.group(2)), False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pwg", default=DEFAULT_PWG)
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    sha = hashlib.sha256()
    with open(args.pwg, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            sha.update(chunk)
    pwg_sha = sha.hexdigest()
    pwg_bytes = os.path.getsize(args.pwg)

    # siglum -> counters; letter -> siglum -> counters
    reg = {}
    by_letter = defaultdict(lambda: defaultdict(lambda: {"raw": 0, "ql": 0}))
    entries = 0
    raw_total = 0
    ql_total = 0
    no_n = {"raw": 0, "ql": 0}
    alpha_ql = 0
    omega_ql = 0
    alpha_entries = 0

    for hdr, body_lines in iter_entries(args.pwg):
        m = RE_HDR.match(hdr)
        if not m:
            continue
        entries += 1
        k1 = m.group(3)
        in_alpha = k1 <= PD_FRONTIER_LAST_K1
        if in_alpha:
            alpha_entries += 1
        body = " ".join(body_lines).replace('<div n="lb">', " ")
        for (n_val, payload), ql in walk_entry(body):
            raw_total += 1
            ql_total += 1 if ql else 0
            if in_alpha:
                alpha_ql += 1 if ql else 0
            else:
                omega_ql += 1 if ql else 0
            base = base_siglum(n_val) if n_val else payload_siglum(payload)
            if not base:
                no_n["raw" if not ql else "ql"] += 1 if not ql else 1
                continue
            sig = canon_key(base)
            lit = letter_bucket(k1)
            r = reg.setdefault(sig, {"raw": 0, "ql": 0, "alpha_raw": 0, "alpha_ql": 0,
                                     "entries": set(),
                                     "letters": defaultdict(lambda: [0, 0]),
                                     "first_lid": m.group(1), "last_lid": m.group(1),
                                     "display": base, "sample_n": n_val or payload})
            r["raw"] += 1
            r["ql"] += 1 if ql else 0
            if in_alpha:
                r["alpha_raw"] += 1
                r["alpha_ql"] += 1 if ql else 0
            r["entries"].add(m.group(1))
            r["last_lid"] = m.group(1)
            lb = r["letters"][lit]
            lb[0] += 1
            lb[1] += 1 if ql else 0
            bl = by_letter[lit][sig]
            bl["raw"] += 1
            bl["ql"] += 1 if ql else 0

    with open(OUT_REGISTER, "w", encoding="utf-8") as out:
        out.write("base_siglum\traw_tags\tql_tags\talpha_raw\talpha_ql\tentries\t"
                  "letters\tfirst_lid\tlast_lid\tsample_n\n")
        for sig in sorted(reg, key=lambda s: -reg[s]["ql"]):
            r = reg[sig]
            letters = ";".join(
                f"{lit}:{r['letters'][lit][1]}"
                for lit in sorted(r["letters"], key=lambda l: -r["letters"][l][1]))
            out.write(f"{sig}\t{r['raw']}\t{r['ql']}\t{r['alpha_raw']}\t{r['alpha_ql']}\t"
                      f"{len(r['entries'])}\t"
                      f"{letters}\t{r['first_lid']}\t{r['last_lid']}\t{r['sample_n']}\n")

    with open(OUT_BY_LETTER, "w", encoding="utf-8") as out:
        out.write("letter\tbase_siglum\traw_tags\tql_tags\n")
        for lit in sorted(by_letter):
            for sig, c in sorted(by_letter[lit].items(), key=lambda kv: -kv[1]["ql"]):
                out.write(f"{lit}\t{sig}\t{c['raw']}\t{c['ql']}\n")

    pins = {
        "pwg_txt": {"path": args.pwg, "bytes": pwg_bytes, "sha256": pwg_sha},
        "registers": {
            "entries": entries,
            "raw_ls_tags": raw_total,
            "quotation_linked": ql_total,
            "deprecated_568730": "never used",
            "deprecated_570817": "never used",
            "tags_without_n_attr": no_n,
        },
        "distinct_base_sigla": len(reg),
        "pd_frontier": {"last_k1": PD_FRONTIER_LAST_K1,
                        "pwg_alpha_entries": alpha_entries,
                        "pwg_alpha_ql": alpha_ql,
                        "pwg_omega_ql": omega_ql},
        "note": "quotation-linked rule = shared unit rule of "
                "scripts/pd_quotations_vs_pwg.py; pins must equal "
                "801788 raw / 729719 ql",
    }
    with open(OUT_PINS, "w", encoding="utf-8") as out:
        json.dump(pins, out, ensure_ascii=False, indent=2, sort_keys=True)
        out.write("\n")

    print(f"entries={entries} raw={raw_total} ql={ql_total} "
          f"sigla={len(reg)} alpha_ql={alpha_ql} omega_ql={omega_ql}")
    if raw_total != 801788 or ql_total != 729719:
        print("PIN MISMATCH against the committed 801,788/729,719",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
