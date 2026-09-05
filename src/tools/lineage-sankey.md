_Created: 23-05-2026 · Last updated: 05-09-2026_

---
title: Lineage Sankey — PWG → MW kosha collapse
toc: false
---

# Lineage Sankey

The central visual evidence for the **kosha-collapse** finding: six PWG `<ls>` labels (left) flow through the actual kosha works they name (middle), then converge into MW's single `<ls>L.</ls>` hedge (right).

## Trust Block

- Evidence: hard-coded PWG and MW citation-flow counts from the documented kosha-collapse analysis.
- Limitations: this is a focused explanatory visual, not a complete source graph or a generated review queue.
- Validation: checked by `npm run build`; counts should be regenerated before paper-final use.
- Owner repo: `csl-atlas`.
- Next use: treat the chart as structural evidence, then check companion docs before making a lineage claim.

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
import * as d3 from "npm:d3@7";
import {sankey, sankeyLinkHorizontal} from "npm:d3-sankey@0.12.3";

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

const label = svg.append("g")
  .selectAll("text")
  .data(graph.nodes)
  .join("text")
    .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
    .attr("y", d => (d.y0 + d.y1) / 2)
    .attr("dy", "0.35em")
    .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
    .style("font-family", "Noto Sans, DejaVu Sans, sans-serif")
    .style("font-size", "11px");

label.selectAll("tspan")
  .data(d => {
    const x = d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6;
    return d.name.split("\n").map((line, index) => ({line, x, index}));
  })
  .join("tspan")
    .attr("x", d => d.x)
    .attr("dy", d => d.index === 0 ? 0 : "1.2em")
    .text(d => d.line);

display(svg.node());
```

---

## What the diagram shows

**Stage 1** (left, six green nodes): PWG's six most-cited *named kosha* labels with their actual citation counts.

**Stage 2** (middle, six pink nodes): the kosha works behind those labels. Hemacandra has two — *Abhidhānacintāmaṇi* (the main lexicon) and the *Anekārthasaṃgraha* (his polysemy supplement).

**Stage 3** (right, one blue node): MW's single `<ls>L.</ls>` hedge — collapses **all six** PWG flows into one. 40,212 citations, 13.95% of all MW entries.

**The collapse is the story.** PWG distinguished six named koshas. MW (and PWK before it) dropped the named-source apparatus and replaced it with `L.` — gaining typographic compactness, losing bibliographic precision.

---

## Shared-corrected-error overlay (APPARATUS-NOT-ERRORS)

```js
const shared = FileAttachment("../data/corrections/shared_error_overlay.json").json();
```

```js
import { csvDownloadButton } from "../lib/csv-download.js";
```

The kosha-collapse Sankey above is about **named sources**. The overlay below is
about **mechanical errors**: headwords that were corrected on both a Petersburg
dictionary (PW / PWG) *and* MW. Edge width is the forensic shared-correction
count (`shared_corrections.csv`, n=${shared.totals.sharedCorrectionRows}). The
**copy-detection verdict is not the edge weight** — it is the Ahlborn direct
test and co-correction null model already computed as F4b.

### Trust Block (overlay)

- Evidence: [`data/forensic/shared_corrections.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/shared_corrections.csv),
  [`data/forensic/f4b_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f4b_report.json),
  packet [`src/data/corrections/shared_error_overlay.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/corrections/shared_error_overlay.json)
  (`npm run build-correction-lane-overlays`).
- Limitations: sample of co-corrected headwords, not the full C3 form-keyed
  loci join; edge weight is raw count, not residual above a confusion-aware null;
  `in_pwgissues` multi-dict fix bundles inflate co-correction by design.
