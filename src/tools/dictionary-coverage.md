---
title: All-dictionary coverage
toc: false
---

# All-dictionary coverage

This tool extends the nine-chapter comparison to every CDSL v02 dictionary with a main source file. It keeps the [MW §3 block vocabulary](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#3-the-five-grounded-constructs) as the probe, but reports both **structure** and **size**: record count, entry length, block character mass, and entry-type inventory.

```js
const coverage = FileAttachment("../data/dictionary-coverage.json").json();
```

```js
const dicts = coverage.dicts;
const blocks = Object.keys(coverage.blockLabels);
const types = Object.keys(coverage.typeLabels);
const bandOrder = ["full structured fit", "partial structured fit", "prose / iti fit", "entry-shell fit", "weak fit", "outside scheme", "empty"];
```

```js
display(Inputs.table(dicts, {
  columns: ["code", "title", "volumes", "records", "meanChars", "medianChars", "lsPerRecord", "inlineItiPerRecord", "nonzeroTypes", "fitScore", "fitBand"],
  header: {
    code: "Dict",
    title: "Title",
    volumes: "Vols",
    records: "Records",
    meanChars: "Mean chars",
    medianChars: "Median chars",
    lsPerRecord: "raw ls tags/rec",
    inlineItiPerRecord: "iti/rec",
    nonzeroTypes: "Types",
    fitScore: "Fit",
    fitBand: "Band"
  },
  format: {
    records: x => x.toLocaleString(),
    meanChars: x => x.toLocaleString(),
    medianChars: x => x.toLocaleString(),
    lsPerRecord: x => x.toFixed(3),
    inlineItiPerRecord: x => x.toFixed(3)
  },
  sort: "fitScore",
  reverse: true
}));
```

## Fit and scale

```js
display(Plot.plot({
  width: 960,
  height: 430,
  marginLeft: 70,
  marginBottom: 70,
  x: {type: "log", label: "records (log scale)", grid: true},
  y: {label: "framework-fit score", domain: [0, 100], grid: true},
  color: {legend: true, domain: bandOrder, range: ["#1b9e77", "#66a61e", "#7570b3", "#a6761d", "#e6ab02", "#666666", "#999999"]},
  marks: [
    Plot.dot(dicts, {x: "records", y: "fitScore", r: d => Math.max(4, Math.min(18, Math.sqrt(d.meanChars) / 1.3)), fill: "fitBand", stroke: "white", tip: true}),
    Plot.text(dicts.filter(d => ["MW", "PWG", "PWK", "SKD", "VCP", "AP"].includes(d.code)), {
      x: "records", y: "fitScore", text: "code", dy: -12, fontSize: 11
    })
  ]
}));
```

## Common-block population

```js
const blockCells = dicts.flatMap(d => blocks.map(block => ({
  dict: d.code,
  block: coverage.blockLabels[block],
  pct: d.blockPct[block],
  band: d.fitBand
})));

display(Plot.plot({
  width: 960,
  height: 520,
  marginLeft: 135,
  marginBottom: 80,
  color: {type: "linear", scheme: "ylorrd", domain: [0, 100], legend: true, label: "% entries"},
  x: {label: "Dictionary", domain: dicts.map(d => d.code), tickRotate: -45},
  y: {label: "Block", domain: blocks.map(b => coverage.blockLabels[b])},
  marks: [
    Plot.cell(blockCells, {x: "dict", y: "block", fill: "pct", tip: true}),
    Plot.text(blockCells, {x: "dict", y: "block", text: d => d.pct >= 25 ? d.pct.toFixed(0) : "", fill: d => d.pct > 60 ? "white" : "black", fontSize: 8})
  ]
}));
```

## Size by dictionary

```js
display(Plot.plot({
  width: 960,
  height: 360,
  marginLeft: 55,
  marginBottom: 70,
  x: {label: "Dictionary", domain: dicts.map(d => d.code), tickRotate: -45},
  y: {label: "mean entry characters", grid: true},
  marks: [
    Plot.barY(dicts, {x: "code", y: "meanChars", fill: d => d.fitBand === "prose / iti fit" ? "#7570b3" : "#1f78b4", tip: true}),
    Plot.ruleY([0])
  ]
}));
```

```js
const selectedCode = view(Inputs.select(dicts.map(d => d.code), {label: "Inspect dictionary", value: "MW"}));
const selected = dicts.find(d => d.code === (selectedCode ?? "MW")) ?? dicts[0];
```

## Block size inside selected dictionary

```js
const blockSizeRows = blocks.map(block => ({
  block: coverage.blockLabels[block],
  chars: selected.blockChars[block],
  pct: selected.blockCharPct[block],
  entries: selected.blockCounts[block],
  entryPct: selected.blockPct[block]
})).sort((a, b) => b.chars - a.chars);

display(Plot.plot({
  width: 900,
  height: 360,
  marginLeft: 150,
  x: {label: "signal characters (overlapping)", grid: true},
  y: {label: null, domain: blockSizeRows.map(d => d.block)},
  marks: [
    Plot.barX(blockSizeRows, {y: "block", x: "chars", fill: "#4daf4a", tip: true}),
    Plot.text(blockSizeRows, {y: "block", x: "chars", text: d => d.chars ? d.pct.toFixed(1) + "%" : "", dx: 4, textAnchor: "start", fontSize: 10}),
    Plot.ruleX([0])
  ]
}));
```

## Entry-type inventory

The current all-dictionary pass uses nine heuristic entry-type buckets: root/verbal lemma, three nominal genders, adjective, indeclinable/particle, compound/continuation, proper/encyclopedic, and other/untyped. This is a research scaffold: the counts identify where the type system transfers cleanly and where dictionary-specific review is needed.

```js
const typeRows = types.map(type => ({
  type: coverage.typeLabels[type],
  count: selected.typeCounts[type],
  pct: selected.typePct[type]
})).filter(d => d.count > 0).sort((a, b) => b.count - a.count);

display(Plot.plot({
  width: 900,
  height: 360,
  marginLeft: 170,
  x: {label: "entries", grid: true},
  y: {label: null, domain: typeRows.map(d => d.type)},
  marks: [
    Plot.barX(typeRows, {y: "type", x: "count", fill: "#377eb8", tip: true}),
    Plot.text(typeRows, {y: "type", x: "count", text: d => d.pct.toFixed(1) + "%", dx: 4, textAnchor: "start", fontSize: 10}),
    Plot.ruleX([0])
  ]
}));
```

```js
display(Inputs.table(typeRows, {
  columns: ["type", "count", "pct"],
  header: {type: "Entry type", count: "Entries", pct: "%"},
  format: {count: x => x.toLocaleString(), pct: x => x.toFixed(2)}
}));
```

---

Source: generated by `npm run build-coverage` from local `../csl-orig/v02` source files. Block character counts are overlapping signal measurements, not a partition of the entry. The fit scores are exploratory and should guide philological review, not replace it.
