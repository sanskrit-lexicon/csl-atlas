"""Phase F8f — answer MG's specimen question about `MBH. 12,8081` in full (H2845).

MG: *"Is `yadā ca pṛthivīṃ sarvāṃ yajamāno 'nuparyagāḥ` in Nilakantha's edition that we have
full etext of? Is it in the Critical edition as well, where? Its absence, if so, is of value
as well."*

The citation is PWG L22170 s.v. {#gA#}, sense {#anupari#} "durchgehen, durchwandern":
    {#yadA ca pfTivIM sarvAM yajamAno 'nuparyagAH#} <ls>MBH. 12,8081</ls>

This script answers it three ways and prints all three, because they disagree — which is
itself the result:

  A. **locus lane** — where the fitted index puts `12,8081`, and what stands there;
  B. **quote lane, vulgate** — where the quoted pratika actually stands in the Nilakantha text;
  C. **quote lane, critical** — whether the same pratika stands anywhere in BORI.

Run from repo root (after f8_mbh_witnesses.py):  python scripts/forensic/f8_mbh_specimen.py
Deps: indic_transliteration; ../sanskrit-util/py (slp1_simplify).
"""
import sys, os, re, json, csv

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath("../sanskrit-util/py"))
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from sanskrit_util import slp1_simplify

OUT = "data/forensic"
VULGATE = f"{OUT}/_mbh_vulgate_verses.jsonl"
BORI = f"{OUT}/_mbh_bori_halfverse.jsonl"
CONCORDANCE = f"{OUT}/mbh_vulgate_concordance.csv"

# the pratika exactly as PWG prints it (SLP1, from csl-orig/v02/pwg/pwg.txt line 109787)
PRATIKA_SLP1 = "yadA ca pfTivIM sarvAM yajamAno 'nuparyagAH"
CITED = (12, 8081)


def fold(s):
    return re.sub(r"[^a-z]", "", slp1_simplify(s or "").lower())


def iast(slp):
    return transliterate(slp, sanscript.SLP1, sanscript.IAST)


