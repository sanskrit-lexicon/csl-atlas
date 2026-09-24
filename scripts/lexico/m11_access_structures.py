"""M11 — access structures (Wiegand's *Zugriffsstrukturen*) of the seven narrative dicts.

The macrostructural census nobody had run: for MW, PWG, PW (PWK), AP, WIL, SKD and VCP,
recover the headword order actually printed (the csl-orig record order), test it against
a grid of candidate collation rules, and report per dictionary the best-fitting rule with
its measured violation rate, the evidence that separates it from its rivals, and the
counterexamples. The two versified kośas (ARMH/ABCH) are excluded on purpose — they are
concept-ordered, not alphabetical; M6 (`m6_kosha_macrostructure.py`) measures them.

WHAT IS MEASURED (all from the `<L>` header lines — no body parsing except the alias test):

1. ORDER VIEWS. Record sequences per dictionary:
   - `all`   — every csl-orig record, in file order.
   - `print` — drops the Cologne-added ALIAS records (body is `{{Lbody=N}}`: an extra
               spelling of another entry's headword, inserted by the digitisers, never a
               printed entry). PW 12,186 / AP 9,625 / MW 4,352 / VCP 1,765 of them.
   - `main`  — `print` minus NESTED sub-records: MW and AP give every run-on compound or
               derivative its own record, marked by the `<e>` level (`<e>2`, `3A`, …);
               `main` keeps level-1 records only. For the five dicts without `<e>` it
               equals `print`.
   - `heads` — AP only (its PRIMARY view): `main` minus fractional-L paragraph run-ons and
               minus the prefix derivatives nested under a verbal root (a root record is
               one whose body carries the conjugation-class mark `¦ €N`).
   - `heads_nest` — AP only (H5409): `heads` with the nest also closing over the root's
               VOWEL GRADES — guṇa, vṛddhi, zero grade of the root's last vowel, so √kṛ
               `kf` swallows kāra and karaṇa. Reported in `root_nests.vowel_grade_filter`
               with the verdict on refutation condition 3 of the methods page; it is NOT
               the scored view (AP stays scored on `heads`).
   Consecutive records with the same `k1` collapse into one UNIT (MW's `1A`/`1B`
   continuation records; adjacent homonyms), so a unit is one position in the order.

2. CANDIDATE RULES. A rule maps an SLP1 `k1` to a sort key. 72 varṇamālā rules =
   4 anusvāra × 3 internal-visarga × 3 final-visarga × 2 gemination policies, + 2 controls:
   - base order: a ā i ī u ū ṛ ṝ ḷ ḹ e ai o au ṃ ḥ k kh g gh ṅ c … m y r l v ś ṣ s h
   - anusvāra `M`: `pos` (own slot after the vowels) · `nasal` (before a stop or nasal =
     that class's nasal, else own slot) · `nasal_m` (class nasal there, `m` elsewhere) ·
     `m` (always `m`)
   - internal visarga `Hi`: `pos` (own slot after ṃ) · `sib` (before a sibilant = that
     sibilant, else own slot) · `s` (always `s`)
   - final visarga `Hf`: `slot` (own slot) · `s` (as `s`) · `drop` (ignored — citation-form
     endings)
   - gemination `G`: `keep` · `degem` (after r a written doubled consonant sorts single)
   - controls: `ascii` (raw SLP1 byte order — no lexicographer sorts this way) and
     `roman` (IAST in Latin-alphabet order, diacritics as a secondary level).
   Candrabindu `~` sorts as anusvāra; Vedic `L` (ḷa) right after `l`.

3. SEGMENTS. A descent is an ALPHABET RESTART — the start of a separately sorted sequence
   (a Nachträge run, a supplement volume) — when the initial letter goes backwards AND the
   next 10 units all sort below the previous 10. Restarts are segment boundaries, not
   violations; everything else is measured within segments.

4. VIOLATION RATES (per dict × view × rule):
   - `descent_rate`   — within-segment adjacent unit pairs whose keys decrease / all
     within-segment adjacent pairs (`descent_rate_raw` counts restarts too).
   - `displaced_rate` — Σ(units − longest non-decreasing subsequence) per segment / units:
     the minimum share of units that must move for the order to satisfy the rule.

5. BEST FIT + FACTOR EVIDENCE. Best fit = minimum within-segment descents in the primary
   view (ties → fewer displaced → grid order; all tied rules are listed). Most adjacent
   pairs never touch ṃ, ḥ or r+geminate, so each factor is judged by PAIRWISE CONTRASTS
   on the pairs where two of its policies disagree (other factors at best fit): < 30 such
   pairs = `undetermined`, ≥ 3:1 = `clear`, else `weak`. `factor_status` summarises the
   chosen policy per factor: what it rejects, what it cannot be told apart from.

6. HOMONYMS. Groups = the same `k1` on ≥ 2 primary-view records within one segment.
   Reported: contiguity, and — where `<h>` numbers exist — ascending / gapless numbering.

7. NESTING (MW, AP). Share of nested sub-records, how often a sub-record's `k1` extends its
   head's, sibling descent rate; for AP the root nests: descent rate by distance from the
   last root, and the roots-only order.

8. COUNTEREXAMPLES. Every within-segment descent of the best-fit rule in the primary view,
   classified `block` (inside a stretch of ≥ 25 consecutive displaced units — listed once
   per block in `displaced_blocks`) or `isolated`, with page refs and IAST; plus a
   common-prefix profile (`descent_profile`) of how local the disorder is.

Stdlib only; UTF-8, no BOM; deterministic (no sets iterated into output, no RNG).
Run from repo root:
    python scripts/lexico/m11_access_structures.py            # the seven dicts
    python scripts/lexico/m11_access_structures.py --dicts wil skd
Outputs (data/lexico/):
    access_structures.json                  envelope: rules, per-dict verdicts, homonyms,
                                            nesting, displaced blocks, sample counterexamples
    access_structures_rules.csv             dict × view × rule rate table
    access_structures_counterexamples.csv   every best-fit descent in the primary view
"""

