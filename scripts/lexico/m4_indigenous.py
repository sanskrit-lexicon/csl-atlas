"""Phase L0.6 / M4 (PROTOTYPE) — indigenous verbal microstructure (SKD/VCP).

The counterpart to m1. m1 counts the European <ab> apparatus and is structurally
blind to SKD/VCP, which carry ZERO <ab>/<div>/<s> markup (see MICROSTRUCTURE_ZERO_MEANING.md)
yet hold thousands of verbal roots, marked the INDIGENOUS way — in romanized-Sanskrit
prose, dhātupāṭha-style. This prototype recovers that layer.

ROOT DETECTION — three complementary signals (union), recorded per row in `root_signal`:
  (1) CITATION: the entry cites a dhātupāṭha/dhātu-commentary — the Kavikalpadruma
      (`iti kavikalpadrumaH`, SKD 2,135×, a pure verb-list ⟹ root), Durgādāsa, the
      Mādhavīya-dhātuvṛtti, or generic `iti …dhātu…`. This carries SKD (cites consistently).
  (2) ANNOTATION: the dhātupāṭha grammatical annotation itself — the seṭ/aniṭ token
      (`sew`/`aniw`) WITH a pada/transitivity abbreviation (`para0`/`Atma0`/`saka0`/…).
      VCP names its source rarely but annotates its roots this way, so (2) is what recovers
      VCP (43 → ~2,230). The pada/transitivity co-requirement keeps it from firing on a stray
      SLP1 substring in a European `{#…#}` body — verified: European dicts stay ≈0.
  (3) YAT-CONJUGATION: Yates' own compact conjugation block `{#(its) PRESENT-FORM#} <class>.
      {%pada.%}` (see yat_features) — YAT cites no dhātupāṭha and marks no seṭ, so it read 0
      under (1)+(2); this dict-specific signal recovers it (0 → 1,643).
The root dicts then converge on ~the dhātupāṭha's size: SKD 2,544, VCP 2,230, KRM 1,757
(a dedicated root dictionary), YAT 1,643 (Yates), plus SHS 463 (Wilson tradition).

FEATURES emitted per root entry (the dhātupāṭha annotation, as real columns):
  - gana          bhvādi…curādi — the 10 conjugation classes. VCP marks them with `0`-forms
                  (`BvA0`/`BvAdi0`, `curA0`/`cu0`, `tu0`, `ju0`, …); SKD via its visarga prose
                  (`curAdiH`) AND its anubandha slot (see below). (Short forms `di0`/`sO0` held.)
  - pada          parasmaipada / ātmanepada / ubhayapada  (`para0` / `Atma0` / `uBa(ya)0`,
                  prose forms, for SKD the ṅ/ñ anubandhas, and for KRM the cluster short
                  forms `para`/`A`/`uBa` — see the KRM cluster note below)
  - transitivity  sakarmaka / akarmaka  (`saka0` / `aka0`, plus the prose stems
                  `sakarmmak`/`akarmmak` for SKD/Durgādāsa, and KRM's `saka`/`sa`/`aka`;
                  `aka0` is lookbehind-guarded so it does not match inside `saka0`)
  - causative     `preraRe` (preraṇe) / `Rijanta` / `RyantaH`
  - seṭ / aniṭ / veṭ  `sew` / `aniw` / `vew`  (iṭ-augment behavior; veṭ = optionally seṭ,
                  a lossless refinement — `sew … vew` ⟹ set=1 AND vet=1)
  - anubandhas    SKD only — the raw Vopadeva it-letter slot after `¦` (`i|ka` = idit+curādi),
                  decoded to gaṇa/pada via the Dhātudīpikā key (decode_anubandhas).
  - gloss         raw snippet between `¦` and the citation (locative meaning + it-markers).

SKD anubandha decode (verified against the Śabdakalpadruma front matter, the Dhātudīpikā's
46-anubandha phala table — docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md): the it-letters encode
GAṆA + morphophonemic OPERATIONS, with only ṅ/ñ marking pada (parasmaipada is the unmarked
default and is NOT asserted). For SKD, gaṇa = anubandha (primary) ∨ visarga-prose (fallback);
pada = prose ∨ ṅ/ñ anubandha; operation-its (incl. `ma` = mit / nici-hrasva, Pāṇ 6.4.92) live in
the raw `anubandhas` column. PROTOTYPE limitations: the meaning is a raw snippet; abbreviated gaṇa
forms (`adA0`) carry mild noise; gaṇa/pada take the first match. Deliberately conservative.

Reads csl-orig via parse_cslorig. Run from repo root:
    python scripts/lexico/m4_indigenous.py --probe aka --dicts skd vcp
    python scripts/lexico/m4_indigenous.py --all
Outputs (data/lexico/):
    indigenous_roots.csv       per root entry: dict, L, k1, signal, source, gana, pada, transitivity,
                               causative, set, anit, vet, anubandhas, gloss
    indigenous_by_dict.json    per-dict root counts + feature tallies + m1-blindness comparison
    m4_report.json
"""

