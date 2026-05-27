---
title: PWG — Boehtlingk-Roth Grosses PW (1855–1875)
---

# PWG — Petersburger Wörterbuch (Großes PW, 1855–1875)

The seven-volume German philological dictionary by [Otto von Böhtlingk](https://en.wikipedia.org/wiki/Otto_von_B%C3%B6htlingk) and [Rudolf Roth](https://en.wikipedia.org/wiki/Rudolf_Roth). **The most citation-dense of all CDSL dicts** — 4.63 `<ls>` citations per record, more than 4× MW's 1.089. MW's principal scholarly source: Monier-Williams used it throughout the 1899 revision.

**[Source: csl-orig v02/pwg/pwg.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt) · [PWG GitHub](https://github.com/sanskrit-lexicon/pwg)**

## At a glance

| | |
|---|---|
| Records | 123,366 |
| Volumes | 7 |
| Language | German |
| Year | 1855–1875 |
| Genre | Structured bilingual |
| Modal blocks/entry | 4 |
| Mean blocks/entry | 3.74 |
| `<ls>` citations total | 571,152 |
| `<ls>` citations/record | 4.63 |

## Block profile

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
    Plot.barX(bars, {y: "block", x: "pct", fill: "#33a02c"}),
    Plot.text(bars, {y: "block", x: "pct",
      text: d => d.pct >= 0.5 ? d.pct.toFixed(1)+"%" : "",
      dx: 4, textAnchor: "start", fontSize: 10}),
    Plot.ruleX([0])
  ]
}));
```

**Absent blocks:** `etym` (0.0%) — etymological notes are folded into the body text; `hedge` (0.0%) — PWG cites named koshas rather than an anonymous lexicographer marker; `xref` (0.0%) — cross-references are inline; `info` (0.5%) — a small CDSL digitisation trace.

## Per-type citation profile

From [`analysis/CROSS_DICT_PROFILES.md`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/CROSS_DICT_PROFILES.md).

| Type | N | cite% | etym% | mean blocks |
|---|---:|---:|---:|---:|
| noun-m | 35,665 | 98.7% | 0.0% | 3.99 |
| noun-f | 14,170 | 98.4% | 0.0% | 3.98 |
| noun-n | 15,082 | 98.4% | 0.0% | 3.98 |
| adj-mfn | 31,671 | 98.5% | 0.0% | 3.98 |
| other | 26,778 | 77.4% | 0.0% | 2.84 |

**Citation spread: 0.4 pts** — the flattest profile of any structured bilingual dict. Every gender-type is essentially identically cited (~98%). The `other` category (verbal and compound sub-entries) is lower (77.4%) because verbs appear as sub-entries rather than top-level cited articles. The `etym%` column is 0.0% throughout: etymological data is not in a separate block, it is integrated into body.

## Framework notes

The common-block framework applies to PWG with two adaptations:

1. **No `etym` block.** Etymological content is integrated into `body`. Block-count comparisons understate PWG's etymological depth relative to MW.
2. **No `hedge` block.** PWG's kosha citations (`H.` 17,337, `AK.` 14,473, `MED.` 13,055) are named and placed in the `cite` block — not hedged anonymously. The absence of an anonymous lexicographer-hedge is a genuine editorial policy difference from MW.

**Multi-volume effect:** 7 volumes allow a higher citation load per entry (4.63 vs 1.089) without sacrificing entry quality. Block-economy still holds — modal kernel is 4 blocks — but the `cite` block is far heavier than in any single-volume dict.

## Lineage position

PWG is MW's principal scholarly predecessor. See [DICT_PROFILE.md — Beyond PWG](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/DICT_PROFILE.md#beyond-pwg--what-mw-contributes) and [PAPER.md §3](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#3-lineage).

## See also

- [Cross-dictionary comparison](../tools/cross-dict)
- [Lineage Sankey](../tools/lineage-sankey)
- [Citation tracer](../tools/citation-tracer)

---

Source: CDSL pwg.txt 2026-05-24 · CC-BY-SA-4.0
