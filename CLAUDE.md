# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

`csl-atlas` is the public **dictionary-evidence** microsite for the Cologne
Digital Sanskrit Dictionaries (CDSL) project — a static, Observable
Framework-based site giving reader-facing chapters, cross-dictionary
comparisons, genealogy/structure views, and review queues for nine narrative
Sanskrit dictionaries (MW, PWG, PWK, AP, WIL, SKD, VCP, ARMH, ABCH) plus an
all-dictionary coverage layer over every local CDSL v02 source. It is
static-first with no backend, database, runtime LLM classification, or
full-text search engine. Companion to the MW microanalysis paper(s) in
`sanskrit-lexicon/MWS`.

## Common commands

```sh
npm run dev              # observable preview (runs sync-site-data first via predev)
npm run build             # observable build → dist/ (runs sync-site-data first via prebuild)
npm run deploy             # observable deploy (runs sync-site-data first via predeploy)
npm test                    # node --test
npm run validate-review-reports   # required before any build in CI
```

Data pipelines are one `npm run build-*` script per dataset (~70 scripts in
`package.json`), each backed by a `scripts/build-*.mjs` (or `.py` for a few
Dharmamitra-import / language-detection / divergence-map scripts). Examples:
`build-mw-depth` + `validate-mw-depth` (MW quantitative depth), `build-dict-comparison`
+ `validate-dict-comparison` (7-dictionary comparison lab), `build-coverage`
(all-dictionary coverage), `build-r2-*` (R2 sense-granularity review series).
Grep `package.json` `scripts` for the exact one you need — do not guess a name.

## Key directories / files

| Path | Purpose |
|---|---|
| `src/` | Observable Framework site source — pages (`.md`), `src/data/*.json` (generated data, partly gitignored), `src/lib/`, `src/tools/*.md` (interactive tool pages), `src/paper/*.md` (paper-tour pages), `src/dicts/*` (per-dictionary chapters) |
| `scripts/` | Node (`.mjs`) and Python build/import/validation scripts, one per data pipeline; `scripts/lib/` holds shared parsers (`mw-parser`, `dict-{normalize,manifest,parser,align}`, etc.) |
| `docs/` | Architecture, boundary rules, per-phase plans/handoffs/review worksheets — read `ARCHITECTURE.md` and `docs/BOUNDARY_RULES.md` first for scope decisions |
| `data/` | Raw/intermediate data inputs (not the generated `src/data/` site copies) |
| `dist/` | Build output — generated, gitignored |
| `.ai_state.md` | Session journal (org-wide convention, see `../CLAUDE.md`) |

## CI workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| `test.yml` | PR, push to `main`, manual | `npm ci` → `npm test` → `validate-review-reports` → `npm run build` |
| `build-and-deploy.yml` | push to `main`, manual | Same test/validate/build steps, then uploads `dist/` and deploys to GitHub Pages |
| `codeql.yml` | push to `main` | CodeQL SAST scan |
| `dependabot-auto-merge.yml` | Dependabot PRs | Auto-merges dependency bumps once checks pass |

## Conventions

- **Display Sanskrit in IAST, never raw SLP1 — a general rule for every
  human-facing page.** SLP1 (`aBAga`, `ABicArika`) is a machine key, unreadable
  to a human; convert it for display with `slp1ToIast` from
  [`src/lib/lookup-normalize.js`](src/lib/lookup-normalize.js) (the canonical
  client-side transcoder; `from_slp1` in `src/lib/sanskrit-util.js` is the same
  map). Keep the SLP1 form only as a muted secondary / search key, and export
  IAST first in any CSV. Any table, list, heading, or link text that shows a
  bare SLP1 headword is a defect to fix.
- **Every table or list gets a CSV download.** Use the shared
  [`csvDownloadButton`](src/lib/csv-download.js) helper (client-side Blob, no
  backend) so a reader can pull the data behind any view; it takes a thunk so the
  export reflects the current filtered set.
- **Source links must open the exact line, not a multi-MB blob.** GitHub refuses
  to render the large `csl-orig` `.txt` files (only "View raw"; `#L…` anchors
  never fire), so review data embeds a compact inline entry snippet
  (`scripts/lib/source-snippet.mjs`) and the
  [`/tools/source`](src/tools/source.md) viewer streams the raw file and stops at
  the requested line + context. Point per-line source references at that viewer.
- **Scope is gated by `docs/BOUNDARY_RULES.md`** (superseded by/consistent with
  `ARCHITECTURE.md`): a page/script/dataset belongs here only if its primary
  object is a dictionary, edition, headword/entry, source citation/siglum, or
  a dictionary-to-dictionary comparison. TEI/OntoLex/FrAC/SHACL/RDF work
  belongs in the sibling `csl-standards` repo instead — do not re-add it here.
  DCS/corpus dashboards belong in `VisualDCS`; org/CI metrics belong in
  `csl-observatory`.
- Data pipelines are **deterministic and source-derived** where possible
  (parsed straight from `csl-orig` dictionary text) — "inferred" or
  "approximate" metrics (lexical families, source-layer dating) are explicitly
  flagged as such in the README/docs and routed to review queues, not asserted
  as fact.
- Generated `src/data/**` JSON files that are build outputs of `sync-site-data`
  are gitignored (see `.gitignore`) — only the pipeline inputs and the
  `scripts/build-*` sources are committed; don't hand-edit generated JSON.
- Every build script has a paired `validate-*` script where cross-dictionary
  correctness matters (e.g. `build-mw-depth`/`validate-mw-depth`,
  `build-dict-comparison`/`validate-dict-comparison`) — run the validator after
  regenerating data, not just the builder.
- Legacy architecture doc is preserved, not deleted: `docs/archive/ARCHITECTURE_LEGACY_INTEGRATED_ATLAS.md`.

## What not to touch

- `dist/`, `node_modules/`, `*.log` (`observable-preview*.log`) — generated/local, gitignored.
- `src/data/dcs/**`, `src/data/lexico/sense_divergence.json`,
  `src/data/external/{langdetect-candidates,dharmamitra-langdetect}.json`,
  `data/forensic/_f6_tcache.json` — generated site-facing copies produced by
  `npm run sync-site-data`, explicitly gitignored; regenerate, don't hand-edit.
- TEI/OntoLex/SHACL/RDF standards work — that's `csl-standards`' territory per
  `docs/BOUNDARY_RULES.md`, not this repo's.
