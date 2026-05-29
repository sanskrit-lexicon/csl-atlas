# Gemini Handoff: Sanskrit Evidence Atlas

Date: 2026-05-29

This handoff is for Gemini Flash 3.5 or another implementation assistant working in `csl-atlas`.

It is intentionally detailed. Treat it as the operational implementation plan for the next several slices of the Sanskrit Evidence Atlas.

## Repository

```text
C:\Users\user\Documents\GitHub\csl-atlas
```

## Read First

Read these files in order before making any changes:

1. `ARCHITECTURE.md`
2. `docs/GEMINI_EVIDENCE_ATLAS_HANDOFF.md`
3. `docs/READER_DEVELOPER_CRITIQUE.md`
4. `docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md`
5. `docs/PROJECT_SPEC.md`
6. `HANDOFF.md`
7. `README.md`
8. `package.json`

Then inspect these implementation examples:

1. `src/tools/typology-treemap.md`
2. `src/tools/interoperability-hard-cases.md`
3. `src/data/article-type-counts.json`
4. `src/data/article-type-examples.json`
5. `scripts/sample-hard-cases.mjs`
6. `scripts/build-dictionary-coverage.mjs`

The project is an Observable Framework atlas. Do not replace it with another framework.

Keep the reader/developer split in mind:

- reader-facing pages should help someone use the dictionaries without learning the internal pipeline first;
- developer-facing pages and reports should explain where to improve parsers, evidence mappings, review queues, and generated data.

## Strategic Direction

The long-term goal is the Sanskrit Evidence Atlas:

```text
corpus evidence + grammar + lexicography
```

The atlas should connect:

- dictionary records;
- corpus attestations;
- grammatical constructions;
- traditional Indian grammatical categories;
- diachronic source layers;
- review status;
- source-level links.

The key research model is:

```text
Claim -> Evidence -> Source
```

Every chart, table, ranking, and grammar statement should eventually be traceable to concrete records or passages.

## Fixed User Decisions

- Main audience: international Sanskritists, especially English- and German-reading researchers.
- Secondary audience: a smaller Russian-reading student audience.
- Public UI remains bilingual in English and Russian.
- German is important as scholarly content, especially for PWG, PWK, and bibliographic traditions.
- The product shape is an interactive research atlas, not a linear academic grammar.
- Documentation always comes before implementation.
- Work proceeds one direction at a time.
- First implementation direction: MW Quantitative Depth.
- Second implementation direction: Comparative Dictionary Lab across MW, AP, PWG, PWK, WIL, VCP, and SKD.
- Third implementation direction: corpus grammar of usage, starting with DCS exports.
- GRETIL is added after DCS.
- Ambuda and Sanskrit Library data are added later only when local access and licensing are clear.
- Use international linguistic terminology and traditional Indian terminology side by side.
- Diachrony should use a detailed period-layer scale, not only broad buckets.
- Manual review should use JSON reports and review interfaces, following the existing TEI/OntoLex review-report pattern.

## Operating Rule

Do not start implementation unless the user explicitly says to implement.

If the user asks for:

- planning;
- architecture;
- handoff;
- roadmap;
- scope;
- questions;
- next-step design;

then update documentation only.

If the user says:

- `go`;
- `implement`;
- `build this module`;
- `add the scripts`;
- or names a concrete implementation slice;

then implement only that approved slice.

## Current Approved Slice

Current approved slice:

```text
Documentation-first architecture and handoff.
```

Next implementation slice, when explicitly approved:

```text
MW Quantitative Depth
```

Main handoff for that slice:

```text
docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md
```

Alignment document:

```text
ARCHITECTURE.md
```

## Non-Negotiable Implementation Constraints

- Keep Observable Framework.
- Do not introduce React, Vue, Next, Vite, a database, or a backend.
- Use deterministic Node.js scripts for generation.
- Do not use Gemini, OpenAI, or any LLM at runtime.
- Do not commit full source dictionaries.
- Do not commit full raw corpora.
- Keep Observable-facing JSON compact.
- Preserve source line links where possible.
- Preserve uncertainty, confidence, and review status in outputs.
- Do not remove unrelated existing changes.
- Do not silently collapse German dictionary evidence into English-only labels.
- Do not present inferred heuristics as observed facts.
- Do not claim exact chronology where only a period bucket is justified.

