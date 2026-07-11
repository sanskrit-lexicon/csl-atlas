"""Phase F8b — verify Böhtlingk's MBH correction notes against BORI reading-evidence, with a
deterministic character-fuzzy quote-retrieval lane (H610, roadmap R1/R3).

The fitted-index locus census (f7's core) is BLOCKED for MBH: PWG/MW cite the Calcutta
*vulgate* by per-parvan continuous number, and no free bulk Nilakantha-vulgate e-text exists
(only BORI-critical: GRETIL/DCS/sanskritdocuments; Manipal Sastri-Vavilla is D3-gated
spot-check). Fitting a continuous index against BORI is the measured DEAD_ENDS §8 dead end.

So instead of locus arithmetic this script runs the retrieval lane the roadmap (R1) prescribes:
SLP1-normalized **character-level fuzzy search of the quoted pratīka across the whole harvested
BORI corpus, independent of the cited locus**. Where a correction note quotes the reading it
endorses (`yenāvibruvatā praśnam`, `brūyāsta`), and that reading stands in the critical text,
the note is *confirmed* by reading-evidence — the critical edition (constituted from all
recensions incl. Bombay) is a legitimate witness to whether a reading exists, even though it
cannot place a vulgate śloka number.

Adjudicator: the local GRETIL BORI mirror (SamudraManthanam/GRETIL-1_sanskr/2_epic/mbh, 18
parvans, IAST) — cascade tier "local-GRETIL" (§5). No web fetch; DCS lemma evidence is the
sibling local tier and is noted where the parallel is obvious.

R3 benchmark schema — every verdict row carries: ref_id (stable), evidence_tier
(quote-exact/quote-fuzzy/lemma/none), verdict (confirmed/edition-variant/unresolvable), and
cascade_tier (where the verdict landed).

Outputs:
  data/forensic/mbh_note_verdicts.csv      per verified note: ref_id, locus, evidence, verdict
  data/forensic/f8_verify_report.json      evidence-tier distribution + baseline framing
  data/forensic/_mbh_bori_folded.jsonl     gitignored transcoded corpus cache (rights: derived)

Run from repo root (after f8_mbh_census.py):  python scripts/forensic/f8_mbh_verify.py
Deps: indic_transliteration; ../sanskrit-util/py (slp1_simplify).
"""
import sys, os, re, json, csv, glob
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath("scripts/forensic"))
sys.path.insert(0, os.path.abspath("scripts/L0"))
sys.path.insert(0, os.path.abspath("../sanskrit-util/py"))
from _provenance import write_source
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from sanskrit_util import slp1_simplify

GRETIL = "../SamudraManthanam/GRETIL-1_sanskr/2_epic/mbh"
NOTES = "data/forensic/mbh_correction_notes.csv"
CACHE = "data/forensic/_mbh_bori_folded.jsonl"   # gitignored (derived e-text)
OUT = "data/forensic"
VERSE_LINE = re.compile(r"^([0-9]{2}),([0-9]+)\.([0-9]+)([a-z])?[*0-9_]*\t(.+?)(?:<BR>)?\s*$")


def fold(s):
    """SLP1 → length/retroflex/sibilant-folded, spaceless — the fuzzy match key."""
    return slp1_simplify(s or "").replace(" ", "")


