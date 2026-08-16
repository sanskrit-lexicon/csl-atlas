"""Throwaway probe (H2845): look at the Santi 226.6 specimen in both witnesses."""
import sys, os, json, csv
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath("../sanskrit-util/py"))
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from sanskrit_util import slp1_simplify

fold = lambda s: slp1_simplify(s or "").replace(" ", "")

# concordance: what does calibrated_N 8081 in parvan 12 map to?
hits = []
with open("data/forensic/mbh_vulgate_concordance.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["parvan"] == "12" and r["calibrated_N"] == "8081":
            hits.append(r)
print("concordance rows for MBH 12,8081:", hits)

vul = {}
for line in open("data/forensic/_mbh_vulgate_verses.jsonl", encoding="utf-8"):
    d = json.loads(line)
    vul[(d["parvan"], d["adhyaya"], d["shloka"])] = d

for sh in (5, 6, 7):
    d = vul.get((12, 226, sh))
    if d:
        print(f"\nvulgate 12.226.{sh}  id={d['id']}  C={d['C']}")
        print("  SLP1:", d["slp1"][:200])
        print("  IAST:", transliterate(d["slp1"], sanscript.SLP1, sanscript.IAST)[:200])

target = "yadA ca pfTivIM sarvAM yajamAno 'nuparyagAH"
tf = fold(transliterate("yadā ca pṛthivīṃ sarvāṃ yajamāno 'nuparyagāḥ", sanscript.IAST, sanscript.SLP1))
print("\nMG probe folded:", tf)

# where does this stand in the vulgate at all?
found = [k for k, d in vul.items() if tf[:24] in fold(d["slp1"])]
print("vulgate loci containing the probe prefix:", found[:10])

bori = [json.loads(l) for l in open("data/forensic/_mbh_bori_folded.jsonl", encoding="utf-8")]
bfound = [b["loc"] for b in bori if tf[:24] in b["folded"]]
print("BORI half-verses containing the probe prefix:", bfound[:10])