## Evidence Labels

All analytical outputs should distinguish these evidence levels:

| Label | Meaning | Example |
|---|---|---|
| `observed` | Directly present in a source file | MW record contains `<lex>m.</lex>` |
| `derived` | Computed by deterministic rule | entry classified as `noun-m` |
| `inferred` | Heuristic, useful but uncertain | family inferred from headword prefix |
| `reviewed` | Human-reviewed and accepted or corrected | alignment confirmed by reviewer |

Every generated JSON file should expose enough metadata for users to see which level applies.

## Review Statuses

Use JSON-first review reports.

Allowed statuses:

```text
machine
needs-review
reviewed-ok
reviewed-corrected
blocked
deferred
```

Review reports should identify:

- what was checked;
- which source records or corpus passages were used;
- which rule or heuristic was used;
- confidence;
- warnings;
- recommended human action;
- links to source lines where possible.

## Source Layout

Dictionary source layout:

```text
../csl-orig/v02/<dict>/<dict>.txt
```

Initial dictionary comparison set:

```text
MW, AP, PWG, PWK, WIL, VCP, SKD
```

Known MW source path:

```text
../csl-orig/v02/mw/mw.txt
```

Corpus order:

```text
DCS exports -> GRETIL dump -> Ambuda -> Sanskrit Library
```

DCS local path is not yet fixed in this handoff. Before implementing the DCS corpus grammar slice, inspect the workspace or ask the user for the exact DCS export directory.

## Period-Layer Policy

Use the detailed period-layer scale from `ARCHITECTURE.md`.

Suggested order:

```js
[
  "early-vedic",
  "late-vedic",
  "brahmana",
  "aranyaka-upanishadic",
  "sutra",
  "epic",
  "early-classical",
  "classical-kavya",
  "classical-sastra",
  "puranic",
  "tantric-agamic",
  "medieval-scholastic",
  "lexicographic",
  "modern-editorial",
  "unknown"
]
```

Every period assignment should include:

- source abbreviation or corpus metadata;
- confidence;
- evidence level;
- warning if uncertain.

`unknown` should not expand chronological span unless it is the only available layer.

## Terminology Policy

Use international linguistic terminology and traditional Indian terminology side by side.

Initial bilingual grammar terminology table:

| International term | Traditional term | Implementation note |
|---|---|---|
| root | dhatu | root or root-like lexical node |
| suffix | pratyaya | distinguish derivational and inflectional suffixes when possible |
| compound | samasa | classify subtypes later; first store generic compound evidence |
| semantic/syntactic role | karaka | useful for corpus grammar, not for early MW-only work |
| finite verbal ending | tin | relevant in corpus grammar phase |
| nominal ending | sup | relevant in corpus grammar phase |
| participial derivative | krdanta | key category for corpus grammar and lexicon |
| secondary derivative | taddhita | important for lexical family depth |
| compound member | samasa component | useful in family and graph views |

Do not build a full Paninian derivation engine in the early phases.

## Global Output Metadata Contract

Every generated JSON output should include:

```json
{
  "schemaVersion": "0.1.0",
  "generatedAt": "ISO-8601 timestamp",
  "generator": "script path",
  "sourcePaths": [],
  "recordCount": 0,
  "assumptions": [],
  "warnings": [],
  "evidenceLevels": ["observed", "derived", "inferred"]
}
```

Where the output is a review report, also include:

```json
{
  "reviewStatus": "machine",
  "checks": [],
  "failures": [],
  "needsReview": []
}
```

## Target Directory Layout

Use this direction for new work:

```text
scripts/lib/
scripts/build-*.mjs
scripts/validate-*.mjs
src/data/mw/
src/data/dicts/
src/data/corpus/
src/data/grammar/
src/data/review/
src/tools/
docs/
```

