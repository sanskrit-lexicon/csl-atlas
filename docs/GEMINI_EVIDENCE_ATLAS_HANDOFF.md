# Legacy Integrated Atlas Handoff Pointer

Date: 2026-06-04

The original Gemini evidence-atlas handoff mixed dictionary evidence, corpus
grammar, DCS ingestion, TEI/OntoLex review patterns, and a broad `LexemeHub`
architecture.

That mixed direction is no longer active for `csl-atlas`.

The full historical text is preserved at
`docs/archive/GEMINI_EVIDENCE_ATLAS_HANDOFF_LEGACY_INTEGRATED_ATLAS.md` so earlier
reasoning remains auditable. New implementation work must use the current
boundary documents instead:

- `docs/BOUNDARY_RULES.md`
- `ARCHITECTURE.md`
- `docs/SESSION_HANDOFF.md`
- `docs/REVIEW_RELEASE_ROADMAP.md`
- `docs/USE_CASES.md`

Active rule: `csl-atlas` starts from dictionaries, headwords, dictionary
entries, source citations, comparison outputs, and dictionary review queues.
Corpus, grammar, standards/export, and GitHub/org observatory work must stay in
their own repositories.