- Validation: F4b numbers reproduced in
  [`docs/A10_REPRODUCIBILITY_AUDIT.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/A10_REPRODUCIBILITY_AUDIT.md);
  packet + page via `npm test` / `npm run build`.
- Owner repo: `csl-atlas` (APPARATUS-NOT-ERRORS).
- Next use: treat co-correction lift as **convergence + editorial coupling**, not
  inheritance of mistakes; pair with [Correction loci](./correction-loci) and
  [Correction front](./correction-front).

```js
const ahl = shared.ahlbornDirectTest;
const nul = shared.nullModel;
display(html`<div style="display:flex;gap:24px;flex-wrap:wrap;margin:8px 0 16px">
  ${[
    ["Ahlborn cases", ahl?.total?.toLocaleString?.() ?? "—"],
    ["Shares PWG error", `${ahl?.sharesError ?? "—"} (${ahl?.sharesErrorPct ?? "—"}%)`],
    ["MW correct form", ahl?.mwCorrect?.toLocaleString?.() ?? "—"],
    ["Co-corrected obs", nul?.observedCoCorrected?.toLocaleString?.() ?? "—"],
    ["Null expected", nul?.expected ?? "—"],
    ["Lift", nul?.lift ?? "—"]
  ].map(([label, value]) => html`<div><div style="font-size:1.5rem;font-weight:700">${value}</div><div style="color:var(--theme-foreground-muted);font-size:.85rem">${label}</div></div>`)}
</div>`);
```

**Verdict (F4b):** MW shares the PWG headword error in only
**${ahl?.sharesError ?? "—"} / ${ahl?.total ?? "—"}** (${ahl?.sharesErrorPct ?? "—"}%)
cases. Co-corrected headwords are elevated (lift ${nul?.lift ?? "—"}), but that
is the *same hard words* receiving *different* fixes — not copied mistakes.

```js
// Pet-dict → MW shared-corrected Sankey (edge width = headword count).
const seNodes = [
  ...shared.edges.map((e) => ({ name: `${e.source}\n${e.sharedCorrectedHeadwords}`, group: "pet" })),
  { name: `MW\nshared-corrected`, group: "mw" }
];
const seLinks = shared.edges.map((e, i) => ({
  source: i,
  target: shared.edges.length,
  value: e.sharedCorrectedHeadwords
}));
const seWidth = 720;
const seHeight = 280;
const seSvg = d3.create("svg").attr("width", seWidth).attr("height", seHeight);
const seLayout = sankey()
  .nodeWidth(18)
  .nodePadding(18)
  .extent([[20, 20], [seWidth - 160, seHeight - 20]]);
const seGraph = seLayout({
  nodes: seNodes.map((d) => Object.assign({}, d)),
  links: seLinks.map((d) => Object.assign({}, d))
});
const seColors = { pet: "#e6550d", mw: "#1f78b4" };
seSvg.append("g").selectAll("rect").data(seGraph.nodes).join("rect")
  .attr("x", (d) => d.x0).attr("y", (d) => d.y0)
  .attr("width", (d) => d.x1 - d.x0).attr("height", (d) => d.y1 - d.y0)
  .attr("fill", (d) => seColors[d.group]).attr("stroke", "#333");
seSvg.append("g").attr("fill", "none").selectAll("path").data(seGraph.links).join("path")
  .attr("d", sankeyLinkHorizontal())
  .attr("stroke", "rgba(230,85,13,0.45)")
  .attr("stroke-width", (d) => Math.max(1, d.width));
const seLabel = seSvg.append("g").selectAll("text").data(seGraph.nodes).join("text")
  .attr("x", (d) => (d.x0 < seWidth / 2 ? d.x1 + 6 : d.x0 - 6))
  .attr("y", (d) => (d.y0 + d.y1) / 2)
  .attr("dy", "0.35em")
  .attr("text-anchor", (d) => (d.x0 < seWidth / 2 ? "start" : "end"))
  .style("font-family", "Noto Sans, DejaVu Sans, sans-serif")
  .style("font-size", "11px");
seLabel.selectAll("tspan")
  .data((d) => {
    const x = d.x0 < seWidth / 2 ? d.x1 + 6 : d.x0 - 6;
    return d.name.split("\n").map((line, index) => ({ line, x, index }));
  })
  .join("tspan")
  .attr("x", (d) => d.x)
  .attr("dy", (d) => (d.index === 0 ? 0 : "1.2em"))
  .text((d) => d.line);
display(seSvg.node());
```

```js
const edgeRows = shared.edges.map((e) => ({
  source: e.source,
  target: e.target,
  sharedCorrectedHeadwords: e.sharedCorrectedHeadwords,
  inPwgissuesBundle: e.inPwgissuesBundle,
  independentOfBundle: e.independentOfBundle,
  examples: e.examples.join("; "),
  evidenceLabel: e.evidenceLabel
}));
display(Inputs.table(edgeRows));
display(csvDownloadButton(edgeRows, "shared-error-lineage-edges.csv"));
```

---

Source: CDSL pwg.txt + mw.txt 2026-05-23. Static SVG: [sankey-en.svg](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/sankey-en.svg). Shared-error overlay: forensic F4/F4b (H1579). CC-BY-SA-4.0.

_Dr. Mārcis Gasūns_
