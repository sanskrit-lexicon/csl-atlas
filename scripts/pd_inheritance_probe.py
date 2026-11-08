#!/usr/bin/env python3
"""H6948 — PD silent inheritance: macro inventory + micro citation/gloss overlap,
calibrated on the bracket-marked class.

The question
------------
PD marks only 1.67 % of its letter-*a* entries with a bracketed source from an
earlier dictionary (H6942 / PD_PREFACE_MEASUREMENTS_2026-10-18 M1). The mark is
the *only* machine-visible trace of inheritance: a headword or sense taken over
silently leaves nothing. So the 1.67 % is a floor whose ceiling is unknown.

This probe asks two questions the floor cannot answer on its own:

  MACRO — how much of PD's letter-*a* inventory is even *shared* with PWG / MW,
          and what share of the PD-only headwords has no corpus attestation
          (DCS 2021)? An inventory that is mostly PD-only and unattested is an
          encyclopaedic dictionary building its own material, not a copy.

  MICRO — for headwords PD shares with PWG / MW, do PD's *citation sets* and
          *gloss strings* look like the earlier dictionary's (Jaccard, and the
          share where PD's mapped citations are a strict subset of PWG's)?

  CALIBRATION — the same micro metrics computed separately on the entries PD
          itself marks as inherited and on the ones it does not. If the marked
          class does not beat the unmarked class, the bracket convention is not
          a proxy for inheritance and the 1.67 % is uninterpretable as a
          ranking; the memo must say so.

DECISION RULE (written before the run; both sides must hold for the bracket)
  D1  citation subsumption lift: p_subset(marked) − p_subset(unmarked) >= 10
      percentage points with the 95 % bootstrap CI excluding 0.
  D2  gloss overlap lift: median Jaccard(PD,PWG) marked − unmarked >= 0.02 with
      the 95 % bootstrap CI excluding 0 (or the PD–MW pair, same thresholds).
  Bracket proxy SURVIVES only if D1 holds and D2 holds for at least one target
  dictionary. If D1 fails, the memo says the bracket is not a proxy — whatever
  D2 does.
  Every micro metric is also reported against a SHUFFLED NULL (PD headword
  paired with a different, same-size-class headword of the same target
  dictionary, seeded). A metric with no lift over its own null is not evidence,
  whatever its absolute value.

Citation sets are compared on the SHARED ABBREVIATION VOCABULARY only
(abbreviation keys present in both dictionaries' citation vocabularies after the
house nfold fold). The share of PD citation mass that the shared vocabulary can
express is reported as `mappable_share`; a low share caps what the metric can
say and must travel with every Jaccard figure.

Boundaries — model/machine output is review EVIDENCE, never an input to a
published metric. This script reads read-only dictionary texts, writes
data/pd/*.tsv and data/pd/*.json only, and never touches a dictionary source.
No claim of "inheritance": only "marked inheritance" and "measurable overlap".

Inputs (pinned by SHA-256 in the output JSON)
  PD_TXT    Cologne PDScan 2020 txt/pd.txt        (H6942 control, 55,122,076 B)
  PWG_TXT   csl-orig v02/pwg/pwg.txt
  MW_TXT    csl-orig v02/mw/mw.txt
  DCS_LEMMA data/dcs/dcs_lemma_summary.json       (DCS 2021 lemma bands)
  PD_SIGLA  data/pd/pd_siglum_families.tsv        (curated PD siglum vocabulary)

Usage
  python3 scripts/pd_inheritance_probe.py                 # measure + write
  python3 scripts/pd_inheritance_probe.py --limit 3000    # quick partial run
  python3 scripts/pd_inheritance_probe.py --no-write      # measure, print only
"""

import argparse
import hashlib
import json
import os
import random
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path.home() / "Documents" / "GitHub" / "sanskrit-util" / "py"))
from sanskrit_util import norm, slp1_form_key

RNG_SEED = 20261018
BOOTSTRAPS = 2000

# PD text is external and read-only (Cologne PDScan 2020 archive, unpacked
# txt/pd.txt). Point PD_TXT at it, or pass --pd.
DEFAULT_PD = Path(os.environ.get("PD_TXT", str(Path.home() / "Documents" / "pd" / "txt" / "pd.txt")))
DEFAULT_PWG = Path.home() / "Documents" / "GitHub" / "csl-orig" / "v02" / "pwg" / "pwg.txt"
DEFAULT_MW = Path.home() / "Documents" / "GitHub" / "csl-orig" / "v02" / "mw" / "mw.txt"

# ---- markup ----------------------------------------------------------------

RE_SLP1 = re.compile(r"\{#.*?#\}", re.DOTALL)      # {#…#}  Sanskrit payload
RE_ITAL = re.compile(r"\{%.*?%\}", re.DOTALL)      # {%…%}  italic gloss
RE_TAG = re.compile(r"<[^>]*>")
RE_BRACKET = re.compile(r"\[[^\]\n]{0,80}\]")
RE_SIGLUM = re.compile(r"([^\W\d_][^\W\d_]*)\.(\([^)]*\))?")
RE_LS = re.compile(r"<ls([^>]*)>(.*?)</ls>", re.DOTALL)
RE_RECORD = re.compile(r"<L>(.*?)<LEND>", re.DOTALL)
RE_K1 = re.compile(r"<k1>(.*?)<k2>", re.DOTALL)
RE_NUM = re.compile(r"^\s*(\d+)")

