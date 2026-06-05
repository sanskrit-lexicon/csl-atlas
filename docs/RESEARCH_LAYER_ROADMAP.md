# CDSL Research & Practitioner Layer — Roadmap

**Version**: 1.2 · **Date**: 2026-05-31 · **Owner**: M. Gasūns + Claude
*v1.1: R2 sense-splitter design decided (§5.1) — heuristic per-dict, full corpus, Sanskrit-anchored alignment; A6/A7 closed.*
*v1.2: historical round-2 decisions (§7) — DCS frequency join, main-dashboard hosting, H1 first, Amarakośa-native field scheme; DCS ownership superseded by v1.3 boundary note.*
*v1.3 boundary update 2026-06-04: DCS/corpus frequency joins are external
VisualDCS work, not atlas generation work.*
**Companion to**: [`BOUNDARY_RULES.md`](BOUNDARY_RULES.md), [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md) (genealogy/phylogeny), [`MICROSTRUCTURE-MACROSTRUCTURE.md`](MICROSTRUCTURE-MACROSTRUCTURE.md) (structure typology), [`METALEXICOGRAPHY_ROADMAP.md`](METALEXICOGRAPHY_ROADMAP.md).

This stream is **additive**. The existing program is researcher-facing (papers M/L/H + a 50-viz catalog). This roadmap turns those analyses into a **practitioner layer** — usable tools for three audiences — and adds new testable hypotheses and visualizations. Two working prototypes ship with it.

---

## 0. What already exists (do not duplicate)

- **Genealogy / phylogenetics** — convention fingerprints, cladograms, lemma-overlap, the unified inheritance score (`LEXICOGRAPHY_ROADMAP.md`, phases L0–L10; executed L0 in `scripts/L0/`, `data/L0/`).
- **Micro/macro typology** — 24 verb + 10 nominal + 20 macrostructure dimensions, a 50+ visualization catalog (`MICROSTRUCTURE-MACROSTRUCTURE.md`).
- **Project measurement** — activity/community/coverage KPIs and GitHub/org dashboards now belong in `csl-observatory`.

What this roadmap **adds**: end-user tools (students + makers), new hypotheses, new visualizations, and two runnable prototypes.

---

## 1. Prototypes shipped this round

Both read sibling `csl-orig` directly, no network, stdlib only; each regenerates committed data + a self-contained HTML.

### 1.1 MICRO — one lemma across dictionaries
`scripts/lexico/micro_entry.py` → [`data/lexico/micro_gam.json`](../data/lexico/micro_gam.json) + `.html`.
A feature matrix (dicts × 12 microstructure features) plus side-by-side entry text for any headword.

**Real findings for `gam` (8 dicts):**
- **PWG** `gam` = **100,962 chars, 1,299 citations** — vs **MW** 7,132 / 115. Confirms PWG's citation-dense, preverb-rich signature.
- **MW72** and **BOP** carry **etymology** (cognates) but **zero `<ls>`** — different citation convention, not absence of sourcing.
- **AP**'s extracted `gam` is a **69-char stub** — likely a pointer or a parsing edge case → a concrete data-quality flag for makers.

### 1.2 MACRO — structural profile of every dictionary
`scripts/lexico/macro_profile.py` → [`data/lexico/dict_profiles.csv`](../data/lexico/dict_profiles.csv) + `.html`.
Samples N entries **stratified across the whole alphabet** of all 43 canonical sources; heatmap of dicts × {entry size, citation density, %cited, %etymology, %cross-ref, %homonym, %grammar}.

**Real findings (stratified sample, 3,000 entries each):**
- A **Western-tagged cited cluster** (`<ls>`) — PWG 94%, SCH 90%, BEN 79%, AP90 32% — **and** an equally citation-dense **indigenous cluster**: **VCP 95% cited, SKD 51%**, via quotations (`“…”`) attributed to abbreviated authorities (`jE0`=Jaimini, `BA0`=Bhāṣya, `amara0`=Amara) closed with `iti`, carrying **no `<ls>` tag**. *(Correction: an earlier `<ls>`-only detector mis-reported SKD/VCP as "citation-free 0%" — they are among the most citation-dense; see Caveats.)*
- **WIL** 99.6% grammar-marked; **BHS** 92% cited + 48% cross-ref; specialized indexes (**SNP, IEG, MCI, INM**) are cross-ref-heavy.
- The structural axes (**citation style × grammar-marking**) separate the Western-tagged, indigenous-quotation, and index traditions — a cheap structural corroboration of the genealogy in `LEXICOGRAPHY_ROADMAP.md`.