import os
import re
import sys
import csv
import glob
import json

sys.path.insert(0, os.path.abspath("scripts/forensic"))
from parse_cslorig import iter_entries, CSL_ORIG

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OUT_DIR = "data/lexico"

# TWO root signals (union). (1) CITATION — a dhātupāṭha source is named; consistent in SKD.
# (2) ANNOTATION — the dhātupāṭha grammatical annotation itself is present, i.e. the seṭ/aniṭ
# token (`sew`/`aniw`), which in the indigenous dicts only ever appears in the root cluster
# `…gaṇa-ādi0 pada0 transitivity0 sew .`. VCP names its source rarely but annotates ~2,277
# roots, so this is what recovers VCP's root layer. To stay root-specific (and not fire on a
# stray SLP1 substring in a European {#…#} body) the annotation requires a pada/transitivity
# abbreviation to accompany the seṭ/aniṭ.
_DHATU_SRC = re.compile(r"kavikalpadrum|durgAdAs|mAdhavIya|iti\s+\S*DAtu")
_ANNOT = re.compile(r"(?<![A-Za-z])(sew|aniw)(?![A-Za-z])")
_PADA_TRANS = re.compile(r"(?<![A-Za-z])(para|Atmane?|uBaya?|saka|akarmma|sakarmma|aka)0?(?![A-Za-z])")
_CAUS = re.compile(r"preraRe|Rijanta|RyantaH")
_SET = re.compile(r"(?<![A-Za-z])sew(?![A-Za-z])")
_ANIT = re.compile(r"(?<![A-Za-z])aniw(?![A-Za-z])")
# veṭ (optionally seṭ) — VCP marks it explicitly as `vew` (98 entries), often as
# `sew … ktvA vew` (generally seṭ, veṭ before ktvā). Per decision round 2 #7 this gets
# its OWN column: `sew … vew` ⟹ set=1 AND vet=1 (a lossless refinement, not an override).
# SKD marks veṭ via the `U`/ūdit anubandha, but that decode is HELD pending the maintainer's
# Kavikalpadruma check (MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md), so SKD `vet` stays 0 for now.
_VET = re.compile(r"(?<![A-Za-z])vew(?![A-Za-z])")

