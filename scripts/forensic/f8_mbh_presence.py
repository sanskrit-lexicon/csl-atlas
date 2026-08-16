"""Phase F8e — the four-state vulgate/critical PRESENCE verdict for every MBh citation (H2845).

MG's question, in full: *"can it link ALSO to the etext? … Is `yadā ca pṛthivīṃ sarvāṃ
yajamāno 'nuparyagāḥ` in Nilakantha's edition that we have full etext of? Is it in the Critical
edition as well, where? Its absence, if so, is of value as well."*

Absence is only "of value" if it is PROVEN. So every citation gets one of four states per
witness, and **`unchecked` is never collapsed into `absent`**:

  vulgate  critical   reading
  present  present    ordinary — the verse stands in both recensions
  present  absent     A FINDING — vulgate-only; PWG cites what BORI relegated to its apparatus
  absent   unchecked  the fitted locus lands on a verse the vulgate does not have there
  unchecked …         the witness was not staged / the locus did not resolve — NOT absence

## Lanes

1. **Locus lane (numbers).** `mbh_vulgate_concordance.csv` maps (parvan, calibrated_N) — the
   per-parvan continuous number PWG/MW actually print — to (adhyaya, shloka). Always read
   `calibrated_N`, never `continuous_C`: for `MBH. 12,8081` the raw continuous column says
   Santi 226.10, the fitted index corrects it to Santi 226.6.
2. **Vulgate lane (text).** `_mbh_vulgate_verses.jsonl` (staged by f8_mbh_witnesses.py) gives
   the Nilakantha mula at that address. Non-empty mula ⇒ `vulgate=present`.
3. **Critical lane (text, CONTENT-ADDRESSED).** Per BORI_CRITICAL_SOURCE.md, vulgate↔critical
   alignment must be **by verse content, not by number** — the vulgate carries exactly the
   passages the critical edition banished to its apparatus, so śloka numbers diverge
   structurally. Each vulgate half-verse is therefore searched against the WHOLE critical
   corpus (158k half-verses) by two-stage retrieval: a 12-gram shingle index indexed at step 4
   and queried at step 1 (so any shared substring ≥ 15 folded chars is guaranteed to surface a
   candidate), then an exact 4-gram coverage score on the few best candidates.

   Shingles whose posting list exceeds MAX_POSTING are dropped from the index: a 12-gram shared
   by more than 40 half-verses of the epic is formulaic (`bharatarsabha`, `mahabaho`) and
   carries no identification value, while keeping it would make the sweep quadratic.

## Thresholds (locked before the run, reported honestly)

  coverage ≥ 0.85  -> `present` / exact-ish       (`critical_evidence = quote-exact`)
  coverage ≥ 0.60  -> `present` / recension variant (`quote-fuzzy`)
  otherwise        -> `absent`                     (`none`)
A vulgate half shorter than MIN_HALF folded chars is too formulaic to decide on
(`X uvāca`) and is skipped; a verse whose every half is skipped is `unchecked`, not `absent`.

## What the citation-level verdict is, and is not

The verse-level table is unconditional: it compares two texts. The citation-level table is
**conditional on the fitted locus being right**, and the fitted index's own held-out accuracy is
0.552 (MBH_CITATION_RESOLUTION_CENSUS.md). The specimen `MBH. 12,8081` is a live counter-example:
its quoted pratika actually stands 110 calibrated ślokas away from where the index sends it. So
read `present/absent` at citation level as "the verse the fitted index points at is vulgate-only",
not yet as "PWG cited a verse BORI rejects" — the quote lane
(`scripts/forensic/f8_mbh_quote_lane.py`) is what upgrades one to the other.

Outputs (measurements only — no verse bytes; both witnesses stay gitignored):
  data/forensic/mbh_vulgate_critical_presence.csv   83,971 rows, one per vulgate verse
  data/forensic/mbh_citation_presence.csv           one row per extractable PWG/MW MBh citation
  data/forensic/mbh_presence_spotcheck.csv          30 sampled loci WITH both rendered links
  data/forensic/f8_presence_report.json             verdict distribution + spot-check

The scan and etext URLs are **functions** (`scan_url`, `etext_url`), not stored columns: baking
90-char URLs into 154k rows would add ~14 MB of derivable text, and the citation renderer — not
the dataset — is where a link belongs. The spot-check CSV carries them rendered so the join is
demonstrable.

Run from repo root (after f8_mbh_witnesses.py):  python scripts/forensic/f8_mbh_presence.py
Deps: ../sanskrit-util/py (slp1_simplify).
"""
import sys, os, re, json, csv, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath("scripts/L0"))
sys.path.insert(0, os.path.abspath("../sanskrit-util/py"))
from _provenance import write_source
from sanskrit_util import slp1_simplify

