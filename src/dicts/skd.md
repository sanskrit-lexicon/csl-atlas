---
title: SKD — Śabdakalpadrumaḥ (Sanskrit–Sanskrit)
---

# SKD — *Śabdakalpadrumaḥ* (1822–1858)

The Sanskrit-Sanskrit encyclopedic dictionary compiled by Rādhākāntadeva. 42,531 entries in Sanskrit with Sanskrit definitions — the first major Sanskrit-Sanskrit lexicon in CDSL by record count. Structurally distinct from the structured bilingual dicts: no `<lex>` (gender tags), no `<ls>` (source citations). Gender is marked inline in Sanskrit; sources cited via inline *iti* quotation.

**[Source: csl-orig v02/skd/skd.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/skd/skd.txt) · [SKD GitHub](https://github.com/sanskrit-lexicon/skd)**

## At a glance

| | |
|---|---|
| Records | 42,531 |
| Volumes | 1 |
| Language | Sanskrit (definitions in Sanskrit) |
| Year | 1822–1858 |
| Genre | Sanskrit–Sanskrit lexicon |
| Modal blocks/entry | 2 |
| Mean blocks/entry | 1.99 |
| `<ls>` citations total | 0 |
| `<ls>` citations/record | 0.000 |
| Inline *iti* quotations | 72,176 |
| Inline *iti*/record | 1.70 |

## Block profile

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
    Plot.barX(bars, {y: "block", x: "pct", fill: "#999999"}),
    Plot.text(bars, {y: "block", x: "pct",
      text: d => d.pct >= 0.5 ? d.pct.toFixed(1)+"%" : "",
      dx: 4, textAnchor: "start", fontSize: 10}),
    Plot.ruleX([0])
  ]
}));
```

Only two blocks register: `head` (100%) and `body` (99.2%). All other blocks — gram, cite, hom, etym, xref, hedge, info — are 0.0%. This is not a sparse dict: the markup scheme for structured bilingual dicts simply does not apply to this genre.

## Framework notes

**The block apparatus does not transfer to SKD.** From [`analysis/CROSS_DICT_PROFILES.md`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/CROSS_DICT_PROFILES.md) Part B:

> SKD carries no `<lex>`/`<ls>`; it marks gender inline in Sanskrit and cites via inline `iti <source>` quotation. The block-profile apparatus — designed for structured bilingual dicts — is **genre-bound** and does not model the Sanskrit-Sanskrit kośa-lexica.

SKD's 72,176 inline *iti* quotations (1.70 per record) show it is citation-rich — but through a prose inline convention, not through a structured `<ls>` tag. A genre-appropriate analysis would need to parse the *iti* quotation stream rather than apply the common-block vocabulary.

## Why SKD is in the atlas

1. **Historical scope.** SKD (1822–1858) is contemporary with [WIL](wil) (1832) and overlaps with [PWG](pwg) (1855–1875). The lexicographic timeline is incomplete without it.
2. **Contrast case.** The near-empty block profile for SKD/[VCP](vcp) is part of the cross-dict argument: block-economy is a property of *structured bilingual* dicts, not of Sanskrit lexicography in general.
3. **Indirect source.** SKD's sense-divisions are a downstream source for [WIL](wil) and thus for [MW](mw), via the Fort William College pandits.

## See also

- [Cross-dictionary comparison](../tools/cross-dict) — SKD shown in grey as Sanskrit genre
- [VCP chapter](vcp) — the second major Sanskrit-Sanskrit lexicon in CDSL (encyclopedic)
- [Lineage Sankey](../tools/lineage-sankey)

---

Source: CDSL skd.txt 2026-05-24 · CC-BY-SA-4.0