# Feature tables: (canonical label, regex). VCP marks each with a trailing `0` abbreviation
# (`para0`, `saka0`, `BvA0`/`BvAdi0`) — the `0` disambiguates the gaṇa names from the ubiquitous
# `-ādi` suffix; SKD states them with a visarga (`curAdiH`) or via anubandhas (not decoded here).
# Boundaries matter: `aka0` (akarmaka) is a substring of `saka0` (sakarmaka), so it is lookbehind-
# guarded. `_first` returns the first label whose pattern hits (ubhaya before para/ātma; gaṇa 1→10).
# Surface forms (verified against VCP): ubhaya `uBa0`/`uBaya0`; parasmaipada `para0`/`pa0`;
# ātmanepada `Atma0` (NOT `Atman0`). Check ubhaya first (it subsumes the others).
_PADA = (
    ("ubhayapada",   re.compile(r"(?<![A-Za-z])(?:uBa(?:ya)?0|uBayapad)")),
    ("parasmaipada", re.compile(r"(?<![A-Za-z])(?:para0|pa0|parasmEpad)")),
    ("atmanepada",   re.compile(r"(?<![A-Za-z])(?:Atma0|Atmanepad)")),
)
# Transitivity. VCP uses the `saka0`/`aka0` abbreviations; SKD/Durgādāsa state it in
# PROSE — and in sandhi (`akarmmako'yaM`, `sakarmmakaH`), so we match the STEM
# `sakarmmak`/`akarmmak` (not the full `…ka`) to catch -ka/-ko/-kaH (decision round 3 #10).
# `aka0`/`akarmmak` stay lookbehind-guarded so they never fire inside `saka0`/`sakarmmak`.
_TRANS = (
    ("sakarmaka", re.compile(r"(?<![A-Za-z])(?:saka0|sakarmmak|sakarmak)")),
    ("akarmaka",  re.compile(r"(?<![A-Za-z])(?:aka0|akarmmak|akarmak)")),
)
# Per gaṇa, the explicit surface forms. The base `{stem}A(?:di)?0|{stem}AdiH` is kept;
# VCP also uses ultra-short forms (`cu0`/`tu0`/`ju0`) that the base misses — added here
# (decision round 2). They are collision-safe. DELIBERATELY EXCLUDED pending maintainer
# review (round 4): `di0` (collides with the `-Adi0` suffix inside BvAdi0/curAdi0/…) and
# `sO0` (unclear expansion — svādi? sautra?). `ada0` (lowercase) is likewise left out.
_GANA = tuple(
    (label, re.compile(rf"(?<![A-Za-z])(?:{'|'.join(forms)})"))
    for label, forms in (
        ("bhvadi",    (r"BvA(?:di)?0", r"BvAdiH")),
        ("adadi",     (r"adA(?:di)?0", r"adAdiH")),
        ("juhotyadi", (r"juhotyA(?:di)?0", r"juhotyAdiH", r"ju0")),
        ("divadi",    (r"divA(?:di)?0", r"divAdiH")),
        ("svadi",     (r"svA(?:di)?0", r"svAdiH")),
        ("tudadi",    (r"tudA(?:di)?0", r"tudAdiH", r"tu0")),
        ("rudhadi",   (r"ruDA(?:di)?0", r"ruDAdiH")),
        ("tanadi",    (r"tanA(?:di)?0", r"tanAdiH")),
        ("kryadi",    (r"kryA(?:di)?0", r"kryAdiH")),
        ("curadi",    (r"curA(?:di)?0", r"curAdiH", r"cu0")),
    )
)
GANA_LABELS = {g for g, _ in _GANA}
PADA_LABELS = {p for p, _ in _PADA}
TRANS_LABELS = {t for t, _ in _TRANS}


def _first(body, table):
    """First canonical label in `table` whose pattern matches `body`, else ''."""
    for label, rx in table:
        if rx.search(body):
            return label
    return ""


# ── KRM cluster parse — KRM does NOT use SKD's anubandha slot (its slot is empty for all
#    1,757 roots). It spells the same Kavikalpadruma grammar out in a parenthesised cluster
#    right after the headword: `(I-BvAdiH-792 sakarmakaH-sew-parasmEpadI)` = bhvādi cl.I,
#    sakarmaka, seṭ, parasmaipada. The gaṇa name (`BvAdiH`/`curAdiH`/…) is caught by `_GANA`
#    anywhere, but the SHORT pada/transitivity forms (`para`/`A`/`uBa`, `saka`/`sa`/`aka`)
#    are not in `_PADA`/`_TRANS` (those expect VCP's `0`-suffix or the full prose stems).
#    Inside the cluster these bare tokens are unambiguous — in particular the bare `A`
#    (=ātmanepada) is safe here, where it would not be in free prose. So KRM pada/trans are
#    parsed cluster-scoped: take the parenthetical group(s) that name a gaṇa, then read the
#    abbreviations from there. (`pada:para` 1,029 · `uBa` 517 · `A` 17; `trans:saka` 1,365 ·
#    `aka` 669 — the 170/50 → ~1.7k gap this closes.)
_KRM_GANA_NAMES = re.compile(r"(?:Bv|ad|juhoty|div|sv|tud|ruD|tan|kry|cur)AdiH")
_KRM_PADA = (
    ("ubhayapada",   re.compile(r"(?<![A-Za-z])uBa(?:ya)?(?:padI)?(?![A-Za-z])")),
    ("parasmaipada", re.compile(r"(?<![A-Za-z])para(?:smEpadI)?(?![A-Za-z])")),
    ("atmanepada",   re.compile(r"(?<![A-Za-z])(?:AtmanepadI|A)(?![A-Za-z])")),
)
_KRM_TRANS = (
    ("sakarmaka", re.compile(r"(?<![A-Za-z])(?:sakarmakaH?|saka|sa)(?![A-Za-z])")),
    ("akarmaka",  re.compile(r"(?<![A-Za-z])(?:akarmakaH?|aka)(?![A-Za-z])")),
)