Large raw data stays outside the repo.

## Phase 0: Documentation Alignment

Status: current active phase.

Purpose:

- define architecture;
- define implementation phases;
- define evidence policy;
- define period-layer policy;
- define terminology policy;
- prepare implementation handoffs.

Files already present or expected:

- `ARCHITECTURE.md`
- `docs/GEMINI_EVIDENCE_ATLAS_HANDOFF.md`
- `docs/READER_DEVELOPER_CRITIQUE.md`
- `docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md`
- `docs/PROJECT_SPEC.md`
- `HANDOFF.md`

Documentation tasks before implementation:

1. Check whether `ARCHITECTURE.md` and `docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md` contradict each other.
2. If they contradict, update the narrower handoff to match `ARCHITECTURE.md`.
3. Confirm that MW Quantitative Depth is the first implementation slice.
4. Confirm that corpus work waits until DCS paths are known.
5. Confirm that comparative dictionary work waits until MW depth outputs exist.

No build is required for documentation-only edits unless a markdown or site link changes in a way that needs verification.

## Phase 1: MW Quantitative Depth

Phase 1 is the first implementation slice after explicit approval.

Primary handoff:

```text
docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md
```

### Phase 1 Goal

Build a deterministic MW-only quantitative layer that computes:

- article type counts and overlaps;
- entry-level features;
- source citation density;
- conservative diachronic source layers;
- compound depth;
- derivational and family depth;
- deepest lexical families;
- machine validation and review outputs;
- Observable dashboards with source links.

### Phase 1 Inputs

Required:

```text
../csl-orig/v02/mw/mw.txt
src/data/article-type-counts.json
src/data/article-type-examples.json
```

Optional reference files:

```text
src/tools/typology-treemap.md
docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md
```

### Phase 1 Files To Add

Scripts:

```text
scripts/lib/mw-parser.mjs
scripts/lib/mw-classifiers.mjs
scripts/lib/mw-source-layers.mjs
scripts/lib/mw-depth-graph.mjs
scripts/build-mw-quantitative-depth.mjs
scripts/validate-mw-depth.mjs
```

Data:

```text
src/data/mw/mw-source-layers.json
src/data/mw/mw-quantitative-summary.json
src/data/mw/mw-type-overlaps.json
src/data/mw/mw-depth-distribution.json
src/data/mw/mw-deepest-families.json
src/data/mw/mw-source-layer-summary.json
src/data/mw/mw-diachronic-profile.json
src/data/mw/mw-validation-report.json
```

Observable pages:

```text
src/tools/mw-depth-dashboard.md
src/tools/mw-diachronic-layers.md
src/tools/mw-family-depth.md
```

Documentation updates:

```text
README.md
docs/PROJECT_SPEC.md
HANDOFF.md
```

Package scripts:

```json
{
  "build-mw-depth": "node scripts/build-mw-quantitative-depth.mjs",
  "validate-mw-depth": "node scripts/validate-mw-depth.mjs"
}
```

### Phase 1 Parser Contract

`scripts/lib/mw-parser.mjs` should export:

```js
export function parseMwRecords(text, options = {}) {}
export function parseMwHeader(line) {}
export function makeMwHref(startLine) {}
```

Each parsed record should include:

```json
{
  "dictionaryId": "mw",
  "L": "10",
  "pc": "1,1",
  "k1": "aMSa",
  "k2": "a/MSa",
  "ecode": "1",
  "body": "...",
  "raw": "...",
  "startLine": 55,
  "endLine": 57,
  "href": "https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt#L55"
}
```

Parser requirements:

- parse `<L>` to `<LEND>`;
- preserve line numbers;
- keep raw record text available inside scripts;
- do not write huge raw-body JSON to Observable-facing outputs unless needed;
- handle duplicate `k1`;
- handle decimal `L` values such as `27.1`;
- keep mojibake-like source artifacts unchanged unless source data is actually corrected elsewhere.

### Phase 1 Classifier Contract

