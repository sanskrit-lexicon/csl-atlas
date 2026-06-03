"""Phase L3 — csl-orig entry parser (foundation for F1/F2/F3).

Parses csl-orig/v02/<code>/<code>.txt into per-entry records. The format is a flat
stream of entries delimited by a `<L>...` header line and a `<LEND>` line, e.g.

  <L>1<pc>1-0001<k1>a<k2>a<h>1            <- header: id, page-col, keys, homonym
  1. {#a#} ... <ls>P. 1,1,14</ls> ...     <- body (1+ lines)
  <LEND>

Extracts: L (id), pc, k1/k2 (RAW headwords — pre-hwnorm1 normalization, so original
spelling/typos survive here), h (homonym number), e (MW display field), the body, and
every <ls>…</ls> citation (inner tags stripped). MW citations are abbreviated
(`<ls>T.</ls>`), PWG/PW fuller (`<ls>P. 1,1,14</ls>`).

NOTE: the citation count is `<ls>`-ONLY (the Western critical-apparatus tag). Dicts that
cite in the indigenous style (SKD/VCP: `iti`+authority, `"..."` quotes, `X0` authorities)
score 0 here yet are the MOST citation-dense in the corpus — see
data/forensic/CITATION_TAGGING.md. "0 <ls>" never means "citation-free".

Use as a module:  from parse_cslorig import iter_entries, load_entries
Or build caches:  python parse_cslorig.py pwg pw mw mw72      (--all = every local dict)
                  -> data/forensic/parsed/<code>.tsv  (L, k1, k2, h, e, n_cit, cites)
The body/gloss is NOT cached (large); F3 re-parses the few dicts it needs.
"""

import os
import re
import sys
import csv
import glob
import json

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

CSL_ORIG = "../csl-orig/v02"
PARSED_DIR = "data/forensic/parsed"

_ATTR = re.compile(r"<(k1|k2|h|e|pc)>([^<]*)")
_LID = re.compile(r"<L>([0-9.]+)")
_LS = re.compile(r"<ls>(.*?)</ls>", re.DOTALL)
_TAG = re.compile(r"<[^>]*>")
_WS = re.compile(r"\s+")


def clean_citation(raw):
    """Strip inner tags + collapse whitespace from an <ls> payload."""
    return _WS.sub(" ", _TAG.sub("", raw)).strip()


def iter_entries(path):
    """Yield dict(L, pc, k1, k2, h, e, body, citations) for each entry in a csl-orig file."""
    L = pc = k1 = k2 = h = e = None
    body = []
    inside = False
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("<LEND>"):
                if inside:
                    text = "".join(body)
                    cites = [clean_citation(m) for m in _LS.findall(text)]
                    yield {"L": L, "pc": pc, "k1": k1, "k2": k2, "h": h, "e": e,
                           "body": text, "citations": [c for c in cites if c]}
                inside = False
                body = []
                continue
            if line.startswith("<L>"):
                L = (_LID.search(line) or [None, None])[1]
                attrs = {k: v.strip() for k, v in _ATTR.findall(line)}
                pc, k1, k2 = attrs.get("pc"), attrs.get("k1"), attrs.get("k2")
                h, e = attrs.get("h"), attrs.get("e")
                inside = True
                body = []
                continue
            if inside:
                body.append(line)


def load_entries(code):
    """Read a cached <code>.tsv back into a list of dicts (citations split on '|')."""
    rows = []
    with open(os.path.join(PARSED_DIR, f"{code}.tsv"), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            r["citations"] = r["cites"].split("|") if r["cites"] else []
            rows.append(r)
    return rows


def build_cache(code):
    src = os.path.join(CSL_ORIG, code, f"{code}.txt")
    if not os.path.exists(src):
        print(f"  {code}: SOURCE MISSING ({src})", file=sys.stderr)
        return None
    os.makedirs(PARSED_DIR, exist_ok=True)
    n, n_cit, n_h = 0, 0, 0
    with open(os.path.join(PARSED_DIR, f"{code}.tsv"), "w", encoding="utf-8", newline="") as out:
        w = csv.writer(out, delimiter="\t")
        w.writerow(["L", "k1", "k2", "h", "e", "n_cit", "cites"])
        for ent in iter_entries(src):
            n += 1
            n_cit += len(ent["citations"])
            if ent["h"]:
                n_h += 1
            # '|' joins citations; sanitise stray tabs/pipes from raw fields
            cites = "|".join(c.replace("|", "/") for c in ent["citations"])
            row = [ent["L"], ent["k1"], ent["k2"], ent["h"], ent["e"], len(ent["citations"]), cites]
            w.writerow([str(x if x is not None else "").replace("\t", " ") for x in row])
    stats = {"code": code, "entries": n, "citations": n_cit, "with_homonym": n_h}
    print(f"  {code:8s} entries={n:>7,} ls_cites={n_cit:>8,} with_homonym={n_h:>7,}  "
          f"(ls only; 0 != citation-free, see CITATION_TAGGING.md)")
    return stats


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    if "--all" in args:
        codes = sorted(os.path.basename(os.path.dirname(p))
                       for p in glob.glob(os.path.join(CSL_ORIG, "*", "*.txt"))
                       if os.path.basename(p)[:-4] == os.path.basename(os.path.dirname(p)))
    else:
        codes = args
    print(f"Parsing {len(codes)} dict(s) from {CSL_ORIG} -> {PARSED_DIR}/")
    stats = [s for c in codes if (s := build_cache(c))]
    with open(os.path.join(PARSED_DIR, "_parse_stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"Cached {len(stats)} dict(s); stats -> {PARSED_DIR}/_parse_stats.json")


if __name__ == "__main__":
    main()
