"""Phase F7b — resolve PWG/MW HARIV. citations against the harvested vulgate, calibrate a
continuous index, run the shared-erroneous-citation test (H488).

Pipeline
--------
1. Anchors. Extract (headword_slp1, HARIV. N) from csl-orig PWG and MW. Reuses
   parse_cslorig.iter_entries for entry segmentation; captures BOTH the full <ls>HARIV. N</ls>
   and the abbreviated <ls n="HARIV.">N</ls> continuation form (the forensic _LS regex misses
   the latter). Skips parvan-style "3,65" (comma) — the numbering under test is continuous.
2. Index. Order the harvested vulgate verses by (parvan, adhyāya, verse); provisional
   continuous number C = running count. Sandhi/inflection-tolerant matching via
   sanskrit-util slp1_simplify (fold retroflex/sibilant/visarga distinctions) + a-stem strip,
   prefix-matched against near-whole verse tokens.
3. Calibrate. Kinjawadekar's chapter division differs from Calcutta's (55/128/135 vs 55/81/135)
   and ~6% of ślokas are uncovered, so C drifts from the cited Calcutta N. Fit a per-adhyāya
   constant offset (median of anchor residuals N-C, robust), clipped to a monotone
   confident-baseline envelope so a few mismatched anchors cannot inject garbage offsets. The
   within-chapter verse order matches Calcutta, so a constant per-chapter offset is near-exact:
   calibrated number  Ĉ(verse) = C + offset[adhyāya].
4. Held-out check (circularity guard). Fit on PWG, hold out MW. Report the fraction of MW
   anchors whose headword sits within ±W of its cited N under the calibrated map, vs a
   shuffled-N null. This is the pass/fail gate — the offset is fitted with robust medians and
   unique-match (N-independent) anchors, and the verdict rests on held-out MW, not the fit.
5. Shared-error test. For each shared rare HARIV. (lemma, N) cited by BOTH dictionaries, locate
   the lemma in the calibrated vulgate:
     corroborated : a locus with |Ĉ-N|<=W  -> citation correct within calibration noise
     displaced    : lemma present only >W from N -> candidate shared error (offset δ)
     absent       : no strict locus (verse among the uncovered ~6%, or a compound the matcher
                    can't see) -> inconclusive
   Reports verse-level corroboration vs a shuffled-N null (the positive result) and the
   displaced shortlist with its own null (a rare word's single locus is usually >W from an
   arbitrary N, so 'displaced' is EXPECTED and is NOT by itself a shared-error proof).

Outputs (committed measurements — NOT the e-text bytes):
  data/forensic/harivamsa_vulgate_concordance.csv          per-verse address -> continuous śloka N
  data/forensic/harivamsa_continuous_index_offsets.csv     per-adhyāya calibration offsets
  data/forensic/harivamsa_shared_citation_resolution.csv   per shared-ref classification
  data/forensic/f7_report.json                             held-out + corroboration + null stats

Run from repo root (after f7_harivamsa_harvest.py):
    python scripts/forensic/f7_harivamsa_resolve.py
Deps: ../sanskrit-util/py on sys.path (sibling repo, as with ../csl-orig).
"""
import sys, os, re, json, csv, bisect, random, statistics
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath("scripts/forensic"))
sys.path.insert(0, os.path.abspath("scripts/L0"))
sys.path.insert(0, os.path.abspath("../sanskrit-util/py"))
from parse_cslorig import iter_entries, CSL_ORIG
from _provenance import write_source
from sanskrit_util import slp1_simplify

VERSES = "data/forensic/_harivamsa_verses.jsonl"     # gitignored input from f7_harivamsa_harvest
POOL = "data/forensic/shared_rare_citations.csv"
W = 3
TOKEN = re.compile(r"[A-Za-z]+")
LS = re.compile(r'<ls(?:\s+n="([^"]*)")?\s*>(.*?)</ls>', re.DOTALL)
TAG = re.compile(r"<[^>]*>")
WS = re.compile(r"\s+")


def stem_key(slp1):
    s = slp1_simplify(slp1 or "")
    if len(s) >= 5 and s.endswith("a"):
        s = s[:-1]
    return s


