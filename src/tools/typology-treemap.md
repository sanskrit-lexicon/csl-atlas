---
title: Typology treemap
toc: false
---

# Article-type treemap

The composition of MW1899's 286,561 records by article type, as a squarified treemap.

```js
const data = FileAttachment("../../data/article-type-counts.json").json();
```

```js
import * as Plot from "@observablehq/plot";
display(
  Plot.plot({
    width: 1000,
    height: 560,
    color: {
      legend: true,
      domain: data.types.map(t => t.type)
    },
    marks: [
      Plot.cell(data.types, Plot.stackY({
        fy: d => d.type,
        x: "count",
        fill: "type",
        title: d => `${d.type}\n${d.count.toLocaleString()} (${(100*d.count/data.total).toFixed(1)}%)`
      }))
    ]
  })
);
```

---

## Reading the treemap

- Largest tile: **compound sub-entries** (126,360, 44.1%) — half the dictionary is compound members.
- Next: **derived forms** (72,119, 25.2%) — suffixed derivatives.
- Then **Vedic-accented** (47,598, 16.6%) — entries with the `/` udātta marker; *overlaps* with other types.
- **Lexicographer-only** (38,414, 13.4%) — entries whose only `<ls>` citation is `L.`; also overlapping.
- Smaller tiles: masculine nouns (19,204), other types.

**Note:** the types overlap (an entry can be both `noun-m` AND `vedic-accented`). The sizes are membership counts, not exclusive partitions. The total is not additive.

---

Source: CDSL mw.txt 2026-05-23. Static SVG: [treemap-en.svg](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/treemap-en.svg). CC-BY-SA-4.0.