---

## 2. New hypotheses (testable on the corpus)

| # | Hypothesis | Signal / method | Audience | Status |
|---|---|---|---|---|
| **H1** | **Sense-granularity inflates over editorial time** — later dicts split senses that earlier ones lump. | meanings-per-entry (sense splitter) vs publication year, on shared lemmas | researchers, makers | needs sense parsing |
| **H2** | **Citation density predicts a sense's survival** into later dictionaries. | for shared senses, correlate ancestor `<ls>` count with presence in descendants | researchers | needs sense parsing + lineage (have L0) |
| **H3** | **Polysemy drift** — derivative dicts *add* net senses rather than faithfully copying. | net sense delta along known inheritance edges (PWG→MW72→MW, AP90→AP) | researchers, historians | needs sense parsing |
| **H4** | **Each dict has a measurable semantic-field bias** (ritual / grammar / flora / law / medicine). | map dictionary headword coverage onto **Amarakosa-native topical fields** → per-dict field distribution | researchers, students | M8 data package and chart built |
| **H5** | **"Ghost entries"** — shared OCR/typo anomalies — are both a lineage fingerprint **and** an editor QA flag. | rarity-weighted shared-anomaly detection (extends L3 forensic) | makers, historians | proposed |
| **H6** | **Structural register (citation × grammar-marking) predicts tradition family.** | cluster the macro profile (§1.2); compare to the genealogy tree | researchers | **prototype supports it** |
| **H7** | **First-N sampling materially biases structure metrics** (early-alphabet entries are shorter/sparser). | compare first-N vs random vs stratified samples on the same dicts | methodology | **✅ A7 resolved 2026-05-31** — full corpus chosen (bias moot for production); the §1.2 prototype already confirmed the first-N skew empirically |

---

## 3. New visualizations (micro + macro)

Beyond the existing 50-viz catalog. **[P]** = prototyped this round; **[ ]** = proposed.

**Micro (entry level)**
- **[P]** Feature matrix — one lemma × dicts × microstructure features (§1.1).
- **[ ]** Sense-alignment view — senses of one lemma *aligned* across dicts (like a sequence alignment), not just side-by-side; highlights where dicts agree/diverge/add senses.
- **[ ]** Sense-provenance timeline — each sense's earliest attesting dict + its citation era.
- **[ ]** Entry-anatomy radar — the 24-dim profile of one entry, overlaid across dicts.

**Macro (corpus level)**
- **[P]** Structural-profile heatmap — dicts × structural metrics (§1.2).
- **[x]** Citation-register scatter — 2-axis (citation density × grammar-marking) positioning of all dicts, generated by `npm run build-structural-register`; directly visualizes H6.
- **[ ]** Sense-divergence map — lemmas ranked by cross-dict disagreement → **an editor worklist**.
- **[x]** Semantic-field coverage matrix — AMAR vargas mapped to dictionary headword coverage (H4/M8).
- **[x]** Semantic-field chart — H4 coverage by dictionary family with caveats, generated by `npm run build-semantic-fields`.
- **[ ]** Coverage ribbon — when each lemma entered the lexicographic record (by dict/year).

---

## 4. Practitioner tools (the new layer)

### 4.1 For students of Sanskrit
Productize the micro prototype into a web **entry-explorer**: search any
headword → cross-dict senses aligned, `<ls>` citations + abbreviations decoded
to full source names, and etymology surfaced. Corpus frequency and difficulty
signals may be linked from VisualDCS later, but they are not generated inside
`csl-atlas`.

### 4.2 For dictionary makers
A **QA worklist** that turns analysis into action: the sense-divergence map + anomaly flags (encoding — now guarded by `csl-orig/scripts/check_encoding.py`; missing senses vs sibling dicts; suspect citations; the `gam`-stub class) surfaced as a per-dictionary review queue, with "what to correct/digitize next" prioritization.

