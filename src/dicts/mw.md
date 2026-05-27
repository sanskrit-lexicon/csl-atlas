---
title: MW — Monier-Williams 1899
---

# MW — Monier-Williams *Sanskrit-English Dictionary* (1899)

*Chapter authored per [Decision 29 Tier A](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#decision-29--phase-4-dictionary-ordering-chapter-templates-minimum-data-added-2026-05-27). Position 1 in the atlas ordering — the framework's home dictionary.*

## 1. Overview

The standard single-volume Sanskrit–English reference, edited by [Monier Monier-Williams](https://en.wikipedia.org/wiki/Monier_Monier-Williams) (Boden Professor of Sanskrit at Oxford 1860–88) with contributions from [Ernst Leumann](https://en.wikipedia.org/wiki/Ernst_Leumann) and [Carl Cappeller](https://en.wikipedia.org/wiki/Carl_Cappeller). Published 1899 (Clarendon Press, Oxford) as a substantial revision of the 1872 first edition. 286,561 records in the CDSL digital edition (compared to ~180,000 entries in PWG, the proximate German predecessor; ~44,000 in [WIL 1832](wil)). Single-volume format, ~1,333 pages, alphabetical macrostructure. MW is the **reference dictionary for this atlas** — all microanalytic constructs (block, slot, profile, hedge, infrastructure) were developed on MW first; the other 8 chapters test how far each construct generalises.

| | |
|---|---|
| **Records** | 286,561 |
| **Volumes** | 1 (single-volume) |
| **Year** | 1899 (2nd edn; 1st edn 1872) |
| **Editor(s)** | Monier-Williams; with Leumann + Cappeller (2nd edn) |
| **Source language** | Sanskrit (SLP1-encoded in `mw.txt`) |
| **Target language** | English |
| **Genre** | Structured bilingual scholarly dictionary |
| **Modal blocks/entry** | 6 (digital edition; 5 in print, sans F17 `<info>`) |
| **`<ls>` citations total** | 311,932 |
| **`<ls>` citations/record** | 1.09 |
| **License** | CC-BY-SA-4.0 |
| **Repo** | [sanskrit-lexicon/MWS](https://github.com/sanskrit-lexicon/MWS) |
| **Source file** | [`csl-orig/v02/mw/mw.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt) (48.9 MB) |
| **CDSL display** | [sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020](https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/web/index.php) |

## 2. Profile table (8+1 primary types × 18 blocks)

The full 8+1 primary-type profile for MW (per the refactored typology in [PAPER.md §5](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#5-profiles-as-the-unit-of-typology)):

| Primary type | Count | % corpus | Avg blocks | % lex-hedged | % Vedic-acc. |
|---|--:|--:|--:|--:|--:|
| Root | 750 | 0.26% | **9.73** | 7% | 8% |
| Nominal (m/f/n) | ≈ 37,700 | ≈ 13.2% | 6.05–6.43 | 12–21% | 18–24% |
| Adjective | 12,240 | 4.27% | 6.25 | 4% | 11% |
| Indeclinable | 1,929 | 0.67% | 6.39 | 2% | 9% |
| Compound sub-entry | 126,360 | **44.10%** | 6.02 | 13% | 14% |
| Derived form | 72,119 | 25.17% | 5.73 | 16% | 19% |
| Continuation sub-entry | 9,294 | 3.24% | 4.76 | 21% | 12% |
| Encyclopedic — botanical | 8,059 | 2.81% | 7.28 | **72%** | 6% |
| Encyclopedic — biographical | 346 | 0.12% | 7.58 | **65%** | 16% |
| Verbal lemma (9th type, added 2026-05-27 per [D18 audit](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md#d18--audit-of-the-other-residual--resolved-2026-05-27-as-verbal-lemma-promotion)) | 7,502 | 2.77% | — | — | — |

Reading: compounds and derived forms together = 69 % of the corpus and define MW's surface; roots are 0.26 % of entries but receive 9.7 blocks of editorial apparatus (the most elaborate profile); encyclopedic entries are 65–72 % lex-hedged (kosha-only).

Block-presence by name (cross-dict-common subset):

```js
const cross = FileAttachment("../data/cross-dict.json").json();
```

```js
const d = cross.dicts.find(d => d.code === "MW");
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

**1.09 `<ls>` per record** (311,932 citations across 286,561 records) — **lowest density of any structured bilingual CDSL dict** ([cross-dict audit](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/CROSS_DICT.md)), and ~4× sparser than PWG (4.63 per record). The sparseness is a single-volume print-economic constraint, *not* a sign of poor coverage.

Top 12 `<ls>` sigla:

| Tag | Source | Count |
|---|---|--:|
| `<ls>L.</ls>` | Generic lexicographer hedge (see §4) | **40,212** |
| `<ls>MBh.</ls>` | *Mahābhārata* | 22,990 |
| `<ls>ib.</ls>` | *ibidem* (editorial back-reference) | 10,094 |
| `<ls>RV.</ls>` | *Ṛgveda* | 9,707 |
| `<ls>R.</ls>` | *Rāmāyaṇa* (Vālmīki) | 9,049 |
| `<ls>W.</ls>` | Wilson 1832 (editorial back-cite) | 8,285 |
| `<ls>BhP.</ls>` | *Bhāgavata-purāṇa* | 6,979 |
| `<ls>Kathās.</ls>` | *Kathāsaritsāgara* | 5,926 |
| `<ls>MW.</ls>` | MW's own earlier editorial entry | 5,710 |
| `<ls>Suśr.</ls>` | *Suśrutasaṃhitā* | 5,690 |
| `<ls>ŚBr.</ls>` | *Śatapatha-brāhmaṇa* | 5,493 |
| `<ls>Cat.</ls>` | *Catalogues* (kosha back-cite) | 5,302 |

The **40,212 `<ls>L.</ls>` hedges** (12.9 % of all citations) are the single largest tag and the structural-distinguishing feature of MW within CDSL — see §4. After the hedge, the apparatus is concentrated on three corpora: Sanskrit epics (MBh., R., 32k), Vedic-corpus (RV., ŚBr., ~15k), and editorial-internal back-references (ib., W., MW., Cat., ~29k). Locator coordinates appear in 15.1 % of `<ls>` tags; the rest are bare work-citations.

## 4. Hedge analysis — the `<ls>L.</ls>` construct

The hedge is the entry-level evidentiary marker absent from PWG, PWK, WIL, BEN, CAE, SKD, VCP, and present 1× in AP. In MW it appears 40,212 times across primary types:

| Primary type | % entries lex-hedged |
|---|--:|
| Encyclopedic — botanical | **71.5 %** |
| Encyclopedic — biographical | **64.7 %** |
| Continuation sub-entry | 21.1 % |
| Derived form | 16.2 % |
| Compound sub-entry | 13.1 % |
| Nominal (m / f / n) | 18.9 / 20.8 / 12.2 % |
| Adjective | 4.4 % |
| Indeclinable | 2.2 % |
| Root | 7.2 % |

72 % of botanical entries and 65 % of biographical entries carry the hedge — *MW's botanical and onomastic identifications are predominantly kosha-only*, a structural fact about the dictionary that the original MW prefaces do not advertise.

**Three-stage lineage** (per the [2026-05-27 print-preface read](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md#mw-1872-preface-and-body-check-added-2026-05-27-d21-resolution)):

| Year | Source | What | Scale |
|--:|---|---|--:|
| 1866 | Benfey | `†` for "no authoritative references" (weaker, methodological) | ~900 |
| 1872 | **MW 1st edn** | Declares L.-convention in Section II of own preface | preface only; ≈ 0 in body |
| 1891 | Cappeller | `*` for "word taught only by grammarians or lexicographers" (first systematic typographic) | 1,370 |
| 1899 | **MW 2nd edn** (w/ Cappeller as co-editor) | `<ls>L.</ls>` (first systematic *tagged*) | **40,212** |

None of the three stages is fully derivative; each adds something. The 40,212 hedges are *the* high-leverage editorial target — resolving any of them to a named kosha ([ARMH](https://github.com/sanskrit-lexicon/armh), [ABCH](https://github.com/sanskrit-lexicon/abch), [ACPH](https://github.com/sanskrit-lexicon/acph), [ACSJ](https://github.com/sanskrit-lexicon/acsj)) lifts citation coverage and tightens evidence.

## 5. Lineage statement

MW occupies the **synthesis position** in the European Sanskrit-lexicography lineage: it draws on [WIL 1832](wil) via the indigenous-kosha tradition (Wilson's base was the Calcutta College's Amarakośa-derived word-list); on [PWG 1855–75](pwg) via the German philological apparatus and the bulk of the lexical material; and on Cappeller 1891 via the systematic typographic discipline that made the 40,212-instance `<ls>L.</ls>` apparatus possible. MW's successors are mostly indirect: [AP 1957](ap) (Apte) explicitly leans on MW for its primary lemma list and adds its own editorial layer; modern Sanskrit-English dictionaries derived from CDSL reuse MW data wholesale.

Full lineage narrative in [DICT_PROFILE.md § Lineage](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/DICT_PROFILE.md#lineage-wil--koshas-mw--pwg).

## 6. Cross-references — divergence/convergence with adjacent chapters

| Adjacent chapter | Convergence | Divergence |
|---|---|---|
| **← prior:** (none — MW is position 1) | — | MW is the framework's home; cross-dict facts emerge in chapters 2–9 |
| **next →: [PWG](pwg)** | Same kernel morphology (small modal + long tail); PWG is the immediate source of much MW lexical material | PWG is **~4× more citation-dense** (4.63 vs 1.09 `<ls>`/record); multi-volume vs single-volume; PWG has 0 hedges (uses named-kosha apparatus instead); PWG type-citation spread 0.4 pts vs MW's 11.3 pts |

## 7. Decisions log

Per-dict editorial choices documented in this chapter:

- **Use the refactored 8+1 primary-type table** (verbal lemma promoted from "other" 2026-05-27 per [DOUBTS D18 audit](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md#d18--audit-of-the-other-residual--resolved-2026-05-27-as-verbal-lemma-promotion)).
- **Report modal-6 (digital) kernel** as headline; print kernel is 5 (without F17), noted in [PAPER §4](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#4-the-block-economy-thesis) per [D17 resolution](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md).
- **Hedge lineage rendered as three-stage** (1872 concept → 1891 Cappeller systematic typographic → 1899 MW tagged), per [D21 resolution](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md#d21--cappeller-precedent-narrative-checked-against-mw-1872--partially-resolved-2026-05-27-finding-three-stage-lineage--was-blocking-now-closed).
- **Effect-size threshold for headline claims**: |pt-diff| ≥ 5 AND FDR-significant (per [D19 resolution](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md)). All percentages on this page exceed both thresholds.

## 8. Data dictionary + reproducibility manifest

- **[`DATA_DICTIONARY.md`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/DATA_DICTIONARY.md)** — full tag inventory, encoding policy, generation pipeline
- **Source file**: [`csl-orig/v02/mw/mw.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt) (commit at fetch time 2026-05-23)
- **Block-detector script**: [`figures/scripts/export_data.py`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/scripts/export_data.py) (functions `classify_type`, `detect_blocks`)
- **Per-dict matrix JSON**: [`data/mw_blocks.json`](../data/mw_blocks.json) (regenerable via `export_dict_blocks.py`)
- **Cross-dict JSON**: [`data/cross-dict.json`](../data/cross-dict.json) (renders all 9 atlas chapters)
- **License**: [CC-BY-SA-4.0](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/LICENSE) (data); CC-BY-SA-4.0 (this chapter)

## See also (tools)

- [Matrix explorer](../tools/matrix-explorer) — full 18×8 block × primary-type heatmap
- [Lineage Sankey](../tools/lineage-sankey) — kosha → WIL → MW → PWG flow
- [Cross-dictionary comparison](../tools/cross-dict) — MW alongside all 8 other CDSL dicts
- [MWS docs-pass ROADMAP](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/ROADMAP.md)

---

Source: CDSL `mw.txt` 2026-05-23 · MWS docs-pass commit reflects audit pipeline as of 2026-05-27 · CC-BY-SA-4.0
