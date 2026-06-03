"""Phase L4 / F6 — DE->EN gloss test: is MW's English a rendering of PWG's German?

The one signal F3 only proxied. Translate PWG's German gloss to English (offline,
argos-translate; run scripts/forensic/_setup_argos.py once) and ask whether MW's English
definition resembles translated-PWG MORE than two baselines:

  - APTE null  : Apte (AP), an INDEPENDENT English Skt dict. Both MW and AP define the
                 same word, so both resemble translated-PWG via the fixed meaning
                 (convergence). Copying shows only as MW > AP.
  - RANDOM base: translated-PWG vs a random MW gloss — the shared-vocabulary floor.

Stratified (per M.G.): ALL / VERB / PHILOSOPHICAL. Verbs and technical philosophical
terms are where an independent compiler is most tempted to lean on a predecessor, so a
copying signal, if it exists anywhere, should surface there.
  verb  = MW marks a verb class ("cl. N ...").
  phil  = the entry cites a darsana text (Vedanta / Samkhya / Nyaya / Yoga / Vaisesika ...).

Self-contained (own minimal csl-orig parser); reproducible (sorted before sampling).
Reads ../csl-orig/v02/{mw,pwg,ap}. Sampled per stratum (neural MT is slow).
Output: data/forensic/f6_gloss_translation.csv, f6_report.json.
Run:  F6_SAMPLE=1500 python scripts/forensic/f6_gloss_translation.py
"""

import os
import re
import sys
import csv
import json
import random
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

CSL_ORIG = "../csl-orig/v02"
SAMPLE = int(os.environ.get("F6_SAMPLE", "1500"))   # per stratum
SEED = 17
_K1 = re.compile(r"<k1>([^<]*)")
_GERMAN = re.compile(r"\{%(.*?)%\}", re.DOTALL)
_MARKUP = re.compile(r"<[^>]*>|\{[#%@][^}]*\}|[¦]")
_LS = re.compile(r"<ls>(.*?)</ls>", re.DOTALL)
_TAG = re.compile(r"<[^>]*>")
_WS = re.compile(r"\s+")
_WORD = re.compile(r"[a-z]{3,}")
_VERB = re.compile(r"\bcl\.\s*\d")                  # MW verb-class notation
_DIGIT = re.compile(r"\d")
STOP = set("the a an and or of to in for with as is are was on at by from that this it its be "
           "also more most see used name kind sort etc esp one two his her their which who whom "
           "whose not no any some such than then there here when where what".split())
# darsana / philosophical text sigils (ASCII-folded, prefix match)
PHIL = ("VEDANTA", "SAMKHYA", "NYAYA", "TARKA", "BHASAP", "YOGAS", "VAIS", "KAPILA", "MUKTAV",
        "BRAHMAS", "SANK", "SARVAD", "KUSUM", "KARIKA", "PRAB", "SADANANDA", "VEDANTAP",
        "BHASAPARICCH", "TATTVAS", "SIDDHANTA")


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).upper()


def iter_entries(path):
    L, body, inside = None, [], False
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("<LEND>"):
                if inside:
                    yield L, "".join(body)
                inside, body = False, []
            elif line.startswith("<L>"):
                m = _K1.search(line)
                L = m.group(1).strip() if m else None
                inside, body = True, []
            elif inside:
                body.append(line)


def is_phil_cites(body):
    for c in _LS.findall(body):
        sig = fold(_TAG.sub("", c))
        if any(sig.lstrip(" .").startswith(p) for p in PHIL):
            return True
    return False


def parse(code, lang):
    """k1 -> dict(gloss, is_verb, is_phil)."""
    out = {}
    for k1, body in iter_entries(os.path.join(CSL_ORIG, code, f"{code}.txt")):
        if not k1:
            continue
        gloss = (" ".join(_GERMAN.findall(body)) if lang == "de"
                 else _WS.sub(" ", _MARKUP.sub(" ", body)))
        rec = out.setdefault(k1, {"gloss": "", "is_verb": False, "is_phil": False})
        rec["gloss"] = (rec["gloss"] + " " + gloss).strip()
        if _VERB.search(body):
            rec["is_verb"] = True
        if is_phil_cites(body):
            rec["is_phil"] = True
    return out


