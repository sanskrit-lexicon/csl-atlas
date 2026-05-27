---
title: VCP — Vācaspatyam (Sanskrit–Sanskrit)
---

# VCP — *Vācaspatyam* (1873–1884)

The encyclopedic Sanskrit-Sanskrit dictionary compiled by [Tārānātha Tarkavācaspati](https://en.wikipedia.org/wiki/Taranatha_Tarkavachaspati). 50,135 records — the **largest Sanskrit-Sanskrit lexicon in CDSL** by record count. Contemporary with [PWG](pwg) (1855–1875); Tārānātha worked without using it. Where [SKD](skd) is concise and lexicographic, VCP is **encyclopedic**: entries quote Manu-Smṛti, the Bhagavad-Gītā, the Yajurveda, Pāṇini sūtras, astronomical texts, and Vedānta commentary. Mean entry length ~494 characters.

**[Source: csl-orig v02/vcp/vcp.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/vcp/vcp.txt) · [VCP GitHub](https://github.com/sanskrit-lexicon/vcp)**

## At a glance

| | |
|---|---|
| Records | 50,135 |
| Volumes | 1 |
| Language | Sanskrit (definitions in Sanskrit) |
| Year | 1873–1884 |
| Genre | Sanskrit–Sanskrit encyclopedic lexicon |
| Modal blocks/entry | 2 |
| Mean blocks/entry | 1.96 |
| `<ls>` citations total | 0 |
| `<ls>` citations/record | 0.000 |
| Inline *iti* quotations | 13,110 |
| Inline *iti*/record | 0.26 |

## Block profile

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
    Plot.barX(bars, {y: "block", x: "pct", fill: "#999999"}),
    Plot.text(bars, {y: "block", x: "pct",
      text: d => d.pct >= 0.5 ? d.pct.toFixed(1)+"%" : "",
      dx: 4, textAnchor: "start", fontSize: 10}),
    Plot.ruleX([0])
  ]
}));
```

Only `head` (100%) and `body` (96.5%) register. VCP's `body` is slightly lower than [SKD](skd)'s 99.2%, reflecting entries that are purely headword. All other blocks = 0.0% for the same genre-bound reason as SKD.

## Framework notes

**The block apparatus does not transfer to VCP.** From [`analysis/CROSS_DICT_PROFILES.md`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/CROSS_DICT_PROFILES.md) Part B:

> SKD/VCP carry no `<lex>`/`<ls>`; they mark gender inline and cite via inline `iti <source>`. The block-profile apparatus is **genre-bound**.

The 13,110 inline *iti* quotations (0.26/record) are lower than [SKD](skd) (1.70/record) despite VCP's encyclopedic character — VCP cites long verbatim passages (Gītā verses, Pāṇini sūtras) rather than brief *iti*-style attributions. Entries are long (mean 494 characters) because of extended Sanskrit prose definitions, not citation density.

## Significance

VCP demonstrates that the **indigenous Sanskrit-Sanskrit lexicographic tradition continued in parallel with the European philological project**. Tārānātha compiled VCP (1873–1884) simultaneously with [PWG](pwg) (1855–1875) — both spanning the same two decades — without the two projects influencing each other. This parallel development is the strongest evidence that the two lexicographic traditions (Sanskrit kośa vs European philological bilingual) are structurally independent.

## See also

- [Cross-dictionary comparison](../tools/cross-dict)
- [SKD chapter](skd) — the earlier Sanskrit-Sanskrit lexicon; concise vs VCP's encyclopedic scope
- [Lineage Sankey](../tools/lineage-sankey)

---

Source: CDSL vcp.txt 2026-05-24 · CC-BY-SA-4.0
