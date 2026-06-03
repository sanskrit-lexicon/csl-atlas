"""Phase L3 / F3 — gloss DE->EN tracking (the cross-lingual signal; weakest, first pass).

MW (English) and PWG/PW (German) are separated by the translation barrier, so the
language-neutral signals (F1 citations, F2 homonyms) carry most of the weight. This
is a CHEAP proxy for "MW's article is an adaptation of Böhtlingk's": does the SIZE of
MW's English gloss track the size of PWG's German gloss, lemma by lemma — more tightly
than it tracks an INDEPENDENT English dict (Apte) or an unrelated German one?

Entry length correlates across any two dicts via lemma importance (big words get big
articles everywhere), so the absolute correlation is uninformative; the DIFFERENTIAL
MW~PWG minus MW~AP(independent English) is the signal. A real proxy only — true
translation evidence needs token-level DE->EN alignment (deferred).

German gloss = the {%…%} spans (Böhtlingk's actual translations). English gloss =
body text stripped of markup. Per shared lemma, lengths are log1p'd and correlated
(Pearson + Spearman).

Reads csl-orig via parse_cslorig.iter_entries (bodies aren't cached).
Output : data/forensic/gloss_length_correlation.csv, data/forensic/f3_report.json.
Run from repo root:  python scripts/forensic/f3_gloss.py
"""

import os
import re
import sys
import csv
import json
import math
import collections

sys.path.insert(0, os.path.abspath("scripts/forensic"))
from parse_cslorig import iter_entries, CSL_ORIG

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

GERMAN = re.compile(r"\{%(.*?)%\}", re.DOTALL)   # Böhtlingk German gloss spans
MARKUP = re.compile(r"<[^>]*>|\{[#%@][^}]*\}|[¦]")
WS = re.compile(r"\s+")
PAIRS = [("PWG", "MW", "de"), ("PW", "MW", "de"), ("AP", "MW", "en"), ("BEN", "MW", "de")]


def gloss_len_map(code, lang):
    """k1 -> total gloss character length (German {%..%} spans, or English body text)."""
    out = collections.defaultdict(int)
    src = os.path.join(CSL_ORIG, code.lower(), f"{code.lower()}.txt")
    for e in iter_entries(src):
        k1 = e["k1"]
        if not k1:
            continue
        if lang == "de":
            text = " ".join(GERMAN.findall(e["body"]))
        else:
            text = WS.sub(" ", MARKUP.sub(" ", e["body"]))
        out[k1] += len(text.strip())
    return out


def corr(xs, ys):
    """Pearson + Spearman on two equal-length numeric lists."""
    n = len(xs)
    if n < 3:
        return 0.0, 0.0

    def pearson(a, b):
        ma, mb = sum(a) / n, sum(b) / n
        va = sum((x - ma) ** 2 for x in a)
        vb = sum((y - mb) ** 2 for y in b)
        if va == 0 or vb == 0:
            return 0.0
        cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        return cov / math.sqrt(va * vb)

    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    return pearson(xs, ys), pearson(ranks(xs), ranks(ys))


def main():
    print("=" * 64)
    print("F3 — gloss-length tracking DE->EN (cross-lingual proxy; weakest signal)")
    print("=" * 64)

    cache = {}
    rows = []
    for a, b, lang in PAIRS:
        if a not in cache:
            cache[a] = gloss_len_map(a, lang)
        if b not in cache:
            cache[b] = gloss_len_map(b, "en")
        ga, gb = cache[a], cache[b]
        shared = [k for k in ga.keys() & gb.keys() if ga[k] > 0 and gb[k] > 0]
        xs = [math.log1p(ga[k]) for k in shared]
        ys = [math.log1p(gb[k]) for k in shared]
        pear, spear = corr(xs, ys)
        rows.append({"source": a, "inheritor": b, "source_lang": lang,
                     "shared_glossed_lemmas": len(shared),
                     "pearson_loglen": round(pear, 4), "spearman_loglen": round(spear, 4)})
        print(f"  {a + '->' + b:10s} ({lang}) shared={len(shared):>7,}  "
              f"pearson={pear:.3f}  spearman={spear:.3f}")

    with open("data/forensic/gloss_length_correlation.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["source", "inheritor", "source_lang",
                                          "shared_glossed_lemmas", "pearson_loglen",
                                          "spearman_loglen"])
        w.writeheader()
        w.writerows(rows)

    pwg = next(r for r in rows if r["source"] == "PWG")["spearman_loglen"]
    ap = next(r for r in rows if r["source"] == "AP")["spearman_loglen"]
    diff = round(pwg - ap, 4)
    print(f"\nDifferential MW~PWG(de) - MW~AP(independent en) = {diff:+.3f} "
          f"({'PWG tracks tighter' if diff > 0 else 'no DE->EN advantage'})")

    report = {
        "pairs": rows,
        "differential_pwg_minus_ap_spearman": diff,
        "interpretation": ("Proxy only. Entry length correlates across any dict pair via lemma "
                           "importance, so read the DIFFERENTIAL MW~PWG minus MW~AP(independent "
                           f"English): {diff:+.3f}. Positive = MW's article size tracks Böhtlingk's "
                           "German more tightly than an independent English dict = consistent with "
                           "adaptation. This is the WEAKEST forensic rung; token-level DE->EN "
                           "alignment (real translation evidence) is deferred. The language-neutral "
                           "F1 (citations) and F2 (homonyms) carry the load."),
    }
    with open("data/forensic/f3_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nWrote gloss_length_correlation.csv ({len(rows)} pairs), f3_report.json")
    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source("data/forensic/gloss_length_correlation.csv", "f3_gloss.py", 3)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