`scripts/lib/mw-classifiers.mjs` should export:

```js
export function classifyMwArticleTypes(record) {}
export function extractMwCitations(record) {}
export function extractDomainFlags(record) {}
export function normalizeLsValue(value) {}
```

Article type rules:

- `root`: body contains `genuineroot`
- `compound`: `ecode` starts with `3` and `k2` has a compound marker
- `continuation`: `ecode` starts with `1A`
- `derived`: `ecode` starts with `2`
- `noun-m`: body contains `<lex>m.</lex>`
- `noun-f`: body contains `<lex>f.</lex>`
- `noun-n`: body contains `<lex>n.</lex>`
- `adjective-mfn`: body contains `<lex>mfn.</lex>`
- `indeclinable`: body contains `<lex>ind.</lex>`
- `botanical`: body contains `<bot>`
- `biographical`: body contains `<bio>`
- `etymological-ie`: body contains `<lang>`
- `vedic-accented`: `k2` contains `/`
- `lexicographer-only`: all `<ls>` values normalize to `L`
- `other`: no matched type

Types overlap. Do not force exclusivity.

The generated type counts should be compared against:

```text
src/data/article-type-counts.json
```

If counts diverge, write explicit warnings into `mw-validation-report.json`.

### Phase 1 Source Layer Contract

`scripts/lib/mw-source-layers.mjs` should export:

```js
export function loadSourceLayerMap(path) {}
export function classifySourceLayers(citations, layerMap) {}
export function computeLayerSpan(layers, periodOrder) {}
```

`src/data/mw/mw-source-layers.json` should contain a conservative source abbreviation map.

Suggested shape:

```json
{
  "schemaVersion": "0.1.0",
  "periodOrder": ["early-vedic", "late-vedic", "epic", "lexicographic", "unknown"],
  "sources": {
    "RV.": {
      "layer": "early-vedic",
      "label": "Rigveda",
      "confidence": "high",
      "evidenceLevel": "derived"
    },
    "MBh.": {
      "layer": "epic",
      "label": "Mahabharata",
      "confidence": "high",
      "evidenceLevel": "derived"
    },
    "L.": {
      "layer": "lexicographic",
      "label": "Lexicographers",
      "confidence": "medium",
      "evidenceLevel": "observed"
    }
  },
  "unknownPolicy": "Unknown sources remain unknown and do not expand chronological span unless they are the only layer."
}
```

Do not attempt exhaustive source mapping in the first pass. Start with common sources and classify the rest as `unknown`.

### Phase 1 Entry Metrics

For each record compute internally:

```json
{
  "k1": "aMSa",
  "L": "10",
  "pc": "1,1",
  "href": "...",
  "types": ["noun-m", "vedic-accented"],
  "typeCount": 2,
  "citationCount": 3,
  "sourceLayers": ["early-vedic", "lexicographic"],
  "sourceLayerCount": 2,
  "earliestLayer": "early-vedic",
  "latestLayer": "lexicographic",
  "sourceLayerSpan": 12,
  "compoundSegmentCount": 1,
  "compoundDepth": 0,
  "continuationFlag": false,
  "derivedFlag": false,
  "rootFlag": false,
  "domainFlags": []
}
```

Do not necessarily publish all entry-level metrics in one huge file. Use them to aggregate compact outputs.

### Phase 1 Family Metrics

`scripts/lib/mw-depth-graph.mjs` should export:

```js
export function buildMwFamilySummaries(records, entryMetrics) {}
export function computeCompoundDepth(record) {}
export function computeDepthScore(family) {}
```

For each family summary produce:

```json
{
  "familyKey": "agni",
  "rootCandidate": "agni",
  "memberCount": 120,
  "descendantCount": 119,
  "maxFamilyDepth": 4,
  "maxCompoundDepth": 3,
  "sourceLayerSpan": 8,
  "earliestLayer": "early-vedic",
  "latestLayer": "classical-sastra",
  "depthScore": 27.4,
  "confidence": "medium",
  "evidenceLevel": "inferred",
  "warnings": [],
  "topExamples": [
    {
      "k1": "agni",
      "L": "123",
      "pc": "5,1",
      "line": 1234,
      "href": "..."
    }
  ]
}
```

