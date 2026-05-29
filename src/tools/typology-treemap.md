---
title: Typology treemap
toc: false
---

# Article-type treemap

The composition of MW1899's 286,561 records by article type, as a squarified treemap.

```js
const data = FileAttachment("../data/article-type-counts.json").json();
const articleExamples = FileAttachment("../data/article-type-examples.json").json();
```

```js
import * as d3 from "npm:d3@7";

const width = 1000;
const height = 560;
const root = d3.hierarchy({children: data.types})
  .sum(d => d.count || 0)
  .sort((a, b) => b.value - a.value);

d3.treemap()
  .tile(d3.treemapSquarify)
  .size([width, height])
  .paddingInner(2)
  .round(true)(root);

const color = d3.scaleOrdinal()
  .domain(data.types.map(d => d.type))
  .range(d3.schemeTableau10.concat(d3.schemeSet3));

const svg = d3.create("svg")
  .attr("viewBox", [0, 0, width, height])
  .attr("width", width)
  .attr("height", height)
  .attr("role", "img")
  .attr("aria-label", "Squarified treemap of MW1899 article types");

const leaf = svg.append("g")
  .selectAll("g")
  .data(root.leaves())
  .join("g")
    .attr("transform", d => `translate(${d.x0},${d.y0})`);

leaf.append("rect")
  .attr("width", d => d.x1 - d.x0)
  .attr("height", d => d.y1 - d.y0)
  .attr("fill", d => color(d.data.type))
  .attr("stroke", "white");

leaf.append("title")
  .text(d => `${d.data.type}\n${d.value.toLocaleString()} (${(100 * d.value / data.total).toFixed(1)}%)`);

leaf.filter(d => (d.x1 - d.x0) > 88 && (d.y1 - d.y0) > 48)
  .append("text")
  .attr("x", 7)
  .attr("y", 18)
  .attr("fill", "white")
  .style("font-size", "12px")
  .style("font-weight", "700")
  .selectAll("tspan")
  .data(d => [
    d.data.type,
    `${d.value.toLocaleString()} (${(100 * d.value / data.total).toFixed(1)}%)`
  ])
  .join("tspan")
    .attr("x", 7)
    .attr("dy", (d, i) => i === 0 ? 0 : "1.2em")
    .text(d => d);

display(svg.node());
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

## Entry examples

Each group lists three MW source records matching the same classifier used for the treemap counts. Links open the `csl-orig` MW source line for that record.

```js
const examplesByType = new Map(articleExamples.types.map(d => [d.type, d.examples]));
const exampleGroups = data.types.map(type => ({
  ...type,
  examples: examplesByType.get(type.type) ?? []
}));

display(html`
  <style>
    .examples-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
      margin: 16px 0 24px;
    }

    .example-group {
      border: 1px solid var(--theme-foreground-faint);
      border-radius: 8px;
      padding: 12px;
      background: color-mix(in srgb, var(--theme-background), var(--theme-foreground) 3%);
    }

    .example-group h3 {
      margin: 0 0 4px;
      font-size: 1rem;
      line-height: 1.25;
    }

    .example-count {
      margin-bottom: 8px;
      color: var(--theme-foreground-muted);
      font-size: 0.84rem;
    }

    .example-group ol {
      display: grid;
      gap: 6px;
      margin: 0;
      padding-left: 1.25rem;
    }

    .example-group li {
      line-height: 1.35;
      overflow-wrap: anywhere;
    }

    .entry-meta {
      display: block;
      color: var(--theme-foreground-muted);
      font-size: 0.78rem;
    }
  </style>

  <div class="examples-grid">
    ${exampleGroups.map(group => html`
      <section class="example-group">
        <h3>${group.type}</h3>
        <div class="example-count">${group.count.toLocaleString()} records</div>
        <ol>
          ${group.examples.map(entry => html`
            <li>
              <a href=${entry.href} target="_blank" rel="noopener noreferrer">${entry.k1}</a>
              <span class="entry-meta">L ${entry.L}; page ${entry.pc}; line ${entry.line}</span>
            </li>
          `)}
        </ol>
      </section>
    `)}
  </div>
`);
```

---

Source: CDSL mw.txt 2026-05-23. Static SVG: [treemap-en.svg](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/treemap-en.svg). CC-BY-SA-4.0.
