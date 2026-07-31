---
title: Citation truncation & hapax overlap
toc: false
---

# Citation truncation & hapax overlap

Headword containment says the Petersburg dictionaries and Monier-Williams share
an enormous amount of stock, but containment is symmetric — it cannot say **who
copied whom**. This page carries the asymmetric test named in
[`docs/LEXICOGRAPHY_ROADMAP.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/LEXICOGRAPHY_ROADMAP.md)
§"Citation truncation patterns" (hypothesis **PET-MW-CITE**): a dictionary can
*shorten* an ancestor's reference — PWG `Rv. 1.22.16` → MW `RV.` — but it cannot
invent locator precision it never had. On the sources both sides cite, the more
specific side is the plausible ancestor.

Beside it sits the content-side half: **hapax overlap**. A shared *common* lemma
is evidence of nothing — every Sanskrit dictionary has *agni*. A lemma recorded
by exactly two of these dictionaries and by no other is the rare-stock analogue
of a shared error.

```js
const data = FileAttachment("../data/lexico/citation_truncation_hapax.json").json();
```

```js
import * as Plot from "npm:@observablehq/plot";
import { csvDownloadButton } from "../lib/csv-download.js";
```

```js
const dicts = data.perDictionary;
const pairs = data.pairs;
const labelOf = new Map(dicts.map(d => [d.code, d.label]));
const relationLabel = {
  "cross-lane": "Petersburg ↔ MW",
  "within-petersburg": "control (within Petersburg)",
  "within-mw": "control (within MW)"
};
```

## Apparatus style, before any pair is formed

Locator depth is the number of numeric or i/v/x roman components a citation
carries after its siglum: `RV.` = 0, `RV. i, 1` = 2, `Rv. 1.22.16` = 3. The two
lanes are separated by this alone.

```js
const depthRows = dicts.flatMap(d =>
  Object.entries(d.depthHistogram).map(([depth, row]) => ({
    dict: d.label,
    depth: Number(depth) >= 4 ? "4+" : depth,
    share: row.share,
    citations: row.citations
  })));
const depthCollapsed = [...depthRows.reduce((map, r) => {
  const key = `${r.dict}|${r.depth}`;
  const prev = map.get(key);
  map.set(key, prev ? { ...prev, share: prev.share + r.share, citations: prev.citations + r.citations } : r);
  return map;
}, new Map()).values()];
display(Plot.plot({
  height: 60 + dicts.filter(d => d.citationsUsable > 0).length * 34,
  marginLeft: 70,
  x: { label: "share of usable citations →", percent: true, grid: true },
  y: { domain: dicts.filter(d => d.citationsUsable > 0).map(d => d.label), label: null },
  color: { domain: ["0", "1", "2", "3", "4+"], range: ["#e45756", "#f2a488", "#b3c7d6", "#6b9ac4", "#2f5d8a"], legend: true, label: "locator depth" },
  marks: [
    Plot.barX(depthCollapsed, { y: "dict", x: "share", fill: "depth",
      title: d => `${d.dict}: depth ${d.depth} — ${d.citations.toLocaleString()} citations (${(d.share * 100).toFixed(1)}%)` }),
    Plot.ruleX([0])
  ]
}));
```

> MW leaves **${(data.findings.mwBareSiglumShare * 100).toFixed(1)}%** of its
> citations at a bare siglum, against
> **${(data.findings.pwgBareSiglumShare * 100).toFixed(1)}%** for PWG.
> Truncation is not a rare event in MW — it is MW's default.

## The per-dictionary census

```js
const censusRows = dicts.map(d => ({
  dictionary: d.label,
  lane: d.lane,
  entries: d.entries,
  headwords: d.headwords,
  "raw <ls>": d.citationsRaw,
  usable: d.citationsUsable,
  "elliptical (no siglum)": d.citationsContinuation,
  "non-text markers": d.citationsNontext,
  sources: d.distinctSources,
  "mean locator depth": d.meanLocatorDepth ?? "—",
  "bare-siglum share": d.bareSiglumShare ?? "—"
}));
display(Inputs.table(censusRows, { rows: censusRows.length + 1, layout: "auto" }));
```

```js
display(csvDownloadButton(censusRows, "citation-truncation-census.csv"));
```

```js
{
  const excluded = data.scope.excludedDictionaries;
  if (excluded.length) {
    const box = document.createElement("div");
    box.className = "note";
    const head = document.createElement("p");
    head.style.margin = "6px 0";
    head.style.fontWeight = "600";
    head.textContent = "Honest shrinkage — dictionaries the citation half cannot reach";
    box.appendChild(head);
    for (const d of excluded) {
      const el = document.createElement("p");
      el.style.margin = "6px 0";
      el.textContent = `${d.label}: ${d.reason}`;
      box.appendChild(el);
    }
    display(box);
  }
}
```

## Truncation asymmetry — the directional test

Each row is one dictionary pair. `evidence(A→B)` is the count of A's citations,
on the sources both cite at least ${data.pairs.find(p => p.citation)?.citation.minCitationsPerSide ?? 5}
times each, whose locator depth exceeds B's mean depth for that same source.
**The within-lane rows are controls** — descent is not in question there, so
they show what the measure reads on ordinary house-style difference.

```js
const asymRows = pairs.filter(p => p.citation).map(p => ({
  pair: p.pair,
  kind: relationLabel[p.relation] ?? p.relation,
  "shared sources": p.citation.sharedSources,
  "evidence A→B": p.citation.truncationEvidenceAB,
  "rate A→B": p.citation.truncationRateAB,
  "evidence B→A": p.citation.truncationEvidenceBA,
  "rate B→A": p.citation.truncationRateBA,
  asymmetry: p.citation.asymmetry,
  "more specific": p.citation.moreSpecific === "tied" ? "tied" : labelOf.get(p.citation.moreSpecific)
}));
display(Plot.plot({
  height: 60 + asymRows.length * 34,
  marginLeft: 110,
  x: { label: "asymmetry  rate(A→B) − rate(B→A) →", grid: true, domain: [-1, 1] },
  y: { domain: asymRows.map(r => r.pair), label: null },
  color: { domain: [...new Set(asymRows.map(r => r.kind))], range: ["#4c78a8", "#bab0ac", "#9c755f"], legend: true },
  marks: [
    Plot.barX(asymRows, { y: "pair", x: "asymmetry", fill: "kind",
      title: d => `${d.pair}: asymmetry ${d.asymmetry} — ${d["more specific"]} is the more specific side\n${d["evidence A→B"].toLocaleString()} vs ${d["evidence B→A"].toLocaleString()} citations over ${d["shared sources"]} shared sources` }),
    Plot.ruleX([0])
  ]
}));
```

```js
display(Inputs.table(asymRows, { rows: asymRows.length + 1, layout: "auto" }));
```

```js
display(csvDownloadButton(asymRows, "citation-truncation-asymmetry.csv"));
```

> ${data.interpretation[2] ?? ""}

## Where the truncation happens — per shared source

Pick a pair to see the sources behind its number: how often each side cites the
source and how deep its locators run. A positive delta means the first
dictionary is the more specific one on that source.

```js
const citationPairs = pairs.filter(p => p.citation);
const chosen = view(Inputs.select(citationPairs, {
  label: "Pair",
  format: p => `${p.pair} — ${relationLabel[p.relation] ?? p.relation}`,
  value: citationPairs.find(p => p.a === "pwg" && p.b === "mw") ?? citationPairs[0]
}));
```

```js
const sourceRows = chosen.citation.topSources.map(s => ({
  source: s.name ?? s.source,
  siglum: s.source,
  [`citations ${chosen.labelA}`]: s.citationsA,
  [`citations ${chosen.labelB}`]: s.citationsB,
  [`mean depth ${chosen.labelA}`]: s.meanDepthA,
  [`mean depth ${chosen.labelB}`]: s.meanDepthB,
  "depth delta": s.depthDelta
}));
display(Inputs.table(sourceRows, { rows: 15, layout: "auto" }));
```

```js
display(csvDownloadButton(() => sourceRows, `citation-truncation-sources-${chosen.a}-${chosen.b}.csv`));
```

```js
display(Plot.plot({
  height: 340,
  marginLeft: 56,
  x: { label: `mean locator depth — ${chosen.labelA} →`, grid: true },
  y: { label: `mean locator depth — ${chosen.labelB} →`, grid: true },
  marks: [
    Plot.line([[0, 0], [4, 4]], { stroke: "var(--theme-foreground-muted)", strokeDasharray: "4,4" }),
    Plot.dot(chosen.citation.topSources, {
      x: "meanDepthA", y: "meanDepthB", r: d => Math.sqrt(d.citationsA + d.citationsB) / 4, fill: "#4c78a8", fillOpacity: 0.7,
      title: d => `${d.name ?? d.source}\n${chosen.labelA} ${d.citationsA.toLocaleString()} cites, depth ${d.meanDepthA}\n${chosen.labelB} ${d.citationsB.toLocaleString()} cites, depth ${d.meanDepthB}`
    })
  ]
}));
```

> Points below the diagonal are sources the first dictionary cites more
> precisely. The dot area is the pair's combined citation volume for that
> source, so a big dot far below the line is where the truncation claim carries
> the most weight.

## Hapax overlap — the rare-stock half

`shared hapax(A,B)` counts lemmas recorded by exactly two of the in-scope
dictionaries, and those two are A and B. `rare Jaccard` restricts both sets to
lemmas in at most two dictionaries; `rare/all` is its ratio to the all-headword
Jaccard, which is structurally ≤ 1 — read it as how much of the pair's agreement
survives when common stock is removed, not as a lift.

```js
const hapaxScope = view(Inputs.radio(["all headwords", "shared-source headwords"], {
  label: "Headword scope", value: "all headwords"
}));
```

```js
const scopeKey = hapaxScope === "all headwords" ? "all" : "citedShared";
const hapaxRows = pairs
  .filter(p => p.hapax[scopeKey])
  .map(p => {
    const h = p.hapax[scopeKey];
    return {
      pair: p.pair,
      kind: relationLabel[p.relation] ?? p.relation,
      [`headwords ${p.labelA}`]: h.headwordsA,
      [`headwords ${p.labelB}`]: h.headwordsB,
      intersection: h.intersection,
      Jaccard: h.jaccard,
      "shared hapax": h.sharedHapax,
      "hapax % of intersection": h.sharedHapaxShareOfIntersection,
      "rare Jaccard": h.rareJaccard,
      "rare/all": h.rareVsAllJaccard
    };
  });
display(Inputs.table(hapaxRows, { rows: hapaxRows.length + 1, layout: "auto" }));
```

```js
display(csvDownloadButton(() => hapaxRows, `citation-truncation-hapax-${scopeKey}.csv`));
```

```js
display(Plot.plot({
  height: 60 + hapaxRows.length * 34,
  marginLeft: 110,
  x: { label: "shared hapax — lemmas recorded by this pair and no other in-scope dictionary →", grid: true },
  y: { domain: hapaxRows.map(r => r.pair), label: null },
  color: { domain: [...new Set(hapaxRows.map(r => r.kind))], range: ["#4c78a8", "#bab0ac", "#9c755f"], legend: true },
  marks: [
    Plot.barX(hapaxRows, { y: "pair", x: "shared hapax", fill: "kind",
      title: d => `${d.pair}: ${d["shared hapax"].toLocaleString()} shared hapax of ${d.intersection.toLocaleString()} shared headwords` }),
    Plot.ruleX([0])
  ]
}));
```

> ${data.interpretation[data.interpretation.length - 1] ?? ""}

## Chart Trust Block

- Claim: ${data.claim} (`${data.evidenceLabel}`).
- Evidence label: `${data.evidenceLabel}` — deterministic parse of `<ls>` tags
  and `<k1>` headwords in csl-orig v02; no model inference anywhere on this page.
- Source files: csl-orig v02 `{pwg, pw, pwkvn, mw, mw72}`;
  [`src/data/dicts/dict-source-aliases.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/dict-source-aliases.json)
  (the reviewed canonical-siglum alias table, shared with the citation
  apparatus); [`src/data/mw-source-layers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/mw-source-layers.json)
  (the editorial-marker list).
- Generated by: `npm run build-citation-truncation` →
  [`data/lexico/citation_truncation_hapax.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/citation_truncation_hapax.json)
  (+ `.source.json` provenance envelope with the csl-orig commit).
