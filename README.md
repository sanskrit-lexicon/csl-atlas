# csl-atlas — Atlas of the Cologne Digital Sanskrit Lexicons

An interactive companion to the [CDSL](https://www.sanskrit-lexicon.uni-koeln.de/) — comparative microstructural analysis of nine narrative Sanskrit-dictionary chapters, plus an all-dictionary coverage layer for every local CDSL v02 source dictionary.

**Status:** active public-atlas implementation. The main atlas chapters and interoperability pilot are reproducible from committed JSON plus local `csl-orig` source dictionaries.

---

## What this is

Companion microsite to the [MW microanalysis paper(s)](https://github.com/sanskrit-lexicon/MWS/tree/docs-pass/papers/microanalysis). Static + interactive. Two reader paths:

- **Paper tour:** read the current atlas argument pages ([Grounded](src/paper/grounded.md) · [Triangulation](src/paper/triangulation.md) · [Appendices](src/paper/appendices.md)).
- **Tools:** explore standalone visualisations — [Cross-Dictionary Comparison](src/tools/cross-dict.md), [All-Dictionary Coverage](src/tools/dictionary-coverage.md), [Matrix Explorer](src/tools/matrix-explorer.md), [Lineage Sankey](src/tools/lineage-sankey.md), [Typology Treemap](src/tools/typology-treemap.md), [Lexicographic Timeline](src/tools/timeline.md), [Type Comparator](src/tools/type-comparator.md), [Citation Tracer](src/tools/citation-tracer.md), and [MW-PWG-PWK interoperability hard cases](src/tools/interoperability-hard-cases.md).

Current URL structure:

```
/                        landing (EN)
/tools/dictionary-coverage
/tools/matrix-explorer   18×8 block/type matrix explorer
/tools/lineage-sankey    kosha → WIL/PWG/PWK/MW lineage Sankey
/tools/interoperability-hard-cases
/paper/grounded
/paper/triangulation
/dicts/mw
```

---

## Coverage (Phase 4 atlas — 9 narrative dicts + all-dictionary inventory)

| Repo | Title | Date | Vols | Status |
|---|---|---|---:|---|
| [MW](https://github.com/sanskrit-lexicon/MWS) | Monier-Williams Sanskrit-English Dictionary | 1899 | 1 | chapter ready |
| [PWG](https://github.com/sanskrit-lexicon/PWG) | Petersburg Sanskrit-Wörterbuch | 1855–75 | 7 | chapter ready |
| [PWK](https://github.com/sanskrit-lexicon/PWK) | Petersburg *Kürzerer Fassung* | 1879–89 | 7 | chapter ready |
| [AP](https://github.com/sanskrit-lexicon/AP) | Apte *Practical* Sanskrit-English | 1957 | 3 | chapter ready |
| [WIL](https://github.com/sanskrit-lexicon/WIL) | Wilson Sanskrit-English | 1832 | 1 | chapter ready |
| [SKD](https://github.com/sanskrit-lexicon/SKD) | *Śabdakalpadruma* (Sanskrit-Sanskrit) | 1822–58 | 7 | chapter ready |
| [VCP](https://github.com/sanskrit-lexicon/vcp) | *Vācaspatya* (Sanskrit-Sanskrit) | 1873–84 | 7 | chapter ready |
| [ARMH](https://github.com/sanskrit-lexicon/armh) | Halāyudha's *Abhidhānaratnamālā* | ~10th c. | 1 | chapter stub |
| [ABCH](https://github.com/sanskrit-lexicon/abch) | Hemacandra's *Abhidhānacintāmaṇi* | ~12th c. | 1 | chapter stub |

Each narrative dictionary gets a chapter; each Tier-1 figure has a per-dictionary variant and a cross-dictionary comparative variant. The separate all-dictionary inventory is generated from local `../csl-orig/v02` and currently covers 43 dictionaries with main source files.

---

## MW-PWG-PWK interoperability track

The interoperability track tests how difficult Sanskrit lexicographic cases move across CDSL source records, TEI archival encoding, and OntoLex semantic modeling.

- [Implementation handoff](HANDOFF.md)
- [Project specification](docs/PROJECT_SPEC.md)
- [All-dictionary coverage and size layer](docs/ALL_DICTIONARY_COVERAGE.md)
- [Interoperability model](docs/INTEROPERABILITY_MODEL.md)
- [Validated TEI and OntoLex/FrAC profile](docs/VALIDATED_INTEROPERABILITY_PROFILE.md)
- [Sampling strategy](docs/SAMPLING_STRATEGY.md)
- [Loss-report schema](docs/LOSS_REPORT_SCHEMA.md)

Regenerate and validate the full pilot with:

```bash
npm run build-pilot
```

Run the optional external validation harness with locally installed TEI/SHACL tools:

```bash
npm run validate-external-profiles
npm run validate-external-profiles:strict
```

The external harness records TEI ODD/RELAX NG and SHACL-engine status in `data/pilot/external-validation-review.json`. It uses `teitorelaxng` from the TEI Stylesheets when available, validates TEI XML with `jing` or `xmllint`, and validates RDF/Turtle with `pyshacl`. Set `CSL_ATLAS_TEI_RNG` to reuse a precompiled TEI RELAX NG schema.

---

## Tech stack

- [**Observable Framework**](https://observablehq.com/framework) (per [Decision 10](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/VISUALISATIONS.md#decision-10--microsite-stack-observable-framework))
- Data: committed JSON exports in `src/data/`, plus generated pilot artifacts in `data/pilot/` and mirrored app JSON in `src/data/pilot/`.
- Palette: committed `src/palette.css` and `src/data/palette-tokens.json`.
- i18n: English/Russian strings in `src/locales-en.json` and `src/locales-ru.json`; the interoperability page exposes a language toggle.
- Deployment: GitHub Pages on push to `main` (workflow in `.github/workflows/build-and-deploy.yml`)

---

## Local development

```bash
npm install
npm run build-coverage
npm run build-pilot
npm run dev      # starts dev server on http://localhost:3000
npm run build    # produces dist/ for GitHub Pages
```

(See [Observable Framework docs](https://observablehq.com/framework/getting-started) for full reference.)

---

## Status checklist

- [x] Observable Framework atlas
- [x] Landing page and dictionary chapters
- [x] Interactive tools: matrix explorer, lineage Sankey, typology treemap, timeline, type comparator, citation tracer
- [x] All-dictionary coverage and size inventory for local CDSL v02 source files
- [x] MW-PWG-PWK hard-case interoperability page
- [x] Pilot generators for hard cases, neutral model, loss reports, TEI profile XML, and OntoLex/FrAC JSON-LD
- [x] 15-case validated TEI archival profile slice beyond stubs
- [x] 15-case validated OntoLex/FrAC JSON-LD plus RDF/Turtle profile slice
- [x] Full 50-case archival TEI machine review and project ODD/profile validation
- [x] Full 50-case OntoLex/RDF machine review and project SHACL/profile validation
- [x] Optional external TEI/SHACL validation harness with strict mode
- [x] Build and link validation
- [ ] Human philological review of all 50 TEI/OntoLex cases

---

## License

CC-BY-SA-4.0, matching [MWS](https://github.com/sanskrit-lexicon/MWS).

Source data: [CDSL csl-orig](https://github.com/sanskrit-lexicon/csl-orig), `mw.txt` 2026-05-23 and sibling dict files. All figures regenerate from JSON data via Python scripts in [MWS papers/microanalysis/figures/scripts/](https://github.com/sanskrit-lexicon/MWS/tree/docs-pass/papers/microanalysis/figures/scripts).
