# HANDOFF -- Gemini 3.5 Flash Implementation Brief

Last updated: 2026-05-29
Repo: `sanskrit-lexicon/csl-atlas`
Branch: `interoperability-handoff`
Remote baseline: `origin/main` at `1d4a39c atlas: O10 landing-page refresh -- reflects all 9 chapters complete`

> **Status note (2026-05-31):** this brief covers the **MW-PWG-PWK interoperability pilot**, which is complete and merged. The atlas has since grown well beyond it — MW Quantitative Depth (Phase 1), the 7-dictionary Comparative Dictionary Lab (Phase 2), DCS corpus reference inventory (Phase 3a), a review layer, unit tests, and navigation. For current state and history see [`CHANGELOG.md`](CHANGELOG.md); for the overall design see [`ARCHITECTURE.md`](ARCHITECTURE.md); for session continuity see `.ai_state.md`. This document remains accurate as provenance for the interoperability track.

## Read This First

You are implementing the **CSL Atlas**, specifically the new **MW-PWG-PWK Interoperability Atlas** track.

The existing repo is already an **Observable Framework** public atlas. Do not replace it with a plain static site. Add the interoperability work as a new track inside the current atlas.

Fixed project decisions:

- Public web atlas from the beginning.
- TEI is the archival/textual model.
- OntoLex is the semantic/web graph model.
- First sample is automatic hard-case sampling, not manually chosen famous examples.
- English/Russian readiness is required. Keep UI strings in locale JSON where possible.

Do not re-plan the research agenda. Implement the next concrete slice.

## Current Repo Shape

Existing remote atlas files:

| Path | Meaning |
|---|---|
| `src/index.md` | Observable landing page |
| `src/dicts/*.md` | Dictionary chapters for MW, PWG, PWK, AP, WIL, BEN, CAE, SKD, VCP, ARMH, ABCH |
| `src/tools/*.md` | Existing tools: matrix explorer, lineage sankey, type comparator, citation tracer, etc. |
| `src/data/*.json` | Existing cross-dictionary atlas data |
| `src/locales-en.json` / `src/locales-ru.json` | Existing English/Russian UI strings |
| `observablehq.config.js` | Observable Framework config |
| `.github/workflows/build-and-deploy.yml` | GitHub Pages deployment |
| `package.json` | Observable scripts |

This branch adds:

| Path | Meaning |
|---|---|
| `HANDOFF.md` | This implementation brief |
| `scripts/sample-hard-cases.mjs` | Generates 50 MW-led hard cases from local `csl-orig` |
| `data/pilot/hard-cases.json` | Generated pilot sample |
| `data/schema/hard-case.schema.json` | JSON schema for hard-case samples |
| `docs/PROJECT_SPEC.md` | Research/tool specification |
| `docs/ROADMAP_3_MONTHS.md` | Three-month plan |
| `docs/INTEROPERABILITY_MODEL.md` | Neutral model plus TEI/OntoLex mapping |
| `docs/SAMPLING_STRATEGY.md` | Automatic hard-case sampling method |
| `docs/LOSS_REPORT_SCHEMA.md` | Loss-report schema |
| `docs/PAPER_OUTLINE.md` | Paper abstract and outline |
| `docs/BILINGUAL_TERMS.md` | English/Russian terminology notes |
| `docs/ALL_DICTIONARY_COVERAGE.md` | Coverage, size, type, and fit plan for every local CDSL v02 dictionary |
| `scripts/build-dictionary-coverage.mjs` | Generates all-dictionary coverage and size data |
| `src/tools/dictionary-coverage.md` | Observable all-dictionary coverage tool |
| `scripts/select-review-cases.mjs` | Deterministically selects the 15-case TEI/OntoLex review slice |
| `data/pilot/review-cases.json` | Generated 15-case review slice metadata |
| `scripts/validate-tei-profile.mjs` | Validates all 50 TEI archival profile files against the project ODD/profile |
| `scripts/validate-ontolex-profile.mjs` | Validates all 50 OntoLex/FrAC JSON-LD plus RDF/Turtle files against the project SHACL/profile |
| `data/schema/tei-archival-profile.odd.xml` | Project TEI ODD/profile for generated archival XML |
| `data/schema/ontolex-frac-profile.shacl.ttl` | Project SHACL/profile for generated OntoLex/FrAC/RDF |
| `data/pilot/tei-review.json` | Full 50-case TEI machine-review report |
| `data/pilot/ontolex-review.json` | Full 50-case OntoLex/RDF machine-review report |
| `scripts/validate-external-profiles.mjs` | Optional external TEI/SHACL validation harness with strict mode |
| `data/pilot/external-validation-review.json` | Generated external-tool availability and validation report |
| `docs/VALIDATED_INTEROPERABILITY_PROFILE.md` | Implementation notes for the validated profile |

Generated sample currently has:

- 50 total cases.
- 12 roots.
- 15 compounds.
- 8 continuations.
- 27 `L.` hedge cases.
- All 50 have MW/PWG/PWK matched records.
- 15 deterministic review cases selected from hard cases:
  - 5 roots.
  - 5 compounds.
  - 3 continuations.
  - 2 hedge-only cases.
