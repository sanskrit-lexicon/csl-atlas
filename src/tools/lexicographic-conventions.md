---
title: Convention fingerprints — the L0 cladogram
toc: true
---

# Convention fingerprints & the formatting cladogram

How do the Cologne dictionaries relate by **house style** — the orthographic and citation
conventions in which they render Sanskrit, independent of *which* words they contain? This
page builds a phylogenetic tree of CDSL dictionaries from a **convention fingerprint**: 25
categorical dimensions, of which the seven canonical ones are [Dhaval Patel's 2016
normalization conventions](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/refs/Patel_2016_Normalizing_headwords.pdf),
populated from Patel's **own per-dictionary classification** (ground truth from the
convention author). The remaining dimensions are auto-extracted from each dictionary's
source markup.

Companion to [Dictionary genealogy](lexicography) (which measures shared *content* via the sanhw1
headword index) and to the [Phase L0 design](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/L0_DESIGN.md) /
[results](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/L0_RESULTS.md).
The headline finding is that **convention-lineage and content-lineage are distinct signals**
— see [the discussion below](#convention-lineage-is-not-content-lineage).

## Trust Block

- Evidence: L0 convention-fingerprint files under `src/data/lexicographic-structure/L0/`, Patel 2016 assignments, and validation reports.
- Limitations: convention lineage measures house style and markup practice; it is separate from content inheritance.
- Validation: checked by `npm run build`; L0 validation details are in `docs/L0_RESULTS.md` and `docs/L0_DESIGN.md`. Against documented descent the published tree scores a **Generalized Quartet Distance of 0.146 — 85.4% agreement** with the expert-resolved quartets, versus 0.666 ± 0.068 for randomly relabelled trees (all ten gated trees fall in 0.110–0.172); the lemma-overlap tree scores 0.430 on the same gold. Method, gold trees, and the five documented edges no tree can represent: [`docs/L0_GQD_VALIDATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/L0_GQD_VALIDATION.md).
- Owner repo: `csl-atlas`.
- Next use: treat the chart as structural evidence, then check companion docs before making a lineage claim.

```js
const patel = await FileAttachment("../data/lexicographic-structure/L0/patel2016_assignments.csv").csv({typed: true});
const boot = await FileAttachment("../data/lexicographic-structure/L0/bootstrap_support.csv").csv({typed: true});
const fp = await FileAttachment("../data/lexicographic-structure/L0/convention_fingerprint.csv").csv({typed: true});
const dist = await FileAttachment("../data/lexicographic-structure/L0/distances/B_whamming.csv").csv({typed: true});
const report = await FileAttachment("../data/lexicographic-structure/L0/validation_report.json").json();
const residual = await FileAttachment("../data/lexicographic-structure/L0/content_convention_residual.csv").csv({typed: true});
const scatter = await FileAttachment("../data/lexicographic-structure/L0/content_convention_scatter.csv").csv({typed: true});
const algo = await FileAttachment("../data/lexicographic-structure/L0/algorithm_support_comparison.csv").csv({typed: true});
```

## At a glance

```js
function stat(label, value, sub) {
  return html`<div style="flex:1 1 150px;padding:0.8rem 1rem;border:1px solid var(--theme-foreground-faint);border-radius:8px;">
    <div style="font-size:1.7rem;font-weight:700;">${value}</div>
    <div style="font-weight:600;">${label}</div>
    <div style="opacity:0.65;font-size:0.85rem;">${sub}</div></div>`;
}
display(html`<div style="display:flex;gap:0.8rem;flex-wrap:wrap;">
  ${stat("dictionaries", report.n_dicts, "with a local source")}
  ${stat("convention dims", report.n_dims, "7 Patel + 18 auto")}
  ${stat("lineage families cohere", "6 / 6", "tighter than global mean")}
  ${stat("edge recovery", (report.known_edge_recovery.recovery_rate*100).toFixed(0) + "%", `${report.known_edge_recovery.tierA_recovered}/${report.known_edge_recovery.tierA_n} tier-A edges`)}
  ${stat("bootstrap", report.n_bootstrap.toLocaleString(), "dimension resamples")}
</div>`);
```

## The canonical convention cladogram

UPGMA on the rare-option-weighted Hamming distance over the 25 convention dimensions, with
1000× dimension-bootstrap consensus. Five readable clades emerge: the **Petersburg
formatting family** (PWG/PW/SCH/CCS/CAE), the **Latin/German etymological + MW** group, the
**Anglo-Indian** line (WIL/SHS/AP90/AP/MD), the **indigenous + verb** dicts (SKD/VCP/KRM),
and a mixed/index cluster.

```js
display(await FileAttachment("../data/lexicographic-structure/L0/trees/canonical_consensus.png").image({width: 760, alt: "L0 convention cladogram"}));
```

## Bootstrap support for known lineage edges

Each bar is a documented inheritance edge; the value is the fraction of 1000 bootstrap trees
in which the child falls among the parent's three nearest neighbours, with a 95% Wilson
interval. **Tier A** = high-confidence (inventory + sanhw1 containment); **tier B** =
scholarly hypothesis under test. The *formatting* edges (WIL→SHS, PWG→PW, PWG→SCH, CCS→CAE)
score high; the *content-only* edges where the heir reformatted (PWG→MW, MW72→MW) score low
— the core finding of this page.

```js
const bootSorted = boot.slice().sort((a,b) => b.consensus_support - a.consensus_support);
Plot.plot({
  width,
  height: 360,
  marginLeft: 110,
  x: {label: "bootstrap support (1000×)", domain: [0, 1], grid: true},
  y: {label: null, domain: bootSorted.map(d => `${d.parent}→${d.child}`)},
  color: {legend: true, domain: ["A", "B"], range: ["#0075ca", "#d93f0b"], label: "tier"},
  marks: [
    Plot.barX(bootSorted, {x: "consensus_support", y: d => `${d.parent}→${d.child}`, fill: "tier", tip: true}),
    Plot.ruleX(bootSorted, {x: "ci95_low", x2: "ci95_high", y: d => `${d.parent}→${d.child}`, strokeWidth: 1.4}),
    Plot.ruleX([0.8], {stroke: "currentColor", strokeDasharray: "3,3", strokeOpacity: 0.5}),
    Plot.ruleX([0])
  ]
})
```

The dashed line marks the 0.80 "strong edge" threshold (design §6.4).

### Three algorithms agree on the strong edges (Phase L0-rigor)

The paper-final tree is checked against all three of the design's algorithms — **UPGMA**
and **Neighbour-Joining** (500× character bootstrap) and a **Bayesian Mk MCMC** (2-state
symmetric morphological model, Felsenstein pruning, NNI + branch-length Metropolis moves,
80k generations). Support = posterior/bootstrap probability that the pair sits in a shared
clade of ≤ 4 leaves.

```js
const algoLong = algo.flatMap(d => [
  {edge: `${d.parent}–${d.child}`, method: "UPGMA", v: d.upgma_support},
  {edge: `${d.parent}–${d.child}`, method: "NJ", v: d.nj_support},
  {edge: `${d.parent}–${d.child}`, method: "Bayes", v: d.bayes_support},
]);
Plot.plot({
  width,
  height: 420,
  marginLeft: 95,
  x: {label: "support — P(shared clade ≤ 4)", domain: [0, 1], grid: true},
  y: {label: null, domain: algo.map(d => `${d.parent}–${d.child}`)},
  fy: {label: null},
  color: {legend: true, domain: ["UPGMA", "NJ", "Bayes"], range: ["#7aa6c2", "#0075ca", "#d93f0b"]},
  marks: [
    Plot.barX(algoLong, {x: "v", y: "edge", fill: "method", fy: "method", tip: true, sort: {y: null}}),
    Plot.ruleX([0])
  ]
})
```

Two takeaways. **The strong formatting edges** — PWG→PW, PWG→SCH, WIL→SHS, AP90→AP — clear
the bar under every algorithm (Bayesian Mk is the most decisive on the Petersburg core,
1.00). **The reformatted edges stay low under every algorithm** (MW72→MW ≤ 0.43, WIL→YAT ≈ 0):
the convention ≠ content result is robust to the clustering method, not an artifact. Bayesian
Mk, sensitive to shared *derived* characters, additionally surfaces PW→CCS (0.74) and the
Bopp→MW hypothesis (0.65) that distance-bootstrap dilutes. Robinson–Foulds between the three
point estimates: UPGMA–NJ 0.59, NJ–Bayes 0.45, UPGMA–Bayes 0.70 (`data/L0/bayesian_report.json`).

## Patel 2016 convention taxonomy

The seven canonical conventions and the dictionaries Patel assigns to each option.
Conventions are multi-valued — a dictionary may follow several options.

```js
Inputs.table(patel, {
  columns: ["convention", "option", "definition", "member_dicts"],
  width: {convention: 90, option: 60, definition: 320},
  rows: 30
})
```

## Per-dictionary convention fingerprint (Patel's 7)

Each cell is the `+`-joined option set the dictionary follows. Dicts sharing a row pattern
share a house style — note how **PWG / PW / SCH** are identical and **CCS** differs by one.

```js
const dimNames = {1:"1 anusvāra", 2:"2 r-dup", 3:"3 -at", 4:"4 inflect", 5:"5 verb-anu", 6:"6 ṛkārānta", 7:"7 vas/yas"};
const fpRows = fp
  .filter(r => r.dim_1_source && r.dim_1_source !== "unknown")
  .map(r => ({
    dict: r.dict,
    "1 anusvāra": r.dim_1_value, "2 r-dup": r.dim_2_value, "3 -at": r.dim_3_value,
    "4 inflect": r.dim_4_value, "5 verb-anu": r.dim_5_value, "6 ṛkārānta": r.dim_6_value,
    "7 vas/yas": r.dim_7_value
  }));
Inputs.table(fpRows, {rows: 32, width: {dict: 60}})
```

## Convention-distance heatmap

Pairwise rare-option-weighted Hamming distance over the 25 dimensions (0 = identical house
style, darker = closer). The bright low-distance blocks are the formatting families.

```js
const codes = dist.columns.filter(k => k !== "");
const long = [];
for (const row of dist) {
  const a = row[""];
  for (const b of codes) if (b !== a) long.push({a, b, d: +row[b]});
}
Plot.plot({
  width: Math.min(width, 760),
  height: Math.min(width, 760),
  marginLeft: 52,
  marginBottom: 56,
  x: {label: null, domain: codes, tickRotate: -90},
  y: {label: null, domain: codes},
  color: {scheme: "viridis", reverse: true, legend: true, label: "convention distance"},
  marks: [Plot.cell(long, {x: "a", y: "b", fill: "d", tip: true})]
})
```

## Convention-lineage is not content-lineage

The pattern of which edges the convention tree recovers — and which it misses — is the
result. Edges that score high are *formatting* inheritances, where an heir adopted its
predecessor's house style: **WIL→SHS (0.81)**, **PWG→PW (0.79)**, **PWG→SCH (0.70)**,
**CCS→CAE (0.64)**. Edges that score low are *content* inheritances where the heir
**reformatted**: **PWG→MW (0.02)**, **MW72→MW (0.29)** — even though, by the
[sanhw1 content measure](lexicography), 89–94% of those sources' lemmas recur in MW.

Monier-Williams absorbed the Petersburg *lexicon* while imposing its own orthographic
standard (ṛ-stems as `-ṛ` not `-ar`; śatṛ as `-at` not `-ant`; `-vas` not `-vaṃs`). The
gap between near-unity content-containment and near-zero convention-similarity is the
quantitative signature of a re-edited, re-typeset descendant. **Content and convention are
orthogonal axes of descent**, and their divergence localises editorial intervention — the
full argument is in [Paper H §5](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_H_convention_vs_content_lineage.md).

### The two axes, plotted (Phase L0.7)

Every point is a dictionary pair: **content** similarity (sanhw1 lemma Jaccard, *x*) against
**convention** similarity (1 − L0 distance, *y*). Points on the diagonal inherit both axes
equally; points **below-right** (high content, low convention) are the reformatting events —
shared vocabulary rendered in a different house style.

```js
Plot.plot({
  width: Math.min(width, 700),
  height: Math.min(width, 700),
  grid: true,
  x: {label: "content similarity (sanhw1 lemma Jaccard) →", domain: [0, 1]},
  y: {label: "↑ convention similarity (1 − L0 distance)", domain: [0, 1]},
  color: {scheme: "RdYlBu", label: "content − convention gap", legend: true},
  marks: [
    Plot.line([[0,0],[1,1]], {stroke: "currentColor", strokeOpacity: 0.3, strokeDasharray: "4,4"}),
    Plot.dot(scatter, {x: "content_similarity", y: "convention_similarity", fill: "gap", r: 3.5, tip: true,
                       channels: {pair: d => `${d.a}–${d.b}`}}),
  ]
})
```

### Ranked reformatting events

Directed inheritance edges (sanhw1 containment ≥ 0.85), scored by
**residual = content containment − convention similarity**. The top rows — everything into
**MW** (Monier-Williams), and **WIL→YAT** — are the heavy editorial recodings; the bottom
rows (SHS↔WIL, PWG→PW, CCS→CAE) inherited form as well as substance.

```js
Plot.plot({
  width,
  height: 420,
  marginLeft: 110,
  x: {label: "reformatting residual (content − convention)", domain: [0, 0.75], grid: true},
  y: {label: null, domain: residual.map(d => `${d.source}→${d.inheritor}`)},
  color: {type: "diverging", scheme: "RdYlBu", reverse: true, legend: true, label: "residual"},
  marks: [
    Plot.barX(residual, {x: "reformatting_residual", y: d => `${d.source}→${d.inheritor}`,
                         fill: "reformatting_residual", tip: true}),
    Plot.ruleX([0])
  ]
})
```

```js
Inputs.table(residual, {
  columns: ["source", "inheritor", "content_containment", "convention_similarity", "reformatting_residual", "temporal_plausible"],
  header: {content_containment: "content", convention_similarity: "convention", reformatting_residual: "residual"},
  sort: "reformatting_residual", reverse: true, rows: 26
})
```

## Method & caveats

- **Fingerprint**: 7 Patel conventions (`source = patel2016`, from his per-dict classification) + 18 auto-extracted markup dimensions. English-headword dicts (BOR, AE) are excluded by Patel from the Sanskrit-headword conventions; LRV, FRI are not in Patel's 36 and remain partially gated; KNA/KOW/AMAR lack a local source.
- **Distance**: rare-option-weighted Hamming, missing-aware, with cell-level Jaccard for multi-valued conventions. Encoding choice barely moves the tree (Robinson–Foulds ≈ 0.07 between Jaccard and Hamming UPGMA); algorithm choice matters more (UPGMA vs NJ ≈ 0.5).
- **Canonical tree**: 1000× dimension-bootstrap consensus UPGMA; full Bayesian MCMC deferred (design §9). Config `B_whamming` is pre-registered, not tuned to recovery.
- **Reproduce**: `scripts/L0/s2_fingerprint.py` → `s2b_patel_auto.py` → `s2d_patel_gold.py` → `s3_cladogram.py`. Taxonomy & numbering in [`refs/fingerprint_conventions.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/refs/fingerprint_conventions.md) + [`refs/concordance.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/refs/concordance.md).

[← back to Dictionary genealogy](lexicography) · [overview](../)
