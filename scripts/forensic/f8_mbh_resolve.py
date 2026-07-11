"""Phase F8d — resolve PWG/MW MBH citations against the harvested Nīlakaṇṭha vulgate, fitting a
per-parvan continuous index (held-out MW gate, shuffled-N null) — ALL 18 PARVANS. H610.

Generalizes H761's book-7 census ([`f8_mbh_drona_fitted_index.py`](f8_mbh_drona_fitted_index.py),
MBH_DRONA_FITTED_INDEX_CENSUS.md) to the whole Mahābhārata: same f7 method, run per parvan over
the full sanatana.in vulgate (f8_mbh_harvest.py, 83,971 verses). Independently reproduces the
book-7 held-out number (90/187) — a cross-check on two separate harvests of the same source.

Per parvan: provisional C = running verse count; robust per-adhyāya offset (median residual N−C)
fitted on PWG anchors; HELD OUT on MW; classify each ref corroborated/displaced/absent. Pooled
and per-parvan held-out gates reported (circularity guard).

Outputs (numbers only — no verse text):
  data/forensic/mbh_vulgate_concordance.csv        per-verse (parvan,adhyaya,shloka)->continuous N
  data/forensic/mbh_continuous_index_offsets.csv    per-adhyaya offsets + anchor support
  data/forensic/mbh_citation_resolution.csv         per note-locus classification
  data/forensic/f8_resolve_report.json              per-parvan + pooled held-out, corroboration
Run from repo root (after f8_mbh_harvest.py):  python scripts/forensic/f8_mbh_resolve.py
Deps: ../sanskrit-util/py (slp1_simplify).
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

VERSES = "data/forensic/_mbh_vulgate_verses.jsonl"
NOTES = "data/forensic/mbh_correction_notes.csv"
W = 3
LS = re.compile(r'<ls(?:\s+n="([^"]*)")?\s*>(.*?)</ls>', re.DOTALL)
TAG = re.compile(r"<[^>]*>")
WS = re.compile(r"\s+")
TOKEN = re.compile(r"[A-Za-z]+")
ROMAN = {"i":1,"ii":2,"iii":3,"iv":4,"v":5,"vi":6,"vii":7,"viii":8,"ix":9,"x":10,
         "xi":11,"xii":12,"xiii":13,"xiv":14,"xv":15,"xvi":16,"xvii":17,"xviii":18}


def stem_key(slp1):
    s = slp1_simplify(slp1 or "")
    if len(s) >= 5 and s.endswith("a"):
        s = s[:-1]
    return s


def pwg_anchors():
    src = os.path.join(CSL_ORIG, "pwg", "pwg.txt")
    rows = []
    for e in iter_entries(src):
        k1 = (e["k1"] or "").strip()
        if not k1:
            continue
        last = None
        for m in LS.finditer(e["body"]):
            attr = WS.sub(" ", TAG.sub("", m.group(1) or "")).strip()
            pay = WS.sub(" ", TAG.sub("", m.group(2) or "")).strip()
            if not (attr.upper().startswith("MBH") or pay.upper().startswith("MBH")):
                continue
            ns = re.sub(r"(?i)MBH\.?|ed\.\s*Calc\.?|ed\.\s*Bomb\.?", " ", pay if re.search(r"\d", pay) else attr)
            mm = re.search(r"(\d+)\s*,\s*(\d+)", ns)
            if mm:
                b, v = int(mm.group(1)), int(mm.group(2))
            else:
                ab = re.search(r"(\d+)\s*,\s*$", attr); pv = re.search(r"^\s*(\d+)\s*$", pay)
                if ab and pv: b, v = int(ab.group(1)), int(pv.group(1))
                elif pv and last is not None: b, v = last, int(pv.group(1))
                else: continue
            if 1 <= b <= 18:
                last = b
                rows.append({"k1": k1, "b": b, "n": v})
    return rows


def mw_anchors():
    src = os.path.join(CSL_ORIG, "mw", "mw.txt")
    rows = []
    for e in iter_entries(src):
        k1 = (e["k1"] or "").strip()
        if not k1:
            continue
        for m in re.finditer(r"MBh\.\s*([ivxlc]+)\s*,\s*(\d+)", e["body"]):
            b = ROMAN.get(m.group(1).lower())
            if b:
                rows.append({"k1": k1, "b": b, "n": int(m.group(2))})
    return rows


def load_verses():
    V = [json.loads(l) for l in open(VERSES, encoding="utf-8")]
    V.sort(key=lambda r: (r["parvan"], r["adhyaya"], r["shloka"]))
    for r in V:
        r["toks"] = set(k for k in (stem_key(t) for t in TOKEN.findall(r["slp1"])) if len(k) >= 3)
        r["simp"] = slp1_simplify(r["slp1"]).replace(" ", "")
    return V


def build_parvan(V):
    P = defaultdict(list)
    for r in V:
        P[r["parvan"]].append(r)
    out = {}
    for b, verses in P.items():
        adh = {}
        for r in verses:
            adh.setdefault(r["adhyaya"], len(adh))
        for r in verses:
            r["A"] = adh[r["adhyaya"]]
        ent = sorted((k, i) for i, r in enumerate(verses) for k in r["toks"])
        out[b] = {"V": verses, "n_adh": len(adh), "keys": [e[0] for e in ent],
                  "ent": ent, "Cby": [r["C"] for r in verses]}
    return out


def strict_matches(key, keys, ent, max_extra=3):
    if len(key) < 4:
        return set()
    out, n, i = set(), len(keys), bisect.bisect_left(keys, key)
    while i < n and keys[i].startswith(key):
        if len(keys[i]) - len(key) <= max_extra:
            out.add(ent[i][1])
        i += 1
    return out


def isotonic(points):
    xs = [p[0] for p in points]; vals = []
    for _, y, w in points:
        blk = [y, w, 1]
        while vals and vals[-1][0] > blk[0]:
            pm, pw, pl = vals.pop(); nw = pw + blk[1]
            blk = [(pm*pw + blk[0]*blk[1])/nw, nw, pl + blk[2]]
        vals.append(blk)
    fitted = []
    for m, w, l in vals: fitted += [m]*l
    return dict(zip(xs, fitted))


def fit_offsets(pk, anchors):
    V, keys, ent, Cby, n_adh = pk["V"], pk["keys"], pk["ent"], pk["Cby"], pk["n_adh"]
    resid_u, resid_all = defaultdict(list), defaultdict(list)
    for a in anchors:
        key = stem_key(a["k1"])
        if len(key) < 4: continue
        m = strict_matches(key, keys, ent)
        if not m or len(m) > 5: continue
        N = a["n"]; best = min(m, key=lambda i: abs(Cby[i]-N))
        resid_all[V[best]["A"]].append(N - Cby[best])
        if len(m) == 1:
            j = next(iter(m)); resid_u[V[j]["A"]].append(N - Cby[j])
    direct, nsup, conf_pts = [None]*n_adh, [0]*n_adh, []
    for a in range(n_adh):
        pool = resid_u[a] if len(resid_u[a]) >= 2 else resid_all[a]
        if not pool: continue
        med = int(round(statistics.median(pool))); direct[a] = med; nsup[a] = len(pool)
        mad = statistics.median([abs(x-med) for x in pool]) if pool else 999
        if len(pool) >= 2 and mad <= 6: conf_pts.append((a, med, len(pool)))
    iso = isotonic(conf_pts); conf = {a: int(round(iso[a])) for a in iso}; ca = sorted(conf)
    def baseline(a):
        below = [x for x in ca if x <= a]; above = [x for x in ca if x >= a]
        if below and above and below[-1] != above[0]:
            a0, a1 = below[-1], above[0]
            return conf[a0] + (conf[a1]-conf[a0])*(a-a0)/(a1-a0)
        if a in conf: return conf[a]
        return conf[below[-1]] if below else (conf[above[0]] if above else 0)
    off = [0]*n_adh
    for a in range(n_adh):
        B = baseline(a)
        off[a] = direct[a] if (direct[a] is not None and abs(direct[a]-B) <= 40) else int(round(B))
    return off, nsup, len(ca)


def match_in_verse(r, key):
    return any(t.startswith(key) and len(t)-len(key) <= 4 for t in r["toks"]) or key in r["simp"]


def held_out(pk, anchors):
    V = pk["V"]; arr = sorted((r["chat"], i) for i, r in enumerate(V))
    chats = [a[0] for a in arr]
    if not chats: return {"ev":0,"hits":0,"agr":0,"nev":0,"nhit":0,"nrate":0}
    hits=ev=nh=nev=0; rng=random.Random(20260711); maxN=int(max(chats))
    for a in anchors:
        key = stem_key(a["k1"])
        if len(key) < 4: continue
        N = a["n"]; lo=bisect.bisect_left(chats,N-W); hi=bisect.bisect_right(chats,N+W)
        win = arr[lo:hi]
        if not win: continue
        ev += 1
        if any(match_in_verse(V[i], key) for _, i in win): hits += 1
        Np = rng.randint(1+W, max(maxN-W, 2+W))
        if abs(Np-N) >= 50:
            lo2=bisect.bisect_left(chats,Np-W); hi2=bisect.bisect_right(chats,Np+W); wp=arr[lo2:hi2]
            if wp:
                nev += 1
                if any(match_in_verse(V[i], key) for _, i in wp): nh += 1
    return {"ev":ev,"hits":hits,"agr":hits/ev if ev else 0,"nev":nev,"nhit":nh,
            "nrate":nh/nev if nev else 0}


def loci(pk, key):
    keys, ent, V = pk["keys"], pk["ent"], pk["V"]
    if len(key) < 4: return []
    out, n, i = [], len(keys), bisect.bisect_left(keys, key)
    while i < n and keys[i].startswith(key):
        if len(keys[i]) - len(key) <= 3: out.append(V[ent[i][1]]["chat"])
        i += 1
    return sorted(set(out))


def classify(pk, key, N):
    ls = loci(pk, key)
    if not ls: return "absent", None
    near = [c for c in ls if abs(c-N) <= W]
    if near: return "corroborated", int(round(min(near, key=lambda c: abs(c-N))-N))
    return "displaced", int(round(min(ls, key=lambda c: abs(c-N))-N))


def main():
    print("F8d — MBH Nīlakaṇṭha-vulgate citation resolution, ALL 18 PARVANS (H610)")
    V = load_verses()
    P = build_parvan(V)
    print(f"vulgate verses={len(V)}  parvans={sorted(P)}")
    pwg = pwg_anchors(); mw = mw_anchors()
    print(f"anchors: PWG={len(pwg)} MW={len(mw)}")

    for b, pk in P.items():
        off, nsup, nconf = fit_offsets(pk, [a for a in pwg if a["b"] == b])
        pk["off"], pk["nsup"], pk["nconf"] = off, nsup, nconf
        for r in pk["V"]:
            r["chat"] = r["C"] + off[r["A"]]

    per = {}; tot_ev=tot_hit=tot_nev=tot_nh=0
    for b, pk in P.items():
        ho = held_out(pk, [a for a in mw if a["b"] == b])
        per[b] = ho; tot_ev+=ho["ev"]; tot_hit+=ho["hits"]; tot_nev+=ho["nev"]; tot_nh+=ho["nhit"]
    pooled_agr = tot_hit/tot_ev if tot_ev else 0
    pooled_null = tot_nh/tot_nev if tot_nev else 0
    passed = pooled_agr >= 0.30 and pooled_agr >= 5*pooled_null
    print(f"\nHELD-OUT (MW) pooled: agreement={pooled_agr:.3f} ({tot_hit}/{tot_ev}) "
          f"null={pooled_null:.3f} -> {'PASS' if passed else 'FAIL'}")
    for b in sorted(per):
        h = per[b]
        if h["ev"]: print(f"  parvan {b:2d}: agr={h['agr']:.2f} ({h['hits']}/{h['ev']}) null={h['nrate']:.2f}")

    if 7 in P:
        pk = P[7]; arr = sorted((r["chat"], i) for i, r in enumerate(pk["V"]))
        chats = [a[0] for a in arr]
        lo = bisect.bisect_left(chats, 9283-4); hi = bisect.bisect_right(chats, 9283+4)
        print("\n=== validation case MBH. 7,9283 (Böhtlingk: Calcutta 'abravat' fehlerhaft für 'abravIt') ===")
        for c, i in arr[lo:hi]:
            r = pk["V"][i]
            if "abravIt" in r["slp1"] or "abravat" in r["slp1"]:
                print(f"  N≈{c} (adh {r['adhyaya']}.{r['shloka']}): …{r['slp1'][-46:]}")

    notes = list(csv.DictReader(open(NOTES, encoding="utf-8"))) if os.path.exists(NOTES) else []
    res = []
    for nrow in notes:
        b = int(nrow["parvan"]); N = int(nrow["verse"])
        if b not in P: continue
        cat, delta = classify(P[b], stem_key(nrow["headword_slp1"]), N)
        res.append({**nrow, "cat": cat, "delta": delta})
    cats = Counter(r["cat"] for r in res)
    if res:
        print(f"\nnote-locus resolution ({len(res)} notes): {dict(cats)}")

    with open("data/forensic/mbh_vulgate_concordance.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["parvan","adhyaya","shloka","continuous_C","calibrated_N","adhyaya_offset","adhyaya_n_anchors"])
        for b in sorted(P):
            pk = P[b]
            for r in sorted(pk["V"], key=lambda r:(r["adhyaya"],r["shloka"])):
                w.writerow([b, r["adhyaya"], r["shloka"], r["C"], int(round(r["chat"])), pk["off"][r["A"]], pk["nsup"][r["A"]]])
    with open("data/forensic/mbh_continuous_index_offsets.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["parvan","adhyaya_ordinal","offset","n_anchors"])
        for b in sorted(P):
            pk = P[b]
            for a in range(pk["n_adh"]): w.writerow([b, a, pk["off"][a], pk["nsup"][a]])
    with open("data/forensic/mbh_citation_resolution.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["L","headword_slp1","parvan","verse","marker","confidence","category","delta"])
        for r in sorted(res, key=lambda r:(r["cat"], int(r["parvan"]), int(r["verse"]))):
            w.writerow([r["L"], r["headword_slp1"], r["parvan"], r["verse"], r["marker"], r["confidence"], r["cat"], r["delta"]])

    report = {"vulgate_verses": len(V), "parvans_harvested": sorted(P),
              "per_parvan_Cmax": {b: P[b]["Cby"][-1] for b in sorted(P)},
              "anchors_pwg": len(pwg), "anchors_mw": len(mw),
              "held_out_pooled_agreement": round(pooled_agr,3), "held_out_pooled_null": round(pooled_null,3),
              "held_out_pass": passed, "held_out_evaluable": tot_ev,
              "per_parvan_held_out": {b: {"agr": round(per[b]["agr"],3), "ev": per[b]["ev"],
                                          "hits": per[b]["hits"], "null": round(per[b]["nrate"],3)} for b in sorted(per)},
              "note_locus_resolution": dict(cats)}
    json.dump(report, open("data/forensic/f8_resolve_report.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    for p in ("mbh_vulgate_concordance.csv","mbh_continuous_index_offsets.csv","mbh_citation_resolution.csv"):
        write_source(f"data/forensic/{p}", "f8_mbh_resolve.py", 8)
    print("\nwrote mbh_vulgate_concordance.csv + mbh_continuous_index_offsets.csv + mbh_citation_resolution.csv + f8_resolve_report.json")


if __name__ == "__main__":
    main()