Family grouping may be heuristic in Phase 1. Clearly mark it as `inferred` unless a record provides explicit root evidence.

### Phase 1 Output Files

`mw-quantitative-summary.json`:

- total records;
- total type memberships;
- type counts;
- top article types;
- citation stats;
- depth stats;
- warnings.

`mw-type-overlaps.json`:

- pairwise type overlaps;
- top overlap combinations;
- examples with links.

`mw-depth-distribution.json`:

- histogram of compound depth;
- histogram of family depth;
- histogram of citation counts;
- histogram of source layer span.

`mw-deepest-families.json`:

- top 50 or 100 deepest families;
- source links;
- confidence and warnings.

`mw-source-layer-summary.json`:

- counts by source layer;
- unknown source counts;
- top source abbreviations;
- source-layer warning summary.

`mw-diachronic-profile.json`:

- type by period layer;
- domain by period layer;
- Vedic/classical/lexicographic overlaps;
- caveats.

`mw-validation-report.json`:

- parsed record count;
- type-count comparison with `article-type-counts.json`;
- missing output checks;
- link checks;
- warning count;
- validation status.

### Phase 1 Observable Pages

`src/tools/mw-depth-dashboard.md`:

- compact metric blocks;
- article-type summary;
- depth histograms;
- top deepest families;
- links to related pages.

`src/tools/mw-diachronic-layers.md`:

- source-layer summary;
- unknown source warning block;
- type by layer heatmap;
- source abbreviation table;
- caveat text.

`src/tools/mw-family-depth.md`:

- searchable/sortable deepest families table;
- depth component breakdown;
- top examples with links;
- warning/confidence badges.

UI requirements:

- keep page usable at desktop and mobile widths;
- avoid huge body-text dumps;
- use compact tables and charts;
- source links open external GitHub URLs;
- if locale strings are added, update both `src/locales-en.json` and `src/locales-ru.json`.

### Phase 1 Commands

After implementation:

```bash
npm run build-mw-depth
npm run validate-mw-depth
npm run build
```

If a dev server is needed for browser verification:

```bash
npm run dev -- --host 127.0.0.1
```

Then verify:

```text
http://127.0.0.1:3000/tools/mw-depth-dashboard
http://127.0.0.1:3000/tools/mw-diachronic-layers
http://127.0.0.1:3000/tools/mw-family-depth
```

### Phase 1 Acceptance Criteria

- One command regenerates all MW quantitative depth JSON.
- Validation passes or records explicit warnings.
- Observable build passes.
- New pages render.
- Source links are present in top examples.
- Type counts are checked against existing treemap counts.
- Inferred family grouping is labeled as inferred.
- No runtime LLM calls.
- No raw `mw.txt` committed.

## Phase 2: Comparative Dictionary Lab

Start only after Phase 1 has usable MW outputs.

### Phase 2 Goal

Compare MW, AP, PWG, PWK, WIL, VCP, and SKD across:

- coverage;
- headword alignment;
- homonym splitting;
- POS/gender disagreement;
- sense-depth differences;
- citation apparatus differences;
- domain vocabulary;
- compounds and derivatives;
- dictionary-unique vocabulary;
- review queues.

### Phase 2 Inputs

```text
../csl-orig/v02/mw/mw.txt
../csl-orig/v02/ap/ap.txt
../csl-orig/v02/pwg/pwg.txt
../csl-orig/v02/pw/pw.txt
../csl-orig/v02/wil/wil.txt
../csl-orig/v02/vcp/vcp.txt
../csl-orig/v02/skd/skd.txt
```

Note: PWK may use directory/file code `pw`; inspect existing scripts before assuming path names.

### Phase 2 Files To Add

Scripts:

```text
scripts/lib/dict-parser.mjs
scripts/lib/dict-normalize.mjs
scripts/lib/dict-align.mjs
scripts/lib/dict-compare.mjs
scripts/build-comparative-dictionary-lab.mjs
scripts/validate-dictionary-comparison.mjs
```

