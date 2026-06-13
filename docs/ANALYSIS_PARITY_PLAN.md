# Full Analysis Parity For Broad Dictionaries

## Goal

All eligible local Sanskrit/BHS headword dictionaries should be analysed with the
same public Atlas questions wherever the source data supports it:

- headword coverage and overlap
- grammar/POS disagreement
- homonym splitting
- citation apparatus
- sense depth and sense-structure divergence
- dossier/reader lookup evidence

The broad headword lookup is only the first layer. It proves dictionary
presence and record counts; it does not by itself provide equal deep analysis.

## Current Audit

Run:

```bash
npm run audit-analysis-capabilities
```

This writes `src/data/dicts/analysis-capability-audit.json`.

Latest broad-set audit:

| Feature | Already supported | Partial | Parser candidates | Weak marker evidence | Missing marker evidence |
| --- | ---: | ---: | ---: | ---: | ---: |
| Grammar/POS | 5 | 2 | 4 | 0 | 29 |
| Citations | 4 | 0 | 12 | 20 | 4 |
| Homonyms | 3 | 0 | 17 | 2 | 18 |
| Senses | 3 | 0 | 18 | 1 | 18 |

`candidate` means enough encoded evidence exists to build or validate a parser.
It is not yet a promise that the dictionary can be compared at the same quality
as MW/AP/PWG/PWK/WIL/VCP/SKD.

## Required Work

1. **Promote shared analyses to the broad set where evidence is neutral.**
   Coverage, pairwise overlap, unique vocabulary, and dossier presence can use
   all broad dictionaries now, with local-only source-link handling.

2. **Add grammar adapters.**
   Keep existing MW/AP/PWG/PWK/WIL `<lex>` extraction, existing SKD/VCP prose
   markers, then validate candidates such as PWKVN, CAE, MD, and BHS before
   including them in gender conflicts.

3. **Add citation adapters.**
   Extend `<ls>` apparatus handling beyond MW/AP/PWG/PWK, then build separate
   prose/source-hint extractors where dictionaries use non-`<ls>` conventions.
   Do not mix `<ls>` source matrices with weak `iti` counts without a method
   label.

4. **Add homonym adapters.**
   Promote dictionaries with meaningful `<h>` usage after checking whether the
   marker means true homonymy, subentry numbering, or editorial grouping.

5. **Add sense adapters.**
   Support per-dictionary markers such as `<div>`, bullets, and numbered brace
   markers. Each adapter needs tests with known multi-sense and single-sense
   examples so sense-depth pages do not confuse formatting with semantics.

6. **Regenerate public data and pages.**
   Deep pages should report all included dictionaries and show method badges or
   capability notes when a signal is unavailable for a dictionary.

## Acceptance Criteria

- Every one of the 40 broad dictionaries appears in broad coverage/overlap.
- No deep metric treats missing markup as zero evidence.
- Each dictionary has explicit capability metadata for grammar, citations,
  homonymy, and sense segmentation.
- Dossier and public pages remain IAST-only.
- Local-only dictionaries never emit broken GitHub links.
- `npm test`, `npm run audit-analysis-capabilities`, and the Observable build
  pass.