- 50 generated TEI archival-profile XML files in `data/pilot/tei/`.
- 50 generated OntoLex/FrAC JSON-LD files in `data/pilot/ontolex/`.
- 50 generated RDF/Turtle files in `data/pilot/rdf/`.
- 50-case TEI ODD/profile validation passes.
- 50-case OntoLex/RDF SHACL/profile validation passes.

## Commands

Run from repo root:

```bash
npm install
npm run build-coverage
npm run build-pilot
npm run validate-tei-profile
npm run validate-ontolex-profile
npm run validate-external-profiles
npm run dev
```

Observable preview usually opens at:

```text
http://localhost:3000
```

The sampler expects sibling CDSL source data:

```text
../csl-orig/v02/mw/mw.txt
../csl-orig/v02/pwg/pwg.txt
../csl-orig/v02/pw/pw.txt
```

The coverage builder scans every sibling dictionary with this shape:

```text
../csl-orig/v02/<code>/<code>.txt
```

Do not commit full source dictionaries. They are huge and live in `csl-orig`.

`npm run build-pilot` now runs the complete pilot pipeline:

```bash
npm run sample-hard-cases
npm run select-review-cases
npm run build-neutral-model
npm run build-loss-reports
npm run export-tei-stubs
npm run export-ontolex-stubs
npm run validate-pilot
npm run validate-tei-profile
npm run validate-ontolex-profile
```

## Implementation Style For Gemini Flash

Be literal and incremental.

Good:

- Add one script at a time.
- Keep data formats small and documented.
- Prefer plain JavaScript and Observable Markdown pages.
- Keep generated outputs reproducible.
- Preserve the current Observable Framework architecture.
- Use generated JSON as the source of truth.

Avoid:

- Do not introduce React, Vue, Vite, Next, or a database.
- Do not remove Observable Framework.
- Do not redesign the whole atlas UI.
- Do not rewrite the sampler unless a task explicitly requires it.
- Do not create a full RDF pipeline before the neutral model exists.
- Do not manually curate the pilot sample as the primary method.
- Do not silently hide conversion loss.

## Current Implemented Slice

Atlas v0.1 now has the first serious TEI/OntoLex implementation layer:

- automatic hard-case sample remains 50 cases;
- deterministic review slice selects 15 hard cases;
- TEI output is no longer a toy entry-only stub for that slice, but a validated archival profile with `TEI`, `teiHeader`, source-entry citations, safe raw preservation, extracted forms/senses where possible, and phenomenon-specific structures;
- OntoLex output is no longer only a minimal JSON-LD stub, but a validated OntoLex/Lexicog/FrAC graph, with RDF/Turtle mirrors for all 50 cases;
- `src/tools/interoperability-hard-cases.md` marks validated-slice cases, shows full 50-case validation status, and links RDF/Turtle for every case.

Remaining limits are deliberate:

- human philological review of all 50 cases is still separate from machine validation;
- external TEI ODD compilation and external SHACL-engine execution are wired through `npm run validate-external-profiles`, but a full pass depends on local `teitorelaxng`, `jing` or `xmllint`, and `pyshacl` availability.

## Historical v0.1 Implementation Slice

Implement **Atlas v0.1 data workbench**.

The initial workbench goal was to make each hard case navigable and ready for mapping. The newer validated-slice work above supersedes the stub-only parts of this section, but the task list remains useful as provenance for the branch.

### Task 1: Observable Hard-Case Tool Page

Add:

```text
src/tools/interoperability-hard-cases.md
```

Then link it from `src/index.md` or the existing tools list.

Behavior:

- Load `data/pilot/hard-cases.json`.
- Show all 50 case cards.
- Selecting a case opens or reveals a detail panel.
- Detail panel shows:
  - key;
  - phenomena badges;
  - MW raw snippet;
  - PWG raw snippet;
  - PWK raw snippet;
  - loss hints;
  - source pointers: `L`, `line`, `pc`.

Acceptance:

- All 50 cases remain visible.
- Works from `npm run dev`.
- `npm run build` still passes.
- No horizontal overflow at mobile width.

### Task 2: Neutral Model Generator

Add:

```text
scripts/build-neutral-model.mjs
data/pilot/neutral-model.json
data/schema/neutral-model.schema.json
```

Input:

```text
data/pilot/hard-cases.json
```

Output model per item:

```json
{
  "id": "mw-pwg-pwk:ac",
  "key": "ac",
  "phenomena": ["hedge", "root"],
  "records": {
    "mw": { "L": "...", "line": 0, "pc": "...", "raw": "..." },
    "pwg": { "L": "...", "line": 0, "pc": "...", "raw": "..." },
    "pwk": { "L": "...", "line": 0, "pc": "...", "raw": "..." }
  },
  "forms": [],
  "senses": [],
  "citations": [],
  "relations": [],
  "loss": []
}
```

Keep arrays empty or heuristic at first. Do not overbuild.

Acceptance:

