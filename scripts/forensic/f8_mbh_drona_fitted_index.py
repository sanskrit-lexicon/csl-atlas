"""Phase F8c — MBH Droṇaparva (book 7) fitted-index locus census against the Nīlakaṇṭha
vulgate (H761). Unblocks the fitted-index lane that f8_mbh_verify.py had to defer.

Context — the blocker is refuted
--------------------------------
f8_mbh_census.py / f8_mbh_verify.py recorded the MBH *fitted-index* locus census as BLOCKED:
PWG/MW cite the Calcutta/Nīlakaṇṭha **vulgate** by per-parvan continuous śloka number, and no
free bulk vulgate e-text existed (only BORI-critical GRETIL/DCS ⇒ DEAD_ENDS §8, a structural
dead end for locus arithmetic). As of 11-07-2026 a full Nīlakaṇṭha vulgate was scraped
(83,971 shlokas, 18 parvans, sanatana.in) into CommentaryStrategies — the correct recension,
in the right numbering family. This script runs the deferred lane for one parva.

Method — the f7 Harivaṃśa fitted-index method, reused verbatim, NOT rebuilt
---------------------------------------------------------------------------
Citation extractors are imported from f8_mbh_census (pwg_citations / mw_citations); the
calibration + held-out gate + shuffled-null + classify machinery is imported from
f7_harivamsa_resolve (stem_key, build_index, fit_offsets, held_out, classify, W). This script
only (a) loads the parva-7 vulgate verses as the index target and (b) wires the two together.

  1. Verses. Load book-7 shlokas from the vulgate JSONL, order by (adhyāya, śloka), provisional
     continuous number C = running count. Sandhi/inflection-tolerant token keys via
     sanskrit_util.slp1_simplify + a-stem strip (f7's stem_key).
  2. Anchors. (headword_slp1, MBH. 7,N) pairs from PWG and MW via the f8 extractors, book 7 only.
  3. Calibrate. Fit a robust per-adhyāya constant offset on PWG anchors (median of residuals
     N−C, isotonic-clipped) → Ĉ(verse) = C + offset[adhyāya].
  4. Held-out gate (method invariant 2 — circularity guard). Fit on PWG, hold out MW; report
     MW agreement within ±W under the calibrated map vs a shuffled-N null. **If the gate FAILS
     the classification lane does NOT run** — a failed gate is a real (publishable) negative
     result about vulgate-edition alignment, not a bug.
  5. Classify each PWG `MBH. 7,*` ref corroborated / displaced / absent (headword at cited locus
     ±W), with a shuffled-N null for the corroboration rate.

Outputs (committed measurements — NO verse text; vulgate bytes stay gitignored, rights):
  data/forensic/mbh_drona_vulgate_concordance.csv     per verse: adhyaya, verse, continuous Ĉ, offset
  data/forensic/mbh_drona_fitted_index_offsets.csv    per-adhyāya calibration offsets
  data/forensic/mbh_drona_citation_resolution.csv     per PWG book-7 ref: category, delta, n_loci
  data/forensic/f8_drona_report.json                  held-out + corroboration + null stats

Run from repo root (after CommentaryStrategies vulgate scrape):
    python scripts/forensic/f8_mbh_drona_fitted_index.py
Deps: ../sanskrit-util/py, ../csl-orig, indic_transliteration; the local vulgate JSONL.
"""
import sys, os, re, json, csv, random, statistics
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
from f8_mbh_census import load as load_cites, pwg_citations, mw_citations
from f7_harivamsa_resolve import stem_key, build_index, fit_offsets, held_out, classify, TOKEN, W

BOOK = 7
VJSONL = "../CommentaryStrategies/mahabharata-nilakantha/nilakantha_vulgate_full.jsonl"
OUT = "data/forensic"


def iast_to_slp1(iast):
    """Vulgate mula_iast → SLP1. Strip pāda separators '|', daṇḍas, and śloka-number digits
    the source embeds inline (`...śikhaṇḍinā||1||`)."""
    s = re.sub(r"[|।॥]", " ", iast or "")
    s = re.sub(r"\d+", " ", s)
    return transliterate(s.strip(), sanscript.IAST, sanscript.SLP1)