# ---- 1. anchors ---------------------------------------------------------------
def harivamsa_numbers(body):
    for attr, payload in LS.findall(body):
        attr = (attr or "").strip()
        payload = WS.sub(" ", TAG.sub("", payload)).strip()
        if payload.upper().startswith("HARIV"):
            numpart = payload[payload.find(".") + 1:] if "." in payload else ""
        elif attr.upper().startswith("HARIV"):
            if "," in attr:
                continue
            numpart = payload
        else:
            continue
        m = re.fullmatch(r"(\d{1,5})", numpart.strip())
        if m:
            yield int(m.group(1))


def load_anchors(code, fname):
    src = os.path.join(CSL_ORIG, code.lower(), f"{fname}.txt")
    rows = []
    for e in iter_entries(src):
        k1 = (e["k1"] or "").strip()
        if not k1:
            continue
        for n in harivamsa_numbers(e["body"]):
            rows.append({"k1": k1, "n": n})
    return rows


# ---- 2. verses + index --------------------------------------------------------
def load_verses():
    V = [json.loads(l) for l in open(VERSES, encoding="utf-8")]
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


def build_index(V):
    entries = [(k, i) for i, r in enumerate(V) for k in r["toks"]]
    entries.sort()
    return entries, [e[0] for e in entries]


def strict_matches(key, entries, keys, max_extra=3):
    if len(key) < 4:
        return set()
    lo = bisect.bisect_left(keys, key)
    out, n, i = set(), len(keys), bisect.bisect_left(keys, key)
    while i < n and keys[i].startswith(key):
        if len(keys[i]) - len(key) <= max_extra:
            out.add(entries[i][1])
        i += 1
    return out


# ---- 3. calibration -----------------------------------------------------------
def _mad(xs, med):
    return statistics.median([abs(x - med) for x in xs]) if xs else 999


def isotonic(points):
    xs = [p[0] for p in points]
    vals = []
    for _, y, w in points:
        blk = [y, w, 1]
        while vals and vals[-1][0] > blk[0]:
            pm, pw, pl = vals.pop()
            nw = pw + blk[1]
            blk = [(pm * pw + blk[0] * blk[1]) / nw, nw, pl + blk[2]]
        vals.append(blk)
    fitted = []
    for m, w, l in vals:
        fitted += [m] * l
    return dict(zip(xs, fitted))


def fit_offsets(V, entries, keys, anchors, n_adh):
    C_by_i = [r["C"] for r in V]
    resid_u, resid_all = defaultdict(list), defaultdict(list)
    for a in anchors:
        key = stem_key(a["k1"])
        if len(key) < 4:
            continue
        m = strict_matches(key, entries, keys)
        if not m or len(m) > 5:
            continue
        N = a["n"]
        best = min(m, key=lambda i: abs(C_by_i[i] - N))
        resid_all[V[best]["A"]].append(N - V[best]["C"])
        if len(m) == 1:
            j = next(iter(m))
            resid_u[V[j]["A"]].append(N - V[j]["C"])
    direct, nsup = [None] * n_adh, [0] * n_adh
    conf_pts = []
    for a in range(n_adh):
        pool = resid_u[a] if len(resid_u[a]) >= 2 else resid_all[a]
        if not pool:
            continue
        med = int(round(statistics.median(pool)))
        direct[a] = med
        nsup[a] = len(pool)
        if len(pool) >= 2 and _mad(pool, med) <= 6:
            conf_pts.append((a, med, len(pool)))
    iso = isotonic(conf_pts)
    conf = {a: int(round(iso[a])) for a in iso}
    ca = sorted(conf)

    def baseline(a):
        below = [x for x in ca if x <= a]
        above = [x for x in ca if x >= a]
        if below and above and below[-1] != above[0]:
            a0, a1 = below[-1], above[0]
            return conf[a0] + (conf[a1] - conf[a0]) * (a - a0) / (a1 - a0)
        if a in conf:
            return conf[a]
        return conf[below[-1]] if below else conf[above[0]]

    TOL = 40
    offset = [0] * n_adh
    for a in range(n_adh):
        B = baseline(a)
        offset[a] = direct[a] if (direct[a] is not None and abs(direct[a] - B) <= TOL) else int(round(B))
    return offset, nsup, len(ca)


def match_in_verse(V, i, key):
    r = V[i]
    return any(t.startswith(key) and len(t) - len(key) <= 4 for t in r["toks"]) or key in r["simp"]


