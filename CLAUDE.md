# CLAUDE.md

_Created: 03-07-2026 · Last updated: 16-08-2026_

`csl-atlas` is the public **dictionary-evidence** microsite for the Cologne
Digital Sanskrit Dictionaries — a static Observable Framework site for
reader-facing chapters, cross-dictionary comparisons, genealogy views, and
review queues over nine narrative dictionaries (MW, PWG, PWK, AP, WIL, SKD,
VCP, ARMH, ABCH) plus an all-dictionary coverage layer. No backend, no
database, no runtime LLM, no full-text search engine. Companion to the MW
microanalysis papers in [`sanskrit-lexicon/MWS`](https://github.com/sanskrit-lexicon/MWS).

Org conventions live in [`../CLAUDE.md`](https://github.com/gasyoun/github-spine/blob/main/CLAUDE.md).
Before encodings or corpus data, read the
[Sanskrit context primer](https://github.com/gasyoun/github-spine/blob/main/SANSKRIT_CONTEXT_PRIMER.md).

## How to run

```sh
npm run dev                       # Observable preview (predev runs sync-site-data)
npm run build                     # → dist/ (prebuild syncs data)
npm run deploy                    # Observable deploy (predeploy syncs)
npm test                          # node --test
npm run validate-review-reports   # required before any CI build
```

Data pipelines are one `npm run build-*` script per dataset (~70 in
[`package.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/package.json)),
each backed by `scripts/build-*.mjs` (or `.py`). Grep `package.json` `scripts`
for the name — do not guess. Pair `build-*` with `validate-*` when a validator
exists (`build-mw-depth` / `validate-mw-depth`, `build-dict-comparison` /
`validate-dict-comparison`).

## Key paths

| Path | Purpose |
|---|---|
| [`src/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/src) | Observable pages (`.md`), generated `src/data/*.json`, `src/lib/`, tool pages, dict chapters |
| [`scripts/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/scripts) | Build/import/validate; shared parsers in `scripts/lib/` |
| [`docs/ARCHITECTURE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ARCHITECTURE.md) · [`docs/BOUNDARY_RULES.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BOUNDARY_RULES.md) | Scope — read first |
| [`data/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data) | Raw/intermediate inputs (not the generated `src/data/` copies) |
| `dist/` | Build output — generated, gitignored |

CI: `test.yml` (PR/push `main`) runs `npm ci` → `npm test` →
`validate-review-reports` → `npm run build`. `build-and-deploy.yml` then
publishes `dist/` to GitHub Pages.

## Conventions

- **Display Sanskrit in IAST, never raw SLP1** on any human-facing page. Convert
  with `slp1ToIast` from
  [`src/lib/lookup-normalize.js`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/lookup-normalize.js).
  Keep SLP1 only as a muted secondary / search key.
- **Every table or list gets a CSV download** via
  [`src/lib/csv-download.js`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/csv-download.js).
- **Source links must open the exact line.** GitHub will not render large
  `csl-orig` `.txt` files; use the [`/tools/source`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/source.md)
  viewer and render raw SLP1-inside-markup with
  [`sourceLineToIast` / `sourceTextToIast`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/source-iast.js).
- Scope is gated by `docs/BOUNDARY_RULES.md`: a page belongs here only if its
  primary object is a dictionary, edition, headword/entry, citation/siglum, or
  dictionary-to-dictionary comparison. TEI/OntoLex/FrAC/SHACL/RDF →
  `csl-standards`. DCS/corpus dashboards → `VisualDCS`. Org/CI metrics →
  `csl-observatory`.
- Generated `src/data/**` JSON from `sync-site-data` is gitignored — regenerate,
  do not hand-edit.

## Do not touch

- `dist/`, `node_modules/`, `*.log` — generated/local.
- `src/data/dcs/**`, `src/data/lexico/sense_divergence.json`,
  `src/data/external/{langdetect-candidates,dharmamitra-langdetect}.json`,
  `data/forensic/_f6_tcache.json` — `npm run sync-site-data` outputs.
- TEI/OntoLex/SHACL/RDF work — `csl-standards`, not this repo.
- `csl-orig` — never commit or push dictionary source there.

Issues use the Cologne tooling taxonomy — see
[`/cologne-issue-runbook`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-issue-runbook.md).
Do not recopy type/severity/milestone tables into this file.

Danger facts:
[Uprava DANGER_FACTS.md](https://github.com/gasyoun/Uprava/blob/main/DANGER_FACTS.md)
(org-private) and the generated block of
[AGENTS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/AGENTS.md).

_Dr. Mārcis Gasūns_