- `node scripts/build-neutral-model.mjs` writes valid JSON.
- Add npm script:

```json
"build-neutral-model": "node scripts/build-neutral-model.mjs"
```

### Task 3: Machine Loss Reports

Add:

```text
scripts/build-loss-reports.mjs
data/pilot/loss-reports.json
data/schema/loss-report.schema.json
```

Use the vocabulary in `docs/LOSS_REPORT_SCHEMA.md`.

Start with rule-based reports:

| Phenomenon | Target | Status | Reason |
|---|---|---|---|
| `hedge` | `tei` | `partial` | TEI can preserve string/type but not shared evidential semantics |
| `hedge` | `ontolex` | `partial` | Needs explicit evidence/provenance node |
| `root` | `tei` | `partial` | Root as entry is preservable; derivational role is not fully explicit |
| `root` | `ontolex` | `lossy` | Root needs lexical plus derivational relation |
| `compound` | `tei` | `clean` | Subentry structure can be archived |
| `compound` | `ontolex` | `partial` | Decomposition needs component graph |
| `continuation` | `tei` | `partial` | Parent must be recovered from adjacency |
| `continuation` | `ontolex` | `lossy` | Suppressed headword needs explicit parent relation |

Acceptance:

- Every case has at least one loss report.
- Reports use `reviewStatus: "machine"`.
- Add npm script:

```json
"build-loss-reports": "node scripts/build-loss-reports.mjs"
```

### Task 4: TEI Stub Export

Add:

```text
scripts/export-tei-stubs.mjs
data/pilot/tei/
```

Generate one XML file per case.

Keep it simple:

```xml
<entry xml:id="mw-pwg-pwk-ac">
  <form type="lemma"><orth notation="SLP1">ac</orth></form>
  <note type="source" target="mw">...</note>
  <note type="source" target="pwg">...</note>
  <note type="source" target="pwk">...</note>
  <note type="model-loss">Machine-generated stub; not reviewed.</note>
</entry>
```

Acceptance:

- XML escapes raw text correctly.
- No claim of full TEI compliance yet.
- Add npm script:

```json
"export-tei-stubs": "node scripts/export-tei-stubs.mjs"
```

### Task 5: OntoLex JSON-LD Stub Export

Add:

```text
scripts/export-ontolex-jsonld-stubs.mjs
data/pilot/ontolex/
```

Generate one JSON-LD file per case.

Keep it small:

```json
{
  "@context": {
    "ontolex": "http://www.w3.org/ns/lemon/ontolex#",
    "lexicog": "http://www.w3.org/ns/lemon/lexicog#",
    "csl": "https://sanskrit-lexicon.github.io/csl-atlas/ns#"
  },
  "@id": "https://sanskrit-lexicon.github.io/csl-atlas/case/ac",
  "@type": "lexicog:Entry",
  "ontolex:canonicalForm": {
    "ontolex:writtenRep": "ac"
  },
  "csl:phenomenon": ["hedge", "root"]
}
```

Acceptance:

- JSON-LD parses as JSON.
- Add npm script:

```json
"export-ontolex-stubs": "node scripts/export-ontolex-jsonld-stubs.mjs"
```

## Update The Public Page After Data Scripts

After tasks 2-5, extend `src/tools/interoperability-hard-cases.md` to link to:

- neutral model item;
- TEI stub file;
- OntoLex JSON-LD stub file;
- loss reports for the case.

Do this only after the files exist.

## Data Rules

- Generated files under `data/pilot/` may be committed.
- Do not commit `node_modules`.
- Do not commit full `mw.txt`, `pwg.txt`, or `pw.txt`.
- Keep snippets truncated enough for the public atlas.
- Use stable IDs:

```text
mw-pwg-pwk:<k1>
```

If duplicate `k1` cases occur, append MW `L`:

```text
mw-pwg-pwk:<k1>-mw<L>
```

## Known Technical Notes

- The current sampler is MW-led.
- Header parsing already handles MW/PWG/PWK enough to produce 50 cases.
- Some SLP1/raw text may contain mojibake-like display artifacts from terminal rendering. Do not fix source snippets unless the source data is actually wrong.
- Existing atlas pages live in `src/`, not the repository root.
- Do not alter existing dictionary chapters unless adding links to the new interoperability tool.

## Verification Checklist

Before finishing any implementation pass:

```bash
npm run build-pilot
npm run validate-tei-profile
npm run validate-ontolex-profile
npm run build
```

The standalone commands remain available, but `build-pilot` is the canonical full-pipeline check.

Then verify:

- Observable preview loads.
- The interoperability tool page shows 50 cases.
- The page marks the 15 validated-slice cases.
- The page shows full 50-case validation status for TEI and OntoLex/RDF.
- Detail view works.
- JSON files parse.
- TEI files are XML-escaped.
- OntoLex files parse as JSON.
- RDF/Turtle files exist for all 50 cases.

## Final Output Expected From Gemini

When done, report:

- files changed;
- commands run;
- generated artifact counts;
- any limitations;
- next recommended slice.

Keep the report concise. Do not include long pasted data.
