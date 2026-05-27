---
title: MW — Monier-Williams 1899
---

# MW — Monier-Williams Sanskrit–English Dictionary (1899)

The standard single-volume Sanskrit–English reference, edited by [Monier Monier-Williams](https://en.wikipedia.org/wiki/Monier_Monier-Williams) with contributions from [Ernst Leumann](https://en.wikipedia.org/wiki/Ernst_Leumann) and [Carl Cappeller](https://en.wikipedia.org/wiki/Carl_Cappeller). **The reference dictionary for this atlas** — all microanalytic constructs were developed on MW first.

**[Cologne web display](https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/web/index.php) · [Source: csl-orig v02/mw/mw.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt) · [MWS GitHub](https://github.com/sanskrit-lexicon/MWS)**

## At a glance

| | |
|---|---|
| Records | 286,561 |
| Volumes | 1 (single-volume) |
| Language | English |
| Year | 1899 (second edition; first: 1872) |
| Genre | Structured bilingual |
| Modal blocks/entry | 5 |
| Mean blocks/entry | 4.71 |
| `<ls>` citations total | 312,159 |
| `<ls>` citations/record | 1.089 |

## Block profile

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

**MW-specific blocks:** `L. hedge` (13.9%) and `info` (95.5%) are not present in any other CDSL dict at scale. The `L.` hedge marks lexicographer-only attestations; `info` is a CDSL digitisation trace, not a print feature. See [PAPER.md §4](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#4-the-hedge-construct) and [D2](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md#d2--the-lslls-mw-innovation-claim--under-checked--important).

## Per-type citation profile

From [`analysis/CROSS_DICT_PROFILES.md`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/CROSS_DICT_PROFILES.md).

| Type | N | cite% | etym% | mean blocks |
|---|---:|---:|---:|---:|
| noun-m | 63,685 | 82.1% | 4.5% | 3.94 |
| noun-f | 31,093 | 75.4% | 1.9% | 3.84 |
| noun-n | 33,327 | 74.5% | 4.0% | 3.84 |
| adj-mfn | 50,606 | 85.8% | 7.3% | 3.99 |
| indeclinable | 5,501 | 79.1% | 5.6% | 3.91 |
| other | 102,349 | 75.5% | 11.1% | 2.98 |

**Citation spread: 11.3 pts** — adj-mfn and noun-m are best-documented; noun-n lowest. Moderate differentiation, comparable to PWK (7.7 pts) but less than AP (15.2 pts). The `other` category (verbal forms, compounds, indeclinables with no `<lex>` tag) has lower mean blocks (2.98 vs ~3.9 for gender-types).

## Framework notes

MW is the framework's native dict: all 9 common blocks are active; the `L. hedge` and `info` blocks are MW-only features at scale. The full 18×14 block-by-article-type matrix is computed only for MW; for other dicts see [per-dict block-matrix extensions](../tools/matrix-explorer).

The [microanalysis paper (PAPER.md)](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md) develops five constructs on MW: **block**, **slot**, **profile**, **hedge**, **infrastructure** — and the **block-economy** thesis (single-volume dicts converge on a small modal kernel). The cross-dict comparison tests whether these constructs generalize.

## Lineage position

MW occupies the **synthesis node** in the CDSL lineage: it inherits from [WIL (1832)](wil) via the kosha tradition and from [PWG (1855–75)](pwg) via the German philological apparatus. See [PAPER.md §3](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#3-lineage) and [DICT_PROFILE.md — Lineage](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/DICT_PROFILE.md#lineage-wil--koshas-mw--pwg).

## See also

- [Cross-dictionary comparison](../tools/cross-dict) — all 9 dicts together
- [Matrix explorer](../tools/matrix-explorer) — MW block×type matrix
- [Lineage Sankey](../tools/lineage-sankey) — WIL → kosha → MW → PWG flow
- [MWS docs-pass ROADMAP](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/ROADMAP.md)
- [DICT_PROFILE.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/DICT_PROFILE.md) — full reader-facing profile

---

Source: CDSL mw.txt 2026-05-24 · CC-BY-SA-4.0