# dictionary-source marks inside PD brackets (H6942 §M1 vocabulary + observed
# orthographic variants: DBHS/DBHS., PW/pw/PW., APTE/APTE., MW/MW., VIŚVA/VIŚVA.,
# nt/nt./NT., vāc/Vācas./Vācs.)
_NO_L = r"(?![^\W\d_])"
_NO_P = r"(?<![^\W\d_])"
MARKS = {
    "DBHS": re.compile(_NO_P + r"DBHS\.?"),
    "PW": re.compile(_NO_P + r"(?:PW|pw|Pw)\.?" + _NO_L),
    "APTE": re.compile(_NO_P + r"(?:APTE|Apte|apte)\.?" + _NO_L),
    "MW": re.compile(_NO_P + r"(?:MW|Mw|mw)\.?" + _NO_L),
    "VIŚVA": re.compile(_NO_P + r"(?:VIŚVA|Viśva|viśva|VISVA|Visva|visva)\.?"),
    "NT": re.compile(_NO_P + r"(?:nt|NT|Nt)\.?" + _NO_L),
    "VĀC": re.compile(_NO_P + r"(?:vāc|VĀC|Vāc|vac|Vācas|Vācs)\.?" + _NO_L),
}

# tokens dropped from gloss comparison — function words of the two gloss
# languages (English for PD/MW, German for PWG). Applied symmetrically, so the
# floor they remove is removed from both sides and the shuffled null absorbs
# what is left.
STOP = set(["the", "and", "for", "with", "from", "that", "this", "these", "those", "into", "upon", "which", "whose", "whom", "what", "when", "where", "while", "than", "then", "also", "only", "very", "such", "some", "any", "all", "one", "two", "three", "not", "but", "are", "was", "were", "been", "being", "have", "has", "had", "having", "other", "others", "same", "after", "before", "under", "over", "about", "above", "below", "between", "during", "through", "auch", "aber", "oder", "wenn", "dann", "als", "wie", "ist", "sind", "war", "waren", "wird", "werden", "wurde", "wurden", "nicht", "nur", "noch", "schon", "sehr", "eine", "einer", "eines", "einem", "einen", "der", "die", "das", "den", "dem", "des", "mit", "von", "zu", "zum", "zur", "auf", "aus", "bei", "nach", "über", "unter", "vor", "für", "gegen", "ohne"])


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


ROMAN = set(["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii", "xiii", "xiv", "xv", "xx"])


def cite_key(token: str) -> str:
    """Abbreviation key: drop a parenthetical qualifier, fold diacritics, lower.

    `MahāBhā.` -> `mahabha`, `MBH.` -> `mbh`, `ṚV.` -> `rv`. `norm` (NFD, strip
    combining marks, lowercase) is used rather than `nfold`: the nasal fold would
    merge `MED.` with `NED.` and is not wanted for abbreviation identity. Roman
    numerals (`iv.` after a work's title) are rejected — they are loci, not works.
    """
    token = re.sub(r"\([^)]*\)", "", token).strip().strip(".,;:")
    key = norm(token).strip(".,;:")
    if key in ROMAN:
        return ""
    return key


# ---- entry parsing ---------------------------------------------------------

def parse_records(text: str):
    """Yield (num, pc, k1, body) for every <L>…<LEND> record."""
    for raw in RE_RECORD.findall(text):
        m = RE_K1.search(raw)
        if not m:
            continue
        n = RE_NUM.match(raw)
        pc = re.search(r"<pc>(.*?)<", raw, re.DOTALL)
        body = RE_K1.sub("", raw, count=1)
        yield (
            int(n.group(1)) if n else 0,
            pc.group(1).strip() if pc else "",
            m.group(1).strip(),
            body,
        )


def pd_marks(body: str):
    """Return (broad_sources, strict_sources) for one PD entry body.

    broad  — every dictionary-source token anywhere in a bracket (a bracket may
             carry a gloss and several sources: `[infamous, MW., APTE]` = 2).
    strict — only brackets whose every comma/semicolon segment is a source, the
             convention behind H6942's 1,801 / 1,956 counts.
    """
    broad = Counter()
    strict = Counter()
    for bracket in RE_BRACKET.findall(body):
        inner = bracket[1:-1]
        found = Counter()
        for name, rx in MARKS.items():
            n = len(rx.findall(inner))
            if n:
                found[name] += n
        if not found:
            continue
        broad.update(found)
        segments = [s for s in re.split(r"[,;]", RE_SLP1.sub("", inner)) if s.strip()]
        ok = bool(segments)
        for seg in segments:
            seg = RE_ITAL.sub("", seg).strip()
            if not any(rx.fullmatch(seg) for rx in MARKS.values()):
                ok = False
                break
        if ok:
            strict.update(found)
    return broad, strict


def pd_citation_set(body: str, sigla_by_key):
    """Curated-siglum matches in the roman prose of a PD entry.

    SLP1 payloads, italic gloss, page markers and markup are stripped first —
    the same order pd_extract_sigla.py uses, so a siglum is only ever the
    roman-running-prose token.
    """
    text = RE_SLP1.sub(" ", body)
    text = RE_ITAL.sub(" ", text)
    text = RE_TAG.sub(" ", text)
    text = RE_BRACKET.sub(" ", text)
    out = set()
    for m in RE_SIGLUM.finditer(text):
        key = cite_key(m.group(1))
        if key in sigla_by_key:
            out.add(key)
    return out


