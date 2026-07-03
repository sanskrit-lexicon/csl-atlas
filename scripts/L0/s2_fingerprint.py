"""Stage 2 — convention fingerprint, REAL extraction.

Replaces the earlier placeholder pass (commit 25705d1) that wrote the same
constant down every column for all 35 dicts -- a degenerate matrix with zero
phylogenetic signal. This version streams each dictionary's local CDSL source
(`../csl-orig/v02/<code>/<code>.txt`), samples up to CAP entries, and derives
the mechanically-recoverable convention dimensions from the actual markup.

Design rules honoured:
- No fabricated values. A dimension with no detectable signal stays `unknown`
  and goes to annotation_todo.csv.
- The 9 Patel/philological dims (1-8, 16) require the Patel 2016 schema or a
  linguistic judgement we cannot make mechanically -> always `unknown` here.
- Per-dimension VARIANCE CHECK: after the matrix is built, any auto dim that
  came out constant across all dicts is reported as non-informative. We surface
  constants; we never invent variance to hide them.
- Confidence is margin-based, capped at 0.9 (only a Patel pass would be 1.0).
"""

import os
import sys
import json
import csv
import re
import unicodedata
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_ROOT = os.path.normpath(os.path.join(REPO, "..", "csl-orig", "v02"))
CAP = 4000  # entries sampled per dict; conventions are global, so first-N is fine

DIMS = [
    {"dim_id": 1, "name": "Anusvāra before consonants", "options": ["opt1", "opt2", "opt3", "opt4", "opt5", "opt6"]},
    {"dim_id": 2, "name": "Duplication after r", "options": ["opt1", "opt2"]},
    {"dim_id": 3, "name": "Words ending with -at", "options": ["opt1", "opt2", "opt3", "opt4", "opt5"]},
    {"dim_id": 4, "name": "Inflected vs uninflected headword form", "options": ["inflected", "uninflected"]},
    {"dim_id": 5, "name": "Anusvāra of verbs", "options": ["present", "absent"]},
    {"dim_id": 6, "name": "ṛkārānta words", "options": ["opt1", "opt2", "opt3"]},
    {"dim_id": 7, "name": "vas/yas suffixes", "options": ["opt1", "opt2", "opt3", "opt4"]},
    {"dim_id": 8, "name": "Sandhi handling at compound boundary", "options": ["preserved", "split", "both"]},
    {"dim_id": 9, "name": "Compound-headword separation", "options": ["hyphen", "space", "merged"]},
    {"dim_id": 10, "name": "Variant-headword inclusion (<k2>)", "options": ["none", "few", "many"]},
    {"dim_id": 11, "name": "Sense numbering style", "options": ["arabic", "roman", "alpha", "sanskrit", "unnumbered"]},
    {"dim_id": 12, "name": "Sense-internal separator", "options": ["semicolon", "comma", "period", "colon"]},
    {"dim_id": 13, "name": "Sub-sense indentation", "options": ["present", "flat"]},
    {"dim_id": 14, "name": "Citation depth", "options": ["full", "partial", "minimal", "mixed"]},
    {"dim_id": 15, "name": "Citation format style", "options": ["abbreviated", "full", "sanskrit"]},
    {"dim_id": 16, "name": "Mahābhārata edition reference", "options": ["pune", "critical"]},
    {"dim_id": 17, "name": "Grammar marker style", "options": ["abbreviated", "full", "sanskrit"]},
    {"dim_id": 18, "name": "Verb-class marker style", "options": ["roman", "arabic", "sanskrit"]},
    {"dim_id": 19, "name": "Etymology presence", "options": ["none", "partial", "full"]},
    {"dim_id": 20, "name": "Cross-reference syntax", "options": ["explicit", "k1", "italic", "absent"]},
    {"dim_id": 21, "name": "Loanword marker", "options": ["tagged", "untagged"]},
    {"dim_id": 22, "name": "Vedic accent preservation", "options": ["present", "absent"]},
    {"dim_id": 23, "name": "Vedic-only marker", "options": ["flagged", "unflagged"]},
    {"dim_id": 24, "name": "Frequency / rarity marker", "options": ["present", "absent"]},
    {"dim_id": 25, "name": "Indeclinable marker style", "options": ["ind", "inv", "nipata", "unmarked"]},
    {"dim_id": 26, "name": "Pāṇinian sūtra reference", "options": ["cited", "uncited"]},
    {"dim_id": 27, "name": "Source-language identification within entries", "options": ["present", "absent"]},
    {"dim_id": 28, "name": "Etymology presence rate", "options": [">5%", "<=5%"]},
    {"dim_id": 29, "name": "Etymology mean-length", "options": ["low", "med", "high"]},
    {"dim_id": 30, "name": "Distinct etym-marker patterns", "options": ["0", "1", ">1"]},
]

