---
title: Citation canon explorer
toc: false
---

# Citation canon explorer

The `<ls>` citation graph across eleven Cologne Sanskrit dictionaries, read as a
single **dictionary × text** matrix: which canonical text each dictionary cites,
how often, and how the whole apparatus is shaped. This is the first-class view of
the [`data/citations/`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/README.md)
graph behind the [A50 paper](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/A50_ls_citation_frequency_graph.md).

It answers one testable question — **PH1 CANON-CORE**: is the shared canon a
*nested* core–periphery (each dictionary's cited texts approximately a subset of
the next-broader one's — one canon in additive strata), or is it *modular*
(dictionaries carry partly disjoint tradition communities)?

> This is the **text graph** — what the dictionaries quote. It is a different
> object from the [Citation apparatus](dictionary-citations) page, which measures
> apparatus *style* (density, breadth, siglum overlap). Read the two together.

```js
const data = FileAttachment("../data/citations/citation_canon.json").json();
```

```js
import * as Plot from "npm:@observablehq/plot";
import { csvDownloadButton } from "../lib/csv-download.js";
```

```js
const verdictLabel = {
  "nested": "Nested (core–periphery)",
  "modular": "Modular (tradition communities)",
  "nested-and-modular": "Nested and modular",
  "neither-detected": "Neither detected"
}[data.verdict] ?? data.verdict;
const nodf = data.stats.nodf;
const mod = data.stats.modularity;
```

> The matrix is **${data.matrix.nDicts} dictionaries × ${data.matrix.nTexts.toLocaleString()} texts**
> with **${data.matrix.nEdges.toLocaleString()}** citation edges (fill ${(data.matrix.fill * 100).toFixed(1)}%).
> Dictionary codes are the `<ls>`-tagged Cologne sources; text names are already IAST.

## Topology verdict — ${verdictLabel}

The binarised matrix is scored two ways and each is compared to
${nodf.nNull.toLocaleString()} degree-preserving (fixed-fixed) permutation nulls
that hold every dictionary's breadth and every text's popularity fixed:

```js
const statRows = [
  { statistic: "NODF nestedness", observed: nodf.observed, "null mean": nodf.nullMean, z: nodf.z, "permutation p": nodf.p, reading: nodf.observed > nodf.nullMean ? "more nested than chance" : "less nested than chance" },
  { statistic: "Barber modularity Q", observed: mod.observed, "null mean": mod.nullMean, z: mod.z, "permutation p": mod.p, reading: mod.observed > mod.nullMean ? "more modular than chance" : "less modular than chance" }
];
display(Inputs.table(statRows, { rows: 2, layout: "auto" }));
```

```js
display(csvDownloadButton(statRows, "citation-canon-stats.csv"));
```

```js
{
  const box = document.createElement("div");
  box.className = "note";
  box.style.borderLeft = "3px solid var(--theme-foreground-focus)";
  box.style.paddingLeft = "12px";
  for (const p of data.interpretation) {
    const el = document.createElement("p");
    el.style.margin = "6px 0";
    el.textContent = p;
    box.appendChild(el);
  }
  display(box);
}
```

## Canon heatmap — dictionaries × most-cited texts

Rows (dictionaries) are ordered by apparatus breadth, top to bottom; columns
(texts) by how many dictionaries cite them, left to right — the packing that
makes a nested matrix look like a staircase and a modular matrix look blocky.
Colour is log citation count.

```js
const heatDicts = data.nestedDictOrder;
const heatTexts = data.topTexts.map(t => t.text);
const cells = data.heatmapCells.filter(c => c.count > 0);
```

```js
display(Plot.plot({
  marginLeft: 56,
  marginBottom: 130,
  marginTop: 10,
  height: 40 + heatDicts.length * 22,
  width: Math.max(720, heatTexts.length * 15),
  x: { domain: heatTexts, tickRotate: -55, label: null, tickSize: 0 },
  y: { domain: heatDicts, label: null },
  color: { type: "log", scheme: "blues", legend: true, label: "citations (log)" },
  marks: [
    Plot.cell(cells, { x: "text", y: "dict", fill: "count", inset: 0.5,
      title: d => `${d.dict} cites ${d.text}: ${d.count.toLocaleString()}` }),
    Plot.axisX({ fontSize: 9 })
  ]
}));
```

> Empty cells are true zeros (that dictionary does not cite that text in its
> tagged apparatus). A staircase of decreasing fill down and to the right would
> mean nesting; discrete blocks would mean disjoint communities.

## Canon curve — how widely shared is each text?

The number of texts cited by exactly *k* of the ${data.matrix.nDicts}
dictionaries. A fat left tail (few universal texts, most texts private to one
dictionary) is the signature of a thin shared head over idiosyncratic tails.

```js
display(Plot.plot({
  marginLeft: 56,
  height: 260,
  x: { domain: data.canonCurve.map(c => String(c.nDicts)), label: "cited by k dictionaries →" },
  y: { grid: true, label: "texts" },
  marks: [
    Plot.barY(data.canonCurve, { x: d => String(d.nDicts), y: "texts", fill: "var(--theme-foreground-focus)" }),
    Plot.text(data.canonCurve.filter(c => c.texts > 0), { x: d => String(d.nDicts), y: "texts", text: d => d.texts.toLocaleString(), dy: -6, fontSize: 10 }),
    Plot.ruleY([0])
  ]
}));
```

```js
display(csvDownloadButton(data.canonCurve, "citation-canon-curve.csv"));
```

## Per-dictionary fingerprint

Breadth (distinct texts cited), total citation volume, coverage of the shared
core (the ${data.perDict[0]?.coreSize ?? 20} most widely-cited texts), and each
dictionary's five heaviest sources.

```js
const fpRows = data.perDict.map(d => ({
  dict: d.dict,
  "distinct texts": d.distinctTexts,
  "total citations": d.totalCites,
  "core coverage": `${d.coreHits}/${d.coreSize}`,
  "top sources": d.topTexts.map(t => `${t.text} (${t.count.toLocaleString()})`).join("; ")
}));
display(Inputs.table(fpRows, {
  rows: data.matrix.nDicts,
  layout: "auto",
  width: { "top sources": 420 },
  sort: "total citations",
  reverse: true
}));
```

```js
display(csvDownloadButton(fpRows, "citation-canon-per-dict.csv"));
```

## Most-cited texts — the shared reading list

The top ${data.topTexts.length} canonical texts by number of dictionaries citing
them, then by in-graph citation volume. The head of this table is the reading a
learner can trust every dictionary to support.

```js
const topRows = data.topTexts.map((t, i) => ({
  rank: i + 1,
  text: t.text,
  "in n dicts": t.nDicts,
  "total citations": t.totalCites,
  "variant forms": t.variants
}));
display(Inputs.table(topRows, { rows: 20, layout: "auto", width: { "variant forms": 260 } }));
```

```js
display(csvDownloadButton(topRows, "citation-canon-top-texts.csv"));
```

## Chart Trust Block

- Claim: ${data.claim}
- Evidence label: `${data.evidenceLabel}`; review status: `${data.reviewStatus}`.
- Source files: [`ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv), [`ls_citation_nodes.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nodes.tsv).
- Generated by: `npm run build-citation-canon` → `src/data/citations/citation_canon.json`; verdict **${verdictLabel}** (NODF ${nodf.observed}, permutation p ${nodf.p}; Barber Q ${mod.observed}, permutation p ${mod.p}; ${nodf.nNull.toLocaleString()} degree-preserving nulls, Dror et al. 2018 protocol).
- Validation: `npm run validate-citation-canon` (matrix dimensions, per-dict counts, canon-curve sum, verdict–stats consistency); `npm test`; `npm run build`.
- Known false negatives: prose/`iti` citations (VCP, SKD, WIL) are not in the `<ls>` graph, so those dictionaries' rows understate their real canon; MW's grammatical/editorial `<ls>` markers (63,582) are filtered as non-text, so MW is under-represented.
- Review status: machine-reviewed; the tradition-community reading of the modular verdict is a candidate for the human-reviewed tradition-tag map (agenda backlog #9).
- Owner repo: `csl-atlas`.
- Next action: read the highlighted off-canon rows (e.g. `bhs`'s Buddhist sources) against the exact dictionary entries via the [source viewer](source), and cross-check apparatus style on the [Citation apparatus](dictionary-citations) page.
- External dependencies: none at runtime; inputs are two committed atlas TSVs.
- Boundary note: dictionary citation evidence only — no corpus passage search, no standards export.

```js
{
  const box = document.createElement("div");
  box.className = "note";
  const head = document.createElement("p");
  head.style.margin = "6px 0";
  head.style.fontWeight = "600";
  head.textContent = "Limitations";
  box.appendChild(head);
  for (const l of data.limitations) {
    const el = document.createElement("p");
    el.style.margin = "6px 0";
    el.textContent = "— " + l;
    box.appendChild(el);
  }
  display(box);
}
```

---

Generated by `npm run build-citation-canon`. See
[`docs/ATLAS_RESEARCH_AGENDA.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ATLAS_RESEARCH_AGENDA.md)
§2 PH1 / §3 V1 and
[`docs/articles/A50_ls_citation_frequency_graph.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/A50_ls_citation_frequency_graph.md).
CC-BY-SA-4.0.
