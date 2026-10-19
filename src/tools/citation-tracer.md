_Created: 23-05-2026 · Last updated: 19-10-2026_

---
title: Citation tracer
---

# Citation tracer

Follow a cited source back to the **MW entries that cite it**, and from an explicit
Ṛgveda locus out to the passage in a stable external edition. This is the entry-level
counterpart of the frequency graph on [citation-canon](/tools/citation-canon): the graph
says *how often* a text is cited; this page says *where*.

```js
const sourceIndex = FileAttachment("../data/citations/source-to-entries.json").json();
const passagePilot = FileAttachment("../data/citations/citation-passage-links.json").json();
```

```js
const sourceLabels = Object.keys(sourceIndex.sources);
const source = view(Inputs.select(sourceLabels, { label: "Source (canonical label)", value: "Ṛgveda" }));
const filter = view(Inputs.text({ label: "Filter L records", placeholder: "e.g. 3873 or 13832" }));
```

```js
const picked = sourceIndex.sources[source];
const needle = filter.trim();
const records = picked.records
  .filter(L => !needle || L.includes(needle) || String(picked.lines[L] ?? "").includes(needle))
  .slice(0, 200);
const pilotForSource = passagePilot.items.filter(item => item.canonicalText === source);
```

```js
display(html`<div class="citation-summary">
  <div><b>${source}</b></div>
  <div>${picked.citations.toLocaleString()} citations · ${picked.entryCount.toLocaleString()} MW <code>&lt;L&gt;</code> records</div>
  <div>raw MW forms: ${Object.entries(picked.rawForms).map(([form, n]) => html`<span><code>${form}</code> (${n.toLocaleString()}) </span>`)}</div>
</div>`);
```

```js
display(html`<div class="warning" label="What this is">
  Source-to-entry links are derived from MW's <code>&lt;ls&gt;</code> tags and the MWS
  abbreviation table. They tell you which entry cites the source, not which quoted words
  match which passage. ${sourceIndex.counts.indexedCitations.toLocaleString()} of
  ${sourceIndex.counts.citations.toLocaleString()} MW citations resolve to one of
  ${sourceIndex.counts.canonicalSources} canonical source labels; unresolved and editorial
  markers are reported in <a href="https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/source-to-entries.json" target="_blank" rel="noopener">the data file</a>.
</div>`);
```

```js
display(html`<table class="cited-table">
  <thead><tr><th>L record</th><th>MW source line</th><th>Open</th></tr></thead>
  <tbody>${records.map(L => {
    const line = picked.lines[L];
    return html`<tr><td><code>${L}</code></td><td>${line ? line.toLocaleString() : "—"}</td><td>${line ? html`<a href="../source#mw/${line}">source line</a>` : "—"}</td></tr>`;
  })}</tbody>
</table>
${picked.records.length > records.length ? html`<p class="muted">Showing ${records.length} of ${picked.records.length.toLocaleString()} records.</p>` : ""}`);
```

## Passage pilot — Ṛgveda to GRETIL

MW writes Ṛgveda loci explicitly (`RV. v, 86, 5` = maṇḍala 5, hymn 86, verse 5), so no
alignment is needed: parse the locus and link to GRETIL's per-verse anchor in the Aufrecht
edition. The pilot carries the **100 most-cited distinct RV verse loci**; every link was
checked for HTTP 200 and for the presence of its `RV_<maṇḍala>.<hymn>.<verse>` anchor.

```js
const pilotRows = (pilotForSource.length ? pilotForSource : passagePilot.items).slice(0, 100);
```

```js
display(html`<div class="citation-summary">
  <div>${passagePilot.summary.verified} / ${passagePilot.summary.pilotSize} passage links verified
    (HTTP 200 ${passagePilot.summary.http200}, anchor present ${passagePilot.summary.anchorVerified})</div>
  <div>${passagePilot.summary.checkedAt ? `checked ${passagePilot.summary.checkedAt}` : "verification snapshot pending"}</div>
</div>`);
```

```js
display(html`<table class="cited-table">
  <thead><tr><th>Locus</th><th>MW citations</th><th>GRETIL passage</th><th>VedaWeb</th></tr></thead>
  <tbody>${pilotRows.map(item => html`<tr>
    <td><code>RV ${item.mandala}.${item.hymn}.${item.verse}</code></td>
    <td>${item.mwCitations}</td>
    <td><a href=${item.url} target="_blank" rel="noopener">${item.gretilId}</a> ${item.verified ? html`<span class="ok">✓</span>` : ""}</td>
    <td><a href=${item.vedawebUrl} target="_blank" rel="noopener">VedaWeb</a></td>
  </tr>`)}</tbody>
</table>`);
```

## Trust Block

- Evidence: `data/citations/source-to-entries.json` (209 canonical labels; 205,722 of 320,828 MW citations resolved) and `data/citations/citation-passage-links.json` (100 RV verse loci, all HTTP 200 with anchors present on 19-10-2026).
- Limitations: MW only; locus parsing covers explicit RV verse citations only. GRETIL is a link-out target and is not ingested. A verified anchor proves the passage exists, not that MW's quotation is accurate.
- Validation: `npm run build-citation-passage-index`, `npm run verify-citation-passage-links`, and `node --test test/citation-passage-index.test.mjs`; the page is built by `npm run build`.
- Owner repo: `csl-atlas`.
- Next use: pick a source, open the citing MW entry, then follow the RV locus to the edition.

<style>
.citation-summary { display: grid; gap: 3px; margin: 10px 0 14px; padding: 10px 12px; border-left: 4px solid var(--theme-foreground-faint); background: color-mix(in srgb, var(--theme-background), var(--theme-foreground) 3%); border-radius: 4px; }
.cited-table { border-collapse: collapse; font-size: .86rem; margin: 8px 0 18px; }
.cited-table th, .cited-table td { border-bottom: 1px solid var(--theme-foreground-faint); padding: 4px 10px; text-align: left; }
.cited-table th { color: var(--theme-foreground-muted); font-weight: 600; }
.muted { color: var(--theme-foreground-muted); }
.ok { color: #2ca02c; font-weight: 700; }
</style>

---

Data: [`source-to-entries.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/source-to-entries.json) · [`citation-passage-links.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/citation-passage-links.json) · [`data/citations/README.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/README.md). CC-BY-SA-4.0.

_Dr. Mārcis Gasūns_
