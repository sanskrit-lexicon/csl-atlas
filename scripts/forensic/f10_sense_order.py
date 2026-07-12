#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""f10 -- the sense-ORDER test (Boehtlingk item #4, the last open clause).

Historical claim under test
---------------------------
Max Mueller's letter of 11 June 1881 (Stache-Weiske 2015) itemises Boehtlingk's
plagiarism charge against Monier-Williams in four clauses. A10
(``article_21_apparatus_not_errors.md``) measures three: shared OMISSIONS
(s3.5 / F9, ~8x coupling), shared ERRORS (s4, null), false CITATIONS (s6, null).
The fourth is verbatim:

    "... u[nd] die Reihenfolge der Bedeutungen einfach abgeschrieben."
    -- and the order of the MEANINGS simply copied out.

A10 only *proxies* it with F5's CITATION order (0.811). The literal claim -- does
MW list its glosses/senses in PWG's order? -- is unmeasured. This script measures it.

The idea
--------
For every headword both dictionaries carry with >=3 senses in each, align MW's
ordered sense sequence to PWG's cross-lingually (by MEANING, not by citation, so
the result is independent of F5), then score whether the two orders agree
(concordant-pair fraction, exactly F5's statistic but over senses not citations).
0.50 = random, 1.00 = MW reproduces PWG's sense sequence.

Sense segmentation (validated per-dict conventions, cf. scripts/lib/dict-feature-adapters.mjs)
    MW  : senses are split across consecutive sub-<L> records sharing k1 (e.g.
          go = L 66884, .02, .04 ...), plus <div n="to|P|1"> divisions within a
          record; the leading declension/paradigm chunk carries no gloss and drops out.
    PWG : one record, senses divided by <div\\b> markers (the "N>" Bedeutungen);
          the pre-first-<div> chunk is grammar/etymology head and drops out.
    AP  : one record, senses divided by the bullet marker U+2219; head drops out.

Cross-lingual alignment (by meaning, citations DELIBERATELY excluded)
    Each sense -> a bag of {English gloss tokens} U {Sanskrit referent tokens}.
    PWG's German gloss is rendered to English offline (argos de->en, cached) -- the
    same MT channel as F6, NOT a live LLM. MW sense i is matched one-to-one (greedy,
    descending similarity) to the PWG sense with the highest bag-Jaccard, position-blind.
    Concordance is then the fraction of matched sense-pairs whose relative order agrees.

Controls (mandatory, per A10 method)
    - APTE (AP, 1890): independent English dict, senses in English (no MT). Senses have
      a partly-forced canonical order (literal -> figurative -> technical), so MW-vs-PWG
      only counts as COPYING if it exceeds MW-vs-Apte, not merely 0.50.
    - SHUFFLED-sense null: re-score each headword with PWG's sense positions permuted;
      isolates the matching/forced-order floor. Copying = MW-vs-PWG >> shuffle.

Honest outcomes: MW-vs-PWG >> Apte and >> shuffle closes the fourth clause; a null
("sense order is convergent, not copied") equally fills the last gap in the charge.

Self-contained (own minimal csl-orig parser), reproducible (sorted + seeded).
Reads ../csl-orig/v02/{mw,pwg,ap}.  Run from repo root:
    python scripts/forensic/f10_sense_order.py            # full run (MT)
    python scripts/forensic/f10_sense_order.py --census   # population sizes only, no MT
Env: F10_SAMPLE caps headwords per comparison (default all); F10_NULLITER (default 20).
Output: data/forensic/sense_order_test.csv, sense_order_examples.csv, f10_report.json.
"""

import os

# CTranslate2 (argos backend) spins up a thread per core and thrashes on the short
# gloss strings translated here — single-thread is ~14x faster (8.8/s vs 0.6/s) and
# bit-identical in output. Must be set before ctranslate2/torch import their pools.
os.environ.setdefault("OMP_NUM_THREADS", "1")

import re
import sys
import csv
import json
import random

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

CSL_ORIG = "../csl-orig/v02"
SEED = 17
NULLITER = int(os.environ.get("F10_NULLITER", "20"))
SAMPLE = int(os.environ.get("F10_SAMPLE", "0"))   # 0 = no cap
MIN_SENSES = 3          # need >=3 senses in BOTH dicts for an order signal
MIN_MATCHED = 3         # need >=3 confidently matched sense-pairs to score order
MIN_GLOSS_TOK = 2       # a chunk is a real sense only with >=2 gloss content tokens

# --- validated sense markers (mirror scripts/lib/dict-feature-adapters.mjs) ---
MW_DIV = re.compile(r'<div n="(?:to|P|1)"\s*/?>')
PWG_DIV = re.compile(r'(?=<div\b)')
AP_BULLET = "∙"                 # the AP sense bullet

_BAR = "¦"                       # the headword/body separator in MW/PWG/AP
_SKT_MW = re.compile(r"<s1?>([^<]+)</s1?>")
_SKT_BRACE = re.compile(r"\{#([^#]+)#\}")
_GERMAN = re.compile(r"\{%(.*?)%\}", re.DOTALL)
_LS = re.compile(r"<ls>.*?</ls>", re.DOTALL)
_TAG = re.compile(r"<[^>]*>")
_BRACE = re.compile(r"\{[#%@][^}]*\}|[¦∙]")
_WS = re.compile(r"\s+")
_WORD = re.compile(r"[a-z]{3,}")
_NUMPFX = re.compile(r"^[\s—\-\.]*[¹²³⁰-⁹\d]+[〉\)\.›]*")

STOP = set(
    "the a an and or of to in for with as is are was on at by from that this it its be also "
    "more most see used name kind sort etc esp one two his her their which who whom whose not "
    "no any some such than then there here when where what having being said each cf viz eg "
    " that any pl sg du acc gen dat loc instr nom voc ibc ifc".split()
)


def toks_en(text):
    return {w for w in _WORD.findall(text.lower()) if w not in STOP}


def toks_skt(text):
    out = set()
    for m in _SKT_MW.finditer(text):
        t = m.group(1).strip().strip("/").replace("/", "").replace("\\", "")
        if t:
            out.add(t.lower())
    for m in _SKT_BRACE.finditer(text):
        t = m.group(1).strip().strip("/").replace("/", "").replace("\\", "")
        if t:
            out.add(t.lower())
    return out


def strip_markup_en(text):
    """English gloss text: drop citations, Sanskrit spans, tags, braces."""
    t = _LS.sub(" ", text)
    t = _SKT_MW.sub(" ", t)
    t = _BRACE.sub(" ", t)
    t = _TAG.sub(" ", t)
    return _WS.sub(" ", t).strip()


def iter_records(path):
    """Yield (k1, L, body) per <L>..<LEND> record, preserving file order."""
    L = k1 = None
    body = []
    inside = False
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("<LEND>"):
                if inside:
                    yield k1, L, "".join(body)
                inside = False
                body = []
            elif line.startswith("<L>"):
                m = re.search(r"<k1>([^<]*)", line)
                k1 = m.group(1).strip() if m else None
                mL = re.search(r"<L>([0-9.]+)", line)
                L = mL.group(1) if mL else None
                inside = True
                body = []
            elif inside:
                body.append(line)


def _post_bar(body):
    """Text after the headword/pronunciation separator (the gloss body)."""
    i = body.find(_BAR)
    return body[i + 1:] if i >= 0 else body


def _sense_from_chunk(chunk):
    """A chunk -> {'en':set, 'skt':set, 'raw':str} or None if it is head/paradigm."""
    body = _post_bar(chunk)
    en = toks_en(strip_markup_en(body))
    skt = toks_skt(body)
    if len(en) < MIN_GLOSS_TOK:
        return None
    return {"en": en, "skt": skt, "raw": _WS.sub(" ", strip_markup_en(body))[:80]}


def senses_mw(records):
    """MW: ordered senses across sub-<L> records (+ intra-record <div n=to|P|1>)."""
    out = []
    for _, _, body in records:
        for chunk in MW_DIV.split(body):
            s = _sense_from_chunk(chunk)
            if s:
                out.append(s)
    return out


def senses_ap(records):
    """AP: bullet-divided senses (single record expected; concatenate if several)."""
    out = []
    for _, _, body in records:
        parts = body.split(AP_BULLET)
        for part in parts[1:] if len(parts) > 1 else parts:
            s = _sense_from_chunk(part)
            if s:
                out.append(s)
    return out


def senses_pwg(records):
    """PWG: <div>-divided Bedeutungen; German gloss rendered to English later."""
    out = []
    for _, _, body in records:
        segs = PWG_DIV.split(body)
        for seg in (segs[1:] if len(segs) > 1 and "<div" not in segs[0] else segs):
            de = " ".join(_GERMAN.findall(seg)).strip()
            skt = toks_skt(seg)
            if not de:
                continue
            out.append({"de": de, "skt": skt, "raw": _WS.sub(" ", de)[:80]})
    return out


def group_by_k1(path):
    """k1 -> list of (k1, L, body) records, in file order."""
    d = {}
    for k1, L, body in iter_records(path):
        if k1:
            d.setdefault(k1, []).append((k1, L, body))
    return d


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a or b) else 0.0


def greedy_match(sim):
    """sim[(i,j)] -> similarity; return one-to-one matches [(i,j)] with sim>0, greedy."""
    pairs = sorted((v, i, j) for (i, j), v in sim.items() if v > 0)
    pairs.reverse()
    used_i, used_j, matches = set(), set(), []
    for v, i, j in pairs:
        if i in used_i or j in used_j:
            continue
        used_i.add(i)
        used_j.add(j)
        matches.append((i, j))
    return matches


def concordant_fraction(matches):
    """Fraction of matched sense-pairs whose relative order agrees. None if <2 matches."""
    n = len(matches)
    if n < 2:
        return None
    conc = tot = 0
    for a in range(n):
        for b in range(a + 1, n):
            i1, j1 = matches[a]
            i2, j2 = matches[b]
            if i1 == i2 or j1 == j2:
                continue
            tot += 1
            conc += 1 if ((i1 < i2) == (j1 < j2)) else 0
    return conc / tot if tot else None


def score_headword(mw_bags, other_bags):
    """mw_bags/other_bags: list of token-sets (already English+Sanskrit merged).
    Returns (concordance, matches, n_other, mean_match_sim) via position-blind greedy match."""
    sim = {}
    for i, a in enumerate(mw_bags):
        for j, b in enumerate(other_bags):
            v = jaccard(a, b)
            if v > 0:
                sim[(i, j)] = v
    matches = greedy_match(sim)
    cf = concordant_fraction(matches) if len(matches) >= MIN_MATCHED else None
    msim = sum(sim[(i, j)] for i, j in matches) / len(matches) if matches else 0.0
    return cf, matches, len(other_bags), msim


def score_floor(mb, ob, floor):
    """Concordance restricting matches to similarity > floor (noise control). None if <3."""
    sim = {}
    for i, a in enumerate(mb):
        for j, b in enumerate(ob):
            v = jaccard(a, b)
            if v > floor:
                sim[(i, j)] = v
    matches = greedy_match(sim)
    if len(matches) < MIN_MATCHED:
        return None
    return concordant_fraction(matches)


def robustness_analyses(mw_bags, pwg_bags, ap_bags, cand_all):
    """Paired within-headword PWG-vs-AP comparison + a similarity-floor noise-control
    sweep, both on headwords with >=3 senses in ALL THREE dicts. Returns a dict."""
    import math
    # paired: per-headword concordance for PWG and AP at the default (>0) floor
    pcf, acf = {}, {}
    for h in cand_all:
        p = score_floor(mw_bags(h), pwg_bags(h), 0.0)
        a = score_floor(mw_bags(h), ap_bags(h), 0.0)
        if p is not None:
            pcf[h] = p
        if a is not None:
            acf[h] = a
    both = sorted(set(pcf) & set(acf))
    diffs = [pcf[h] - acf[h] for h in both]
    wins = sum(1 for d in diffs if d > 0)
    ties = sum(1 for d in diffs if d == 0)
    loss = sum(1 for d in diffs if d < 0)
    nn = wins + loss
    z = (wins - nn / 2) / math.sqrt(nn / 4) if nn else 0.0
    paired = {
        "headwords_ge3_all_three": len(cand_all),
        "scored_in_both": len(both),
        "paired_mean_pwg": round(sum(pcf[h] for h in both) / len(both), 4) if both else None,
        "paired_mean_ap": round(sum(acf[h] for h in both) / len(both), 4) if both else None,
        "mean_diff_pwg_minus_ap": round(sum(diffs) / len(diffs), 4) if diffs else None,
        "pwg_gt_ap": wins, "tie": ties, "pwg_lt_ap": loss, "sign_test_z": round(z, 2),
    }
    # similarity-floor sweep (paired): does the null survive noise control?
    sweep = []
    for floor in (0.0, 0.05, 0.10, 0.15, 0.20, 0.30):
        p2, a2 = {}, {}
        for h in cand_all:
            p = score_floor(mw_bags(h), pwg_bags(h), floor)
            a = score_floor(mw_bags(h), ap_bags(h), floor)
            if p is not None:
                p2[h] = p
            if a is not None:
                a2[h] = a
        b2 = sorted(set(p2) & set(a2))
        if not b2:
            continue
        mp = sum(p2[h] for h in b2) / len(b2)
        ma = sum(a2[h] for h in b2) / len(b2)
        sweep.append({"sim_floor": floor, "n_paired": len(b2),
                      "pwg": round(mp, 4), "ap": round(ma, 4), "pwg_minus_ap": round(mp - ma, 4)})
    return {"paired": paired, "sim_floor_sweep": sweep}


def null_concordance(matches, n_other, rng):
    """Mean concordance when the OTHER dict's sense positions are permuted."""
    if len(matches) < MIN_MATCHED:
        return None
    vals = []
    for _ in range(NULLITER):
        perm = list(range(n_other))
        rng.shuffle(perm)
        shuffled = [(i, perm[j]) for (i, j) in matches]
        cf = concordant_fraction(shuffled)
        if cf is not None:
            vals.append(cf)
    return sum(vals) / len(vals) if vals else None


def main():
    census = "--census" in sys.argv
    print("=" * 70)
    print("F10 -- sense-ORDER test: does MW reproduce PWG's order of meanings?")
    print("=" * 70)

    print("\nparsing MW / PWG / AP (grouping records by headword)...")
    mw_rec = group_by_k1(os.path.join(CSL_ORIG, "mw", "mw.txt"))
    pwg_rec = group_by_k1(os.path.join(CSL_ORIG, "pwg", "pwg.txt"))
    ap_rec = group_by_k1(os.path.join(CSL_ORIG, "ap", "ap.txt"))
    print(f"  MW k1={len(mw_rec):,}  PWG k1={len(pwg_rec):,}  AP k1={len(ap_rec):,}")

    print("segmenting senses...")
    mw_s = {k: senses_mw(v) for k, v in mw_rec.items()}
    pwg_s = {k: senses_pwg(v) for k, v in pwg_rec.items()}
    ap_s = {k: senses_ap(v) for k, v in ap_rec.items()}

    # Candidate headwords: >=MIN_SENSES senses in MW AND in the comparison dict.
    cand_pwg = sorted(h for h in (mw_s.keys() & pwg_s.keys())
                      if len(mw_s[h]) >= MIN_SENSES and len(pwg_s[h]) >= MIN_SENSES)
    cand_ap = sorted(h for h in (mw_s.keys() & ap_s.keys())
                     if len(mw_s[h]) >= MIN_SENSES and len(ap_s[h]) >= MIN_SENSES)
    print(f"\ncandidates (>= {MIN_SENSES} senses in both):")
    print(f"  MW vs PWG : {len(cand_pwg):,}")
    print(f"  MW vs AP  : {len(cand_ap):,}")
    if census:
        import statistics
        for name, cand, other in (("PWG", cand_pwg, pwg_s), ("AP", cand_ap, ap_s)):
            mws = [len(mw_s[h]) for h in cand]
            ots = [len(other[h]) for h in cand]
            if mws:
                print(f"  {name}: MW senses/hw median {statistics.median(mws):.0f} "
                      f"max {max(mws)}; {name} senses/hw median {statistics.median(ots):.0f} "
                      f"max {max(ots)}; PWG-german glosses to translate ~ "
                      f"{sum(len(other[h]) for h in cand):,}")
        return

    # Sample pools (deterministic: sorted head) BEFORE translating, so a capped
    # run only pays MT for the headwords it will actually score.
    pwg_pool = cand_pwg if not SAMPLE else cand_pwg[:SAMPLE]
    ap_pool = cand_ap if not SAMPLE else cand_ap[:SAMPLE]

    # --- MT: translate the sampled PWG German sense glosses (offline argos, cached) ---
    import argostranslate.translate as tr
    cache_path = "data/forensic/_f10_sense_tcache.json"
    tcache = {}
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            tcache = json.load(f)
    need = []
    for h in pwg_pool:
        for s in pwg_s[h]:
            if s["de"] not in tcache:
                need.append(s["de"])
    need = sorted(set(need))
    print(f"\ntranslating {len(need):,} unique PWG German sense-glosses (de->en, cached)...")
    for n, de in enumerate(need):
        tcache[de] = tr.translate(de[:1500], "de", "en")
        if (n + 1) % 500 == 0:
            print(f"    {n + 1}/{len(need)}")
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(tcache, f)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(tcache, f)

    def mw_bags(h):
        return [s["en"] | s["skt"] for s in mw_s[h]]

    def pwg_bags(h):
        return [toks_en(tcache.get(s["de"], "")) | s["skt"] for s in pwg_s[h]]

    def ap_bags(h):
        return [s["en"] | s["skt"] for s in ap_s[h]]

    rng = random.Random(SEED)
    rows = []
    examples = []
    summary = {}
    for name, cand, pool, bagf in (("PWG", cand_pwg, pwg_pool, pwg_bags),
                                   ("AP", cand_ap, ap_pool, ap_bags)):
        vals, nulls, msims, matchns = [], [], [], []
        n_ident = 0
        for h in pool:
            cf, matches, n_other, msim = score_headword(mw_bags(h), bagf(h))
            if cf is None:
                continue
            nv = null_concordance(matches, n_other, rng)
            vals.append(cf)
            msims.append(msim)
            matchns.append(len(matches))
            if nv is not None:
                nulls.append(nv)
            if cf == 1.0:
                n_ident += 1
            if name == "PWG" and len(matches) >= 4 and len(examples) < 250:
                examples.append({"headword": h, "n_matched": len(matches),
                                 "mw_senses": len(mw_s[h]), "pwg_senses": len(pwg_s[h]),
                                 "concordance": round(cf, 3)})
        n = len(vals)
        mean_cf = sum(vals) / n if n else None
        mean_null = sum(nulls) / len(nulls) if nulls else None
        summary[name] = {
            "shared_headwords_ge3_senses": len(cand),
            "scored_headwords": n,
            "mean_sense_order_concordance": round(mean_cf, 4) if mean_cf is not None else None,
            "pct_identical_order": round(100 * n_ident / n, 1) if n else None,
            "mean_shuffled_null": round(mean_null, 4) if mean_null is not None else None,
            "mean_matched_pairs": round(sum(matchns) / n, 2) if n else None,
            "mean_match_similarity": round(sum(msims) / n, 4) if n else None,
        }
        rows.append({"vs": name, "is_null": name == "AP", **summary[name]})

    # --- write outputs ---
    os.makedirs("data/forensic", exist_ok=True)
    with open("data/forensic/sense_order_test.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["vs", "is_null", "shared_headwords_ge3_senses",
                                          "scored_headwords", "mean_sense_order_concordance",
                                          "pct_identical_order", "mean_shuffled_null",
                                          "mean_matched_pairs", "mean_match_similarity"])
        w.writeheader()
        w.writerows(rows)
    examples.sort(key=lambda r: (-r["concordance"], -r["n_matched"]))
    with open("data/forensic/sense_order_examples.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["headword", "n_matched", "mw_senses",
                                          "pwg_senses", "concordance"])
        w.writeheader()
        w.writerows(examples)

    print("\n" + "=" * 70)
    print("Sense-ORDER concordance (0.50=random, 1.00=MW reproduces PWG's sense sequence)")
    print("  NULL = Apte (independent English dict); shuffle = permuted-sense floor")
    print("=" * 70)
    print(f"  {'MW vs':6s} {'cand':>6s} {'scored':>7s} {'ORDER':>7s} {'%ident':>7s} "
          f"{'shuffle':>8s} {'match#':>7s} {'matchsim':>9s}")
    for r in rows:
        tag = "  (null)" if r["is_null"] else ""
        print(f"  {r['vs']:6s} {r['shared_headwords_ge3_senses']:>6,} {r['scored_headwords']:>7,} "
              f"{(r['mean_sense_order_concordance'] or 0):>7.3f} "
              f"{(r['pct_identical_order'] or 0):>6.1f}% "
              f"{(r['mean_shuffled_null'] or 0):>8.3f} "
              f"{(r['mean_matched_pairs'] or 0):>7.2f} {(r['mean_match_similarity'] or 0):>9.4f}{tag}")
    pwg = summary["PWG"]["mean_sense_order_concordance"] or 0
    ap = summary["AP"]["mean_sense_order_concordance"] or 0
    shuf = summary["PWG"]["mean_shuffled_null"] or 0
    print(f"\n  MW-vs-PWG {pwg:.3f}  vs  independent Apte {ap:.3f}  vs  shuffle {shuf:.3f}")

    # --- robustness: paired within-headword comparison + similarity-floor sweep ---
    cand_all = sorted(h for h in (mw_s.keys() & pwg_s.keys() & ap_s.keys())
                      if len(mw_s[h]) >= MIN_SENSES and len(pwg_s[h]) >= MIN_SENSES
                      and len(ap_s[h]) >= MIN_SENSES)
    if SAMPLE:
        cand_all = cand_all[:SAMPLE]
    robust = robustness_analyses(mw_bags, pwg_bags, ap_bags, cand_all)
    pd = robust["paired"]
    print("\n  PAIRED (same headwords scored in both, n=%d): MW-vs-PWG %.4f  vs  Apte %.4f  "
          "(diff %+.4f, sign-test z=%.2f)" % (pd["scored_in_both"], pd["paired_mean_pwg"],
          pd["paired_mean_ap"], pd["mean_diff_pwg_minus_ap"], pd["sign_test_z"]))
    print("  similarity-floor sweep (paired PWG vs Apte; excess emerges only on the")
    print("  high-confidence subset where MW's gloss most closely echoes PWG's):")
    print(f"    {'floor':>6s} {'n':>5s} {'PWG':>7s} {'Apte':>7s} {'PWG-Apte':>9s}")
    for s in robust["sim_floor_sweep"]:
        print(f"    >{s['sim_floor']:.2f} {s['n_paired']:>5d} {s['pwg']:>7.4f} "
              f"{s['ap']:>7.4f} {s['pwg_minus_ap']:>+9.4f}")
    with open("data/forensic/sense_order_robustness.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sim_floor", "n_paired", "pwg", "ap", "pwg_minus_ap"])
        w.writeheader()
        w.writerows(robust["sim_floor_sweep"])

    report = {
        "min_senses": MIN_SENSES, "min_matched": MIN_MATCHED, "null_iters": NULLITER,
        "segmentation": {"mw": "sub-<L> records + <div n=to|P|1>", "pwg": "<div> Bedeutungen",
                         "ap": "U+2219 bullets"},
        "alignment": ("position-blind greedy 1:1 match on {English gloss + Sanskrit referent} "
                      "token-Jaccard; PWG German rendered de->en offline (argos, cached); "
                      "citations DELIBERATELY excluded so the result is independent of F5"),
        "pairs": rows,
        "petersburg_order": pwg, "null_apte_order": ap, "shuffle_floor": shuf,
        "robustness": robust,
        "interpretation": (
            "SENSE order is the fourth Boehtlingk clause ('die Reihenfolge der Bedeutungen "
            "einfach abgeschrieben'). MW-vs-PWG concordance is copying only if it clears BOTH "
            "the shuffled-sense floor (matching/forced-order artifact) AND the independent Apte "
            "control (a shared literal->figurative->technical ordering convention). Read the "
            "gradient, not the absolute value."),
    }
    with open("data/forensic/f10_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nWrote sense_order_test.csv, sense_order_examples.csv ({len(examples)}), f10_report.json")
    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source("data/forensic/sense_order_test.csv", "f10_sense_order.py", 10)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
