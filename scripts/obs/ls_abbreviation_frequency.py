#!/usr/bin/env python3
"""OBS-C per-abbreviation `<ls>` token frequencies (csl-atlas#222, GH-4).

`data/obs/citation_registers.json` gives per-dictionary `<ls>` *totals* but not
which abbreviations make them up, so csl-guides' abbreviation-resolvability
hypothesis (GH-4) can only state an exposure upper bound — "how many citations
sit under some abbreviation" — never true legend coverage ("how many citations
sit under an abbreviation the dictionary's own legend explains"). Legend
coverage is a token-weighted question: it needs the occurrence mass behind each
distinct abbreviation, per dictionary.

This script emits that missing layer: `data/obs/ls_abbreviation_frequency.json`,
shaped `{dict: {token: count}}` over all discovered csl-orig dictionaries.

Method (two reused conventions, neither re-derived here)
-------------------------------------------------------
1. **Citation extraction** — `parse_cslorig.iter_entries`, which matches both
   `<ls>` shapes (bare `<ls>Pāṇ. vi, 2, 161</ls>` and attributed
   `<ls n="RV.">vii, 96, 3</ls>`) and joins `@n` with the tag content. A literal
   `<ls>` match misses the attributed form entirely — the H1086 defect that
   undercounted MW's `<ls>` total by 28.6%.
2. **Citation → abbreviation token** — a Python port of the splitter the shipped
   apparatus pipeline already uses, `baseForm(normalizeSource(c))` from
   `scripts/lib/mw-source-layers.mjs` / `scripts/lib/mw-classifiers.mjs`
   (`build-citation-apparatus.mjs` line ~92): collapse whitespace, drop a
   trailing period, then cut at the first `.` or `,` — "MBh. iii,5" -> "MBh".
   Keep in lockstep with those two modules.

The emitted token is the **raw** abbreviation as the dictionary writes it
("MBh", "MBH", "ṚV", "RV"), not a fold key: the legend question is about the
form a reader meets on the page. `foldSiglum`/`canonicalSiglum`
(`scripts/lib/source-siglum.mjs`, ported in `scripts/obs/siglum_families.py`)
are the cross-dictionary identity layer and stay a separate concern.

Every `<ls>` citation contributes exactly one token, so per dictionary
`sum(counts) == citation_registers.json dicts[code].ls`. That invariant is the
artifact's correctness test (`test/ls-abbreviation-frequency.test.mjs`); it is
why a citation whose base form comes out empty (a lone `<ls>.</ls>`) falls back
to its own raw text rather than being dropped.

Usage (from the repo root; CSL_ORIG env overrides the ../csl-orig/v02 default):
    python scripts/obs/ls_abbreviation_frequency.py
"""
import json
import os
import re
import sys
import unicodedata
from collections import Counter

sys.path.insert(0, os.path.abspath("scripts/forensic"))
sys.path.insert(0, os.path.abspath("scripts/lib"))
sys.path.insert(0, os.path.abspath("scripts/obs"))
from parse_cslorig import iter_entries  # noqa: E402
from dataset_meta import (  # noqa: E402
    generated_at_for_payload, license_fields, read_json_if_exists,
)
# Same dictionary roster as the sibling register artifact, imported rather than
# re-globbed so the two artifacts can never disagree about which dicts exist
# (the test asserts their `dicts` key sets are identical).
from citation_register_gaps import CSL_ORIG, discover_dicts  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OUT = os.path.join("data", "obs", "ls_abbreviation_frequency.json")
REGISTERS = os.path.join("data", "obs", "citation_registers.json")
SCHEMA_VERSION = "1.0.0"

_WS = re.compile(r"\s+")
_TRAILING_DOT = re.compile(r"\.$")
_BASE_SPLIT = re.compile(r"[.,]")


def normalize_source(value):
    """Port of normalizeSource() in scripts/lib/mw-classifiers.mjs."""
    return _TRAILING_DOT.sub("", _WS.sub(" ", unicodedata.normalize("NFC", value or "")).strip())


def base_form(normalized):
    """Port of baseForm() in scripts/lib/mw-source-layers.mjs."""
    base = _BASE_SPLIT.split(normalized)[0].strip()
    return base if base else normalized


def abbreviation_token(citation):
    """The abbreviation a citation is filed under, raw as written.

    Falls back to the citation's own text when the base form is empty (only a
    citation that is nothing but punctuation, e.g. `<ls>.</ls>`), so the
    one-token-per-citation invariant holds without inventing a sentinel key.
    """
    token = base_form(normalize_source(citation))
    return token if token else _WS.sub(" ", (citation or "").strip())


def tokens_for(code):
    """Counter of raw abbreviation tokens for one dictionary (empty if no <ls>)."""
    path = os.path.join(CSL_ORIG, code, f"{code}.txt")
    if not os.path.exists(path):
        return None
    counts = Counter()
    for entry in iter_entries(path):
        for citation in entry.get("citations") or []:
            token = abbreviation_token(citation)
            if token:
                counts[token] += 1
    return counts