def load_parva_verses(book):
    """Book-`book` verses as f7-shaped index rows (C, A, toks, simp)."""
    V = []
    for line in open(VJSONL, encoding="utf-8"):
        d = json.loads(line)
        if d.get("parva_no") != book:
            continue
        V.append({"parvan": book, "adhyaya": d["adhyaya"], "verse": d["shloka"],
                  "slp1": iast_to_slp1(d.get("mula_iast") or "")})
    V.sort(key=lambda r: (r["parvan"], r["adhyaya"], r["verse"]))
    adh = {}
    for r in V:
        adh.setdefault((r["parvan"], r["adhyaya"]), len(adh))
    for i, r in enumerate(V):
        r["C"] = i + 1
        r["A"] = adh[(r["parvan"], r["adhyaya"])]
        r["toks"] = set(k for k in (stem_key(t) for t in TOKEN.findall(r["slp1"])) if len(k) >= 3)
        r["simp"] = slp1_simplify(r["slp1"]).replace(" ", "")
    return V, len(adh)


def book_anchors(cites, book, with_verse_only=False):
    """(k1, N) anchors for one book from an f8 census cite list. cites rows: (k1, L, tup);
    PWG tup=(book,verse,form,edition), MW tup=(book,verse,form)."""
    out = []
    for k1, _L, tup in cites:
        b, v = tup[0], tup[1]
        if b == book and v is not None and (k1 or "").strip():
            out.append({"k1": k1.strip(), "n": v})
    return out


