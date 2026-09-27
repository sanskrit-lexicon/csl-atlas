_Created: 23-05-2026 · Last updated: 24-09-2026_

---
title: ABCH — Abhidhānacintāmaṇi (Hemacandra)
---

# ABCH — *Abhidhānacintāmaṇi* (~12th c.)

The classical Sanskrit synonymic kosha by [Hemacandra](https://en.wikipedia.org/wiki/Hemachandra) (~12th century CE), the Jain scholarly tradition's great *nāmaliṅgānuśāsana*. This page is a **data chapter**: every count and chart below renders from [generated data](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/kosa-chapters/kosa_chapters.json) built on the [kośa macrostructure schema](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/schema/kosa-macrostructure.schema.json), with AMAR and ARMH alongside for contrast. ABCH is also **the most-cited kosha in PWG** — cited 17,337 times as `H.` (Hemacandra), making it the single most-referenced source in the entire Großes PW.

**[Source: csl-orig v02/abch/abch.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/abch/abch.txt) · [ABCH GitHub](https://github.com/sanskrit-lexicon/abch)**

## Trust Block

- Evidence: the CDSL v02 `abch.txt` digitization (revision `f4c08c5`), measured by the kośa macrostructure builder [`m10_kosa_macrostructure_model.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m10_kosa_macrostructure_model.py) (H5328) and reshaped for this page by [`build-kosa-chapters.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-kosa-chapters.mjs) (H5329); field inventory from [`data/parse-rules/abch.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/parse-rules/abch.json).
- Limitations: synonym-set boundaries (`<eid>`) and gender tags are the annotators' reading of the verse, not marks in the verse itself ([methods §2](../paper/kosa-macrostructure)); counts of sets carry their own denominator per source artifact and are never mixed.
- Validation: `npm run validate-kosa-chapters` (arithmetic + cross-artifact reconciliation) and `node --test test/kosa-chapters.test.mjs` (mutations prove the validator can fail); page renders checked by `npm run build`.
- Owner repo: `csl-atlas` (handoff H5329, epic E014; model and measures H5328).
- Next use: cite the counts as the ABCH row of the kośa macrostructure type; drill into any division via the table below.

## At a glance

```js
const packet = FileAttachment("../data/kosa-chapters/kosa_chapters.json").json();
const abch = packet.koshas.ABCH;
const t = abch.totals;
```

| | |
|---|---|
| Genre | Classical Sanskrit synonymic kosha (Jain) |
| Author / date | Hemacandra, ~12th c. |
| Digitization model | **grouped** — one `<L>` record per verse-group |
| Records | ${t.verseGroups.toLocaleString("en-US")} verse-groups |
| Divisions | ${t.kandas} kāṇḍas · ${t.vargas} sections (kāṇḍa 4, *tiryak*, has 10 upavargas) |
| Synonym-sets | ${t.sets.toLocaleString("en-US")} (${abch.setSizes["synonym-set"].sets.toLocaleString("en-US")} synonym-sets + ${abch.setSizes["indeclinable-set"].sets} indeclinable-sets) |
| Word forms (members) | ${t.members.toLocaleString("en-US")} |
| Full verses | ${t.fullVerses.toLocaleString("en-US")} in verse-groups (${abch.numbering.fullVerseCount.inFile.toLocaleString("en-US")} in the file) |
| Mean synonyms per set | ${abch.setSizes["synonym-set"].mean} (max ${abch.setSizes["synonym-set"].max}) |
| PWG citations of ABCH | 17,337 (as `H.`) — plus 9,771 as `H. an.` (*Anekārthasaṃgraha*) |

## The macrostructure, counted

Hemacandra orders the universe hierarchically: gods, mortals (*martya*), animals and plants (*tiryak*, ten upavargas from earth to five-sensed beings), hell-beings, and a common section, closing with indeclinables. The chart shows full verses per section; the table carries the full counts.

```js
import { Plot } from "@observablehq/plot";
const vargaRows = abch.divisions.flatMap((d) =>
  d.vargas.map((v) => ({
    section: v.labelIast ?? `${d.labelIast ?? `kāṇḍa ${d.n}`}`,
    kanda: d.labelIast ?? `kāṇḍa ${d.n}`,
    sectionType: v.sectionType,
    verseGroups: v.counts.groups,
    sets: v.counts.sets,
    members: v.counts.members,
    fullVerses: v.counts.fullVerses,
  })));
```

```js
display(Plot.plot({
  marginLeft: 150,
  x: {label: "full verses", grid: true},
  y: {label: null},
  marks: [
    Plot.barY(vargaRows, {x: "section", y: "fullVerses", fill: "sectionType", sort: {y: "-x"}}),
    Plot.ruleX([0]),
  ],
}));
```

```js
display(Inputs.table(vargaRows, {rows: vargaRows.length, layout: "auto"}));
```

**Verse numbering never restarts.** ABCH's verse numbers run **continuously** through all ${abch.numbering.sectionBoundaries} section boundaries (${abch.numbering.restarts} restarts) — the mark of a text read as one continuous composition. The Amarakośa does the opposite: its numbering restarts at every one of its varga boundaries. Same genre, different text-shaping habit — visible only because both are measured by the same model.

## Sets and gender

```js
const setSizeRows = Object.entries(abch.setSizes).map(([kind, s]) => ({kind, sets: s.sets, meanSize: s.mean, maxSize: s.max, singletons: s.singletons}));
const genderRows = Object.entries(abch.genderTags.top).slice(0, 6).map(([tag, n]) => ({tag, members: n}));
```

```js
display(Inputs.table(setSizeRows, {rows: setSizeRows.length, layout: "auto"}));
display(Plot.plot({
  marginLeft: 60,
  x: {label: "tagged members", grid: true},
  y: {label: null},
  marks: [Plot.barY(genderRows, {x: "tag", y: "members", fill: "var(--theme-foreground-focus)", sort: {y: "-x"}}), Plot.ruleX([0])],
}));
```

Across the ${abch.genderContiguity.multiGenderSets} sets that mix genders, each gender holds together in one run ${Math.round(abch.genderContiguity.contiguousObserved * 100)}% of the time against a ${Math.round(abch.genderContiguity.contiguousExpectedUnderPermutation * 100)}% permutation baseline — gender organizes the verse line, but far less tightly than in the Amarakośa (${Math.round(packet.koshas.AMAR.genderContiguity.contiguousObserved * 100)}% vs ${Math.round(packet.koshas.AMAR.genderContiguity.contiguousExpectedUnderPermutation * 100)}%). Alphabetical adjacency among members is ${abch.alphabeticalAdjacency.nondecreasing.toFixed(4)} — chance level, confirming the kośa carries no alphabetical device.

## Chart Trust Block

- **Claim:** Hemacandra's *Abhidhānacintāmaṇi* is an onomasiological, versified kośa whose macrostructure — kāṇḍas, the tenfold *tiryak* upavarga tier, continuously numbered verses, `<eid>` synonym-sets, liṅga tags — is countable from the CDSL digitization and comparable, device by device, with AMAR and ARMH.
- **Evidence label:** `derived` — every number is a deterministic reshape of committed generated artifacts ([kosa model instances + measures](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/kosa_model_measures.json), H5328) and the [ABCH parse rules](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/parse-rules/abch.json); nothing on this page is hand-counted.
- **Source files:** [`src/data/kosa-chapters/kosa_chapters.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/kosa-chapters/kosa_chapters.json) with provenance sidecar `kosa_chapters.source.json`; upstream `csl-orig` v02/abch at revision `f4c08c5`.
- **Generated by:** `npm run build-kosa-chapters`
- **Validation:** `npm run validate-kosa-chapters` (totals re-derived from divisions, instance totals reconciled against parse-rules `record_count` — 1,965 verse-groups, honesty checks that ARMH's absent devices stay absent) and `node --test test/kosa-chapters.test.mjs` (9 tests including four mutations).
- **Known false positives:** none — no detection happens on this page.
- **Known false negatives:** set counts use the instances' per-division denominators; the `<eid>` tag count in the parse rules (4,619) counts markup occurrences, not the same unit — both are labelled and never summed.
- **Review status:** machine-reviewed (deterministic validator); underlying measures reviewed in H5328 (class-verifier PASS).
- **Owner repo:** `csl-atlas`.
- **Next action:** none open; the ARMH counterpart chapter and this page's AMAR comparison land together (H5329).

## ABCH beside AMAR and ARMH

```js
display(Inputs.table(packet.comparison.rows, {rows: packet.comparison.rows.length, layout: "auto"}));
```

## Why ABCH is in the atlas

1. **Most-cited source in PWG.** `H.` (Hemacandra = ABCH) appears 17,337 times in PWG's `<ls>` apparatus — more than *Amarakośa* (14,473), *Medinīkośa* (13,055), or any Vedic text. ABCH is the highest-impact single source in the European philological tradition as represented in CDSL.
2. **What MW's `L.` hides.** MW inherits kosha senses via WIL, then suppresses their individual attributions behind the anonymous `<ls>L.</ls>` hedge: 17,337 named Hemacandra attributions reduced to a single anonymous marker.
3. **Jain lexicographic tradition.** Hemacandra's hierarchy of beings reflects the Jain scholastic tradition, distinct from the Brahmanical cosmological kāṇḍas of *Amarakośa* and Halāyudha — the same word in both sources may carry different register.

## The four CDSL koshas

| CDSL repo | Title | Author | Date |
|---|---|---|---|
| [ARMH](https://github.com/sanskrit-lexicon/armh) | *Abhidhānaratnamālā* | Halāyudha | ~10th c. |
| [ABCH](https://github.com/sanskrit-lexicon/abch) | *Abhidhānacintāmaṇi* | Hemacandra | ~12th c. |
| [ACPH](https://github.com/sanskrit-lexicon/acph) | *Abhidhānacintāmaṇi-pariśiṣṭa* | Hemacandra | ~12th c. |
| [ACSJ](https://github.com/sanskrit-lexicon/acsj) | *Abhidhānacintāmaṇi-śiloñcha* | Hemacandra (attr.) | ~12th c. |

## See also

- [Methods — the kośa as a macrostructural type](../paper/kosa-macrostructure) — the schema and the observed/inferred separation behind every count on this page
- [ARMH chapter](./armh) — Halāyudha's exploded digitization, the grouped model's mirror case
- WIL chapter — the Fort William College dictionary that drew on the kosha tradition
- Lineage Sankey — kosha → WIL → MW lineage visualisation
- [LS_HEDGE_CHECK.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md) — the audit of MW's `L.` hedge that collapsed kosha attributions

---

Source: CDSL abch.txt via the kośa macrostructure model (H5328) · CC-BY-SA-4.0

_Dr. Mārcis Gasūns_
