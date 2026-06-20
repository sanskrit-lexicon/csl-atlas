# Release Checklist

Date: 2026-06-03

Use this checklist before publishing or opening a release PR for the review-release roadmap.

## Source Snapshot

- [ ] Confirm local `../csl-orig/v02` exists and note its snapshot date.
- [ ] Confirm no raw dictionary files are staged.
- [ ] Confirm generated data was rebuilt from one consistent source snapshot.

## Rebuild Commands

Run the relevant generators before validation:

```bash
npm run build-coverage
npm run build-mw-depth
npm run build-dict-comparison
npm run build-citation-apparatus
npm run build-structural-register
npm run build-h6-structural-review
npm run build-sense-depth
npm run build-gender-review
npm run build-source-layer-review
npm run build-alignment-review
npm run build-semantic-fields
npm run build-h4-family-profiles
npm run build-xref-lineage
npm run build-xref-hub-review
npm run recover-r2-archive
npm run build-r2-source-anchors
npm run build-r2-parser-diagnostics
npm run build-h5-anomaly-review
```

## Validation Gates

Required:

```bash
npm test
npm run validate-mw-depth
npm run validate-dict-comparison
npm run validate-review-reports
npm run build
```

## Review Preservation

- [ ] Inspect one previously human-reviewed item, if any exists.
- [ ] Rerun that queue generator.
- [ ] Confirm `reviewStatus`, `reviewedValue`, `reviewer`, `reviewedAt`, and `note` survive.
- [ ] Confirm no generated source data was manually edited to encode a review decision.

## Public Site Checks

- [ ] Reader lookup opens from the sidebar and landing page.
- [ ] Lookup exact examples work: `agni`, `dharma`, `śiva`, `aMSa`.
- [ ] Reader lookup and dictionary dossier open from manifest samples without loading the core monoliths first.
- [ ] Broad lookup still returns expected exact/prefix headword matches.
- [ ] Dictionary dossier core mode returns exact/prefix matches and shows DCS chips from shards where available.
- [ ] Lookup no-result state is explicit and does not imply corpus or sandhi search.
- [ ] Review queues expose machine vs reviewed status.
- [ ] Dictionary structure pages open: genealogy, convention fingerprints, structural register, semantic fields, cross-reference lineage, R2 sense explorer.
- [ ] Mobile viewport has no incoherent text overlap.
- [ ] GitHub Pages assets copied by `postbuild`: `manifest.json`, `sw.js`, `favicon.svg`.

## Known Caveats To Keep Visible

- Reader Lookup v1 is static headword lookup for lemmas attested in at least 4 target dictionaries, not full-text search or long-tail lookup.
- DCS and corpus work belong in VisualDCS or a future grammar repo, not in this atlas release.
- Source-layer mappings are conservative review seeds, not exact chronology.
- VCP/SKD gender extraction is useful but incomplete for feminine/neuter cases.
- TEI/OntoLex full 50-case validation lives in `csl-standards`, not this atlas.
- R2 sense-alignment pages are archived snapshots until the rebuild contract is
  implemented.
- H5 anomaly candidates are review seeds, not automatic ghost-entry claims.