def krm_cluster(body):
    """The KRM grammar cluster: text inside the parenthetical group(s) that name a gaṇa.
    Tags are stripped first so a cluster split by `<s>…</s>` (`I<s>-BvAdiH</s>-792`) reads
    as one string. Returns '' when no gaṇa-bearing parenthetical is present (e.g. a noun)."""
    text = re.sub(r"<[^>]+>", "", body)
    return " ".join(m.group(1) for m in re.finditer(r"\(([^()]*)\)", text)
                    if _KRM_GANA_NAMES.search(m.group(1)))


# ── YAT (Yates) verbal-root parse — YAT reads 0 under BOTH the dhātupāṭha-citation and the
#    seṭ/aniṭ-annotation signals (it cites no dhātupāṭha and marks no `sew`/`saka0`), so issue
#    #30 flagged it as needing its own format probe. Yates encodes the conjugation compactly in
#    its own English-tradition convention: `{#(anubandhas) PRESENT-FORM#} <class>. {%pada.%}`,
#    e.g. `{#(O-x) gacCati#} 1. {%a.%}` = gam, present gacchati, cl.1 bhvādi, parasmaipada.
#    The class digit (1–10) IS the gaṇa; the pada letter is `a`=parasmaipada (-ti), `d`=ātmanepada
#    (-te, "deponent"), `c`=ubhayapada (both -ti/-te). The leading `(O-x)`/`(Na, wu)` are the same
#    Pāṇinian it-letters SKD uses (recorded raw in `anubandhas`). Requiring a PRESENT form (ending
#    in `ti`/`te`) before the class digit excludes Yates' gender-triple adjectives (`(vaH-vA-vaM)
#    1. {%a.%}` "silent" — where `a.`=adjective, not parasmaipada). 1,643 roots; the gaṇa
#    distribution (bhvādi 1,009 ≫ curādi 219 > tudādi 139 > divādi 117 …) and pada (para 1,162 >
#    ātmane 369 > ubhaya 112) are linguistically correct — the same convergence-on-the-dhātupāṭha
#    that validates SKD/VCP/KRM/SHS.
_YAT_VB = re.compile(r"\{#(?:\(([^)#]*)\)\s*)?[^#]*?(?:ti|te)#\}\s*(10|[1-9])\.\s*\{%([adc])\.")
_YAT_GANA = {"1": "bhvadi", "2": "adadi", "3": "juhotyadi", "4": "divadi", "5": "svadi",
             "6": "tudadi", "7": "rudhadi", "8": "tanadi", "9": "kryadi", "10": "curadi"}
_YAT_PADA = {"a": "parasmaipada", "d": "atmanepada", "c": "ubhayapada"}


def yat_features(body):
    """(gaṇa, pada, raw-anubandhas) from the first Yates conjugation block, or None if the
    entry carries no finite-verb block (so it never fires on a noun/adjective)."""
    m = _YAT_VB.search(body)
    if not m:
        return None
    anu, cls, p = m.group(1), m.group(2), m.group(3)
    return _YAT_GANA[cls], _YAT_PADA[p], " ".join((anu or "").replace(",", " ").split())


