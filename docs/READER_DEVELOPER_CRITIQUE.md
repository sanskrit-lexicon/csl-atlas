# Reader And Developer Critique

Date: 2026-05-29

This note critiques the current Sanskrit Evidence Atlas direction from two practical viewpoints:

- a new reader who wants to use Sanskrit dictionaries;
- a developer who wants to decide where to contribute next.

The goal is to keep the atlas from becoming only an expert-facing architecture document.

## From A New Dictionary Reader's Viewpoint

### What Is Strong

- The project has a clear scholarly center: connect dictionaries, corpus evidence, grammar, and source links.
- The existing dictionary pages already give readers a place to start with MW, AP, PWG, PWK, WIL, VCP, SKD, and other CDSL dictionaries.
- The typology treemap and article examples make MW less opaque: readers can see that the dictionary is made of roots, nouns, compounds, derivatives, continuations, and source-heavy records.
- Source links to `csl-orig` are valuable because a reader can inspect real dictionary records instead of trusting only a dashboard summary.

### What Is Still Weak

- A newcomer does not yet have a simple answer to "Which dictionary should I use first?"
- The site needs a reader-facing path separate from the research pipeline. The architecture is strong, but it can feel like an internal engineering plan.
- Terms such as `OntoLex`, `FrAC`, `lexicographer-only`, `source layer`, and `LexemeHub` need plain-language explanations near the UI.
- The project has many tools, but no guided "start here" flow for someone looking up a Sanskrit word.
- The English/Russian bilingual layer is present, but the German scholarly layer is not yet explained to ordinary users.
- Evidence labels like `observed`, `derived`, and `inferred` are methodologically good, but they need reader-friendly labels such as "in the source", "computed", and "probable".
- The current pages risk making dictionary data look more certain than it is unless uncertainty and review status are visible.

### Reader-Facing Improvements To Prioritize

1. Add a "How to use these dictionaries" page.
2. Add a per-dictionary "best for" summary:
   - MW: broad Sanskrit-English lookup and citations.
   - AP: practical Sanskrit-English lookup.
   - PWG/PWK: deep German lexicographic tradition.
   - WIL/VCP/SKD: complementary coverage and older lexicographic perspectives.
3. Add a "What does this evidence label mean?" explainer.
4. Add a "Look up a word" path that leads to dictionary entries first, and research dashboards second.
5. Add compact tooltips or glossary links for Sanskrit and digital-lexicography terms.
6. Make uncertainty visible in tables and cards, especially for inferred families, diachronic layers, and dictionary alignments.

## From A Developer's Viewpoint

### What Is Strong

- The project now has a realistic phase order: MW depth first, dictionary comparison second, DCS corpus grammar third.
- The documentation states important boundaries: no runtime LLM classification, no raw dictionary commits, static-first Observable, compact generated JSON.
- The handoff gives concrete scripts, data outputs, pages, commands, and acceptance criteria for Phase 1.
- The evidence-level policy makes the future review interface feasible.
- The separation between source data, generated data, review reports, and Observable pages is mostly clear.

### What Is Still Weak

- The architecture is ambitious enough that a new developer may not know what "done" means for a small contribution.
- Source availability is uneven: CDSL is local, DCS exists but path/schema are not documented, and GRETIL/Ambuda/Sanskrit Library are future work.
- The difference between user-facing pages and internal validation reports should be made clearer.
- `LexemeHub` is conceptually central, but should not be implemented before the simpler MW and dictionary-comparison outputs exist.
- Diachronic layers are necessary, but source abbreviation mapping can become a large scholarly task. The first pass must be intentionally conservative.
- Review queues need a stable schema before they become scattered one-off reports.
- There is not yet a single developer checklist saying "if you only have one day, do this."

### Developer-Facing Improvements To Prioritize

1. Keep Phase 1 small and deterministic:
   - parser;
   - classifiers;
   - source-layer map;
   - compact summaries;
   - validation report;
   - three Observable pages.
2. Do not build a generalized corpus model before DCS schema is inspected and documented.
3. Do not build full `LexemeHub` before comparative dictionary alignment produces real conflicts.
4. Add a review-report schema shared by MW depth, dictionary comparison, and corpus grammar.
5. Make every generated output carry `assumptions`, `warnings`, and `evidenceLevels`.
6. Treat source-layer mapping as a growing reviewed dataset, not as a one-shot script.
7. Preserve small examples with links in every dashboard so developers can debug metrics from source records.

## Product Correction

The atlas needs two entry modes:

```text
Reader mode:
  I want to look up a Sanskrit word and understand which dictionary evidence I can trust.

Research/developer mode:
  I want to inspect, compare, validate, and improve dictionary and corpus data.
```

Both modes should use the same underlying evidence model, but they should not expose the same level of complexity by default.

## Concrete Next Documentation Tasks

Before or alongside implementation, add:

- `docs/DICTIONARY_USER_GUIDE.md`
- `docs/EVIDENCE_LABELS.md`
- `docs/REVIEW_REPORTS.md`

These should be short and reader-facing. They should explain the atlas without requiring knowledge of TEI, OntoLex, Observable, or CDSL internals.

## Concrete Next Implementation Tasks

When implementation resumes, start with the approved Phase 1:

1. implement MW Quantitative Depth;
2. expose source-linked examples;
3. show evidence labels and warnings in the UI;
4. validate generated counts against existing MW typology counts;
5. add review queues only where the machine output is uncertain.

Do not start dictionary comparison or corpus grammar in the same pass unless explicitly requested.
