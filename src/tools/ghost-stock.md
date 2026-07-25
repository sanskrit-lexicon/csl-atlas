---
title: Ghost stock
toc: false
---

# Ghost stock — is dictionary-unique vocabulary real?

42% of the cross-dictionary union's lemmas appear in exactly **one** dictionary.
Are they recorded language, or lexicographic sediment — inherited citation-forms,
artefacts, ghost words? This page joins the
[union headword backbone](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv)
against two independent modern witnesses: the
[Digital Corpus of Sanskrit](http://www.sanskrit-linguistics.org/dcs/) attestation
flags (via the frozen VisualDCS summary) and, for MW, the
[Sanskrit Heritage](https://sanskrit.inria.fr/) lexicon crosswalk
(agenda hypotheses **PH4 GHOST-STOCK** + **PH6 HERITAGE-WIT**).

```js
const data = FileAttachment("../data/ghost-stock/ghost_stock.json").json();
```

```js
import * as Plot from "npm:@observablehq/plot";
import { csvDownloadButton } from "../lib/csv-download.js";
import { slp1ToIast } from "../lib/lookup-normalize.js";
```

```js
const totals = data.totals;
```

> Of **${totals.unionLemmas.toLocaleString()} union lemmas**,
> **${totals.unionAttested.toLocaleString()}**
> (${(totals.attestedPct * 100).toFixed(1)}%) are DCS-attested — but the rate
> climbs monotonically from
> **${(data.byMultiplicity[0].rate * 100).toFixed(1)}% at n_dicts = 1** to 100%
> for lemmas shared by 13+ dictionaries. Dictionary-unique vocabulary is
> overwhelmingly corpus-invisible.

## Attestation by multiplicity (PH4)

Share of lemmas DCS attests, per number of dictionaries listing the lemma.
Whiskers are Wilson 95% score intervals (mostly narrower than the dots).

```js
display(Plot.plot({
  width: 760,
  height: 320,
  marginLeft: 50,
  x: { label: "dictionaries listing the lemma (n_dicts)", domain: data.byMultiplicity.map((r) => r.nDicts), type: "band" },
  y: { label: "DCS-attested share", domain: [0, 1], grid: true, percent: true },
  marks: [
    Plot.ruleX(data.byMultiplicity, { x: "nDicts", y1: "ciLo", y2: "ciHi", stroke: "var(--theme-foreground-alt)" }),
    Plot.dot(data.byMultiplicity, { x: "nDicts", y: "rate", r: 5, fill: "var(--theme-foreground-focus)",
      title: (r) => `n_dicts=${r.nDicts}: ${r.attested.toLocaleString()}/${r.lemmas.toLocaleString()} attested (${(r.rate * 100).toFixed(1)}%)` }),
    Plot.ruleY([0])
  ]
}));
```

```js
display(Inputs.table(data.byMultiplicity, {
  columns: ["nDicts", "lemmas", "attested", "rate", "ciLo", "ciHi"],
  header: { nDicts: "n_dicts", lemmas: "Lemmas", attested: "Attested", rate: "Rate", ciLo: "CI lo", ciHi: "CI hi" },
  format: { lemmas: (x) => x.toLocaleString(), attested: (x) => x.toLocaleString() },
  rows: 16
}));
```

```js
display(csvDownloadButton(data.byMultiplicity, "ghost-stock-by-multiplicity.csv"));
```

## Which dictionaries' unique stock is real? (per-dict)

Among each dictionary's **unique** lemmas (n_dicts = 1), the share DCS attests.
Note the honest surprise: the highest unique-and-attested shares belong to
**MW and MD** (general dictionaries), not to the specialised lexica the agenda
predicted — though DCS under-samples Buddhist and technical literature, which
caps what BHS-style uniqueness *can* show (see Trust Block limitations).

```js
const perDictSorted = [...data.perDict].sort((a, b) => b.uniqueAttestedShare - a.uniqueAttestedShare);
display(Plot.plot({
  marginLeft: 46,
  height: 40 + perDictSorted.length * 20,
  width: 760,
  x: { label: "unique-and-attested share", domain: [0, Math.max(...perDictSorted.map((d) => d.ciHi)) * 1.1], percent: true, grid: true },
  y: { domain: perDictSorted.map((d) => d.code), label: null },
  color: { legend: true, label: "family" },
  marks: [
    Plot.ruleX(perDictSorted, { y: "code", x1: "ciLo", x2: "ciHi", stroke: "var(--theme-foreground-alt)" }),
    Plot.dot(perDictSorted, { y: "code", x: "uniqueAttestedShare", r: 5, fill: "family",
      title: (d) => `${d.code} (${d.family}): ${d.uniqueAttested.toLocaleString()}/${d.unique.toLocaleString()} unique lemmas attested` }),
    Plot.ruleX([0])
  ]
}));
```

```js
display(Inputs.table(perDictSorted, {
  columns: ["code", "family", "lemmas", "unique", "uniqueAttested", "uniqueAttestedShare"],
  header: { code: "Dict", family: "Family", lemmas: "Lemmas", unique: "Unique", uniqueAttested: "Unique attested", uniqueAttestedShare: "Share" },
  format: { lemmas: (x) => x.toLocaleString(), unique: (x) => x.toLocaleString(), uniqueAttested: (x) => x.toLocaleString() },
  rows: 16
}));
```

```js
display(csvDownloadButton(data.perDict, "ghost-stock-per-dict.csv"));
```

## Logistic model

Descriptive logistic regression of `attested` on `n_dicts` plus
family-presence indicators (deterministic IRLS; McFadden pseudo-R²
**${data.logistic.mcFaddenR2}**, n = ${data.logistic.n.toLocaleString()}).
Each additional witnessing dictionary multiplies the odds of corpus
attestation by ≈ ${Math.exp(data.logistic.terms.find((t) => t.term === "n_dicts").estimate).toFixed(2)}.

```js
display(Inputs.table(data.logistic.terms, {
  columns: ["term", "estimate", "se", "z"],
  header: { term: "Term", estimate: "Estimate (log-odds)", se: "SE", z: "z" },
  rows: 8
}));
```

> ${data.logistic.note}

## The Heritage triangulation (PH6) — MW lemmas only

For the ${totals.mwLemmas.toLocaleString()} union lemmas MW lists, a 2×2×2
cube: MW-unique × Heritage-covered × DCS-attested. Both witnesses point the
same way — Heritage-uncovered lemmas are far likelier to be DCS-unattested.

```js
const cubeRows = data.heritageCube.cells.map((c) => ({
  "MW-unique": c.mwUnique ? "yes" : "no",
  "Heritage-covered": c.heritageCovered ? "yes" : "no",
  "DCS-attested": c.dcsAttested ? "yes" : "no",
  lemmas: c.lemmas
}));
display(Inputs.table(cubeRows, { rows: 8, format: { lemmas: (x) => x.toLocaleString() } }));
```

```js
display(Inputs.table(data.heritageCube.oddsRatios.map((o) => ({
  contrast: o.contrast, "odds ratio": o.oddsRatio, "95% CI": `${o.ciLo}–${o.ciHi}`
})), { rows: 4, layout: "auto" }));
```

```js
display(csvDownloadButton(cubeRows, "ghost-stock-heritage-cube.csv"));
```

## Ranked ghost-candidate queue — `inferred`, not asserted

The triple filter **MW-unique ∧ Heritage-uncovered ∧ DCS-unattested** isolates
**${totals.tripleFilter.toLocaleString()}** candidates in two evidence tiers:
`explicit` (${data.tripleFilter.explicitUncovered.length.toLocaleString()} —
Heritage's own MW↔DICO alignment saw the key and did not cover it) ranks above
`crosswalk-missing` (${data.tripleFilter.crosswalkMissing.length.toLocaleString()} —
key absent from the crosswalk, possibly a key artefact). These are **review
candidates for the H5-style QA queue**: absence from two modern witnesses is
evidence of rarity, not proof a word never existed.

```js
const tierPick = view(Inputs.radio(["all", "explicit", "crosswalk-missing"], { value: "all", label: "tier" }));
const search = view(Inputs.text({ label: "filter (IAST or SLP1)", placeholder: "e.g. gaurav" }));
```

```js
const queueAll = [
  ...data.tripleFilter.explicitUncovered.map((h) => ({ headword: h, tier: "explicit" })),
  ...data.tripleFilter.crosswalkMissing.map((h) => ({ headword: h, tier: "crosswalk-missing" }))
];
const searchLower = search.trim().toLowerCase();
const queueRows = queueAll
  .filter((r) => tierPick === "all" || r.tier === tierPick)
  .filter((r) => {
    if (!searchLower) return true;
    const iast = slp1ToIast(r.headword).toLowerCase();
    return iast.includes(searchLower) || r.headword.toLowerCase().includes(searchLower);
  });
```

```js
display(Inputs.table(queueRows.map((r) => ({ headword: slp1ToIast(r.headword), slp1: r.headword, tier: r.tier })), {
  rows: 20,
  layout: "auto"
}));
```

```js
display(csvDownloadButton(
  queueRows.map((r) => ({ headword_iast: slp1ToIast(r.headword), headword_slp1: r.headword, tier: r.tier, evidence_grade: "inferred" })),
  "ghost-candidate-queue.csv"
));
```

## Chart Trust Block

- **Claim:** dictionary-unique headwords are disproportionately
  corpus-unattested (PH4), and Heritage non-coverage triangulates the same
  ghost stratum for MW, yielding a ranked candidate queue (PH6).
- **Evidence label:** `derived` for the attestation rates, strata, cube, and
  model (deterministic joins + arithmetic on committed inputs); **`inferred`**
  for the ghost-candidate queue — no row is asserted as a ghost word until a
  human source read (H5 discipline) decides it.
- **Source files:**
  [`union_headwords.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv)
  (${totals.unionLemmas.toLocaleString()} normalized lemmas; owned by
  SanskritLexicography),
  [`mw_heritage_crosswalk.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_heritage_crosswalk.tsv)
  (same owner),
  [`data/dcs/dcs_lemma_summary.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dcs/dcs_lemma_summary.json)
  (${totals.dcsLemmas.toLocaleString()} lemmas, frozen VisualDCS export);
  committed packet
  [`src/data/ghost-stock/ghost_stock.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/ghost-stock/ghost_stock.json)
  with provenance in its `.source.json` sidecar.
- **Generated by:** `npm run build-ghost-stock`
- **Validation:** `npm run validate-ghost-stock` — strata/cube/queue
  arithmetic, Wilson-CI bracketing, logistic convergence, plus a full rebuild
  cross-check against the sibling checkout when present; the logistic fit is
  independently reproduced (NumPy IRLS) to 4 decimals.
- **Known false positives:** none at the join level — attestation and coverage
  are read directly off the committed witness files, not inferred.
- **Known false negatives:** DCS samples the transmitted literature —
  "unattested" means absent from that corpus release, not absent from
  Sanskrit; Buddhist/technical vocabulary is under-sampled, which is exactly
  why BHS's unique stock scores low here. Homonyms collapse onto one
  normalized key (attested if any homonym is). Heritage coverage is
  MW-keyed and mirror-derived, not a live INRIA query.
- **Review status:** machine-reviewed (deterministic validator); the
  ghost-candidate queue awaits human spot-check — route via the H5 anomaly
  review discipline before any correction or paper claim.
- **Owner repo:** `csl-atlas` (join + rendering); the union backbone and
  crosswalk are owned by `SanskritLexicography`; corpus attestation belongs
  to VisualDCS per the consumption contract.
- **Next action:** `/spot-check-sample` a stratified sample of the `explicit`
  tier against MW source lines; then fold verdicts into the H5 queue.
- **External dependencies:**
  [`SanskritLexicography`](https://github.com/gasyoun/SanskritLexicography)
  (union + crosswalk), VisualDCS summary (in-repo frozen copy).
- **Boundary note:** no DCS ingestion here (VisualDCS contract); Heritage is
  cited and joined, never cloned (LGPLLR).