import argparse
import bisect
import csv
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections import Counter, OrderedDict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GH = os.path.abspath(os.path.join(ROOT, ".."))
CSL = os.path.join(GH, "csl-orig", "v02")
OUT_DIR = os.path.join(ROOT, "data", "lexico")

DICTS = ["mw", "pwg", "pw", "ap", "wil", "skd", "vcp"]
DICT_LABEL = {"mw": "MW", "pwg": "PWG", "pw": "PW (PWK)", "ap": "AP", "wil": "WIL",
              "skd": "SKD", "vcp": "VCP"}

FACTORS = OrderedDict([
    ("M", ["pos", "nasal", "nasal_m", "m"]),     # anusvāra ṃ
    ("Hi", ["pos", "sib", "s"]),                 # visarga ḥ inside the word
    ("Hf", ["slot", "s", "drop"]),               # visarga ḥ word-final (citation endings)
    ("G", ["keep", "degem"]),                    # doubled consonant after r (karṇṇa, varddha)
])
FACTOR_LABEL = {"M": "anusvara", "Hi": "visarga_internal", "Hf": "visarga_final", "G": "gemination_after_r"}
CONTROLS = ["ascii", "roman"]


def rule_name(pol):
    return "/".join(f"{f}-{pol[f]}" for f in FACTORS)


def parse_rule(name):
    return OrderedDict(part.split("-", 1) for part in name.split("/"))


def _grid():
    out = [OrderedDict()]
    for f, pols in FACTORS.items():
        out = [OrderedDict(list(o.items()) + [(f, p)]) for o in out for p in pols]
    return out


VARNA_RULES = [rule_name(p) for p in _grid()]
RULES = VARNA_RULES + CONTROLS
VIEWS = ["all", "print", "main", "heads", "heads_nest"]
PRIMARY_VIEW = {"ap": "heads"}   # every other dict is scored on `main`
RESTART_WINDOW = 10         # units compared on each side of a candidate restart
MIN_SENSITIVE = 30          # below this a contrast verdict is `undetermined`
RUN_MIN = 25                # displaced stretch this long = an out-of-place block
SAMPLE_ISOLATED = 25        # isolated counterexamples embedded in the JSON per dict
CONFIRM_SHARE = 0.75        # share of the heads→roots-only gap a filter must close (H5409)
PARTLY_SHARE = 0.25         # below CONFIRM_SHARE but at least this = `partly`
# First page of a supplement the digitisers MERGED into alphabetical place (fractional L),
# so record order cannot show it as a separate sequence: MW's Additions and Corrections.
MERGED_SUPPLEMENT_FROM_PAGE = {"mw": 1308}

# ---------------------------------------------------------------- collation ----------

VARNA = ("a A i I u U f F x X e E o O M H "
         "k K g G N c C j J Y w W q Q R t T d D n p P b B m "
         "y r l L | v S z s h").split()
RANK = {ch: i for i, ch in enumerate(VARNA)}
UNKNOWN_RANK = len(VARNA)   # any other char sorts after h (counted in `unknown_chars`)

# the class nasal of every class consonant — the nasal itself included, so ṃ before
# n/m (saṃnakha, saṃmata) reads as that nasal under the `nasal` policies
CLASS_NASAL = {}
for cls, nasal in (("kKgGN", "N"), ("cCjJY", "Y"), ("wWqQR", "R"), ("tTdDn", "n"), ("pPbBm", "m")):
    for s in cls:
        CLASS_NASAL[s] = nasal
SIBILANTS = set("Szs")
# unaspirated partner of an aspirate: Bengal-style gemination writes rddh as r+d+dh
DEASPIRATE = {"K": "k", "G": "g", "C": "c", "J": "j", "W": "w", "Q": "q",
              "T": "t", "D": "d", "P": "p", "B": "b"}
CONSONANTS = set("kKgGNcCjJYwWqQRtTdDnpPbBmylvSzsh")

SLP1_TO_IAST = {
    "a": "a", "A": "ā", "i": "i", "I": "ī", "u": "u", "U": "ū",
    "f": "ṛ", "F": "ṝ", "x": "ḷ", "X": "ḹ", "e": "e", "E": "ai", "o": "o", "O": "au",
    "M": "ṃ", "H": "ḥ", "~": "m̐", "z": "ṣ", "k": "k", "K": "kh", "g": "g", "G": "gh",
    "N": "ṅ", "c": "c", "C": "ch", "j": "j", "J": "jh", "Y": "ñ", "w": "ṭ", "W": "ṭh",
    "q": "ḍ", "Q": "ḍh", "R": "ṇ", "t": "t", "T": "th", "d": "d", "D": "dh", "n": "n",
    "p": "p", "P": "ph", "b": "b", "B": "bh", "m": "m", "y": "y", "r": "r", "l": "l",
    "v": "v", "L": "ḻ", "|": "ḻh", "S": "ś", "s": "s", "h": "h", "'": "'",
}


def slp1_to_iast(text):
    return "".join(SLP1_TO_IAST.get(ch, ch) for ch in text)


def apply_g(k, policy):
    """`degem`: after r, a written doubled consonant (rmm, rṇṇ, rtt, rddh = r+d+dh) sorts as single."""
    if policy == "keep" or "r" not in k:
        return k
    out = []
    i = 0
    while i < len(k):
        ch = k[i]
        out.append(ch)
        if ch == "r" and i + 2 < len(k):
            a, b = k[i + 1], k[i + 2]
            if a in CONSONANTS and (a == b or DEASPIRATE.get(b) == a):
                i += 2          # skip the first member of the geminate
                continue
        i += 1
    return "".join(out)


