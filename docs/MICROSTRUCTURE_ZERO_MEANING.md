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

## To actually measure SKD/VCP verbal microstructure

It needs a **separate indigenous-marker parser** (`m-indigenous`, not a tweak to `m1`) keyed on the
prose tokens above: `dhātuḥ` root detection, `preraṇe`/ṇic forms (causative), conjugation-class names
(`bhvādi`, `adādi`, `curādi`, …), pada/voice, transitivity, and `iti`-source attribution. Until that
exists, SKD/VCP/SHS/YAT must be reported as **out of scope for the `<ab>`/`<div>` detectors**, not as
zero-structure dictionaries.
