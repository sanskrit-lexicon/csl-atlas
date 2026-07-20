---
title: PD × DCS corpus coverage
toc: false
---

# What share of the Poona Dictionary's canon does DCS cover?

The **Poona Dictionary** (PD, *An Encyclopaedic Dictionary of Sanskrit on Historical
Principles*) cites its sources by siglum — a de-facto declaration of the Sanskrit literary
canon. The **Digital Corpus of Sanskrit** (DCS) is the largest lemmatised Sanskrit corpus.
This page measures one against the other, for PD's published **a-** volumes. Full write-up:
[PD_DCS_CORPUS_COVERAGE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md).

```js
const metrics = FileAttachment("../data/pd/pd_dcs_metrics.json").json();
const crosswalk = FileAttachment("../data/pd/pd_dcs_text_crosswalk.tsv").tsv({typed: true});
const residue = FileAttachment("../data/pd/pd_dcs_residue_top.tsv").tsv({typed: true});
```

```js
function tile(label, value, sub) {
  return htl.html`<div style="border:1px solid var(--theme-foreground-faint);border-radius:8px;padding:0.75rem 1rem">
    <div style="font-size:0.8rem;color:var(--theme-foreground-muted)">${label}</div>
    <div style="font-size:1.9rem;font-weight:700;line-height:1.1">${value}</div>
    <div style="font-size:0.8rem;color:var(--theme-foreground-muted)">${sub}</div>
  </div>`;
}
```

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:0.75rem;margin:1rem 0">
${tile("PD-citation-weighted", metrics.metric_pd_citation_weighted_pct + "%", "of what PD cites is in DCS")}
${tile("Title-level", "~2.4–4.8%", metrics.n_covered_dcs_titles + " of ~" + metrics.n_primary_works_skeleton_estimate + " works")}
${tile("DCS-token-weighted (2026)", metrics.metric_dcs_token_weighted_2026_pct + "%", "of DCS's mass is PD-cited")}
${tile("DCS-token-weighted (2021)", metrics.metric_dcs_token_weighted_2021_pct + "%", "+3.8 pp by 2026")}
</div>

**The two headline numbers diverge on purpose.** DCS holds only a **quarter** of PD's
citation practice (metric 1) yet its **own bulk is 78 % PD-cited** (metric 3): DCS is a deep
sample of the archaic/classical *core* PD leans on, not of PD's encyclopedic *breadth*.

## Where PD's citation mass goes

```js
const massData = [
  {band: "Covered by DCS", occ: metrics.covered_mass, kind: "covered"},
  {band: "Residue (not in DCS)", occ: metrics.residue_mass, kind: "residue"},
  {band: "Secondary scholarship", occ: metrics.secondary_mass, kind: "secondary"},
  {band: "Structural / grammatical", occ: metrics.structural_mass, kind: "structural"}
];
```

```js
Plot.plot({
  marginLeft: 170,
  x: {label: "PD siglum occurrences (a- volumes)", grid: true},
  y: {label: null},
  color: {domain: ["covered","residue","secondary","structural"],
          range: ["#2c7fb8","#d95f0e","#7a7a7a","#bdbdbd"], legend: false},
  marks: [
    Plot.barX(massData, {x: "occ", y: "band", fill: "kind", sort: {y: "-x"}}),
    Plot.text(massData, {x: "occ", y: "band", text: d => d.occ.toLocaleString(),
                         dx: 4, textAnchor: "start"}),
    Plot.ruleX([0])
  ]
})
```

## Top residue — PD works DCS does not hold

The purāṇas, the lexicographic tradition (kośa), classical kāvya, and the grammatical
commentary layer. The single largest item (Padmapurāṇa, 3,506) outweighs all but three
*covered* texts.

```js
Plot.plot({
  marginLeft: 200,
  height: 640,
  x: {label: "PD citations", grid: true},
  y: {label: null},
  marks: [
    Plot.barX(residue, {x: "pd_citations", y: "work", fill: "#d95f0e", sort: {y: "-x"}}),
    Plot.ruleX([0])
  ]
})
```

## Covered DCS texts, by PD citation frequency

```js
Plot.plot({
  marginLeft: 220,
  height: 720,
  x: {label: "PD citations", grid: true},
  y: {label: null},
  marks: [
    Plot.barX(crosswalk, {x: "pd_citations", y: "dcs_title", fill: "#2c7fb8",
                          sort: {y: "-x", limit: 40}}),
    Plot.ruleX([0])
  ]
})
```

## Trust Block

- **Evidence.** PD sigla harvested from
  [pd.txt](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/external_src/pd/pd.txt)
  (107,630 entries, 398,359 citation occurrences); DCS inventory + token counts from
  [VisualDCS Corpus-Delta 2021–2026](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Corpus-Delta-2021-2026/per_text_token_delta.csv)
  (276 texts). n and dates are on every artifact.
- **Method.** Anchored on DCS's bounded 276-text set; every siglum carries an adjudicated
  `match_type` (covered / residue / secondary / structural). Scripts:
  [pd_extract_sigla.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_extract_sigla.py),
  [pd_dcs_crosswalk.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_dcs_crosswalk.py).
- **Limitations.** PD is published under letter **a-** only (6 of 37+ volumes), so these are
  PD's sources *as exercised under a-*, not its full canon. Siglum→title expansion is
  Opus-adjudicated, not sourced from PD's printed abbreviation list. See the report's §6.
- **Owner repo.** `csl-atlas`. Data:
  [data/pd/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/pd).
- **Download.** [Covered-text crosswalk (TSV)](../data/pd/pd_dcs_text_crosswalk.tsv) ·
  [Top residue (TSV)](../data/pd/pd_dcs_residue_top.tsv) ·
  [Metrics (JSON)](../data/pd/pd_dcs_metrics.json).

## Covered-text crosswalk (data table)

```js
Inputs.table(crosswalk, {
  columns: ["dcs_title","pd_sigla","pd_citations","dcs_tok_2026","dcs_chapters","coverage_grade"],
  header: {dcs_title: "DCS text", pd_sigla: "PD siglum", pd_citations: "PD cites",
           dcs_tok_2026: "DCS tokens (2026)", dcs_chapters: "DCS chapters",
           coverage_grade: "grade"},
  sort: "pd_citations", reverse: true
})
```