OUT = "data/forensic"
VULGATE = f"{OUT}/_mbh_vulgate_verses.jsonl"
BORI = f"{OUT}/_mbh_bori_halfverse.jsonl"
CONCORDANCE = f"{OUT}/mbh_vulgate_concordance.csv"
INVENTORY = f"{OUT}/mbh_citation_inventory.csv"

GRAM = 4           # scoring n-gram
ANCHOR = 12        # shingle length of the inverted index
STEP = 4           # index every STEP-th shingle position (query steps by 1)
MAX_POSTING = 40   # drop shingles shared by more half-verses than this — formulaic, not identifying
TOP_CAND = 4       # how many anchor-hit leaders get the exact coverage score
MIN_HALF = 16      # folded chars below which a half-verse is too formulaic to adjudicate
EXACTISH = 0.85
FUZZY = 0.60
SPOTCHECK_N = 30
SEED = 2845

PARVA_SLUG = {
    1: "adiparva", 2: "sabhaparva", 3: "vanaparva", 4: "virataparva", 5: "udyogaparva",
    6: "bhishmaparva", 7: "dronaparva", 8: "karnaparva", 9: "shalyaparva", 10: "sauptikaparva",
    11: "striparva", 12: "shantiparva", 13: "anushasanaparva", 14: "ashwamedhikaparva",
    15: "ashramavasikaparva", 16: "mausalaparva", 17: "mahaprasthanikaparva",
    18: "swargarohanaparva",
}
ETEXT_BASE = "https://sanatana.in/mahabharata/listing/parva/"
SCAN_BASE = "https://sanskrit-lexicon-scans.github.io/mbhcalc?"


def fold(s):
    return re.sub(r"[^a-z]", "", slp1_simplify(s or "").lower())


def grams(s, n=GRAM):
    return {s[i:i + n] for i in range(len(s) - n + 1)} if len(s) >= n else ({s} if s else set())


def etext_url(parvan, upaparva, adhyaya, shloka):
    """Deep link into the sanatana.in Nilakantha reader.

    The site was rebuilt in 2026 around `listing/parva/<slug>?id=P..._U..._A..._S...`; the old
    `listing/getParvaByPage/` AJAX endpoint now returns an empty body. The id is exactly the
    `div.shloka` id the harvest recorded, so the link is verifiable against our own data."""
    slug = PARVA_SLUG.get(parvan)
    if not slug:
        return ""
    return (f"{ETEXT_BASE}{slug}?id=P{parvan:02d}_U{upaparva:02d}"
            f"_A{adhyaya:03d}_S{shloka:03d}")


def scan_url(parvan, cited_verse):
    """The Cologne scan link that already ships today (ls_links.py `mbhcalc`)."""
    return f"{SCAN_BASE}{parvan}.{cited_verse}"


# ---- critical-corpus index ----------------------------------------------------
def build_index(bori):
    """shingle -> [half-verse index]. Formulaic shingles (posting list > MAX_POSTING) are
    dropped: they identify nothing and would dominate every candidate set."""
    inv = defaultdict(list)
    for j, b in enumerate(bori):
        f = b["folded"]
        for i in range(0, max(1, len(f) - ANCHOR + 1), STEP):
            inv[f[i:i + ANCHOR]].append(j)
    return {k: v for k, v in inv.items() if len(v) <= MAX_POSTING}


def best_match(half_folded, bori, inv):
    """Max 4-gram coverage of a CRITICAL half-verse by this vulgate half. Coverage is measured
    on the critical side (|shared| / |critical grams|): a critical half fully contained in the
    vulgate reading scores 1.0, and a long vulgate expansion cannot inflate the score."""
    hits = Counter()
    for i in range(len(half_folded) - ANCHOR + 1):
        for j in inv.get(half_folded[i:i + ANCHOR], ()):
            hits[j] += 1
    if not hits:
        return 0.0, ""
    qg = grams(half_folded)
    best, bestloc = 0.0, ""
    for j, _ in hits.most_common(TOP_CAND):
        cg = grams(bori[j]["folded"])
        if not cg:
            continue
        cov = len(cg & qg) / len(cg)
        if cov > best:
            best, bestloc = cov, bori[j]["loc"]
    return best, bestloc


