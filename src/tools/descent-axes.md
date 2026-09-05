_Created: 08-07-2026 · Last updated: 05-09-2026_

---
title: Descent axes
toc: false
---

# Descent axes — is the citation canon a fourth axis?

The atlas measures dictionary inheritance along three committed axes — **content**
(headword-stock containment), **convention** (house-style fingerprint similarity),
and **microstructure** (register/layer similarity) — and
[THREE-AXIS-INDEP](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/THREE_AXIS_INDEPENDENCE.md)
showed they are statistically separate on the 13 documented L0 edges. This page
tests **PH2 CITE-4AXIS**: is the **citation profile** — cosine similarity of two
dictionaries' normalised citation vectors, "do they quote the same books?" — a
*fourth* separable axis, or does it just travel with one of the three?

> The citation vectors come from the canonical-siglum source matrix behind the
> [Citation apparatus](dictionary-citations) page; the dict×text graph behind the
> [Citation canon explorer](citation-canon) is reported as a sensitivity column
> (its MW coverage is degenerate — see the Trust Block).

```js
const data = FileAttachment("../data/lexico/four_axis_citation_independence.json").json();
```

```js
import * as Plot from "npm:@observablehq/plot";
import { csvDownloadButton } from "../lib/csv-download.js";
```

```js
const edges = data.edges.map((e) => ({ ...e, edge: `${e.parent}→${e.child}` }));
const critical = { p05: 0.878, p01: 0.959 };
```

> **n = ${data.n} testable edges** of the ${data.nDocumentedEdges} documented L0 edges —
> only 7 of the 14 edge dictionaries have a validated `<ls>` citation adapter,
> so ${data.edgeShrinkage.excludedEdges.length} edges are excluded (listed below), not imputed.
> At this n only near-perfect collinearity would be detectable (critical |r| = ${critical.p05} at p=0.05);
> read every number as descriptive.

## Verdict — ${data.findings.citationAxisSeparable ? "independence not rejected: consistent with a fourth axis" : "collinearity detected"}

No citation~axis correlation reaches the n=${data.n} p=0.05 threshold, and no exact
label-permutation p (all ${data.citationCorrelations[0].nPermutations} permutations
enumerated) falls below 0.05:

```js
const corrRows = data.citationCorrelations.map((c) => ({
  "axis pair": c.pair,
  Pearson: c.pearson,
  Spearman: c.spearman,
  "exact permutation p": c.permutationP,
  reading: c.strength === "not-significant" ? "not detectable at n=" + data.n : c.strength
}));
display(Inputs.table(corrRows, { rows: 3, layout: "auto" }));
```

```js
display(csvDownloadButton(corrRows, "descent-axes-citation-correlations.csv"));
```

The one estimate worth watching is **citation~microstructure** (Pearson
${data.citationCorrelations[2].pearson}, permutation p ${data.citationCorrelations[2].permutationP}) —
the strongest cross-axis coupling measured on any axis pair so far. It is not
detectable at n=${data.n}, but it is the first thing to re-test when the documented
edge set grows.

## Axis-pair scatters — one dot per documented edge

Each panel plots the ${data.n} testable edges with the citation cosine on the
vertical axis against one of the three committed axes (Pearson r per panel:
content ${data.citationCorrelations[0].pearson}, convention
${data.citationCorrelations[1].pearson}, microstructure
${data.citationCorrelations[2].pearson}).

```js
const AXIS_LABELS = {
  contentAxis: "content (parent-in-child)",
  conventionAxis: "convention similarity",
  microstructureAxis: "microstructure similarity"
};
const longEdges = edges.flatMap((e) =>
  Object.keys(AXIS_LABELS).map((axisKey) => ({
    edge: e.edge,
    panel: AXIS_LABELS[axisKey],
    axisScore: e[axisKey],
    citationAxis: e.citationAxis
  }))
);
display(Plot.plot({
  width: Math.min(width, 960),
  height: 340,
  marginBottom: 45,
  fx: { label: null, domain: Object.values(AXIS_LABELS) },
  x: { label: "axis score", domain: [0, 1], grid: true },
  y: { label: "citation cosine", domain: [0, 1], grid: true },
  marks: [
    Plot.frame(),
    Plot.dot(longEdges, { fx: "panel", x: "axisScore", y: "citationAxis", r: 5, fill: "var(--theme-foreground-focus)", tip: true, title: (d) => `${d.edge}\n${d.panel}: ${d.axisScore}\ncitation: ${d.citationAxis}` }),
    Plot.text(longEdges, { fx: "panel", x: "axisScore", y: "citationAxis", text: "edge", dy: -10, fontSize: 10, fill: "currentColor" })
  ]
}));
```

