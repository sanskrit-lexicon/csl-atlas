# Microstructure subentry inventory — M1–M3 results

**Date**: 2026-06-03 · **Phase**: L0.6 (Subentry analysis) → Article 9 ("verb-derivation matrix")
**Scripts**: [`m1_subentries.py`](../scripts/lexico/m1_subentries.py) (derivative subentries), [`m2_preverbs.py`](../scripts/lexico/m2_preverbs.py) (preverbs), [`m3_xrefs.py`](../scripts/lexico/m3_xrefs.py) (cross-references), [`validate_lexico.py`](../scripts/lexico/validate_lexico.py)
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
| PWG | 1,209 | **8,647** | 315 |
| PW (PWK) | 1,178 | **8,429** | 395 |
| CAE | 555 | 3,303 | 144 |
| WIL | 186 | 702 | 41 |

(A `<div n="p">` block is a preverb subentry only when it opens `— {#preverb#} {%gloss%}`;
blocks that open `— <ab>caus./partic./desid.</ab> {#form#}` are secondary-conjugation forms
already counted by m1, and are excluded — hence these are the *clean* preverb totals.)

**Corpus-wide preverb productivity** (subentries across all dicts) — the canonical productive
upasargas, ranked empirically:

> **vi** (1,439) · **sam** (1,364) · **pra** (1,354) · **ā** (1,098) · **pari** (1,033) ·
> **abhi** (988) · **ud** (827) · **upa** (768) · **anu** (759) · ava (729) · prati (712) · ni (710)

Validated against the canonical test case: **PWG `gam` = 62 preverb subentries**
(accha-, ati-, adhi-, anu-, abhi-, vyapa-, abhyā-, samud-, upasaṃ-, …) — the "PWG is preverb-dominant"
claim of MICROSTRUCTURE §1.4/§2.2, now a number.

**Lineage cross-check.** **CAE** (Cappeller English, 1891) carries the Petersburg `<div n="p">`
convention (3,303), but its sibling **CCS** (Cappeller German, 1887) reads **0** on both M1 and
M2. So the Cappeller pair — near-identical on *headword* conventions in the L0 study — **diverges
on microstructure markup**. Evidence that content-, convention-, and microstructure-inheritance
are distinct axes (feeds Paper H §5 + the two-axis methods note). **MW = 0 by design**: it has no
preverb div because it promotes preverb-verbs to headwords.

---

## M3 — cross-reference edges (cat 24): the internal link graph

Cross-references (`see / cf. / vergleiche X`) split cleanly by tradition, both with an SLP1
target so they are directly comparable:

| Dict | entries w/ xref | edges | kind | distinct targets |
|---|---|---|---|---|
| PWG | 12,283 | **22,987** | `Vgl.` (`<div n="v">`) | 16,351 |
| MW | 7,507 | **7,665** | `cf.` (`<ab>cf.</ab> <s>…</s>`) | 6,636 |

PW/MW72/WIL/indigenous use neither pattern → 0 (a convention gap, not an absence of links).
MW's `cf.` count (11,652) exceeds its captured edges (7,665) because `cf.` + `<lang>` (Western
cognate) / + `<hom>` (homonym pointer) are deliberately skipped — only Sanskrit-lemma targets count.
**Deliberately excluded:** AP/AP90/BEN use `<ab>cf.</ab>` (1,660 / 1,038 / 2,867) too, but there
it is predominantly **cognate** (`<lang>Goth./Gr./L.</lang> {%…%}`) and **citation** (`<ls>`), with
Sanskrit-lemma cross-refs entangled in quote `{#…#}` spans — not a clean seam, so left out rather
than inject noise.

**Hub lemmas** — the most-referenced targets corpus-wide are compound/prefix *families*, not single
lemmas: **a°** (320) · **mahā°** (254) · **su°** (160) · **vi°** (75) · **deva°** (72) · brahma° ·
tri° · sa° · prati° · rāja°. Petersburg cross-references predominantly point "see the X-compounds"
(the `°` = the compound series) — a macrostructural pointer, itself a finding.

Validated: PWG `gam` = 24 atomic `Vgl.` edges (agata, evaṃgata, kaṇṭhagata, adhigantṛ, anugata, …);
30,654 edges total. Feeds the lineage roadmap §3.1 ("shared cross-reference patterns") — a cross-dict
graph-overlap (PWG `Vgl.` set vs MW `cf.` set) is the natural next step.

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

- **Compound subtypes are largely UNtagged** — a negative result for Article 10's premise.
  Samāsa subtypes are sparse: AP `Bah./Tat./Avyayī. comp.` total ~24 (vs 5,051 generic `comp.`),
  AP90 ~28, MW/BEN none. The one systematic distinction is **PWG `adj. comp.` (1,398)**
  (adjectival vs nominal). So a samāsa-typology matrix is not recoverable from markup — CDSL
  dicts record compounds generically; subtype is left to the reader.
- **Cross-references (cat 24)** — done as **M3** above (PWG `Vgl.` + MW `cf.`). Only PWG uses
  `<div n="v">`; PW does not. AP/AP90/BEN `cf.` is mostly cognate/citation, not a clean seam (excluded).
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
python scripts/lexico/m1_subentries.py --all          # microstructure_subentries.csv (derivative subentries)
python scripts/lexico/m2_preverbs.py   --all          # preverb_subentries.csv (preverb subentries)
python scripts/lexico/m3_xrefs.py      --all          # xref_edges.csv (cross-references)
python scripts/lexico/validate_lexico.py              # consistency checks (m1 + m2 + m3)
python scripts/lexico/m1_subentries.py --probe gam    # ground-truth check
```