# ---- build / cache the folded BORI corpus -------------------------------------
def build_corpus():
    if os.path.exists(CACHE):
        return [json.loads(l) for l in open(CACHE, encoding="utf-8")]
    rows = []
    for path in sorted(glob.glob(f"{GRETIL}/mbh_*_u.htm")):
        if re.search(r"mbh1-18", path):
            continue
        parvan = int(re.search(r"mbh_(\d+)_u", path).group(1))
        # accumulate pādas into whole verses (pratīkas may span two pādas)
        cur, curtext = None, []
        for raw in open(path, encoding="utf-8", errors="replace"):
            m = VERSE_LINE.match(raw)
            if not m:
                continue
            p, a, v = int(m.group(1)), int(m.group(2)), int(m.group(3))
            iast = re.sub(r"<[^>]+>", " ", m.group(5)).strip()
            if not iast:
                continue
            slp = transliterate(iast, sanscript.IAST, sanscript.SLP1)
            key = (p, a, v)
            if key != cur:
                if cur is not None:
                    rows.append({"loc": f"{cur[0]:02d},{cur[1]}.{cur[2]}",
                                 "folded": fold(" ".join(curtext))})
                cur, curtext = key, []
            curtext.append(slp)
        if cur is not None:
            rows.append({"loc": f"{cur[0]:02d},{cur[1]}.{cur[2]}", "folded": fold(" ".join(curtext))})
    with open(CACHE, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return rows


def ngrams(s, n=4):
    return {s[i:i + n] for i in range(len(s) - n + 1)} if len(s) >= n else {s}


# ---- retrieval ----------------------------------------------------------------
def build_ngram_index(corpus, n=4):
    """corpus verse n-gram sets (once) + inverted 4-gram → verse-index postings, so fuzzy
    scoring touches only verses that share ≥1 n-gram with the pratīka (not all 72k)."""
    vsets = [ngrams(r["folded"], n) for r in corpus]
    inv = {}
    for j, g in enumerate(vsets):
        for gram in g:
            inv.setdefault(gram, []).append(j)
    return vsets, inv


def retrieve(pratika_folded, corpus, concat, offsets, vsets, inv):
    """Return (evidence_tier, locus). Exact substring → quote-exact; else best 4-gram coverage
    over candidate verses (via inverted index), ≥0.60 → quote-fuzzy, ≥0.35 → lemma. Locus-free."""
    import bisect
    if len(pratika_folded) < 6:
        return "short", None
    idx = concat.find(pratika_folded)
    if idx >= 0:
        j = bisect.bisect_right(offsets, idx) - 1
        return "quote-exact", corpus[j]["loc"]
    pg = ngrams(pratika_folded)
    if not pg:
        return "none", None
    cand = Counter()
    for gram in pg:
        for j in inv.get(gram, ()):
            cand[j] += 1
    if not cand:
        return "none", None
    best, bestloc = 0.0, None
    for j, inter in cand.items():
        jac = inter / len(pg)            # coverage of the pratīka's n-grams
        if jac > best:
            best, bestloc = jac, corpus[j]["loc"]
    if best >= 0.85:
        return "quote-fuzzy", bestloc    # near-exact: the pratīka's text stands in the verse
    if best >= 0.50:
        return "lemma", bestloc          # partial: some words present, not the full pratīka
    return "none", None


def pratikas_from_quote(quote, corrected):
    """Candidate QUOTED VERSE fragments to retrieve. A genuine pratīka is connected verse text —
    ≥2 word tokens, no comma. Comma-separated {#…#} are grammatical PARADIGM listings
    (`abruvam, abravīt`), NOT verse quotes, and must be excluded (they fuzzy-match spuriously).
    A lone long compound (≥10 chars) is kept as a distinctive single-word probe. Single short
    forms (abravīt) are too common to retrieve decisively — left to a locus spot-check."""
    cands = []
    for f in re.findall(r"\{#([^#]*)#\}", quote):
        f = f.strip()
        if "," in f:
            continue                                   # paradigm listing, not a verse quote
        toks = [t for t in re.split(r"\s+", f) if re.search(r"[A-Za-z]", t)]
        if len(toks) >= 2 or (len(toks) == 1 and len(re.sub(r"[^A-Za-z]", "", f)) >= 10):
            cands.append(f)
    if corrected and "," not in corrected:
        toks = [t for t in re.split(r"\s+", corrected) if t]
        if len(toks) >= 2 or len(corrected) >= 10:
            cands.append(corrected)
    seen, out = set(), []
    for c in cands:
        k = fold(c)
        if k and len(k) >= 8 and k not in seen:        # need enough chars to be distinctive
            seen.add(k); out.append(c)
    return out


def main():
    print("F8b — MBH note verification via BORI reading-evidence + character-fuzzy retrieval (H610)")
    corpus = build_corpus()
    concat = "|".join(r["folded"] for r in corpus)
    # offsets[j] = start index of corpus[j]'s folded text within concat
    offsets, pos = [], 0
    for r in corpus:
        offsets.append(pos)
        pos += len(r["folded"]) + 1
    print(f"BORI corpus: {len(corpus)} verses, {sum(len(r['folded']) for r in corpus):,} folded chars")
    vsets, inv = build_ngram_index(corpus)
    print(f"inverted 4-gram index: {len(inv):,} distinct grams")

    notes = list(csv.DictReader(open(NOTES, encoding="utf-8")))
    verdicts = []
    for n in notes:
        cands = pratikas_from_quote(n["quote"], n["corrected_slp1"])
        if not cands:
            tier, loc, used = "none", None, ""
        else:
            best = ("none", None, "")
            order = {"quote-exact": 4, "quote-fuzzy": 3, "lemma": 2, "short": 1, "none": 0}
            for c in cands:
                t, l = retrieve(fold(c), corpus, concat, offsets, vsets, inv)
                if order.get(t, 0) > order.get(best[0], 0):
                    best = (t, l, c)
            tier, loc, used = best
        # verdict from evidence tier
        if tier in ("quote-exact", "quote-fuzzy"):
            verdict = "confirmed"          # endorsed reading attested in the critical text
        elif tier == "lemma":
            verdict = "reading-supported"  # root/word present at the retrieved locus, partial
        else:
            verdict = "unresolvable"       # BORI lacks the parallel (vulgate-only or unmatchable)
        ref_id = f"PWG-L{n['L']}-MBH{n['parvan']}.{n['verse']}"
        verdicts.append({
            "ref_id": ref_id, "parvan": n["parvan"], "verse": n["verse"],
            "headword_slp1": n["headword_slp1"], "marker": n["marker"],
            "confidence": n["confidence"], "edition_ref": n["edition_ref"],
            "evidence_tier": tier if tier != "short" else "none",
            "bori_locus": loc or "", "verdict": verdict,
            "cascade_tier": "local-GRETIL" if loc else "none",
            "retrieved_form_slp1": used, "quote": n["quote"][:200]})

    # only notes carrying a retrievable pratīka are "evaluable" for the retrieval lane
    evaluable = [v for v in verdicts if v["evidence_tier"] != "none" or v["retrieved_form_slp1"]]
    tiers = Counter(v["evidence_tier"] for v in verdicts)
    vc = Counter(v["verdict"] for v in verdicts)
    hi = [v for v in verdicts if v["confidence"] == "high"]
    hi_conf = sum(1 for v in hi if v["verdict"] == "confirmed")

    with open(f"{OUT}/mbh_note_verdicts.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ref_id", "parvan", "verse", "headword_slp1", "marker", "confidence",
                    "edition_ref", "evidence_tier", "bori_locus", "verdict", "cascade_tier",
                    "retrieved_form_slp1", "quote"])
        order = {"quote-exact": 0, "quote-fuzzy": 1, "lemma": 2, "none": 3}
        for v in sorted(verdicts, key=lambda v: (order.get(v["evidence_tier"], 9), v["parvan"], int(v["verse"]))):
            w.writerow([v[k] for k in ["ref_id", "parvan", "verse", "headword_slp1", "marker",
                        "confidence", "edition_ref", "evidence_tier", "bori_locus", "verdict",
                        "cascade_tier", "retrieved_form_slp1", "quote"]])

    report = {
        "bori_corpus_verses": len(corpus),
        "notes_total": len(notes),
        "notes_with_retrievable_pratika": len([v for v in verdicts if v["retrieved_form_slp1"] or v["evidence_tier"] != "none"]),
        "evidence_tier_distribution": dict(tiers),
        "verdict_distribution": dict(vc),
        "high_conf_notes": len(hi),
        "high_conf_confirmed": hi_conf,
        # R1 baseline framing: the fitted-index lane is unavailable (no free vulgate), so the
        # retrieval lane is the SOLE lane here — stated honestly, not a suppressed comparison.
        "baseline_note": ("fitted-index lane unavailable (no free bulk Nilakantha-vulgate "
                          "e-text; BORI-only ⇒ DEAD_ENDS §8). Retrieval-only is the sole lane; "
                          "hybrid = retrieval-only for MBH until a vulgate e-text is obtained."),
    }
    json.dump(report, open(f"{OUT}/f8_verify_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    write_source(f"{OUT}/mbh_note_verdicts.csv", "f8_mbh_verify.py", 8)

    print(f"\nevidence tiers: {dict(tiers)}")
    print(f"verdicts: {dict(vc)}")
    print(f"high-conf notes: {len(hi)}  confirmed via retrieval: {hi_conf}")
    print("\n=== validation cases ===")
    for v in verdicts:
        if v["parvan"] == "7" and v["verse"] in ("9283", "9226"):
            print(f"  {v['ref_id']}  {v['marker']:11s} tier={v['evidence_tier']:11s} "
                  f"locus={v['bori_locus'] or '-':10s} verdict={v['verdict']}")
    print("\nwrote mbh_note_verdicts.csv + f8_verify_report.json")


if __name__ == "__main__":
    main()