- Statistics: none inferential. Every number here is a count, a mean, a rate or
  a Jaccard — there is no significance test, because with
  ${data.findings.crossLanePairsTested} testable cross-lane pairs there is
  nothing to test against. The **within-lane control pairs** carry the
  falsification load instead.
- Validation: `npm run validate-citation-truncation` (count/rate/asymmetry
  coherence, verdict-vs-asymmetry consistency, shrinkage checked in both
  directions, per-source floor, hapax set algebra, plus a live PWKVN
  re-derivation when csl-orig is present); `npm test`; `npm run build`.
- Known limits: locator depth measures **formatting** specificity, not
  scholarship — MW's compression is editorial policy as much as descent. Full
  list below.
- Review status: `${data.reviewStatus}` — the lane assignment is documented
  genealogy (title pages, L0 layer), not inferred here.
- Owner repo: `${data.ownerRepo}`. Hypothesis: **${data.hypothesis}** in
  [`docs/HYPOTHESIS_INDEX.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md).
- Next action: recompute hapax rarity against the 44-dictionary base
  (OBS-R `data/obs/headword_collapse.json` lane) so "recorded by no other
  dictionary" is a corpus claim rather than a five-dictionary floor; and extend
  the alias table so more sources survive into the shared set.
- Boundary note: dictionary citations and headwords only. csl-orig is read,
  never written.

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

Generated by `npm run build-citation-truncation`. See
[`docs/LEXICOGRAPHY_ROADMAP.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/LEXICOGRAPHY_ROADMAP.md)
§"Citation truncation patterns" and
[`docs/HYPOTHESIS_INDEX.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md)
(PET-MW-CITE). CC-BY-SA-4.0.
