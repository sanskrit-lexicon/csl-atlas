_Created: 24-07-2026 · Last updated: 05-09-2026_

---
title: Correction front
toc: false
---

# Correction front — where editorial attention moves over time

The **diachronic correction front**: month-by-month and era-split views of where
Cologne dictionaries receive accepted fixes, coloured by OBS-T microstructure
component (`headword`, `sense`, `markup`, `citation`, …). Atlas **renders** this
strip; the event typology is owned by
[`csl-observatory`](https://github.com/sanskrit-lexicon/csl-observatory)
(OBS-T / MW-ATTENTION boundary — never recomputed here).

Sister pages: spatial loci on
[Correction loci](./correction-loci), shared-error lineage overlay on
[Lineage Sankey](./lineage-sankey).

```js
const data = FileAttachment("../data/corrections/correction_front.json").json();
```

```js
import * as Plot from "npm:@observablehq/plot";
import { csvDownloadButton } from "../lib/csv-download.js";
```

## Trust Block

- Evidence: OBS-T
  [`correction_events_release.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_release.csv)
  aggregated by `npm run build-correction-lane-overlays` into
  [`src/data/corrections/correction_front.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/corrections/correction_front.json)
  (${data.totals.events.toLocaleString()} events; top ${data.topDicts.length} dicts in the strip).
- Limitations: event grain ≠ csl-corrections change-file loci; `error_component=unattributed`
  is the plurality class; corrector identity omitted (personal data).
- Validation: `npm run build-correction-lane-overlays` + `npm test` (correction-lane-overlays);
  page by `npm run build`.
- Owner repo: `csl-atlas` (rendering). Data owner: `csl-observatory`.
- Next use: teach the 2014–2018 vs 2019–2026 component shift; pair with correction-loci for
  "where in the book" vs "when / which layer".

```js
display(html`<div style="display:flex;gap:24px;flex-wrap:wrap;margin:8px 0 16px">
  ${[
    ["Events", data.totals.events.toLocaleString()],
    ["Dated", data.totals.dated.toLocaleString()],
    ["Dicts in corpus", data.totals.dicts.toLocaleString()],
    ["Strip dicts", data.topDicts.length],
    ["Era split", data.eraSplit]
  ].map(([label, value]) => html`<div><div style="font-size:1.5rem;font-weight:700">${value}</div><div style="color:var(--theme-foreground-muted);font-size:.85rem">${label}</div></div>`)}
</div>`);
```

## Era overview — 2014–2018 vs 2019–2026

Total events per top dictionary in each era (all components). The second era is
not simply "more of the same": component mix shifts (see next chart).

```js
const eraOrder = ["2014-2018", "2019-2026"];
const dictOrder = data.topDicts;
```

```js
display(Plot.plot({
  marginLeft: 56,
  width: Math.min(width, 920),
  height: 80 + dictOrder.length * 22,
  x: { label: "events", grid: true },
  y: { domain: dictOrder, label: null },
  fx: { domain: eraOrder, label: null },
  color: { legend: true, scheme: "observable10" },
  marks: [
    Plot.barX(data.eraOverview, {
      x: "count",
      y: "dict",
      fx: "era",
      fill: "dict",
      tip: true
    })
  ]
}));
```

```js
display(csvDownloadButton(data.eraOverview, "correction-front-era-overview.csv"));
```

## Era × component (small multiples)

Stacked component share per dictionary within each era. Read left→right for the
front's maturation: surface/markup vs sense-layer attention.

```js
const eraComp = data.era;
const componentOrder = Object.keys(data.components);
```

```js
display(Plot.plot({
  marginLeft: 56,
  width: Math.min(width, 960),
  height: 90 + dictOrder.length * 26,
  x: { label: "events", grid: true },
  y: { domain: dictOrder, label: null },
  fx: { domain: eraOrder, label: null },
  color: {
    legend: true,
    domain: componentOrder,
    scheme: "tableau10"
  },
  marks: [
    Plot.barX(eraComp, {
      x: "count",
      y: "dict",
      fx: "era",
      fill: "component",
      tip: {
        format: {
          count: (d) => d.toLocaleString()
        }
      }
    })
  ]
}));
```

```js
display(csvDownloadButton(eraComp, "correction-front-era-component.csv"));
```

## Monthly front — pick a dictionary

Month × component stream for one top dictionary. Spikes are usually batch
ingest or focused proofreading campaigns, not a smooth editorial rate.

```js
const dictPick = view(Inputs.select(dictOrder, { value: dictOrder[0], label: "dictionary" }));
```

```js
const monthlyOne = data.monthly.filter((r) => r.dict === dictPick);
```

```js
display(Plot.plot({
  marginLeft: 48,
  width: Math.min(width, 960),
  height: 320,
  x: { type: "band", label: "month", tickRotate: -60 },
  y: { label: "events", grid: true },
  color: { legend: true, domain: componentOrder, scheme: "tableau10" },
  marks: [
    Plot.barY(monthlyOne, {
      x: "month",
      y: "count",
      fill: "component",
      tip: true
    })
  ]
}));
```

```js
display(csvDownloadButton(monthlyOne, `correction-front-monthly-${dictPick}.csv`));
```

## Component inventory (whole corpus)

```js
const compRows = Object.entries(data.components).map(([component, count]) => ({ component, count }));
display(Inputs.table(compRows, { rows: 12 }));
display(csvDownloadButton(compRows, "correction-front-components.csv"));
```

## Dictionary ranking (full corpus)

```js
display(Inputs.table(data.dictRanking, { rows: 20 }));
display(csvDownloadButton(data.dictRanking, "correction-front-dict-ranking.csv"));
```

_Dr. Mārcis Gasūns_