# ── SHS (Śabda-Sāgara) feature parse — SHS IS already detected as a root dict (463, via the
#    seṭ/aniṭ + pada/trans annotation), but its features were UNDER-read: it marks the grammar
#    in a VCP-style SLP1 cluster that uses DASH separators (`{#BvA-para-saka-sew .#}`, `curA-uBa0`)
#    where m4's `_GANA`/`_PADA` expect the `0` suffix (`BvA0`/`para0`), so only the few `0`-suffixed
#    or full tokens matched (gaṇa 254/pada 236/trans 266 of 463). Two fixes, both scoped to SHS:
#    (a) parse the `{#…sew…#}` cluster with a dash/0-tolerant gaṇa abbrev + the KRM short-form
#    pada/trans detectors (bare `A`=ātmanepada is safe inside the cluster, as for KRM); (b) fall
#    back to SHS's English ordinal `r. Nth cl.` (present on 421/463) for gaṇa when the cluster is
#    silent. Root DETECTION is unchanged — only the feature columns are filled.
_SHS_CLUSTER = re.compile(r"\{#([^#]*(?:sew|aniw|vew)[^#]*)#\}")
_SHS_GANA = (
    ("bhvadi", re.compile(r"(?<![A-Za-z])BvA(?:di)?[-0]")),
    ("adadi", re.compile(r"(?<![A-Za-z])adA(?:di)?[-0]")),
    ("juhotyadi", re.compile(r"(?<![A-Za-z])juhotyA(?:di)?[-0]")),
    ("divadi", re.compile(r"(?<![A-Za-z])divA(?:di)?[-0]")),
    ("svadi", re.compile(r"(?<![A-Za-z])svA(?:di)?[-0]")),
    ("tudadi", re.compile(r"(?<![A-Za-z])tudA(?:di)?[-0]")),
    ("rudhadi", re.compile(r"(?<![A-Za-z])ruDA(?:di)?[-0]")),
    ("tanadi", re.compile(r"(?<![A-Za-z])tanA(?:di)?[-0]")),
    ("kryadi", re.compile(r"(?<![A-Za-z])kryA(?:di)?[-0]")),
    ("curadi", re.compile(r"(?<![A-Za-z])curA(?:di)?[-0]")),
)
_SHS_ENG = re.compile(r"r\.\s*(10|[1-9])(?:st|nd|rd|th)?\s*cls?")  # English ordinal class
# SHS pada: like the KRM short forms, but SHS also writes ātmanepada dash-joined as `Atma`
# (`BvA-Atma-saka-sew`) — not the bare `A` nor `Atma0` — so atmanepada admits `Atma` too.
_SHS_PADA = (
    ("ubhayapada",   re.compile(r"(?<![A-Za-z])uBa(?:ya)?(?:padI)?(?![A-Za-z])")),
    ("parasmaipada", re.compile(r"(?<![A-Za-z])para(?:smEpadI)?(?![A-Za-z])")),
    ("atmanepada",   re.compile(r"(?<![A-Za-z])(?:AtmanepadI|Atma|A)(?![A-Za-z])")),
)


def shs_cluster(body):
    """The SHS SLP1 grammar cluster — the `{#…#}` block carrying seṭ/aniṭ — or '' if none."""
    m = _SHS_CLUSTER.search(body)
    return m.group(1) if m else ""


# ── SKD anubandha decode — the Vopadeva/Kavikalpadruma key as given by Durgādāsa's
#    Dhātudīpikā, reproduced in the Śabdakalpadruma front matter (46 anubandhas / 1754
#    roots; docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md). SKD writes the it-letters in a slot
#    right after `¦` (`aka¦, i ka` = idit + curādi). They encode GAṆA + morphophonemic
#    OPERATIONS; only ṅ/ñ mark pada (parasmaipada is the unmarked default — NOT asserted).
#    SLP1: ṅ=N ñ=Y ṇ=R ṭ=w ḍ=q ś=S ṣ=z ṛ=f ṝ=F ḷ=x ā=A ī=I ū=U ai=E au=O.
_ANU_GANA = {  # → one of the 10 gaṇas (avāntara subclasses folded to their main gaṇa)
    "ka": "curadi", "ki": "curadi", "ga": "kryadi", "gi": "kryadi", "Ga": "adadi",
    "ja": "bhvadi", "Ja": "bhvadi", "Ra": "bhvadi", "Wa": "bhvadi", "da": "tanadi",
    "Da": "rudhadi", "na": "svadi", "pa": "tudadi", "Ba": "divadi", "mi": "bhvadi",
    "ya": "divadi", "la": "adadi", "li": "juhotyadi", "lu": "adadi", "va": "bhvadi",
    "Sa": "tudadi", "Si": "tudadi", "kza": "adadi",
}
_ANU_PADA = {"Na": "atmanepada", "Ya": "ubhayapada"}
_ANU_OP = {
    "a": "none", "A": "nishtha-vet", "i": "num", "ir": "ad-aug", "I": "anit-nishtha",
    "u": "ktva-vet", "U": "vet", "f": "cang-ahrasva", "F": "cang-ahrasva-va", "x": "ang",
    "e": "sic-avrddhi", "E": "yajadi", "o": "nishtha-na", "O": "anit", "Yi": "present-nishtha",
    "wu": "athu", "qu": "krtrima", "za": "krd-ang", "ta": "adanta", "ra": "vaidika",
    "ma": "nici-hrasva",   # m/mit — penultimate shortens before ṇic (Pāṇ 6.4.92 mitāṃ hrasvaḥ);
}                          # one of the 17 anubandhas Vop. keeps with Pāṇinian sense (Palsule, KKD App. III)
_ANU_KEY = {}
for _d, _kind in ((_ANU_GANA, "gana"), (_ANU_PADA, "pada"), (_ANU_OP, "op")):
    for _k, _v in _d.items():
        _ANU_KEY[_k] = (_kind, _v)
