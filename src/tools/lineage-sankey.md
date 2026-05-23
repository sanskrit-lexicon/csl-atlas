---
title: Lineage Sankey — PWG → MW kosha collapse
toc: false
---

# Lineage Sankey

The central visual evidence for the **kosha-collapse** finding: six PWG `<ls>` labels (left) flow through the actual kosha works they name (middle), then converge into MW's single `<ls>L.</ls>` hedge (right).

```js
// Counts directly from PWG (1855-75) and MW (1899) data files
const pwgFlows = [
  { label: "H.",     work: "Abhidhānacintāmaṇi (Hemacandra)",  count: 17337 },
  { label: "AK.",    work: "Amarakośa",                         count: 14473 },
  { label: "MED.",   work: "Medinīkośa",                        count: 13055 },
  { label: "H. an.", work: "Anekārthasaṃgraha (Hemacandra)",    count: 9771 },
  { label: "TRIK.",  work: "Trikāṇḍaśeṣa",                      count: 8365 },
  { label: "HALĀY.", work: "Abhidhānaratnamālā (Halāyudha)",    count: 5114 }
];
const mwLTotal = 40212;
```

```js
import {sankey, sankeyLinkHorizontal} from "https://cdn.jsdelivr.net/npm/d3-sankey@0/+esm";
import * as d3 from "d3";

// Build nodes and links
const nodes = [
  ...pwgFlows.map(f => ({ name: `${f.label}\n${f.count.toLocaleString()}`, group: "pwg" })),
  ...pwgFlows.map(f => ({ name: f.work, group: "kosha" })),
  { name: `MW <ls>L.</ls>\n${mwLTotal.toLocaleString()}`, group: "mw" }
];
const links = [];
pwgFlows.forEach((f, i) => {
  // Stage 1 -> Stage 2
  links.push({ source: i, target: pwgFlows.length + i, value: f.count });
  // Stage 2 -> Stage 3 (proportional)
  const totalPwg = pwgFlows.reduce((s, x) => s + x.count, 0);
  const flow = Math.round((mwLTotal * f.count) / totalPwg);
  links.push({ source: pwgFlows.length + i, target: 2 * pwgFlows.length, value: flow });
});

const width = 1000;
const height = 600;
const svg = d3.create("svg").attr("width", width).attr("height", height);
const colors = { pwg: "#33a02c", kosha: "#fb9a99", mw: "#1f78b4" };

const layout = sankey()
  .nodeWidth(20)
  .nodePadding(15)
  .extent([[20, 20], [width - 200, height - 30]]);

const graph = layout({ nodes: nodes.map(d => Object.assign({}, d)), links: links.map(d => Object.assign({}, d)) });

svg.append("g")
  .selectAll("rect")
  .data(graph.nodes)
  .join("rect")
    .attr("x", d => d.x0)
    .attr("y", d => d.y0)
    .attr("width", d => d.x1 - d.x0)
    .attr("height", d => d.y1 - d.y0)
    .attr("fill", d => colors[d.group])
    .attr("stroke", "#333");

svg.append("g")
  .attr("fill", "none")
  .selectAll("path")
  .data(graph.links)
  .join("path")
    .attr("d", sankeyLinkHorizontal())
    .attr("stroke", (d, i) => i < pwgFlows.length ? "rgba(51,160,44,0.4)" : "rgba(255,215,0,0.5)")
    .attr("stroke-width", d => Math.max(1, d.width));

svg.append("g")
  .selectAll("text")
  .data(graph.nodes)
  .join("text")
    .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
    .attr("y", d => (d.y0 + d.y1) / 2)
    .attr("dy", "0.35em")
    .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
    .style("font-family", "Noto Sans, DejaVu Sans, sans-serif")
    .style("font-size", "11px")
    .selectAll("tspan")
    .data(d => d.name.split("\n"))
    .join("tspan")
      .attr("x", d => d.parent ? d.parent.x : 0)
      .text(d => d);

display(svg.node());
```

---

## What the diagram shows

**Stage 1** (left, six green nodes): PWG's six most-cited *named kosha* labels with their actual citation counts.

**Stage 2** (middle, six pink nodes): the kosha works behind those labels. Hemacandra has two — *Abhidhānacintāmaṇi* (the main lexicon) and the *Anekārthasaṃgraha* (his polysemy supplement).

**Stage 3** (right, one blue node): MW's single `<ls>L.</ls>` hedge — collapses **all six** PWG flows into one. 40,212 citations, 13.95% of all MW entries.

**The collapse is the story.** PWG distinguished six named koshas. MW (and PWK before it) dropped the named-source apparatus and replaced it with `L.` — gaining typographic compactness, losing bibliographic precision.

---

Source: CDSL pwg.txt + mw.txt 2026-05-23. Static SVG: [sankey-en.svg](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/sankey-en.svg). CC-BY-SA-4.0.