Data:

```text
src/data/dicts/dictionary-manifest.json
src/data/dicts/lexeme-hub-summary.json
src/data/dicts/dictionary-coverage-matrix.json
src/data/dicts/dictionary-overlaps.json
src/data/dicts/dictionary-disagreements.json
src/data/dicts/dictionary-unique-vocabulary.json
src/data/dicts/dictionary-review-queue.json
src/data/dicts/dictionary-validation-report.json
```

Pages:

```text
src/tools/dictionary-comparison-lab.md
src/tools/dictionary-overlap-explorer.md
src/tools/dictionary-disagreement-review.md
```

### Phase 2 Alignment Confidence

Use confidence levels:

| Confidence | Rule |
|---|---|
| `high` | exact normalized `k1` plus compatible POS/gender |
| `medium` | exact normalized `k1`, but POS/gender missing or different |
| `low` | fuzzy normalized headword or ambiguous homonym |
| `needs-review` | multiple possible alignments or serious conflict |

Do not silently choose one alignment when multiple are plausible.

### Phase 2 LexemeHub Minimal Shape

```json
{
  "lexemeId": "lex:aMSa",
  "canonicalLemma": "aMSa",
  "normalizedLemma": "aMSa",
  "homonymId": null,
  "dictionaryEntries": [
    {
      "dictionaryId": "mw",
      "recordId": "mw:L10",
      "k1": "aMSa",
      "pos": "noun",
      "gender": "m",
      "href": "..."
    }
  ],
  "coverage": {
    "mw": true,
    "ap": false,
    "pwg": true
  },
  "alignmentConfidence": "medium",
  "reviewStatus": "machine",
  "warnings": []
}
```

### Phase 2 Metrics

Compute:

- records per dictionary;
- unique normalized headwords per dictionary;
- overlap by dictionary pair;
- full intersection across all target dictionaries;
- entries unique to one dictionary;
- POS disagreement count;
- gender disagreement count;
- sense-depth approximate comparison;
- citation-density comparison;
- examples for each disagreement class.

### Phase 2 Acceptance Criteria

- All seven target dictionaries are represented in the manifest.
- Coverage matrix builds deterministically.
- Every disagreement row includes source links where possible.
- Low-confidence alignments go to a review queue.
- Observable build passes.
- No full dictionary source files are committed.

## Phase 3: DCS Corpus Grammar Of Usage

Start only after Phase 2 or after explicit user approval to switch tracks.

### Phase 3 Goal

Connect dictionary and grammar claims to corpus usage.

Start with DCS exports because they provide lemmatized evidence.

### Phase 3 Precondition

Find or ask for the local DCS export path.

Do not guess the DCS schema. Inspect files first and document:

- file format;
- encoding;
- text metadata;
- token format;
- lemma format;
- morphology tags;
- source references.

### Phase 3 Files To Add

Scripts:

```text
scripts/lib/dcs-parser.mjs
scripts/lib/corpus-normalize.mjs
scripts/lib/corpus-grammar-metrics.mjs
scripts/build-dcs-corpus-grammar.mjs
scripts/validate-corpus-grammar.mjs
```

Data:

```text
src/data/corpus/corpus-manifest.json
src/data/corpus/dcs-summary.json
src/data/corpus/dcs-lemma-frequency.json
src/data/corpus/dcs-pos-by-genre.json
src/data/corpus/dcs-morphology-profile.json
src/data/corpus/dcs-construction-seeds.json
src/data/corpus/dcs-validation-report.json
```

Pages:

```text
src/tools/corpus-grammar-dashboard.md
src/tools/corpus-lemma-evidence.md
src/tools/corpus-morphology-explorer.md
```

### Phase 3 Initial Grammar Metrics

Compute:

- token count by text;
- lemma count by text;
- POS distribution by genre;
- morphology tag distribution;
- lemma frequency;
- high-frequency indeclinables;
- participle/krdanta candidates;
- finite verb patterns if tags allow;
- compound/token segmentation evidence if tags allow;
- dictionary coverage for high-frequency lemmas.

