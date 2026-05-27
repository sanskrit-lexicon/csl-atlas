---
title: WIL — Wilson Sanskrit–English Dictionary (1832)
---

# WIL — Wilson's Sanskrit–English Dictionary (1832)

The 1832 Sanskrit–English dictionary by [Horace Hayman Wilson](https://en.wikipedia.org/wiki/Horace_Hayman_Wilson), compiled at [Fort William College, Calcutta](https://en.wikipedia.org/wiki/Fort_William_College) with the aid of Indian pandits. **MW's direct English-language ancestor** — Monier-Williams used the 1832 WIL as the base for both editions (1872 and 1899), supplementing it with [PWG](pwg)'s philological apparatus. CDSL classifies WIL as a `koSa` (kosha), not a European philological dictionary — reflecting the Indian scholarly tradition that shaped it.

**[Source: csl-orig v02/wil/wil.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/wil/wil.txt) · [WIL GitHub](https://github.com/sanskrit-lexicon/wil)**

## At a glance

| | |
|---|---|
| Records | 44,577 |
| Volumes | 1 (single-volume) |
| Language | English |
| Year | 1832 |
| Genre | Structured bilingual (kosha-lineage) |
| Modal blocks/entry | 3 |
| Mean blocks/entry | 3.00 |
| `<ls>` citations total | 230 |
| `<ls>` citations/record | 0.005 |

## Block profile

```js
const cross = FileAttachment("../data/cross-dict.json").json();
```

```js
const d = cross.dicts.find(d => d.code === "WIL");
const LABEL = {head:"head",body:"body (¦)",gram:"gram (lex)",cite:"cite (ls)",hom:"homograph",etym:"etymology",xref:"cross-ref",hedge:"L. hedge",info:"info (digit.)"};
const bars = cross.blocks.map(b => ({block: LABEL[b] ?? b, pct: d.blocks_pct[b]}));
display(Plot.plot({
  width: 580, height: 240, marginLeft: 90,
  x: {label: "% of entries", domain: [0, 100], grid: true},
  y: {label: null},
  marks: [
    Plot.barX(bars, {y: "block", x: "pct", fill: "#ff7f00"}),
    Plot.text(bars, {y: "block", x: "pct",
      text: d => d.pct >= 0.5 ? d.pct.toFixed(1)+"%" : "",
      dx: 4, textAnchor: "start", fontSize: 10}),
    Plot.ruleX([0])
  ]
}));
```

**Key signal:** `cite` block present in only 0.5% of entries — effectively absent. WIL operates without a source-citation apparatus. The `gram` block (99.8%) is near-universal — more systematic than [MW](mw) (67.5%) or [PWG](pwg) (79.8%). Modal blocks = head + body + gram: a very consistent three-block entry across the entire dictionary.

## Per-type citation profile

From [`analysis/CROSS_DICT_PROFILES.md`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/CROSS_DICT_PROFILES.md).

| Type | N | cite% | etym% | mean blocks |
|---|---:|---:|---:|---:|
| noun-m | 15,294 | 0.7% | 0.0% | 3.01 |
| noun-f | 5,950 | 0.9% | 0.0% | 3.01 |
| noun-n | 6,521 | 0.2% | 0.0% | 3.00 |
| adj-mfn | 13,239 | 0.2% | 0.0% | 3.00 |
| indeclinable | 880 | 0.0% | 0.0% | 3.00 |
| other | 2,693 | 0.3% | 0.0% | 2.97 |

**Citation spread: 0.9 pts** — near-zero across all types. Note: this reflects the absence of an `<ls>` apparatus, not a genuine "uniform citation culture." WIL's flat profile is structurally different from [PWG](pwg)'s flat profile — PWG = uniformly *high* citing; WIL = uniformly *absent* citing. Mean blocks ~3.0 for all types: WIL's entry format is exceptionally consistent.

## Framework notes

The common-block framework applies at a reduced level:

- **No `cite` apparatus.** Only 230 `<ls>` tags across 44,577 entries. The citation-profile construct yields no useful comparative information for WIL.
- **No `etym`, `xref`, `hedge`, or `info`** blocks at any meaningful scale.
- **Gram coverage (99.8%) is the highest of any dict.** WIL is exceptional for systematic grammatical notation — every headword gets a `<lex>` tag — while providing almost no source attribution.

The contrast with MW is the point of the lineage analysis: MW inherits WIL's sense-division structure while adding PWG's citation apparatus on top. See [DICT_PROFILE.md — Lineage](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/DICT_PROFILE.md#lineage-wil--koshas-mw--pwg) and [PAPER.md §3](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#3-lineage).

## Lineage position

WIL is the **bridge node**: classical Indian kosha → European philological bilingual dictionary → [MW](mw). The kosha lineage is provable through CDSL's own `koSa` subject classification and the Fort William College record. See [ARMH](armh) and [ABCH](abch) for the kosha sources WIL's pandits worked from.

## See also

- [Cross-dictionary comparison](../tools/cross-dict)
- [Lineage Sankey](../tools/lineage-sankey) — kosha → WIL → MW flow
- [ARMH chapter](armh) · [ABCH chapter](abch) — the kosha sources

---

Source: CDSL wil.txt 2026-05-24 · CC-BY-SA-4.0
