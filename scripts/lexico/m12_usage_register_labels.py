"""M12 — usage and register labels of the nine narrative dictionaries (H5333).

The cross-dictionary census of how each Cologne dict marks WHERE a word is used
(lexicographers-only, Vedic, post-Vedic, epic, classical, poetic, liturgical,
figurative, literal) and which middle-Indo-Aryan speech it is ascribed to
(Prākrit, Pāli, Apabhraṃśa). The lexicographers-only label has been studied for
MW alone; here every usage/register label is extracted per dictionary from the
tagged markup, normalised to ONE vocabulary, and the mapping table is published
with per-dictionary counts and rates.

WHAT IS COUNTED (all from the csl-orig record text — no semantic parsing):

1. TAGGED SURFACES. Two Cologne tags carry usage/register labels:
   - `<ab>…</ab>`  abbreviation runs — AP files `Ved.` here (1,915×), PWG files
     its LEXICOGRAPHERS-ONLY family here (`Lexicogrr.`/`Lexicogr.`/`Lexicc.`),
     MW files `poet.`/`fig.`/`lit.` here.
   - `<lang>…</lang>` language-tag runs — MW files `Ved.`/`ep.` here, PWG/PW
     file `ved.`/`klass.`/`nachved.` here. A `<lang>` token NOT in the mapping
     is a true language name (Gk., Lat., Mar., …) — counted per dict in the
     envelope under `language_name_tags`, never in the register table.
2. NORMALISATION. Raw → normalised label via the published mapping (exact
   string keys after trimming whitespace and stripping paired bracket
   punctuation `().,:;`); kind ∈ register | middle_indic. Unmapped tags are not
   registers and are excluded.
3. UNTAGGED RESIDUE. The same core tokens occurring as NET-untagged text —
   tag-stripped occurrences MINUS the tagged ones (MW writes `poet.` truly
   untagged 43× against 3 `<ab>poet.</ab>`; its `Ved.` is 99.8% tagged:
   613 stripped − 612 `<lang>` = 1) — reported per dict as `untagged_core`
   so the undercount of the tagged layer is quantified, not hidden. Residue is
   NOT added to the register rates.
4. RATES. Per dictionary: records (csl-orig `<L>` lines) as denominator; each
   normalised register label reported as count and per-1,000-records rate.

The four Sanskrit-medium dictionaries (SKD, VCP, ARMH, ABCH) carry no tagged
usage labels at all — a finding, not a bug: their markers live in Devanāgarī
prose, outside this tag census. Envelope pins the csl-orig commit.

Stdlib only; UTF-8, no BOM; deterministic (no timestamps, no set iteration into
output, no RNG).
Run from repo root:
    python scripts/lexico/m12_usage_register_labels.py
    python scripts/lexico/m12_usage_register_labels.py --dicts mw pwg
Outputs (data/lexico/):
    usage_register_labels.json          envelope + per-dict counts/rates
    usage_register_labels_map.csv       published mapping table
    usage_register_labels_counts.csv    dict × label × surface counts + rates
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter, OrderedDict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GH = os.path.abspath(os.path.join(ROOT, ".."))
CSL = os.path.join(GH, "csl-orig", "v02")
OUT_DIR = os.path.join(ROOT, "data", "lexico")

DICTS = ["mw", "pwg", "pw", "ap", "wil", "skd", "vcp", "armh", "abch"]
DICT_LABEL = {
    "mw": "MW", "pwg": "PWG", "pw": "PW (PWK)", "ap": "AP", "wil": "WIL",
    "skd": "SKD", "vcp": "VCP", "armh": "ARMH", "abch": "ABCH",
}

# ---------------------------------------------------------------- mapping -----------
# raw token (whitespace-trimmed, bracket punctuation stripped) -> (normalised label, kind)
MAPPING = OrderedDict([
    # chronological / genre register
    ("Ved",       ("VEDIC", "register")),
    ("ved",       ("VEDIC", "register")),
    ("nachved",   ("POST_VEDIC", "register")),
    ("ep",        ("EPIC", "register")),
    ("epic",      ("EPIC", "register")),
    ("klass",     ("CLASSICAL", "register")),
    ("poet",      ("POETIC", "register")),
    ("Lexicogrr", ("LEXICOGRAPHERS_ONLY", "register")),
    ("Lexicogr",  ("LEXICOGRAPHERS_ONLY", "register")),
    ("Lexicc",    ("LEXICOGRAPHERS_ONLY", "register")),
    ("lex",       ("LEXICOGRAPHERS_ONLY", "register")),   # bare text only (MW prose)
    ("liturg",    ("LITURGICAL", "register")),
    ("fig",       ("FIGURATIVE", "register")),
    ("Fig",       ("FIGURATIVE", "register")),
    ("lit",       ("LITERAL", "register")),
    ("Lit",       ("LITERAL", "register")),
    ("Litt",      ("LITERAL", "register")),
    ("liter",     ("LITERAL", "register")),
    # middle-Indo-Aryan ascription (usage domain, not genre register)
    ("Prākṛt",     ("PRAKRIT", "middle_indic")),
    ("Prākrit",    ("PRAKRIT", "middle_indic")),
    ("Pāli",       ("PALI", "middle_indic")),
    ("Apabhraṃśa", ("APABHRAMSA", "middle_indic")),
])

# core tokens tracked as bare (untagged) residue — exact regexes, word-bounded
BARE_TOKENS = OrderedDict([
    ("VEDIC", re.compile(r"\b[Vv]ed\.")),
    ("EPIC", re.compile(r"\b(?:ep\.|epic\.)")),
    ("POETIC", re.compile(r"\bpoet\.")),
    ("LEXICOGRAPHERS_ONLY", re.compile(r"\blex\.")),
])

AB_RE = re.compile(r"<ab>(.*?)</ab>", re.S)
LANG_RE = re.compile(r"<lang>(.*?)</lang>", re.S)
TAG_RE = re.compile(r"<[^>]+>")

LABEL_KIND = {}      # normalised label -> kind (middle_indic wins when shared by many raws)
for _raw, (_label, _kind) in MAPPING.items():
    LABEL_KIND.setdefault(_label, _kind)


def clean_token(raw):
    """Trim whitespace and paired bracket punctuation the digitisers leave behind."""
    return raw.strip().strip("().,:;").strip()


def normalize_token(raw):
    """raw string -> (normalised label, kind) or (None, None) when unmapped."""
    return MAPPING.get(clean_token(raw), (None, None))


def scan_line(line):
    """One record line -> (ab raw tokens, lang raw tokens), in text order."""
    return ([m.group(1) for m in AB_RE.finditer(line)],
            [m.group(1) for m in LANG_RE.finditer(line)])


def scan_bare(line):
    """One record line with tags stripped -> normalised bare-register tokens."""
    bare = TAG_RE.sub(" ", line)
    out = []
    for label, rx in BARE_TOKENS.items():
        n = len(rx.findall(bare))
        if n:
            out.extend([label] * n)
    return out


def census_records(lines):
    """Aggregate one dictionary: counts per surface and normalised label."""
    tagged = {}   # label -> {"ab": n, "lang": n}
    for ab, lang in (scan_line(ln) for ln in lines):
        for raw in ab:
            label, kind = normalize_token(raw)
            if label:
                slot = tagged.setdefault(label, {"ab": 0, "lang": 0})
                slot["ab"] += 1
        for raw in lang:
            label, kind = normalize_token(raw)
            if label:
                slot = tagged.setdefault(label, {"ab": 0, "lang": 0})
                slot["lang"] += 1
    bare = Counter(tok for ln in lines for tok in scan_bare(ln))
    return tagged, bare


def csl_orig_commit(csl=CSL):
    try:
        return subprocess.run(["git", "-C", os.path.dirname(csl), "rev-parse", "HEAD"],
                              capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
    except Exception:
        return None


def run_dict(code, csl=CSL):
    path = os.path.join(csl, code, f"{code}.txt")
    records = 0
    lang_names = Counter()
    with open(path, encoding="utf-8") as fh:
        lines = []
        for ln in fh:
            if ln.startswith("<L>"):
                records += 1
            lines.append(ln)
    tagged, bare = census_records(lines)
    # NET untagged residue: tag-stripped text still shows tagged labels, so the
    # truly-untagged count is bare minus tagged (MW `poet.`: 46 bare − 3 <ab> = 43).
    tagged_totals = {lb: s["ab"] + s["lang"] for lb, s in tagged.items()}
    residue = OrderedDict(sorted(
        (lb, n - tagged_totals.get(lb, 0)) for lb, n in bare.items()
        if n - tagged_totals.get(lb, 0) > 0))
    for ln in lines:
        for raw in LANG_RE.findall(ln):
            label, _ = normalize_token(raw)
            if not label:
                lang_names[clean_token(raw)] += 1
    return OrderedDict([
        ("dict", code), ("label", DICT_LABEL[code]), ("records", records),
        ("tagged", OrderedDict(sorted(tagged.items()))),
        ("untagged_core", residue),
        ("language_name_tags", sum(lang_names.values())),
        ("language_name_top", OrderedDict(lang_names.most_common(5))),
    ])


def mapping_rows(csl=CSL, dicts=None):
    """Published mapping table: raw token × surface × dict provenance, recomputed live."""
    dicts = dicts or DICTS
    rows = []
    seen = OrderedDict()
    for code in dicts:
        path = os.path.join(csl, code, f"{code}.txt")
        with open(path, encoding="utf-8") as fh:
            for ab, lang in (scan_line(ln) for ln in fh):
                for raw, surface in ([(r, "ab") for r in ab] + [(r, "lang") for r in lang]):
                    label, kind = normalize_token(raw)
                    if not label:
                        continue
                    key = (label, kind, clean_token(raw), surface)
                    cell = seen.setdefault(key, {"total": 0, "dicts": set()})
                    cell["total"] += 1
                    cell["dicts"].add(code)
    for (label, kind, raw, surface), cell in seen.items():
        rows.append(OrderedDict([
            ("normalized", label), ("kind", kind), ("raw", raw), ("surface", surface),
            ("dicts", ",".join(sorted(cell["dicts"]))), ("total", cell["total"]),
        ]))
    rows.sort(key=lambda r: (r["normalized"], r["raw"], r["surface"]))
    return rows


def build_envelope(per_dict):
    totals = OrderedDict()
    for d in per_dict:
        for label, slots in d["tagged"].items():
            t = totals.setdefault(label, 0) + slots["ab"] + slots["lang"]
            totals[label] = t
    return OrderedDict([
        ("schema", "csl-atlas/usage-register-labels/1.0"),
        ("generatedBy", "scripts/lexico/m12_usage_register_labels.py"),
        ("cslOrigCommit", csl_orig_commit()),
        ("sourceFiles", [f"csl-orig/v02/{c}/{c}.txt" for c in DICTS]),
        ("mapping", OrderedDict(
            (label, {"kind": kind, "rawTokens": [k for k, v in MAPPING.items() if v[0] == label]})
            for label, kind in sorted({v for v in MAPPING.values()})
        )),
        ("totalsByLabel", OrderedDict(sorted(totals.items()))),
        ("notes", [
            "Register/usage labels counted from the tagged markup only (<ab>, <lang>); "
            "untagged_core is the NET untagged residue (tag-stripped occurrences minus tagged) "
            "per dict, excluded from rates.",
            "A <lang> token absent from the mapping is a true language name (Gk., Lat., …); "
            "these are envelope counts (language_name_tags), never register rows.",
            "SKD/VCP/ARMH/ABCH carry no tagged usage labels — their markers are Devanāgarī prose, "
            "outside this tag census; zeros are findings, not defects.",
            "Rate denominator = csl-orig <L> records per dict.",
        ]),
        ("perDict", per_dict),
    ])


def write_outputs(env, mrows, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "usage_register_labels.json"), "w", encoding="utf-8") as fh:
        json.dump(env, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with open(os.path.join(out_dir, "usage_register_labels_map.csv"), "w",
              encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["normalized", "kind", "raw", "surface", "dicts", "total"])
        w.writeheader()
        w.writerows(mrows)
    with open(os.path.join(out_dir, "usage_register_labels_counts.csv"), "w",
              encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["dict", "label", "records", "normalized", "kind", "ab", "lang",
                    "total", "rate_per_1000_records"])
        for d in env["perDict"]:
            for label, slots in d["tagged"].items():
                total = slots["ab"] + slots["lang"]
                kind = LABEL_KIND[label]
                rate = round(total * 1000.0 / d["records"], 2) if d["records"] else 0.0
                w.writerow([d["dict"], d["label"], d["records"], label, kind,
                            slots["ab"], slots["lang"], total, rate])


def main(argv=None):
    ap = argparse.ArgumentParser(description="M12 usage/register-label census (H5333)")
    ap.add_argument("--dicts", nargs="+", default=DICTS, choices=DICTS)
    ap.add_argument("--csl", default=CSL)
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args(argv)

    run_dicts = args.dicts
    per_dict = [run_dict(c, csl=args.csl) for c in run_dicts]
    env = build_envelope(per_dict)
    mrows = mapping_rows(csl=args.csl, dicts=run_dicts)

    write_outputs(env, mrows, args.out)
    for d in per_dict:
        n = sum(s["ab"] + s["lang"] for s in d["tagged"].values())
        print(f"{d['label']:>9}: records={d['records']:>7}  tagged_labels={n:>6}  "
              f"untagged_core={sum(d['untagged_core'].values()):>4}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
