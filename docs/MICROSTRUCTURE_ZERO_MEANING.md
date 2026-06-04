# What a "0" means in the microstructure scripts — and what it does NOT

**Date**: 2026-06-03 · Companion to [`MICROSTRUCTURE_M1_M2_RESULTS.md`](MICROSTRUCTURE_M1_M2_RESULTS.md)

## The correction

An earlier summary said *"SKD/VCP/SHS/YAT all 0 as expected."* That phrasing is wrong and
misleading. **SKD has thousands of verbs** (and rich verbal microstructure); so does VCP.
The `0` reported by `m1`/`m2`/`m3` for these dictionaries is a fact about **the detectors**,
not about the dictionaries. This document explains exactly what is counted, proves why these
dicts score 0, and shows how SKD *actually* marks its verbs.

This is the verb-side twin of a mistake already recorded for citations: SKD/VCP are among the
**densest** citers in CDSL (indigenous `iti` + quotation style) yet score **0** on an `<ls>`-based
counter. Same trap, different feature. The rule below generalises both.

## What each script literally counts

All three are **markup detectors** — they search for the European critical-apparatus tags. They
do not "read Sanskrit"; they match XML-ish tokens:

| Script | Counts exactly | Blind to |
|---|---|---|
| `m1_subentries` | `<ab>…</ab>` abbreviation tags whose payload is `caus./pass./desid./intens./den./periphr./comp.` | any verbal info not wrapped in `<ab>` |
| `m2_preverbs` | `<div n="p">— {#preverb#}` blocks | preverbs expressed any other way |
| `m3_xrefs` | `<div n="v">` (`Vgl.`) and `<ab>cf.</ab> <s>target</s>` | cross-refs expressed any other way |

So every count is **"how often this dictionary uses *this specific markup*"** — never "how much of
this phenomenon the dictionary contains."

## The proof: these dicts contain none of that markup

Corpus-wide tag inventory (raw counts of the opening tag):

| dict | `<ab>` | `<div` | `<s>` | `{#…#}` | entries | uses the apparatus? |
|---|---|---|---|---|---|---|
| **SKD** | **0** | **0** | **0** | **0** | 42,531 | none at all |
| **VCP** | **0** | **0** | **0** | **0** | 50,135 | none at all |
| **SHS** | **0** | **0** | 1 | 209,002 | 47,326 | `{#…#}` only |
| **YAT** | **0** | **0** | 0 | 92,979 | 45,206 | `{#…#}` only |
| MW | 182,097 | 15,312 | 350,610 | 0 | 286,560 | full |
| PWG | 185,563 | 113,613 | 0 | 577,105 | 123,366 | full |

`m1` needs `<ab>`, `m2` needs `<div n="p">`, `m3` needs `<div n="v">` or `<ab>cf.</ab><s>`.
**SKD/VCP have zero of all four tag types; SHS/YAT have zero `<ab>` and zero `<div>`.** A
marker-based detector therefore returns 0 *by construction*. The 0 is blindness, not evidence.

## SKD *does* have verbs — marked the indigenous way

SKD (Śabdakalpadruma) is a Sanskrit→Sanskrit kośa: each entry is romanized-Sanskrit prose
(SLP1, headword closed by `¦`, sources cited with `iti`, quotations in `"…"`). It records verbal
microstructure with **indigenous grammatical terminology**, not Latin abbreviations:

| Indigenous marker (in prose) | Meaning | SKD count |
|---|---|---|
| `DAtuH` (dhātuḥ) | "[is a] verbal root" | 267 |
| `preraRe` (preraṇe) | "in the sense of impelling" = **the causative** | 33 |
| `BvAdi` (bhvādi) | conjugation **class 1** (+ other class names) | 79 |
| `parasmEpadI` / `Atmanepadi` | voice (active / middle) | 9 / 19 |
| `sakarmmakaH` / `akarmmakaH` | transitive / intransitive | 6 / 15 |

These are lower bounds on *explicit* tags; verbal forms and derivatives pervade far more of the
42,531 entries. A real example — the root `īr` (SKD `<L>…` entry):

```
Ira¦, ki gatO . preraRe . iti kavikalpadrumaH . (vA, curAM-paraM-sakaM-sew .) nudi . ki Irayati Irati .
```

Read: *"īr — [class] in the sense 'to go' (gatau); **preraṇe** (in the causative sense); thus the
Kavikalpadruma [a dhātupāṭha]; (optionally curādi, parasmaipada, sakarmaka, …); īrayati, īrati [the
forms]."* This entry contains a root, its meaning, a **causative**, a conjugation class, a voice, a
transitivity, a grammarian citation, and inflected forms — and **not one `<ab>` tag**. `m1` sees 0.
VCP (Vācaspatya) is the same indigenous style (`DAtuH` ×164, `parasmEpadI` ×8, …).

## Why each "0" dict is 0 — three different reasons, none of them "no verbs"

