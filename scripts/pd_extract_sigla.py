#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H1336 Phase 1 — extract citation sigla from the Poona Dictionary (pd.txt).

Reads the external, read-only pd.txt (drdhaval2785/SanskritSpellCheck) and
harvests every citation-siglum candidate with its occurrence count and up to
three sample contexts, writing data/pd/pd_siglum_raw.tsv.

A "siglum candidate" is an uppercase-initial alphabetic token ending in a
period, appearing in the roman running prose. Before matching we strip, in order:
  * {#...#}  SLP1 Sanskrit payloads (headwords / quoted Sanskrit, NOT citations)
  * {%...%}  italic gloss (English/IAST, not citations)
  * <...>    markup tags (<L>, <div n="lb">, <sup>, <pc>, <k1>, ...)
  * [...]    page markers ([Page1-0001a+ 54]) and editorial brackets

A trailing parenthetical qualifier — ŚivSū.(Gr.) — is consumed with the token
so the qualifier's own "Gr." is not miscounted as a separate siglum.

Occurrence mass, not distinct-token count, is what the coverage metrics weight,
so the count column is load-bearing downstream.
"""
import sys
import re
import os
import io
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

PD_TXT = os.environ.get(
    "PD_TXT",
    r"C:\Users\user\Documents\GitHub\SanskritSpellCheck\external_src\pd\pd.txt",
)
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "pd")
OUT_TSV = os.path.join(OUT_DIR, "pd_siglum_raw.tsv")

# strip helpers (order matters: SLP1 payloads first, then italic, then tags)
RE_SLP1 = re.compile(r"\{#.*?#\}")
RE_ITALIC = re.compile(r"\{%.*?%\}")
RE_TAG = re.compile(r"<[^>]*>")
RE_BRACKET = re.compile(r"\[[^\]]*\]")

# a siglum token: uppercase-initial run of Unicode letters ending in '.',
# with an optional trailing "(...)" qualifier consumed but discarded.
# [^\W\d_] = Unicode letter (no digit, no underscore) under re.UNICODE (default for str).
RE_SIGLUM = re.compile(r"([^\W\d_][^\W\d_]*)\.(\([^)]*\))?")

CTX_RADIUS = 45
MAX_CTX = 3


def clean_line(line: str) -> str:
    line = RE_SLP1.sub(" ", line)
    line = RE_ITALIC.sub(" ", line)
    line = RE_TAG.sub(" ", line)
    line = RE_BRACKET.sub(" ", line)
    return line


def main() -> int:
    counts = Counter()
    contexts = defaultdict(list)
    total_occ = 0
    n_lines = 0
    n_entries = 0

    with io.open(PD_TXT, "r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            n_lines += 1
            # header / file banner
            if raw.startswith("%***"):
                continue
            if "<L>" in raw:
                n_entries += raw.count("<L>")
            cleaned = clean_line(raw)
            for m in RE_SIGLUM.finditer(cleaned):
                token = m.group(1)
                # must be uppercase-initial to be a siglum (skips cf., v., etc.)
                if not token[:1].isupper():
                    continue
                siglum = token + "."
                counts[siglum] += 1
                total_occ += 1
                if len(contexts[siglum]) < MAX_CTX:
                    start = max(0, m.start() - CTX_RADIUS)
                    end = min(len(cleaned), m.end() + CTX_RADIUS)
                    snippet = cleaned[start:end].replace("\t", " ").strip()
                    snippet = re.sub(r"\s+", " ", snippet)
                    contexts[siglum].append(snippet)

    os.makedirs(OUT_DIR, exist_ok=True)
    with io.open(OUT_TSV, "w", encoding="utf-8", newline="\n") as out:
        out.write("siglum\tcount\tctx1\tctx2\tctx3\n")
        for siglum, c in counts.most_common():
            ctx = contexts[siglum] + ["", "", ""]
            out.write(f"{siglum}\t{c}\t{ctx[0]}\t{ctx[1]}\t{ctx[2]}\n")

    # sanity summary to stderr
    distinct = len(counts)
    hapax = sum(1 for v in counts.values() if v == 1)
    tail_3_10 = sum(1 for v in counts.values() if 3 <= v <= 10)
    print(f"lines read           : {n_lines:,}", file=sys.stderr)
    print(f"<L> entries          : {n_entries:,}", file=sys.stderr)
    print(f"distinct sigla       : {distinct:,}", file=sys.stderr)
    print(f"total occurrences    : {total_occ:,}", file=sys.stderr)
    print(f"hapax (freq 1)       : {hapax:,}", file=sys.stderr)
    print(f"tail (freq 3-10)     : {tail_3_10:,}", file=sys.stderr)
    print(f"wrote                : {OUT_TSV}", file=sys.stderr)
    print("\ntop 20:", file=sys.stderr)
    for siglum, c in counts.most_common(20):
        print(f"  {siglum:16s} {c:6d}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
