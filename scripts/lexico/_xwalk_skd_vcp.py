"""SKD × VCP anubandha cross-walk — produces the proposed SKD it-marker key.

Evidence script for docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md (issue #30, decision
round 3). Re-run to regenerate the anubandha→property table the maintainer verifies.

VCP writes the dhatupatha annotation out in plain `0`-abbreviations
(`idit BvAdi0 Atma0 saka0 sew`); SKD encodes the SAME grammar as Vopadeva/
Kavikalpadruma anubandhas (single romanized it-letters right after `¦`). For
roots present in BOTH as 1:1 (one root entry each), we align them and tally,
per SKD anubandha, the distribution of VCP's explicit properties. The dominant
associations = the proposed anubandha->property key, for the maintainer to
adjudicate. Deliberately conservative: only unambiguous 1:1 roots are used.
"""
import os, re, sys, collections
sys.path.insert(0, os.path.abspath("scripts/forensic"))
sys.path.insert(0, os.path.abspath("scripts/lexico"))
from parse_cslorig import iter_entries, CSL_ORIG
from m4_indigenous import analyze_entry, _PADA, _TRANS, _GANA, _first
sys.stdout.reconfigure(encoding="utf-8")

def src(code): return os.path.join(CSL_ORIG, code, f"{code}.txt")

# --- SKD: leading short SLP1 tokens after ¦ = candidate anubandhas (stop at the
#     first long token = the locative meaning; gender-marked nominals yield []). ---
GENDER = {"puM,", "klI,", "strI,", "tri,", "avya0", "puM", "klI", "strI", "tri"}
def skd_anubandhas(body):
    if "¦" not in body:
        return []
    after = body.split("¦", 1)[1].lstrip(" ,")
    out = []
    for t in after.split():
        if t in GENDER:
            return []                      # a nominal entry, not a root
        if re.fullmatch(r"[A-Za-z]{1,2}", t):
            out.append(t)
        else:
            break
    return out

# --- VCP: pull the explicit properties out of the annotation. ---
_IDIT = re.compile(r"(?<![A-Za-z])idit(?![A-Za-z])")
_SEW  = re.compile(r"(?<![A-Za-z])sew(?![A-Za-z])")
_ANIW = re.compile(r"(?<![A-Za-z])aniw(?![A-Za-z])")
_VEW  = re.compile(r"(?<![A-Za-z])vew(?![A-Za-z])")
def vcp_props(body):
    return {
        "idit": bool(_IDIT.search(body)),
        "pada": _first(body, _PADA),
        "trans": _first(body, _TRANS),
        "gana": _first(body, _GANA),
        "set": bool(_SEW.search(body)),
        "anit": bool(_ANIW.search(body)),
        "vet": bool(_VEW.search(body)),
    }

def load(code, root_fields):
    """k1 -> list of (info) for root entries only."""
    by = collections.defaultdict(list)
    for e in iter_entries(src(code)):
        a = analyze_entry(e["body"])
        if not a:
            continue
        by[e["k1"]].append(root_fields(e["body"]))
    return by

skd = load("skd", skd_anubandhas)
vcp = load("vcp", vcp_props)

# 1:1 shared roots only (unambiguous alignment).
shared = [k for k in skd if k in vcp and len(skd[k]) == 1 and len(vcp[k]) == 1
          and skd[k][0]]                       # SKD must actually carry anubandhas
print(f"SKD roots={sum(len(v) for v in skd.values()):,} (k1={len(skd):,})  "
      f"VCP roots={sum(len(v) for v in vcp.values()):,} (k1={len(vcp):,})")
print(f"1:1 shared roots with SKD anubandhas: {len(shared):,}\n")

# Cross-tab: per anubandha, the VCP property distribution.
pada_by = collections.defaultdict(collections.Counter)
idit_by = collections.Counter(); idit_tot = collections.Counter()
vet_by  = collections.Counter()
trans_by = collections.defaultdict(collections.Counter)
tot = collections.Counter()
for k in shared:
    anus = skd[k][0]
    p = vcp[k][0]
    for a in anus:
        tot[a] += 1
        if p["pada"]:  pada_by[a][p["pada"]] += 1
        if p["trans"]: trans_by[a][p["trans"]] += 1
        idit_tot[a] += 1
        if p["idit"]:  idit_by[a] += 1
        if p["vet"]:   vet_by[a] += 1

def pct(n, d): return f"{100*n//d:>3d}%" if d else "  -"
print(f"{'anu':>5} {'N':>5} | {'idit':>5} {'veṭ':>5} | pada (para/Atma/uBa)          | trans (saka/aka)")
print("-" * 86)
for a, n in tot.most_common(22):
    pad = pada_by[a]; tr = trans_by[a]
    padtot = sum(pad.values()); trtot = sum(tr.values())
    padstr = (f"para {pct(pad['parasmaipada'],padtot)} Atma {pct(pad['atmanepada'],padtot)} "
              f"uBa {pct(pad['ubhayapada'],padtot)} (n={padtot})")
    trstr = f"saka {pct(tr['sakarmaka'],trtot)} aka {pct(tr['akarmaka'],trtot)} (n={trtot})"
    print(f"{a!r:>5} {n:>5} | {pct(idit_by[a],idit_tot[a]):>5} {pct(vet_by[a],n):>5} | {padstr:<30} | {trstr}")
