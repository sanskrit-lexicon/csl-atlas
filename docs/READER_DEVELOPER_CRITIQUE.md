_Created: 29-05-2026 · Last updated: 05-09-2026_

# Reader And Developer Critique

Date: 2026-06-04

This is the active critique for the dictionary-only atlas. The old integrated
critique is preserved in
`docs/archive/READER_DEVELOPER_CRITIQUE_LEGACY_INTEGRATED_ATLAS.md`.

## Product Boundary

`csl-atlas` should help a user move from a Sanskrit word or dictionary question
to dictionary evidence, source links, comparison context, and review status.

It should not become the place where corpus, standards/export, or GitHub/org
observatory work accumulates. Those paths now have separate homes:

- DCS and corpus comparison: `VisualDCS`;
- grammar: future grammar repo;
- TEI/OntoLex/FrAC/RDF standards: `csl-standards`;
- GitHub/org observatory: `csl-observatory`.

## From A New Dictionary Reader's Viewpoint

### What Is Strong

- The atlas has a clear source of trust: real dictionary entries and generated
  data that can point back to those entries.
- Reader Lookup v1 gives a direct path from a word to dictionary coverage.
- The existing comparison pages expose useful differences between MW, AP, PWG,
  PWK, WIL, VCP, SKD, and other dictionaries.
- Evidence labels make it possible to say "observed in the source" instead of
  flattening everything into one confidence level.

### What Is Still Weak

- A newcomer still needs a simple answer to "which dictionary should I use?"
- German and Russian scholarly terminology needs careful review; labels should
  not be invented casually.
- Complex tools need short caveats near the data, especially where outputs are
  inferred or machine-reviewed.
- Some older docs still preserve integrated corpus/standards ambitions, so new
  contributors need the boundary docs before acting.

### Reader Priorities

1. Keep the lookup path obvious.
2. Show dictionary choice guidance near the reader entry point.
3. Explain evidence labels in ordinary language.
4. Link from summaries to source records whenever possible.
5. Keep uncertainty visible in tables, cards, and review queues.

## From A Developer's Viewpoint

### What Is Strong

- The atlas now has a narrower, buildable shape: static dictionary evidence and
  comparison data.
- Generated files are compact and committed under predictable locations.
- Review reports already use stable status vocabulary.
- The boundary rules name where standards, corpus, grammar, and observatory work
  belong.

### What Is Still Weak

- Old roadmap files contain valuable dictionary research mixed with old hosting
  assumptions. They need boundary notes rather than silent deletion.
- Review preservation must remain a hard rule whenever generators change.
- Reader Lookup v1 needs tests for normalization, no-result behavior, source
  links, and mobile rendering.
- Any future cross-repo integration object must be justified by real conflicts,
  not introduced as a large abstraction first.

### Developer Priorities

1. Keep new atlas pages dictionary-first.
2. Add locale keys for public bilingual text instead of hard-coding labels.
3. Preserve human review fields across generator reruns.
4. Make every generated output carry assumptions, warnings, and evidence labels.
5. Keep DCS/corpus, TEI/OntoLex/FrAC, and GitHub/org work out of package scripts.

## Acceptance Shape

The atlas is healthy when:

- a reader can look up a word and see dictionary coverage;
- a reviewer can find the highest-value queues;
- a researcher can trace a chart to generated data and source records;
- a developer can run validation without rebuilding external standards or corpus
  systems;
- boundary violations are caught by documentation before they become code.

## Related Docs

- `docs/BOUNDARY_RULES.md`
- `docs/USE_CASES.md`
- `docs/DICTIONARY_USER_GUIDE.md`
- `docs/EVIDENCE_LABELS.md`
- `docs/REVIEW_RELEASE_ROADMAP.md`
- `docs/archive/READER_DEVELOPER_CRITIQUE_LEGACY_INTEGRATED_ATLAS.md`

_Dr. Mārcis Gasūns_
