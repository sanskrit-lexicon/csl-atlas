"""M12 — lemmatisation policy census of the seven narrative dictionaries (H5332, epic E014).

M1 and M2 measured headword PROMOTION (what gets a subentry, what a preverb does to the
macrostructure) but never asked the prior question: *what counts as a lemma at all?* A
dictionary must decide, for every word class, which of a paradigm's forms is the one that
carries the entry — the verbal root or a finite form, the nominal stem or its nominative
citation form, the compound as its own head or as a run-on under its first member, the
derivative as its own head or inside its base's nest. Those four decisions are this
dictionary's lemmatisation policy, and each of MW, PWG, PW (PWK), AP, WIL, SKD and VCP
answers them differently. The versified kośas (ARMH/ABCH) are excluded: they are
concept-ordered verse, with no headword layer to lemmatise (M6 measures them).

WHAT IS MEASURED (from the `<L>` header lines, plus the first body line for AP's root mark):

1. NOMINAL STEMS — the citation-shape test. The distribution of `k1` finals over the
   primary view: final `H` (visarga — a nominative singular *akṣaraḥ*), final `M`
   (*akṣaraṃ*, a neuter nominative), vowel-final, consonant-final. A dictionary whose
   headwords carry inflectional endings is keying CITATION FORMS; one whose headwords end
   in the bare stem is keying STEMS. The verdict is the majority shape, with the minority
   listed as the exception class.

2. VERBS — the Whitney spine test. Whitney's *Roots, Verb-forms and Primary Derivatives*
   (1885) gives 938 roots; they are read in IAST, transliterated to SLP1 and looked up in
   each dictionary in four ways:
   - `root_exact`    — a headword whose `k1` IS the root (root-form lemmatisation);
   - `finite_form`   — no exact root entry, but a headword equal to the root plus a present
     ending (`ti te ati ate anti ante yati yate`) — the dictionary lemmatises a finite form.
     This is a LOWER BOUND: it recognises thematic forms only, not guṇa/vṛddhi grades
     (*bhū* → *bhavati* is not caught), and that limit is stated in the report;
   - `derived_only`  — no exact root entry and no finite form, but ≥ 1 headword that extends
     the root (participles, action nouns, agent nouns);
   - `absent`        — the root has no headword of any of those shapes.
   Roots shorter than two characters are dropped (nothing can be tested on them).

3. COMPOUNDS — the own-head vs run-on test. A headword is COMPOUND-LIKE when its `k1`
   splits into two pieces that are BOTH headwords of the same dictionary, each ≥ 3
   characters (a self-referential test: it uses no external word list, so it measures the
   dictionary against its own macrostructure). Each compound-like headword is then scored
   as its own level-1 entry or as a nested sub-record (`<e>` level ≥ 2). The nesting share
   is the policy.

4. DERIVATIVES — the suffix test. A headword is DERIVATIVE-LIKE when it ends in one of
   fifteen frequent kṛt/taddhita suffixes AND the remainder is itself a headword of the
   same dictionary (again self-referential). Scored own-entry vs nested, with the suffix
   profile.

5. THE DCS SPINE, STRATIFIED. Every lemma of the DCS lemma summary (83,239, Hellwig's
   ~2021 snapshot) carries a frequency band 1 (hapax) … 5 (very common). Per dictionary and
   per band: the share lemmatised as an exact headword, the share reachable only through a
   citation-form key (lemma + `H`/`M`), and the share absent. The bands ARE the strata —
   coverage of a hapax and of a very common lemma are different questions, and a single
   overall coverage number hides the difference. A deterministic per-band sample of the
   absent lemmas is written to the exceptions CSV.

Every verdict is a THRESHOLD over a measured rate, never a judgement: the thresholds are
named in `policy_thresholds` in the JSON envelope and repeated in the report.

Stdlib only; UTF-8, no BOM; deterministic (no RNG, no set iterated into output).
Run from repo root:
    python scripts/lexico/m12_lemmatisation_policy.py
    python scripts/lexico/m12_lemmatisation_policy.py --dicts wil skd
Outputs (data/lexico/):
    lemmatisation_policy.json            envelope: per-dict policy per word class + counts
    lemmatisation_policy_classes.csv     dict × word class × measure table
    lemmatisation_policy_exceptions.csv  the exception rows (absent roots, off-policy
                                         headwords, absent DCS lemmas by band)
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
WHITNEY = os.path.join(GH, "WhitneyRoots", "Whitney_roots_class-PP.txt")
DCS_SUMMARY = os.path.join(ROOT, "data", "dcs", "dcs_lemma_summary.json")
OUT_DIR = os.path.join(ROOT, "data", "lexico")

DICTS = ["mw", "pwg", "pw", "ap", "wil", "skd", "vcp"]
DICT_LABEL = {"mw": "MW", "pwg": "PWG", "pw": "PW (PWK)", "ap": "AP", "wil": "WIL",
              "skd": "SKD", "vcp": "VCP"}

# Verdict thresholds — stated, not tuned per dictionary.
THRESH = OrderedDict([
    ("citation_form_min", 0.20),      # ≥ 20 % of headwords inflected ⇒ citation-form keys
    ("citation_form_mixed", 0.02),    # 2–20 % ⇒ mixed, below 2 % ⇒ stem keys
    ("root_form_min", 0.60),          # ≥ 60 % of Whitney roots as exact headwords ⇒ root-form
    ("root_form_partial", 0.20),      # 20–60 % ⇒ partial
    ("nesting_min", 0.50),            # ≥ 50 % of the class nested ⇒ run-on policy
    ("nesting_mixed", 0.05),          # 5–50 % ⇒ mixed, below 5 % ⇒ own-head policy
])

PRESENT_ENDINGS = ("ti", "te", "ati", "ate", "anti", "ante", "yati", "yate")
# Frequent kṛt / taddhita suffixes in SLP1, longest first so the profile is unambiguous.
SUFFIXES = ("tva", "tA", "tara", "tama", "maya", "aka", "ana", "ita", "in", "mat",
            "vat", "tf", "tas", "ya", "ka")
MIN_PIECE = 3          # shortest member of a compound split
MIN_ROOT = 2           # shortest testable Whitney root
SAMPLE = 25            # exception rows per (dict × class) or (dict × band)

_LID = re.compile(r"^<L>(\S+)")
_ATTR = re.compile(r"<(\w+)>([^<]*)")
ROOT_MARK = {"ap": re.compile(r"¦\s*€\d")}

# ------------------------------------------------------------- transliteration ---------

IAST_SLP1 = [
    ("ā", "A"), ("ī", "I"), ("ū", "U"), ("ṝ", "F"), ("ṛ", "f"), ("ḹ", "X"), ("ḷ", "x"),
    ("kh", "K"), ("gh", "G"), ("ch", "C"), ("jh", "J"), ("ṭh", "W"), ("ḍh", "Q"),
    ("th", "T"), ("dh", "D"), ("ph", "P"), ("bh", "B"),
    ("ṭ", "w"), ("ḍ", "q"), ("ṅ", "N"), ("ñ", "Y"), ("ṇ", "R"), ("ś", "S"), ("ṣ", "z"),
    ("ṃ", "M"), ("ḥ", "H"), ("ḻ", "L"),
]
SLP1_IAST = {
    "A": "ā", "I": "ī", "U": "ū", "f": "ṛ", "F": "ṝ", "x": "ḷ", "X": "ḹ",
    "K": "kh", "G": "gh", "C": "ch", "J": "jh", "W": "ṭh", "Q": "ḍh", "T": "th",
    "D": "dh", "P": "ph", "B": "bh", "w": "ṭ", "q": "ḍ", "N": "ṅ", "Y": "ñ", "R": "ṇ",
    "S": "ś", "z": "ṣ", "M": "ṃ", "H": "ḥ", "L": "ḻ", "~": "m̐",
}


def iast_to_slp1(text):
    """IAST → SLP1, longest match first (aspirates before their plain consonants)."""
    out = []
    i = 0
    low = text
    while i < len(low):
        for src, dst in IAST_SLP1:
            if low.startswith(src, i):
                out.append(dst)
                i += len(src)
                break
        else:
            out.append(low[i])
            i += 1
    return "".join(out)


def slp1_to_iast(text):
    return "".join(SLP1_IAST.get(c, c) for c in text or "")


# ------------------------------------------------------------------- sources -----------

def read_records(code, csl=CSL):
    """Header records in file order: L, pc, k1, e, alias, root (same shape as M11)."""
    path = os.path.join(csl, code, f"{code}.txt")
    root_re = ROOT_MARK.get(code)
    recs = []
    cur = None
    first_body = False
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("<L>"):
                m = _LID.match(line)
                attrs = dict(_ATTR.findall(line))
                cur = {"L": m.group(1) if m else "", "pc": attrs.get("pc", ""),
                       "k1": attrs.get("k1", ""), "e": attrs.get("e", "").strip(),
                       "alias": False, "root": False}
                recs.append(cur)
                first_body = True
            elif cur is not None and first_body:
                if line.startswith("{{Lbody="):
                    cur["alias"] = True
                if root_re is not None and root_re.search(line):
                    cur["root"] = True
                first_body = False
            if line.startswith("<LEND>"):
                cur = None
    return recs


def e_level(e):
    m = re.match(r"(\d+)", e or "")
    return int(m.group(1)) if m else 1


def whitney_roots(path=WHITNEY):
    """The Whitney root spine as SLP1, in file order, deduplicated (homonyms collapse)."""
    if not os.path.exists(path):
        return []
    line_re = re.compile(r"^\s*\d+\.\s+(?:\d+\s+)?√?\s*([^\s]+)")
    seen, out = set(), []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = line_re.match(line)
            if not m:
                continue
            slp = iast_to_slp1(m.group(1).strip("√ "))
            if len(slp) < MIN_ROOT or not slp.isascii() or slp in seen:
                continue
            seen.add(slp)
            out.append(slp)
    return out


def dcs_lemmas(path=DCS_SUMMARY):
    """DCS lemma spine → {lemma: band}. Empty when the summary is not synced."""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        blob = json.load(f)
    return {k: v.get("freqBand") for k, v in (blob.get("lemmas") or {}).items()}


def csl_orig_commit(csl=CSL):
    try:
        out = subprocess.run(["git", "-C", os.path.dirname(csl), "rev-parse", "HEAD"],
                             capture_output=True, text=True, encoding="utf-8", timeout=30)
        return out.stdout.strip()[:8] if out.returncode == 0 else ""
    except Exception:
        return ""


# ------------------------------------------------------------------ measures -----------

def rate(a, b):
    return round(a / b, 6) if b else None


def final_shape(k1):
    if not k1:
        return "empty"
    last = k1[-1]
    if last == "H":
        return "visarga"
    if last in "M~":
        return "anusvara"
    if last in "aAiIuUfFxXeoE O".replace(" ", ""):
        return "vowel"
    return "consonant"


def citation_policy(recs):
    """Word class 1 — nominal stems: are the keys stems or inflected citation forms?"""
    shapes = Counter(final_shape(r["k1"]) for r in recs)
    total = sum(shapes.values())
    inflected = shapes["visarga"] + shapes["anusvara"]
    share = rate(inflected, total) or 0.0
    if share >= THRESH["citation_form_min"]:
        verdict = "citation form (inflected nominative keys)"
        off = [r for r in recs if final_shape(r["k1"]) in ("vowel", "consonant")]
    elif share >= THRESH["citation_form_mixed"]:
        verdict = "mixed — stem keys with a citation-form minority"
        off = [r for r in recs if final_shape(r["k1"]) in ("visarga", "anusvara")]
    else:
        verdict = "stem (uninflected keys)"
        off = [r for r in recs if final_shape(r["k1"]) in ("visarga", "anusvara")]
    return {
        "verdict": verdict,
        "headwords": total,
        "shapes": OrderedDict((k, shapes[k]) for k in
                              ("vowel", "consonant", "visarga", "anusvara", "empty")),
        "inflected_share": share,
        "exception_count": len(off),
    }, off


def verb_policy(keys, prefix_index, roots, root_marked):
    """Word class 2 — verbs: root form, finite form, derivative only, or absent."""
    buckets = OrderedDict((k, []) for k in
                          ("root_exact", "citation_root", "finite_form", "derived_only",
                           "absent"))
    finite_examples = []
    for r in roots:
        if r in keys:
            buckets["root_exact"].append(r)
            continue
        if (r + "H") in keys or (r + "M") in keys:
            buckets["citation_root"].append(r)
            continue
        hit = next((r + e for e in PRESENT_ENDINGS if (r + e) in keys), None)
        if hit:
            buckets["finite_form"].append(r)
            if len(finite_examples) < SAMPLE:
                finite_examples.append({"root": r, "headword": hit})
            continue
        if prefix_index.get(r[:MIN_ROOT]) and any(
                k.startswith(r) and k != r for k in prefix_index[r[:MIN_ROOT]]):
            buckets["derived_only"].append(r)
            continue
        buckets["absent"].append(r)
    total = len(roots)
    exact = rate(len(buckets["root_exact"]), total) or 0.0
    cited = rate(len(buckets["citation_root"]), total) or 0.0
    if exact >= THRESH["root_form_min"]:
        verdict = "root form (the bare dhātu is the headword)"
    elif cited >= THRESH["root_form_partial"]:
        verdict = "citation-form root (the dhātu carries a nominative ending)"
    elif exact >= THRESH["root_form_partial"]:
        verdict = "partial root form — a minority of roots carries its own headword"
    else:
        verdict = "marginal root layer — most roots are reached only through derivatives"
    return {
        "verdict": verdict,
        "whitney_roots_tested": total,
        "counts": OrderedDict((k, len(v)) for k, v in buckets.items()),
        "root_exact_share": exact,
        "citation_root_share": cited,
        "root_marked_records": root_marked,
        "finite_form_examples": finite_examples,
    }, buckets


def split_policy(recs, keys, kind):
    """Word classes 3 and 4 — compounds and derivatives: own head or nested run-on?

    `kind` is "compound" (k1 splits into two headwords) or "derivative" (k1 = headword +
    a listed suffix). Both tests are self-referential: the dictionary's own key set is the
    only word list used.
    """
    own, nested, profile = [], [], Counter()
    for r in recs:
        k = r["k1"]
        piece = None
        if kind == "compound":
            for i in range(MIN_PIECE, len(k) - MIN_PIECE + 1):
                if k[:i] in keys and k[i:] in keys:
                    piece = k[:i]
                    break
        else:
            for suf in SUFFIXES:
                if len(k) > len(suf) + MIN_PIECE - 1 and k.endswith(suf) \
                        and k[:-len(suf)] in keys:
                    piece = suf
                    break
        if piece is None:
            continue
        profile[piece if kind == "derivative" else "split"] += 1
        (nested if e_level(r["e"]) >= 2 else own).append(r)
    found = len(own) + len(nested)
    share = rate(len(nested), found) or 0.0
    label = "compounds" if kind == "compound" else "derivatives"
    recorded = any(e_level(r["e"]) >= 2 for r in recs)
    if not recorded:
        verdict = (f"own head — every {label[:-1]} is a level-1 entry; csl-orig records "
                   f"no nesting level for this dictionary, so a printed run-on would not "
                   f"be visible here")
    elif share >= THRESH["nesting_min"]:
        verdict = f"nested — most {label} are run-ons inside another entry"
    elif share >= THRESH["nesting_mixed"]:
        verdict = f"mixed — {label} appear both as own heads and as run-ons"
    else:
        verdict = f"own head — {label} get their own entry"
    out = {
        "verdict": verdict,
        "nesting_recorded": recorded,
        "detected": found,
        "own_head": len(own),
        "nested": len(nested),
        "nested_share": share,
        "detected_share_of_records": rate(found, len(recs)),
    }
    if kind == "derivative":
        out["suffix_profile"] = OrderedDict(
            (slp1_to_iast(s), profile[s]) for s in SUFFIXES if profile[s])
    # The exception class is the minority side of the verdict.
    off = own if share >= THRESH["nesting_min"] else nested
    return out, off


def dcs_policy(keys, lemmas):
    """The stratified spine tie — coverage per DCS frequency band."""
    bands = OrderedDict((b, {"lemmas": 0, "exact": 0, "citation_only": 0, "absent": 0})
                        for b in (1, 2, 3, 4, 5))
    missing = OrderedDict((b, []) for b in (1, 2, 3, 4, 5))
    for lemma in sorted(lemmas):
        b = lemmas[lemma]
        if b not in bands:
            continue
        bands[b]["lemmas"] += 1
        if lemma in keys:
            bands[b]["exact"] += 1
        elif (lemma + "H") in keys or (lemma + "M") in keys:
            bands[b]["citation_only"] += 1
        else:
            bands[b]["absent"] += 1
            if len(missing[b]) < SAMPLE:
                missing[b].append(lemma)
    for b, row in bands.items():
        row["exact_share"] = rate(row["exact"], row["lemmas"])
        row["covered_share"] = rate(row["exact"] + row["citation_only"], row["lemmas"])
    total = sum(r["lemmas"] for r in bands.values())
    covered = sum(r["exact"] + r["citation_only"] for r in bands.values())
    return {"bands": bands, "lemmas": total, "covered": covered,
            "covered_share": rate(covered, total)}, missing


# --------------------------------------------------------------------- driver ----------

def run_dict(code, class_rows, exc_rows, roots, lemmas, csl=CSL):
    recs = read_records(code, csl=csl)
    printed = [r for r in recs if not r["alias"]]
    level1 = [r for r in printed if e_level(r["e"]) == 1]
    keys = {r["k1"] for r in printed if r["k1"]}
    prefix_index = {}
    for k in keys:
        prefix_index.setdefault(k[:MIN_ROOT], []).append(k)
    root_marked = sum(1 for r in printed if r["root"])

    nominal, nominal_off = citation_policy(level1)
    verbs, verb_buckets = verb_policy(keys, prefix_index, roots, root_marked)
    compounds, comp_off = split_policy(printed, keys, "compound")
    derivatives, deriv_off = split_policy(printed, keys, "derivative")
    spine, spine_missing = dcs_policy(keys, lemmas)

    label = DICT_LABEL[code]
    for cls, block, extra in (
            ("nominal_stems", nominal, {"measure": "inflected_share"}),
            ("verbs", verbs, {"measure": "root_exact_share"}),
            ("compounds", compounds, {"measure": "nested_share"}),
            ("derivatives", derivatives, {"measure": "nested_share"})):
        class_rows.append({
            "dict": label, "word_class": cls, "verdict": block["verdict"],
            "measure": extra["measure"], "value": block.get(extra["measure"]),
            "counted": block.get("headwords") or block.get("whitney_roots_tested")
                       or block.get("detected"),
            "exceptions": block.get("exception_count")
                          if cls == "nominal_stems"
                          else (block["counts"]["absent"] if cls == "verbs"
                                else min(block["own_head"], block["nested"])),
        })

    for r in nominal_off[:SAMPLE]:
        exc_rows.append({"dict": label, "word_class": "nominal_stems",
                         "exception": "off-policy key shape", "key": r["k1"],
                         "iast": slp1_to_iast(r["k1"]), "L": r["L"], "page": r["pc"]})
    for r in verb_buckets["absent"][:SAMPLE]:
        exc_rows.append({"dict": label, "word_class": "verbs",
                         "exception": "Whitney root with no headword of any shape",
                         "key": r, "iast": slp1_to_iast(r), "L": "", "page": ""})
    for cls, off in (("compounds", comp_off), ("derivatives", deriv_off)):
        for r in off[:SAMPLE]:
            exc_rows.append({"dict": label, "word_class": cls,
                             "exception": "minority side of the nesting verdict",
                             "key": r["k1"], "iast": slp1_to_iast(r["k1"]),
                             "L": r["L"], "page": r["pc"]})
    for b, lemmata in spine_missing.items():
        for lemma in lemmata:
            exc_rows.append({"dict": label, "word_class": f"dcs_band_{b}",
                             "exception": "DCS lemma absent from the headword list",
                             "key": lemma, "iast": slp1_to_iast(lemma), "L": "", "page": ""})

    return OrderedDict([
        ("dict", label),
        ("records", len(recs)),
        ("printed_records", len(printed)),
        ("level1_records", len(level1)),
        ("distinct_keys", len(keys)),
        ("nominal_stems", nominal),
        ("verbs", verbs),
        ("compounds", compounds),
        ("derivatives", derivatives),
        ("dcs_spine", spine),
    ])


def main(argv=None):
    ap = argparse.ArgumentParser(description="M12 lemmatisation policy census")
    ap.add_argument("--dicts", nargs="*", default=DICTS)
    ap.add_argument("--csl", default=CSL)
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args(argv)

    roots = whitney_roots()
    lemmas = dcs_lemmas()
    if not roots:
        print(f"WARN: Whitney spine not found at {WHITNEY} — verb census will be empty",
              file=sys.stderr)
    if not lemmas:
        print(f"WARN: DCS summary not found at {DCS_SUMMARY} — spine tie will be empty",
              file=sys.stderr)

    class_rows, exc_rows, per_dict = [], [], OrderedDict()
    for code in args.dicts:
        print(f"[m12] {DICT_LABEL.get(code, code)} …", file=sys.stderr)
        per_dict[code] = run_dict(code, class_rows, exc_rows, roots, lemmas, csl=args.csl)

    os.makedirs(args.out, exist_ok=True)
    envelope = OrderedDict([
        ("generator", "scripts/lexico/m12_lemmatisation_policy.py"),
        ("handoff", "H5332"),
        ("epic", "E014"),
        ("csl_orig_commit", csl_orig_commit(args.csl)),
        ("whitney_roots", len(roots)),
        ("dcs_lemmas", len(lemmas)),
        ("policy_thresholds", THRESH),
        ("present_endings_tested", list(PRESENT_ENDINGS)),
        ("suffixes_tested", [slp1_to_iast(s) for s in SUFFIXES]),
        ("dicts", per_dict),
    ])
    with open(os.path.join(args.out, "lemmatisation_policy.json"), "w",
              encoding="utf-8", newline="\n") as f:
        json.dump(envelope, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(os.path.join(args.out, "lemmatisation_policy_classes.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dict", "word_class", "verdict", "measure",
                                          "value", "counted", "exceptions"])
        w.writeheader()
        w.writerows(class_rows)
    with open(os.path.join(args.out, "lemmatisation_policy_exceptions.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dict", "word_class", "exception", "key",
                                          "iast", "L", "page"])
        w.writeheader()
        w.writerows(exc_rows)

    for row in class_rows:
        print(f"{row['dict']:<9} {row['word_class']:<14} {row['value']} — {row['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
