# Microstructure subentry inventory — M1 + M2 results

**Date**: 2026-06-03 · **Phase**: L0.6 (Subentry analysis) → Article 9 ("verb-derivation matrix")
**Scripts**: [`scripts/lexico/m1_subentries.py`](../scripts/lexico/m1_subentries.py), [`scripts/lexico/m2_preverbs.py`](../scripts/lexico/m2_preverbs.py)
**Companion**: [`MICROSTRUCTURE-MACROSTRUCTURE.md`](MICROSTRUCTURE-MACROSTRUCTURE.md) (the 15-category subentry typology this operationalises)

Empirical first pass over **all 43 local csl-orig dicts (1,495,459 entries scanned)**.
Two complementary, deterministic signals — no LLM, no sampling. Outputs in `data/lexico/`.

---

## Method

| | M1 — derivative subentries | M2 — preverb subentries |
|---|---|---|
| Signal | `<ab>…</ab>` abbreviation tags, **case-insensitively** (MW `Caus.` = PWG `caus.`) | `<div n="p">— {#preverb#} {%gloss%}` blocks |
| Categories | caus, pass, desid, intens, den, periphr, comp (cats 1–6 + 14) | preverb-verb subentries (cats 7–10) |
| Token discipline | lowercased + dot-stripped + exact-set match, so `compar.` (comparative) ≠ `comp.` | first SLP1 `{#…#}` after the em-dash |
| Output | `microstructure_subentries.csv` (34,180 rows, `n_subentries>0`) | `preverb_subentries.csv` (3,140 rows); joins M1 on `(dict, L)` |

QA confirmed zero false positives: every matched payload is a genuine marker
(`denom.`/`Den.`, `comp.`/`compp.`/`Bah. comp.`, `desid.`/`desid. v.`).

---

## M1 — derivative-subentry density (vderiv/verb = secondary conjugations per verb root)

| Dict | verbal entries | entries w/ subentry | markers | **vderiv/verb** | dominant category |
|---|---|---|---|---|---|
| PW (PWK) | 1,160 | 5,059 | 9,913 | **3.77** | comp |
| GRA (Rigveda) | 390 | 404 | 1,221 | **3.08** | caus |
| BEN | 952 | 3,740 | 5,901 | **2.55** | comp |
| PWG | 2,572 | 5,620 | 9,987 | **2.35** | comp |
| AP90 | 930 | 1,774 | 2,060 | 1.25 | caus |
| AP | 975 | 6,205 | 6,632 | 1.24 | comp |
| STC | 1,442 | 1,472 | 1,645 | 1.12 | caus |
| **MW** | **11,491** | 7,218 | 8,909 | **0.48** | comp |
| **WIL** | 1,912 | 210 | 211 | **0.11** | desid |

**Headline — the macro/micro trade-off, quantified.** MW has *10× the verbal entries* of PW
(11,491 vs 1,160) but the *lowest* derivative density per verb (0.48 vs 3.77). This is the
KPI predicted in MICROSTRUCTURE §3.2: MW promotes preverb-verbs and derivatives to **separate
headwords** (deep macrostructure, shallow microstructure); the Petersburg dicts **nest** them
(shallow macrostructure, deep microstructure). Read the ratio *within* comparable dicts — MW's
`<info verb=>` makes its "verbal" denominator generous.

**"0 markers ≠ structureless"** (mirrors [`CITATION_TAGGING.md`](../data/forensic/CITATION_TAGGING.md)).
**27 of 43 dicts emit zero** `<ab>` derivative markers — not because they are flat, but because
they don't use the European `<ab>` apparatus:
- **Indigenous** (SKD, VCP) — Sanskrit-Sanskrit, prose conventions;
- **MW72** — the 1872 first edition predates MW's `<ab>` apparatus entirely (0 across 55k entries; "prose-heavy, transitional" per MICROSTRUCTURE §1.4, now quantified);
- **Reverse / English-Sanskrit** (MWE), **specialised** (INM, PE, PGN, IEG, SNP, PUI, MCI — name/plant/epigraphy, few verb roots), **continuations** (SCH, CCS), and other bilinguals (BOP, LRV, YAT, …).
- **WIL** is the instructive edge: it marks **desideratives** (`desid. v.`, 119) but essentially never causatives → vderiv/verb 0.11.