def window(arr, chats, N, w=W):
    return arr[bisect.bisect_left(chats, N - w):bisect.bisect_right(chats, N + w)]


def held_out(V, arr, chats, anchors):
    hits = ev = null_hits = null_ev = 0
    deltas = []
    rng = random.Random(20260710)
    maxN = int(max(c for c, _ in arr))
    for a in anchors:
        key = stem_key(a["k1"])
        if len(key) < 4:
            continue
        N = a["n"]
        win = window(arr, chats, N)
        if not win:
            continue
        ev += 1
        found = next((int(round(c - N)) for c, i in win if match_in_verse(V, i, key)), None)
        if found is not None:
            hits += 1
            deltas.append(max(-W, min(W, found)))
        Np = rng.randint(1 + W, maxN - W)
        if abs(Np - N) >= 50:
            wp = window(arr, chats, Np)
            if wp:
                null_ev += 1
                if any(match_in_verse(V, i, key) for _, i in wp):
                    null_hits += 1
    return {"evaluable": ev, "hits": hits, "agreement": hits / ev if ev else 0,
            "null_evaluable": null_ev, "null_hits": null_hits,
            "null_rate": null_hits / null_ev if null_ev else 0,
            "delta_dist": dict(sorted(Counter(deltas).items()))}


# ---- 5. shared-error test -----------------------------------------------------
def loci(key, V, entries, keys, max_extra=3):
    if len(key) < 4:
        return []
    out, n, i = [], len(keys), bisect.bisect_left(keys, key)
    while i < n and keys[i].startswith(key):
        if len(keys[i]) - len(key) <= max_extra:
            out.append(V[entries[i][1]]["chat"])
        i += 1
    return sorted(set(out))


def classify(key, N, V, entries, keys):
    ls = loci(key, V, entries, keys)
    if not ls:
        return "absent", None, 0
    near = [c for c in ls if abs(c - N) <= W]
    if near:
        return "corroborated", int(round(min(near, key=lambda c: abs(c - N)) - N)), len(ls)
    nearest = min(ls, key=lambda c: abs(c - N))
    return "displaced", int(round(nearest - N)), len(ls)


def load_shared():
    out = []
    for r in csv.DictReader(open(POOL, encoding="utf-8")):
        m = re.search(r"HARIV\.\s*(\d+)", r["shared_ref"].upper())
        if m:
            out.append({"lemma": r["lemma"], "N": int(m.group(1)), "src": r["source_dict"],
                        "inh": r["inheritor"], "corpus_n": int(r.get("corpus_lemmas_with_ref", 0) or 0)})
    return out


