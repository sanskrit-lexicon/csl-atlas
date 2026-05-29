# Sanskrit Evidence Atlas Architecture

Date: 2026-05-29

Status: documentation-first architecture. This file defines the long-term direction before implementation slices are started.

## Mission

Build an interactive research atlas for Sanskrit that connects three evidence domains that are usually kept separate:

- corpus evidence;
- grammatical analysis;
- lexicographic evidence.

The atlas is not just a dictionary dashboard and not just a corpus search interface. Its central object is a traceable scholarly claim:

```text
Claim -> Evidence -> Source
```

Every quantitative statement, grammar pattern, lexical family, dictionary comparison, and diachronic profile should be traceable back to corpus passages, dictionary records, source citations, review notes, or explicitly documented heuristics.

## Audience And Languages

Primary audience:

- international Sanskritists;
- corpus linguists;
- digital humanities researchers;
- Sanskrit lexicographers;
- advanced students.

Interface language policy:

- public UI remains bilingual in English and Russian, following the current atlas pattern;
- German is a first-class scholarly content language because PWG, PWK, and other lexicographic sources contain German descriptions and bibliographic traditions;
- a future German UI locale is possible, but not required for the first implementation phases.

## Product Shape

The target shape is an interactive research atlas, not a linear academic grammar.

The atlas should expose:

- narrative research pages;
- Observable dashboards;
- linked evidence dossiers;
- dictionary comparison tools;
- corpus grammar explorers;
- review queues for uncertain or conflicting evidence.

The site should stay static-first and Observable Framework-based unless there is a later explicit architecture decision to add a backend.

The atlas must serve two entry modes:

- reader mode: looking up a Sanskrit word and understanding dictionary evidence;
- research/developer mode: inspecting, comparing, validating, and improving dictionary and corpus data.

See `docs/READER_DEVELOPER_CRITIQUE.md` for the current critique of the architecture from both viewpoints.

See `docs/USE_CASES.md` for the full use-case inventory that should guide product scope, implementation phases, review queues, and reader-facing documentation.

Reader-facing entry documentation:

- `docs/DICTIONARY_USER_GUIDE.md` — which dictionary to use and how to read an entry;
- `docs/EVIDENCE_LABELS.md` — what the certainty labels mean in plain language.

## Core Principle

Separate the following levels of certainty in all data outputs:

| Level | Meaning | Example |
|---|---|---|
| `observed` | Directly present in a source file | MW record contains `<lex>m.</lex>` |
| `derived` | Computed by a deterministic rule | record classified as `noun-m` |
| `inferred` | Heuristic, useful but uncertain | lexical family inferred from prefix/base pattern |
| `reviewed` | Human-reviewed and accepted or corrected | reviewer confirms a dictionary alignment |

No visualization should hide whether a result is observed, derived, inferred, or reviewed.

## Source Domains

### Dictionaries

Initial dictionary layer:

- MW;
- AP;
- PWG;
- PWK;
- WIL;
- VCP;
- SKD.

Additional CDSL dictionaries can be added after the first comparison model is stable.

Dictionary data stays outside the repository when it is large:

```text
../csl-orig/v02/<dict>/<dict>.txt
```

Generated summaries and small review reports may be committed under `src/data/` or `data/`.

### Corpora

Planned corpus order:

1. DCS exports, because they provide lemmatized corpus evidence.
2. GRETIL dump, because it provides broad text coverage.
3. Ambuda data, when local access and licensing are clear.
4. Sanskrit Library data, when local access and licensing are clear.

Corpus ingestion must preserve text metadata:

- text id;
- title;
- author if known;
- genre;
- period layer;
- source collection;
- license or access note;
- tokenization and lemmatization status;
- line, verse, passage, or chapter reference.

## Common Data Model

The central integration object is `LexemeHub`.

```text
LexemeHub
  canonicalLemma
  normalizedLemma
  homonymId
  pos
  rootCandidate
  grammarFeatures
  dictionaryEntries[]
  corpusOccurrences[]
  senses[]
  sourceCitations[]
  constructions[]
  derivationalRelations[]
  compoundRelations[]
  reviewStatus
```

`LexemeHub` is not a replacement for source records. It is an alignment layer that connects evidence across dictionaries, corpora, and grammar modules.

### DictionaryEntry

```text
DictionaryEntry
  dictionaryId
  recordId
  L
  pc
  k1
  k2
  ecode
  pos
  gender
  senses[]
  citations[]
  domains[]
  rawSnippet
  sourceLineHref
  confidence
```

### CorpusOccurrence

```text
CorpusOccurrence
  corpusId
  textId
  passageId
  token
  lemma
  normalizedLemma
  morphology
  constructionTags[]
  genre
  periodLayer
  sourceHref
  confidence
```

### Construction

```text
Construction
  constructionId
  name
  internationalTerm
  traditionalTerm
  grammarDomain
  diagnostics[]
  examples[]
  frequencyByGenre
  frequencyByPeriod
  evidenceStatus
```

## Grammar Terminology

Use international linguistic terminology and place the traditional Indian framework next to it.

Examples:

| International term | Traditional term | Notes |
|---|---|---|
| root | dhatu | verbal root or lexical root node |
| suffix | pratyaya | must distinguish derivational and inflectional use |
| compound | samasa | later classify samasa subtypes where evidence allows |
| semantic/syntactic role | karaka | keep as parallel analytical layer |
| finite verbal ending | tin | relevant for verb morphology |
| nominal ending | sup | relevant for nominal inflection |
| participial derivative | krdanta | important for corpus grammar |
| secondary derivative | taddhita | important for lexical family depth |
| compound member | samasa component | useful for graph visualization |