def toks(text):
    return {w for w in _WORD.findall(text.lower()) if w not in STOP}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def main():
    print("=" * 64)
    print(f"F6 — DE->EN gloss test, stratified (sample {SAMPLE}/stratum)")
    print("=" * 64)
    try:
        import argostranslate.translate as tr
    except Exception as e:
        print(f"argostranslate missing: {e}; run _setup_argos.py", file=sys.stderr)
        sys.exit(1)

    print("\nparsing glosses + verb/phil tags...")
    pwg = parse("pwg", "de")
    mw = parse("mw", "en")
    ap = parse("ap", "en")
    shared = sorted(h for h in (pwg.keys() & mw.keys() & ap.keys())
                    if pwg[h]["gloss"].strip() and mw[h]["gloss"].strip() and ap[h]["gloss"].strip())
    # stratum membership uses MW tags (verb-class) + either-dict phil citations
    verb = [h for h in shared if mw[h]["is_verb"] or pwg[h]["is_verb"]]
    phil = [h for h in shared if mw[h]["is_phil"] or pwg[h]["is_phil"]]
    print(f"  shared(3): {len(shared):,} · verb: {len(verb):,} · philosophical: {len(phil):,}")

    random.seed(SEED)
    strata = {"ALL": shared, "VERB": verb, "PHIL": phil}
    samples = {name: random.sample(pool, min(SAMPLE, len(pool))) for name, pool in strata.items()}
    union = sorted(set().union(*samples.values()))
    print(f"  translating {len(union):,} unique PWG German glosses (de->en)...")

    tpwg = {}
    for i, h in enumerate(union):
        tpwg[h] = toks(tr.translate(pwg[h]["gloss"][:1500], "de", "en"))
        if (i + 1) % 500 == 0:
            print(f"    ...{i+1}/{len(union)}")

    pool_mw = list(mw.keys())
    rows = []
    summary = {}
    for name, samp in samples.items():
        s_mw = s_ap = s_rand = 0.0
        cnt = 0
        for h in samp:
            tp = tpwg.get(h)
            if not tp:
                continue
            jmw = jaccard(tp, toks(mw[h]["gloss"]))
            jap = jaccard(tp, toks(ap[h]["gloss"]))
            jr = jaccard(tp, toks(mw[random.choice(pool_mw)]["gloss"]))
            s_mw += jmw
            s_ap += jap
            s_rand += jr
            cnt += 1
            if name != "ALL":   # keep stratified rows for eyeball
                rows.append({"stratum": name, "headword": h, "sim_mw": round(jmw, 4),
                             "sim_ap": round(jap, 4), "sim_random": round(jr, 4),
                             "mw_minus_ap": round(jmw - jap, 4)})
        summary[name] = {"n": cnt, "sim_mw": round(s_mw / cnt, 4), "sim_ap": round(s_ap / cnt, 4),
                         "sim_random": round(s_rand / cnt, 4), "mw_minus_ap": round((s_mw - s_ap) / cnt, 4)}

    rows.sort(key=lambda r: -r["mw_minus_ap"])
    with open("data/forensic/f6_gloss_translation.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["stratum", "headword", "sim_mw", "sim_ap", "sim_random", "mw_minus_ap"])
        w.writeheader()
        w.writerows(rows)

    print("\n" + "=" * 64)
    print("Gloss similarity to translated-PWG, by stratum (Δ>0 = MW beats independent null)")
    print("=" * 64)
    print(f"  {'stratum':6s} {'n':>5s} {'sim_MW':>7s} {'sim_Apte':>9s} {'sim_rand':>9s} {'MW-Apte':>8s}")
    for name in ("ALL", "VERB", "PHIL"):
        s = summary[name]
        print(f"  {name:6s} {s['n']:>5} {s['sim_mw']:>7.4f} {s['sim_ap']:>9.4f} "
              f"{s['sim_random']:>9.4f} {s['mw_minus_ap']:>+8.4f}")
    print("\n  Δ (MW-Apte) > 0 in any stratum => MW's prose tracks PWG beyond convergence there.")

    report = {
        "sample_per_stratum": SAMPLE, "strata": summary,
        "n_shared": len(shared), "n_verb": len(verb), "n_phil": len(phil),
        "phil_sigils": list(PHIL),
        "top_mw_over_ap": rows[:30],
        "method": ("PWG German gloss translated offline (argos de->en); token-Jaccard vs MW, vs "
                   "Apte (independent-English null), vs random MW gloss (floor). Stratified ALL / "
                   "VERB (MW 'cl. N') / PHIL (cites a darsana text). Copying = MW>Apte; MW<=Apte = "
                   "convergence on the fixed meaning. Reproducible (sorted+seeded)."),
    }
    with open("data/forensic/f6_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nWrote f6_gloss_translation.csv ({len(rows)} verb+phil rows), f6_report.json")


if __name__ == "__main__":
    main()