def main():
    for p in (VULGATE, BORI):
        if not os.path.exists(p):
            print(f"FATAL: {p} missing — run scripts/forensic/f8_mbh_witnesses.py first.",
                  file=sys.stderr)
            return 2
    probe = fold(PRATIKA_SLP1)
    print(f"specimen pratika (PWG L22170 s.v. gA):\n  SLP1  {PRATIKA_SLP1}\n"
          f"  IAST  {iast(PRATIKA_SLP1)}\n  fold  {probe}\n")

    vul = [json.loads(l) for l in open(VULGATE, encoding="utf-8")]
    by_addr = {(v["parvan"], v["adhyaya"], v["shloka"]): v for v in vul}
    bori = [json.loads(l) for l in open(BORI, encoding="utf-8")]

    addr_to_n, n_to_addr = {}, {}
    with open(CONCORDANCE, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            k = (int(r["parvan"]), int(r["adhyaya"]), int(r["shloka"]))
            addr_to_n[k] = int(r["calibrated_N"])
            n_to_addr.setdefault((int(r["parvan"]), int(r["calibrated_N"])), k)

    result = {"pratika_slp1": PRATIKA_SLP1, "pratika_iast": iast(PRATIKA_SLP1),
              "cited": f"MBH. {CITED[0]},{CITED[1]}"}

    # --- A. locus lane -------------------------------------------------------
    addr = n_to_addr.get(CITED)
    print("A. LOCUS LANE — where the fitted index sends MBH. 12,8081")
    if addr:
        v = by_addr.get(addr)
        print(f"   calibrated_N {CITED[1]} -> parvan {addr[0]}, adhyaya {addr[1]}, "
              f"shloka {addr[2]} (continuous_C {v['C'] if v else '?'})")
        if v:
            print(f"   text there: {iast(v['slp1'])[:120]}")
        hit = bool(v and probe[:20] in fold(v["slp1"]))
        print(f"   contains the quoted pratika? {'YES' if hit else 'NO'}")
        result["locus_lane"] = {"address": f"{addr[0]}.{addr[1]}.{addr[2]}",
                                "contains_pratika": hit,
                                "text_iast": iast(v["slp1"]) if v else ""}
    else:
        print("   calibrated_N 8081 does not resolve in parvan 12")
        result["locus_lane"] = {"address": None, "contains_pratika": False}

    # --- B. quote lane, vulgate ---------------------------------------------
    print("\nB. QUOTE LANE, VULGATE — where the pratika actually stands")
    vhits = [v for v in vul if probe[:24] in fold(v["slp1"])]
    for v in vhits:
        n = addr_to_n.get((v["parvan"], v["adhyaya"], v["shloka"]))
        print(f"   {v['parvan']}.{v['adhyaya']}.{v['shloka']}  id={v['id']}  "
              f"continuous_C={v['C']}  calibrated_N={n}")
        print(f"     {iast(v['slp1'])[:160]}")
    result["vulgate_quote_lane"] = [{
        "address": f"{v['parvan']}.{v['adhyaya']}.{v['shloka']}", "id": v["id"],
        "continuous_C": v["C"],
        "calibrated_N": addr_to_n.get((v["parvan"], v["adhyaya"], v["shloka"])),
        "text_iast": iast(v["slp1"]),
    } for v in vhits]
    result["vulgate_state"] = "present" if vhits else "absent"
    if vhits:
        d = CITED[1] - (result["vulgate_quote_lane"][0]["calibrated_N"] or 0)
        print(f"   >> vulgate = PRESENT; cited 12,{CITED[1]} vs fitted "
              f"calibrated_N {result['vulgate_quote_lane'][0]['calibrated_N']} — delta {d}")
        result["cited_minus_fitted_N"] = d

    # --- C. quote lane, critical --------------------------------------------
    print("\nC. QUOTE LANE, CRITICAL (BORI) — exact, then best fuzzy")
    exact = [b["loc"] for b in bori if probe[:24] in b["folded"]]
    print(f"   exact substring hits: {exact if exact else 'NONE'}")
    qg = {probe[i:i + 4] for i in range(len(probe) - 3)}
    best, bestloc, bestfold = 0.0, "", ""
    for b in bori:
        cg = {b["folded"][i:i + 4] for i in range(len(b["folded"]) - 3)}
        if not cg:
            continue
        cov = len(cg & qg) / len(cg)
        if cov > best:
            best, bestloc, bestfold = cov, b["loc"], b["folded"]
    print(f"   best 4-gram coverage: {best:.3f} at {bestloc}")
    print(f"     folded: {bestfold[:120]}")
    crit = "present" if (exact or best >= 0.60) else "absent"
    print(f"   >> critical = {crit.upper()}")
    result["critical_state"] = crit
    result["critical_exact_hits"] = exact
    result["critical_best"] = {"coverage": round(best, 3), "locus": bestloc}

    # a control: is the fitted locus's own verse in BORI? (guards against a broken lane)
    if addr and by_addr.get(addr):
        ctrl = fold(by_addr[addr]["slp1"])
        cg_hit = [b["loc"] for b in bori if len(b["folded"]) >= 16 and b["folded"][:16] in ctrl]
        print(f"\n   control — the verse at the fitted locus is in BORI at: "
              f"{cg_hit[:3] if cg_hit else 'NOT FOUND'}")
        result["control_fitted_locus_in_bori"] = cg_hit[:3]

    result["verdict"] = f"{result['vulgate_state']}/{result['critical_state']}"
    print(f"\nFOUR-STATE VERDICT for the specimen: {result['verdict']}")
    json.dump(result, open(f"{OUT}/f8_specimen_mbh_12_8081.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"wrote {OUT}/f8_specimen_mbh_12_8081.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