The first phases may store these as labels and tags. Full Paninian rule modeling is out of scope until the evidence model is stable.

## Diachronic Scale

Use a more detailed but conservative source-layer scale.

Suggested period order:

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

Every period assignment must include:

- source abbreviation or corpus metadata used;
- confidence;
- whether the layer is directly observed or derived;
- warning if the date is only a rough tradition-based bucket.

Do not present this as exact dating. It is a controlled diachronic index for comparison.

## Analytical Tracks

### Track 1: MW Quantitative Depth

First implementation direction.

Purpose:

- measure MW anatomy;
- compute article type overlaps;
- compute lexical family depth;
- compute source/citation density;
- create a controlled diachronic profile for MW;
- produce source-linked examples and review reports.

Detailed handoff:

```text
docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md
```

### Track 2: Comparative Dictionary Lab

Second implementation direction.

Purpose:

- compare MW, AP, PWG, PWK, WIL, VCP, and SKD;
- build dictionary coverage matrices;
- detect POS/gender disagreements;
- compare sense depth and citation depth;
- identify dictionary-unique vocabulary;
- expose alignment confidence and manual review queues.

Detailed plan:

```text
docs/DICTIONARY_COMPARISON_PLAN.md
```

Core comparison levels:

| Level | Question |
|---|---|
| lemma coverage | Which dictionaries contain this lemma? |
| homonym split | Does one dictionary split what another merges? |
| grammar profile | Do POS, gender, or root status disagree? |
| sense inventory | Which dictionary is deeper or broader? |
| citation apparatus | Which sources are cited and where? |
| domain tagging | Which technical domains are recognized? |
| lexical family | Which derivatives and compounds are covered? |

### Track 3: Corpus Grammar Of Usage

Third implementation direction.

Purpose:

- connect lexical entries to corpus occurrences;
- build genre- and period-sensitive grammar dashboards;
- create construction profiles;
- compare dictionary claims with actual corpus attestations.

Initial corpus should be DCS exports. GRETIL follows after a stable metadata and tokenization strategy exists.

Detailed plan:

```text
docs/DCS_CORPUS_INGESTION_PLAN.md
```

Key grammar areas:

- nominal inflection;
- case functions;
- finite verb morphology;
- participles and krdanta forms;
- absolutives;
- infinitives;
- passive and causative patterns;
- compound density;
- indeclinables;
- karaka-linked argument patterns;
- Vedic vs Classical grammatical shifts.

## Visualization Series

### Corpus Grammar Series

- period and genre coverage dashboard;
- POS heatmap by genre and period;
- case profile explorer;
- finite verb morphology explorer;
- participle and krdanta dashboard;
- absolutive chain explorer;
- compound density by genre;
- Vedic vs Classical shift dashboards;
- sandhi and segmentation ambiguity dashboard.

### Lexical Atlas Series

- article type treemap;
- root family depth graph;
- derivative and compound network;
- compound productivity leaderboard;
- source citation density map;
- lexicographer-only vocabulary atlas;
- botanical, ritual, grammar, medicine, astronomy, and poetics vocabulary maps;
- Vedic-accented layer explorer.

### Comparative Dictionary Series

- dictionary coverage matrix;
- UpSet-style overlap chart;
- POS/gender disagreement table;
- sense-depth comparison;
- citation overlap graph;
- dictionary-unique vocabulary list;
- per-lemma dictionary dossier;
- low-confidence alignment review queue.

### Diachronic Series

- earliest source layer heatmap;
- lexical growth by period layer;
- domain emergence timeline;
- Vedic retention and loss;
- source-layer Sankey diagrams;
- dictionary vs corpus attestation gaps.

## Review Architecture

Manual review is part of the design, not an afterthought.

Review reports should be JSON-first and reproducible, following the pattern already used for TEI and OntoLex review reports.

The shared review-report shape and status vocabulary are defined in `docs/REVIEW_REPORTS.md`.

Suggested review statuses:

```text
machine
needs-review
reviewed-ok
reviewed-corrected
blocked
deferred
```

Review interfaces should support:

- low-confidence dictionary alignments;
- conflicting POS or gender;
- uncertain source period mapping;
- corpus lemma mismatches;
- suspected OCR or encoding problems;
- over-broad lexical family heuristics.

## Directory Strategy

Use small, documented JSON outputs for Observable pages.

Suggested future layout:

```text
src/data/mw/
src/data/dicts/
src/data/corpus/
src/data/grammar/
src/data/review/
docs/
scripts/lib/
```

Large raw corpora and dictionaries should not be committed.

## Phase Order

Documentation always comes before implementation.

Phase 0:

- architecture;
- handoffs;
- terminology policy;
- source and period-layer policy.

Phase 1:

- MW Quantitative Depth.

Phase 2:

- Comparative Dictionary Lab for MW, AP, PWG, PWK, WIL, VCP, SKD.

Phase 3:

- DCS-based corpus grammar of usage.

Phase 4:

- GRETIL ingestion and corpus metadata expansion.

Phase 5:

- Ambuda and Sanskrit Library integration, if access and licensing allow.

## Non-Goals For Early Phases

- no database requirement;
- no full RDF endpoint;
- no replacement of Observable Framework;
- no full Paninian derivation engine;
- no claim of exact dating;
- no LLM-based runtime classification;
- no automatic publication of unreviewed uncertain claims without confidence labels.

## Success Definition

The atlas succeeds when a user can move from a high-level quantitative pattern to source-level evidence:

```text
visualization -> lemma/family/construction -> dictionary record -> corpus passage -> review status
```

The strongest contribution is the integration of corpus grammar, Sanskrit lexicography, and diachronic evidence in one traceable research environment.
