# MW Quantitative Depth Handoff

This handoff describes a deterministic implementation plan for adding synchronic and diachronic quantitative metrics for Monier-Williams (`mw.txt`) to `csl-atlas`.

## Repository

- Workspace: `C:\Users\user\Documents\GitHub\csl-atlas`
- Primary source: `..\csl-orig\v02\mw\mw.txt`
- Existing typology page: `src/tools/typology-treemap.md`
- Existing typology counts: `src/data/article-type-counts.json`
- Existing typology examples: `src/data/article-type-examples.json`

Do not use LLM inference at runtime. All classification must be deterministic and reproducible from MW markup, headword fields, e-codes, source tags, and documented heuristics.

## Goal

Build a Node.js pipeline that extracts quantitative MW metrics at maximum useful depth:

- synchronic dictionary anatomy;
- article type overlaps;
- entry, compound, and family depth;
- citation/source density;
- conservative diachronic source-layer profiles;
- top deepest lexical families with source links.

The output should feed Observable pages using `FileAttachment`.

## Add Scripts

Add:

- `scripts/lib/mw-parser.mjs`
- `scripts/lib/mw-classifiers.mjs`
- `scripts/lib/mw-source-layers.mjs`
- `scripts/lib/mw-depth-graph.mjs`
- `scripts/build-mw-quantitative-depth.mjs`
- `scripts/validate-mw-depth.mjs`

Add package scripts:

- `build-mw-depth`
- `validate-mw-depth`

## Parser Requirements

Parse every MW record from `<L>` through `<LEND>`.

For each record extract:

- `L`
- `pc`
- `k1`
- `k2`
- `ecode`
- `body`
- `startLine`
- `href`

Use this link format:

```text
https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt#L{startLine}
```

Preserve line numbers. Avoid generating very large Observable-facing JSON if a smaller summary is enough.

## Article Type Classifier

Reproduce the classifier already used for the treemap counts.

Rules:

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

Validation must compare generated type counts with `src/data/article-type-counts.json` and emit explicit warnings for any divergence.

## Source Layer Classifier

Add:

- `src/data/mw-source-layers.json`

This file should map MW source abbreviations conservatively to source layers.

Initial layers:

- `vedic`
- `epic`
- `classical`
- `puranic`
- `technical`
- `lexicographic`
- `unknown`

Rules:

- Vedic sources map to `vedic`.
- Epics map to `epic`.
- Classical literary sources map to `classical`.
- Puranic sources map to `puranic`.
- Sastra and technical sources map to `technical`.
- `L.` and lexicon-only abbreviations map to `lexicographic`.
- Ambiguous sources remain `unknown`.

Do not overclaim chronology. Include assumptions and uncertainty in outputs.

## Entry Metrics

For each record compute:

- `types`
- `typeCount`
- `citationCount`
- `sourceLayers`
- `sourceLayerCount`
- `earliestLayer`
- `latestLayer`
- `sourceLayerSpan`
- `compoundSegmentCount`
- `compoundDepth`
- `continuationFlag`
- `derivedFlag`
- `rootFlag`
- `domainFlags`

Suggested layer order:

```js
["vedic", "epic", "classical", "puranic", "technical", "lexicographic", "unknown"]
```

Keep `unknown` out of chronological span unless it is the only layer.

## Family Metrics

Build lexical family summaries. The first implementation may use conservative heuristics:

- group root records by `genuineroot` where available;
- group derived and compound members by normalized base/headword prefix when no explicit root link is available;
- keep assumptions in output JSON.

For each family compute:

- `familyKey`
- `rootCandidate`
- `memberCount`
- `descendantCount`
- `maxFamilyDepth`
- `maxCompoundDepth`
- `sourceLayerSpan`
- `earliestLayer`
- `latestLayer`
- `topExamples` with `k1`, `L`, `pc`, `line`, `href`, and metric components

The useful ranking score may be:

```text
depthScore =
  familyDepth * 3
+ compoundDepth * 2
+ sourceLayerSpan * 2
+ log1p(citationCount)
+ log1p(descendantCount)
```

Always store components separately. The score is only for sorting.

## Data Outputs

Generate under:

- `src/data/mw/`

Required files:

- `mw-quantitative-summary.json`
- `mw-type-overlaps.json`
- `mw-depth-distribution.json`
- `mw-deepest-families.json`
- `mw-source-layer-summary.json`
- `mw-diachronic-profile.json`
- `mw-validation-report.json`

Each JSON must include:

- `schemaVersion`
- `generatedAt`
- `sourcePath`
- `sourceDate` if known
- `recordCount`
- `assumptions`
- `warnings`

## Observable Pages

Add:

- `src/tools/mw-depth-dashboard.md`
- `src/tools/mw-diachronic-layers.md`
- `src/tools/mw-family-depth.md`

Pages should include:

- compact metric blocks;
- top deepest families table;
- depth distribution chart;
- source layer chart;
- source entry links.

Keep styling consistent with existing Observable pages. Do not create a landing page.

## Validation

Run:

```bash
npm run build-mw-depth
npm run validate-mw-depth
npm run build
```

Validation should fail if:

- parsed record count is unexpectedly far from `286561`;
- any required output JSON is missing;
- deepest families have no source links;
- type counts diverge from `src/data/article-type-counts.json` without explicit warning;
- Observable build fails.

## Documentation

Update:

- `README.md`
- `docs/PROJECT_SPEC.md`
- `HANDOFF.md`

Document:

- what is counted;
- what is inferred;
- what remains approximate;
- how synchronic and diachronic metrics differ;
- how to regenerate outputs.

## Acceptance Criteria

- One command regenerates all MW quantitative depth JSON.
- Validation passes.
- Observable build passes.
- New pages render without console errors.
- Outputs include examples with links.
- Runtime does not depend on Gemini, OpenAI, or any other LLM.
