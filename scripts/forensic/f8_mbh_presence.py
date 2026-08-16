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
   corpus (158k half-verses) with a folded character 4-gram coverage score, anchored by an
   8-gram inverted index (step-6 winnowing: any shared substring ≥ 14 folded chars is found).

## Thresholds (locked before the run, reported honestly)

  coverage ≥ 0.85  -> `present` / exact-ish       (`critical_evidence = quote-exact`)
  coverage ≥ 0.60  -> `present` / recension variant (`quote-fuzzy`)
  otherwise        -> `absent`                     (`none`)
A vulgate half shorter than MIN_HALF folded chars is too formulaic to decide on
(`X uvāca`) and is skipped; a verse whose every half is skipped is `unchecked`, not `absent`.

Outputs (measurements only — no verse bytes; both witnesses stay gitignored):
  data/forensic/mbh_vulgate_critical_presence.csv   83,971 rows, one per vulgate verse
  data/forensic/mbh_citation_presence.csv           one row per extractable PWG/MW MBh citation
  data/forensic/f8_presence_report.json             verdict distribution + spot-check

Run from repo root (after f8_mbh_witnesses.py):  python scripts/forensic/f8_mbh_presence.py
Deps: ../sanskrit-util/py (slp1_simplify).
"""
import sys, os, re, json, csv, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath("scripts/forensic"))
sys.path.insert(0, os.path.abspath("../sanskrit-util/py"))
from _provenance import write_source
from sanskrit_util import slp1_simplify

OUT = "data/forensic"
VULGATE = f"{OUT}/_mbh_vulgate_verses.jsonl"
BORI = f"{OUT}/_mbh_bori_halfverse.jsonl"
CONCORDANCE = f"{OUT}/mbh_vulgate_concordance.csv"
INVENTORY = f"{OUT}/mbh_citation_inventory.csv"

GRAM = 4           # scoring n-gram
ANCHOR = 8         # inverted-index gram
STEP = 6           # index every STEP-th anchor position (winnowing)
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
    inv = defaultdict(list)
    for j, b in enumerate(bori):
        f = b["folded"]
        for i in range(0, max(1, len(f) - ANCHOR + 1), STEP):
            inv[f[i:i + ANCHOR]].append(j)
    return inv


def best_match(half_folded, bori, bsets, inv):
    """Max 4-gram coverage of a CRITICAL half-verse by this vulgate half. Coverage is measured
    on the critical side (|shared| / |critical grams|): a critical half fully contained in the
    vulgate reading scores 1.0, and a long vulgate expansion cannot inflate the score."""
    cand = set()
    for i in range(len(half_folded) - ANCHOR + 1):
        cand.update(inv.get(half_folded[i:i + ANCHOR], ()))
    if not cand:
        return 0.0, ""
    qg = grams(half_folded)
    best, bestloc = 0.0, ""
    for j in cand:
        cg = bsets[j]
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
    print(f"vulgate {len(vul):,} verses · critical {len(bori):,} half-verses")
    bsets = [grams(b["folded"]) for b in bori]
    inv = build_index(bori)
    print(f"anchor index: {len(inv):,} distinct {ANCHOR}-grams")

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
        if k and k % 10000 == 0:
            print(f"  … {k:,}/{len(vul):,}")
        halves = [fold(h) for h in v.get("halves_slp1") or []]
        halves = [h for h in halves if len(h) >= MIN_HALF]
        whole = fold(v.get("slp1"))
        vulgate_state = "present" if whole else "absent"
        if not halves:
            crit_state, evid, score, loc, matched = "unchecked", "no-adjudicable-half", 0.0, "", 0
        else:
            best, bestloc, matched = 0.0, "", 0
            for h in halves:
                sc, lc = best_match(h, bori, bsets, inv)
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
            "etext_url": etext_url(v["parvan"], v["upaparva"], v["adhyaya"], v["shloka"]),
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
                    "critical_score": "", "bori_locus": "",
                    "scan_url": scan_url(p, n), "etext_url": ""})
                continue
            a, s = addr
            r = by_addr.get((p, a, s))
            if r is None:
                cit_rows.append({
                    "dict": c["dict"], "L": c["L"], "headword_slp1": c["headword_slp1"],
                    "parvan": p, "cited_verse": n, "adhyaya": a, "shloka": s,
                    "vulgate": "unchecked", "critical": "unchecked",
                    "verdict": "unchecked/unchecked", "critical_evidence": "witness-missing",
                    "critical_score": "", "bori_locus": "",
                    "scan_url": scan_url(p, n), "etext_url": ""})
                continue
            cit_rows.append({
                "dict": c["dict"], "L": c["L"], "headword_slp1": c["headword_slp1"],
                "parvan": p, "cited_verse": n, "adhyaya": a, "shloka": s,
                "vulgate": r["vulgate"], "critical": r["critical"],
                "verdict": f"{r['vulgate']}/{r['critical']}",
                "critical_evidence": r["critical_evidence"],
                "critical_score": r["critical_score"], "bori_locus": r["bori_locus"],
                "scan_url": scan_url(p, n), "etext_url": r["etext_url"]})

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
        spot.append({
            "dict": c["dict"], "headword_slp1": c["headword_slp1"],
            "cited": f"MBH. {p},{c['cited_verse']}", "resolved": f"{p}.{a}.{s}",
            "roundtrip_calibrated_N": back,
            "roundtrip_ok": bool(back == c["cited_verse"]),
            "vulgate_text_present": c["vulgate"] == "present",
            "verdict": c["verdict"], "bori_locus": c["bori_locus"],
            "critical_score": c["critical_score"], "etext_url": c["etext_url"]})
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
        "thresholds": {"gram": GRAM, "anchor": ANCHOR, "step": STEP,
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