def apply_m(k, policy):
    if "M" not in k and "~" not in k:
        return k
    out = []
    for i, ch in enumerate(k):
        if ch in "M~":
            nxt = k[i + 1] if i + 1 < len(k) else ""
            if policy == "pos":
                out.append("M")
            elif policy == "m":
                out.append("m")
            elif nxt in CLASS_NASAL:
                out.append(CLASS_NASAL[nxt])
            else:
                out.append("M" if policy == "nasal" else "m")
        else:
            out.append(ch)
    return "".join(out)


def apply_h(k, internal, final):
    if "H" not in k:
        return k
    out = []
    last = len(k) - 1
    for i, ch in enumerate(k):
        if ch != "H":
            out.append(ch)
            continue
        if i == last:
            if final == "slot":
                out.append("H")
            elif final == "s":
                out.append("s")
            continue            # drop
        nxt = k[i + 1]
        if internal == "pos":
            out.append("H")
        elif internal == "s":
            out.append("s")
        else:  # sib
            out.append(nxt if nxt in SIBILANTS else "H")
    return "".join(out)


def roman_key(k):
    """IAST in Latin-alphabet order: base letters first, diacritics as a tie-break."""
    s = unicodedata.normalize("NFD", slp1_to_iast(k))
    primary, secondary = [], []
    for ch in s:
        if unicodedata.combining(ch):
            secondary.append(ord(ch))
        else:
            primary.append(ord(ch.lower()))
            secondary.append(0)
    return (tuple(primary), tuple(secondary))


def transform(k, pol):
    return apply_h(apply_m(apply_g(k, pol["G"]), pol["M"]), pol["Hi"], pol["Hf"])


def make_key(rule):
    if rule == "ascii":
        return lambda k: k
    if rule == "roman":
        return roman_key
    pol = parse_rule(rule)

    def key(k):
        return tuple(RANK.get(ch, UNKNOWN_RANK) for ch in transform(k, pol))
    return key


# ---------------------------------------------------------------- parsing ------------

_ATTR = re.compile(r"<(k1|k2|h|e|pc)>([^<]*)")
_LID = re.compile(r"^<L>([0-9.]+)")
# AP prints a verb root with its gaṇa number(s) right after the headword: `{#aMS#}¦ €10 <ab>U.</ab>`
# (3,201 records). Its derivatives follow it in derivational, not alphabetical, order.
ROOT_MARK = {"ap": re.compile(r"¦\s*€\d")}


def read_records(code, csl=CSL):
    """Header records in file order: L, pc, k1, k2, h, e, alias, root."""
    path = os.path.join(csl, code, f"{code}.txt")
    root_re = ROOT_MARK.get(code)
    recs = []
    cur = None
    first_body = False
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("<L>"):
                m = _LID.match(line)
                attrs = dict(_ATTR.findall(line))
                cur = {"L": m.group(1) if m else "", "pc": attrs.get("pc", ""),
                       "k1": attrs.get("k1", ""), "k2": attrs.get("k2", ""),
                       "h": attrs.get("h", "").strip(), "e": attrs.get("e", "").strip(),
                       "alias": False, "root": False}
                recs.append(cur)
                first_body = True
            elif cur is not None and first_body:
                if line.startswith("{{Lbody="):
                    cur["alias"] = True
                if root_re is not None and root_re.search(line):
                    cur["root"] = True
                first_body = False
            if line.startswith("<LEND>"):
                cur = None
    return recs


def e_level(e):
    m = re.match(r"(\d+)", e or "")
    return int(m.group(1)) if m else 1


VOWELS = set("aAiIuUfFxXeEoO")
# Vowel grades (H5409). A derivative nested under a root carries the root vowel in one of
# three grades, so its stem is NOT a literal prefix extension of the root: √kṛ (`kf`) nests
# kāra (`kAra`, vṛddhi) and karaṇa (`karaRa`, guṇa); √budh (`buD`) nests bodha (`boDa`).
GUNA = {"a": "a", "A": "A", "i": "e", "I": "e", "u": "o", "U": "o",
        "f": "ar", "F": "ar", "x": "al", "X": "al", "e": "e", "E": "E", "o": "o", "O": "O"}
VRDDHI = {"a": "A", "A": "A", "i": "E", "I": "E", "u": "O", "U": "O",
          "f": "Ar", "F": "Ar", "x": "Al", "X": "Al", "e": "E", "E": "E", "o": "O", "O": "O"}
ZERO = {"A": "a", "I": "i", "U": "u", "F": "f", "X": "x", "e": "i", "E": "i",
        "o": "u", "O": "u"}


def grade_variants(root):
    """Stem prefixes a derivative of `root` may open with: the root itself plus its guṇa,
    vṛddhi and zero-grade forms, the root vowel being the LAST vowel of the root string
    (Sanskrit roots are all but monosyllabic once the class mark is stripped).
    √kṛ `kf` → kf, kar, kAr; √budh `buD` → buD, boD, bOD; √gam `gam` → gam, gAm.
    Returns a deterministic list, the literal root first. Not modelled: samprasāraṇa,
    nasal infix loss, set/anit ā-roots (`sTA` → sTita) — those stay counterexamples."""
    idx = [i for i, ch in enumerate(root) if ch in VOWELS]
    if not idx:
        return [root]
    i = idx[-1]
    onset, nuc, coda = root[:i], root[i], root[i + 1:]
    out = [root]
    for table in (GUNA, VRDDHI, ZERO):
        g = table.get(nuc)
        if not g:
            continue
        v = onset + g + coda
        if v not in out:
            out.append(v)
    return out


