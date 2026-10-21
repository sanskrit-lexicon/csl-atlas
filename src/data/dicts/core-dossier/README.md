# Core dossier

28,524 lemmas attested in at least five of seven Cologne Digital Sanskrit
Lexicon dictionaries (MW, AP, PWG, PWK, WIL, VCP, SKD).

## Files

- `manifest.json` — record count, dictionary list, shard index, assumptions,
  warnings, and sample entries.
- `shards/<id>.json` — entries for one SLP1 initial. Each entry is
  `{l, c, d}`: normalized headword, dictionary count, and per-dictionary
  `[code, records, firstLine, gender]` tuples.
- `.source.json` — frozen-build provenance: `csl-orig` revision, atlas
  revision, builder, and SHA-256 hashes of every payload file.

## Provenance and licence

Built by `npm run build-dict-comparison` from `csl-orig` `v02` revision
`f4c08c578b330e2379e38f54d3a541f1564b8eee` at atlas revision `12bd3d1`. The
dataset is CC BY-SA 4.0, inherited from `csl-orig`. See `.source.json` for the
exact hashes.

## Cite this dataset

- **Version:** dataset 1.0.0, repo release `v0.20.0`
- **DOI (this version):** [10.5281/zenodo.23536487](https://doi.org/10.5281/zenodo.23536487)
- **DOI (concept):** [10.5281/zenodo.21419691](https://doi.org/10.5281/zenodo.21419691)
- **Licence:** CC BY-SA 4.0
- **OntoLex profile:** [docs/ONTOLEX_PROFILE_CORE_DOSSIER.md](../../../../docs/ONTOLEX_PROFILE_CORE_DOSSIER.md)
- **Data statement:** [docs/DATA_STATEMENT_CORE_DOSSIER.md](../../../../docs/DATA_STATEMENT_CORE_DOSSIER.md)

Cite the version DOI for this release; the concept DOI always resolves to the
latest tagged release.

## Limits

The dossier carries no senses, definitions, etymology, or citation links. It is
a coverage table, not a dictionary. See the data statement for the full list.
