---
title: PWK — Böhtlingk Kürzeres PW (1879–1889)
---

# PWK — Böhtlingk Sanskrit-Wörterbuch in kürzerer Fassung (1879–1889)

The single-volume condensed Sanskrit–German dictionary by [Otto von Böhtlingk](https://en.wikipedia.org/wiki/Otto_von_B%C3%B6htlingk). Published after the completion of the seven-volume [PWG](pwg) as an affordable one-volume reference; abridges PWG while adding corrections. **The largest dict by record count in CDSL** (170,556 records), but with a much lower citation density (0.515 `<ls>` per record) than either MW or PWG — condensation preferentially drops citations.

**[Source: csl-orig v02/pw/pw.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pw/pw.txt) · [PWK GitHub](https://github.com/sanskrit-lexicon/pwk)**

## At a glance

| | |
|---|---|
| Records | 170,556 |
| Volumes | 1 (single-volume condensed) |
| Language | German |
| Year | 1879–1889 |
| Genre | Structured bilingual |
| Modal blocks/entry | 3 |
| Mean blocks/entry | 3.32 |
| `<ls>` citations total | 87,812 |
| `<ls>` citations/record | 0.515 |

## Block profile

```js
const cross = FileAttachment("../data/cross-dict.json").json();
```

```js
const d = cross.dicts.find(d => d.code === "PWK");
const LABEL = {head:"head",body:"body (¦)",gram:"gram (lex)",cite:"cite (ls)",hom:"homograph",etym:"etymology",xref:"cross-ref",hedge:"L. hedge",info:"info (digit.)"};
const bars = cross.blocks.map(b => ({block: LABEL[b] ?? b, pct: d.blocks_pct[b]}));
display(Plot.plot({
  width: 580, height: 240, marginLeft: 90,
  x: {label: "% of entries", domain: [0, 100], grid: true},
  y: {label: null},
  marks: [
    Plot.barX(bars, {y: "block", x: "pct", fill: "#6a3d9a"}),
    Plot.text(bars, {y: "block", x: "pct",
      text: d => d.pct >= 0.5 ? d.pct.toFixed(1)+"%" : "",
      dx: 4, textAnchor: "start", fontSize: 10}),
    Plot.ruleX([0])
  ]
}));
```

**Notable:** `cite` block present in only 37.4% of entries — much lower than [PWG](pwg) (94.0%) or [MW](mw) (78.7%). The condensation strategy preferentially drops citations. `xref` (0.0%) and `hedge` (0.0%) are absent, as in PWG. `etym` (2.5%) is present but minimal. `hom` (5.6%) is higher than in MW (3.3%) or PWG (0.1%), reflecting more systematic compound sub-entry tagging.

## Per-type citation profile

From [`analysis/CROSS_DICT_PROFILES.md`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/CROSS_DICT_PROFILES.md).

| Type | N | cite% | etym% | mean blocks |
|---|---:|---:|---:|---:|
| noun-m | 47,304 | 37.6% | 0.0% | 3.38 |
| noun-f | 18,882 | 42.1% | 0.1% | 3.42 |
| noun-n | 20,995 | 41.7% | 0.4% | 3.42 |
| adj-mfn | 46,265 | 45.2% | 0.1% | 3.45 |
| indeclinable | 87 | 21.8% | 0.0% | 3.22 |
| other | 37,023 | 22.7% | 11.2% | 2.10 |

**Citation spread: 7.7 pts** — adj-mfn best-cited (45.2%), indeclinable and other lowest (~22%). The `other` category has the highest etym% (11.2%) — verbal and compound forms where etymology is the main content. Moderate differentiation, between [MW](mw) (11.3 pts) and [PWG](pwg) (0.4 pts).

## Framework notes

The common-block framework applies to PWK with the same adaptations as PWG:

- **No `hedge` or `xref` blocks** — follow the same rules as PWG.
- **Lower citation density** is a condensation choice, not a structural difference. The `cite` block is structurally identical where it appears.
- **Homograph marker (`hom`, 5.6%)** is more common here than in MW or PWG, reflecting more systematic compound sub-entries.

PWK occupies a useful comparison position: same language and editorial tradition as PWG, but same single-volume format constraint as MW. It shows that format (volumes) matters as much as editorial policy in determining block profiles.

## See also

- [Cross-dictionary comparison](../tools/cross-dict)
- [PWG chapter](pwg) — the 7-volume predecessor this condensed
- [MW chapter](mw) — the English-language single-volume parallel

---

Source: CDSL pw.txt 2026-05-24 · CC-BY-SA-4.0