### Phase 3 CorpusOccurrence Shape

```json
{
  "corpusId": "dcs",
  "textId": "text-id",
  "passageId": "passage-id",
  "token": "agnim",
  "lemma": "agni",
  "normalizedLemma": "agni",
  "morphology": {
    "pos": "noun",
    "case": "accusative",
    "number": "singular",
    "gender": "masculine"
  },
  "genre": "vedic",
  "periodLayer": "early-vedic",
  "sourceHref": null,
  "confidence": "source-provided",
  "evidenceLevel": "observed"
}
```

### Phase 3 Acceptance Criteria

- DCS export schema is documented.
- Corpus manifest exists.
- Summary outputs are compact.
- At least one page links corpus lemmas back to dictionary evidence where possible.
- Unknown metadata is explicit, not hidden.

## Phase 4: GRETIL Expansion

Start after DCS ingestion model is stable.

Goal:

- broaden text coverage;
- add corpus metadata;
- compare lemmatized DCS evidence with less-annotated GRETIL text coverage.

Expected challenge:

- GRETIL may not provide consistent tokenization, lemmatization, or metadata.

First implementation should therefore focus on:

- text inventory;
- metadata normalization;
- raw token counts;
- script/transliteration detection;
- genre/period mapping;
- search index-friendly summaries.

Do not promise DCS-quality grammar analysis for GRETIL unless the data supports it.

## Phase 5: Ambuda And Sanskrit Library Expansion

Start only after access and licensing are clear.

Goals:

- add additional corpus evidence;
- preserve provenance;
- avoid mixing incompatible licenses;
- enrich text and translation links where permitted.

Implementation must include:

- source access note;
- license note;
- whether text can be redistributed;
- whether only derived metrics can be committed.

## Cross-Track Integration

After Phases 1-3, build integrated evidence dossiers.

Possible page:

```text
src/tools/lexeme-evidence-dossier.md
```

For a selected lexeme, show:

- dictionary entries;
- corpus occurrences;
- grammar features;
- source layers;
- family graph summary;
- review status;
- warnings.

Do not build this before MW, dictionary comparison, and corpus outputs exist.

## Localization And UI Policy

Existing atlas uses:

```text
src/locales-en.json
src/locales-ru.json
```

When adding reusable UI labels, update both locale files.

For scholarly terms:

- show English labels in the main interface;
- Russian labels in the Russian locale;
- preserve German source labels where they belong to a dictionary or citation;
- do not translate headwords, source abbreviations, or dictionary sigla.

Suggested UI label pattern:

```text
Root / dhatu
Compound / samasa
Suffix / pratyaya
Role / karaka
```

## Validation Strategy

Every implementation phase should include:

- build script;
- validation script;
- generated validation report;
- Observable build check.

Minimum command pattern:

```bash
npm run build-<slice>
npm run validate-<slice>
npm run build
```

Validation reports should be committed if they summarize generated public data and are compact.

## Browser Verification

After frontend/page changes:

1. Start or reuse the local dev server.
2. Open the relevant page.
3. Check that the page renders.
4. Check the browser console for errors.
5. Verify key counts shown on page match generated JSON.
6. Verify source links exist.

Expected local URL:

```text
http://127.0.0.1:3000
```

## Implementation Style

Good:

- small modules in `scripts/lib`;
- deterministic scripts;
- compact JSON outputs;
- explicit assumptions;
- explicit warnings;
- source links;
- confidence fields;
- review queues;
- reuse existing Observable page patterns.

Avoid:

- broad rewrites;
- new frameworks;
- unreviewed claims without confidence labels;
- huge raw data in `src/data`;
- hidden dictionary/corpus parsing failures;
- exact dating claims;
- LLM-based runtime classification;
- manual-only sample selection as the primary method.

## What To Do If Blocked

If a source path is missing:

1. report the missing path;
2. inspect nearby directories if safe;
3. do not invent data;
4. add a clear warning or ask the user.