### 4.3 For researchers / DH
The macro profile and hypotheses feed the existing **Papers L / M / H** directly — H6 is a ready figure; H1–H3 become the empirical core of a sense-evolution study once sense parsing lands.

---

## 5. Phasing (each ships a dashboard page + paper material)

| Phase | Deliverable | Depends on | Unlocks |
|---|---|---|---|
| **R0** (done) | Two prototypes + this roadmap | — | proof of concept |
| **R1** | Productize the micro explorer (any lemma, web) | parse + index headwords (have `sanhw1`) | students |
| **R2** | **Sense splitter** per dict format → sense-level corpus — *first slice shipped 2026-05-31* ([R2_FINDINGS.md](R2_FINDINGS.md)) | dict format study (have micro typology) | H1–H3, sense-alignment, divergence map |
| **R3** | Semantic-field coverage and chart (Amarakosa-native) | Amarakosa topical hierarchy (`AMAR`) + dictionary headword sets | H4, semantic chart |
| **R4** | Maker QA worklist | R2 + encoding guard + anomaly detectors | dictionary makers |
| **R5** | Student learning paths + external corpus-frequency handoff | R1 + VisualDCS output contract | students |

The **sense splitter (R2)** is the critical dependency — it gates H1–H3, the sense-alignment/divergence views, and the maker worklist. Recommended first real build after R0.

### 5.1 R2 — decided design (2026-05-31)

Decisions (M.G.): a **heuristic per-dict** splitter (deterministic, **no LLM**), run on the **full corpus**, with cross-language sense comparison **anchored on Sanskrit** rather than gloss translation. Anchor/test lemmas: **`gam`, `dharma` (Darma), `rāma`, `iti`, `bodhisattva` (BHS)** — chosen to exercise polysemy, proper-noun/homonym handling, the indigenous citation-boundary parser, and the Buddhist register respectively.

**Sense-marker grammars by structural cluster.** The §1.2 structural clusters double as parser families; each dict's exact markers are now documented in its repo `DATA_DICTIONARY.md` and the **M3 `CLAUDE.md` data-format example** (one real annotated first-entry per dict — produced 2026-05-31), which is the per-dict format study R2 depends on.

| Cluster | Dicts | Sense-boundary signal | Sanskrit anchor |
|---|---|---|---|
| **Western-tagged** | PWG, PW, PWK, SCH, BEN, CAE, CCS, MW, MW72, AP, AP90, BOP, MD, BHS, STC, KRM, BUR, WIL | Numbered sense markers (`.²N`, bold numerals), `<lex>` category shifts, `;`-delimited sub-glosses | cited SLP1 forms + cognates in the gloss |
| **Indigenous-quotation** | VCP, SKD | Sanskrit-synonym glosses + `iti`-closed authority quotations; senses run together — synonym blocks are the units (hardest cluster) | the synonym glosses are *already* Sanskrit |
| **Reverse-direction (EN→SA)** | ApteES/AE (+ future MWE 1851, BOR 1877) | Circled `Ⓐ Ⓑ …` markers + numbered `{@N@}` sub-senses | the `<s>…</s>` Sanskrit equivalents |
| **Index / catalogue** | ACC, VEI, MCI, INM, SNP, IEG | Not word-senses — entries are references/cross-refs → **out of scope** for sense-splitting (handle as reference-instances) | n/a |

**Sanskrit-anchored alignment (A6).** Each split sense gets a **Sanskrit fingerprint** — the set of SLP1 tokens it carries (synonyms, cited forms, cognates, the headword). Cross-dict sense alignment is the overlap (Jaccard) of these fingerprints — **language-agnostic and deterministic**, with no German/French/English translation step. This works because every tradition exposes Sanskrit material to anchor on: indigenous dicts gloss directly in Sanskrit, reverse-direction dicts give Sanskrit equivalents, and Western dicts cite Sanskrit forms and cognates.

