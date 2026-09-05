_Created: 26-07-2026 · Last updated: 05-09-2026_

---
title: Orthographic drift explorer
toc: false
---

# Orthographic drift explorer

The first atlas page about the **gloss languages themselves**: pre-reform German
(*Thier → Tier*) and pre-1918 Russian (*въ → в*) spellings in the dictionary
gloss text, counted against the frozen
[SanskritSpellCheck reform maps](https://github.com/drdhaval2785/SanskritSpellCheck/tree/master/ortho_drift)
and read as a **dating and descent signal** (PH5 ORTHO-CLOCK, agenda §2/§3 V5).

It answers two testable questions — **(i) the clock**: does pre-reform density
fall monotonically with publication date across PWG → PW → Nachträge → Schmidt?
**(ii) descent**: do declared descendants carry *elevated* fossil orthography
relative to date-matched independents, because copied German glosses carry the
parent's spellings?

> This is the **meta-language layer** — how the lexicographers spelled their
> German and Russian, not how they recorded Sanskrit. The Sanskrit-side house
> style lives on the [Convention fingerprints](lexicographic-conventions) page.

```js
const data = FileAttachment("../data/lexico/ortho_drift.json").json();
```

```js
import * as Plot from "npm:@observablehq/plot";
import { csvDownloadButton } from "../lib/csv-download.js";
```

```js
const de = data.german.dicts;
const reg = data.german.regression;
const lineageColor = {
  domain: ["progenitor", "descendant", "independent"],
  range: ["#4c78a8", "#f58518", "#54a24b"],
  legend: true
};
const clockLabel = {
  "supported": "Supported",
  "direction-consistent-inconclusive": "Direction-consistent, inconclusive at n",
  "not-supported": "Not supported"
}[data.verdict.clock] ?? data.verdict.clock;
const descentLabel = { supported: "Supported", refuted: "Refuted", untestable: "Untestable" }[data.verdict.descent] ?? data.verdict.descent;
```

## Verdicts — clock: ${clockLabel} · descent: ${descentLabel}

```js
{
  const box = document.createElement("div");
  box.className = "note";
  box.style.borderLeft = "3px solid var(--theme-foreground-focus)";
  box.style.paddingLeft = "12px";
  for (const text of [data.verdict.clockDetail, data.verdict.eraCompositionDetail, data.verdict.descentDetail]) {
    const el = document.createElement("p");
    el.style.margin = "6px 0";
    el.textContent = text;
    box.appendChild(el);
  }
  display(box);
}
```

## Drift vs year — the German census

Each point is one dictionary: dated-reform pre-1901/1996 spellings per 1,000
German gloss tokens, at the inventory mid-year of its publication span, with
entry-level bootstrap 95% CIs (often narrower than the dot). The dashed line is
the descriptive OLS fit (Spearman ρ ${reg.spearmanRho}, exact permutation
p ${reg.spearmanExactPTwoSided} over all ${reg.spearmanPermutations.toLocaleString()} orderings).

```js
const fitLine = [1860, 1930].map((year) => ({ year, drift: reg.intercept + reg.slopePer1kPerYear * year }));
display(Plot.plot({
  height: 340,
  marginLeft: 56,
  x: { label: "publication mid-year →", domain: [1858, 1935], tickFormat: "d" },
  y: { label: "dated pre-reform spellings / 1,000 tokens", grid: true, domain: [0, 20] },
  color: lineageColor,
  marks: [
    Plot.line(fitLine, { x: "year", y: "drift", stroke: "var(--theme-foreground-muted)", strokeDasharray: "4,4" }),
    Plot.ruleX(de, { x: "midYear", y1: d => d.ci.driftPer1k[0], y2: d => d.ci.driftPer1k[1], stroke: "lineage", strokeWidth: 1.5 }),
    Plot.dot(de, { x: "midYear", y: "driftPer1k", fill: "lineage", r: 6,
      title: d => `${d.label} (${d.startYear}–${d.endYear ?? d.startYear}, ${d.lineage})\n${d.driftPer1k}/1k dated · ${d.driftPer1kAllMap}/1k all-map\n${d.tokens.toLocaleString()} tokens` }),
    Plot.text(de, { x: "midYear", y: "driftPer1k", text: "label", dy: -12, fontSize: 11, fontWeight: 600 }),
    Plot.ruleY([0])
  ]
}));
```

> The pattern is sharper than a date clock: the **Böhtlingk lane stays uniformly
> fossil** (PWG 14.8 → PW 17.5 → PWKVN 17.1 per 1k — his *kürzere Fassung* of
> 1879–89 is even more pre-reform than the 1855–75 original), while the
> **non-Böhtlingk dictionaries modernise with date** (GRA 10.4, CCS 6.5,
> SCH 4.8). Pre-reform density is a **house-style clock**, not a pure
> publication-date clock.

## Era composition — each dictionary's orthographic epoch

Which reform regime dominates each dictionary's dated fossils. Every
19th-century dictionary is 1901-reform-dominated (*th → t*, *c → k/z*); Schmidt
(1928) flips to 1996-*ß*-dominated with the 1901 signal collapsed — his epoch is
readable from his own gloss text.

```js
const eraRows = de.flatMap(d => [
  { dict: d.label, regime: "1901 reforms (th→t, c→k/z, -iren)", share: d.eraProfile?.share1901 ?? 0 },
  { dict: d.label, regime: "1996 reform (ß→ss)", share: d.eraProfile?.share1996ss ?? 0 }
]);
display(Plot.plot({
  height: 60 + de.length * 30,
  marginLeft: 70,
  x: { label: "share of dated pre-reform hits →", percent: true, grid: true },
  y: { domain: de.map(d => d.label), label: null },
  color: { domain: eraRows.map(r => r.regime).filter((v, i, a) => a.indexOf(v) === i), range: ["#4c78a8", "#e45756"], legend: true },
  marks: [
    Plot.barX(eraRows, { y: "dict", x: "share", fill: "regime",
      title: d => `${d.dict}: ${(d.share * 100).toFixed(1)}% ${d.regime}` }),
    Plot.ruleX([0])
  ]
}));
```

## The census table

```js
const censusRows = de.map(d => ({
  dict: d.label,
  span: `${d.startYear}–${d.endYear ?? d.startYear}`,
  lineage: d.lineage,
  entries: d.entries,
  "gloss tokens": d.tokens,
  "dated drift/1k": d.driftPer1k,
  "95% CI": `[${d.ci.driftPer1k[0]}, ${d.ci.driftPer1k[1]}]`,
  "all-map drift/1k": d.driftPer1kAllMap,
  "pre-share (pre/(pre+post))": d.preShare,
  "distinct old forms": d.distinctPreForms,
  "form overlap with PWG": d.fossilOverlapWithPwg ?? "—"
}));
display(Inputs.table(censusRows, { rows: de.length + 1, layout: "auto" }));
```

```js
display(csvDownloadButton(censusRows, "ortho-drift-census.csv"));
```

## The descent contrast — refuted, and honestly bounded

With exactly **one** independent German dictionary in the corpus (GRA), no
group-level permutation test is identifiable; the descent claim is tested as
directional entry-level pair contrasts:

```js
const pairRows = data.german.pairTests.map(t => ({
  contrast: `${t.a.toUpperCase()} → ${t.b.toUpperCase()}`,
  claim: t.claim,
  "Δ dated drift/1k (b−a)": t.diffPer1k,
  "one-sided p": t.pOneSided,
  direction: t.direction
}));
display(Inputs.table(pairRows, { rows: pairRows.length, layout: "auto", width: { claim: 420 } }));
```

```js
display(csvDownloadButton(pairRows, "ortho-drift-pair-tests.csv"));
```

> Cappeller declared CCS "nach den Petersburger Wörterbüchern bearbeitet", yet
> his 1887 German is **less** pre-reform than the *independent* GRA of 1873 —
> copying Petersburg content did not copy Petersburg spelling. Orthography
> follows the **editor's own decade and house style**, not the source text. The
> form-overlap column above says the same thing gently: even GRA (independent)
> shares 71% of its drifted forms with PWG, because the same high-frequency
> German words (*Theil*, *thun*, *Thier*) drift everywhere — fossil *forms* are
> shared German, not a descent fingerprint.

## Top drifted forms — the searchable fossil list

The dated-reform fossils across all six dictionaries (old form · modern form ·
reform era · per-dictionary counts). Search matches old and modern forms. The
era-unattributed corpus-mined map rows are excluded from this showcase (they
remain in the all-map counts above).

```js
const formRows = data.german.topForms.map(f => ({
  old: f.old,
  modern: f.modern,
  era: f.era,
  total: f.total,
  PWG: f.pwg, GRA: f.gra, PWK: f.pw, PWKVN: f.pwkvn, CCS: f.ccs, SCH: f.sch
}));
```

```js
const formSearch = view(Inputs.search(formRows, { placeholder: "Search Thier, Teil, blüthe…" }));
```

```js
display(Inputs.table(formSearch, { rows: 15, layout: "auto", sort: "total", reverse: true }));
```

```js
display(csvDownloadButton(() => formSearch, "ortho-drift-top-forms.csv"));
```

> **Learner read.** This table is why searching PWG for modern German fails:
> PWG never writes *Teil*, it writes *Theil* (1,245× across the roster). To
> search 19th-century German glosses, de-reform your query: *t* → *th* inside
> Erbwörter, *k/z* → *c* in Latinate words, *ss* → *ß*. The CSV doubles as a
> query-normalisation map.

## Russian — Kossovich, the radical-reform case

```js
const ru = data.russian.dicts[0];
```

The 1918 Russian reform abolished whole letters (ѣ, і, ѳ, ѵ, word-final ъ), so
pre-reform Russian is detectable **by definition**, wordlist-free. Kossovich
(1854) runs at **${ru ? ru.driftPer1k : "—"} per 1,000 tokens** — roughly
${ru ? Math.round(ru.driftPer1k / 10) : "—"}% of all Russian gloss tokens, an
order of magnitude past the German maximum (${Math.max(...de.map(d => d.driftPer1k))}/1k),
because the hard-sign rule alone touches nearly every masculine noun.

```js
if (ru) {
  const ruRows = [{
    dict: ru.label,
    year: ru.year,
    entries: ru.entries,
    "gloss tokens": ru.tokens,
    "drift/1k": ru.driftPer1k,
    "95% CI": `[${ru.ci.driftPer1k[0]}, ${ru.ci.driftPer1k[1]}]`,
    "pre-share": ru.preShare,
    "map hits": ru.preHitsAllMap,
    "definitional hits (letter test)": ru.definitionalHits
  }];
  display(Inputs.table(ruRows, { rows: 2, layout: "auto" }));
  display(csvDownloadButton(ruRows, "ortho-drift-russian.csv"));
}
```

```js
if (data.russian.topForms.length) {
  const ruForms = data.russian.topForms.map(f => ({ old: f.old, modern: f.modern, era: f.era, count: f.count }));
  display(Inputs.table(ruForms, { rows: 10, layout: "auto" }));
  display(csvDownloadButton(ruForms, "ortho-drift-russian-forms.csv"));
}
```

> ${data.russian.note}

## Chart Trust Block

- Claim: pre-reform gloss-language spelling density and era composition, per
  dictionary, as a dating/descent signal — clock **${clockLabel}**, descent
  **${descentLabel}** (`derived`).
- Evidence label: `derived` — deterministic map-membership census over csl-orig
  gloss text; no model inference on this page.
- Source files: [`de_reform_map.tsv`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/ortho_drift/de_reform_map.tsv)
  (${data.german.referenceMap.forms.toLocaleString()} pairs) ·
  [`ru_reform_map.tsv`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/ortho_drift/ru_reform_map.tsv)
  (${data.russian.referenceMap.forms.toLocaleString()} pairs) — owned by
  SanskritSpellCheck (A37 lane), consumed frozen; csl-orig v02 gloss text
  (pwg, gra, pw, pwkvn, ccs, sch); SamudraManthanam `kossovich.jsonl`.
- Generated by: `npm run build-ortho-drift` →
  [`data/lexico/ortho_drift.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/ortho_drift.json)
  (+ `.source.json` provenance envelope with sibling commits).
- Statistics: entry-level bootstrap 95% CIs (B=1,000, fixed-seed mulberry32);
  exhaustive n!-permutation Spearman for the tiny-n date regression; directional
  entry-level permutation pair tests (B=1,000) — Dror et al. 2018 protocol,
  Bollmann 2019 framing for historical normalisation.
- Validation: `npm run validate-ortho-drift` (rate/share/era-sum coherence, CI
  bracketing, residuals-vs-fit, verdict-vs-statistics consistency, live map
  row-count cross-check when the sibling checkout is present); `npm test`;
  `npm run build`.
- Known limits: the meta-language axis dates the **editing**, not the Sanskrit;
  map-membership counting undercounts unmapped inflected drift; the
  era-unattributed map rows are excluded from the headline clock. Full list
  below.
- Review status: machine-reviewed; the lineage labels (progenitor / descendant /
  independent) are documented genealogy (title pages, L0 layer), not inferred
  here.
- Owner repo: `csl-atlas`; reform maps stay upstream in SanskritSpellCheck —
  the atlas owns only this cross-dictionary census layer.
- Next action: a second independent German dictionary (outside CDSL) would make
  the descent contrast group-testable; KNA (1893) text would give Russian a
  second dated point.
- Boundary note: gloss-language orthography only — Sanskrit-side drift is
  VisualDCS territory; csl-orig is never written.

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

Generated by `npm run build-ortho-drift`. See
[`docs/ATLAS_RESEARCH_AGENDA.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ATLAS_RESEARCH_AGENDA.md)
§2 PH5 / §3 V5 / §5d and
[`docs/HYPOTHESIS_INDEX.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md).
CC-BY-SA-4.0.

_Dr. Mārcis Gasūns_