## The 4×4 correlation matrix (same reduced edge set)

Pearson correlations of all four axes on the same n=${data.n} edges — the three-axis
cells here differ from [THREE-AXIS-INDEP](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/THREE_AXIS_INDEPENDENCE.md)'s
n=13 values because the edge set is reduced; the committed n=13 stats remain the
reference for the original three axes.

```js
const axisOrder = ["content", "convention", "microstructure", "citation"];
display(Plot.plot({
  width: 460,
  height: 420,
  marginLeft: 110,
  x: { domain: axisOrder, label: null },
  y: { domain: axisOrder, label: null },
  color: { type: "diverging", domain: [-1, 1], scheme: "RdBu", label: "Pearson r", legend: true },
  marks: [
    Plot.cell(data.correlationMatrix, { x: "a", y: "b", fill: "pearson" }),
    Plot.text(data.correlationMatrix, { x: "a", y: "b", text: (d) => d.pearson.toFixed(2), fill: (d) => Math.abs(d.pearson) > 0.6 ? "white" : "black" })
  ]
}));
```

```js
display(csvDownloadButton(data.correlationMatrix, "descent-axes-correlation-matrix.csv"));
```

## The testable edges

```js
const edgeRows = edges.map((e) => ({
  edge: e.edge,
  tier: e.tier,
  content: e.contentAxis,
  convention: e.conventionAxis,
  microstructure: e.microstructureAxis,
  "citation (apparatus cosine)": e.citationAxis,
  "shared sources": e.citationSharedSources,
  "ls-graph cosine (sensitivity)": e.graphCitationCosine
}));
display(Inputs.table(edgeRows, { rows: 5, layout: "auto" }));
```

```js
display(csvDownloadButton(edgeRows, "descent-axes-edges.csv"));
```

The sensitivity column is the same cosine computed on the
[`data/citations/`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/README.md)
dict×text graph. It rank-agrees with the apparatus cosine at Spearman
${data.citationVectorSource.sensitivityAgreementSpearman}, but its MW values are
artifacts of resolver coverage (BEN→MW = 0.0 because the graph resolves MW to only
a handful of texts) — which is why the apparatus matrix is the primary source.

## Excluded edges (honest shrinkage)

```js
const excludedRows = data.edgeShrinkage.excludedEdges.map((e) => ({ edge: `${e.parent}→${e.child}`, reason: e.reason }));
display(Inputs.table(excludedRows, { rows: 8, layout: "auto" }));
```

```js
display(csvDownloadButton(excludedRows, "descent-axes-excluded-edges.csv"));
```

## Chart Trust Block

- Claim: ${data.claim}
- Evidence label: `${data.evidenceLabel}`; review status: `${data.reviewStatus}`.
- n = ${data.n} testable edges of ${data.nDocumentedEdges} documented (honest shrinkage: ${data.edgeShrinkage.excludedEdges.length} edges excluded for missing `<ls>` adapters — fewer than the agenda's "9 of 13" estimate; nothing imputed). **Small-n caveat:** critical |r| at n=${data.n} is ${critical.p05} (p=0.05) / ${critical.p01} (p=0.01); all verdicts are descriptive, not confirmatory.
- Source files: [`three_axis_comparison.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/three_axis_comparison.json), [`citation-apparatus.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/citation-apparatus.json), [`ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv) (sensitivity only).
- Generated by: `npm run build-four-axis-independence` → `src/data/lexico/four_axis_citation_independence.json`; exact label-permutation p over all ${data.citationCorrelations[0].nPermutations} permutations per citation~axis pair.
- Validation: `npm run validate-four-axis-independence` (recomputation match, edge accounting, matrix symmetry, cosine bounds); `npm test`; `npm run build`.
- Known limitation: the citation vectors live in the apparatus top-source space (head of the citation-frequency distribution); MW is under-represented in the sensitivity ls-graph column, not in the primary apparatus column.
- Owner repo: `csl-atlas`.
- Next action: re-test citation~microstructure when the documented edge set grows (csl-atlas#89/#92); read the fourth-axis verdict into A03 §4 ([`paper_three_axes_descent.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_three_axes_descent.md)).
- External dependencies: none at runtime; inputs are committed atlas artifacts.
- Boundary note: dictionary citation evidence only — no corpus passage search, no standards export.

Related: [Citation canon explorer](citation-canon) (the dict×text matrix this axis
is derived from) · [Citation apparatus](dictionary-citations) (apparatus style) ·
[Dictionary genealogy](lexicography) (the descent evidence the axes decompose).

_Dr. Mārcis Gasūns_
