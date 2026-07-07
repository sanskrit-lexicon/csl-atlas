# What the Sanskrit lexicographic tradition cites: a citation-frequency graph of `<ls>` source tags across 11 Cologne dictionaries

_Created: 06-07-2026 · Last updated: 06-07-2026_

**Status: readiness 2/5 (skeleton).** The dataset is built and committed (data 4/5); the
prose is an outline (1/5). This file forces the data inventory before the writing.

## Claim

*The Cologne Sanskrit dictionaries, read together through their `<ls>` source-citation tags,
expose a shared canon: a small set of texts (the Mahābhārata, Rāmāyaṇa, Ṛgveda, Manusmṛti,
Amarakoṣa …) is cited across nearly every dictionary, while each lexicon also leans on
idiosyncratic authorities that mark its tradition — and this citation profile separates the
Vedic, classical-kāvya, and Buddhist lexica quantitatively.* The frequency graph over 828,505
canonicalized citations from 11 dictionaries is the evidence.

## Data inventory

Each intended result → the committed artifact that backs it. Gaps are the work plan.

| Intended result | Backing artifact | Status |
|---|---|---|
| The graph itself: which text each dict cites, how often | [`data/citations/ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv) (1,707 edges) | ✅ exists (PR #220) |
| Canonical text nodes + variant forms | [`data/citations/ls_citation_nodes.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nodes.tsv) (912 texts) | ✅ exists |
| Coverage / resolution rate per dict (11 dicts, 57.8%) | [`README.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/README.md) coverage table | ✅ exists |
| MW non-text-marker filter (audit trail) | [`data/citations/ls_citation_nontext_filtered.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nontext_filtered.tsv) | ✅ exists |
| Reproducible builder | [`data/citations/build_ls_citation_graph.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/build_ls_citation_graph.py) | ✅ exists |
| Cross-tradition ranking (universal vs idiosyncratic authorities) | [`citation_canon.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/citations/citation_canon.json) `topTexts` + `canonCurve`, rendered on [`/tools/citation-canon`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/citation-canon.md) | ✅ exists (H305): 608/912 texts single-dict, none in all 11; Rāmāyaṇa top by reach (9 dicts) |
| Canon TOPOLOGY test — nested core–periphery vs modular tradition communities (PH1 CANON-CORE) | [`scripts/build-citation-canon.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-citation-canon.mjs) → NODF + Barber modularity vs 1,000 degree-preserving nulls | ✅ exists (H305): **refuted-modular** — NODF 24.4 (< null 29.0, p=1.0), Q 0.50 (> null 0.43, p=0.001). §4 must frame traditions as separate citation communities, not shared-canon strata |
| Vedic vs classical vs Buddhist citation profiles | per-dict edges × a text→tradition tag; per-dict fingerprints already on [`/tools/citation-canon`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/citation-canon.md) | ⚠ tradition map still needs curating (agenda backlog #9, human-reviewed) — fingerprints exist, tradition tags do not |
| dict × text co-citation matrix / heatmap figure | live nested-order `cell` heatmap on [`/tools/citation-canon`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/citation-canon.md) | ✅ exists (H305) |
| Keyless-dict coverage (ieg/gra/ae/bor) | — | ❌ blocked: no abbreviation key; ieg is an epigraphic outlier (cites EI/SII, not texts) — enhancement, not a gate |
| Citable data release (Zenodo DOI) | — | ❌ needs `/data-release` before submission |

## Outline

- **§1 Introduction** — dictionaries as citation networks; the `<ls>` tag as a machine-readable
  source pointer; the question "what does the whole tradition quote?"
- **§2 Data & method** — `<ls>` extraction, per-dict abbreviation-key resolution, the MW
  non-text filter, the `? [Cologne Addition]` placeholder problem, key-borrow, canonical folding.
  (All committed; §2 is largely a write-up of the README.)
- **§3 The shared canon** — the most-cited texts across dicts; universal (`n_dicts` high) vs
  idiosyncratic (single-dict) authorities.
- **§4 Tradition profiles** — Vedic (mw/pwg Vedic layer) vs classical-kāvya (ap/ap90/lrv) vs
  Buddhist (bhs/pwkvn) citation signatures; the epigraphic outlier (ieg). **Now grounded
  quantitatively (H305, PH1 CANON-CORE, `/tools/citation-canon`): the matrix is significantly
  MODULAR, not a nested shared canon (Barber Q 0.50 > null 0.43, p=0.001; NODF 24.4 < null 29.0),
  so §4 should present the traditions as genuinely separate citation communities over a thin
  universal head, not additive strata of one canon.**
- **§5 Limitations** — resolution ceiling, title-synonymy tail, no per-locus resolution,
  MW's low text yield.
- **§6 Conclusion** — the citation graph as a reusable layer for descent/register studies (ties
  to A08/A10).

## Comparanda / literature

- **A08 (OBS-C, two citation registers)** and **A10 (Apparatus, not errors — shared-erroneous
  citations)** — the sibling csl-atlas citation work; this paper is the *frequency* layer they
  don't cover. Must be cited and demarcated (anti-salami).
- Citation-network / bibliometric methods on reference corpora (to name at draft time).
- Digital-humanities work on intertextuality in Sanskrit (e.g. Vedic/epic quotation studies) —
  the domain analog for "what a corpus quotes."

## Venue candidates

DH / computational-lexicography methods venue (DSH, *Cultural Analytics*) or a data-journal
(*Journal of Open Humanities Data*) paired with the Zenodo release. `/venue-scout` later.

## Provenance

Scaffolded 06-07-2026 by Opus 4.8 (`claude-opus-4-8`) under handoff
[H213](https://github.com/gasyoun/Uprava/blob/main/handoffs/H213-Opus_csl-atlas_ls_citation_graph_canonicalization_06.07.26.md);
dataset built + merged in [csl-atlas PR #220](https://github.com/sanskrit-lexicon/csl-atlas/pull/220).

_Dr. Mārcis Gasūns_