def heads_filter(recs, nest_aware=False):
    """AP only: drop paragraph run-ons (fractional L at level 1) and the derivatives that
    follow a root inside its nest. `nest_aware=False` (the `heads` view) matches a
    derivative only when its k1 literally extends the root's k1; `nest_aware=True` (the
    `heads_nest` view, H5409) also matches the root's guṇa/vṛddhi/zero-grade stems, so the
    whole nest collapses into one sort unit keyed on the root. Returns kept, stats."""
    kept, runons, nested, roots, graded = [], 0, 0, 0, 0
    root = None
    variants = ()
    for r in recs:
        if "." in r["L"]:
            runons += 1
            continue
        if r["root"]:
            roots += 1
            root = r["k1"]
            variants = grade_variants(root) if nest_aware else (root,)
            kept.append(r)
            continue
        if root is not None and r["k1"] != root:
            hit = next((v for v in variants if r["k1"].startswith(v)), None)
            if hit is not None:
                nested += 1
                if hit != root:
                    graded += 1
                continue
        root = None
        variants = ()
        kept.append(r)
    st = {"roots": roots, "paragraph_runons_dropped": runons,
          "root_nest_derivatives_dropped": nested}
    if nest_aware:
        st["vowel_grade_derivatives_dropped"] = graded
    return kept, st


def view_records(recs, view, code=None):
    if view == "all":
        return recs
    kept = [r for r in recs if not r["alias"]]
    if view == "print":
        return kept
    main_ = [r for r in kept if e_level(r["e"]) == 1]
    if view == "main" or code not in ROOT_MARK:
        return main_
    return heads_filter(main_, nest_aware=(view == "heads_nest"))[0]


def units(recs):
    """Collapse consecutive identical k1 into one unit (keeps the first record)."""
    out = []
    for r in recs:
        if out and out[-1]["k1"] == r["k1"]:
            continue
        out.append(r)
    return out


# ---------------------------------------------------------------- metrics ------------

def lnds(keys):
    """Longest non-decreasing subsequence: (length, on_path flags)."""
    tails, tails_idx = [], []
    parent = [-1] * len(keys)
    for i, k in enumerate(keys):
        j = bisect.bisect_right(tails, k)
        if j == len(tails):
            tails.append(k)
            tails_idx.append(i)
        else:
            tails[j] = k
            tails_idx[j] = i
        parent[i] = tails_idx[j - 1] if j > 0 else -1
    on = [False] * len(keys)
    i = tails_idx[-1] if tails_idx else -1
    while i >= 0:
        on[i] = True
        i = parent[i]
    return len(tails), on


def descents(keys):
    return [i for i in range(len(keys) - 1) if keys[i + 1] < keys[i]]


def restarts(keys, desc, window=RESTART_WINDOW):
    """A descent is an ALPHABET RESTART (a new separately-sorted sequence begins — a
    supplement, a Nachträge run) when (a) the INITIAL letter goes backwards and (b) the
    whole next window sorts below the whole previous window. (b) means a single misplaced
    unit on either side can never qualify; (a) means a block inversion or a nest inside one
    initial-letter section (AP's root nests, WIL's asr-/asv- swap) stays a counted
    violation instead of being excused as a segment."""
    out = []
    for i in desc:
        if not keys[i + 1][:1] < keys[i][:1]:
            continue
        before = keys[max(0, i + 1 - window):i + 1]
        after = keys[i + 1:i + 1 + window]
        if len(before) < 3 or len(after) < 3:
            continue
        if max(after) < min(before):
            out.append(i)
    return out


def keys_for(us, rule, cache):
    key = make_key(rule)
    c = cache.setdefault(rule, {})
    ks = []
    for u in us:
        k1 = u["k1"]
        if k1 not in c:
            c[k1] = key(k1)
        ks.append(c[k1])
    return ks


def evaluate(us, rule, cache):
    ks = keys_for(us, rule, cache)
    d = descents(ks)
    rs = restarts(ks, d)
    rset = set(rs)
    within = [i for i in d if i not in rset]
    bounds = [0] + [i + 1 for i in rs] + [len(ks)]
    on = []
    displaced = 0
    for a, b in zip(bounds, bounds[1:]):
        ln, seg_on = lnds(ks[a:b])
        displaced += (b - a) - ln
        on.extend(seg_on)
    n = len(ks)
    return {"keys": ks, "descents": d, "restarts": rs, "within": within, "n": n,
            "displaced": displaced, "on": on, "bounds": bounds}


def rate(a, b):
    return round(a / b, 6) if b else None


# ---------------------------------------------------------------- analyses -----------

