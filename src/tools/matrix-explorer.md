---
title: Matrix explorer
toc: false
---

# Matrix explorer

The 18 × 14 block-by-article-type heatmap. Hover any cell to see exact percentages + entry counts. Click an article type to filter.

```js
const matrix = FileAttachment("../data/block-by-type-matrix.json").json();
const palette = FileAttachment("../data/palette-tokens.json").json();
```

```js
const types = matrix.types;
const blocks = matrix.blocks;
```

<div class="card">
  <h2>Filter by article type</h2>
  ${Inputs.select(types, {label: "Article type", value: types[0]})}
</div>

```js
display(
  Plot.plot({
    width: 1000,
    height: 700,
    marginLeft: 200,
    color: {
      type: "linear",
      scheme: "ylorrd",
      domain: [0, 100],
      legend: true,
      label: "% of entries"
    },
    x: {label: "Article type", domain: types, tickRotate: 0},
    y: {label: "Formal block", domain: blocks.reverse(), tickRotate: 0},
    marks: [
      Plot.cell(
        matrix.matrix.flatMap(row =>
          blocks.map(b => ({
            type: row.type,
            block: b,
            count: row[b],
            pct: row[b + "_pct"]
          }))
        ),
        {
          x: "type",
          y: "block",
          fill: "pct",
          tip: {
            format: {
              type: true,
              block: true,
              count: ",d",
              pct: ".1f"
            }
          }
        }
      ),
      Plot.text(
        matrix.matrix.flatMap(row =>
          blocks.map(b => ({
            type: row.type,
            block: b,
            pct: row[b + "_pct"],
            label: row[b + "_pct"] > 0 ? row[b + "_pct"].toFixed(0) : ""
          }))
        ),
        {
          x: "type",
          y: "block",
          text: "label",
          fill: d => d.pct > 60 ? "white" : "black",
          fontSize: 9
        }
      )
    ]
  })
);
```

---

## Reading the heatmap

- **Y-axis (rows):** 18 formal blocks (F01 Record header through F18 Correction record) — each block is a structural component of an MW entry.
- **X-axis (columns):** 14 article types — categories of entries (root, masculine noun, compound sub-entry, etc.).
- **Colour:** percentage of entries of that type containing that block. 0% = white; 100% = dark red.
- **Type-defining blocks:** the rows-with-cells-near-100% (F10 sense gloss, F17 machine annotation) are near-universal; the cells-near-100% on specific types (F14 botanical in *botanical* column) define that type.
- **Off-diagonals:** the most informative cells. F13 (`L.` hedge) at 71.5% in botanical and 64.7% in biographical reveals that those types are *koshic*-attested rather than textually attested.

The static SVG version is in the [MWS docs-pass branch](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/heatmap-en.svg).

Source: CDSL mw.txt 2026-05-23 · CC-BY-SA-4.0
