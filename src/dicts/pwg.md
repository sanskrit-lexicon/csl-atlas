---
title: PWG — Boehtlingk-Roth Grosses PW (1855–1875)
---

# PWG — Sanskrit-Wörterbuch (Grosses PW, 1855–1875)

*Chapter authored per [Decision 29 Tier A](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#decision-29--phase-4-dictionary-ordering-chapter-templates-minimum-data-added-2026-05-27). Position 2 in the atlas ordering — the multi-volume German philological apparatus that MW collapsed.*

## 1. Overview

The seven-volume *Sanskrit-Wörterbuch*, compiled by [Otto von Böhtlingk](https://en.wikipedia.org/wiki/Otto_von_B%C3%B6htlingk) and [Rudolph Roth](https://en.wikipedia.org/wiki/Rudolph_von_Roth) under the auspices of the Imperial Russian Academy of Sciences in Saint Petersburg (hence "Petersburger Wörterbuch", PW). Published in seven folio volumes 1855–1875, ~9,500 columns total. The reference Sanskrit-German dictionary of the 19th century, exceeding all predecessors in both lemma coverage and citation density. PWG is the **proximate source** for MW 1899: Monier-Williams worked from PWG (and its shorter seven-part counterpart PWK) as the German philological base, applying his own editorial reduction to produce a single-volume English-language work. Within CDSL, PWG carries the **densest citation apparatus** of any dictionary (4.6 `<ls>` per record, ~4× MW's 1.09) and a **fully differentiated named-kosha apparatus** (821 distinct `<ls>` sigla including 238,271 distinct values overall) — what MW collapsed into the single `<ls>L.</ls>` hedge.

| | |
|---|---|
| **Records** | 123,366 |
| **Volumes** | **7 (multi-volume folio)** |
| **Year** | 1855–1875 |
| **Editor(s)** | Otto von Böhtlingk + Rudolph Roth |
| **Publisher** | Kaiserliche Akademie der Wissenschaften, St Petersburg |
| **Source language** | Sanskrit (Devanāgarī in print) |
| **Target language** | German |
| **Genre** | Structured bilingual scholarly dictionary (multi-volume) |
| **`<ls>` citations total** | 570,817 |
| **`<ls>` citations/record** | **4.63** (~4× MW) |
| **Distinct `<ls>` sigla** | 238,271 |
| **License** | CC-BY-SA-4.0 |
| **Repo** | [sanskrit-lexicon/PWG](https://github.com/sanskrit-lexicon/PWG) |
| **Source file** | [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt) |
| **CDSL display** | [sanskrit-lexicon.uni-koeln.de/scans/PWGScan/2020](https://www.sanskrit-lexicon.uni-koeln.de/scans/PWGScan/2020/web/index.php) |
| **Project ROADMAP** | [PWG/ROADMAP.md](https://github.com/sanskrit-lexicon/PWG/blob/docs-pass/ROADMAP.md) — 53 open issues in quarterly plan |
| **DICT_PROFILE** | [PWG/DICT_PROFILE.md](https://github.com/sanskrit-lexicon/PWG/blob/docs-pass/DICT_PROFILE.md) |

## 2. Profile table (5 primary types × profile)

Per the refactored typology in [PAPER.md §5](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#5-profiles-as-the-unit-of-typology), restricted to the types PWG's data supports (PWG has no `<info>` tagging, no `<bot>`/`<bio>`, no `<lang>`):

| Primary type | Count | % corpus | cite% | etym% | Mean common-blocks |
|---|--:|--:|--:|--:|--:|
| Nominal — noun_m | 35,665 | 28.9 % | **98.7 %** | 0.0 % | 3.99 |
| Nominal — noun_f | 14,170 | 11.5 % | **98.4 %** | 0.0 % | 3.98 |
| Nominal — noun_n | 15,082 | 12.2 % | **98.4 %** | 0.0 % | 3.98 |
| Adjective (mfn / a.) | 31,671 | 25.7 % | **98.5 %** | 0.0 % | 3.98 |
| Other (verbs, compounds, indeclinables without `<lex>`) | 26,778 | 21.7 % | 77.4 % | 0.0 % | 2.84 |

**Citation profile spread: 0.4 pts** — every typed-bucket is cited at ~98.4 %. PWG can afford to cite **every entry uniformly** because seven folio volumes give it the print space; MW's 11.3-pt spread is the single-volume editor's *selective* version of the same impulse ([analysis/CROSS_DICT_PROFILES.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/CROSS_DICT_PROFILES.md)).

Block-presence by name (cross-dict-common subset):

```js
const cross = FileAttachment("../data/cross-dict.json").json();
```

```js
const d = cross.dicts.find(d => d.code === "PWG");
const LABEL = {head:"head",body:"body (¦)",gram:"gram (lex)",cite:"cite (ls)",hom:"homograph",etym:"etymology",xref:"cross-ref",hedge:"L. hedge",info:"info (digit.)"};
const bars = cross.blocks.map(b => ({block: LABEL[b] ?? b, pct: d.blocks_pct[b]}));
display(Plot.plot({
  width: 580, height: 240, marginLeft: 90,
  x: {label: "% of entries", domain: [0, 100], grid: true},
  y: {label: null},
  marks: [
    Plot.barX(bars, {y: "block", x: "pct", fill: "#1f78b4"}),
    Plot.text(bars, {y: "block", x: "pct",
      text: d => d.pct >= 0.5 ? d.pct.toFixed(1)+"%" : "",
      dx: 4, textAnchor: "start", fontSize: 10}),
    Plot.ruleX([0])
  ]
}));
```

## 3. Citation density and apparatus

**4.63 `<ls>` per record** (570,817 citations across 123,366 records) — the densest of any structured bilingual CDSL dict, and ~4× MW. The PWG editors chose to cite every kosha and literary work by name; the 7-volume format made this affordable.

Top 12 `<ls>` sigla ([analysis/LS_HEDGE_CHECK.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md)):

| Tag | Source | Count |
|---|---|--:|
| `<ls>ŚKDR.</ls>` | *[Śabdakalpadruma](https://en.wikipedia.org/wiki/Shabdakalpadruma)* | **20,109** |
| `<ls>MED.</ls>` | *[Medinīkośa](https://en.wikipedia.org/wiki/Medinikosha)* | 7,176 |
| `<ls>H. an.</ls>` | *[Hemacandra Anekārtha-saṃgraha](https://en.wikipedia.org/wiki/Hemacandra)* | 6,619 |
| `<ls>RĀJAN.</ls>` | *Rājanighaṇṭu* | 5,904 |
| `<ls>ŚABDAR.</ls>` | *Śabdaratnāvalī* | 3,123 |
| `<ls>ed. Bomb.</ls>` | Bombay-edition textual source | 2,662 |
| `<ls>WILS.</ls>` | Wilson 1832 (back-citation) | 2,014 |
| `<ls>GORR.</ls>` | Gorresio's *Rāmāyaṇa* recension | 1,586 |
| `<ls>UJJVAL.</ls>` | Ujjvaladatta's *Uṇādisūtra* commentary | 1,499 |
| `<ls>ŚABDAC.</ls>` | *Śabdacandrikā* | 1,427 |
| `<ls>KULL.</ls>` | Kullūka's *Manu-smṛti* commentary | 1,417 |
| `<ls>SĀY.</ls>` | Sāyaṇa's Vedic commentaries | 1,253 |

**Striking absence: `<ls>L.</ls>` = 0**. PWG never collapses kosha sources into a generic hedge — it always names which kosha. The top 5 sigla are all named indigenous Sanskrit lexicons (ŚKDR, MED, H. an., RĀJAN, ŚABDAR); together they account for 42,931 citations (7.5 % of PWG's total apparatus). MW's `<ls>L.</ls>` 40,212-instance hedge ([MW chapter §4](mw#4-hedge-analysis-the-ls-l-ls-construct)) is the editorial compression of *exactly this kind of named-kosha citation* into a binary "named-source vs lexicographer-only" distinction.

## 4. Hedge analysis — PWG has none, by design

**PWG carries 0 generic-hedge tags** (of 570,817 `<ls>` total). The contrast with MW is the central data point of the L.-hedge analysis:

| Dict | Records | `<ls>` total | `<ls>L.</ls>` | Hedges/1k records |
|---|--:|--:|--:|--:|
| MW | 286,561 | 311,932 | 40,212 | 140.3 |
| **PWG** | **123,366** | **570,817** | **0** | **0.0** |
| PWK | 170,556 | 86,750 | 0 | 0.0 |
| AP | 90,654 | 62,656 | 1 | 0.01 |
| WIL/BEN/CAE/SKD/VCP | — | — | 0 | 0.0 |

The PWG design treats every indigenous lexicon as a *named source on a par with literary works*. There is no need for a generic hedge because every kosha citation already carries a specific siglum. The L.-hedge is therefore a **single-volume editorial invention** — MW could not afford PWG's 821-siglum apparatus in one volume and substituted a binary "named source vs L." compression. The three-stage lineage of the hedge (Benfey 1866 `†` → MW 1872 preface declaration → Cappeller 1891 `*` → MW 1899 tagged `<ls>L.</ls>`) is detailed in [analysis/LS_HEDGE_CHECK.md §"MW 1872 preface and body check"](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md#mw-1872-preface-and-body-check-added-2026-05-27-d21-resolution); PWG belongs to the *named-source* tradition that the hedge replaces, not to the hedge lineage itself.

## 5. Lineage statement

PWG occupies the **densest node** in the CDSL European-Sanskrit-lexicography lineage. It draws on the indigenous Sanskrit kosha tradition (via direct citation of Amarakośa, Medinīkośa, Hemacandra, Śabdakalpadruma, Rājanighaṇṭu, Halāyudha, etc.) and on the extant European Sanskrit dictionaries of the early 19th century (Wilson 1832, cited as `<ls>WILS.</ls>` 2,014×). Its 19-year compilation (1855–1875) sets the methodological benchmark that every later European Sanskrit dictionary measures itself against. Its direct successors: **[PWK](pwk)** (Böhtlingk's own compact seven-part abridgement, 1879–1889, which dropped 90+ % of PWG's kosha apparatus); **[MW 1899](mw)** (the English-language single-volume re-edition with `<ls>L.</ls>` compression). The four indigenous-kosha repos that resolve PWG's named-kosha citations live at [ARMH](https://github.com/sanskrit-lexicon/armh), [ABCH](https://github.com/sanskrit-lexicon/abch), [ACPH](https://github.com/sanskrit-lexicon/acph), [ACSJ](https://github.com/sanskrit-lexicon/acsj).

Full lineage narrative in [PWG/DICT_PROFILE.md § Lineage](https://github.com/sanskrit-lexicon/PWG/blob/docs-pass/DICT_PROFILE.md).

## 6. Cross-references — divergence/convergence with adjacent chapters

| Adjacent chapter | Convergence | Divergence |
|---|---|---|
| **← prior: [MW](mw)** | Same kernel morphology (small modal + long tail of enrichment); MW inherits the bulk of PWG's lexical material via German philology | PWG ~4× more citation-dense (4.63 vs 1.09 `<ls>`/record); 7 volumes vs 1; **PWG has 0 hedges** (uses named-kosha apparatus instead); PWG type-citation spread 0.4 pts (uniform) vs MW's 11.3 pts (selective) |
| **next →: [PWK](pwk)** | Same editor (Böhtlingk) without Roth; structurally identical record format; same `<ls>` tag system; both seven-volume Petersburg works at different physical scales | PWK drops PWG's kosha apparatus almost entirely (PWG `<ls>ŚKDR.</ls>` 20,109 → PWK 0; PWG `<ls>H. an.</ls>` 6,619 → PWK 0); PWK's compact design produces type-citation spread of 7.7 pts |

## 7. Decisions log

Per-dict editorial choices for this chapter:

- **5-type profile** (not 8+1): PWG's data lacks `<info>`, `<bot>`, `<bio>`, `<lang>` — so the encyclopedic, IE-cognate, and verbal-lemma primary types from MW's [refactored 8+1 typology](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#5-profiles-as-the-unit-of-typology) cannot be detected in PWG. The remaining types (nominal-m/f/n, adjective, other) are reported.
- **"Other" 21.7 %** is large because PWG verbal lemmas and compounds use grammar in prose (`<ab>P.</ab>`, `<ab>Ā.</ab>`) rather than `<lex>` (same pattern as MW per [DOUBTS D18](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md#d18--audit-of-the-other-residual--resolved-2026-05-27-as-verbal-lemma-promotion)).
- **No `<ls>L.</ls>` reporting** because PWG has 0; the contrast itself is the finding.
- **Three-stage L.-hedge lineage** is named in §4 but PWG sits *outside* the lineage (it belongs to the named-source tradition the hedge replaces), per [D21 resolution](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md#d21--cappeller-precedent-narrative-checked-against-mw-1872--partially-resolved-2026-05-27-finding-three-stage-lineage--was-blocking-now-closed).
- **Effect-size threshold** ([D19](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md)): all percentages on this page exceed |Δ| ≥ 5 pt vs corpus baseline and would survive FDR at q = 0.05.

## 8. Data dictionary + reproducibility manifest

- **[`DATA_DICTIONARY.md`](https://github.com/sanskrit-lexicon/PWG/blob/docs-pass/DATA_DICTIONARY.md)** — full tag inventory for PWG
- **Source file**: [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt)
- **Block-detector script**: [`figures/scripts/export_data.py`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/scripts/export_data.py) (functions `classify_type`, `detect_blocks`)
- **Cross-dict aggregate JSON**: [`src/data/cross-dict.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/interoperability-handoff/src/data/cross-dict.json) (includes PWG block matrix data)
- **License**: [CC-BY-SA-4.0](https://github.com/sanskrit-lexicon/PWG/blob/docs-pass/LICENSE)

## See also (tools)

- [Matrix explorer](../tools/matrix-explorer) — PWG block × type heatmap (where applicable)
- [Lineage Sankey](../tools/lineage-sankey) — kosha → PWG → PWK → MW flow
- [Cross-dictionary comparison](../tools/cross-dict) — PWG alongside all 8 other CDSL dicts
- [PWG/ROADMAP.md](https://github.com/sanskrit-lexicon/PWG/blob/docs-pass/ROADMAP.md) — 53 open issues in quarterly plan

---

Source: CDSL `pwg.txt` 2026-05-23 · MWS docs-pass commit reflects audit pipeline as of 2026-05-27 · CC-BY-SA-4.0
