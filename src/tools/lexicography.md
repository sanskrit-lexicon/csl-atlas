---
title: Dictionary genealogy - first findings
toc: true
---

# Dictionary Genealogy

First empirical findings from the **lexicography research stream**. Everything here is derived from the canonical [`sanhw1.txt`](https://github.com/sanskrit-lexicon/hwnorm1/blob/master/sanhw1/sanhw1.txt) master headword index (469,844 normalised SLP1 lemmas across 41 dictionaries).

This page is companion to the [Lexicography Roadmap](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/LEXICOGRAPHY_ROADMAP.md), which lays out the broader research plan (Phases L0-L10, Papers M, L, H).

```js
const inv = await FileAttachment("../data/lexicographic-structure/dictionary_inventory.csv").csv({typed: true});
const edges = await FileAttachment("../data/lexicographic-structure/sanhw1_inheritance_edges.csv").csv({typed: true});
const distances = await FileAttachment("../data/lexicographic-structure/sanhw1_distance_matrix.csv").csv({typed: true});
```

## The 41-dictionary CDSL inventory

The Cologne Digital Sanskrit Lexicon hosts dictionaries grouped into 7 families. Each row's `sanhw1_lemmas` is the empirical headword count from sanhw1.txt.

```js
Inputs.table(inv.filter(d => +d.sanhw1_lemmas > 0).sort((a,b) => +b.sanhw1_lemmas - +a.sanhw1_lemmas), {
  columns: ["code", "year", "family", "language_pair", "sanhw1_lemmas", "deprecated", "full_name"],
  width: {sanhw1_lemmas: 100, year: 60, code: 80, family: 160, deprecated: 80}
})
```

## Lemma counts by dictionary

```js
const sized = inv.filter(d => +d.sanhw1_lemmas > 0)
  .sort((a, b) => +b.sanhw1_lemmas - +a.sanhw1_lemmas);

Plot.plot({
  width,
  height: 700,
  marginLeft: 80,
  x: {label: "Lemmas in sanhw1 (canonical CDSL master index)", grid: true},
  y: {label: null, domain: sized.map(d => d.code)},
  color: {legend: true, scheme: "tableau10"},
  marks: [
    Plot.barX(sized, {
      x: d => +d.sanhw1_lemmas,
      y: "code",
      fill: "family",
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

**Observation**: MW (1899) has 194,084 lemmas — by far the largest. Combined with PW (151k) + PWG (106k) the Petersburger family is the foundational corpus. PD (Encyclopedic 1976) is 105k.

## Inheritance edges (top temporal-plausible)

These are dictionary pairs where ≥85% of one dict's lemmas appear in another, AND the source dict is older. Each edge is empirical evidence for inheritance:

```js
const top = edges.filter(e => e.temporal_plausible === "True" && +e.containment >= 0.85)
  .slice(0, 25);

Plot.plot({
  width,
  height: 600,
  marginLeft: 200,
  x: {label: "Containment (fraction of source's lemmas in inheritor)", grid: true, domain: [0.85, 1.0]},
  y: {label: null, domain: top.map(e => `${e.source} (${e.source_year}) → ${e.inheritor} (${e.inheritor_year})`)},
  marks: [
    Plot.barX(top, {
      x: d => +d.containment,
      y: d => `${d.source} (${d.source_year}) → ${d.inheritor} (${d.inheritor_year})`,
      fill: "#0075ca",
      tip: true
    }),
    Plot.ruleX([0.85])
  ]
})
```

**Confirmed inheritance lines**:
- `WIL (1832) → SHS (1900)` — 95.3%, confirms Wilson is direct ancestor of Shabda-Sagara
- `WIL (1832) → YAT (1846)` — 92.6% — *new finding*: Yates derived from Wilson
- `PWG (1855) → PW (1879)` — 93.8%, confirms PWG → PWK abridgement
- `MW72 (1872) → MW (1899)` — 89.6%, Monier-Williams self-expansion
- `CCS (1887) → CAE (1891)` — 94.0%, Cappeller German→English
- `PWG (1855) → MW (1899)` — 89.3%, the German→English transmission line
- `ARMH (1861) → MW (1899)` — 92.8% — Hemacandra's *Abhidhānaratnamālā* absorbed into MW
- `ABCH (1896) → MW (1899)` — 92.5% — *Abhidhānacintāmaṇi* of Hemacandra absorbed too

## Heatmap: 41 × 41 lemma-distance matrix

Distance = 1 − Jaccard. Darker = more similar. The dense block in the lower-right is the WIL/YAT/SHS + PWG/PW/MW/Cappeller core.

```js
// Reshape distance matrix wide → long
const dictNames = distances[0] ? Object.keys(distances[0]).filter(k => k !== "dict") : [];
const long = [];
for (const row of distances) {
  for (const col of dictNames) {
    if (col !== row.dict) {
      long.push({a: row.dict, b: col, d: +row[col]});
    }
  }
}

Plot.plot({
  width: Math.min(width, 800),
  height: Math.min(width, 800),
  marginLeft: 60,
  marginBottom: 60,
  x: {label: null, domain: dictNames, tickRotate: -90},
  y: {label: null, domain: dictNames},
  color: {scheme: "viridis", reverse: true, legend: true, label: "Distance"},
  marks: [
    Plot.cell(long, {x: "a", y: "b", fill: "d", tip: true})
  ]
})
```

## Sense-level structure (R2)

Beyond shared *headwords*, the [archived R2 sense-alignment findings](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_FINDINGS.md) split entries into individual **senses** and align them across dictionaries by the **Sanskrit material they share** — SLP1 forms, `<ls>` citations, indigenous `…0` sigla — with **no translation**. This aligns a German PWG sense to an English Apte sense, and a Western sense to an indigenous *Vācaspatya* one, through Sanskrit alone (the "anchor on Sanskrit" method). The current branch keeps this as archived evidence until the R2 generator package is restored or rebuilt.

**[Open the interactive sense-alignment explorer](/tools/r2-explorer)** — pick a headword (`dharma`, `rāma`, …) and browse its senses across up to 13 dictionaries, with the Sanskrit-anchored cross-tradition alignments highlighted.

**H1 — does sense granularity inflate over time?** Measured over the full corpus of 11 general dictionaries (1822–1957): **no.** The year-trend is essentially flat (Pearson *r* = 0.06). Sense granularity is a **lexicographic-family trait** — Benfey/Apte enumerate ~2.5 sense-units per entry, Monier-Williams/Petersburg lump to ~1 — not a function of date, so Paper L treats it as a covariate to control for. [**See the H1 figure**](/tools/r2-h1) · [R2_FINDINGS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_FINDINGS.md).

## What this means for the papers

- **Paper M** (methodology): the unified inheritance score (this lemma signal + convention fingerprints + forensic typos) recovers known CDSL lineage at >90% confidence on the strongest edges. Validates the framework.
- **Paper L** (linguistic): MW is the empirical convergence point of multiple independent dictionary traditions (German, English, Indian Skt-Skt). 89-94% of lemmas from each major source dict appear in MW.
- **Paper H** (historical): WIL → YAT → SHS (English popular tradition) is a 78-year transmission chain visible in lemma data. PWG → PW → MW (German scholarly → English consolidation) is parallel.

## Method

`sanhw1.txt` is the canonical CDSL master headword index, computed and maintained at [hwnorm1/sanhw1](https://github.com/sanskrit-lexicon/hwnorm1/tree/master/sanhw1) by the Cologne team. It applies headword normalisation per [Patel 2016](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/refs/Patel_2016_Normalizing_headwords.pdf) so that variant spellings of the same lemma collapse.

For each pair of dictionaries (A, B):
- **Jaccard distance** = 1 − |A ∩ B| / |A ∪ B|
- **Containment** = |A ∩ B| / |A| → fraction of A's lemmas also in B
- **Temporal plausibility** = year(A) ≤ year(B) → A could be ancestor of B

UPGMA cladogram from the distance matrix is in [`data/sanhw1_cladogram.newick`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/sanhw1_cladogram.newick).

[← back to overview](/)
