_Created: 23-05-2026 · Last updated: 24-09-2026_

---
title: ARMH — Abhidhānaratnamālā (Halāyudhakośa)
---

# ARMH — *Abhidhānaratnamālā* (*Halāyudhakośa*, ~10th c.)

The classical Sanskrit synonymic kosha by [Halāyudha](https://en.wikipedia.org/wiki/Hal%C4%81yudha) (~10th century CE) — a verse-format synonymic dictionary, each verse listing the synonyms of one concept. This page is a **data chapter**, and it is also the honest mirror case of the kośa model: the CDSL digitization is **exploded** — one `<L>` record per synonym, with set boundaries, varga names and gender all *not encoded* — so this chapter counts exactly what the digitization can show and labels the rest as absent.

**[Source: csl-orig v02/armh/armh.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/armh/armh.txt) · [ARMH GitHub](https://github.com/sanskrit-lexicon/armh)**

## Trust Block

- Evidence: the CDSL v02 `armh.txt` digitization (revision `f4c08c5`), measured by the kośa macrostructure builder [`m10_kosa_macrostructure_model.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m10_kosa_macrostructure_model.py) (H5328) and reshaped for this page by [`build-kosa-chapters.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-kosa-chapters.mjs) (H5329); field inventory from [`data/parse-rules/armh.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/parse-rules/armh.json).
- Limitations: the exploded digitization encodes neither synonym-set boundaries nor gender, and its `<vn>` locator varies only at the kāṇḍa level — the chapter states those absences as measured facts, never fills them by inference.
- Validation: `npm run validate-kosa-chapters` (arithmetic + cross-artifact reconciliation, incl. 7,907 records = instance members) and `node --test test/kosa-chapters.test.mjs`; page renders checked by `npm run build`.
- Owner repo: `csl-atlas` (handoff H5329, epic E014; model and measures H5328).
- Next use: cite as the exploded-digitization row of the kośa macrostructure type; the kāṇḍa profile below is the finest structure the digitization supports.

## At a glance

```js
const packet = FileAttachment("../data/kosa-chapters/kosa_chapters.json").json();
const armh = packet.koshas.ARMH;
const t = armh.totals;
const pr = armh.parseRules;
```

| | |
|---|---|
| Genre | Classical Sanskrit synonymic kosha (Brahmanical) |
| Author / date | Halāyudha, ~10th c. |
| Digitization model | **exploded** — one `<L>` record per synonym |
| Records | ${pr.recordCount.toLocaleString("en-US")} (= word forms recovered from the verses) |
| Verse-groups | ${t.verseGroups.toLocaleString("en-US")} (`<vn>` locators) |
| Divisions | ${t.kandas} kāṇḍas — numeric locators only, no varga tier |
| Full verses | ${t.fullVerses.toLocaleString("en-US")} |
| Set boundaries | not encoded |
| Gender (liṅga) marking | absent in markup |
| CDSL role | Lineage source for WIL → MW chain; cited in PWG as `HALĀY.` |

## The digitization shape, counted

Each record carries the headword (`<k1>`), a segmented sort key (`<k2>`), the page-column coordinate (`<pc>`) — and the **verse locator** (`<vn>`), the tag that groups the exploded records back into their verses: 7,907 `<vn>` tags, one per record. The locator's first field is the kāṇḍa; it never varies below it, so kāṇḍa 1–5 is the finest division the digitization encodes. Kāṇḍa 5 is the homonym book (*anekārtha*) — identified from its "…api…" formula, not from a heading.

```js
import { Plot } from "@observablehq/plot";
const kandaRows = armh.divisions.map((d) => ({
  kanda: d.labelStatus === "numeric-locator-only" ? `kāṇḍa ${d.n}` : d.labelIast,
  sectionType: d.vargas[0].sectionType,
  verseGroups: d.vargas.reduce((s, v) => s + v.counts.groups, 0),
  members: d.vargas.reduce((s, v) => s + v.counts.members, 0),
  fullVerses: d.vargas.reduce((s, v) => s + v.counts.fullVerses, 0),
}));
```

```js
display(Plot.plot({
  marginLeft: 70,
  x: {label: "records (synonyms)", grid: true},
  y: {label: null},
  marks: [
    Plot.barY(kandaRows, {x: "kanda", y: "members", fill: "sectionType"}),
    Plot.text(kandaRows, {x: "kanda", y: "members", text: (d) => d.members.toLocaleString("en-US"), dy: -8}),
  ],
}));
```

```js
display(Inputs.table(kandaRows, {rows: kandaRows.length, layout: "auto"}));
```

## What the digitization does not encode

The kośa model's `orderingDevices` table measures absence as honestly as presence. For ARMH the absent devices are the point: the verses carry the macrostructure, the digitization does not.

```js
const absentRows = armh.devices.filter((d) => d.evidence === "absent")
  .map((d) => ({device: d.device, layer: d.layer, level: d.level, note: d.note}));
display(Inputs.table(absentRows, {rows: absentRows.length, layout: "auto"}));
```

Alphabetical adjacency across the ${armh.alphabeticalAdjacency.pairs.toLocaleString("en-US")} record pairs is ${armh.alphabeticalAdjacency.nondecreasing.toFixed(4)} — chance level, as expected for a concept-ordered kośa whose records happen to sit in verse order.

## Chart Trust Block

- **Claim:** ARMH's CDSL digitization is an *exploded* kośa — 7,907 one-synonym records regroupable into ${t.verseGroups.toLocaleString("en-US")} verse-groups via the `<vn>` locator, with kāṇḍa as the finest encoded division, and set boundaries, varga names and gender absent from the markup; its macrostructure is countable only down to the kāṇḍa, and the chapter says so rather than inferring the rest.
- **Evidence label:** `derived` — a deterministic reshape of the committed [kosa model artifacts](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/kosa_model_measures.json) (H5328) and [ARMH parse rules](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/parse-rules/armh.json); nothing hand-counted.
- **Source files:** [`src/data/kosa-chapters/kosa_chapters.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/kosa-chapters/kosa_chapters.json) with provenance sidecar `kosa_chapters.source.json`; upstream `csl-orig` v02/armh at revision `f4c08c5`.
- **Generated by:** `npm run build-kosa-chapters`
- **Validation:** `npm run validate-kosa-chapters` (instance members 7,907 reconciled against parse-rules `record_count`; explicit checks that ARMH carries **no** grouped-model measures and that the varga and synonym-set devices stay `absent`) and `node --test test/kosa-chapters.test.mjs` (9 tests including four mutations).
- **Known false positives:** none — no detection happens on this page.
- **Known false negatives:** the kāṇḍa-5 homonym identification is `inferred` (the "…api…" formula), and is labelled so in the devices table; full-verse counts derive from verse-end digits and inherit that method's limits.
- **Review status:** machine-reviewed (deterministic validator); underlying measures reviewed in H5328 (class-verifier PASS).
- **Owner repo:** `csl-atlas`.
- **Next action:** none open; this chapter and the ABCH counterpart land together (H5329).

## ARMH beside AMAR and ABCH

```js
display(Inputs.table(packet.comparison.rows, {rows: packet.comparison.rows.length, layout: "auto"}));
```

Where AMAR and ABCH digitizations are *grouped* (one record per verse, `<eid>` sets, liṅga tags), ARMH's exploded records preserve the words and the verse locator but discard the set structure — the same genre at two digitization depths, which is exactly what the [kośa macrostructure schema](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/schema/kosa-macrostructure.schema.json) models with its `unsegmented-verse` set kind.

## Why ARMH is in the atlas

1. **The kosha group as WIL's primary source.** Wilson (WIL) and the Fort William College pandits worked from classical kosha sense-divisions to construct English glosses; ARMH is one of the principal sources of those sense-divisions.
2. **Same word, different traditions.** *aṃśu* appears in ARMH's synonym verse for "sun" and for "ray" — the very sense-divisions WIL preserves ("A ray of light, a sun-beam... The sun...") and MW inherits. From [DICT_PROFILE.md — The four Cologne koshas](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/DICT_PROFILE.md#the-four-cologne-koshas): *aṃśu* in ARMH L369 (names of the sun) and ARMH L411 (words for "ray").
3. **Cited in PWG as `HALĀY.`** Böhtlingk-Roth cite Halāyudha explicitly; Monier-Williams collapses these citations into the anonymous `<ls>L.</ls>` hedge.

## The four CDSL koshas

| CDSL repo | Title | Author | Date |
|---|---|---|---|
| [ARMH](https://github.com/sanskrit-lexicon/armh) | *Abhidhānaratnamālā* | Halāyudha | ~10th c. |
| ABCH | *Abhidhānacintāmaṇi* | Hemacandra | ~12th c. |
| [ACPH](https://github.com/sanskrit-lexicon/acph) | *Abhidhānacintāmaṇi-pariśiṣṭa* | Hemacandra | ~12th c. |
| [ACSJ](https://github.com/sanskrit-lexicon/acsj) | *Abhidhānacintāmaṇi-śiloñcha* | Hemacandra (attr.) | ~12th c. |

## See also

- [Methods — the kośa as a macrostructural type](../paper/kosa-macrostructure) — the schema, the observed/inferred separation, and why exploded digitizations get an `unsegmented-verse` set kind
- [ABCH chapter](./abch) — Hemacandra's grouped digitization; the most-cited kosha in PWG (17,337 times as `H.`)
- WIL chapter — the Fort William College dictionary that drew on the kosha tradition
- Lineage Sankey — kosha → WIL → MW lineage visualisation
- [LS_HEDGE_CHECK.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md) — the audit of MW's `L.` hedge that collapsed kosha attributions

---

Source: CDSL armh.txt via the kośa macrostructure model (H5328) · CC-BY-SA-4.0

_Dr. Mārcis Gasūns_
