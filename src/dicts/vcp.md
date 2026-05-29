---
title: VCP — Vācaspatyam (1873–1884)
---

# VCP — *Vācaspatyam* (1873–1884)

*Chapter authored per [Decision 29 Tier C](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#decision-29--phase-4-dictionary-ordering-chapter-templates-minimum-data-added-2026-05-27). Position 9 in the original atlas chapter ordering — the **second Sanskrit-Sanskrit lexicon** and the framework's outer limit for the structured-bilingual block model.*

## 1. Overview

[*Vācaspatyam*](https://en.wikipedia.org/wiki/Vachaspatya) ("the work of Vācaspati", named after the editor's epithet), an encyclopedic Sanskrit-Sanskrit dictionary compiled by **Tārānātha Tarkavācaspati**, published Calcutta 1873–1884 in seven volumes. VCP is the **second indigenous-Indian large-scale Sanskrit-Sanskrit lexicon** in CDSL, contemporary with PWG's later volumes and PWK's beginning, and one of the major CDSL Sanskrit-Sanskrit works (50,135 records). VCP is structurally similar to [SKD](skd) — encyclopedic, monolingual, prose-paragraph entries with inline `iti` citation — but with a *much sparser* inline citation density (0.26 *iti* / record vs SKD's 1.70). In the nine-chapter atlas path, VCP confirms the genre boundary discovered at SKD; the all-dictionary coverage layer extends beyond this chapter path by measuring partial framework fit across every available CDSL v02 dictionary.

| | |
|---|---|
| **Records** | **50,135** (largest in CDSL by raw record count) |
| **Volumes** | 7 |
| **Year** | 1873–1884 |
| **Editor** | Tārānātha Tarkavācaspati |
| **Publisher** | Various Calcutta presses |
| **Source language** | Sanskrit |
| **Target language** | **Sanskrit** (monolingual, encyclopedic) |
| **Genre** | **Sanskrit-Sanskrit encyclopedic *kośa*** (genre-bound) |
| **`<lex>` tagged grammar** | 0 |
| **`<ls>` tagged source citations** | **0** |
| **Inline `iti` citations / record** | **0.26** (much sparser than SKD's 1.70) |
| **Mean entry length** | 494 characters |
| **License** | CC-BY-SA-4.0 |
| **Repo** | [sanskrit-lexicon/VCP](https://github.com/sanskrit-lexicon/VCP) |
| **Source file** | [`csl-orig/v02/vcp/vcp.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/vcp/vcp.txt) |

## 2. Genre-bound (the framework does not apply — second confirmation)

VCP confirms the genre boundary that SKD established. The same three preconditions fail in VCP as in SKD:

1. **No `<lex>` tags.** Gender + grammatical category encoded inline in Sanskrit.
2. **No `<ls>` tags.** Sources cited via inline `iti <source>` prose.
3. **Long encyclopedic prose entries.** Mean 494 characters per entry.

The 18-block detector produces the same degenerate output as for SKD: every block-presence column at or near zero, no meaningful profile differentiation.

Block-presence by name:

```js
const cross = FileAttachment("../data/cross-dict.json").json();
```

```js
const d = cross.dicts.find(d => d.code === "VCP");
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

## 3. Prose-pattern analysis — sparser *iti* than SKD

VCP's inline-`iti` citation density is **0.26 per record** — about a sixth of SKD's 1.70. The same *iti*-formula apparatus is operative (sources named in prose as "*… iti <SOURCE>*"), but VCP's editorial choice was to *quote more sparingly*. Where SKD entries typically include 1–2 quoted prior-kośa passages, VCP entries are often **encyclopedic prose without quotation** — Tārānātha's own synthesis, with named-source attribution reserved for direct quotations. This is a *different editorial philosophy* within the same genre:

| | SKD | VCP |
|---|--:|--:|
| Records | 42,531 | 50,135 |
| Volumes | 7 | 7 |
| Inline `iti` total | 72,176 | 13,110 |
| Inline `iti` / record | **1.70** | **0.26** |
| Mean entry length | 532 chars | 494 chars |

SKD is the **quotation-rich** kośa (the prior tradition speaks through the entries); VCP is the **synthesis-rich** kośa (the editor speaks, citing only where direct quotation matters). Both are valid genre-internal variants — neither maps to the European-bilingual structured-block framework.

## 4. Why the framework changes here — boundary, not endpoint

This chapter makes the framework's scope explicit. The 18-block apparatus developed for MW in [PAPER.md §3](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#3-the-five-grounded-constructs) was designed to analyse structured bilingual dictionaries — works where every source citation occupies a discrete tagged slot and every entry decomposes into a kernel + enrichment block-economy. SKD and VCP do not have this structure; they are *encyclopedic Sanskrit-Sanskrit kośa* works whose source-discipline lives in prose. The 18-block detector applied to them returns a degenerate "everything is zero" reading — not because the dictionaries are deficient, but because they are *a different kind of artefact*.

[PAPER.md §8](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#8-implications-for-future-cdsl-work) names this explicitly:

> "*The block apparatus is therefore genre-bound to structured bilingual dictionaries — a useful limit on the framework's scope.*"

And [PAPER.md §10](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#10-conclusion) further:

> "*Sanskrit-Sanskrit lexica … require a different microstructural framework, oriented to inline-iti citation rather than tagged sources.*"

The original chapter sequence therefore reaches a boundary at VCP, but the atlas itself should not stop there. The next layer is an all-dictionary coverage and size inventory: first measure which blocks partially transfer to every CDSL v02 dictionary, then design a companion microanalysis for inline-prose citation, with `iti` as its primary structural unit and paragraph-flow as its block unit. That extension would include SKD, VCP, and the indigenous-*kośa* tradition the four kosha repos ([ARMH](https://github.com/sanskrit-lexicon/armh), [ABCH](https://github.com/sanskrit-lexicon/abch), [ACPH](https://github.com/sanskrit-lexicon/acph), [ACSJ](https://github.com/sanskrit-lexicon/acsj)) represent.

## 5. Lineage statement

VCP occupies the **synthesis-rich position** in the indigenous Sanskrit *kośa* tradition. Tārānātha Tarkavācaspati (active 1855–1885) was a Calcutta-based Sanskrit grammarian and lexicographer; his *Vācaspatyam* draws on the same prior-*kośa* sources as SKD (Amarakośa, Hemacandra, Medinīkośa, Halāyudha) but with a *more synthetic* editorial voice — quoting less, explaining more. VCP is **contemporary with PWG's later volumes** (1873–1884 vs PWG's last volume 1875) but the two enterprises did not draw on each other: PWG cited prior indigenous *kośa* sources directly; VCP did not engage with the European tradition. The two run as parallel monuments of 19th-century Sanskrit-lexicography on opposite sides of the genre boundary.

The four kosha repos that resolve MW's `<ls>L.</ls>` hedge are *prior to* both SKD and VCP in the indigenous tradition; SKD and VCP synthesised them rather than introducing new material. The full lineage chain of the indigenous tradition lies *upstream* of this atlas.

## 6. Cross-references — divergence/convergence with adjacent chapters

| Adjacent chapter | Convergence | Divergence |
|---|---|---|
| **← prior: [SKD](skd)** | Both encyclopedic Sanskrit-Sanskrit *kośa*; both no `<lex>`/`<ls>` tags; both prose-paragraph entries; same genre, same editorial tradition | SKD inline `iti` density = **1.70**/record (quotation-rich prototype); VCP = **0.26** (synthesis-rich variant). SKD is the *prototype* of the genre, VCP is a *variant editorial philosophy* within it. Both confirm the genre boundary; together they delimit the structured-bilingual framework's outer limit |
| **next →: [All-dictionary coverage](../tools/dictionary-coverage)** | Moves from nine narrative chapters to every CDSL v02 dictionary with a main source file | The next question is not only block presence, but size: record counts, entry lengths, block character mass, and type distributions across partial fits |

## 7. Decisions log

- **Boundary chapter** in the original nine-dictionary path — cross-references now point onward to all-dictionary coverage rather than treating VCP as the atlas's last possible node.
- **Tier C template** per [Decision 29 §29.2](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#292--chapter-template-variants-three-tiers).
- **Two-monograph comparison with SKD** structures §3: SKD vs VCP shows two editorial philosophies *within* the genre-bound kośa tradition (quotation-rich vs synthesis-rich).
- **Explicit framework-limit statement** in §4 — the atlas's *purpose* in including SKD and VCP is to demarcate the framework's outer scope, not to extend the framework to cover them.
- **Phase-5 future work** flagged in §4 as the next research project (all-dictionary coverage first, then a different microstructural tool for inline-`iti` citation).
- **Effect-size threshold** ([D19](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md)): all numerical comparisons (SKD 1.70 vs VCP 0.26, both vs MW 0) are large effects.

## 8. Data dictionary + reproducibility manifest

- **`DATA_DICTIONARY.md`** — [VCP/DATA_DICTIONARY.md](https://github.com/sanskrit-lexicon/VCP/blob/docs-pass/DATA_DICTIONARY.md) (notes absence of `<lex>`/`<ls>`)
- **Source file**: [`csl-orig/v02/vcp/vcp.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/vcp/vcp.txt)
- **Block-detector script**: [`figures/scripts/export_data.py`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/scripts/export_data.py) (same degenerate output as SKD)
- **Cross-dict aggregate JSON**: [`src/data/cross-dict.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/interoperability-handoff/src/data/cross-dict.json) (includes VCP metadata; VCP does not use tagged `<ls>` citation blocks)
- **License**: [CC-BY-SA-4.0](https://github.com/sanskrit-lexicon/VCP/blob/master/LICENSE)

## See also (tools + epilogue)

- [Cross-dictionary comparison](../tools/cross-dict) — VCP shown alongside SKD and the structured bilingual dicts for the nine-chapter comparison
- [All-dictionary coverage](../tools/dictionary-coverage) — VCP shown inside the full CDSL v02 coverage and size inventory
- [VCP#31 — docs-pass tracking issue](https://github.com/sanskrit-lexicon/VCP/issues/31)
- **Boundary of the nine-chapter path.** Continue to the coverage tool for the full-dictionary inventory.

---

Source: CDSL `vcp.txt` 2026-05-23 · MWS docs-pass commit reflects audit pipeline as of 2026-05-28 · CC-BY-SA-4.0
