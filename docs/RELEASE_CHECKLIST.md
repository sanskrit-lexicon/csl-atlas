_Created: 04-06-2026 · Last updated: 05-09-2026_

# Release Checklist

Date: 2026-06-03

Use this checklist before publishing or opening a release PR. The governing
delivery order is [`ROADMAP_2026_2027.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ROADMAP_2026_2027.md).

## Source Snapshot

- [ ] Confirm local `../csl-orig/v02` exists and note its snapshot date.
- [ ] Confirm no raw dictionary files are staged.
- [ ] Confirm generated data was rebuilt from one consistent source snapshot.

## Rebuild Commands

Regenerate the review evidence from one consistent source snapshot:

```bash
npm run regen-review-artifacts
```

## Validation Gates

Required:

```bash
npm run verify
```

## Review Preservation

- [ ] Confirm `regen-review-artifacts` reports byte-equivalent preserved human fields.
- [ ] Confirm it is run twice by `verify` without a tracked diff.
- [ ] Never use the R2 `--reseed` flag in a release workflow.
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
- [ ] Live footer reports `v0.2.0` and the deployed `main` SHA.
- [ ] Run the five-part publish-safety gate immediately before publishing.

## Known Caveats To Keep Visible

- Reader Lookup v1 is static headword lookup for lemmas attested in at least 4 target dictionaries, not full-text search or long-tail lookup.
- DCS and corpus work belong in VisualDCS or a future grammar repo, not in this atlas release.
- Source-layer mappings are conservative review seeds, not exact chronology.
- VCP/SKD gender extraction is useful but incomplete for feminine/neuter cases.
- TEI/OntoLex full 50-case validation lives in `csl-standards`, not this atlas.
- R2 sense-alignment pages are archived snapshots until the rebuild contract is
  implemented.
- H5 anomaly candidates are review seeds, not automatic ghost-entry claims.

_Dr. Mārcis Gasūns_
