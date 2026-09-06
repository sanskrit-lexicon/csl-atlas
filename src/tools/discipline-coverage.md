_Created: 06-09-2026 · Last updated: 06-09-2026_

---
title: Discipline coverage
toc: false
---

# Discipline coverage — which parts of the atlas serve which discipline

The atlas's dictionary inventory joined through the estate's **ratified
Russian-Indology discipline taxonomy**: each dict carries a meso-discipline
assignment ([`dict_meso_assignments.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/disciplines/dict_meso_assignments.json)),
which the build joins through
[`meso_discipline_crosswalk.csv`](https://github.com/gasyoun/IndologyScholars/blob/main/curation/meso_discipline_crosswalk.csv)
to [`disciplines.csv`](https://github.com/gasyoun/IndologyScholars/blob/main/curation/disciplines.csv)
(ratified by IndologyScholars decision D1, 10-07-2026). The taxonomy is
**never re-derived here** — this page is the atlas's first consumer of the
crosswalk (H3567 ruling F5, released by F5c; landed by H4178).

```js
const data = FileAttachment("../data/disciplines/discipline_coverage.json").json();
```

## Summary

- ${data.totals.dicts} atlas dicts: **${data.totals.assigned} assigned** to at
  least one discipline, ${data.totals.unassigned} honestly unassigned (no
  confident meso facet — listed below with reasons).
- ${data.totals.disciplines} distinct disciplines reached.

```js
import * as Plot from "npm:@observablehq/plot";
```

<div class="card">
${Plot.plot({
  marks: [
    Plot.barX(data.perDiscipline, { y: (d) => `${d.labelEn} (${d.code})`, x: (d) => d.dicts.length }),
    Plot.ruleX([0]),
  ],
  marginLeft: 220,
  width: 720,
})}
</div>

## Per-discipline dict sets

${data.perDiscipline.map((d) => `- **${d.labelEn}** (${d.code}) — ${d.dicts.length} dicts: ${d.dicts.join(", ")}`).join("\n")}

## Full dict table

| Dict | Meso code | Discipline(s) | Conf. |
|---|---|---|---|
${data.dicts
  .map(
    (d) =>
      d.disciplines.length
        ? `| ${d.dict} | ${d.mesoCode} | ${d.disciplines.map((x) => `${x.labelEn}`).join("; ")} | ${d.disciplines[0].confidence} |`
        : `| ${d.dict} | — (unassigned) | ${d.rationale} | 0 |`
  )
  .join("\n")}

## Deliberately NOT-MAPPED meso codes

The crosswalk refuses to map methodological/regional/chronological codes to
disciplines (regional codes like `bengal`, methodological like
`comparative_analysis`). The build carries those sentinel rows verbatim; any
future assignment using them must fail loudly.

## Trust Block

- Evidence: sibling-pinned IndologyScholars
  `curation/meso_discipline_crosswalk.csv` + `curation/disciplines.csv`
  (commit pin in
  [`discipline_coverage.source.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/disciplines/discipline_coverage.source.json));
  assignment layer reviewed in-repo.
- Limitations: general Sanskrit lexicography has no dedicated meso code —
  those dicts sit on the nearest Sanskrit facet at ≤0.6 confidence; five dicts
  stay unassigned pending human curation (see table).
- Validation: `npm run build-discipline-coverage` + `npm run validate-discipline-coverage`.
- Owner repo: `csl-atlas`; taxonomy owner: `IndologyScholars` (never re-derive).
