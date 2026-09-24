# REVIEW_POOL_STUDENT_GUIDE.ru.md — metadoc

_Created: 24-09-2026 · Last updated: 24-09-2026_

Companion record for
[`docs/REVIEW_POOL_STUDENT_GUIDE.ru.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_STUDENT_GUIDE.ru.md).

## Purpose

Teach a second-year Sanskrit student with no lexicography training how to key one row of
each of the three community-review-pool packets (R2 checkpoint ×10, H4 semantic field ×105,
xref shared-core ×40 + 10 auto-resolved) by reading the Cologne source line, not by clicking
the proposed label. One section per packet: what the card shows, what the question really
asks and does not ask, the label vocabulary in plain Russian, a step procedure, worked
examples from real rows, and what to do when unsure. Shared preamble covers the review-sheet
UI, the double-keying protocol (do not peek at the existing R2/H4 decisions), Cologne markup
and the SLP1→IAST table.

## Audience

Students recruited for the review pool (samskrtam.ru network); the adjudicator reading
their `decisions.json`; any session extending the pool to new packets. Reviewer-facing,
Russian only. Not a public-site page and not a second source of truth for any label
vocabulary — those stay in `data/lexico/*_packet.json`.

## Provenance

- Handoff: [H5310](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5310-Fable_csl-atlas_review-pool-student-guide-ru_23.09.26.md)
  (epic E014, ATLAS fair-pubs wave 1), roadmap item «Community review pool v1» in
  [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md).
- Model: Claude Code Fable 5.1 (`claude-fable-5-1`), 24-09-2026.
- Worked-example answers are the recorded decisions in
  `src/data/review/r2-checkpoint-review.json` (10/10 `reviewed-ok`, reviewer gasyoun,
  source-verified notes) and the H1621 agent stage in
  [H4_REVIEW_WORKSHEET.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H4_REVIEW_WORKSHEET.md)
  (89 rows). Xref examples were source-read against the local `csl-orig` clone for this
  document; the packet has no recorded human decisions.
- Sibling docs: [XREF_SHARED_CORE_LABEL_TAXONOMY.ru.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_SHARED_CORE_LABEL_TAXONOMY.ru.md)
  (xref labels, selection bias, MW-on-PWG dependence), [R2_CHECKPOINT_DECISIONS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_CHECKPOINT_DECISIONS.md),
  [H4_SEMANTIC_FIELD_REVIEW.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H4_SEMANTIC_FIELD_REVIEW.md).

## Finding recorded while writing (not fixed here)

The xref source-check packet flags four rows as «exact edge missing in MW». A manual read of
`csl-orig/v02/mw/mw.txt` shows the MW cross-reference present in all four: `Akzit` L22386
«cf. a/nAkzit», `ArAt` L26162 «cf. Are/» (L25987 is a «See s.v.» pointer), `BaMsas` L147529
«cf. Basa/d» — three targets carrying an udātta `/` — and `Darmya` L100511 «cf. -DArmyAyaRa»,
a hyphen-prefixed target inside a continuation sub-record (`<e>2A`). The edge extractor
apparently drops accented targets and does not look into continuation records. The guide
teaches the student to read the line rather than trust the flag; the generator
([scripts/build-xref-source-check-packet.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-xref-source-check-packet.mjs)
and its upstream `m6_xref_lineage.py` normaliser) is unchanged by this handoff.

## Maintenance

- Row identifiers and `L` numbers quoted in the examples are pinned to the committed
  packets of 24-09-2026; a packet regeneration that renumbers rows must be followed by a
  re-read of the examples.
- When the double-keyed sheets (H5308) and the kappa tool (H5309) land, replace the
  «работайте по рабочему листу» fallback in the R2 section with the sheet name and add the
  submission path.
- No test pins this file's figures (unlike the xref taxonomy pair); the counts it repeats
  (10 / 105 = 89 + 16 / 40 + 10, 641 shared edges) come from the generated worksheets,
  which are themselves byte-pinned by `test/review-worksheets.test.mjs`.

_Гасунс_