---

## M2 — preverb (upasarga) subentries: the Petersburg signature

| Dict | entries w/ preverb sub | preverb subentries | distinct preverbs |
|---|---|---|---|
| PWG | 1,221 | **9,110** | 770 |
| PW (PWK) | 1,178 | **8,428** | 395 |
| CAE | 555 | 3,190 | 193 |
| WIL | 186 | 689 | 50 |

**Corpus-wide preverb productivity** (subentries across all dicts) — the canonical productive
upasargas, ranked empirically:

> **vi** (1,423) · **sam** (1,352) · **pra** (1,334) · **ā** (1,084) · **pari** (1,017) ·
> **abhi** (971) · **ud** (821) · **upa** (758) · **anu** (752) · ava (720) · prati (707) · ni (705)

Validated against the canonical test case: **PWG `gam` = 66 preverb subentries, PW `gam` = 69**
(ati-, adhi-, anu-, abhi-, vyapa-, abhyā-, samud-, upasaṃ-, …) — the "PWG is preverb-dominant"
claim of MICROSTRUCTURE §1.4/§2.2, now a number.

**Lineage cross-check.** **CAE** (Cappeller English, 1891) carries the Petersburg `<div n="p">`
convention (3,190), but its sibling **CCS** (Cappeller German, 1887) reads **0** on both M1 and
M2. So the Cappeller pair — near-identical on *headword* conventions in the L0 study — **diverges
on microstructure markup**. Evidence that content-, convention-, and microstructure-inheritance
are distinct axes (feeds Paper H §5 + the two-axis methods note). **MW = 0 by design**: it has no
preverb div because it promotes preverb-verbs to headwords.

---

## Discoveries / leads for v3

- **`<div n=…>` type-code semantics** (CDSL `<div>` is a flat self-delimiting marker — never closed):

  | code | dicts | meaning |
  |---|---|---|
  | `p` | PWG, PW, CAE, WIL | **preverb subentry** (mined by M2) |
  | `v` | PWG, PW | `Vgl.`/cross-reference (cat 24) |
  | `1`,`2`,`3` | PWG, PW | sense/meaning divisions |
  | `to` | MW (11,000) | sense block ("to approach…"), English-infinitive gloss |
  | `vp` | MW (3,792) | verbal-derivative block — *wraps* the `<ab>Caus./Desid.</ab>` M1 counts |

- **AP encodes compound subtypes**: `Bah. comp.` (bahuvrīhi), `Tat. comp.` (tatpuruṣa),
  `Avyayī. comp.` (avyayībhāva), PWG `copul. comp.` (dvandva) → a future **cat-14 compound-typology**
  pass (m3) can recover samāsa subtypes directly.
- **MW idioms** (object+verb, cat 11) remain **untagged prose** — no dedicated div — confirming
  MICROSTRUCTURE §2.3 that they are MW's prose signature, not machine-recoverable by a uniform marker.

---

## Caveats to carry into the paper

1. `n_subentries` counts marker **mentions**, not distinct top-level blocks: PWG repeats
   `<ab>caus.</ab>` inside each preverb sub-block, so its marker total is a density, not a block count.
2. `verbal_deriv_per_verbal` excludes `comp`/`den` (largely nominal) and is comparable only across
   dicts with a similar `verbal` definition (MW's `<info verb=>` is generous).
3. `max_depth` is a coarse 0/1/2 flag (a single `<ab>Desid. Caus.</ab>` = depth 2); true nesting
   needs per-dict structural parsing.

## Reproduce

```sh
python scripts/lexico/m1_subentries.py --all          # microstructure_subentries.csv
python scripts/lexico/m2_preverbs.py   --all          # preverb_subentries.csv
python scripts/lexico/m1_subentries.py --probe gam    # ground-truth check
```
