---
title: AP — Apte Practical Sanskrit-English Dictionary (1890 / 1957)
---

# AP — Apte *Practical Sanskrit-English Dictionary* (1890 / 1957 revised)

*Chapter authored per [Decision 29 Tier A](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#decision-29--phase-4-dictionary-ordering-chapter-templates-minimum-data-added-2026-05-27). Position 4 in the atlas ordering — the **modern successor** that shows how the 18-block apparatus reads on a 20th-century artefact.*

## 1. Overview

[Vaman Shivaram Apte](https://en.wikipedia.org/wiki/Vaman_Shivaram_Apte)'s *Practical Sanskrit-English Dictionary*, first published 1890, revised and enlarged 1957 (the edition digitised in CDSL). A single-volume work designed for active reading of classical Sanskrit literature, particularly the *kāvya* and *śāstra* corpora, with substantial coverage of the [Aṣṭādhyāyī](https://en.wikipedia.org/wiki/A%E1%B9%A3%E1%B9%AD%C4%81dhy%C4%81y%C4%AB) terminology. The most recent dictionary in the CDSL bilingual set and the only modern (post-1899) work in the atlas. AP's distinguishing structural feature is its **maximum type-citation differentiation** (spread 15.2 pts — the largest in CDSL): Apte chose to cite the literary apparatus heavily for adjectives and indeclinables and lightly for nouns, reflecting his pedagogical orientation toward reading rather than reference.

| | |
|---|---|
| **Records** | 90,654 |
| **Volumes** | 1 (single-volume) |
| **Year** | 1890 (1st edn); 1957 (revised, digitised) |
| **Editor** | Vaman Shivaram Apte (1890); P. K. Gode + C. G. Karve (1957 rev.) |
| **Publisher** | Prasad Prakashan, Poona (1957 revised) |
| **Source language** | Sanskrit |
| **Target language** | English |
| **Genre** | Structured bilingual practical-reading dictionary |
| **`<ls>` citations total** | 62,656 |
| **`<ls>` citations/record** | 0.69 |
| **`<ls>L.</ls>` hedges** | **1** (only AP and MW have any L. hedge in CDSL) |
| **License** | CC-BY-SA-4.0 |
| **Repo** | [sanskrit-lexicon/AP90](https://github.com/sanskrit-lexicon/AP90) (1890 base) and [AP](https://github.com/sanskrit-lexicon/AP) (1957 revised) |
| **Source file** | [`csl-orig/v02/ap90/ap90.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ap90/ap90.txt) |

## 2. Profile table

Per [PAPER.md §5](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#5-profiles-as-the-unit-of-typology), restricted to the types AP's data supports:

| Primary type | Count | % corpus | cite% | etym% | Mean common-blocks |
|---|--:|--:|--:|--:|--:|
| Nominal — noun_m | 2,646 | 2.9 % | 34.4 % | 0.0 % | 3.37 |
| Nominal — noun_f | 2,969 | 3.3 % | 41.2 % | 0.0 % | 3.44 |
| Nominal — noun_n | 882 | 1.0 % | 37.0 % | 0.0 % | 3.42 |
| Adjective | 18,764 | 20.7 % | 40.0 % | 0.0 % | 3.41 |
| Indeclinable | 1,552 | 1.7 % | **49.6 %** | 0.1 % | 3.53 |
| Other (compounds, verbs without `<lex>`) | 63,841 | 70.4 % | 28.1 % | 0.0 % | 2.15 |

**Citation profile spread: 15.2 pts** — the largest in CDSL. Apte cites indeclinables (sandhi particles, sentence connectives) most heavily (49.6 %), nouns less so (34–41 %), and the unmarked "other" residual (most of the corpus — verbal lemmas and compounds carry grammar in prose) least (28.1 %). The spread reflects **pedagogical purpose**: the indeclinables Apte cites are the connectives a student of Sanskrit literature must recognise; the nouns are mostly content-words where the gloss alone suffices.

Block-presence by name:

```js
const cross = FileAttachment("../data/cross-dict.json").json();
```

```js
const d = cross.dicts.find(d => d.code === "AP");
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

**0.69 `<ls>` per record** — between PWK (0.51) and MW (1.09). Top 12 sigla:

| Tag | Source | Count |
|---|---|--:|
| `<ls>Mb.</ls>` | *Mahābhārata* (Apte's siglum, distinct from MW's `<ls>MBh.</ls>`) | 485 |
| `<ls>L. D. B.</ls>` | *Lakṣmīdhara's Bhāvārtha-dīpikā* | 393 |
| `<ls>Sk.</ls>` | *Siddhānta-kaumudī* | 391 |
| `<ls>Rām.</ls>` | *Rāmāyaṇa* | 382 |
| `<ls>Tv.</ls>` | *Tantra-vārtika* | 304 |
| `<ls>Subhāṣ.</ls>` | *Subhāṣita* anthology | 268 |
| `<ls>Pt. 1</ls>` | *Pañcatantra* book 1 | 251 |
| `<ls>Ś. 1</ls>` | *Abhijñāna-Śākuntalam* act 1 | 230 |
| `<ls>Nm.</ls>` | Nirṇaya-sāgara editions | 221 |
| `<ls>Mbh.</ls>` | *Mahābhāṣya* (Patañjali — distinct from `<ls>Mb.</ls>`) | 207 |
| `<ls>Ak.</ls>` | *Amarakośa* | 177 |
| `<ls>Suśr.</ls>` | *Suśrutasaṃhitā* | 171 |

**Sigla profile**: mixed scholarly (Mb., Rām., Subhāṣ., Pt., Ś.) + Apte-specific abbreviations (L. D. B., Nm., Tv.) reflecting the 19th-century Indian editorial tradition the 1890 edition emerged from. The 1957 revision (digitised) added but did not replace the 1890 apparatus.

## 4. Hedge analysis — AP has exactly one `<ls>L.</ls>`

**AP carries exactly 1 generic `<ls>L.</ls>` hedge** ([analysis/LS_HEDGE_CHECK.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md)) — making it the **only** CDSL dictionary other than MW that uses the hedge at all. The single occurrence is anomalous (probably an editorial inheritance from a source that MW had hedged) and does not reflect a systematic Apte design — AP's editorial discipline is to **name the source** wherever possible. This single hedge instance is consistent with AP being a *post-MW* work that inherited some MW conventions selectively.

The 1957 revision predates the wide use of MW's tagged form by digital-edition standards, so the hedge does not propagate further: of the 8 other CDSL bilingual + Sanskrit-Sanskrit dictionaries, only MW (40,212×) and AP (1×) carry any L. instances.

## 5. Lineage statement

AP occupies the **modern-successor position** in the CDSL European-Sanskrit-lexicography lineage. Apte (1858–1892) was educated at Deccan College, Pune, in the late-19th-century Indian indological tradition that incorporated PWG + MW alongside indigenous-kosha scholarship. The 1890 dictionary draws on PWG (cited as `<ls>BR.</ls>` or `<ls>PW.</ls>` in some entries) and MW 1872 (cited as `<ls>MW.</ls>`); the 1957 revision adds material from the 20th-century editions of Mahābhārata and Rāmāyaṇa critical editions. AP's distinguishing methodological move is **pedagogical re-organisation**: where MW is alphabetical by Sanskrit headword, AP groups syntactically and provides example-rich glosses aimed at the *student of Sanskrit literature*, not the comparative philologist. AP has no direct successor in CDSL but is the *de facto* English-Sanskrit reference for active reading in the 20th and 21st centuries.

Full lineage in [AP/DICT_PROFILE.md](https://github.com/sanskrit-lexicon/AP90/blob/docs-pass/DICT_PROFILE.md).

## 6. Cross-references — divergence/convergence with adjacent chapters

| Adjacent chapter | Convergence | Divergence |
|---|---|---|
| **← prior: [PWK](pwk)** | Both single-volume; both moderate `<ls>` density (PWK 0.51, AP 0.69) | AP is 20th-century English practical; PWK is 19th-century German scholarly; AP has 1× `<ls>L.</ls>` (post-MW inheritance), PWK has 0; AP type-citation spread 15.2 pts (most selective) vs PWK 7.7 pts |
| **next →: [BEN](ben)** | Both compact single-volume reference works | AP is 20th-century practical (1957); BEN is 19th-century philological (1866); AP has `<lex>` tagging, BEN does not; AP has 1× `<ls>L.</ls>`, BEN has 0 |

## 7. Decisions log

- **5-type profile** (PWG-like) per same reason: AP lacks `<info>`, `<bot>`, `<bio>`, `<lang>` so encyclopedic / IE / verbal-lemma primary types from MW's [refactored typology](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#5-profiles-as-the-unit-of-typology) cannot be detected.
- **The single `<ls>L.</ls>` instance** is documented as an anomaly (post-MW inheritance) rather than a systematic Apte convention.
- **15.2-pt spread** is the highest in CDSL — surfaced as a *pedagogical* feature (indeclinables most-cited, content-nouns least-cited).
- **Effect-size threshold** ([D19](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md)): all numerical claims on this page exceed |Δ| ≥ 5 pt threshold.

## 8. Data dictionary + reproducibility manifest

- **[`DATA_DICTIONARY.md`](https://github.com/sanskrit-lexicon/AP90/blob/docs-pass/DATA_DICTIONARY.md)** — full tag inventory
- **Source file**: [`csl-orig/v02/ap90/ap90.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ap90/ap90.txt)
- **Block-detector script**: [`figures/scripts/export_data.py`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/scripts/export_data.py)
- **Per-dict matrix JSON**: [`data/ap_blocks.json`](../data/ap_blocks.json) (note: `csl_code='ap90'` but filename is `ap_blocks.json` — Round 1 S6 bug fix)
- **Cross-dict aggregate**: [`data/cross-dict.json`](../data/cross-dict.json)
- **License**: [CC-BY-SA-4.0](https://github.com/sanskrit-lexicon/AP90/blob/master/LICENSE)

## See also (tools)

- [Cross-dictionary comparison](../tools/cross-dict)
- [AP90#31 — docs-pass tracking issue](https://github.com/sanskrit-lexicon/AP90/issues/31)

---

Source: CDSL `ap90.txt` 2026-05-23 · MWS docs-pass commit reflects audit pipeline as of 2026-05-27 · CC-BY-SA-4.0