def contrasts(us, cache, best, restart_set):
    """Pairwise policy contrasts per factor, judged on the adjacent pairs where the two
    policies disagree (every other factor held at its best-fit policy). Restart pairs are
    excluded. Which pair isolates which context (methods page §3):
    M pos|nasal = ṃ before a class consonant · M nasal|nasal_m = ṃ before y r l v ś ṣ s h
    or final · Hi pos|sib = ḥ before a sibilant · Hi sib|s = ḥ before k kh p ph ·
    Hf slot|drop = a final ḥ counted at its slot or ignored · G keep|degem = r+geminate."""
    out = OrderedDict()
    for factor, policies in FACTORS.items():
        ks = {}
        for p in policies:
            pol = OrderedDict(best)
            pol[factor] = p
            ks[p] = keys_for(us, rule_name(pol), cache)
        fixed = "/".join(f"{f}-{v}" for f, v in best.items() if f != factor)
        rows = []
        for a_i, p in enumerate(policies):
            for q in policies[a_i + 1:]:
                wins_p = wins_q = 0
                ex_p, ex_q = [], []
                for i in range(len(us) - 1):
                    if i in restart_set:
                        continue
                    vp = ks[p][i + 1] < ks[p][i]
                    vq = ks[q][i + 1] < ks[q][i]
                    if vp == vq:
                        continue
                    a, b = us[i], us[i + 1]
                    ex = {"prev_iast": slp1_to_iast(a["k1"]), "next_iast": slp1_to_iast(b["k1"]),
                          "next_L": b["L"], "next_pc": b["pc"]}
                    if vq:          # q violated, p satisfied
                        wins_p += 1
                        if len(ex_p) < 4:
                            ex_p.append(ex)
                    else:
                        wins_q += 1
                        if len(ex_q) < 4:
                            ex_q.append(ex)
                n = wins_p + wins_q
                if n < MIN_SENSITIVE:
                    verdict, winner = "undetermined", None
                elif wins_p == wins_q:
                    verdict, winner = "tie", None
                else:
                    winner = p if wins_p > wins_q else q
                    hi, lo = max(wins_p, wins_q), min(wins_p, wins_q)
                    verdict = "clear" if hi >= 3 * lo else "weak"
                rows.append(OrderedDict([
                    ("contrast", f"{p}|{q}"), ("disagreeing_pairs", n),
                    ("pairs_ordered_only_by_" + p, wins_p), ("pairs_ordered_only_by_" + q, wins_q),
                    ("verdict", verdict), ("winner", winner),
                    ("examples_for_" + p, ex_p), ("examples_for_" + q, ex_q),
                ]))
        out[FACTOR_LABEL[factor]] = OrderedDict([("factor", factor), ("held_fixed", fixed),
                                                 ("pairwise", rows)])
    return out


def homonyms(recs, us, bounds):
    """Homonym groups = same k1 on >= 2 records WITHIN one alphabet segment."""
    seg_of_unit = []
    for s, (a, b) in enumerate(zip(bounds, bounds[1:])):
        seg_of_unit.extend([s] * (b - a))
    groups = OrderedDict()
    ui = -1
    prev = None
    for r in recs:
        if r["k1"] != prev:
            ui += 1
            prev = r["k1"]
        groups.setdefault((seg_of_unit[ui], r["k1"]), []).append((ui, r))
    k1_segments = Counter(k1 for (_, k1) in groups)
    multi = [(k, v) for k, v in groups.items() if len(v) >= 2]
    contiguous = numbered = asc = gapless = 0
    scattered = []
    for (seg, k1), members in multi:
        uis = {ui for ui, _ in members}
        if len(uis) == 1:
            contiguous += 1
        elif len(scattered) < 8:
            scattered.append({"k1": k1, "iast": slp1_to_iast(k1), "segment": seg,
                              "L": [r["L"] for _, r in members][:6],
                              "pc": [r["pc"] for _, r in members][:6]})
        hs = [r["h"] for _, r in members]
        if all(h.isdigit() for h in hs):
            numbered += 1
            nums = [int(h) for h in hs]
            if nums == sorted(nums):
                asc += 1
            if sorted(nums) == list(range(1, len(nums) + 1)):
                gapless += 1
    sizes = Counter(len(v) for _, v in multi)
    n = len(multi)
    return OrderedDict([
        ("groups", n),
        ("records_in_groups", sum(len(v) for _, v in multi)),
        ("size_distribution", OrderedDict((str(s), sizes[s]) for s in sorted(sizes))),
        ("contiguous", contiguous), ("contiguous_rate", rate(contiguous, n)),
        ("h_numbered_groups", numbered),
        ("h_ascending", asc), ("h_ascending_rate", rate(asc, numbered)),
        ("h_gapless_from_1", gapless), ("h_gapless_rate", rate(gapless, numbered)),
        ("headwords_repeated_across_segments", sum(1 for c in k1_segments.values() if c > 1)),
        ("scattered_examples", scattered),
    ])


def nesting(print_recs, rule, cache):
    sub = [r for r in print_recs if e_level(r["e"]) > 1]
    if not sub:
        return OrderedDict([("nested_records", 0), ("model", "flat — no <e> sub-record levels")])
    key = make_key(rule)
    c = cache.setdefault(rule, {})

    def k(x):
        if x not in c:
            c[x] = key(x)
        return c[x]
    prefix = total = 0
    sib_pairs = sib_desc = 0
    parent = None
    prev_sib = None
    for r in print_recs:
        if e_level(r["e"]) == 1:
            parent, prev_sib = r, None
            continue
        if parent is None:
            continue
        total += 1
        if r["k1"].startswith(parent["k1"]):
            prefix += 1
        if prev_sib is not None and prev_sib["k1"] != r["k1"] and e_level(prev_sib["e"]) == e_level(r["e"]):
            sib_pairs += 1
            if k(r["k1"]) < k(prev_sib["k1"]):
                sib_desc += 1
        prev_sib = r
    return OrderedDict([
        ("model", "hierarchical — sub-records follow their level-1 head"),
        ("nested_records", len(sub)),
        ("nested_share_of_print", rate(len(sub), len(print_recs))),
        ("nested_k1_extends_head_k1", prefix),
        ("nested_k1_extends_head_rate", rate(prefix, total)),
        ("same_level_sibling_pairs", sib_pairs), ("same_level_sibling_descents", sib_desc),
        ("same_level_sibling_descent_rate", rate(sib_desc, sib_pairs)),
    ])


