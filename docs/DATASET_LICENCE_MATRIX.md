# Per-dataset licence matrix — what licence each `data/` family may carry, and why

_Created: 24-09-2026 · Last updated: 24-09-2026_

**This is a proposal, not an applied change.** No data file, sidecar, `LICENSE`,
`CITATION.cff` or `.zenodo.json` is edited by the pass that produced this document
([H5302](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5302-Opus_csl-atlas_dataset-licence-matrix-per-source_23.09.26.md)).
Every row states the upstream sources of one data family, the rights basis those sources
impose, the licence proposed for the derived files, and an exception flag. Applying any row
— writing a licence key into a data file, changing `LICENSE`, or minting a DOI — is separate
work that a human should authorise.

## The governing constraint, measured first

The repo's own [`LICENSE`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/LICENSE),
[`CITATION.cff`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/CITATION.cff) and
[`.zenodo.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.zenodo.json) all say
**CC-BY-SA-4.0**, and that is the only defensible whole-repo value:

1. **`csl-orig` is CC BY-SA 4.0** — probed 24-09-2026 in the local clone
   (`csl-orig/LICENSE`, "Attribution-ShareAlike 4.0 International"), confirming what this
   repo's own `LICENSE` preamble already asserts. Every dictionary-derived family here is an
   *adaptation* of that text (counts, fingerprints, concordances extracted from `v02/*.txt`),
   so **ShareAlike propagates**: CC BY 4.0 is *not* available for any family that reads
   `csl-orig`.
2. **`csl-guides` is CC BY-SA 4.0** (probed: `csl-guides/LICENSE`) — the abbreviations key
   behind [`data/citations/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/citations).
3. **DCS is CC BY-SA 4.0** (probed: `DCS/LICENSE`, "Creative Commons Attribution-ShareAlike
   4.0 International") — not the bare "CC BY" one atlas file records (see defect D1).

So the mission's hoped-for shape — "CC BY 4.0 where clean" — resolves to **CC BY 4.0 is
clean for exactly two families**, both of which contain no adapted dictionary text: the JSON
schemas and the pure edition-metadata inventory. Everything else is CC BY-SA 4.0 by
inheritance, and four families carry an exception on top of that.

**Zenodo posture** ([SanskritLexicography `CONTRADICTIONS.md` §17](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md),
ruled by MG 07-09-2026 via [H3961](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3961-Sonnet_SanskritLexicography_zenodo-governance-match-live-archival_02.09.26.md)):
repo-level Zenodo archival is the intended posture, because a GitHub release archive carries
only the *tracked* tree at the tag. That ruling transfers here with one condition worth
stating explicitly: **this repo's tracked tree redistributes no source dictionary text** —
the PD, Harivaṃśa, Mahābhārata and *Indische Sprüche* inputs all live outside it and only
derived numbers are committed. A repo-level deposit is therefore safe *as long as that stays
true*; the moment a source e-text is vendored into `data/`, §17's original worry (sweeping in
content we cannot redistribute) becomes live for csl-atlas too. §17's second half also
applies: a repo-level record does **not** give a dataset its own DOI, so a per-family
citable deposit would still be curated work.

## Coverage today

`python scripts/audit_dataset_licence_keys.py` (added by this pass, 24-09-2026):

- **130** JSON files under `data/` (excluding `*.source.json` provenance sidecars).
- **21** declare a top-level `license`/`licence` key — all of them `CC-BY-SA-4.0`,
  concentrated in [`data/lexico/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/lexico) (17),
  [`data/obs/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/obs) (3) and
  `data/etymology-oracle.json` (1).
- **109** declare nothing. The mint-time figure (18 of 172, 21-09-2026) counted the sidecars
  as well; the ratio is the same story either way — **~84% of data JSON is licence-silent**,
  and no CSV/TSV/Newick file carries a licence statement at all (that is 57 further files).

The gap is a *metadata* gap, not a rights gap: the repo `LICENSE` covers the tree. What is
missing is the per-file self-description a consumer of one downloaded JSON needs.

## The matrix

Rights basis = what the upstream permits, as probed. Proposed licence = the value a row's
files should declare. Flag: 🟢 clean · 🟠 condition attached · 🔴 unresolved conflict.

| # | Family | What it is | Upstream sources | Rights basis inherited | Proposed licence | Flag |
|---|---|---|---|---|---|---|
| 1 | [`data/citations/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/citations) | `<ls>` cross-dictionary citation-frequency graph (edges, nodes, unresolved, filtered) | `csl-orig` v02 `*.txt`; `csl-guides` abbreviations key (both revisions pinned in [`ls_citation_graph.source.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_graph.source.json)) | CC BY-SA 4.0 ×2 — adaptation, ShareAlike | **CC BY-SA 4.0** | 🟢 |
| 2 | [`data/dcs/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/dcs) | DCS lemma frequency-band summary (83,239 lemmas) | DCS 2021 snapshot (Oliver Hellwig), via `VisualDCS` | CC BY-SA 4.0 (probed `DCS/LICENSE`) | **CC BY-SA 4.0** | 🟠 D1 |
| 3 | [`data/forensic/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/forensic) | MW-vs-Petersburg descent evidence: citation inventories, concordances, order/omission tests, A50 ledger | `csl-orig`; GRETIL BORI Mahābhārata (via the [`SamudraManthanam`](https://github.com/gasyoun/SamudraManthanam) mirror); Kinjawadekar Harivaṃśa e-text (Chitrashala 1936, volunteer transcription); Cologne `boesp2` *Indische Sprüche* digitization; Argos offline MT for the F6 gloss lane | CC BY-SA 4.0 for the dictionary layer; e-text layers measured-not-redistributed | **CC BY-SA 4.0** | 🟠 E1, E2 |
| 4 | [`data/integrity/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/integrity) | `csl_atlas_review.pin.json` — SHA-256 pin over the review-report store | This repo only (hashes of own artifacts) | Own work | **CC BY-SA 4.0** (repo default) | 🟢 |
| 5 | [`data/L0/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/L0) | Convention/typology layer: fingerprints, distances, trees, GQD validation, Patel-annotation scaffold and assignments | `csl-orig`; the label taxonomy of Patel 2016 (see [`docs/L0_PATEL_ANNOTATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/L0_PATEL_ANNOTATION.md)); our own annotation decisions | CC BY-SA 4.0; taxonomy labels are scholarly categories, not copied text | **CC BY-SA 4.0** | 🟠 E3 |
| 6 | [`data/lexico/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/lexico) | Microstructure + kośa layer: profiles, xref lineage, semantic fields, R2 sense data, kośa macrostructure model | `csl-orig`; **AMAR** (Amarakośa `amar.txt`, mirrored locally) | CC BY-SA 4.0 for `csl-orig`; **AMAR's own licence is contradictory across four surfaces** | **CC BY-SA 4.0** *pending E4* | 🔴 E4 |
| 7 | [`data/megastructure/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/megastructure) | Per-dictionary edition/imprint metadata + scan-page inventory (`mw.json`, `skd.json`, `scan_inventory.tsv`) | Title-page OCR of Cologne scan sets; bibliographic facts | Facts + short captions; no scan image is redistributed (filenames only) | **CC BY-SA 4.0** | 🟠 E5 |
| 8 | [`data/metalex/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/metalex) | L8 entry-level scan-link census (which entries resolve to a scan page) | `csl-orig` entry structure + Cologne scan directory listings | CC BY-SA 4.0; link/filename census only | **CC BY-SA 4.0** | 🟠 E5 |
| 9 | [`data/obs/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/obs) | Citation registers, headword collapse/multiplicity, siglum-family candidates | `csl-orig` v02 | CC BY-SA 4.0 — adaptation | **CC BY-SA 4.0** (already declared in 3 files) | 🟢 |
| 10 | [`data/parse-rules/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/parse-rules) | Per-dictionary MUDIDI Pass-1 parse-rules (field inventory, abbreviations, entry structure) for 12 dictionaries | `csl-orig` v02 `*.txt`; the *object shape* of the [MUDIDI](https://github.com/DavidSamuell/MUDIDI) benchmark; MDF mapping table from [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards) | CC BY-SA 4.0 for the extracted content; the borrowed shape is a schema, not data | **CC BY-SA 4.0** | 🟠 E6 |
| 11 | [`data/pd/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/pd) | PD × DCS corpus-coverage: siglum inventories, crosswalk, metrics | **Poona Dictionary `pd.txt`** (read from a local `external_src` path, never committed here); DCS 2021/2026 inventories | DCS CC BY-SA 4.0; **PD upstream rights unverified** | **CC BY-SA 4.0** *for the derived measurements* | 🔴 E7 |
| 12 | [`data/schema/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/schema) | JSON Schemas (`kosa-macrostructure`, `megastructure-component`, `review-report`) | Own work — no dictionary content | None inherited | **CC BY 4.0** (or CC0) — the one genuinely clean family | 🟢 |
| 13 | [`data/snapshots/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/snapshots) | Frozen `headwords.json` at 2026-05-07 (reproducibility baseline) | `csl-orig` v02 (counts per dictionary) | CC BY-SA 4.0 — adaptation | **CC BY-SA 4.0** | 🟢 |
| 14 | `data/` root files | [`dictionary_inventory.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary_inventory.csv), [`dictionary-coverage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary-coverage.json), [`headwords.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/headwords.json), [`etymology-oracle.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/etymology-oracle.json), `sanhw1_*` cladistics | `csl-orig` v02 + its `etymology_stats`; `csl-observatory` snapshot `sanhw1.txt`; bibliographic facts for the inventory | CC BY-SA 4.0 for everything derived from dictionary text | **CC BY-SA 4.0**, except `dictionary_inventory.csv` → **CC BY 4.0** (bibliographic facts only) | 🟢 |

Every family under `data/` is covered: 13 directories plus the root file group.

## Exceptions, in the order they should be resolved

### 🔴 E4 — AMAR's licence is stated four ways, and one of them is copyleft software

Probed 24-09-2026 in the local `sanskrit-lexicon/AMAR` clone (remote confirmed via
`git remote -v`):

| Surface | Value |
|---|---|
| `AMAR/LICENSE` (339 lines) | **GNU General Public License, Version 2, June 1991** |
| `AMAR/README.md` licence row | CC-BY-SA-4.0 |
| `AMAR/CITATION.cff` | CC-BY-SA-4.0 |
| This repo's [`data/lexico/kosa_model_measures.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/kosa_model_measures.json) `sources.AMAR.licence` | **GPL-3.0** |

Three distinct values across four surfaces, and the atlas records a fourth reading (GPL-3.0)
that matches none of them. The same sidecar block also names the upstream
`sanskrit-kosha/kosha`, while the clone's actual remote is `sanskrit-lexicon/AMAR`.

The GPL-3.0 reading has already propagated beyond the sidecar: it appears in published prose
in [`docs/articles/paper_kosha_macrostructure.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_kosha_macrostructure.md),
on the reader-facing page [`src/paper/kosa-macrostructure.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/paper/kosa-macrostructure.md),
and in [`docs/EMBEDDING_RETRIEVAL_LANE_PLAN.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EMBEDDING_RETRIEVAL_LANE_PLAN.md).
Whatever E4 resolves to, those three surfaces are part of the fix.

Why it matters here: `kosa_model_measures.json` and `kosa_model_amar_sample.json` declare
themselves `CC-BY-SA-4.0` while recording a **GPL** source. GPL and CC BY-SA 4.0 are both
copyleft but not mutually compatible in that direction — you cannot relicense GPL material
as CC BY-SA. If the GPL reading is the true one, the AMAR-derived rows in family 6 are
mislabelled today.

Mitigating fact, not a resolution: what the atlas extracts from `amar.txt` is *structural
measurement* (varga counts, grouping model, gender marking), not verse text, and a
measurement over a work is not a derivative of the software licence attached to its
repository. That argument is strong enough to keep shipping and weak enough that it should
be written down rather than assumed.

**What a human should decide:** ask the AMAR maintainers which file is authoritative (the
GPLv2 `LICENSE` blob or the CC-BY-SA-4.0 README/CITATION), then either correct the atlas
sidecar to the ruled value or carve the AMAR-derived measures out of the CC-BY-SA-4.0
declaration. Until then family 6's proposed licence is *pending*, not settled.

### 🔴 E7 — the Poona Dictionary source has no verified rights statement

[`scripts/pd_extract_sigla.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_extract_sigla.py)
reads `pd.txt` from a local `SanskritSpellCheck/external_src/pd/` path via the `PD_TXT`
environment variable. That file is **not** in this repo and not in `csl-orig`'s v02 tree; no
licence statement accompanies it here. The *Sanskrit Dictionary on Historical Principles*
(Deccan College, Poona) is a 20th-century work still plausibly in copyright.

What we actually ship is derived: siglum frequency counts, a 118-row text crosswalk, four
headline metrics, and three sample *contexts* per siglum in
[`pd_siglum_raw.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_siglum_raw.tsv).
The counts and the crosswalk are facts about the work. **The sample contexts are short
excerpts of it** — that is the only place in `data/` where source text from a
rights-unverified work is committed, and it is the one line item worth checking before any
dataset release of family 11.

Per the org's standing policy, rights *uncertainty* is not a stop
([STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md](https://github.com/gasyoun/Uprava/blob/main/docs/STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md)):
record the known facts and proceed. This row does exactly that. **What a human should
decide:** whether the three-context excerpt column stays as-is, gets truncated, or is
dropped from any citable release of family 11.

### 🟠 E1 — e-texts are measured, never redistributed (family 3)

The Harivaṃśa work already states its own rule and follows it:
[`harivamsa_vulgate_concordance.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/harivamsa_vulgate_concordance.csv)
is 15,364 rows of **numbers only, no verse text — explicitly for rights reasons**
([census §"Rights"](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md)).
The same holds for the GRETIL BORI Mahābhārata lane (offsets, presence flags, resolution
verdicts) and for `boesp2` (verdict rows, not *Sprüche* text). **The condition on family 3's
CC BY-SA 4.0 is therefore behavioural, not legal: it holds only while no future forensic
script commits verse text.** Any new `data/forensic/` artifact that would carry source
verses needs a rights check before it lands.

### 🟠 E2 — the F6 gloss lane is machine-translation output (family 3)

[`f6_gloss_translation.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f6_gloss_translation.csv)
holds PWG German glosses translated offline with Argos (`f6_report.json` `method`). The input
is CC BY-SA 4.0 Cologne text; the MT step is a mechanical transformation and adds no new
upstream rights holder. Worth a one-line provenance note in the file, no licence change.

### 🟠 E3 — Patel 2016 supplies labels, not data (family 5)

`data/L0/patel2016_assignments.csv` and its scaffold use the *taxonomy labels* of a published
paper; the assignments themselves are our own coding, with the discriminating evidence
carried in `patel_evidence.json`. Category names are not protectable expression, so no
licence condition follows — but the attribution belongs in the file, and today it lives only
in [`docs/L0_PATEL_ANNOTATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/L0_PATEL_ANNOTATION.md).

### 🟠 E5 — scan metadata rides on images we do not own (families 7, 8)

`scan_inventory.tsv` and the L8 census carry scan-page **filenames, refs and short captions**
from the Cologne scan sets, plus title-page OCR in `mw.json`/`skd.json`. No image bytes are
committed, and short bibliographic captions are facts. The condition: if a future page ever
embeds or mirrors the scan images themselves, that is a different rights question from this
metadata and needs Cologne's terms checked first.

### 🟠 E6 — MUDIDI contributes a schema shape (family 10)

`data/parse-rules/*.json` emit `schema: mudidi-parse-rules/0.1`, a shape borrowed from the
[MUDIDI](https://github.com/DavidSamuell/MUDIDI) benchmark; all the *content* is extracted
from `csl-orig`. A schema shape is an interface, not licensed data. If the parse-rules are
ever contributed *back* to MUDIDI as a Sanskrit subset (an explicit option in
[`data/parse-rules/README.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/parse-rules/README.md)),
MUDIDI's own licence becomes the governing question for that contribution — not for what we
publish here.

## Metadata defects found while building the matrix

These are wrong *statements*, independent of the licensing decisions above.

- **D1 — `data/dcs/dcs_lemma_summary.json` records DCS as "CC BY".** DCS ships **CC BY-SA
  4.0** (`DCS/LICENSE`, probed 24-09-2026). The `bandingRule` string understates the
  upstream's ShareAlike condition. One-word fix, but it is the string a downstream consumer
  would read.
- **D2 — the AMAR source block in `data/lexico/kosa_model_*.json` names the wrong upstream**
  (`sanskrit-kosha/kosha` vs the clone's real remote `sanskrit-lexicon/AMAR`) **and a licence
  value (GPL-3.0) that appears on none of AMAR's four surfaces.** See E4.
- **D3 — 109 of 130 data JSON files, and all 57 CSV/TSV/Newick files, carry no licence
  statement.** The repo `LICENSE` covers them; a single downloaded file does not say so.

## Recommended application order (not executed here)

1. Fix D1 and D2 — they are factual corrections, cheap, and they block nothing.
2. Ask AMAR upstream the E4 question; record the answer in
   [`SanskritLexicography/CONTRADICTIONS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
   as a new section, since it is exactly that registry's shape (four surfaces, three values).
3. Decide E7's excerpt question before any family-11 dataset release.
4. Only then stamp licence keys family-by-family, following this matrix's proposed column —
   and add the stamp to each builder script so new outputs inherit it, rather than
   back-filling by hand.
5. Leave `LICENSE`, `CITATION.cff` and `.zenodo.json` alone: CC-BY-SA-4.0 is already the
   correct whole-repo value and every step above is a per-file refinement inside it.

## Reproduce

```sh
python scripts/audit_dataset_licence_keys.py
```

Prints the file count, every file that declares a licence key with its value, and the
undeclared count per family — the three numbers in § Coverage today.

_Гасунс_
