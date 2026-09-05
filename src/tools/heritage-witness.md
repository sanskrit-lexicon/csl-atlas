_Created: 08-07-2026 · Last updated: 05-09-2026_

---
title: Heritage witness
toc: false
---

# Heritage witness — an independent, non-Cologne confirmation

The [Sanskrit Heritage Platform](https://sanskrit.inria.fr/) (INRIA) lexicon is
an independent witness, entirely outside the Cologne Digital Sanskrit
Dictionaries pipeline. The
[MW↔Heritage crosswalk](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_heritage_crosswalk.tsv)
(built from the mirror's own MW↔DICO alignment — no OCR or fuzzy matching)
makes it joinable onto MW's headword set: this page shows **which MW
headwords Heritage independently confirms**, useful evidence for the
P-series papers' attestation arguments.

```js
const data = FileAttachment("../data/heritage/heritage_witness.json").json();
```

```js
import * as Plot from "npm:@observablehq/plot";
import { csvDownloadButton } from "../lib/csv-download.js";
import { slp1ToIast } from "../lib/lookup-normalize.js";
```

```js
const totals = data.totals;
```

> Of **${totals.mwEntries.toLocaleString()} distinct MW headwords**, Heritage
> covers **${totals.heritageCovered.toLocaleString()}**
> (${(totals.coveragePct * 100).toFixed(1)}%) — ${totals.anchored.toLocaleString()}
> resolved to an exact DICO entry anchor, ${totals.coveredNoAnchor.toLocaleString()}
> covered but unresolved (MW's plain key drops DICO's homonym suffix).

## Coverage by initial letter

Where Heritage coverage concentrates across the MW alphabet — each bar is one
initial (SLP1), split anchored vs covered-without-anchor, against the total
MW headword count for that initial.

```js
const initialRows = data.perInitial
  .flatMap((r) => [
    { initial: r.initial, tier: "anchored", n: r.anchored },
    { initial: r.initial, tier: "covered-no-anchor", n: r.coveredNoAnchor },
    { initial: r.initial, tier: "uncovered", n: r.mwEntries - r.anchored - r.coveredNoAnchor }
  ]);
```

```js
display(Plot.plot({
  marginLeft: 40,
  height: 40 + data.perInitial.length * 16,
  width: 760,
  x: { label: "MW headwords" },
  y: { domain: data.perInitial.map((r) => r.initial), label: null },
  color: {
    domain: ["anchored", "covered-no-anchor", "uncovered"],
    range: ["var(--theme-foreground-focus)", "var(--theme-foreground-alt)", "var(--theme-foreground-faintest)"],
    legend: true
  },
  marks: [
    Plot.barX(initialRows, { x: "n", y: "initial", fill: "tier",
      title: (r) => `${r.initial} ${r.tier}: ${r.n.toLocaleString()}` }),
    Plot.ruleX([0])
  ]
}));
```

```js
display(csvDownloadButton(data.perInitial, "heritage-coverage-by-initial.csv"));
```

## Heritage-covered headwords

Every MW headword Heritage covers, with its match tier and a link into the
[source viewer](source) at the first MW occurrence (headwords shown in IAST).

```js
const tierPick = view(Inputs.radio(["all", "anchored", "covered-no-anchor"], { value: "all", label: "match tier" }));
const search = view(Inputs.text({ label: "filter (IAST or SLP1)", placeholder: "e.g. deva" }));
```

```js
const searchLower = search.trim().toLowerCase();
const witnessRows = data.witnessed
  .filter((w) => tierPick === "all" || w.matchTier === tierPick)
  .filter((w) => {
    if (!searchLower) return true;
    const iast = slp1ToIast(w.headword).toLowerCase();
    return iast.includes(searchLower) || w.headword.toLowerCase().includes(searchLower);
  })
  .map((w) => ({
    headword: slp1ToIast(w.headword),
    "match tier": w.matchTier,
    "heritage anchor": w.heritageAnchor
      ? html`<a href="https://sanskrit.inria.fr/${w.heritageAnchor}" target="_blank" rel="noopener">${w.heritageAnchor}</a>`
      : "",
    occurrences: w.occurrences,
    source: html`<a href="source#mw/${w.mwLine}">line ${w.mwLine}</a>`
  }));
```

```js
display(Inputs.table(witnessRows, {
  rows: 20,
  layout: "auto",
  format: { "heritage anchor": (v) => v, source: (v) => v }
}));
```

```js
display(csvDownloadButton(
  data.witnessed
    .filter((w) => tierPick === "all" || w.matchTier === tierPick)
    .filter((w) => {
      if (!searchLower) return true;
      const iast = slp1ToIast(w.headword).toLowerCase();
      return iast.includes(searchLower) || w.headword.toLowerCase().includes(searchLower);
    })
    .map((w) => ({
      headword_iast: slp1ToIast(w.headword),
      headword_slp1: w.headword,
      match_tier: w.matchTier,
      heritage_anchor: w.heritageAnchor ?? "",
      occurrences: w.occurrences,
      mw_line: w.mwLine
    })),
  "heritage-witness.csv"
));
```

## Chart Trust Block

- **Claim:** which MW headwords the Sanskrit Heritage Platform's lexicon
  independently lists, and at what match confidence (anchored vs
  covered-without-a-resolved-anchor).
- **Evidence label:** `derived` — deterministic key join on normalized SLP1;
  no classification or model.
- **Source files:**
  [`SanskritLexicography/HeadwordLists/mw_heritage_crosswalk.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_heritage_crosswalk.tsv)
  (${totals.crosswalkRows.toLocaleString()} rows, built read-only from the
  Heritage mirror's own MW↔DICO alignment by
  [`heritage_mw_crosswalk.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_mw_crosswalk.py),
  owned by SanskritLexicography) joined onto MW's `<k1>` headwords from
  `csl-orig/v02/mw/mw.txt`; committed atlas packet
  [`src/data/heritage/heritage_witness.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/heritage/heritage_witness.json)
  with crosswalk-commit provenance in its `.source.json` sidecar.
- **Generated by:** `npm run build-heritage-witness`
- **Validation:** `npm run validate-heritage-witness` — totals arithmetic,
  per-initial sums, witnessed-row tier consistency, plus a full rebuild
  cross-check against the sibling crosswalk + live MW dict when the checkout
  is present.
- **Known false positives:** none at the join level — entry existence is
  read directly off the committed crosswalk's `covered_flag`/anchor columns,
  not inferred.
- **Known false negatives:** entry-existence only, not sense-level agreement
  — a match confirms Heritage lists the headword, not that the two
  dictionaries agree on meaning; MW records differing only by homonym suffix
  or accent collapse onto one normalized row, so a homonym-specific Heritage
  mismatch is invisible here; Heritage coverage reflects the mirror's
  snapshot, not a live INRIA query.
- **Review status:** machine-reviewed (deterministic validator; 20 rows of
  the underlying crosswalk hand-verified against the mirror's `DICO/*.html`
  and MW's raw HTML per the crosswalk's own sanity check).
- **Owner repo:** `csl-atlas` (rendering + join); the crosswalk itself is
  owned by `SanskritLexicography`.
- **Next action:** the parallel kosha ingest (H345) joins the same crosswalk
  onto kosha's frequency layer as a third coverage witness — once merged, a
  follow-on could add a "corpus-attested AND Heritage-covered" combined axis
  here.
- **External dependencies:**
  [`SanskritLexicography`](https://github.com/gasyoun/SanskritLexicography)
  (crosswalk), csl-orig v02 (MW headwords).
- **Boundary note:** the atlas joins and renders; the DICO alignment itself,
  its homonym-fallback logic, and any Heritage-side corrections stay with
  SanskritLexicography.

_Dr. Mārcis Gasūns_