# Dims we never auto-fill: Patel transcription schema (1-3,5-7), sandhi (8),
# inflection judgement (4), Mahābhārata-edition (16). Left for the human gate.
ANNOTATION_ONLY = {1, 2, 3, 4, 5, 6, 7, 8, 16}

# ---- compiled patterns --------------------------------------------------
RX = {
    "ls": re.compile(r"<ls\b[^>]*>(.*?)</ls>", re.S),
    "s_tok": re.compile(r"<s1?>(.*?)</s1?>", re.S),
    "hash_tok": re.compile(r"\{#(.*?)#\}", re.S),
    # final alternative catches mid-line sense markers like YAT/SHS "} 1. NO, ... 2. A ..."
    # -- "} 1. " or " 1. " followed by an uppercase letter or {# Sanskrit form.
    "num_arabic": re.compile(r"\.²\s*\d|\{@\s*-*\s*\d|<hom>\s*\d|(?:^|\n)\s*\d{1,2}\.\s|[\s\}]\d{1,2}\.\s+[A-Z{]"),
    "num_roman": re.compile(r"<hom>\s*[IVXLivxl]{1,4}\b|(?:^|\n|\s)[IVXL]{1,4}\.\s"),
    "num_alpha": re.compile(r"\(\s*\{?%?\s*[a-z]\s*%?\}?\s*\)|(?:^|\s)[a-z]\)\s"),
    "gram_abbrev": re.compile(r"(?:<lex>\s*)?\b(?:mfn|m|f|n)\."),
    "gram_full": re.compile(r"\b(?:masc|fem|neut)\."),
    "gram_skt": re.compile(r"\b[a-zA-Zāīūṛṅñṭḍṇśṣ]+0\b"),
    "cl_arabic": re.compile(r"\b\d+(?:st|nd|rd|th)?\s*cl\b|\bcl\.\s*\d"),
    "cl_roman": re.compile(r"\bcl\.\s*[ivxIVX]+\b"),
    # WIL writes ".E. {#..#}" (period-E-period); SHS writes " E. {#..#}" (space-E-period).
    # The unified pattern: E. preceded by sentence end or whitespace, then followed by a
    # Sanskrit headword in {#..#}. Requiring the {# anchor avoids false hits on initials
    # or stray "E." abbreviations.
    "etym_E": re.compile(r"(?:^|[\s.¦])E\.\s+\{#"),
    "etym_tag": re.compile(r"<etym>(.*?)</etym>", re.S),
    "etym_lang": re.compile(r"<lang\b|<gk>|<ar>|<zd>"),
    "etym_fr": re.compile(r"\bfr\.\s"),
    "etym_bracket": re.compile(r"\[\{#(.*?)#\}", re.S),
    "xref": re.compile(r"\bq\.v\.|<ab>\s*cf\.|\bcf\.\s|\b[Ss]ee\s\{#|\bs\.\s\{#"),
    # genuine source-language / cognate tagging only.
    # NB: {%...%} is the universal *italic-gloss* convention (English/French/German/
    # Latin target glosses) -- NOT a language tag -- so it must be excluded, else
    # every bilingual glossary spuriously scores "loanword tagged".
    "lang_tag": re.compile(r"<lang\b|<gk>|<ar>|<zd>|\b(?:Gk|Lat|Goth|Germ|Pers|Arab|Lith|Slav|Zend)\."),
    "ind_ind": re.compile(r"(?:<lex>\s*)?\bindecl?\."),
    "ind_inv": re.compile(r"\binv\."),
    "ind_nipata": re.compile(r"nipAta|\bnip\."),
    "panini": re.compile(r"\bPāṇ|<ls>\s*P\.\s*\d|\bP\.\s*\d+\s*,\s*\d"),
    "vedic": re.compile(r"\bVed\.|\bvedisch|\bvaidika"),
    "freq": re.compile(r"\brare(?:ly)?\b|\bfrequent(?:ly)?\b|\boften\b|\bselten\b|\bhäufig\b|\bgew\."),
    "subsense": re.compile(r"<div\b|\(\s*\{?%?\s*[a-z]\s*%?\}?\s*\)"),
    "accent": re.compile(r"[/\\]"),
}