If a parser rule is uncertain:

1. implement the conservative version;
2. mark output as `inferred` or `needs-review`;
3. add examples to the validation report.

If a generated file would be huge:

1. aggregate it;
2. keep only top examples;
3. write a warning explaining what was omitted;
4. do not dump full raw records into Observable-facing JSON.

## Detailed Work Order For The Next "go"

When the user approves MW Quantitative Depth, implement in this exact order:

1. Inspect current `package.json`, `src/tools/typology-treemap.md`, and `src/data/article-type-counts.json`.
2. Add `scripts/lib/mw-parser.mjs`.
3. Add a small parser smoke test inside `scripts/validate-mw-depth.mjs` or a temporary validation path.
4. Add `scripts/lib/mw-classifiers.mjs`.
5. Generate type counts and compare with existing counts.
6. Add `src/data/mw/mw-source-layers.json` with conservative mappings.
7. Add `scripts/lib/mw-source-layers.mjs`.
8. Add entry-level metric computation inside `scripts/build-mw-quantitative-depth.mjs`.
9. Add `scripts/lib/mw-depth-graph.mjs`.
10. Generate compact output JSON files under `src/data/mw/`.
11. Add `scripts/validate-mw-depth.mjs`.
12. Add package scripts.
13. Run `npm run build-mw-depth`.
14. Run `npm run validate-mw-depth`.
15. Add Observable pages.
16. Run `npm run build`.
17. Browser-check the new pages.
18. Update docs.
19. Report changed files, generated files, command results, warnings, and next slice.

Do not start Phase 2 in the same pass unless the user explicitly asks.

## Ready Prompt For Documentation Review

Use this when asking Gemini to review the plan without implementing:

```text
You are working in:

C:\Users\user\Documents\GitHub\csl-atlas

Read:

1. ARCHITECTURE.md
2. docs/GEMINI_EVIDENCE_ATLAS_HANDOFF.md
3. docs/READER_DEVELOPER_CRITIQUE.md
4. docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md
5. docs/PROJECT_SPEC.md
6. HANDOFF.md

Follow the documentation-first rule. Do not implement code.

Current long-term goal:
Build the Sanskrit Evidence Atlas: corpus evidence + grammar + lexicography in one traceable interactive research atlas.

For this pass:
1. identify contradictions between these docs;
2. identify missing assumptions for MW Quantitative Depth;
3. propose small documentation edits only;
4. do not change code or generated data.
```

## Ready Prompt For MW Implementation

Use this only after explicitly approving implementation:

```text
You are working in:

C:\Users\user\Documents\GitHub\csl-atlas

Read:

1. ARCHITECTURE.md
2. docs/GEMINI_EVIDENCE_ATLAS_HANDOFF.md
3. docs/READER_DEVELOPER_CRITIQUE.md
4. docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md
5. docs/PROJECT_SPEC.md
6. HANDOFF.md

Implement Phase 1 only: MW Quantitative Depth.

Follow the detailed work order in docs/GEMINI_EVIDENCE_ATLAS_HANDOFF.md.

Constraints:
- Keep Observable Framework.
- Use deterministic Node.js scripts.
- Do not use LLM inference at runtime.
- Do not commit raw mw.txt.
- Keep generated Observable-facing JSON compact.
- Preserve evidence levels, confidence, warnings, and source links.
- Do not start comparative dictionary work or corpus grammar work in this pass.

After implementation, run:

npm run build-mw-depth
npm run validate-mw-depth
npm run build

Then report:
1. files changed;
2. generated outputs;
3. command results;
4. validation warnings;
5. browser verification status if pages were added;
6. next recommended slice.
```

## Expected Gemini Response Format

When reporting back, include:

1. files changed;
2. whether the work was documentation-only or implementation;
3. commands run, if any;
4. validation/build results, if any;
5. generated artifact counts, if any;
6. assumptions;
7. unresolved questions;
8. warnings;
9. recommended next slice.

Keep the report concise, but do not hide warnings.
