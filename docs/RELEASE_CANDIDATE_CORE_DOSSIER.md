_Created: 19-10-2026 · Last updated: 21-10-2026_

# Release record — csl-atlas core dossier v1.0.0 / repo v0.20.0

Status: **PUBLISHED.** This note records what the release contains, its DOI, and
how to verify it from the frozen data.

## What is frozen

| Item | Value |
|---|---|
| Dataset | `src/data/dicts/core-dossier/` |
| Dataset version | 1.0.0 |
| Release tag | [`v0.20.0`](https://github.com/sanskrit-lexicon/csl-atlas/releases/tag/v0.20.0) |
| Frozen data revision | [`12bd3d1`](https://github.com/sanskrit-lexicon/csl-atlas/commit/12bd3d1c7e698d9c508267ceac4ac2b834db1f88) |
| csl-orig revision | `f4c08c578b330e2379e38f54d3a541f1564b8eee` |
| Records | 28,524 lemmas |
| Provenance sidecar | `src/data/dicts/core-dossier/.source.json` |
| Payload tree SHA-256 | `5d88357ed16fb27f15a580e904bdd910d457d13d3a1e953788743dc2d5d9aa80` |
| Licence | CC BY-SA 4.0 |

## Release payload

- `docs/ONTOLEX_PROFILE_CORE_DOSSIER.md` — field mapping, worked `iti` example,
  no-equivalent list.
- `docs/DATA_STATEMENT_CORE_DOSSIER.md` — motivation, provenance, licence,
  limitations, maintenance, review split.
- `src/data/dicts/core-dossier/.source.json` — input/output hashes and pinned
  revisions.
- `src/data/dicts/core-dossier/README.md` — dataset-level citation block.
- `README.md` and `src/index.md` — "Cite this dataset" blocks.
- `CITATION.cff` and `.zenodo.json` — version `0.20.0`.
- `docs/DATASET_LICENCE_MATRIX.md` — core-dossier row.
- `csl-standards` issue [#165](https://github.com/sanskrit-lexicon/csl-standards/issues/165)
  — pointer naming the normative exporter owner.

## DOI

| DOI | Value | Check |
|---|---|---|
| Version (v0.20.0) | [`10.5281/zenodo.23536487`](https://doi.org/10.5281/zenodo.23536487) | `curl -I` returned HTTP/2 302 (2026-10-21) |
| Concept (all versions) | [`10.5281/zenodo.21419691`](https://doi.org/10.5281/zenodo.21419691) | `curl -I` returned HTTP/2 302 (2026-10-21) |

Zenodo record: <https://zenodo.org/records/23536487> — version `0.20.0`,
published 2026-10-21, licence `cc-by-sa-4.0`, archive
`sanskrit-lexicon/csl-atlas-v0.20.0.zip`.

The version DOI above was minted by Zenodo when the `v0.20.0` GitHub release
was published. Do not mint DOIs manually and do not tag non-merged commits.

## Verification before citing

1. `curl -I https://doi.org/10.5281/zenodo.23536487` returns 200/302.
2. `git show 12bd3d1 -- src/data/dicts/core-dossier/manifest.json` confirms the
   frozen data revision.
3. Recompute `.source.json` hashes with the commands in the profile §8.
4. Open `docs/ONTOLEX_PROFILE_CORE_DOSSIER.md` §7 and confirm the `iti` tuple
   matches `shards/69.json` exactly.
5. Confirm the profile names the no-equivalent fields (sense text, coverage
   count, record count, composite grammar tokens, source-line citation,
   transliteration, entry identity).

## Risks

- The dataset has no sense rows; an exporter must not fabricate
  `ontolex:Sense` from it. The profile makes this explicit.
- `package.json` version is `0.18.0`, while release tags are `0.19.x` and this
  release is `0.20.0`. The release metadata is tag-driven; bumping
  `package.json` is out of H7102 scope.