def norm(s):
    return unicodedata.normalize("NFC", s)


def iter_entries(path, cap):
    """Yield (k1, k2, body) for up to `cap` entries, streaming line by line."""
    k1 = k2 = None
    body = []
    started = False
    n = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("<L>") or line.startswith("<L "):
                if started:
                    yield k1 or "", k2 or "", "".join(body)
                    n += 1
                    if n >= cap:
                        return
                started = True
                body = []
                m1 = re.search(r"<k1>([^<]*)", line)
                m2 = re.search(r"<k2>([^<]*)", line)
                k1 = m1.group(1) if m1 else ""
                k2 = m2.group(1) if m2 else ""
            elif "<LEND>" in line:
                if started:
                    yield k1 or "", k2 or "", "".join(body)
                    n += 1
                    if n >= cap:
                        return
                    started = False
                    body = []
            elif started:
                body.append(line)
    if started and body:
        yield k1 or "", k2 or "", "".join(body)


def extract(path):
    c = defaultdict(int)
    etym_markers = set()
    etym_lens = []
    for k1, k2, body in iter_entries(path, CAP):
        c["n"] += 1
        b = body

        # --- headword separation / variants (dims 9,10) ---
        if k2:
            c["k2_total"] += 1
            if "—" in k2 or "-" in k2:
                c["k2_hyphen"] += 1
            elif " " in k2:
                c["k2_space"] += 1
            if "—" in k2 or "-" in k2 or " " in k2 or "+" in k2:
                c["k2_sep_any"] += 1

        # --- sense numbering (dim 11) ---
        c["num_arabic"] += len(RX["num_arabic"].findall(b))
        c["num_roman"] += len(RX["num_roman"].findall(b))
        c["num_alpha"] += len(RX["num_alpha"].findall(b))

        # --- sense separator (dim 12) ---
        c["sep_semicolon"] += b.count(";")
        c["sep_comma"] += b.count(",")
        c["sep_colon"] += b.count(":")

        # --- citations (dims 14,15) ---
        ls = RX["ls"].findall(b)
        if ls:
            c["ls_entries"] += 1
            c["ls_count"] += len(ls)
            for content in ls:
                c["ls_chars"] += len(content)
                if re.search(r"\d", content):
                    c["ls_locus"] += 1
                if "<s" in content or "{#" in content:
                    c["ls_sanskrit"] += 1

        # --- grammar marker style (dim 17) ---
        c["gram_abbrev"] += len(RX["gram_abbrev"].findall(b))
        c["gram_full"] += len(RX["gram_full"].findall(b))
        c["gram_skt"] += len(RX["gram_skt"].findall(b))

        # --- verb-class marker (dim 18) ---
        c["cl_arabic"] += len(RX["cl_arabic"].findall(b))
        c["cl_roman"] += len(RX["cl_roman"].findall(b))

        # --- etymology (dims 19,28,29,30) ---
        had_etym = False
        m_e = RX["etym_E"].search(b)
        if m_e:
            had_etym = True
            etym_markers.add("E.")  # unified WIL `.E.` + SHS-style ` E. ` Nirukta marker
            seg = b[m_e.end():]
            etym_lens.append(len(re.sub(r"<[^>]+>", "", seg).strip()[:200]))
        for content in RX["etym_tag"].findall(b):
            had_etym = True
            etym_markers.add("<etym>")
            etym_lens.append(len(content))
        if RX["etym_lang"].search(b):
            had_etym = True
            etym_markers.add("<lang>")
        for content in RX["etym_bracket"].findall(b):
            had_etym = True
            etym_markers.add("[{#")
            etym_lens.append(len(content))
        if RX["etym_fr"].search(b):
            had_etym = True
            etym_markers.add("fr.")
        if had_etym:
            c["etym_entries"] += 1

        # --- cross-reference (dim 20) ---
        if RX["xref"].search(b):
            c["xref_explicit"] += 1

        # --- loanword / source-language (dims 21,27) ---
        if RX["lang_tag"].search(b):
            c["lang_tag"] += 1

        # --- accents (dim 22) ---
        toks = RX["hash_tok"].findall(b) + RX["s_tok"].findall(b)
        if toks:
            for t in toks:
                c["skt_tokens"] += 1
                if RX["accent"].search(t):
                    c["skt_accent"] += 1

        # --- indeclinable marker (dim 25) ---
        c["ind_ind"] += len(RX["ind_ind"].findall(b))
        c["ind_inv"] += len(RX["ind_inv"].findall(b))
        c["ind_nipata"] += len(RX["ind_nipata"].findall(b))

        # --- Pāṇini, Vedic-only, frequency, sub-sense (dims 26,23,24,13) ---
        if RX["panini"].search(b):
            c["panini"] += 1
        if RX["vedic"].search(b):
            c["vedic"] += 1
        if RX["freq"].search(b):
            c["freq"] += 1
        if RX["subsense"].search(b):
            c["subsense"] += 1

    c["etym_markers"] = etym_markers
    c["etym_lens"] = etym_lens
    return c


