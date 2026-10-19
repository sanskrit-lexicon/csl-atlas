_Created: 19-10-2026 · Last updated: 19-10-2026_

# Data statement — csl-atlas core dossier

This statement follows the Bender & Friedman (2018) data-statement shape and
the fields the atlas research agenda requires for a released dataset. It
describes the dataset, not the whole atlas.

## Dataset identity

| Field | Value |
|---|---|
| Name | csl-atlas core dossier |
| Version | 1.0.0 |
| Repo release | `v0.20.0` |
| Path | `src/data/dicts/core-dossier/` |
| Size | 28,524 lemmas; 48 JSON shards plus one manifest (4.0 MB) |
| Frozen data revision | [`12bd3d1`](https://github.com/sanskrit-lexicon/csl-atlas/commit/12bd3d1c7e698d9c508267ceac4ac2b834db1f88) |
| Provenance | [`src/data/dicts/core-dossier/.source.json`](../src/data/dicts/core-dossier/.source.json) |
| Profile | [`docs/ONTOLEX_PROFILE_CORE_DOSSIER.md`](ONTOLEX_PROFILE_CORE_DOSSIER.md) |
| Licence | CC BY-SA 4.0 |

## Motivation and intended audience

The dossier answers one question cheaply and reproducibly: **which well-attested
Sanskrit headwords are shared across the Cologne Digital Sanskrit Lexicon
dictionaries, and how much dictionary material does each dictionary carry for
them?** It exists so that a reader can move from a normalized headword to the
first source line of every dictionary that attests it, without downloading the
whole `csl-orig` corpus.

Intended audiences:

- Sanskritists and lexicographers checking cross-dictionary attestation.
- Digital-humanities researchers who need a compact, citable coverage table.
- Ontology and standards engineers who need a real retrodigitized dataset to
  test OntoLex-Lemon/DMLex/TEI-Lex0 mappings.
- Teachers and students using the Reader Lookup and Lemma Dossier pages.

It is **not** a dictionary, a critical edition, a sense inventory, or a
translation resource.

## Language and writing system

- Headwords (`entries[].l`) are normalized **SLP1** ASCII transliteration.
- No Devanagari, IAST, IPA, or pronunciation field is present.
- Dictionary names and grammar tokens are abbreviated in ASCII.
- The dataset itself contains no running definition text. The companion R2
  sense file used for the profile example does contain mixed
  Sanskrit/English source text; it is a separate dataset with its own
  provenance.

## Provenance and curation

The dataset is machine-built from the seven target dictionaries in
[`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig) `v02`:
MW, AP, PWG, PWK, WIL, VCP, SKD. The builder is
`scripts/build-dictionary-comparison.mjs`, invoked as
`npm run build-dict-comparison`.

Method in one paragraph: parse each dictionary's `<L>`/`<LEND>` records,
normalize headwords, group by normalized headword, keep lemmas present in at
least five of the seven dictionaries, then record per dictionary the number of
records, the first source line of the block, and the `<lex>` grammar token.
Lookup is exact/prefix over the normalized key, not substring search. The
frozen build used `csl-orig` revision
`f4c08c578b330e2379e38f54d3a541f1564b8eee` (2026-09-24).

Curation rationale: five-of-seven is the smallest threshold that still gives a
cross-dictionary claim rather than a single-dictionary lookup. It yields 28,524
lemmas out of the much larger full corpus. The threshold is declared in
`manifest.minDicts`; the omitted tail is a known limitation, not a hidden
filter.

## Licence and attribution

The dataset is **CC BY-SA 4.0**, inherited from `csl-orig` and matching the
repository `LICENSE`, `CITATION.cff`, and `.zenodo.json`. Reuse requires
attribution to the Cologne Digital Sanskrit Dictionaries project and to
csl-atlas, and derivative datasets must carry the same licence. The sidecar
declares the licence and URL explicitly.

## Known limitations

1. **No senses or definitions.** The dossier has no `ontolex:Sense` material;
   the profile demonstrates a Sense only through a clearly labelled companion
   join, not from this dataset.
2. **Coverage, not completeness.** Only lemmas in at least five of seven
   dictionaries are included. The long tail needs a search backend and is not
   in this release.
3. **No homonym resolution.** `l` is a normalized headword. Homonyms and
   cross-dictionary homographs can collapse into one row; `records` counts the
   source records but does not identify them individually.
4. **Lossy grammar tokens.** `gender` is a sorted concatenation of atomic
   tokens (`m`, `f`, `n`, `adj`, `ind`). Empty and composite cases are real;
   `adj` and `ind` are parts of speech, not genders. Do not read the token as a
   full morphological analysis.
5. **Source line, not citation.** `firstLine` points into a `csl-orig` `v02`
   plain-text file. It is stable only for that revision and is not a scan page
   or a permanent bibliographic citation.
6. **No etymology, examples, citation links, review status, or evidence
   labels.** Those live in other atlas datasets or not at all.
7. **Machine-only curation.** No row in this dataset is human-reviewed. The
   atlas has human review queues elsewhere; they do not overlay this dataset.
8. **Transliteration bias.** SLP1 normalization can merge surface variants that
   a Devanagari or IAST reader would distinguish. Ambiguous sandhi is not
   resolved.
9. **Build-time metadata.** The build timestamp and counts describe the frozen
   build; re-running the builder against a newer `csl-orig` will change them.

## Maintenance

- Regenerate with `npm run build-dict-comparison` from a pinned `csl-orig`
  checkout; record the new `csl-orig` revision in `.source.json`.
- Do not hand-edit shards. If a correction is needed, fix the builder or the
  upstream source and rebuild.
- Report data issues at
  <https://github.com/sanskrit-lexicon/csl-atlas/issues>.
- Versioning is per repo release; dataset-level changes require a new
  `.source.json` version and a new release tag.
- The normative RDF exporter is maintained in
  [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards), not
  here.

## Human/machine review split

| Layer | Who/what | Status |
|---|---|---|
| Parsing, normalization, thresholding | machine, deterministic builder | complete for this release |
| Grammar-token interpretation | machine extraction from `<lex>` | complete, lossy |
| Sense/definition mapping | not in this dataset | out of scope |
| Row-level human review | none | 0 of 28,524 rows |
| Release/profile review | human reviewer per handoff verifier | pending PR review |

## Citation

Use the release citation block in the repository
[`README.md`](../README.md#cite-this-dataset) and the concept DOI
[`10.5281/zenodo.21419691`](https://doi.org/10.5281/zenodo.21419691). The
version DOI is minted by Zenodo when the `v0.20.0` GitHub release is published;
the release-candidate note
[`docs/RELEASE_CANDIDATE_CORE_DOSSIER.md`](RELEASE_CANDIDATE_CORE_DOSSIER.md)
records the blocker and the post-merge steps.