def build_payload(per_dict):
    dicts = {
        code: dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
        for code, counts in sorted(per_dict.items())
    }
    corpus = Counter()
    for counts in per_dict.values():
        corpus.update(counts)
    return {
        "schemaVersion": SCHEMA_VERSION,
        **license_fields(),
        "generatedBy": "scripts/obs/ls_abbreviation_frequency.py",
        "sourceRoot": "../csl-orig/v02",
        "method": {
            "extraction": "every <ls>…</ls> element per parse_cslorig.iter_entries (bare and "
                          "@n-attributed shapes both matched, @n joined to the tag content — "
                          "the H1086 fix)",
            "token": "baseForm(normalizeSource(citation)) ported from scripts/lib/"
                     "mw-source-layers.mjs + scripts/lib/mw-classifiers.mjs: NFC, collapse "
                     "whitespace, drop a trailing period, cut at the first '.' or ',' — "
                     "'MBh. iii,5' -> 'MBh'; a citation with an empty base form falls back "
                     "to its own text",
            "form": "raw abbreviation as the dictionary writes it, NOT folded — 'MBh' and "
                    "'MBH' stay distinct; cross-dictionary identity is foldSiglum/"
                    "canonicalSiglum in scripts/lib/source-siglum.mjs",
            "invariant": "exactly one token per <ls> citation, so per dictionary "
                         "sum(counts) == data/obs/citation_registers.json dicts[code].ls",
            "ordering": "written count-descending, then token ascending, for diff stability — "
                        "but do NOT rely on JSON object key order when reading: a JS engine "
                        "hoists integer-like keys (a locator-only citation such as <ls>78</ls> "
                        "yields the token '78') to the front in numeric order. Sort by value.",
        },
        "dictionaryCount": len(dicts),
        "totals": {
            "ls": sum(corpus.values()),
            "distinctTokensCorpus": len(corpus),
            "distinctTokenDictPairs": sum(len(v) for v in dicts.values()),
            "dictsWithLs": sum(1 for v in dicts.values() if v),
        },
        "dicts": dicts,
    }


def print_report(payload):
    totals = payload["totals"]
    print(f"=== <ls> abbreviation tokens ({payload['dictionaryCount']} dicts) ===")
    print(f"  citations={totals['ls']:,}  distinct tokens (corpus)={totals['distinctTokensCorpus']:,}  "
          f"dict×token pairs={totals['distinctTokenDictPairs']:,}  "
          f"dicts with <ls>={totals['dictsWithLs']}")

    registers = read_json_if_exists(REGISTERS)
    if registers:
        print("\n=== Invariant check vs citation_registers.json ===")
        mismatches = []
        for code, counts in payload["dicts"].items():
            expected = (registers.get("dicts", {}).get(code) or {}).get("ls")
            got = sum(counts.values())
            if expected is not None and expected != got:
                mismatches.append((code, expected, got))
        if mismatches:
            for code, expected, got in mismatches:
                print(f"  MISMATCH {code}: registers ls={expected:,} vs tokens={got:,}")
        else:
            print(f"  OK — every dict's token sum equals its <ls> total "
                  f"(corpus {totals['ls']:,} vs {registers.get('totals', {}).get('ls'):,})")

    print("\n=== Most-cited abbreviations per dictionary (top 5) ===")
    ranked = sorted(payload["dicts"].items(), key=lambda kv: -sum(kv[1].values()))
    for code, counts in ranked[:8]:
        if not counts:
            continue
        top = list(counts.items())[:5]
        print(f"  {code.upper():6s} {sum(counts.values()):>8,} citations over {len(counts):>6,} tokens  "
              + "  ".join(f"{t}×{n:,}" for t, n in top))

    # The GH-4 lever: legend coverage is token-weighted, so what matters is how
    # much citation mass a short legend can reach. A steep head means a legend
    # of a few dozen entries already explains most of the apparatus.
    print("\n=== Legend-coverage lever: citation mass by token rank ===")
    print(f"  {'dict':6s} {'citations':>10s} {'tokens':>7s} {'top50':>7s} {'top100':>7s} {'>=10x':>7s} {'hapax':>7s}")
    for code, counts in ranked:
        if not counts:
            continue
        total = sum(counts.values())
        values = sorted(counts.values(), reverse=True)
        top50 = sum(values[:50]) / total
        top100 = sum(values[:100]) / total
        frequent = sum(v for v in values if v >= 10) / total
        hapax = sum(1 for v in values if v == 1)
        print(f"  {code.upper():6s} {total:>10,} {len(counts):>7,} {top50:>6.1%} {top100:>6.1%} "
              f"{frequent:>6.1%} {hapax:>7,}")


def main():
    per_dict = {}
    for code in discover_dicts():
        counts = tokens_for(code)
        if counts is not None:
            per_dict[code] = counts

    payload = build_payload(per_dict)
    payload["generatedAt"] = generated_at_for_payload(read_json_if_exists(OUT), payload)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print_report(payload)
    print(f"\nWrote {OUT} ({payload['dictionaryCount']} dicts, "
          f"{payload['totals']['distinctTokenDictPairs']:,} dict×token rows)")


if __name__ == "__main__":
    main()