def conf(margin, base=0.5, scale=0.4):
    return round(min(0.9, base + scale * margin), 2)


def dominant(pairs):
    """pairs: list of (label, count). Return (label, share) or (None, 0)."""
    total = sum(v for _, v in pairs)
    if total == 0:
        return None, 0.0
    label, count = max(pairs, key=lambda p: p[1])
    return label, count / total


def derive(c):
    """Return {dim_id: (value, confidence)} for auto dims with signal."""
    out = {}
    n = max(c["n"], 1)

    # dim 9 compound-headword separation
    lab, share = dominant([("hyphen", c["k2_hyphen"]), ("space", c["k2_space"])])
    if c["k2_total"]:
        sep_rate = c["k2_sep_any"] / c["k2_total"]
        if sep_rate < 0.02:
            out[9] = ("merged", conf(1 - sep_rate))
        elif lab:
            out[9] = (lab, conf(share))

    # dim 10 variant/compound headword rate
    if c["k2_total"]:
        r = c["k2_sep_any"] / c["k2_total"]
        val = "none" if r < 0.02 else ("few" if r < 0.30 else "many")
        out[10] = (val, 0.7)

    # dim 11 sense numbering
    lab, share = dominant([("arabic", c["num_arabic"]), ("roman", c["num_roman"]),
                           ("alpha", c["num_alpha"])])
    if lab and (c["num_arabic"] + c["num_roman"] + c["num_alpha"]) >= max(5, 0.02 * n):
        out[11] = (lab, conf(share))
    elif (c["num_arabic"] + c["num_roman"] + c["num_alpha"]) < max(5, 0.02 * n):
        out[11] = ("unnumbered", 0.6)

    # dim 12 sense-internal separator
    lab, share = dominant([("semicolon", c["sep_semicolon"]), ("comma", c["sep_comma"]),
                           ("colon", c["sep_colon"])])
    if lab:
        out[12] = (lab, conf(share))

    # dim 13 sub-sense indentation
    r = c["subsense"] / n
    out[13] = (("present", 0.75) if r > 0.02 else ("flat", 0.7))

    # dim 14 citation depth
    ls_rate = c["ls_entries"] / n
    if ls_rate < 0.05:
        out[14] = ("minimal", conf(1 - ls_rate))
    elif c["ls_count"]:
        locus_share = c["ls_locus"] / c["ls_count"]
        if locus_share > 0.6:
            out[14] = ("full", conf(locus_share))
        elif locus_share < 0.2:
            out[14] = ("partial", conf(1 - locus_share))
        else:
            out[14] = ("mixed", 0.6)

    # dim 15 citation format style
    if c["ls_count"]:
        skt_share = c["ls_sanskrit"] / c["ls_count"]
        avg_len = c["ls_chars"] / c["ls_count"]
        if skt_share > 0.4:
            out[15] = ("sanskrit", conf(skt_share))
        elif avg_len > 25:
            out[15] = ("full", 0.65)
        else:
            out[15] = ("abbreviated", 0.8)

    # dim 17 grammar marker style
    lab, share = dominant([("abbreviated", c["gram_abbrev"]), ("full", c["gram_full"]),
                           ("sanskrit", c["gram_skt"])])
    if lab:
        out[17] = (lab, conf(share))

    # dim 18 verb-class marker style
    lab, share = dominant([("arabic", c["cl_arabic"]), ("roman", c["cl_roman"])])
    if lab and (c["cl_arabic"] + c["cl_roman"]) >= 3:
        out[18] = (lab, conf(share))

    # dim 19 etymology presence
    er = c["etym_entries"] / n
    if er < 0.01:
        out[19] = ("none", conf(1 - er))
    elif er < 0.20:
        out[19] = ("partial", 0.7)
    else:
        out[19] = ("full", conf(er))

    # dim 20 cross-reference syntax
    xr = c["xref_explicit"] / n
    out[20] = (("explicit", conf(min(1, xr * 10))) if xr > 0.005 else ("absent", 0.7))

    # dim 21 loanword marker
    lr = c["lang_tag"] / n
    out[21] = (("tagged", 0.8) if lr > 0.01 else ("untagged", 0.75))

    # dim 22 Vedic accent preservation
    if c["skt_tokens"]:
        ar = c["skt_accent"] / c["skt_tokens"]
        out[22] = (("present", conf(min(1, ar * 5))) if ar > 0.01 else ("absent", 0.75))

    # dim 23 Vedic-only marker
    vr = c["vedic"] / n
    out[23] = (("flagged", 0.7) if vr > 0.005 else ("unflagged", 0.7))

    # dim 24 frequency / rarity marker
    fr = c["freq"] / n
    out[24] = (("present", 0.7) if fr > 0.01 else ("absent", 0.7))

    # dim 25 indeclinable marker style
    lab, share = dominant([("ind", c["ind_ind"]), ("inv", c["ind_inv"]),
                           ("nipata", c["ind_nipata"])])
    if lab and (c["ind_ind"] + c["ind_inv"] + c["ind_nipata"]) >= 3:
        out[25] = (lab, conf(share))
    elif (c["ind_ind"] + c["ind_inv"] + c["ind_nipata"]) < 3:
        out[25] = ("unmarked", 0.6)

    # dim 26 Pāṇinian sūtra reference
    pr = c["panini"] / n
    out[26] = (("cited", conf(min(1, pr * 10))) if pr > 0.003 else ("uncited", 0.75))

    # dim 27 source-language identification (same evidence as dim 21, distinct concept)
    out[27] = (("present", 0.78) if c["lang_tag"] / n > 0.01 else ("absent", 0.72))

    # dim 28 etymology presence rate
    out[28] = ((">5%", 0.8) if c["etym_entries"] / n > 0.05 else ("<=5%", 0.8))

    # dim 29 etymology mean-length
    if c["etym_lens"]:
        ml = sum(c["etym_lens"]) / len(c["etym_lens"])
        val = "low" if ml < 30 else ("med" if ml < 80 else "high")
        out[29] = (val, 0.65)

    # dim 30 distinct etym-marker patterns
    nm = len(c["etym_markers"])
    out[30] = (("0", 0.85) if nm == 0 else ("1" if nm == 1 else ">1", 0.8))

    return out


