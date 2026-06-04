# CSL Atlas Review Release Roadmap

Date: 2026-06-03

Status: active 3-month roadmap for turning the current evidence-atlas build into a stable public release.

## Summary

The next release is a public-atlas release, not a paper-only package and not a backend rewrite. The work keeps the existing Observable Framework architecture, generated JSON pipeline, and review-report overlay model.

North star:

```text
reader question -> dictionary evidence -> source link -> evidence/review status
```

## Phase 0: Stabilize Current WIP

Treat the current dirty tree as valuable work and separate it into release buckets:

| Bucket | Main files | Release action |
|---|---|---|
| Standards split | `csl-standards` | TEI/OntoLex/FrAC/RDF work has moved out of the atlas. Keep only external pointers. |
| PWA / discoverability | `src/manifest.json`, `src/sw.js`, `src/premium.css`, `observablehq.config.js`, `package.json` | Build locally and verify GitHub Pages asset paths. |
| Reader/public UI | tool pages, locale files, landing/sidebar changes | Verify mobile layout, links, and bilingual labels. |
| Release process | PR template, changelog, checklist docs | Keep validation commands and caveats visible. |

Required gates:

```bash
npm test
npm run validate-review-reports
npm run build
```

## Phase 1: Public Atlas Readiness

- Make Reader Mode visible from the sidebar and landing page.
- Keep the dictionary user guide and evidence-label docs linked from the public entry path.
- Keep the external corpus boundary explicit: DCS work belongs in VisualDCS,
  not in this dictionary-atlas release.
- Keep machine/review status visible on dictionary review pages.
- Do not invent Russian scholarly terminology; low-confidence Russian UI terms remain marked for maintainer review.

## Phase 2: Light Review Sprint

Use `docs/LIGHT_REVIEW_SPRINT.md` as the review worklist. The sprint assumes scarce reviewer time and samples high-value cases:

- all 7 low-confidence alignments;
- top 50 unknown MW source-layer sigla by frequency;
- top 50 source-siglum alias candidates by citation count;
- 25 representative gender-conflict cases;
- Standards review belongs in `csl-standards`; it is no longer part of the
  dictionary-atlas review sprint.

Review decisions must be recorded in the existing review files or mapping tables, never by editing generated source data directly.

## Phase 3: Reader Lookup v1

Reader Lookup v1 is implemented as a static Observable page backed by compact generated JSON:

- data output: `src/data/dicts/lemma-lookup.json`;
- page: `src/tools/reader-lookup.md`;
- query normalization: `src/lib/lookup-normalize.js`;
- generator: `npm run build-dict-comparison`.

Scope:

- supports exact and prefix lookup over normalized dictionary headwords;
- indexes lemmas attested in at least 4 of the 7 target dictionaries; lower-coverage lemmas remain a future search-index/backend item;
- supports SLP1 and IAST query normalization;
- shows dictionary coverage, record counts, gender/POS where extracted, and source links;
- does not implement full-text search, corpus lookup, sandhi recovery, Devanagari input, or `LexemeHub`.

## Future Roadmap Items

- Full dictionary search index for raw entry text and low-coverage lemmas.
- Corpus dashboards and dictionary-to-corpus joins belong in VisualDCS or a
  future grammar repo, not in `csl-atlas`.
- `LexemeHub` only if a future cross-repo integration project proves it is
  needed; it is not an atlas roadmap item.
- TEI/OntoLex/FrAC standards work in `csl-standards`, not `csl-atlas`.