**Build order:** Western-tagged first (most dicts, cleanest markers, covers the known inheritance edges PWG→MW72→MW and AP90→AP that H1–H3 need) → reverse-direction (small, clean) → indigenous-quotation (hardest) → indexes excluded. **Output:** a sense-level corpus `data/lexico/senses_<dict>.jsonl` (one record per sense: dict, lemma, sense-index, gloss-span, Sanskrit-fingerprint), feeding the sense-alignment view and the divergence map (the maker worklist).

**✅ First slice shipped 2026-05-31** — `scripts/lexico/sense_split.py` on the 5 anchor lemmas × 8 Western-tagged dicts ([R2_FINDINGS.md](R2_FINDINGS.md)). Proven: (1) **Sanskrit-anchored alignment works across the language barrier** — PWG's German *dharma* sense aligned to Apte's English sense with **no translation**, via shared SLP1 + `<ls>` citations; (2) sense granularity is a **lexicographic-family trait** (Apte enumerates ~22 senses, the MW/Petersburg family lumps into one run-on gloss) — a refinement H1 must control for. Next: homonym-block aggregation (MW), verb-marker grammar, then the indigenous + reverse clusters.

---

## 6. Caveats & method notes

- **Heuristic detectors (and a fixed bug).** Citation detection now counts **both** the Western `<ls>` tag **and** the indigenous quotation style (`“…”` + `…0` authority abbreviations + `iti`) — an earlier `<ls>`-only version wrongly reported the citation-dense indigenous dicts (SKD, VCP) as 0% cited. Residual under-counting remains for Western dicts that cite via inline/bracketed forms or `.E.` Nirukta (MW72, BOP, WIL); a per-dict citation-format normaliser (ties into L6) would close it.
- **Sampling (fixed).** The macro prototype now samples **stratified across the whole alphabet** (every k-th entry), not the first N — first-N skewed to short early-alphabet entries and missed big mid-alphabet entries like `dharma` (`Darma`). The micro prototype also resolves Patel headword-convention variants (doubled-`r` → `Darmma`, inflected visarga → `DarmmaH`) and concatenates homonyms, so the same word is found whatever a dict does.
- **Sense parsing is hard.** H1–H3 and the alignment/divergence views all need a robust per-dict sense splitter (R2) — the main investment.

---

## 7. Decisions And Boundary Notes

- **✅ A6 resolved 2026-05-31** — cross-language alignment **anchors on Sanskrit** (SLP1 fingerprints), no gloss translation (§5.1).
- **✅ A7 resolved 2026-05-31** — **full-corpus** measurement; anchor lemmas `gam`/`dharma`/`rāma`/`iti`/`bodhisattva` (§5.1).
- **✅ R2 method resolved 2026-05-31** — **heuristic per-dict** splitter, deterministic, no LLM (§5.1).

**Round 2 — resolved 2026-05-31:**
- **Frequency/difficulty corpus** → external **DCS/VisualDCS** work, joined on
  SLP1 headword through a future compact output contract. The atlas may consume
  a stable dictionary-facing summary later, but it must not own DCS ingestion,
  passage dashboards, or corpus chronology.
- **Practitioner-layer hosting** → a **page in the main Observable dashboard** (client-side interactive; the ~10 MB `sanhw1` index loads in-browser). No new infra — leverages the existing static-site stack. (Cologne integration deferred to DNS item C3.)
- **First hypothesis after R2** → **H1 (sense inflation over editorial time)** — the lead figure / core of Paper L's sense-evolution section.
- **Semantic-field scheme (H4 / R3)** → **Amarakosa-native**: use the Amarakosa's own topical hierarchy (from the `AMAR` repo) as the field taxonomy — indigenous, culturally grounded, and self-validating against a classical Sanskrit thesaurus. Data package and chart built 2026-06-05 as M8 headword-field coverage plus `/tools/semantic-fields`.

**Still open:** anomaly/ghost-entry detector scope (H5); whether the H1 study is its own short paper or a Paper-L section; co-author assignment for the sense-evolution work.

---
*Prototypes: `scripts/lexico/micro_entry.py`, `scripts/lexico/macro_profile.py`.
Data: `data/lexico/`. Round-2 decisions recorded 2026-05-31; boundary update
for DCS/VisualDCS recorded 2026-06-04.*