1. **Indigenous Sanskrit→Sanskrit (SKD, VCP)** — no Western markup whatsoever; verbs, causatives,
   classes, and voice are written in Sanskrit prose (`dhātuḥ`, `preraṇe`, `bhvādi`, `iti`-sources).
2. **Terse English→Sanskrit (SHS, YAT)** — use `{#…#}` SLP1 headwords/forms + English glosses but
   **no `<ab>` apparatus**; verbs are present, secondary conjugations simply aren't tagged.
3. **MW72** — the 1872 first Monier-Williams predates MW's `<ab>` apparatus (0 across 55k entries).
4. **Specialised dicts (INM, PE, SNP, PGN, IEG, …)** — name/plant/epigraphy lexicons that genuinely
   contain few verb roots (a content fact, but still not measured by these detectors).

## The rule (carry into every paper claim)

> Marker-based counts are comparable **only within the set of dictionaries that share the same
> markup convention** (the `<ab>`/`<div>` European apparatus: MW, PWG, PW, AP, AP90, BEN, …).
> A cross-dictionary **0 is never a statement about content.** Report it as "does not use this
> markup," never as "lacks this feature."

(Identical to the citation lesson in [`../data/forensic/CITATION_TAGGING.md`](../data/forensic/CITATION_TAGGING.md):
"0 `<ls>` ≠ citation-free.")

## Measuring SKD/VCP verbal microstructure — prototyped (M4)

[`scripts/lexico/m4_indigenous.py`](../scripts/lexico/m4_indigenous.py) is the indigenous-tradition
counterpart to `m1`. It flags a **verbal-root entry** by **two complementary signals** (recorded per
row in `root_signal`):
- **citation** — the entry names a dhātupāṭha; the Kavikalpadruma (`iti kavikalpadrumaH`, 2,135× in
  SKD) is purely a root-list, so citing it ⟹ a root. This carries **SKD**, which cites consistently.
- **annotation** — the dhātupāṭha grammatical annotation itself: the seṭ/aniṭ token (`sew`/`aniw`)
  together with a pada/transitivity abbreviation (`para0`/`Atma0`/`saka0`/…), as in VCP's
  `aGa¦ … BvAdi0 Atma0 saka0 sew`. This carries **VCP**, which names its source rarely. The
  pada/transitivity co-requirement keeps it from firing on a stray SLP1 substring in a European
  `{#…#}` body (verified: European dicts stay ≈0 — MW72 1, the rest 0).

Inside each root it **emits the dhātupāṭha annotation as columns** — `gaṇa` (the 10 conjugation
classes), `pada` (parasmaipada/ātmanepada/ubhayapada), `transitivity` (sakarmaka/akarmaka),
`causative` (preraṇe/ṇijanta), and `seṭ`/`aniṭ`. VCP's gaṇa names carry the `0` abbreviation marker
(`BvA0`, `curA0`), which disambiguates them from the `-ādi` ("etc.") suffix.

**Results** — for the very dicts that read **0** under `m1`'s `<ab>` apparatus:

| dict | indigenous roots (M4) | seṭ | aniṭ | causative | `<ab>` markers (M1) |
|---|---|---|---|---|---|
| **SKD** | **2,544** | 1,973 | 303 | 17 | **0** |
| **VCP** | **2,230** | 1,950 | 276 | 24 | **0** |
| KRM (dedicated verb-root dict) | 1,757 | 1,696 | 15 | 21 | 0 |
| SHS (Wilson tradition) | 463 | 415 | 63 | 3 | 0 |

The two-signal union lifts VCP from **43 → 2,230**. All three indigenous/root dicts then converge on
**~the size of the Sanskrit dhātupāṭha (~2,000 roots)** — independent corroboration that the signal is
real, not an artifact.

**The emitted annotations are linguistically correct** — itself strong evidence the parse is real,
not noise. VCP's roots break down as: **pada** parasmaipada 1,124 > ubhaya 525 > ātmanepada 248 (the
natural ordering); **transitivity** sakarmaka 1,680 > akarmaka 503; **gaṇa** bhvādi 1,152 ≫ curādi
146 > divādi 85 > adādi 63 > … — and bhvādi (class 1) *should* dwarf the rest, as the largest gaṇa.
A detector inventing matches would not reproduce the known shape of the Sanskrit verb system.

So SKD's "0" became **2,544 verbal roots**, and VCP's **2,230**, the moment the detector matched the
dictionary's *own* convention. The prototype stays conservative — SKD encodes pada/transitivity
mostly via undecoded anubandha it-markers (so its coverage is lower than VCP's); the abbreviated gaṇa
forms carry mild noise; gaṇa/pada/transitivity take the first match; veṭ (optional seṭ) is not split.
A feasibility proof, not a finished parser. But it settles the methodological point:
**the 0 was the detector, never the dictionary.**