def main():
    print("F7 — Harivaṃśa vulgate citation resolution (H488)")
    V, n_adh = load_verses()
    entries, keys = build_index(V)
    print(f"verses={len(V)}  adhyāyas={n_adh}  coverage={len(V)/16374*100:.1f}%")

    pwg = load_anchors("PWG", "pwg")
    mw = load_anchors("MW", "mw")
    print(f"anchors: PWG={len(pwg)}  MW={len(mw)}")

    offset, nsup, n_conf = fit_offsets(V, entries, keys, pwg, n_adh)
    for r in V:
        r["chat"] = r["C"] + offset[r["A"]]
    arr = sorted((r["chat"], i) for i, r in enumerate(V))
    chats = [a[0] for a in arr]
    print(f"calibration: confident adhyāyas={n_conf}/{n_adh}  offset {min(offset)}..{max(offset)}")

    ho = held_out(V, arr, chats, mw)
    passed = ho["agreement"] >= 0.30 and ho["agreement"] >= 5 * ho["null_rate"]
    print(f"\nHELD-OUT (MW): agreement={ho['agreement']:.3f} (hits {ho['hits']}/{ho['evaluable']})  "
          f"null={ho['null_rate']:.3f}  ->  {'PASS' if passed else 'FAIL'}")
    print(f"  δ dist (±{W}): {ho['delta_dist']}")

    report = {"n_verses": len(V), "coverage_pct": round(len(V) / 16374 * 100, 1),
              "n_adhyaya": n_adh, "confident_adhyaya": n_conf,
              "anchors_pwg": len(pwg), "anchors_mw": len(mw), "held_out": ho, "held_out_pass": passed}

    if not passed:
        print("\nHeld-out check FAILED — index not trustworthy; shared-error test NOT run (a valid exit).")
    else:
        shared = load_shared()
        res = []
        for h in shared:
            key = stem_key(h["lemma"])
            cat, delta, nl = classify(key, h["N"], V, entries, keys)
            res.append({**h, "key": key, "cat": cat, "delta": delta, "nloci": nl})
        ev = [r for r in res if len(r["key"]) >= 4]
        cats = Counter(r["cat"] for r in ev)
        rng = random.Random(20260710)
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
        print(f"\nSHARED POOL ({len(ev)} evaluable of {len(res)}): "
              f"corroborated={cats['corroborated']} displaced={cats['displaced']} absent={cats['absent']}")
        print(f"(A) verse-level corroboration: {cats['corroborated']}/{len(ev)} "
              f"= {cats['corroborated']/len(ev)*100:.1f}%  vs shuffled-N null "
              f"{statistics.mean(nc):.1f} ({statistics.mean(nc)/len(ev)*100:.1f}%)")
        print(f"(B) displaced(<=3 loci): observed {len(disp_clear)}  vs null {statistics.mean(nd):.1f}"
              f"  -> no shared-error excess above chance")
        report.update({"shared_evaluable": len(ev), "shared_total": len(res),
                       "corroborated": cats["corroborated"], "displaced": cats["displaced"],
                       "absent": cats["absent"],
                       "corroboration_pct": round(cats["corroborated"] / len(ev) * 100, 1),
                       "null_corr_mean": round(statistics.mean(nc), 1),
                       "null_corr_sd": round(statistics.pstdev(nc), 2),
                       "displaced_clear": len(disp_clear),
                       "null_displaced_clear_mean": round(statistics.mean(nd), 1)})
        # write resolution csv
        with open("data/forensic/harivamsa_shared_citation_resolution.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["lemma", "cited_N", "category", "delta", "n_loci", "source_dict", "inheritor", "corpus_n"])
            for r in sorted(res, key=lambda r: (r["cat"], r["N"])):
                w.writerow([r["lemma"], r["N"], r["cat"], r["delta"], r["nloci"], r["src"], r["inh"], r["corpus_n"]])

    # offsets csv (always)
    pa_by_ord = {}
    for r in V:
        pa_by_ord.setdefault(r["A"], (r["parvan"], r["adhyaya"]))
    with open("data/forensic/harivamsa_continuous_index_offsets.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["adhyaya_ordinal", "parvan", "adhyaya", "offset", "n_anchors"])
        for a in range(n_adh):
            p, adh = pa_by_ord[a]
            w.writerow([a, p, adh, offset[a], nsup[a]])

    # per-verse concordance (always): Kinjawadekar parvan-adhyāya-verse -> continuous Calcutta
    # śloka number Ĉ = C + offset[adhyāya]. Numbers only — no verse text (rights: the e-text is
    # a volunteer transcription, only measurements are redistributed). continuous_sloka is an
    # ESTIMATE (calibration noise ±1–2; held-out MW 68.4% land within ±3). adhyaya_n_anchors>0
    # marks a directly-fitted adhyāya; 0 = offset interpolated from neighbours.
    with open("data/forensic/harivamsa_vulgate_concordance.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["parvan", "adhyaya", "verse", "continuous_sloka", "adhyaya_offset", "adhyaya_n_anchors"])
        for r in sorted(V, key=lambda r: (r["parvan"], r["adhyaya"], r["verse"])):
            w.writerow([r["parvan"], r["adhyaya"], r["verse"], int(round(r["chat"])),
                        offset[r["A"]], nsup[r["A"]]])

    json.dump(report, open("data/forensic/f7_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    write_source("data/forensic/harivamsa_continuous_index_offsets.csv", "f7_harivamsa_resolve.py", 7)
    write_source("data/forensic/harivamsa_vulgate_concordance.csv", "f7_harivamsa_resolve.py", 7)
    if passed:
        write_source("data/forensic/harivamsa_shared_citation_resolution.csv", "f7_harivamsa_resolve.py", 7)
    print(f"\nwrote data/forensic/harivamsa_vulgate_concordance.csv ({len(V)} verses) + "
          "harivamsa_continuous_index_offsets.csv + harivamsa_shared_citation_resolution.csv + f7_report.json")


if __name__ == "__main__":
    main()