def main():
    os.makedirs("data/L0", exist_ok=True)
    with open("data/L0/dim_schema.json", "w", encoding="utf-8") as f:
        json.dump(DIMS, f, indent=2, ensure_ascii=False)

    dicts = []
    with open("data/L0/inventory_subset.csv", "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            dicts.append(r["code"])
    print(f"Loaded {len(dicts)} dicts.")

    results = []
    per_dim_values = defaultdict(set)
    cells_auto = 0
    cells_unknown = 0
    missing_src = []

    for code in dicts:
        path = os.path.join(SRC_ROOT, code.lower(), code.lower() + ".txt")
        derived = {}
        if os.path.isfile(path):
            c = extract(path)
            derived = derive(c)
            print(f"  {code:5s} n={c['n']:5d} auto_dims={len(derived)}")
        else:
            missing_src.append(code)
            print(f"  {code:5s} SOURCE MISSING -> all unknown")

        row = {"dict": code}
        for d in range(1, 31):
            if d in ANNOTATION_ONLY or d not in derived:
                row[f"dim_{d}_value"] = "unknown"
                row[f"dim_{d}_source"] = "unknown"
                row[f"dim_{d}_confidence"] = ""
                cells_unknown += 1
            else:
                val, cf = derived[d]
                row[f"dim_{d}_value"] = val
                row[f"dim_{d}_source"] = "auto"
                row[f"dim_{d}_confidence"] = cf
                per_dim_values[d].add(val)
                cells_auto += 1
        results.append(row)

    # --- write fingerprint CSV ---
    fieldnames = ["dict"]
    for d in range(1, 31):
        fieldnames += [f"dim_{d}_value", f"dim_{d}_source", f"dim_{d}_confidence"]
    with open("data/L0/convention_fingerprint.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)

    # --- annotation_todo: every unknown cell ---
    todos = []
    for r in results:
        for d in range(1, 31):
            if r[f"dim_{d}_source"] == "unknown":
                todos.append({"dict": r["dict"], "dim_id": d,
                              "dim_name": DIMS[d - 1]["name"],
                              "options_available": "|".join(DIMS[d - 1]["options"])})
    with open("data/L0/annotation_todo.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dict", "dim_id", "dim_name", "options_available"])
        w.writeheader()
        w.writerows(todos)

    # --- variance check: flag any auto dim that is constant ---
    auto_dims = sorted(set(range(1, 31)) - ANNOTATION_ONLY)
    constants = []
    informative = []
    coverage = {}
    for d in auto_dims:
        vals = per_dim_values.get(d, set())
        filled = sum(1 for r in results if r[f"dim_{d}_source"] == "auto")
        coverage[d] = {"name": DIMS[d - 1]["name"], "dicts_filled": filled,
                       "distinct_values": sorted(vals)}
        if len(vals) <= 1:
            constants.append(d)
        else:
            informative.append(d)

    summary = {
        "total_cells": len(dicts) * 30,
        "cells_auto": cells_auto,
        "cells_unknown": cells_unknown,
        "fill_fraction": round(cells_auto / (len(dicts) * 30), 3),
        "dicts_total": len(dicts),
        "dicts_missing_source": missing_src,
        "auto_dims": auto_dims,
        "annotation_only_dims": sorted(ANNOTATION_ONLY),
        "informative_dims": informative,
        "constant_dims_flagged": constants,
        "per_dim_coverage": coverage,
        "cap_entries_per_dict": CAP,
    }
    with open("data/L0/fingerprint_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from _provenance import write_source
        write_source("data/L0/convention_fingerprint.csv", "s2_fingerprint.py", 2)
    except Exception as e:
        print(f"Provenance error: {e}")

    print(f"\ncells_total: {len(dicts) * 30}")
    print(f"cells_filled_auto: {cells_auto}  ({summary['fill_fraction']*100:.0f}%)")
    print(f"cells_unknown: {cells_unknown}")
    print(f"annotation_todo_rows: {len(todos)}")
    print(f"informative auto dims: {len(informative)}  {informative}")
    print(f"CONSTANT (flagged) auto dims: {len(constants)}  {constants}")
    print(f"missing-source dicts: {missing_src}")


if __name__ == "__main__":
    main()