def ls_citation_set(body: str):
    """Citation keys from Cologne `<ls>` markup (PWG / MW convention).

    The abbreviation sits either at the head of the content (`<ls>ṚV. 10,146,4</ls>`)
    or in the `n` attribute when the content is a bare locus
    (`<ls n="ṚV.">1,84,7</ls>`). Continuation loci with neither are skipped.
    """
    out = set()
    for m in RE_LS.finditer(body):
        attr, content = m.group(1), RE_TAG.sub("", m.group(2)).strip()
        abbr = None
        nm = re.search(r'n="([^"]*)"', attr)
        if nm and nm.group(1).strip():
            abbr = nm.group(1).strip().split()[0]
        if abbr is None and content and content[0].isalpha():
            abbr = content.split()[0]
        if not abbr:
            continue
        key = cite_key(abbr)
        if len(key) >= 2:
            out.add(key)
    return out


def pd_gloss_tokens(body: str) -> set:
    italic = " ".join(RE_ITAL.findall(body))
    text = RE_SLP1.sub(" ", body)
    text = RE_BRACKET.sub(" ", text)
    text = RE_TAG.sub(" ", text)
    text = italic + " " + text
    text = RE_SIGLUM.sub(" ", text)          # drop citation sigla
    text = re.sub(r"\d+", " ", text)
    return gloss_tokens(text)


def mw_gloss_tokens(body: str) -> set:
    text = re.sub(r"<s1?>.*?</s1?>", " ", body, flags=re.DOTALL)
    text = re.sub(r"<ls[^>]*>.*?</ls>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<gk>.*?</gk>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<hom>.*?</hom>", " ", text, flags=re.DOTALL)
    text = RE_TAG.sub(" ", text)
    return gloss_tokens(text)


def pwg_gloss_tokens(body: str) -> set:
    italic = " ".join(RE_ITAL.findall(body))   # PWG italic = German gloss
    text = RE_SLP1.sub(" ", body)
    text = re.sub(r"<ls[^>]*>.*?</ls>", " ", text, flags=re.DOTALL)
    text = RE_TAG.sub(" ", text)
    text = italic + " " + text
    text = re.sub(r"\d+", " ", text)
    return gloss_tokens(text)


def gloss_tokens(text: str) -> set:
    """Folded alphabetic tokens of a gloss string.

    SLP1 residue is rejected rather than folded: `q`, `z`, `S` and a mid-token
    capital are SLP1-only signatures (IAST/English never carry them), and the
    bare SLP1 headword echo at the start of a PD entry would otherwise enter the
    gloss as `akalakuzmarqa`. `norm` is used so English `pumpkin` stays
    `pumpkin` (the `nfold` nasal fold would give `punpkin`).
    """
    out = set()
    for tok in re.findall(r"[^\W\d_]{3,}", text):
        if re.search(r"[qzS]", tok) or re.search(r"[A-Z]", tok[1:]):
            continue
        key = norm(tok)
        if key and key not in STOP:
            out.add(key)
    return out


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def size_class(n: int) -> str:
    if n == 0:
        return "0"
    if n <= 10:
        return "1-10"
    if n <= 50:
        return "11-50"
    if n <= 200:
        return "51-200"
    return "200+"


# ---- statistics ------------------------------------------------------------

def boot_ci(values, stat=statistics.mean, n=BOOTSTRAPS, seed=RNG_SEED):
    """Percentile bootstrap CI of a statistic over a list of values."""
    if not values:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    k = len(values)
    draws = []
    for _ in range(n):
        draws.append(stat([values[rng.randrange(k)] for _ in range(k)]))
    draws.sort()
    lo = draws[int(0.025 * (n - 1))]
    hi = draws[int(0.975 * (n - 1))]
    return (lo, hi)


def boot_diff_ci(a, b, n=BOOTSTRAPS, seed=RNG_SEED):
    """Percentile bootstrap CI of mean(a) − mean(b), independent resamples."""
    if not a or not b:
        return (float("nan"), float("nan"), float("nan"))
    rng = random.Random(seed)
    draws = []
    for _ in range(n):
        ma = sum(a[rng.randrange(len(a))] for _ in range(len(a))) / len(a)
        mb = sum(b[rng.randrange(len(b))] for _ in range(len(b))) / len(b)
        draws.append(ma - mb)
    draws.sort()
    return (
        draws[int(0.025 * (n - 1))],
        draws[int(0.975 * (n - 1))],
        statistics.mean(draws),
    )


