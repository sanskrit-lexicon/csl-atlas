"""Phase F8g — the quote lane: where PWG's own quoted pratika actually stands (H2845).

The presence lane (`f8_mbh_presence.py`) resolves a citation by NUMBER, through the fitted
continuous index. This script resolves the same citations by TEXT, and measures how often the
two agree — which is the only honest way to say how much a citation-level `present/absent`
verdict is worth.

PWG prints a great many citations in the shape

    {#yadA ca pfTivIM sarvAM yajamAno 'nuparyagAH#} <ls>MBH. 12,8081</ls>

i.e. the verse itself immediately before the locus. Every such pair is a free labelled example:
retrieve the pratika in the Nilakantha vulgate, read off the calibrated_N of the verse it lands
in, and compare with the number PWG printed. No held-out split is needed — PWG never saw our
fitted index.

Reported:
  * agreement at |delta| = 0, ≤ 2, ≤ 10, ≤ 50 calibrated ślokas
  * the delta distribution (signed), so a systematic offset is visible as such
  * per-pratika rows, so any single verdict can be audited

Output: data/forensic/mbh_quote_lane_check.csv + data/forensic/f8_quote_lane_report.json
Run from repo root (after f8_mbh_witnesses.py):  python scripts/forensic/f8_mbh_quote_lane.py
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
CONCORDANCE = f"{OUT}/mbh_vulgate_concordance.csv"
PWG = "../csl-orig/v02/pwg/pwg.txt"

# {#pratika#} immediately followed by <ls>MBH. p,v</ls> — optionally with the closing period.
PAIR = re.compile(r"\{#([^#]{12,300})#\}\s*<ls>\s*MBH\.\s*(\d+),\s*(\d+)\s*\.?\s*</ls>")
SHINGLE = 12
STEP = 4
MAX_POSTING = 40
MIN_PROBE = 24     # folded chars a pratika needs before it can identify a verse
COVER = 0.60
SAMPLE = 1500      # cap the sweep; sampled with a fixed seed so the number is reproducible
SEED = 2845


def fold(s):
    return re.sub(r"[^a-z]", "", slp1_simplify(s or "").lower())


def grams(s, n=4):
    return {s[i:i + n] for i in range(len(s) - n + 1)} if len(s) >= n else set()


def main():
    if not os.path.exists(VULGATE):
        print(f"FATAL: {VULGATE} missing — run f8_mbh_witnesses.py first.", file=sys.stderr)
        return 2
    if not os.path.exists(PWG):
        print(f"FATAL: {PWG} missing — clone sanskrit-lexicon/csl-orig next to this repo.",
              file=sys.stderr)
        return 2

    vul = [json.loads(l) for l in open(VULGATE, encoding="utf-8")]
    folded = [fold(v["slp1"]) for v in vul]
    addr_to_n = {}
    with open(CONCORDANCE, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            addr_to_n[(int(r["parvan"]), int(r["adhyaya"]), int(r["shloka"]))] = int(r["calibrated_N"])

    # per-parvan shingle index over the vulgate: a PWG pratika cited as MBH. p,… is searched
    # inside parvan p only, which is both faster and the assumption PWG's own numbering makes.
    inv = defaultdict(lambda: defaultdict(list))
    for j, f_ in enumerate(folded):
        p = vul[j]["parvan"]
        for i in range(0, max(1, len(f_) - SHINGLE + 1), STEP):
            inv[p][f_[i:i + SHINGLE]].append(j)
    inv = {p: {k: v for k, v in d.items() if len(v) <= MAX_POSTING} for p, d in inv.items()}
    print(f"vulgate {len(vul):,} verses indexed per parvan", flush=True)

    raw = open(PWG, encoding="utf-8", errors="replace").read()
    pairs = [(m.group(1), int(m.group(2)), int(m.group(3))) for m in PAIR.finditer(raw)]
    print(f"PWG quoted-pratika + MBH-locus pairs: {len(pairs):,}", flush=True)
    rnd = random.Random(SEED)
    if len(pairs) > SAMPLE:
        pairs = rnd.sample(pairs, SAMPLE)

    rows, deltas = [], []
    for pratika, p, cited in pairs:
        probe = fold(pratika)
        if len(probe) < MIN_PROBE or p not in inv:
            rows.append({"parvan": p, "cited_verse": cited, "pratika_folded_len": len(probe),
                         "outcome": "probe-too-short", "found_address": "",
                         "found_calibrated_N": "", "delta": "", "coverage": ""})
            continue
        hits = Counter()
        for i in range(len(probe) - SHINGLE + 1):
            for j in inv[p].get(probe[i:i + SHINGLE], ()):
                hits[j] += 1
        best, bj = 0.0, None
        qg = grams(probe)
        for j, _ in hits.most_common(6):
            vg = grams(folded[j])
            if not vg:
                continue
            # coverage of the PRATIKA by the verse: the pratika is usually a half of the verse
            cov = len(vg & qg) / len(qg) if qg else 0.0
            if cov > best:
                best, bj = cov, j
        if bj is None or best < COVER:
            rows.append({"parvan": p, "cited_verse": cited, "pratika_folded_len": len(probe),
                         "outcome": "not-retrieved", "found_address": "",
                         "found_calibrated_N": "", "delta": "", "coverage": round(best, 3)})
            continue
        v = vul[bj]
        n = addr_to_n.get((v["parvan"], v["adhyaya"], v["shloka"]))
        d = (cited - n) if n is not None else None
        if d is not None:
            deltas.append(d)
        rows.append({"parvan": p, "cited_verse": cited, "pratika_folded_len": len(probe),
                     "outcome": "retrieved",
                     "found_address": f"{v['parvan']}.{v['adhyaya']}.{v['shloka']}",
                     "found_calibrated_N": n if n is not None else "",
                     "delta": d if d is not None else "", "coverage": round(best, 3)})

    with open(f"{OUT}/mbh_quote_lane_check.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    write_source(f"{OUT}/mbh_quote_lane_check.csv", "f8_mbh_quote_lane.py", 8)

    oc = Counter(r["outcome"] for r in rows)
    n = len(deltas)
    within = {str(k): (sum(1 for d in deltas if abs(d) <= k) / n if n else 0.0)
              for k in (0, 2, 10, 50, 200)}
    report = {
        "pwg_pairs_found": len(rows), "sample_cap": SAMPLE, "seed": SEED,
        "outcomes": dict(oc), "retrieved_with_calibrated_N": n,
        "fitted_index_agreement_within_k_slokas": {k: round(v, 4) for k, v in within.items()},
        "delta_median": sorted(deltas)[n // 2] if n else None,
        "delta_mean": round(sum(deltas) / n, 2) if n else None,
        "note": ("PWG's printed number vs the calibrated_N of the verse its own quoted pratika "
                 "actually stands in. This is the accuracy the citation-level presence verdict "
                 "inherits; the verse-level table does not depend on it."),
    }
    json.dump(report, open(f"{OUT}/f8_quote_lane_report.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"outcomes: {dict(oc)}")
    print(f"retrieved with a calibrated_N: {n}")
    for k, v in within.items():
        print(f"  |delta| <= {k:>3}: {v:.3f}")
    print(f"median delta {report['delta_median']}, mean {report['delta_mean']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