for _two in list(_ANU_KEY):        # bare-consonant variant: the slot may drop inherent 'a' (`i N`=ṅ)
    if len(_two) == 2 and _two.endswith("a") and _two[0].isalpha():
        _ANU_KEY.setdefault(_two[0], _ANU_KEY[_two])
_ANU_GENDER = {"puM,", "klI,", "strI,", "tri,", "puM", "klI", "strI", "tri", "avya0", "[n]"}


def skd_anubandha_slot(body):
    """SKD's anubandha slot: the leading it-letter tokens after `¦`, before the meaning.
    Returns [] for gender-marked nominal entries (so it never fires on a noun)."""
    if "¦" not in body:
        return []
    out = []
    for t in body.split("¦", 1)[1].lstrip(" ,").split():
        if t in _ANU_GENDER:
            return []
        if t in _ANU_KEY or (len(t) <= 2 and re.fullmatch(r"[A-Za-zfFxX]+", t)):
            out.append(t)
        else:
            break
    return out


def decode_anubandhas(slot):
    """(gaṇa, pada, [operations]) from a slot per the Dhātudīpikā key. First gaṇa/pada wins;
    pada only from ṅ/ñ (parasmaipada = unmarked default, deliberately NOT asserted here)."""
    gana = pada = ""
    ops = []
    for t in slot:
        kv = _ANU_KEY.get(t)
        if not kv:
            continue
        kind, val = kv
        if kind == "gana" and not gana:
            gana = val
        elif kind == "pada" and not pada:
            pada = val
        elif kind == "op":
            ops.append(val)
    return gana, pada, ops


def analyze_entry(body, code=None):
    """Return root-entry features, or None if the entry is not a verbal root. For SKD the
    gaṇa/pada come from the Vopadeva anubandha slot (the authoritative Dhātudīpikā key);
    other dicts use the `0`-marked / prose detectors."""
    cite = bool(_DHATU_SRC.search(body))
    annot = bool(_ANNOT.search(body)) and bool(_PADA_TRANS.search(body))
    yat = yat_features(body) if code == "yat" else None
    if not (cite or annot or yat):
        return None
    if "kavikalpadrum" in body:
        src = "kavikalpadruma"
    elif "mAdhavIya" in body:
        src = "madhaviya"
    elif "durgAdAs" in body:
        src = "durgadasa"
    elif cite:
        src = "dhatupatha"
    elif yat:
        src = "(yat-conjugation)"
    else:
        src = "(annotation-only)"
    signal = ("both" if (cite and annot) else "citation" if cite
              else "annotation" if annot else "yat-conjugation")
    snip = ""
    if "¦" in body:                       # ¦ closes the headword
        after = body.split("¦", 1)[1]
        snip = " ".join(after.split(" iti ", 1)[0].split())[:60].strip()
    gana = _first(body, _GANA)
    pada = _first(body, _PADA)
    trans = _first(body, _TRANS)
    anubandhas = ""
    if code == "skd":                     # decode the Vopadeva slot (authoritative for SKD)
        slot = skd_anubandha_slot(body)
        if slot:
            anubandhas = "|".join(slot)
            a_gana, a_pada, _ops = decode_anubandhas(slot)
            if a_gana:                    # anubandha gaṇa supersedes the crude detector
                gana = a_gana
            if a_pada and not pada:        # ṅ/ñ pada where the prose is silent
                pada = a_pada
    elif code == "krm":                   # KRM spells grammar in a parenthesised cluster, not a slot
        cluster = krm_cluster(body)
        if cluster:                       # cluster-scoped short forms (para/A/uBa, saka/sa/aka)
            k_pada = _first(cluster, _KRM_PADA)
            k_trans = _first(cluster, _KRM_TRANS)
            if k_pada:
                pada = k_pada
            if k_trans:
                trans = k_trans
    elif yat:                             # Yates encodes class+pada in its own conjugation block
        gana, pada, anubandhas = yat[0], yat[1], yat[2]
    elif code == "shs":                   # SHS marks grammar in a dash-joined SLP1 cluster + English ordinal
        cl = shs_cluster(body)
        if cl:                            # cluster short forms (para/A/uBa, saka/aka) + dash/0 gaṇa
            s_gana = _first(cl, _SHS_GANA)
            s_pada = _first(cl, _SHS_PADA)
            s_trans = _first(cl, _KRM_TRANS)
            if s_gana:
                gana = s_gana
            if s_pada:
                pada = s_pada
            if s_trans:
                trans = s_trans
        if not gana:                      # fall back to the English ordinal `r. Nth cl.`
            em = _SHS_ENG.search(body)
            if em:
                gana = _YAT_GANA[em.group(1)]
    return {
        "root_signal": signal,
        "dhatupatha_source": src,
        "gana": gana,
        "pada": pada,
        "transitivity": trans,
        "causative": int(bool(_CAUS.search(body))),
        "set": int(bool(_SET.search(body))),
        "anit": int(bool(_ANIT.search(body))),
        "vet": int(bool(_VET.search(body))),
        "anubandhas": anubandhas,
        "gloss_snippet": snip,
    }