def factor_status(contrast_block, chosen):
    """Summarise one factor for the best-fit rule: which alternatives the data rejects
    (and how firmly) and which it cannot tell apart from the chosen policy."""
    rejected, indistinct, beaten_by = OrderedDict(), [], []
    for row in contrast_block["pairwise"]:
        p, q = row["contrast"].split("|")
        if chosen not in (p, q):
            continue
        other = q if chosen == p else p
        if row["verdict"] in ("undetermined", "tie"):
            indistinct.append(other)
        elif row["winner"] == chosen:
            rejected[other] = OrderedDict([("verdict", row["verdict"]),
                                           ("disagreeing_pairs", row["disagreeing_pairs"])])
        else:
            beaten_by.append(other)
    if beaten_by:
        status = "contested"
    elif not rejected:
        status = "undetermined"
    elif indistinct:
        status = "partial"      # some alternatives rejected, others indistinguishable
    elif all(v["verdict"] == "clear" for v in rejected.values()):
        status = "clear"
    else:
        status = "weak"
    return OrderedDict([("policy", chosen), ("status", status), ("rejects", rejected),
                        ("indistinguishable_from", indistinct), ("beaten_by", beaten_by)])


def common_prefix(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def descent_profile(us, within):
    """How local is the disorder? Common-prefix length of each violating pair (k1)."""
    bins = OrderedDict([("ending_variant", 0), ("prefix_4plus", 0), ("prefix_2_3", 0), ("prefix_0_1", 0)])
    for i in within:
        a, b = us[i]["k1"], us[i + 1]["k1"]
        c = common_prefix(a, b)
        if c >= min(len(a), len(b)) - 1:
            bins["ending_variant"] += 1
        elif c >= 4:
            bins["prefix_4plus"] += 1
        elif c >= 2:
            bins["prefix_2_3"] += 1
        else:
            bins["prefix_0_1"] += 1
    return bins


def page_of(pc):
    m = re.match(r"(?:\d+-)?0*(\d+)", pc or "")
    return int(m.group(1)) if m else None


def root_distance_profile(us, ev):
    """Descent rate of the pair (j, j+1) by j's distance from the last preceding root unit.
    A root-nested macrostructure concentrates its violations just after each root."""
    rset = set(ev["restarts"])
    dset = set(ev["within"])
    buckets = OrderedDict((str(d), [0, 0]) for d in range(10))
    buckets["10+"] = [0, 0]
    buckets["before_first_root"] = [0, 0]
    last = None
    for j in range(len(us) - 1):
        if us[j]["root"]:
            last = j
        if j in rset:
            continue
        key = "before_first_root" if last is None else (str(j - last) if j - last < 10 else "10+")
        buckets[key][0] += 1
        if j in dset:
            buckets[key][1] += 1
    return OrderedDict((k, OrderedDict([("pairs", v[0]), ("descents", v[1]), ("descent_rate", rate(v[1], v[0]))]))
                       for k, v in buckets.items())


def nest_aware_block(main_recs, rule, cache, heads_rate, roots_rate):
    """H5409 — re-measure AP on the `heads_nest` view (root nests collapsed through the
    vowel grades) and grade refutation condition 3 of the census methods page: does a
    vowel-grade-aware filter move the heads-view rate toward the roots-only floor?
    `confirmed` = at least CONFIRM_SHARE of the gap between the two closed, `partly` = at
    least PARTLY_SHARE, `refuted` = less (or the rate gets worse)."""
    kept, st = heads_filter(main_recs, nest_aware=True)
    us = units(kept)
    ev = evaluate(us, rule, cache)
    nest_rate = rate(len(ev["within"]), len(us) - 1 - len(ev["restarts"]))
    gap = heads_rate - roots_rate
    closed = rate(heads_rate - nest_rate, gap) if gap > 0 else None
    verdict = "refuted"
    if closed is not None and closed >= CONFIRM_SHARE:
        verdict = "confirmed"
    elif closed is not None and closed >= PARTLY_SHARE:
        verdict = "partly"
    residual = []
    for i in ev["within"][:SAMPLE_ISOLATED]:
        a, b = us[i], us[i + 1]
        residual.append(OrderedDict([
            ("prev_L", a["L"]), ("prev_pc", a["pc"]), ("prev_iast", slp1_to_iast(a["k1"])),
            ("prev_is_root", bool(a["root"])),
            ("next_L", b["L"]), ("next_pc", b["pc"]), ("next_iast", slp1_to_iast(b["k1"])),
            ("next_is_root", bool(b["root"]))]))
    return OrderedDict([
        ("view", "heads_nest"),
        ("rule", rule),
        ("grades", "guna / vrddhi / zero-grade of the root's last vowel"),
        ("units", len(us)),
        ("root_nest_derivatives_dropped", st["root_nest_derivatives_dropped"]),
        ("vowel_grade_derivatives_dropped", st["vowel_grade_derivatives_dropped"]),
        ("descents", len(ev["within"])),
        ("descent_rate", nest_rate),
        ("heads_view_descent_rate", heads_rate),
        ("roots_only_descent_rate", roots_rate),
        ("share_of_heads_rate_removed", rate(heads_rate - nest_rate, heads_rate) if heads_rate else None),
        ("share_of_gap_to_roots_only_closed", closed),
        ("refutation_condition_3_verdict", verdict),
        ("descent_rate_by_distance_from_last_root", root_distance_profile(us, ev)),
        ("residual_counterexamples_sample", residual),
    ])


def displaced_blocks(us, on):
    blocks, i = [], 0
    while i < len(us):
        if on[i]:
            i += 1
            continue
        j = i
        while j < len(us) and not on[j]:
            j += 1
        if j - i >= RUN_MIN:
            a, b = us[i], us[j - 1]
            blocks.append(OrderedDict([
                ("start_index", i), ("units", j - i),
                ("first_L", a["L"]), ("first_pc", a["pc"]), ("first_iast", slp1_to_iast(a["k1"])),
                ("last_L", b["L"]), ("last_pc", b["pc"]), ("last_iast", slp1_to_iast(b["k1"])),
            ]))
        i = j
    return blocks


def segment_map(us, ev):
    segs = []
    for s, (a, b) in enumerate(zip(ev["bounds"], ev["bounds"][1:])):
        first, last = us[a], us[b - 1]
        segs.append(OrderedDict([
            ("segment", s), ("units", b - a),
            ("first_L", first["L"]), ("first_pc", first["pc"]), ("first_iast", slp1_to_iast(first["k1"])),
            ("last_L", last["L"]), ("last_pc", last["pc"]), ("last_iast", slp1_to_iast(last["k1"])),
        ]))
    return segs


def csl_orig_commit(csl=CSL):
    try:
        return subprocess.run(["git", "-C", os.path.dirname(csl), "rev-parse", "HEAD"],
                              capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
    except Exception:
        return None


# ---------------------------------------------------------------- driver -------------

def run_dict(code, rules_rows, cex_rows, csl=CSL):
    recs = read_records(code, csl)
    cache = {}
    unknown = Counter(ch for r in recs for ch in r["k1"] if ch not in RANK and ch not in "M~H")
    primary = PRIMARY_VIEW.get(code, "main")
    per_view = OrderedDict()
    evals = {}
    for view in VIEWS:
        if view in ("heads", "heads_nest") and code not in ROOT_MARK:
            continue
        us = units(view_records(recs, view, code))
        per_view[view] = OrderedDict()
        for rule in RULES:
            ev = evaluate(us, rule, cache)
            nd, nw, n = len(ev["descents"]), len(ev["within"]), ev["n"]
            nr = len(ev["restarts"])
            row = OrderedDict([("units", n), ("segments", nr + 1),
                               ("descents_raw", nd), ("descent_rate_raw", rate(nd, n - 1)),
                               ("descents", nw), ("descent_rate", rate(nw, n - 1 - nr)),
                               ("displaced", ev["displaced"]), ("displaced_rate", rate(ev["displaced"], n))])
            per_view[view][rule] = row
            rules_rows.append([code, view, rule, n, nr + 1, nd, row["descent_rate_raw"],
                               nw, row["descent_rate"], ev["displaced"], row["displaced_rate"]])
            if view == primary:
                evals[rule] = ev
    us = units(view_records(recs, primary, code))
    print_recs = view_records(recs, "print", code)
    main_recs = view_records(recs, "main", code)
    varna = VARNA_RULES
    pv = per_view[primary]
    ranked = sorted(varna, key=lambda r: (pv[r]["descents"], pv[r]["displaced"], varna.index(r)))
    best, runner = ranked[0], ranked[1]
    tied = [r for r in varna if pv[r]["descents"] == pv[best]["descents"]]
    best_pol = parse_rule(best)
    ev = evals[best]
    rset = set(ev["restarts"])
    factors = contrasts(us, cache, best_pol, rset)
    blocks = displaced_blocks(us, ev["on"])
    in_block = [False] * len(us)
    for b in blocks:
        for i in range(b["start_index"], b["start_index"] + b["units"]):
            in_block[i] = True
    alt_keys = [evals[r]["keys"] for r in varna]
    isolated = []
    n_iso = 0
    for i in ev["within"]:
        a, b = us[i], us[i + 1]
        kind = "block" if (in_block[i] or in_block[i + 1]) else "isolated"
        sensitive = any(ks[i + 1] >= ks[i] for ks in alt_keys)
        cex_rows.append([code, primary, best, kind, int(sensitive), i, a["L"], a["pc"], a["k1"],
                         slp1_to_iast(a["k1"]), b["L"], b["pc"], b["k1"], slp1_to_iast(b["k1"])])
        if kind == "isolated":
            n_iso += 1
            if len(isolated) < SAMPLE_ISOLATED:
                isolated.append(OrderedDict([
                    ("prev_L", a["L"]), ("prev_pc", a["pc"]), ("prev_iast", slp1_to_iast(a["k1"])),
                    ("next_L", b["L"]), ("next_pc", b["pc"]), ("next_iast", slp1_to_iast(b["k1"])),
                    ("sensitive_to_anusvara_visarga_policy", sensitive)]))
    pb = pv[best]
    status = OrderedDict((FACTOR_LABEL[f], factor_status(factors[FACTOR_LABEL[f]], best_pol[f]))
                         for f in FACTORS)
    merged = None
    if code in MERGED_SUPPLEMENT_FROM_PAGE:
        first = MERGED_SUPPLEMENT_FROM_PAGE[code]
        sup = [r for r in print_recs if (page_of(r["pc"].split(",")[0]) or 0) >= first]
        merged = OrderedDict([("from_page", first), ("print_records", len(sup)),
                              ("level1_records", sum(1 for r in sup if e_level(r["e"]) == 1)),
                              ("fractional_L", sum(1 for r in sup if "." in r["L"]))])
    out = OrderedDict([
        ("dict", code), ("label", DICT_LABEL[code]),
        ("records", len(recs)),
        ("alias_records", sum(1 for r in recs if r["alias"])),
        ("print_records", len(print_recs)),
        ("main_records", len(main_recs)),
        ("primary_view", primary),
        ("primary_units", len(us)),
        ("unknown_chars", OrderedDict(sorted(unknown.items()))),
        ("best_fit", OrderedDict([
            ("rule", best), ("policies", OrderedDict((FACTOR_LABEL[f], v) for f, v in best_pol.items())),
            ("tied_rules", tied),
            ("segments", pb["segments"]),
            ("descents", pb["descents"]), ("descent_rate", pb["descent_rate"]),
            ("displaced", pb["displaced"]), ("displaced_rate", pb["displaced_rate"]),
            ("descents_raw", pb["descents_raw"]), ("descent_rate_raw", pb["descent_rate_raw"]),
            ("runner_up", runner), ("runner_up_descents", pv[runner]["descents"]),
            ("margin_descents", pv[runner]["descents"] - pb["descents"]),
            ("worst_varnamala_rule", ranked[-1]),
            ("worst_varnamala_descent_rate", pv[ranked[-1]]["descent_rate"]),
            ("control_roman_descent_rate", pv["roman"]["descent_rate"]),
            ("control_ascii_descent_rate", pv["ascii"]["descent_rate"]),
            ("isolated_descents", n_iso),
            ("descents_inside_displaced_blocks", pb["descents"] - n_iso),
        ])),
        ("factor_status", status),
        ("descent_profile", descent_profile(us, ev["within"])),
        ("merged_supplement", merged),
        ("policy_contrasts", factors),
        ("view_effect", OrderedDict((v, OrderedDict([
            ("units", per_view[v][best]["units"]),
            ("descent_rate", per_view[v][best]["descent_rate"]),
            ("displaced_rate", per_view[v][best]["displaced_rate"])])) for v in per_view)),
        ("segments", segment_map(us, ev)),
        ("homonyms", homonyms(view_records(recs, primary, code), us, ev["bounds"])),
        ("nesting", nesting(print_recs, best, cache)),
        ("displaced_blocks", blocks),
        ("isolated_counterexamples_sample", isolated),
        ("rates", per_view),
    ])
    if code in ROOT_MARK:
        _, st = heads_filter(main_recs)
        mu = units(main_recs)
        mev = evaluate(mu, best, cache)
        st["main_view_descent_rate_same_rule"] = rate(len(mev["within"]), len(mu) - 1 - len(mev["restarts"]))
        st["heads_view_descent_rate"] = pb["descent_rate"]
        st["descent_rate_by_distance_from_last_root"] = root_distance_profile(us, ev)
        roots_only = [u for u in us if u["root"]]
        rev = evaluate(roots_only, best, cache)
        st["roots_only_units"] = len(roots_only)
        st["roots_only_descents"] = len(rev["within"])
        roots_rate = rate(len(rev["within"]), len(roots_only) - 1 - len(rev["restarts"]))
        st["roots_only_descent_rate"] = roots_rate
        st["vowel_grade_filter"] = nest_aware_block(main_recs, best, cache,
                                                    pb["descent_rate"], roots_rate)
        out["root_nests"] = st
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="M11 access-structures census (H5331)")
    ap.add_argument("--dicts", nargs="+", default=DICTS)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--csl", default=CSL)
    args = ap.parse_args(argv)
    rules_rows, cex_rows, dicts = [], [], []
    for code in args.dicts:
        print(f"[m11] {code} …", file=sys.stderr)
        dicts.append(run_dict(code, rules_rows, cex_rows, args.csl))
    os.makedirs(args.out_dir, exist_ok=True)
    env = OrderedDict([
        ("schemaVersion", "1.0.0"),
        ("dataset", "access_structures"),
        ("generatedBy", "python scripts/lexico/m11_access_structures.py"),
        ("handoff", "H5331"),
        ("cslOrigCommit", csl_orig_commit(args.csl)),
        ("sourceFiles", [f"csl-orig/v02/{c}/{c}.txt" for c in args.dicts]),
        ("assumptions", [
            "Printed order = csl-orig record order; alias records ({{Lbody=N}}) are digitiser additions and are excluded from every view but `all`.",
            "Sort key = k1 (accentless normalised SLP1); k2 accents and hyphens are not a sort level.",
            "Consecutive records with the same k1 are one position (unit).",
            "A descent is an alphabet restart (segment boundary, e.g. a supplement) when the next %d units all sort below the previous %d; restarts are reported as segments, not counted as violations." % (RESTART_WINDOW, RESTART_WINDOW),
            "A policy contrast needs >= %d disagreeing adjacent pairs; fewer = undetermined." % MIN_SENSITIVE,
            "AP's collation is scored on its `heads` view (paragraph run-ons and root-nest derivatives removed); its `main` view is reported alongside.",
            "Running heads are not in the csl-orig data; they are out of scope for this census.",
        ]),
        ("base_order", " ".join(VARNA)),
        ("rules", RULES),
        ("views", VIEWS),
        ("thresholds", OrderedDict([("min_disagreeing_pairs", MIN_SENSITIVE),
                                    ("restart_window_units", RESTART_WINDOW),
                                    ("displaced_block_min_units", RUN_MIN)])),
        ("dicts", dicts),
    ])
    with open(os.path.join(args.out_dir, "access_structures.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(env, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(os.path.join(args.out_dir, "access_structures_rules.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["dict", "view", "rule", "units", "segments", "descents_raw", "descent_rate_raw",
                    "descents", "descent_rate", "displaced", "displaced_rate"])
        w.writerows(rules_rows)
    with open(os.path.join(args.out_dir, "access_structures_counterexamples.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["dict", "view", "rule", "kind", "sensitive_to_anusvara_visarga_policy", "unit_index",
                    "prev_L", "prev_pc", "prev_k1", "prev_iast", "next_L", "next_pc", "next_k1", "next_iast"])
        w.writerows(cex_rows)
    for d in dicts:
        b = d["best_fit"]
        print(f"{d['label']:9} {d['primary_view']:5} best {b['rule']:14} seg {b['segments']:>3} "
              f"descents {b['descents']:>5} ({b['descent_rate']:.3%}) displaced {b['displaced_rate']:.3%} "
              f"| runner {b['runner_up']} +{b['margin_descents']} | roman {b['control_roman_descent_rate']:.1%}")
        print("    " + "  ".join(f"{f_}={v['policy']}[{v['status']}]" + (f"~{','.join(v['indistinguishable_from'])}" if v["indistinguishable_from"] else "")
                                   for f_, v in d["factor_status"].items()))


if __name__ == "__main__":
    main()
