# DH improvement memo — the correction-data feed into csl-atlas

_Created: 07-07-2026 · Last updated: 07-07-2026_

**What this is.** The atlas-facing half of the
[H271](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H271-Fable_csl-corrections_correction-hypotheses-atlas-DH-ACL_07.07.26.md)
design memo: how the [`csl-corrections`](https://github.com/sanskrit-lexicon/csl-corrections)
audit-trail corpus becomes an atlas data feed, plus the external-DH / internal-reuse
recommendations that raise the atlas's scientific and pedagogical standard. The correction-data
hypotheses, census figures, ACL method table, and ranked backlog live in the anchor memo:
[`csl-corrections/docs/HYPOTHESES_AND_VIZ_MEMO.md`](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/HYPOTHESES_AND_VIZ_MEMO.md).

**Boundary.** The *general* csl-atlas research agenda is owned by the queued sibling handoff
[H273](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H273-Fable_csl-atlas_atlas_research_agenda_07.07.26.md)
(its deliverable was absent from `docs/` at write time — verified 07-07-2026). This memo stays
in the H271 lane: **what correction data supplies to the atlas**, and defers everything else to
H273. Memo only — no pages, data, or scripts were changed.

**Provenance.** Written 07-07-2026 by Fable 5 (`claude-fable-5`) from a same-day atlas inventory
by an Explore subagent (Fable 5 `claude-fable-5`, inherited), against `origin/main` at commit
`a78b7ee`.

---

## 1. Where the atlas stands today (relevant facts only)

- **35 tool pages** under [`src/tools/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/src/tools),
  strong on lexical-semantic, lineage/phylogenetic, structural, and review-queue themes;
  Observable Plot + d3 only (no Leaflet/geo — verified against `package.json` and all authored
  pages).
- **csl-corrections is already an input, but only to scripts.**
  [`scripts/forensic/f4_shared_corrections.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f4_shared_corrections.py)
  and [`f4b_ahlborn_nulltest.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f4b_ahlborn_nulltest.py)
  read it into
  [`data/forensic/shared_corrections.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/shared_corrections.csv)
  (290 rows) — no live page ingests corrections (`grep csl-corrections src/` = zero hits).
- **No atlas layer keys on (dict, L-number).** `content_lift.csv` and the citation TSVs key on
  dict-pairs or dict×text; the forensic tables key on SLP1 headword + dict. A correction feed
  therefore needs either an L-number-aware new table or a headword-key join — the anchor memo's
  `correction_loci.tsv` (its §5.1) provides both keys at once (`<L>` + `<k1>`).
- **Governance assets already exist and must be used as-is:** the four evidence grades in
  [`docs/EVIDENCE_LABELS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS.md)
  (`observed`/`derived`/`inferred`/`reviewed`), the mandatory Trust Blocks in
  [`docs/CHART_TRUST_TEMPLATE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CHART_TRUST_TEMPLATE.md),
  the CSV-download-per-table rule (repo `CLAUDE.md`, helper
  [`src/lib/csv-download.js`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/csv-download.js)),
  and the one-owner-repo rule in
  [`docs/HYPOTHESIS_INDEX.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md).
- Known reproducibility debt worth honoring in anything new:
  [`data/L0/content_lift.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/content_lift.csv)
  is flagged unreproducible (generator never committed). Every new feed ships its committed
  builder + `.source.json` sidecar, per existing convention.

---

## 2. The feed contract

One derived table, built in csl-corrections (anchor memo §5.1, backlog #1), consumed here
read-only, mirroring the
[`VISUALDCS_CONSUMPTION_CONTRACT.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/VISUALDCS_CONSUMPTION_CONTRACT.md)
pattern:

- **`correction_loci.tsv`** — dict, `<L>`, `<pc>` page, column, `<k1>`/`<k2>`, source line,
  batch/date, process (bulk/human), directive, tag-context, old/new strings. Keys: (dict, L)
  primary; `slp1_form_key(k1)` (via vendored
  [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util) v0.4.0 — the atlas
  already re-exports it as
  [`src/lib/source-iast.js`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/source-iast.js))
  for joins to the forensic headword tables.
- Atlas-side: one `scripts/build-correction-feed.mjs` that filters/aggregates the TSV into
  page-sized JSON, with `.source.json` provenance; no direct sibling-path reads from pages.
- Evidence grades carried per field: loci and old/new are `derived` from `observed` headers;
  cross-dict matches are `inferred` until reviewed; anything a human confirms is promoted
  `reviewed`. Corrector identities stay out of the public feed (personal data — pseudonymized
  aggregate only, `/publish-safety-check` before publishing any corrector-level page).

---

## 3. Correction-fed pages (specs)

Each page: existing page it extends, feed, chart form, Trust Block claim. All Observable Plot,
CSV download on every table.

1. **Correction-locus heatmap** (new page `tools/correction-loci.md`). Per dict: page-position ×
   column density of corrections, bulk/human toggle. Extends the
   [`source.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/source.md)
   raw-line viewer (deep-link a cell → the source lines). Trust claim: "where reported errors
   sit in the printed edition" (`derived`; reader-bias caveat = anchor memo C6 confound).
2. **Editorial-overlay axes on the per-dict radar** (unblocks
   [`METALEXICOGRAPHY_ROADMAP.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/METALEXICOGRAPHY_ROADMAP.md)
   §2.6 + §3, currently HOLD): corrections per 1k entries, component mix, human-share,
   fix-latency median. The other radar axes (markup density etc.) stay HOLD — not correction-gated.
3. **Shared-corrected-error overlay** on
   [`lineage-sankey.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/lineage-sankey.md) /
   [`xref-lineage.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/xref-lineage.md):
   edge weight = shared-corrected-error count beyond confusion-rate expectation (anchor memo C3).
   Extends APPARATUS-NOT-ERRORS (owner stays csl-atlas per HYPOTHESIS_INDEX); `inferred` until
   the null model is reviewed.
4. **Correction-front strip** (small multiple per dict, time × component, era-split 2014–2019 /
   2019–2026): the atlas-side rendering of OBS-T's diachronic finding plus the anchor memo's C2
   process split. Data owner remains
   [`csl-observatory`](https://github.com/sanskrit-lexicon/csl-observatory) (MW-ATTENTION
   boundary respected — atlas renders, observatory owns the attention/event data).
5. **Maker QA worklist enrichment** (existing
   [`RESEARCH_LAYER_ROADMAP.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/RESEARCH_LAYER_ROADMAP.md)
   §4.2 lane): add "correction pressure" (recent human corrections near a locus) as a
   prioritization signal in the existing review queues — no new page, one column.

Pedagogical framing (the personas the atlas already serves): the heatmap doubles as a
proofreading treasure map for student contributors; the radar's editorial axes answer the
dictionary-chooser question "how actively maintained is this dict?"; the correction-front strip
is a ready-made lesson in how digitization projects mature.

---

## 4. External DH standards → concrete atlas adoptions

Reusing H265's standards research
([`ACL_DH_COMPATIBILITY_ANALYSIS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md))
plus the live ACL fetch (anchor memo §4). Modelling recommended here; **export builds route to
[`csl-standards`](https://github.com/gasyoun/csl-standards)** per
[`docs/TEI_ONTOLEX_MIGRATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/TEI_ONTOLEX_MIGRATION.md)
(already just a pointer there — hub registration of that ownership is missing, flagged in §5).

| Standard / project | What they do | Atlas adoption |
|---|---|---|
| OntoLex-Lemon — CDSL already modelled by Mondaca & Rau 2020 ([2020.ldl-1.2](https://aclanthology.org/2020.ldl-1.2/)) | RDF model of our exact corpus | keep atlas JSON field names mappable to it (lemma/sense/citation granularity); export = csl-standards |
| TEI Lex-0 (per H265 §3: full-entry standard; overkill for lists) | interchange for dictionary entries | same posture as H265: documented TSV/JSON schemas now, TEI wrapping only when a consumer exists |
| OntoLex-FrAC | frequency/attestation/corpus links | when DCS-JOIN lands (Type-3 hypothesis, VisualDCS-owned), model attestation fields FrAC-compatibly |
| ELEXIS MWSA ([2020.lrec-1.395](https://aclanthology.org/2020.lrec-1.395/)) | sense-alignment relation inventory (=, ⊃, ⊂, ~) | adopt the relation vocabulary in `sense-divergence.md` worklists instead of ad-hoc labels |
| Data statements (Bender & Friedman, per H265) + Responsible-NLP checklist | artifact documentation | one data statement per released atlas dataset; the Trust Block already covers most fields — add license + maintenance lines |
| Evidence grading (already native) | — | the atlas's `observed/derived/inferred/reviewed` ladder is *ahead* of most DH dictionary sites; keep it, and keep the CHART_TRUST_TEMPLATE `machine-reviewed`/`human-reviewed` distinction consistent with EVIDENCE_LABELS (naming divergence noted — one-line reconciliation edit, cheap win) |

Versioning/citability: atlas datasets that papers cite (forensic, L0, citations) should get
kosha manifest rows + eventual DOIs via `/data-release` — the correction feed enters the same
pipeline (manifest duty already assigned in the anchor memo §5).

## 5. Internal reuse — consume, don't rebuild

| Owned elsewhere | Asset | Atlas use |
|---|---|---|
| [`csl-observatory`](https://github.com/sanskrit-lexicon/csl-observatory) | OBS-T [`correction_events_release.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_release.csv) (52,498 rows) + schema | component labels, corrector stats, trends — §3.4 renders it; never recompute typology here |
| [`kosha`](https://github.com/gasyoun/kosha) | [`datasets.json`](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) manifest, [`lemma_frequency.tsv`](https://github.com/gasyoun/kosha/blob/main/data/frequency/lemma_frequency.tsv) (83,277 rows) | registration target for the feed; frequency joins for "is this a high-traffic lemma" context in dossiers |
| [`VisualDCS`](https://github.com/gasyoun/VisualDCS) | Fonetika grapheme/akshara frequencies, M9 `archive.sqlite` | confusion-vs-frequency normalization for the C4 matrices consumed by §3.3's null model |
| [`SanskritLexicography`](https://github.com/gasyoun/SanskritLexicography) | [`union_headwords.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv) (323k) | entry-count denominators for all densities |
| [`SanskritSpellCheck`](https://github.com/gasyoun/SanskritSpellCheck) | [`do_not_file_suppress.txt`](https://github.com/gasyoun/SanskritSpellCheck/blob/main/nochange/do_not_file_suppress.txt) (2,297 deliberate variants; already wired via [`scripts/lib/do-not-file-suppression.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/do-not-file-suppression.mjs)) | suppress deliberate-nonstandard spellings from every correction-derived error stat |
| [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util) v0.4.0 | transcoding + `slp1_form_key` + markup-aware display | the only sanctioned key-folding for all joins |

**Hub gap found while mapping:** TEI/OntoLex ownership by csl-standards is asserted in atlas
docs but absent from
[`Uprava/REUSE_INDEX.md`](https://github.com/gasyoun/Uprava/blob/main/REUSE_INDEX.md) /
[`PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md)
(grep TEI/OntoLex = zero hits) — one registration line to add at the next hub sync.

---

## 6. What this memo does NOT do

No general atlas agenda (H273's lane), no geographic layer (deferred by MG ruling 07-07-2026;
one `@DO` — the imprint-city list — mirrored to GTD), no TEI/RDF export build (csl-standards),
no attention/commit analytics (csl-observatory). Build order and effort/tier tags: anchor memo
§7 ranked backlog.

_Cross-links: anchor memo
[`csl-corrections/docs/HYPOTHESES_AND_VIZ_MEMO.md`](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/HYPOTHESES_AND_VIZ_MEMO.md) ·
series: H265 ✅, H269/H272/H273 queued at write time._

_Dr. Mārcis Gasūns_
