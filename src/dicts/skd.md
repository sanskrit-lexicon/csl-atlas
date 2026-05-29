---
title: SKD — Śabdakalpadrumaḥ (1822–1858)
---

# SKD — *Śabdakalpadrumaḥ* (1822–1858)

*Chapter authored per [Decision 29 Tier C](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#decision-29--phase-4-dictionary-ordering-chapter-templates-minimum-data-added-2026-05-27). Position 8 in the atlas ordering — the **first Sanskrit-Sanskrit lexicon**, where the 18-block framework stops applying.*

## 1. Overview

[*Śabdakalpadrumaḥ*](https://en.wikipedia.org/wiki/Shabdakalpadruma) ("the wishing-tree of words"), an encyclopedic Sanskrit-Sanskrit dictionary in seven volumes compiled by Rājā Rādhākānta Deva and his circle, published Calcutta 1822–1858. SKD is the **first indigenous-Indian large-scale lexicon** in the modern Sanskrit-philological tradition: encyclopedic in scope, monolingual in language (Sanskrit headword + Sanskrit definitions), and rich with citations from literary works and prior *kośa* sources via **inline `iti <source>` prose**. Within CDSL, SKD marks the **genre boundary** of the present framework: where MW, PWG, PWK, AP, BEN, CAE, WIL are *structured bilingual* dictionaries amenable to the 18-block detector, SKD and [VCP](vcp) are *encyclopedic Sanskrit-Sanskrit* works whose source-discipline lives in prose, not in tags. The block apparatus developed for MW does not apply.

| | |
|---|---|
| **Records** | 42,531 |
| **Volumes** | 7 (multi-volume Calcutta print) |
| **Year** | 1822–1858 |
| **Editor** | Rājā Rādhākānta Deva and circle |
| **Publisher** | Various Calcutta presses |
| **Source language** | Sanskrit |
| **Target language** | **Sanskrit** (monolingual, encyclopedic) |
| **Genre** | **Sanskrit-Sanskrit encyclopedic *kośa*** (genre-bound) |
| **`<lex>` tagged grammar** | 0 (gender marked inline in prose) |
| **`<ls>` tagged source citations** | **0** (citation via inline `iti <source>` prose) |
| **Inline `iti` citations / record** | **1.70** (the operative apparatus) |
| **Mean entry length** | 532 characters (~7× MW) |
| **License** | CC-BY-SA-4.0 |
| **Repo** | [sanskrit-lexicon/SKD](https://github.com/sanskrit-lexicon/SKD) |
| **Source file** | [`csl-orig/v02/skd/skd.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/skd/skd.txt) |

## 2. Why the structured-bilingual block framework does not apply

The 18-block apparatus developed for MW in [PAPER.md §3](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#3-the-five-grounded-constructs) is **genre-bound** to structured bilingual dictionaries. SKD violates the framework's three core preconditions:

1. **No `<lex>` grammatical category tag.** SKD marks gender, voice, declension class, etc. inline in Sanskrit prose ("*X iti puṁsi*" — "X is masculine", literally "X-thus-in-masculine"). The MW detector that searches for `<lex>m.</lex>` finds zero matches.
2. **No `<ls>` source citation tag.** SKD cites sources via the formula "*… iti <SOURCE>*" inline in the gloss prose. Inline `iti` appears 72,176 times across SKD's 42,531 records — **1.70 per record** (vs MW ≈ 0). This is the *operative* citation apparatus; the digitisation does not extract it as `<ls>` because the prose context does not survive tagging.
3. **Long encyclopedic prose entries.** Mean entry length is 532 characters in SKD (vs ~80 in MW). The "kernel + enrichment" block-economy that defines MW does not have a counterpart — SKD entries are *paragraphs of prose* with quotations woven through, not slot-and-block compositions.

The block apparatus is therefore **inapplicable** to SKD. Block-presence by name shows mostly empty:

```js
const cross = FileAttachment("../data/cross-dict.json").json();
```

```js
const d = cross.dicts.find(d => d.code === "SKD");
const LABEL = {head:"head",body:"body (¦)",gram:"gram (lex)",cite:"cite (ls)",hom:"homograph",etym:"etymology",xref:"cross-ref",hedge:"L. hedge",info:"info (digit.)"};
const bars = cross.blocks.map(b => ({block: LABEL[b] ?? b, pct: d.blocks_pct[b]}));
display(Plot.plot({
  width: 580, height: 240, marginLeft: 90,
  x: {label: "% of entries", domain: [0, 100], grid: true},
  y: {label: null},
  marks: [
    Plot.barX(bars, {y: "block", x: "pct", fill: "#984ea3"}),
    Plot.text(bars, {y: "block", x: "pct",
      text: d => d.pct >= 0.5 ? d.pct.toFixed(1)+"%" : "",
      dx: 4, textAnchor: "start", fontSize: 10}),
    Plot.ruleX([0])
  ]
}));
```

(The bars largely flatline at zero — this is the visual signature of the genre boundary.)

## 3. Prose-pattern analysis — the *iti* citation apparatus

SKD's source-discipline is **inline prose** rather than tagged. The pattern is the formula "*… iti <SOURCE>*" — literally "*thus says <SOURCE>*" — which marks the preceding quotation or paraphrase as drawn from the named work. From [analysis/CROSS_DICT_PROFILES.md Part B](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/CROSS_DICT_PROFILES.md):

| Metric | SKD | (vs MW for contrast) |
|---|--:|--:|
| Records | 42,531 | 286,561 |
| `<ls>` tags | 0 | 311,932 |
| Inline `iti` | **72,176** | ≈ 0 |
| `iti` per record | **1.70** | ≈ 0 |
| Mean entry length (chars) | 532 | ~80 |

A typical SKD entry quotes Manu, Amarakośa, *Bhagavad-Gītā*, *Yajurveda*, *Līlāvatī*, or a Pāṇinian *sūtra* by name in the prose. The reader who knows the *iti*-formula reads the source-attribution off the page; the digital detector that searches for `<ls>` does not.

## 4. How indigenous-kosha citation differs from European source-tagging

The European tradition (PWG, MW, etc.) treats every source citation as a *separable structural slot*: a `<ls>` tag occupies a fixed position in the entry, machine-distinguishable from the gloss it accompanies. The indigenous *kośa* tradition (SKD, VCP, and the prior Amarakośa / Medinīkośa / Hemacandra works SKD synthesises) treats every source citation as a *prose feature* of the gloss itself — the source is *part of what the gloss says*, not a tagged annotation about the gloss. This is not a technical limitation of the medium (SKD was printed in 7 large volumes with full typographic apparatus); it is a *design choice* rooted in the encyclopedic-kosha tradition's preference for woven, paragraph-length, citation-rich definitions over the European tradition's slot-and-block compactness.

The implication for the present framework: the 18-block apparatus is **not a universal microanalysis tool**. It is a tool calibrated to structured bilingual dictionaries — the 7 CDSL works that MW, PWG, PWK, AP, BEN, CAE, WIL belong to. SKD and VCP require a *different* microanalysis tool, one that takes inline-`iti` as its citation unit and paragraph-prose-flow as its block unit. This work is not done in the present atlas; it would be a separate paper / future Phase-5 project.

## 5. Lineage statement

SKD occupies the **encyclopedic-synthesis position** in the indigenous Sanskrit *kośa* tradition. It draws on the prior *kośa* literature (*[Amarakośa](https://en.wikipedia.org/wiki/Amarakosha)* 6th c., *[Medinīkośa](https://en.wikipedia.org/wiki/Medinikosha)* 14th c., *Hemacandra Anekārtha-saṃgraha* 12th c., *Trikāṇḍaśeṣa*, *Halāyudha*, *Śabdaratnāvalī*, *Vaijayantī*) and on the Sanskrit literary canon (Vedic, epic, Purāṇic, classical *kāvya*, dharma-śāstra). It is the **first encyclopedic work** of the modern Indian indological tradition — Rādhākānta Deva's circle was working under British-colonial patronage but the editorial choices are recognisably *kośa*-traditional. The four indigenous-kosha repos that resolve MW's `<ls>L.</ls>` hedge ([ARMH](https://github.com/sanskrit-lexicon/armh), [ABCH](https://github.com/sanskrit-lexicon/abch), [ACPH](https://github.com/sanskrit-lexicon/acph), [ACSJ](https://github.com/sanskrit-lexicon/acsj)) are the prior *kośa* works SKD itself synthesises; SKD therefore plays a dual role — encyclopedic *kośa* in its own right, and the *target* into which MW's hedges resolve.

PWG cites SKD as `<ls>ŚKDR.</ls>` 20,109 times — SKD's biggest impact on the European tradition was as PWG's primary indigenous-lexicon source.

## 6. Cross-references — divergence/convergence with adjacent chapters

| Adjacent chapter | Convergence | Divergence |
|---|---|---|
| **← prior: [WIL](wil)** | Both 19th-century Calcutta compilations rooted in indigenous-Indian scholarship | WIL is bilingual (Sanskrit → English); SKD is monolingual Sanskrit-Sanskrit; WIL is structured-bilingual genre, SKD is genre-bound encyclopedic; the **genre boundary** in the atlas falls here |
| **next →: [VCP](vcp)** | Both encyclopedic Sanskrit-Sanskrit; both no `<lex>`/`<ls>` tags; both prose-paragraph entries | SKD inline `iti` density = 1.70/record (the densest); VCP = 0.26/record (much sparser). SKD is the *prototype* of the genre, VCP is a *variant* — different editor (Tārānātha), different methodology, but same genre |

## 7. Decisions log

- **Tier C template** per [Decision 29 §29.2](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#292--chapter-template-variants-three-tiers). §§ 2–4 replaced with structural-features, prose-pattern, and "why framework does not transfer" sections.
- **The genre boundary is the chapter's central finding** — explicit linkage to [PAPER.md §8](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#8-implications-for-future-cdsl-work) (framework is genre-bound to structured bilingual dicts).
- **Dual role of SKD** (indigenous *kośa* + PWG citation source `<ls>ŚKDR.</ls>` 20,109×) surfaced in §5.
- **Effect-size threshold** ([D19](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md)): numerical claims (1.70 iti/record, 0/0/0 tags, 532-char mean length) exceed the threshold by orders of magnitude — these are not borderline findings.

## 8. Data dictionary + reproducibility manifest

- **[`DATA_DICTIONARY.md`](https://github.com/sanskrit-lexicon/SKD/blob/docs-pass/DATA_DICTIONARY.md)** — full tag inventory (notes the absence of `<lex>` / `<ls>`)
- **Source file**: [`csl-orig/v02/skd/skd.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/skd/skd.txt)
- **Block-detector script**: [`figures/scripts/export_data.py`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/scripts/export_data.py) (note: SKD output is the degenerate case — every column zero)
- **Cross-dict aggregate JSON**: [`src/data/cross-dict.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/interoperability-handoff/src/data/cross-dict.json) (includes SKD metadata; SKD does not use tagged `<ls>` citation blocks)
- **License**: [CC-BY-SA-4.0](https://github.com/sanskrit-lexicon/SKD/blob/master/LICENSE)

## See also (tools)

- [Cross-dictionary comparison](../tools/cross-dict) — SKD shown alongside structured bilingual dicts for contrast
- [SKD#20 — docs-pass tracking issue](https://github.com/sanskrit-lexicon/SKD/issues/20)
- [Kosha resolution repos](https://github.com/sanskrit-lexicon/armh): ARMH · [ABCH](https://github.com/sanskrit-lexicon/abch) · [ACPH](https://github.com/sanskrit-lexicon/acph) · [ACSJ](https://github.com/sanskrit-lexicon/acsj)

---

Source: CDSL `skd.txt` 2026-05-23 · MWS docs-pass commit reflects audit pipeline as of 2026-05-27 · CC-BY-SA-4.0