def discover_dicts():
    return sorted(os.path.basename(os.path.dirname(p))
                  for p in glob.glob(os.path.join(CSL_ORIG, "*", "*.txt"))
                  if os.path.basename(p)[:-4] == os.path.basename(os.path.dirname(p)))


def src_path(code):
    return os.path.join(CSL_ORIG, code, f"{code}.txt")


def probe(lemma, codes):
    print(f"\n--probe {lemma}: indigenous root entries per dict\n" + "-" * 64)
    for code in codes:
        path = src_path(code)
        if not os.path.exists(path):
            continue
        for e in iter_entries(path):
            if e["k1"] != lemma:
                continue
            a = analyze_entry(e["body"], code)
            if not a:
                continue
            tags = [a["gana"], a["pada"], a["transitivity"]] + [f for f in ("causative", "set", "anit", "vet") if a[f]]
            tags = ", ".join(t for t in tags if t)
            anu = f" anu={a['anubandhas']}" if a["anubandhas"] else ""
            print(f"  {code.upper():5s} L{e['L']:<7s} sig={a['root_signal']:<10s} [{tags or '-'}]{anu}  {a['gloss_snippet']!r}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    if "--dicts" in args:
        i = args.index("--dicts")
        codes = [a for a in args[i + 1:] if not a.startswith("--")]
    else:
        codes = discover_dicts()
    if "--probe" in args:
        probe(args[args.index("--probe") + 1], codes)
        return
    if "--all" not in args and "--dicts" not in args:
        print("Specify --all, --dicts <codes>, or --probe <lemma>.", file=sys.stderr)
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    print("=" * 64)
    print(f"M4 (prototype) — indigenous verbal roots  ({len(codes)} dicts)")
    print("=" * 64)

    by_dict = {}
    csv_path = os.path.join(OUT_DIR, "indigenous_roots.csv")
    fields = ["dict", "L", "k1", "root_signal", "dhatupatha_source",
              "gana", "pada", "transitivity", "causative", "set", "anit", "vet",
              "anubandhas", "gloss_snippet"]
    n_rows = 0
    with open(csv_path, "w", encoding="utf-8", newline="") as fcsv:
        w = csv.DictWriter(fcsv, fieldnames=fields)
        w.writeheader()
        for code in codes:
            path = src_path(code)
            if not os.path.exists(path):
                continue
            agg = {"entries": 0, "root_entries": 0, "causative": 0, "set": 0, "anit": 0, "vet": 0,
                   "by_source": {}, "by_signal": {}, "by_gana": {}, "by_pada": {}, "by_transitivity": {}}
            for e in iter_entries(path):
                agg["entries"] += 1
                a = analyze_entry(e["body"], code)
                if not a:
                    continue
                agg["root_entries"] += 1
                for f in ("causative", "set", "anit", "vet"):
                    agg[f] += a[f]
                agg["by_source"][a["dhatupatha_source"]] = agg["by_source"].get(a["dhatupatha_source"], 0) + 1
                agg["by_signal"][a["root_signal"]] = agg["by_signal"].get(a["root_signal"], 0) + 1
                for col in ("gana", "pada", "transitivity"):
                    if a[col]:
                        agg["by_" + col][a[col]] = agg["by_" + col].get(a[col], 0) + 1
                w.writerow({"dict": code, "L": e["L"], "k1": e["k1"] or "", **a})
                n_rows += 1
            if agg["root_entries"]:
                by_dict[code] = agg
                tg = max(agg["by_gana"], key=agg["by_gana"].get) if agg["by_gana"] else "-"
                print(f"  {code:6s} roots={agg['root_entries']:>6,} caus={agg['causative']:>4,} "
                      f"seṭ={agg['set']:>5,} aniṭ={agg['anit']:>4,} veṭ={agg['vet']:>4,} "
                      f"pada={sum(agg['by_pada'].values()):>5,} trans={sum(agg['by_transitivity'].values()):>5,} "
                      f"gaṇa={sum(agg['by_gana'].values()):>5,}(top {tg})")

    by_dict_path = os.path.join(OUT_DIR, "indigenous_by_dict.json")
    with open(by_dict_path, "w", encoding="utf-8") as f:
        json.dump({"dicts": by_dict}, f, indent=2, ensure_ascii=False)

    report = {
        "prototype": True,
        "csv_rows": n_rows,
        "dicts_with_roots": list(by_dict.keys()),
        "headline": {c: {"indigenous_roots_m4": a["root_entries"], "ab_markers_m1": 0}
                     for c, a in by_dict.items() if c in ("skd", "vcp", "krm", "yat", "shs")},
        "method": ("Root = (1) dhātupāṭha citation OR (2) the seṭ/aniṭ + pada/transitivity annotation "
                   "OR (3) YAT's own conjugation block `(its) PRESENT-FORM <class>. {pada}` "
                   "(recorded in root_signal). Emitted columns: gaṇa (bhvādi…curādi, via VCP's 0-marked "
                   "forms BvA0/curA0/…, KRM's parenthesised cluster, SHS's dash-joined cluster "
                   "and English ordinal, YAT's class digit, or SKD's anubandha slot), "
                   "pada (parasmaipada/ātmanepada/ubhayapada), transitivity "
                   "(sakarmaka/akarmaka), causative (preraṇe/ṇijanta), seṭ/aniṭ."),
        "caveats": ("PROTOTYPE. SKD/VCP read 0 under m1's <ab> apparatus but carry ~2k roots each — the "
                    "0 was detector blindness (MICROSTRUCTURE_ZERO_MEANING.md). SKD pada/gaṇa are now "
                    "decoded from its Vopadeva anubandha slot via the authoritative Dhātudīpikā 46-anubandha "
                    "key (MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md, verified against the Śabdakalpadruma front "
                    "matter): the it-letters encode GAṆA + operations, only ṅ/ñ mark pada (parasmaipada is "
                    "the unmarked default, not asserted); `ma` = m/mit (nici-hrasva). gaṇa/pada "
                    "take the first match; abbreviated gaṇa forms (adA0/svA0) carry mild noise; veṭ (vew) "
                    "split into its own column. KRM carries an EMPTY anubandha slot (slot=0 for all 1,757) "
                    "but spells the same Kavikalpadruma grammar in a parenthesised cluster "
                    "(`(I-BvAdiH-792 saka-sew-para)`); krm_cluster reads its short pada/trans forms "
                    "(para/A/uBa, saka/sa/aka) cluster-scoped — pada 170→1,378, trans 50→1,735. "
                    "YAT's class digit and `a`/`d`/`c` pada marker are decoded, while its raw "
                    "parenthesised it/anubandha material is preserved but not interpreted; "
                    "YAT transitivity and seṭ/aniṭ are not systematically decoded pending "
                    "source-specific review. SHS root detection is unchanged; this pass only fills "
                    "gaṇa/pada/transitivity from its dash-joined SLP1 cluster and `r. Nth cl.` "
                    "English ordinal where already-detected root rows were under-read. "
                    "Sanity-checked: VCP pada parasmaipada>ubhaya>ātmane and "
                    "gaṇa bhvādi≫rest are linguistically correct."),
    }
    with open(os.path.join(OUT_DIR, "m4_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nHeadline: " + "; ".join(
        f"{c.upper()} {a['root_entries']:,} indigenous roots (m1 <ab> = 0)"
        for c, a in by_dict.items() if c in ("skd", "vcp")))
    print(f"Wrote {csv_path} ({n_rows:,} rows), {os.path.basename(by_dict_path)}, m4_report.json")
    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source(csv_path, "m4_indigenous.py", 6)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