def main():
    print(f"F8c — MBH Droṇaparva (book {BOOK}) fitted-index census vs Nīlakaṇṭha vulgate (H761)")
    if not os.path.exists(VJSONL):
        sys.exit(f"vulgate JSONL missing: {VJSONL} — run CommentaryStrategies nilakantha_parser.py scrape")

    V, n_adh = load_parva_verses(BOOK)
    entries, keys = build_index(V)
    total_sh = len(V)
    print(f"vulgate book {BOOK}: {total_sh} shlokas, {n_adh} adhyāyas")

    pwg_cites, _notes = load_cites("PWG", "pwg", pwg_citations)
    mw_cites, _ = load_cites("MW", "mw", mw_citations)
    pwg = book_anchors(pwg_cites, BOOK)
    mw = book_anchors(mw_cites, BOOK)
    print(f"book-{BOOK} anchors: PWG={len(pwg)}  MW={len(mw)}")

    offset, nsup, n_conf = fit_offsets(V, entries, keys, pwg, n_adh)
    for r in V:
        r["chat"] = r["C"] + offset[r["A"]]
    arr = sorted((r["chat"], i) for i, r in enumerate(V))
    chats = [a[0] for a in arr]
    print(f"calibration: confident adhyāyas={n_conf}/{n_adh}  offset {min(offset)}..{max(offset)}")

    # --- 4. held-out gate (fit on PWG, verdict on MW) ---
    ho = held_out(V, arr, chats, mw)
    passed = ho["agreement"] >= 0.30 and ho["agreement"] >= 5 * ho["null_rate"]
    print(f"\nHELD-OUT (MW): agreement={ho['agreement']:.3f} (hits {ho['hits']}/{ho['evaluable']})  "
          f"null={ho['null_rate']:.3f}  ->  {'PASS' if passed else 'FAIL'}")
    print(f"  δ dist (±{W}): {ho['delta_dist']}")

    report = {"book": BOOK, "parva": "Droṇa", "vulgate_source": "sanatana.in (Nīlakaṇṭha vulgate)",
              "n_verses": total_sh, "n_adhyaya": n_adh, "confident_adhyaya": n_conf,
              "anchors_pwg": len(pwg), "anchors_mw": len(mw),
              "held_out": ho, "held_out_pass": passed,
              "offset_min": min(offset), "offset_max": max(offset)}

    # --- offsets + concordance CSVs (always emitted; numbers only) ---
    pa_by_ord = {}
    for r in V:
        pa_by_ord.setdefault(r["A"], (r["parvan"], r["adhyaya"]))
    with open(f"{OUT}/mbh_drona_fitted_index_offsets.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["adhyaya_ordinal", "parvan", "adhyaya", "offset", "n_anchors"])
        for a in range(n_adh):
            p, adh = pa_by_ord[a]
            w.writerow([a, p, adh, offset[a], nsup[a]])
    with open(f"{OUT}/mbh_drona_vulgate_concordance.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["parvan", "adhyaya", "verse", "continuous_sloka", "adhyaya_offset", "adhyaya_n_anchors"])
        for r in sorted(V, key=lambda r: (r["parvan"], r["adhyaya"], r["verse"])):
            w.writerow([r["parvan"], r["adhyaya"], r["verse"], int(round(r["chat"])),
                        offset[r["A"]], nsup[r["A"]]])

    if not passed:
        print("\nHeld-out gate FAILED — index not trustworthy; classification NOT run (a valid exit).")
        report["classification_run"] = False
        json.dump(report, open(f"{OUT}/f8_drona_report.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        write_source(f"{OUT}/mbh_drona_fitted_index_offsets.csv", "f8_mbh_drona_fitted_index.py", 8)
        write_source(f"{OUT}/mbh_drona_vulgate_concordance.csv", "f8_mbh_drona_fitted_index.py", 8)
        print("\nwrote offsets + concordance + f8_drona_report.json (no resolution CSV — gate failed)")
        return

    # --- 5. classify every PWG book-7 ref ---
    res = []
    for a in pwg:
        key = stem_key(a["k1"])
        cat, delta, nl = classify(key, a["n"], V, entries, keys)
        res.append({"lemma": a["k1"], "key": key, "N": a["n"], "cat": cat, "delta": delta, "nloci": nl})
    ev = [r for r in res if len(r["key"]) >= 4]
    cats = Counter(r["cat"] for r in ev)

    # shuffled-N null for the corroboration rate (chance baseline)
    rng = random.Random(20260712)
    Ns = [r["N"] for r in ev]
    nc, nd = [], []
    for _ in range(300):
        sh = Ns[:]
        rng.shuffle(sh)
        c = d = 0
        for r, Nn in zip(ev, sh):
            cc, _, nl = classify(r["key"], Nn, V, entries, keys)
            if cc == "corroborated":
                c += 1
            elif cc == "displaced" and nl <= 3:
                d += 1
        nc.append(c)
        nd.append(d)
    disp_clear = [r for r in ev if r["cat"] == "displaced" and r["nloci"] <= 3]
    corr_pct = cats["corroborated"] / len(ev) * 100 if ev else 0
    null_mean = statistics.mean(nc) if nc else 0
    print(f"\nCLASSIFICATION ({len(ev)} evaluable of {len(res)} PWG book-{BOOK} refs): "
          f"corroborated={cats['corroborated']} displaced={cats['displaced']} absent={cats['absent']}")
    print(f"(A) verse-level corroboration: {cats['corroborated']}/{len(ev)} = {corr_pct:.1f}%  "
          f"vs shuffled-N null {null_mean:.1f} ({null_mean/len(ev)*100:.1f}%)")
    print(f"(B) displaced(<=3 loci): observed {len(disp_clear)}  vs null {statistics.mean(nd):.1f}")

    report.update({"classification_run": True, "evaluable_refs": len(ev), "total_refs": len(res),
                   "corroborated": cats["corroborated"], "displaced": cats["displaced"],
                   "absent": cats["absent"], "corroboration_pct": round(corr_pct, 1),
                   "null_corr_mean": round(null_mean, 1),
                   "null_corr_sd": round(statistics.pstdev(nc), 2) if nc else 0,
                   "null_corr_pct": round(null_mean / len(ev) * 100, 1) if ev else 0,
                   "displaced_clear": len(disp_clear),
                   "null_displaced_clear_mean": round(statistics.mean(nd), 1) if nd else 0})

    with open(f"{OUT}/mbh_drona_citation_resolution.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["headword_slp1", "cited_verse", "category", "delta", "n_loci"])
        for r in sorted(res, key=lambda r: ({"corroborated": 0, "displaced": 1, "absent": 2}.get(r["cat"], 3), r["N"])):
            w.writerow([r["lemma"], r["N"], r["cat"], r["delta"] if r["delta"] is not None else "", r["nloci"]])

    json.dump(report, open(f"{OUT}/f8_drona_report.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for p in ("mbh_drona_fitted_index_offsets.csv", "mbh_drona_vulgate_concordance.csv",
              "mbh_drona_citation_resolution.csv"):
        write_source(f"{OUT}/{p}", "f8_mbh_drona_fitted_index.py", 8)
    print("\nwrote mbh_drona_vulgate_concordance.csv + mbh_drona_fitted_index_offsets.csv + "
          "mbh_drona_citation_resolution.csv + f8_drona_report.json")


if __name__ == "__main__":
    main()