def main():
    print("F8e — MBh vulgate/critical four-state presence verdict (H2845)")
    for p in (VULGATE, BORI):
        if not os.path.exists(p):
            print(f"FATAL: {p} missing — run scripts/forensic/f8_mbh_witnesses.py first.",
                  file=sys.stderr)
            return 2

    vul = [json.loads(l) for l in open(VULGATE, encoding="utf-8")]
    bori = [json.loads(l) for l in open(BORI, encoding="utf-8")]
    print(f"vulgate {len(vul):,} verses · critical {len(bori):,} half-verses", flush=True)
    inv = build_index(bori)
    print(f"shingle index: {len(inv):,} identifying {ANCHOR}-grams "
          f"(posting cap {MAX_POSTING})", flush=True)

    # concordance: (parvan, adhyaya, shloka) -> calibrated_N, and (parvan, N) -> address
    addr_to_n, n_to_addr = {}, {}
    with open(CONCORDANCE, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            p, a, s = int(r["parvan"]), int(r["adhyaya"]), int(r["shloka"])
            n = int(r["calibrated_N"])
            addr_to_n[(p, a, s)] = n
            n_to_addr.setdefault((p, n), (a, s))
    print(f"concordance: {len(addr_to_n):,} addressed verses, "
          f"{len(n_to_addr):,} distinct calibrated numbers")

    # ---- lane 2+3 over every vulgate verse -----------------------------------
    rows = []
    for k, v in enumerate(vul):
        if k and k % 5000 == 0:
            print(f"  … {k:,}/{len(vul):,}", flush=True)
        halves = [fold(h) for h in v.get("halves_slp1") or []]
        halves = [h for h in halves if len(h) >= MIN_HALF]
        whole = fold(v.get("slp1"))
        vulgate_state = "present" if whole else "absent"
        if not halves:
            crit_state, evid, score, loc, matched = "unchecked", "no-adjudicable-half", 0.0, "", 0
        else:
            best, bestloc, matched = 0.0, "", 0
            for h in halves:
                sc, lc = best_match(h, bori, inv)
                if sc >= FUZZY:
                    matched += 1
                if sc > best:
                    best, bestloc = sc, lc
            score, loc = round(best, 3), bestloc
            if best >= EXACTISH:
                crit_state, evid = "present", "quote-exact"
            elif best >= FUZZY:
                crit_state, evid = "present", "quote-fuzzy"
            else:
                crit_state, evid = "absent", "none"
        rows.append({
            "parvan": v["parvan"], "adhyaya": v["adhyaya"], "shloka": v["shloka"],
            "upaparva": v["upaparva"], "continuous_C": v["C"],
            "calibrated_N": addr_to_n.get((v["parvan"], v["adhyaya"], v["shloka"]), ""),
            "vulgate": vulgate_state, "critical": crit_state,
            "critical_evidence": evid, "critical_score": score, "bori_locus": loc,
            "n_halves": len(halves), "n_halves_matched": matched,
        })

    with open(f"{OUT}/mbh_vulgate_critical_presence.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    by_addr = {(r["parvan"], r["adhyaya"], r["shloka"]): r for r in rows}
    print(f"wrote mbh_vulgate_critical_presence.csv ({len(rows):,} rows)")

    # ---- lane 1: join onto PWG/MW's own citations -----------------------------
    cites, cit_rows = 0, []
    with open(INVENTORY, encoding="utf-8") as f:
        for c in csv.DictReader(f):
            try:
                p, n = int(c["parvan"]), int(c["verse"])
            except (TypeError, ValueError):
                continue
            cites += 1
            addr = n_to_addr.get((p, n))
            if not addr:
                cit_rows.append({
                    "dict": c["dict"], "L": c["L"], "headword_slp1": c["headword_slp1"],
                    "parvan": p, "cited_verse": n, "adhyaya": "", "shloka": "",
                    "vulgate": "unchecked", "critical": "unchecked",
                    "verdict": "unresolved-locus", "critical_evidence": "locus-out-of-range",
                    "critical_score": "", "bori_locus": ""})
                continue
            a, s = addr
            r = by_addr.get((p, a, s))
            if r is None:
                cit_rows.append({
                    "dict": c["dict"], "L": c["L"], "headword_slp1": c["headword_slp1"],
                    "parvan": p, "cited_verse": n, "adhyaya": a, "shloka": s,
                    "vulgate": "unchecked", "critical": "unchecked",
                    "verdict": "unchecked/unchecked", "critical_evidence": "witness-missing",
                    "critical_score": "", "bori_locus": ""})
                continue
            cit_rows.append({
                "dict": c["dict"], "L": c["L"], "headword_slp1": c["headword_slp1"],
                "parvan": p, "cited_verse": n, "adhyaya": a, "shloka": s,
                "vulgate": r["vulgate"], "critical": r["critical"],
                "verdict": f"{r['vulgate']}/{r['critical']}",
                "critical_evidence": r["critical_evidence"],
                "critical_score": r["critical_score"], "bori_locus": r["bori_locus"]})

    with open(f"{OUT}/mbh_citation_presence.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cit_rows[0].keys()))
        w.writeheader()
        w.writerows(cit_rows)
    print(f"wrote mbh_citation_presence.csv ({len(cit_rows):,} rows of {cites:,} numeric citations)")

    # ---- held-out spot check: 30 random RESOLVED loci -------------------------
    rnd = random.Random(SEED)
    pool = [c for c in cit_rows if c["adhyaya"] != ""]
    sample = rnd.sample(pool, min(SPOTCHECK_N, len(pool)))
    spot = []
    for c in sample:
        p, a, s = c["parvan"], c["adhyaya"], c["shloka"]
        back = addr_to_n.get((p, a, s))
        vv = by_addr.get((p, a, s))
        spot.append({
            "dict": c["dict"], "headword_slp1": c["headword_slp1"],
            "cited": f"MBH. {p},{c['cited_verse']}", "resolved": f"{p}.{a}.{s}",
            "roundtrip_calibrated_N": back,
            "roundtrip_ok": bool(back == c["cited_verse"]),
            "vulgate_text_present": c["vulgate"] == "present",
            "verdict": c["verdict"], "bori_locus": c["bori_locus"],
            "critical_score": c["critical_score"],
            "scan_url": scan_url(p, c["cited_verse"]),
            "etext_url": etext_url(p, vv["upaparva"] if vv else 0, a, s)})
    with open(f"{OUT}/mbh_presence_spotcheck.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(spot[0].keys()))
        w.writeheader()
        w.writerows(spot)
    rt_ok = sum(1 for x in spot if x["roundtrip_ok"])
    tx_ok = sum(1 for x in spot if x["vulgate_text_present"])
    print(f"spot check ({len(spot)} loci): locus round-trip {rt_ok}/{len(spot)}, "
          f"vulgate text present {tx_ok}/{len(spot)}")

    # ---- report ---------------------------------------------------------------
    vc = Counter(f"{r['vulgate']}/{r['critical']}" for r in rows)
    cc = Counter(c["verdict"] for c in cit_rows)
    per_parvan = defaultdict(Counter)
    for r in rows:
        per_parvan[r["parvan"]][f"{r['vulgate']}/{r['critical']}"] += 1
    report = {
        "vulgate_verses": len(vul), "critical_half_verses": len(bori),
        "thresholds": {"gram": GRAM, "shingle": ANCHOR, "index_step": STEP,
                       "max_posting": MAX_POSTING, "top_candidates": TOP_CAND,
                       "min_half_folded_chars": MIN_HALF,
                       "exactish": EXACTISH, "fuzzy": FUZZY},
        "verse_level_verdicts": dict(vc),
        "citation_level_verdicts": dict(cc),
        "citations_seen": cites, "citation_rows": len(cit_rows),
        "per_parvan": {str(p): dict(c) for p, c in sorted(per_parvan.items())},
        "spotcheck": {"n": len(spot), "seed": SEED,
                      "locus_roundtrip_ok": rt_ok, "vulgate_text_present": tx_ok},
        "integrity_note": ("`unchecked` is emitted whenever the locus does not resolve or no "
                           "half-verse clears MIN_HALF; it is never written as `absent`."),
    }
    json.dump(report, open(f"{OUT}/f8_presence_report.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for path in ("mbh_vulgate_critical_presence.csv", "mbh_citation_presence.csv",
                 "mbh_presence_spotcheck.csv"):
        write_source(f"{OUT}/{path}", "f8_mbh_presence.py", 8)

    print(f"\nverse-level: {dict(vc)}")
    print(f"citation-level: {dict(cc)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
