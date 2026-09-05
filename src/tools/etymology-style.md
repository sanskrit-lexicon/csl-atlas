_Created: 23-07-2026 · Last updated: 05-09-2026_

---
title: Etymology style witness
toc: false
---

# Etymology style — Nirukta markers vs Western `cf.`

A **frozen exploratory witness** of how five Cologne dictionaries mark
etymology / derivation. The claim is descriptive, not a new inference:
**WIL (1832)** still writes Nirukta-style affix notation inside `.E.` blocks
(`aff.`, `c.`, `neg.` …), while later Western editions (MW72, MW) shift to
comparativist `cf.` cross-references. Apte editions sit in between with sparse
morphology tags and almost no `cf.`.

Source probes live in
[csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) as frozen
CSVs; this atlas page only **renders** them (dictionary microstructure belongs
here per
[`BOUNDARY_RULES.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BOUNDARY_RULES.md)).
Not a full 44-dict census.

```js
import * as Plot from "npm:@observablehq/plot";
import * as d3 from "npm:d3@7";
import {csvDownloadButton} from "../lib/csv-download.js";
```

```js
function parseWitnessCsv(text) {
  const body = text
    .split(/\r?\n/)
    .filter((line) => line.length && !line.startsWith("#"))
    .join("\n");
  return d3.csvParse(body, d3.autoType);
}
```

```js
const markerText = await FileAttachment("../data/witness/etymology_marker_preliminary.csv").text();
const tokenText = await FileAttachment("../data/witness/wil_nirukta_tokens.csv").text();
const markers = parseWitnessCsv(markerText);
const tokens = parseWitnessCsv(tokenText);
```

```js
const dictOrder = markers
  .slice()
  .sort((a, b) => a.year - b.year)
  .map((d) => d.dict);
const styleColors = {
  Nirukta: "var(--theme-foreground-focus)",
  "Western-cf": "var(--theme-foreground-alt)",
  "Western-cf-plus": "var(--theme-foreground)",
  minimal: "var(--theme-foreground-faint)",
  "mixed-italic-headword": "var(--theme-foreground-muted)"
};
```

```js
function stat(label, value, sub) {
  return html`<div style="flex:1 1 140px;padding:0.8rem 1rem;border:1px solid var(--theme-foreground-faint);border-radius:8px;">
    <div style="font-size:1.6rem;font-weight:700;">${value}</div>
    <div style="font-weight:600;">${label}</div>
    <div style="opacity:0.65;font-size:0.85rem;">${sub}</div></div>`;
}
const wil = markers.find((d) => d.dict === "WIL");
const mw = markers.find((d) => d.dict === "MW");
display(html`<div style="display:flex;gap:0.8rem;flex-wrap:wrap;margin:0.5rem 0 1rem;">
  ${stat("dictionaries", markers.length, "preliminary sample")}
  ${stat("WIL Nirukta .E.", wil ? wil.nirukta_E_pct + "%" : "—", "share of entries with .E.")}
  ${stat("MW cf. hits", mw ? mw.cf_count.toLocaleString() : "—", "Western-cf-plus style")}
  ${stat("WIL top tokens", tokens.length, "abbreviations in .E. blocks")}
</div>`);
```

## Nirukta-style `.E.` share by dictionary

Percent of entries carrying a Nirukta-style etymology block (Wilson's `.E.`
notation). Only WIL is non-zero in this spike — the later sample has already
dropped the indigenous affix apparatus.

```js
display(Plot.plot({
  width: Math.min(width, 760),
  height: 280,
  marginLeft: 56,
  marginBottom: 48,
  x: {domain: dictOrder, label: null},
  y: {label: "nirukta_E_pct (%)", domain: [0, 100], grid: true},
  color: {
    domain: Object.keys(styleColors),
    range: Object.values(styleColors),
    legend: true,
    label: "etym_style"
  },
  marks: [
    Plot.barY(markers, {
      x: "dict",
      y: "nirukta_E_pct",
      fill: "etym_style",
      tip: true,
      title: (d) => `${d.dict} (${d.year}): ${d.nirukta_E_pct}% · ${d.etym_style}`
    }),
    Plot.ruleY([0])
  ]
}));
```

```js
display(csvDownloadButton(
  markers.map((d) => ({
    dict: d.dict,
    year: d.year,
    entries: d.entries,
    nirukta_E_pct: d.nirukta_E_pct,
    etym_style: d.etym_style
  })),
  "etymology-style-nirukta-pct.csv"
));
```

## Western `cf.` count by dictionary

Raw `cf.` hit counts (comparativist cross-reference style). MW72 and MW dominate;
WIL has zero in this probe.

```js
display(Plot.plot({
  width: Math.min(width, 760),
  height: 280,
  marginLeft: 56,
  marginBottom: 48,
  x: {domain: dictOrder, label: null},
  y: {label: "cf_count", grid: true},
  color: {
    domain: Object.keys(styleColors),
    range: Object.values(styleColors),
    legend: true,
    label: "etym_style"
  },
  marks: [
    Plot.barY(markers, {
      x: "dict",
      y: "cf_count",
      fill: "etym_style",
      tip: true,
      title: (d) => `${d.dict} (${d.year}): cf_count=${d.cf_count}`
    }),
    Plot.ruleY([0])
  ]
}));
```

```js
display(csvDownloadButton(
  markers.map((d) => ({
    dict: d.dict,
    year: d.year,
    cf_count: d.cf_count,
    etym_style: d.etym_style
  })),
  "etymology-style-cf-count.csv"
));
```

## Timeline — year × Nirukta `.E.` share

Connected scatter (slope chart) of the same five dictionaries by publication
year. The drop from WIL 1832 (~89%) to every later point (0%) is the visual
of the style shift; it is **not** a regression over the full CDSL set.

```js
const timeline = markers.slice().sort((a, b) => a.year - b.year);
```

```js
display(Plot.plot({
  width: Math.min(width, 760),
  height: 300,
  marginLeft: 48,
  marginBottom: 40,
  grid: true,
  x: {label: "year", type: "linear"},
  y: {label: "nirukta_E_pct (%)", domain: [0, 100]},
  color: {
    domain: Object.keys(styleColors),
    range: Object.values(styleColors),
    legend: true,
    label: "etym_style"
  },
  marks: [
    Plot.line(timeline, {
      x: "year",
      y: "nirukta_E_pct",
      stroke: "var(--theme-foreground-faint)",
      strokeWidth: 1.5
    }),
    Plot.dot(timeline, {
      x: "year",
      y: "nirukta_E_pct",
      fill: "etym_style",
      r: 6,
      tip: true,
      title: (d) => `${d.dict} ${d.year}: ${d.nirukta_E_pct}%`
    }),
    Plot.text(timeline, {
      x: "year",
      y: "nirukta_E_pct",
      text: "dict",
      dy: -12,
      fontSize: 11,
      fill: "var(--theme-foreground)"
    })
  ]
}));
```

```js
display(csvDownloadButton(
  timeline.map((d) => ({
    dict: d.dict,
    year: d.year,
    nirukta_E_pct: d.nirukta_E_pct,
    etym_style: d.etym_style
  })),
  "etymology-style-timeline.csv"
));
```

## WIL Nirukta tokens (top abbreviations)

Top tokens counted inside WIL `.E.` blocks. **`aff.`** (affix / pratyaya) alone
is ~14.7k — the indigenous derivation apparatus is affix-notation-heavy, not
`cf.`-heavy.

```js
const tokensSorted = tokens.slice().sort((a, b) => b.count - a.count);
```

```js
display(Plot.plot({
  width: Math.min(width, 760),
  height: 40 + tokensSorted.length * 22,
  marginLeft: 88,
  marginBottom: 40,
  x: {label: "count", grid: true},
  y: {domain: tokensSorted.map((d) => d.token), label: null},
  marks: [
    Plot.barX(tokensSorted, {
      x: "count",
      y: "token",
      fill: "var(--theme-foreground-focus)",
      tip: true,
      title: (d) => `${d.token}: ${d.count.toLocaleString()} — ${d.meaning}`
    }),
    Plot.ruleX([0])
  ]
}));
```

```js
display(csvDownloadButton(
  tokensSorted.map((d) => ({
    token: d.token,
    count: d.count,
    meaning: d.meaning
  })),
  "wil-nirukta-tokens.csv"
));
```

## Full tables

### Marker summary (5 dictionaries)

```js
display(Inputs.table(
  markers.slice().sort((a, b) => a.year - b.year).map((d) => ({
    dict: d.dict,
    year: d.year,
    entries: d.entries,
    nirukta_E_pct: d.nirukta_E_pct,
    cf_count: d.cf_count,
    caus: d.caus,
    pass: d.pass,
    desid: d.desid,
    freq: d.freq,
    bopp: d.bopp,
    etym_style: d.etym_style
  })),
  {rows: 10, layout: "auto"}
));
```

```js
display(csvDownloadButton(
  markers.slice().sort((a, b) => a.year - b.year),
  "etymology-marker-preliminary.csv"
));
```

### WIL token inventory

```js
display(Inputs.table(tokensSorted, {rows: 16, layout: "auto"}));
```

```js
display(csvDownloadButton(tokensSorted, "wil-nirukta-tokens-full.csv"));
```

## Chart Trust Block

- **Claim:** among a five-dictionary exploratory sample, WIL (1832) is the only
  dictionary with a high share of Nirukta-style `.E.` etymology blocks
  (~88.9%), while MW72/MW show large `cf.` counts and zero Nirukta-block share;
  WIL's top `.E.` token is `aff.` (affix).
- **Evidence label:** `derived` — deterministic token/marker counts from frozen
  observatory probes; **witness grade = exploratory spike** (not a full census,
  not a model).
- **Source files:** vendored copies under
  [`src/data/witness/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/src/data/witness)
  with provenance headers pointing at
  [`csl-observatory/data/etymology_marker_preliminary.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/etymology_marker_preliminary.csv)
  (commit `582f5337`) and
  [`csl-observatory/data/wil_nirukta_tokens.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/wil_nirukta_tokens.csv)
  (commit `8c4b78be`). **n = 5 dictionaries** / **16 WIL tokens**.
- **Generated by:** no atlas builder — FileAttachment of frozen CSVs only (H1525).
- **Validation:** `npm run build` must include this page; CSV provenance headers
  present; plot count ≥ 4.
- **Known false positives:** a `cf.` string match can hit non-etymological uses;
  morphology tags (`caus`/`pass`/`desid`) are co-present columns, not a style
  classification.
- **Known false negatives:** only five dictionaries were probed — the other ~39
  CDSL dictionaries are invisible here; orthographic reform maps (agenda V5)
  are out of scope.
- **Review status:** machine-rendered exploratory witness; **not** human-reviewed
  as a full etymology typology.
- **Owner repo:** `csl-atlas` (rendering); probes owned by `csl-observatory`.
- **Next action:** if a paper needs the style claim, extend the probe to a
  pre-registered dict set (or re-run a documented extractor) before promoting
  beyond "exploratory spike"; do **not** re-extract in-page.
- **External dependencies:**
  [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) frozen
  CSVs only (no live scrape).
- **Boundary note:** dictionary microstructure markers belong in the atlas;
  org metrics stay in the observatory
  ([`DICTIONARY_STRUCTURE_MOVED.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DICTIONARY_STRUCTURE_MOVED.md)).

## Related

- [WIL dictionary chapter](../dicts/wil) — Wilson as the base of the European line
- [Dictionary genealogy](lexicography) — content inheritance, not etymology style
- [Convention fingerprints](lexicographic-conventions) — house-style cladogram (Patel L0)
- [Structural register](structural-register) — citation × grammar family scatter
- [Lemma dossier](dictionary-dossier) — look up a headword across dictionaries

_Dr. Mārcis Gasūns_
