---
title: AP — Apte Practical Sanskrit–English Dictionary (1890)
---

# AP — Apte's Practical Sanskrit–English Dictionary (1890)

The single-volume Sanskrit–English dictionary by [Vaman Shivaram Apte](https://en.wikipedia.org/wiki/Vaman_Shivaram_Apte). Designed for practical use rather than philological exhaustiveness. **Lowest mean block count** of all structured bilingual dicts (2.53) — the most compact entry format. **Highest per-type citation spread** (15.2 pts) — types are more differentiated by citation behaviour here than in any other dict, reflecting Apte's targeted editorial policy.

**[Source: csl-orig v02/ap90/ap90.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ap90/ap90.txt) · [AP90 GitHub](https://github.com/sanskrit-lexicon/ap90)**

## At a glance

| | |
|---|---|
| Records | 90,654 |
| Volumes | 1 (single-volume practical) |
| Language | English |
| Year | 1890 |
| Genre | Structured bilingual |
| Modal blocks/entry | 2 |
| Mean blocks/entry | 2.53 |
| `<ls>` citations total | 62,671 |
| `<ls>` citations/record | 0.691 |

## Block profile

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
    Plot.barX(bars, {y: "block", x: "pct", fill: "#e31a1c"}),
    Plot.text(bars, {y: "block", x: "pct",
      text: d => d.pct >= 0.5 ? d.pct.toFixed(1)+"%" : "",
      dx: 4, textAnchor: "start", fontSize: 10}),
    Plot.ruleX([0])
  ]
}));
```

**Notable:** `gram` block present in only 29.7% of entries — the lowest gram-coverage of any structured bilingual dict. `etym`, `hedge`, `hom`, and `info` are effectively absent. Modal blocks = 2 (head + body), the minimum viable entry. Despite compactness, `xref` (1.7%) and `cite` (31.6%) are non-zero — Apte cites sources, but selectively.

## Per-type citation profile

From [`analysis/CROSS_DICT_PROFILES.md`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/CROSS_DICT_PROFILES.md).

| Type | N | cite% | etym% | mean blocks |
|---|---:|---:|---:|---:|
| noun-m | 2,646 | 34.4% | 0.0% | 3.37 |
| noun-f | 2,969 | 41.2% | 0.0% | 3.44 |
| noun-n | 882 | 37.0% | 0.0% | 3.42 |
| adj-mfn | 18,764 | 40.0% | 0.0% | 3.41 |
| indeclinable | 1,552 | 49.6% | 0.1% | 3.53 |
| other | 63,841 | 28.1% | 0.0% | 2.15 |

**Citation spread: 15.2 pts** — the highest of all structured bilingual dicts. Indeclinables are best-cited (49.6%), while the `other` category (compounds, verb forms) is lowest (28.1%). The `other` category dominates by record count (63,841 of 90,654 = 70%), pulling the mean block count down significantly (2.15 vs 3.4+ for gender-types). This reflects Apte's compound-heavy coverage with minimal philological apparatus per entry.

## Framework notes

The common-block framework applies to AP, but at a reduced granularity:

- **Minimal blocks.** Modal = 2 (head + body). The majority of AP entries have no separate gram, cite, etym, xref, hedge, or info block. Block-economy is extreme: AP chooses compactness over documentation depth.
- **No `hedge` or `etym` blocks** — not applicable to Apte's editorial approach.
- **High per-type spread (15.2 pts)** means the citation construct is meaningfully differentiated across types — more so than in MW (11.3 pts) or PWG (0.4 pts). This makes AP an interesting counter-case: compact format, but selective citation is more type-specific.

## See also

- [Cross-dictionary comparison](../tools/cross-dict)
- [MW chapter](mw) — the fuller scholarly reference for the same target language

---

Source: CDSL ap90.txt 2026-05-24 · CC-BY-SA-4.0
