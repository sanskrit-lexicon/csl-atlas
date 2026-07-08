---
title: Correction loci
toc: false
---

# Correction loci — where the fixes land in the printed book

Every accepted correction to a Cologne dictionary's digital text is recorded as
a change-file line in
[`csl-corrections`](https://github.com/sanskrit-lexicon/csl-corrections); its
[`correction_loci.tsv`](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/data/derived/correction_loci.tsv)
feed resolves each record to the printed **`<pc>` page** it touches. This page
reads that feed as a spatial and editorial signal: **where in each printed
edition the reported errors sit**, and **how actively maintained each
dictionary is** — the editorial axes of the per-dictionary radar
([METALEXICOGRAPHY_ROADMAP](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/METALEXICOGRAPHY_ROADMAP.md) §2.6/§3).

> **Read the process split first.** 76% of all records are *machine batches*
> (the BOR digitization completion and the LRV markup-homogenization sweep),
> not human proofreading. Every view below separates `human` from `bulk`;
> cross-dictionary maintenance comparisons should default to the human series.

```js
const data = FileAttachment("../data/corrections/correction_loci.json").json();
```

```js
import * as Plot from "npm:@observablehq/plot";
import { csvDownloadButton } from "../lib/csv-download.js";
import { slp1ToIast } from "../lib/lookup-normalize.js";
```

```js
const perDict = data.perDict;
const totals = data.totals;
```

> The feed carries **${totals.records.toLocaleString()} correction records**
> across **${totals.dicts} dictionaries** — ${totals.human.toLocaleString()}
> human, ${totals.bulk.toLocaleString()} bulk;
> ${totals.pcResolved.toLocaleString()} are resolved to a printed page.

## Editorial KPIs — corrections per 1,000 entries

Corrections per 1k current entries (`<L>` records in csl-orig v02), stacked by
process. This is the "how actively maintained" axis: BOR's enormous per-1k
value is its one-shot digitization completion batch, not ongoing editorial
attention — which is exactly why the human slice is drawn separately.

```js
const per1kRows = perDict
  .filter((d) => d.per1k != null)
  .flatMap((d) => [
    { dict: d.dict, process: "human", per1k: d.per1kHuman },
    { dict: d.dict, process: "bulk", per1k: Math.max(0, (d.per1k ?? 0) - (d.per1kHuman ?? 0)) }
  ])
  .filter((r) => r.per1k > 0);
```

```js
display(Plot.plot({
  marginLeft: 56,
  height: 320,
  x: { type: "log", label: "corrections per 1k entries (log)", domain: [0.01, 1000] },
  y: { domain: perDict.filter((d) => d.per1k != null).map((d) => d.dict), label: null },
  color: { domain: ["human", "bulk"], range: ["var(--theme-foreground-focus)", "var(--theme-foreground-fainter)"], legend: true },
  marks: [
    Plot.dot(per1kRows, { x: "per1k", y: "dict", fill: "process", r: 5,
      title: (r) => `${r.dict} ${r.process}: ${r.per1k} per 1k entries` }),
    Plot.ruleX([0.01])
  ]
}));
```

```js
const kpiRows = perDict.map((d) => ({
  dict: d.dict,
  records: d.records,
  human: d.human,
  bulk: d.bulk,
  "human share": d.humanShare,
  entries: d.entries,
  "per 1k": d.per1k,
  "per 1k (human)": d.per1kHuman,
  "pages touched": d.distinctPages,
  "page coverage": d.pageCoverage,
  "pc-resolved share": d.pcResolvedShare,
  "first batch": d.firstDate,
  "last batch": d.lastDate
}));
display(Inputs.table(kpiRows, { rows: 16, layout: "auto" }));
display(csvDownloadButton(kpiRows, "correction-editorial-kpis.csv"));
```

## Editorial radar — the correction-fed axes

Five editorial axes per dictionary, each normalized to the maximum across the
dictionaries currently shown (per-1k axes on a log scale, so BOR's batch spike
does not flatten everyone else). These are the axes this feed contributes to
the roadmap's per-dictionary radar; markup-density and citation axes stay on
HOLD in the roadmap and are not drawn here.

```js
const radarDicts = perDict.filter((d) => d.per1k != null && d.pcResolved > 0);
const radarPick = view(Inputs.select(radarDicts.map((d) => d.dict), {
  multiple: true,
  value: ["mw", "ap", "shs", "lrv"],
  label: "dictionaries"
}));
```

```js
const AXES = [
  { key: "per1k", label: "per 1k (all)", value: (d) => Math.log10(1 + (d.per1k ?? 0)) },
  { key: "per1kHuman", label: "per 1k (human)", value: (d) => Math.log10(1 + (d.per1kHuman ?? 0)) },
  { key: "humanShare", label: "human share", value: (d) => d.humanShare ?? 0 },
  { key: "pageCoverage", label: "page coverage", value: (d) => d.pageCoverage ?? 0 },
  { key: "pcShare", label: "pc-resolved", value: (d) => d.pcResolvedShare ?? 0 }
];
const shown = radarDicts.filter((d) => radarPick.includes(d.dict));
const axisMax = AXES.map((ax) => Math.max(...radarDicts.map((d) => ax.value(d)), 1e-9));
const angle = (i) => (i / AXES.length) * 2 * Math.PI - Math.PI / 2;
const radarLines = shown.flatMap((d) => {
  const pts = AXES.map((ax, i) => {
    const r = ax.value(d) / axisMax[i];
    return { dict: d.dict, axis: ax.label, r, x: r * Math.cos(angle(i)), y: r * Math.sin(angle(i)) };
  });
  return [...pts, { ...pts[0] }];
});
const rings = [0.25, 0.5, 0.75, 1].flatMap((r) =>
  [...AXES.map((ax, i) => ({ ring: r, x: r * Math.cos(angle(i)), y: r * Math.sin(angle(i)) })),
    { ring: r, x: r * Math.cos(angle(0)), y: r * Math.sin(angle(0)) }]
);
const axisLabels = AXES.map((ax, i) => ({ label: ax.label, x: 1.22 * Math.cos(angle(i)), y: 1.22 * Math.sin(angle(i)) }));
```

```js
display(Plot.plot({
  width: 560,
  height: 480,
  aspectRatio: 1,
  x: { axis: null, domain: [-1.45, 1.45] },
  y: { axis: null, domain: [-1.35, 1.35] },
  color: { legend: true },
  marks: [
    Plot.line(rings, { x: "x", y: "y", z: "ring", stroke: "var(--theme-foreground-faintest)", strokeWidth: 0.6 }),
    Plot.link(axisLabels, { x1: 0, y1: 0, x2: (d) => d.x / 1.22, y2: (d) => d.y / 1.22, stroke: "var(--theme-foreground-faintest)", strokeWidth: 0.6 }),
    Plot.text(axisLabels, { x: "x", y: "y", text: "label", fontSize: 11, fill: "var(--theme-foreground-muted)" }),
    Plot.line(radarLines, { x: "x", y: "y", z: "dict", stroke: "dict", strokeWidth: 1.8, curve: "linear-closed", opacity: 0.85 }),
    Plot.dot(radarLines, { x: "x", y: "y", stroke: "dict", r: 2.5,
      title: (d) => `${d.dict} — ${d.axis}: ${(d.r * 100).toFixed(0)}% of max` })
  ]
}));
```

```js
const radarCsv = shown.map((d) => Object.fromEntries([
  ["dict", d.dict],
  ...AXES.map((ax, i) => [ax.label, Number((ax.value(d) / axisMax[i]).toFixed(4))])
]));
display(csvDownloadButton(radarCsv, "correction-radar-axes.csv"));
```

## Locus heatmap — normalized page position × dictionary

Each row is one dictionary's printed edition, left edge = page 1, right edge =
its **last corrected page** (see the trust block: the feed's own maximum, not
the true page count). Colour is corrections per position bin
(${data.positionBins} bins). Toggle the process series; "row share" rescales
each row by its own total so sparsely-corrected dictionaries stay readable.

```js
const processPick = view(Inputs.radio(["all", "human", "bulk"], { value: "all", label: "process" }));
const rowNorm = view(Inputs.toggle({ label: "row share (normalize each dictionary)", value: false }));
```

```js
const binTotals = new Map();
for (const c of data.heatmapCells) {
  if (processPick !== "all" && c.process !== processPick) continue;
  const key = `${c.dict}|${c.bin}`;
  binTotals.set(key, (binTotals.get(key) ?? 0) + c.count);
}
const rowSums = new Map();
for (const [key, n] of binTotals) {
  const dict = key.split("|")[0];
  rowSums.set(dict, (rowSums.get(dict) ?? 0) + n);
}
const heatCells = [...binTotals.entries()].map(([key, count]) => {
  const [dict, bin] = key.split("|");
  return { dict, bin: Number(bin), count, share: count / (rowSums.get(dict) || 1) };
});
const heatDicts = data.heatmapDicts.filter((d) => rowSums.has(d));
const maxPageOf = new Map(perDict.map((d) => [d.dict, d.maxPage]));
```

```js
display(Plot.plot({
  marginLeft: 56,
  height: 60 + heatDicts.length * 26,
  width: 940,
  x: { label: "normalized page position (0 = page 1, 1 = last corrected page)", domain: [0, data.positionBins], ticks: 5, tickFormat: (b) => (b / data.positionBins).toFixed(2) },
  y: { domain: heatDicts, label: null },
  color: rowNorm
    ? { scheme: "blues", label: "share of row", legend: true }
    : { type: "log", scheme: "blues", label: "corrections (log)", legend: true },
  marks: [
    Plot.cell(heatCells, {
      x: "bin", y: "dict", fill: rowNorm ? "share" : "count", inset: 0.5,
      title: (c) => {
        const maxPage = maxPageOf.get(c.dict) ?? 0;
        const lo = Math.round((c.bin / data.positionBins) * maxPage);
        const hi = Math.round(((c.bin + 1) / data.positionBins) * maxPage);
        return `${c.dict} pages ~${lo}–${hi}: ${c.count} corrections (${(c.share * 100).toFixed(1)}% of row)`;
      }
    })
  ]
}));
```

```js
display(csvDownloadButton(heatCells.map((c) => ({ dict: c.dict, bin: c.bin, count: c.count, share: Number(c.share.toFixed(4)) })), "correction-heatmap-cells.csv"));
```

## One dictionary in detail — position × column

For dictionaries whose change files carry a regular column notation
(${data.columnDicts.join(", ")}), the same positions split by printed column.

```js
const detailDict = view(Inputs.select(data.columnDicts, { value: data.columnDicts.includes("mw") ? "mw" : data.columnDicts[0], label: "dictionary" }));
```

```js
const detailCells = data.columnCells
  .filter((c) => c.dict === detailDict && (processPick === "all" || c.process === processPick))
  .reduce((m, c) => {
    const key = `${c.bin}|${c.col}`;
    m.set(key, (m.get(key) ?? 0) + c.count);
    return m;
  }, new Map());
const detailRows = [...detailCells.entries()].map(([key, count]) => {
  const [bin, col] = key.split("|");
  return { bin: Number(bin), col, count };
});
const detailCols = [...new Set(detailRows.map((r) => r.col))].sort();
```

```js
display(Plot.plot({
  marginLeft: 56,
  height: 60 + detailCols.length * 30,
  width: 940,
  x: { label: "normalized page position", domain: [0, data.positionBins], ticks: 5, tickFormat: (b) => (b / data.positionBins).toFixed(2) },
  y: { domain: detailCols, label: "column" },
  color: { type: "log", scheme: "blues", label: "corrections (log)", legend: true },
  marks: [
    Plot.cell(detailRows, { x: "bin", y: "col", fill: "count", inset: 0.5,
      title: (c) => `${detailDict} col ${c.col}, bin ${c.bin}: ${c.count}` })
  ]
}));
```

## Hottest pages — deep links into the source

The most-corrected printed pages per dictionary. Each row links into the
[source viewer](source) at a sample corrected line, so a cell of the heatmap is
one click from the actual dictionary text (headwords shown in IAST).

```js
const topDictPick = view(Inputs.select(["all", ...perDict.filter((d) => d.pcResolved > 0).map((d) => d.dict)], { value: "all", label: "dictionary" }));
```

```js
const topRows = data.topPages
  .filter((p) => topDictPick === "all" || p.dict === topDictPick)
  .map((p) => ({
    dict: p.dict,
    page: p.page,
    corrections: p.count,
    human: p.human,
    bulk: p.bulk,
    "sample headword": slp1ToIast(p.sampleK1 || ""),
    source: p.sampleLine ? html`<a href="source#${p.dict}/${p.sampleLine}">line ${p.sampleLine}</a>` : ""
  }));
display(Inputs.table(topRows, { rows: 15, layout: "auto", format: { source: (v) => v } }));
display(csvDownloadButton(
  data.topPages
    .filter((p) => topDictPick === "all" || p.dict === topDictPick)
    .map((p) => ({ dict: p.dict, page: p.page, corrections: p.count, human: p.human, bulk: p.bulk, sample_headword_iast: slp1ToIast(p.sampleK1 || ""), sample_line: p.sampleLine })),
  "correction-top-pages.csv"
));
```

## Batch cadence

Records per batch month, by process. Change files land in dated batches, so
this is delivery cadence (when fixes were filed into csl-orig), not discovery
dates.

```js
display(Plot.plot({
  marginLeft: 56,
  height: 240,
  x: { label: null, type: "band" },
  y: { label: "records", type: "sqrt" },
  color: { domain: ["human", "bulk"], range: ["var(--theme-foreground-focus)", "var(--theme-foreground-fainter)"], legend: true },
  marks: [
    Plot.barY(data.monthly, { x: "month", y: "count", fill: "process",
      title: (m) => `${m.month} ${m.process}: ${m.count.toLocaleString()}` }),
    Plot.ruleY([0])
  ]
}));
display(csvDownloadButton(data.monthly, "correction-monthly.csv"));
```

## Chart Trust Block

- **Claim:** where reported-and-fixed errors sit in each printed edition, and
  how much accepted correction activity each dictionary has received per 1,000
  entries, split machine-batch vs human.
- **Evidence label:** `derived` — deterministic aggregation of the
  locus-resolved correction feed; no classification or model.
- **Source files:**
  [`csl-corrections/data/derived/correction_loci.tsv`](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/data/derived/correction_loci.tsv)
  (${totals.records.toLocaleString()} records; parser
  [`build_correction_loci.py`](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/scripts/build_correction_loci.py)
  owned by csl-corrections) +
  [`dict_entry_counts.tsv`](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/data/derived/dict_entry_counts.tsv)
  (csl-orig v02 `<L>` counts, 2026-07-07); committed atlas packet
  [`src/data/corrections/correction_loci.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/corrections/correction_loci.json)
  with feed-commit provenance in its `.source.json` sidecar.
- **Generated by:** `npm run build-correction-feed`
- **Validation:** `npm run validate-correction-feed` — per-dict sums, heatmap
  cell sums vs pc-resolved counts, per-1k arithmetic, plus a full row-count
  cross-check against the sibling feed when the checkout is present.
- **Known false positives:** hot pages read as *reader attention*, not print
  quality — corrections require a reader to pass by (C6 confound in the
  [csl-corrections memo](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/HYPOTHESES_AND_VIZ_MEMO.md)).
  BOR/LRV bulk batches are digitization completion / markup homogenization,
  not error findings.
- **Known false negatives:** the normalized position axis ends at each
  dictionary's last *corrected* page, so never-corrected tail pages are
  invisible; STC records carry no `<pc>` headers at all; corrections merged
  before the change-file convention (2014) are absent.
- **Review status:** machine-reviewed (deterministic validator; no human
  review of individual loci).
- **Owner repo:** `csl-atlas` (rendering + aggregation); the feed itself is
  owned by `csl-corrections`.
- **Next action:** proofreading targets — sort the heatmap's *cold* bins of
  heavily-read dictionaries (MW mid-alphabet troughs) for the next human
  correction sweep; and when the observatory's component-labeled event feed is
  wired, add component mix + fix-latency as the two missing radar axes
  (roadmap §2.6).
- **External dependencies:**
  [`csl-corrections`](https://github.com/sanskrit-lexicon/csl-corrections)
  (feed), csl-orig v02 (entry counts, via the feed's sidecar).
- **Boundary note:** the atlas aggregates and renders; correction typology,
  corrector stats, and trends stay with
  [`csl-observatory`](https://github.com/sanskrit-lexicon/csl-observatory)'s
  event data, and the change-file parser stays in csl-corrections.