# ---- main ------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pd", type=Path, default=DEFAULT_PD)
    ap.add_argument("--pwg", type=Path, default=DEFAULT_PWG)
    ap.add_argument("--mw", type=Path, default=DEFAULT_MW)
    ap.add_argument("--sigla", type=Path,
                    default=Path(__file__).resolve().parent.parent / "data" / "pd" / "pd_siglum_families.tsv")
    ap.add_argument("--dcs", type=Path,
                    default=Path(__file__).resolve().parent.parent / "data" / "dcs" / "dcs_lemma_summary.json")
    ap.add_argument("--limit", type=int, default=0, help="cap records per dictionary (quick runs)")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--out-dir", type=Path,
                    default=Path(__file__).resolve().parent.parent / "data" / "pd")
    args = ap.parse_args()

    for p in (args.pd, args.pwg, args.mw, args.sigla):
        if not p.exists():
            print(f"MISSING input: {p}", file=sys.stderr)
            return 2

    print("reading PD text …", file=sys.stderr)
    pd_text = read_text(args.pd)
    print("reading PWG text …", file=sys.stderr)
    pwg_text = read_text(args.pwg)
    print("reading MW text …", file=sys.stderr)
    mw_text = read_text(args.mw)

    # -- curated PD siglum vocabulary --------------------------------------
    sigla_by_key = {}
    with args.sigla.open(encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        ix = {name: i for i, name in enumerate(header)}
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(header):
                continue
            if parts[ix["class"]] != "primary":
                continue
            key = cite_key(parts[ix["siglum"]])
            if len(key) < 2:
                continue
            try:
                mass = int(parts[ix["count"]])
            except ValueError:
                continue
            if mass > sigla_by_key.get(key, ("", 0))[1]:
                sigla_by_key[key] = (parts[ix["siglum"]], mass)

    # -- PD entries ---------------------------------------------------------
    pd_entries = {}
    pd_by_key = defaultdict(list)          # form_key -> [entry dicts]
    pd_records = 0
    for num, pc, k1, body in parse_records(pd_text):
        pd_records += 1
        broad, strict = pd_marks(body)
        fk = slp1_form_key(k1)
        rec = {
            "num": num,
            "pc": pc,
            "k1": k1,
            "fk": fk,
            "broad": dict(broad),
            "strict": dict(strict),
            "cits": pd_citation_set(body, sigla_by_key),
            "gloss": pd_gloss_tokens(body),
            "size": len(body),
        }
        pd_entries[num] = rec
        pd_by_key[fk].append(rec)
        if args.limit and pd_records >= args.limit:
            break
    print(f"PD records {pd_records} · distinct form_keys {len(pd_by_key)}", file=sys.stderr)

    # -- PWG / MW entries ---------------------------------------------------
    pd_keys = set(pd_by_key)

    def parse_target(text, gloss_fn, limit):
        """Full letter-a key set + citation vocabulary; per-entry payload only
        for headwords PD also has (memory: MW alone is 286k records)."""
        keys = set()
        vocab_c = Counter()
        recs = []
        n = 0
        for num, pc, k1, body in parse_records(text):
            if not k1.startswith("a"):
                continue
            n += 1
            fk = slp1_form_key(k1)
            keys.add(fk)
            cits = ls_citation_set(body)
            vocab_c.update(cits)
            if fk in pd_keys:
                recs.append({
                    "k1": k1,
                    "fk": fk,
                    "cits": cits,
                    "gloss": gloss_fn(body),
                    "size": len(body),
                })
            if limit and n >= limit:
                break
        return keys, vocab_c, recs

    pwg_keys, pwg_vocab, pwg_recs = parse_target(pwg_text, pwg_gloss_tokens, args.limit)
    mw_keys, mw_vocab, mw_recs = parse_target(mw_text, mw_gloss_tokens, args.limit)
    pwg_by_key = defaultdict(list)
    mw_by_key = defaultdict(list)
    for r in pwg_recs:
        pwg_by_key[r["fk"]].append(r)
    for r in mw_recs:
        mw_by_key[r["fk"]].append(r)
    print(f"PWG letter-a keys {len(pwg_keys)} · shared kept {len(pwg_recs)}", file=sys.stderr)
    print(f"MW  letter-a keys {len(mw_keys)} · shared kept {len(mw_recs)}", file=sys.stderr)

    # -- shared abbreviation vocabulary ------------------------------------
    pd_vocab = Counter()
    pd_cit_mass = 0
    for rec in pd_entries.values():
        pd_cit_mass += sum(sigla_by_key[k][1] for k in rec["cits"] if k in sigla_by_key)
        pd_vocab.update(rec["cits"])

    shared = {
        "PWG": sorted(set(pd_vocab) & set(pwg_vocab)),
        "MW": sorted(set(pd_vocab) & set(mw_vocab)),
    }
    mappable_share = {}
    for name, keys in shared.items():
        covered = sum(pd_vocab[k] for k in keys)
        mappable_share[name] = {
            "shared_keys": len(keys),
            "pd_citation_mass_covered": covered,
            "pd_citation_mass_total": sum(pd_vocab.values()),
            "share": covered / sum(pd_vocab.values()) if pd_vocab else 0.0,
            "target_vocab_keys": len(pwg_vocab if name == "PWG" else mw_vocab),
        }

    # -- macro inventory ----------------------------------------------------
    union = pwg_keys | mw_keys
    pd_only = pd_keys - union
    pd_only_any_dcs = pd_only
    dcs_attest = {}
    if args.dcs.exists():
        dcs = json.loads(read_text(args.dcs))
        for lemma, info in dcs.get("lemmas", {}).items():
            dcs_attest[slp1_form_key(lemma)] = info
    shared_keys_all = pd_keys & union
    attested = [k for k in pd_only_any_dcs if dcs_attest.get(k, {}).get("attested")]
    shared_attested = [k for k in shared_keys_all if dcs_attest.get(k, {}).get("attested")]
    bands = Counter(
        str(dcs_attest.get(k, {}).get("freqBand", "absent")) for k in pd_only_any_dcs
    )
    macro = {
        "pd_letter_a_entries": pd_records,
        "pd_distinct_headwords": len(pd_keys),
        "pwg_letter_a_distinct": len(pwg_keys),
        "mw_letter_a_distinct": len(mw_keys),
        "pd_and_pwg": len(pd_keys & pwg_keys),
        "pd_and_mw": len(pd_keys & mw_keys),
        "pd_and_both": len(pd_keys & pwg_keys & mw_keys),
        "pd_only_vs_pwg_mw": len(pd_only),
        "pwg_only_within_pd_frame": len(pwg_keys - pd_keys),
        "mw_only_within_pd_frame": len(mw_keys - pd_keys),
        "pd_only_share": len(pd_only) / len(pd_keys) if pd_keys else 0.0,
        "pd_only_with_dcs_lemma": len(attested),
        "pd_only_dcs_attested_share": len(attested) / len(pd_only) if pd_only else 0.0,
        "pd_only_dcs_freqband": dict(bands.most_common()),
        "shared_with_targets": len(shared_keys_all),
        "shared_dcs_attested": len(shared_attested),
        "shared_dcs_attested_share": (len(shared_attested) / len(shared_keys_all)) if shared_keys_all else 0.0,
        "citation_practice": {
            "pd_distinct_citations_per_entry_mean": statistics.mean(
                len(r["cits"]) for r in pd_entries.values()) if pd_entries else 0.0,
            "pd_entries_with_zero_citations_share": (
                sum(1 for r in pd_entries.values() if not r["cits"]) / pd_records) if pd_records else 0.0,
            "pwg_distinct_citations_per_entry_mean": statistics.mean(
                len(r["cits"]) for r in pwg_recs) if pwg_recs else 0.0,
            "mw_distinct_citations_per_entry_mean": statistics.mean(
                len(r["cits"]) for r in mw_recs) if mw_recs else 0.0,
            "note": ("PD cites more DISTINCT works per shared headword than either target, "
                     "so a strict-subset test is biased against PD wherever its mapped set is "
                     "the larger one; target_coverage (how much of the target's citation set "
                     "PD reproduces) is reported alongside as the direction-correct companion. "
                     "Medians per shared headword are filled in after sampling."),
        },
        "dcs_lemma_table_present": bool(dcs_attest),
    }

    # -- micro: shared headwords -------------------------------------------
    def pair_metrics(pd_key, target_key, target_by_key, target_name):
        """Per-headword metrics for one PD form_key shared with one target."""
        pd_recs = pd_by_key[pd_key]
        tg_recs = target_by_key[target_key]
        pd_cits = set().union(*(r["cits"] for r in pd_recs))
        pg_cits = set().union(*(r["cits"] for r in tg_recs))
        pd_gloss = set().union(*(r["gloss"] for r in pd_recs))
        pg_gloss = set().union(*(r["gloss"] for r in tg_recs))
        mapped = pd_cits & set(shared[target_name])
        mapped_target = pg_cits & set(shared[target_name])
        marks = Counter()
        for r in pd_recs:
            marks.update(r["broad"])
        return {
            "pd_key": pd_key,
            "target": target_name,
            "pd_k1": pd_recs[0]["k1"],
            "target_k1": tg_recs[0]["k1"],
            "pd_entries": len(pd_recs),
            "target_entries": len(tg_recs),
            "pd_cits_n": len(pd_cits),
            "target_cits_n": len(pg_cits),
            "pd_mapped_n": len(mapped),
            "cit_jaccard": jaccard(mapped, mapped_target),
            "cit_subset": 1 if (mapped and mapped <= mapped_target) else 0,
            "cit_subset_applicable": 1 if mapped else 0,
            "target_coverage": (len(mapped & mapped_target) / len(mapped_target)) if mapped_target else 0.0,
            "target_coverage_applicable": 1 if mapped_target else 0,
            "cit_count_ratio": (len(pd_cits) / len(pg_cits)) if pg_cits else 0.0,
            "gloss_jaccard": jaccard(pd_gloss, pg_gloss),
            "pd_gloss_n": len(pd_gloss),
            "target_gloss_n": len(pg_gloss),
            "marked": 1 if marks else 0,
            "marked_strict": 1 if any(r["strict"] for r in pd_recs) else 0,
            "marked_mw": 1 if marks.get("MW") else 0,
            "marked_pw": 1 if marks.get("PW") else 0,
            "pd_size_class": size_class(max(r["size"] for r in pd_recs)),
        }

    pairs = {"PWG": [], "MW": []}
    for name, target_keys, target_by_key in (
        ("PWG", pwg_keys, pwg_by_key),
        ("MW", mw_keys, mw_by_key),
    ):
        for k in sorted(pd_keys & target_keys):
            pairs[name].append(pair_metrics(k, k, target_by_key, name))

    # -- stratified sample + shuffled null ---------------------------------
    # Frame: shared headwords, stratified by marked/unmarked x PD entry-size
    # class. Sample: min(2000, stratum size) per stratum, seeded. The null
    # re-pairs each sampled PD headword with a target entry of the SAME size
    # class drawn from the sampled target pool (never its own form_key).
    rng = random.Random(RNG_SEED)
    sampled = {"PWG": [], "MW": []}
    null_metrics = {"PWG": [], "MW": []}
    for name in ("PWG", "MW"):
        strata = defaultdict(list)
        for row in pairs[name]:
            strata[(row["marked"], row["pd_size_class"])].append(row)
        for key in sorted(strata):
            rows = strata[key]
            take = min(2000, len(rows))
            sampled[name].extend(rng.sample(rows, take) if take < len(rows) else rows)
        target_by_key = pwg_by_key if name == "PWG" else mw_by_key
        pool_by_class = defaultdict(list)
        for row in sampled[name]:
            pool_by_class[row["pd_size_class"]].append(row)
        for row in sampled[name]:
            cands = [c for c in pool_by_class[row["pd_size_class"]] if c["pd_key"] != row["pd_key"]]
            if not cands:
                continue
            other = cands[rng.randrange(len(cands))]
            tg = target_by_key[other["pd_key"]]
            pg_cits = set().union(*(r["cits"] for r in tg))
            pg_gloss = set().union(*(r["gloss"] for r in tg))
            pd_recs = pd_by_key[row["pd_key"]]
            pd_cits = set().union(*(r["cits"] for r in pd_recs))
            pd_gloss = set().union(*(r["gloss"] for r in pd_recs))
            mapped = pd_cits & set(shared[name])
            mt = pg_cits & set(shared[name])
            null_metrics[name].append({
                "cit_jaccard": jaccard(mapped, mt),
                "cit_subset": 1 if (mapped and mapped <= mt) else 0,
                "cit_subset_applicable": 1 if mapped else 0,
                "target_coverage": (len(mapped & mt) / len(mt)) if mt else 0.0,
                "target_coverage_applicable": 1 if mt else 0,
                "gloss_jaccard": jaccard(pd_gloss, pg_gloss),
                "marked": row["marked"],
            })

    macro["citation_practice"]["pd_citations_per_shared_headword_median"] = {
        n: statistics.median([r["pd_cits_n"] for r in sampled[n]]) if sampled[n] else 0
        for n in ("PWG", "MW")}
    macro["citation_practice"]["target_citations_per_shared_headword_median"] = {
        n: statistics.median([r["target_cits_n"] for r in sampled[n]]) if sampled[n] else 0
        for n in ("PWG", "MW")}

    # -- calibration --------------------------------------------------------
    def summarise(rows):
        if not rows:
            return {"n": 0}
        applicable = [r for r in rows if r.get("cit_subset_applicable")]
        out = {
            "n": len(rows),
            "cit_jaccard_mean": statistics.mean(r["cit_jaccard"] for r in rows),
            "cit_jaccard_median": statistics.median(r["cit_jaccard"] for r in rows),
            "subset_rate": statistics.mean(r["cit_subset"] for r in rows),
            "gloss_jaccard_mean": statistics.mean(r["gloss_jaccard"] for r in rows),
            "gloss_jaccard_median": statistics.median(r["gloss_jaccard"] for r in rows),
            "mapped_entries": len(applicable),
            "mapped_share": len(applicable) / len(rows),
            "target_coverage_mean": statistics.mean(r.get("target_coverage", 0.0) for r in rows),
            "target_coverage_median": statistics.median(r.get("target_coverage", 0.0) for r in rows),
        }
        if applicable:
            out["subset_rate_applicable"] = statistics.mean(r["cit_subset"] for r in applicable)
            out["cit_jaccard_applicable_mean"] = statistics.mean(r["cit_jaccard"] for r in applicable)
        else:
            out["subset_rate_applicable"] = None
            out["cit_jaccard_applicable_mean"] = None
        return out

    def delta(rows_a, rows_b, key):
        a = [r[key] for r in rows_a]
        b = [r[key] for r in rows_b]
        lo, hi, _ = boot_diff_ci(a, b)
        return {
            "point": (statistics.mean(a) - statistics.mean(b)) if a and b else None,
            "ci95": [lo, hi],
            "n_a": len(a),
            "n_b": len(b),
        }

    def applicable(rows):
        return [r for r in rows if r.get("cit_subset_applicable")]

    def size_stratified(rows, min_side=5):
        """Marked-minus-unmarked deltas computed WITHIN each PD entry-size class.

        Pooled deltas mix classes whose metrics differ by an order of magnitude
        (a 2,700-line entry and a one-line entry do not have comparable citation
        sets), so the stratified estimate is the robustness check: a sign that
        survives inside every class is not a size artefact.
        """
        out = {}
        for metric in ("cit_subset", "cit_jaccard", "gloss_jaccard", "target_coverage"):
            per = {}
            num = den = 0.0
            for sc in sorted({r["pd_size_class"] for r in rows}):
                m = [r[metric] for r in rows
                     if r["marked"] and r["pd_size_class"] == sc
                     and (metric != "cit_subset" or r["cit_subset_applicable"])]
                u = [r[metric] for r in rows
                     if not r["marked"] and r["pd_size_class"] == sc
                     and (metric != "cit_subset" or r["cit_subset_applicable"])]
                if len(m) >= min_side and len(u) >= min_side:
                    d = statistics.mean(m) - statistics.mean(u)
                    per[sc] = {"marked_mean": statistics.mean(m), "unmarked_mean": statistics.mean(u),
                               "delta": d, "n_marked": len(m), "n_unmarked": len(u)}
                    w = len(m) + len(u)
                    num += w * d
                    den += w
            out[metric] = {"weighted_delta": (num / den) if den else None, "by_class": per}
        return out

    calibration = {}
    for name in ("PWG", "MW"):
        rows = sampled[name]
        marked = [r for r in rows if r["marked"]]
        unmarked = [r for r in rows if not r["marked"]]
        strict_marked = [r for r in rows if r["marked_strict"]]
        # the named source this target dictionary corresponds to: PD marks
        # inheritance from `MW` and `PW` by name, so those brackets are the
        # direct test of the convention, not the aggregate marked class.
        source_key = "marked_mw" if name == "MW" else "marked_pw"
        named = [r for r in rows if r[source_key]]
        calibration[name] = {
            "sampled": summarise(rows),
            "marked": summarise(marked),
            "unmarked": summarise(unmarked),
            "marked_strict": summarise(strict_marked),
            "marked_named_source": summarise(named),
            "named_source_token": "MW" if name == "MW" else "PW",
            "null_shuffled": summarise(null_metrics[name]),
            "delta_subset_marked_minus_unmarked": delta(applicable(marked), applicable(unmarked),
                                                         "cit_subset"),
            "delta_subset_named_minus_unmarked": delta(applicable(named), applicable(unmarked),
                                                       "cit_subset"),
            "delta_cit_jaccard_marked_minus_unmarked": delta(marked, unmarked, "cit_jaccard"),
            "delta_gloss_marked_minus_unmarked": delta(marked, unmarked, "gloss_jaccard"),
            "delta_gloss_named_minus_unmarked": delta(named, unmarked, "gloss_jaccard"),
            "delta_gloss_vs_null": delta(rows, null_metrics[name], "gloss_jaccard"),
            "delta_cit_vs_null": delta(rows, null_metrics[name], "cit_jaccard"),
            "delta_coverage_marked_minus_unmarked": delta(marked, unmarked, "target_coverage"),
            "delta_coverage_named_minus_unmarked": delta(named, unmarked, "target_coverage"),
            "delta_coverage_vs_null": delta(rows, null_metrics[name], "target_coverage"),
            "size_stratified": size_stratified(rows),
        }

    # -- the three distributions, with CIs --------------------------------
    def quantiles(values):
        if not values:
            return {}
        vs = sorted(values)
        def q(f):
            return vs[min(len(vs) - 1, int(f * (len(vs) - 1) + 0.5))]
        return {"p10": q(0.10), "p25": q(0.25), "p50": q(0.50), "p75": q(0.75), "p90": q(0.90)}

    def dist_block(values):
        if not values:
            return {"n": 0}
        lo, hi = boot_ci(values)
        return {"n": len(values), "mean": statistics.mean(values),
                "mean_ci95": [lo, hi], **quantiles(values)}

    distributions = {}
    for name in ("PWG", "MW"):
        rows = sampled[name]
        distributions[name] = {
            "citation_jaccard_mapped": dist_block([r["cit_jaccard"] for r in rows]),
            "citation_subset_rate_applicable": dist_block(
                [r["cit_subset"] for r in rows if r["cit_subset_applicable"]]),
            "gloss_jaccard": dist_block([r["gloss_jaccard"] for r in rows]),
            "target_citation_coverage": dist_block([r["target_coverage"] for r in rows]),
            "by_marks": {
                label: {
                    "citation_jaccard_mapped": dist_block([r["cit_jaccard"] for r in sel]),
                    "citation_subset_rate_applicable": dist_block(
                        [r["cit_subset"] for r in sel if r["cit_subset_applicable"]]),
                    "gloss_jaccard": dist_block([r["gloss_jaccard"] for r in sel]),
                    "target_citation_coverage": dist_block([r["target_coverage"] for r in sel]),
                }
                for label, sel in (
                    ("marked", [r for r in rows if r["marked"]]),
                    ("unmarked", [r for r in rows if not r["marked"]]),
                    ("marked_named_source", [r for r in rows
                                             if r["marked_mw" if name == "MW" else "marked_pw"]]),
                )
            },
        }

    # -- verdict, applied mechanically -------------------------------------
    def passes(block, threshold):
        if not block:
            return False
        point, lo = block["point"], block["ci95"][0]
        if point is None or lo != lo:  # NaN guard
            return False
        return point >= threshold and lo > 0

    d1 = {n: passes(calibration[n]["delta_subset_marked_minus_unmarked"], 0.10)
          for n in ("PWG", "MW")}
    d1_named = {n: passes(calibration[n]["delta_subset_named_minus_unmarked"], 0.10)
                for n in ("PWG", "MW")}
    # gloss is only comparable where the gloss languages agree: PD and MW are
    # both English, PWG is German. PD-PWG gloss overlap is reported as a
    # language-mismatch control, never as evidence.
    d2 = {"MW": passes(calibration["MW"]["delta_gloss_marked_minus_unmarked"], 0.02)}
    d2_named = {"MW": passes(calibration["MW"]["delta_gloss_named_minus_unmarked"], 0.02)}
    bracket_survives = any(d1.values()) and any(d2.values())
    verdict = {
        "D1_citation_subsumption_lift": d1,
        "D1_named_source_citation_subsumption_lift": d1_named,
        "D2_gloss_overlap_lift_PD_MW_only": d2,
        "D2_named_source_gloss_overlap_lift": d2_named,
        "bracket_proxy_survives": bracket_survives,
        "rule": ("D1: delta subset rate >= 10 pp with the 95 % bootstrap CI lower bound > 0, "
                 "computed on the entries whose mapped citation set is non-empty; "
                 "D2: delta gloss Jaccard >= 0.02 with CI lower bound > 0, PD-MW only "
                 "(PD-PWG is a language-mismatch control). Bracket proxy survives iff "
                 "both hold for at least one target dictionary."),
    }

    # -- marks census (macro, complements H6942) ---------------------------
    broad_entries = sum(1 for r in pd_entries.values() if r["broad"])
    strict_entries = sum(1 for r in pd_entries.values() if r["strict"])
    marks = {
        "entries": pd_records,
        "broad_entries_with_any_dictionary_source": broad_entries,
        "broad_share": broad_entries / pd_records if pd_records else 0.0,
        "strict_entries_all_segments_sources": strict_entries,
        "strict_share": strict_entries / pd_records if pd_records else 0.0,
        "broad_marks_by_source": dict(sum((Counter(r["broad"]) for r in pd_entries.values()), Counter()).most_common()),
        "strict_marks_by_source": dict(sum((Counter(r["strict"]) for r in pd_entries.values()), Counter()).most_common()),
        "broad_marks_total": sum(sum(r["broad"].values()) for r in pd_entries.values()),
        "strict_marks_total": sum(sum(r["strict"].values()) for r in pd_entries.values()),
        "h6942_reference": {
            "entries": 107630, "entries_with_mark": 1801, "marks": 1956,
            "by_source": {"DBHS": 852, "PW": 399, "APTE": 264, "MW": 245,
                          "VIŚVA": 101, "NT": 84, "VĀC": 11},
            "note": ("H6942 counted a narrower convention (1,801 / 1,956). The broad "
                     "channel here also counts gloss-prefixed source brackets "
                     "(`[infamous, MW., APTE]`); strict is the source-only bracket."),
        },
    }

    # crosswalk-free within-PD check: does a marked entry look like a shorter,
    # less independently cited entry than an unmarked one? No abbreviation
    # mapping is involved, so the mixed SLP1/IAST sigla convention cannot
    # contaminate it.
    def entry_profile(rows):
        if not rows:
            return {"n": 0}
        cits = [len(r["cits"]) for r in rows]
        sizes = [r["size"] for r in rows]
        return {
            "n": len(rows),
            "citations_per_entry_mean": statistics.mean(cits),
            "citations_per_entry_median": statistics.median(cits),
            "zero_citation_share": sum(1 for c in cits if c == 0) / len(cits),
            "entry_chars_mean": statistics.mean(sizes),
            "entry_chars_median": statistics.median(sizes),
        }

    all_recs = list(pd_entries.values())
    marks["within_pd_profile"] = {
        "unmarked": entry_profile([r for r in all_recs if not r["broad"]]),
        "marked_broad": entry_profile([r for r in all_recs if r["broad"]]),
        "marked_strict": entry_profile([r for r in all_recs if r["strict"]]),
        "note": ("no abbreviation mapping involved: this is PD against itself. A "
                 "marked entry that were a taken-over entry should carry fewer of "
                 "PD's own citations and be shorter if the borrowing were wholesale."),
    }

    doc = {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/pd_inheritance_probe.py (H6948)",
        "generatedAt": "2026-10-18",
        "seed": RNG_SEED,
        "bootstraps": BOOTSTRAPS,
        "inputs": {
            "pd": {"path": str(args.pd), "bytes": args.pd.stat().st_size,
                   "sha256": sha256_file(args.pd)},
            "pwg": {"path": str(args.pwg), "bytes": args.pwg.stat().st_size,
                    "sha256": sha256_file(args.pwg)},
            "mw": {"path": str(args.mw), "bytes": args.mw.stat().st_size,
                   "sha256": sha256_file(args.mw)},
            "sigla": str(args.sigla),
            "dcs": str(args.dcs) if args.dcs.exists() else None,
            "records_capped_by_limit": args.limit or None,
        },
        "sampling": {
            "frame": ("all PD letter-a headwords (distinct slp1_form_key) also present in the "
                      "target dictionary's letter-a headwords"),
            "strata": "marked x PD entry-size class (0 / 1-10 / 11-50 / 51-200 / 200+ chars)",
            "sample": "min(2000, stratum size) per stratum, seeded random.Random(20261018)",
            "null": ("each sampled PD headword re-paired with a target entry of the same PD "
                     "size class, never its own form_key"),
            "per_headword_tsv": "data/pd/pd_inheritance_metrics.tsv (sampled rows, all fields)",
            "population_aggregates": "the macro and mappable_share blocks are full-population, not sampled",
        },
        "marks": marks,
        "macro": macro,
        "mappable_share": mappable_share,
        "calibration": calibration,
        "distributions": distributions,
        "verdict": verdict,
    }

    print(json.dumps({"marks": {k: marks[k] for k in marks if k != "h6942_reference"},
                      "macro": macro, "mappable_share": mappable_share,
                      "verdict": verdict}, ensure_ascii=False, indent=2))

    if args.no_write:
        return 0

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "pd_inheritance_distributions.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    columns = ["pd_key", "target", "pd_k1", "target_k1", "pd_entries", "target_entries",
               "pd_cits_n", "target_cits_n", "pd_mapped_n", "cit_jaccard", "cit_subset",
               "cit_subset_applicable", "target_coverage", "target_coverage_applicable",
               "cit_count_ratio", "gloss_jaccard", "pd_gloss_n",
               "target_gloss_n", "marked", "marked_strict", "marked_mw", "marked_pw",
               "pd_size_class"]
    lines = ["\t".join(columns)]
    for name in ("PWG", "MW"):
        for row in sampled[name]:
            lines.append("\t".join(str(row[c]) for c in columns))
    (args.out_dir / "pd_inheritance_metrics.tsv").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir}/pd_inheritance_distributions.json and "
          f"pd_inheritance_metrics.tsv ({len(lines)-1} rows)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
