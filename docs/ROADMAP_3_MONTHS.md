# Three-Month Roadmap

This roadmap assumes the atlas is public from the first scaffold, but scholarship leads the engineering. The tool is a research instrument.

## Month 1: Model And Hard Sample

Goal: define the research object and generate the first difficult sample.

Deliverables:

- Project spec and public site skeleton.
- All-dictionary coverage and size inventory for local CDSL v02 source files.
- Neutral JSON model v0.1.
- Automatic hard-case sampler for MW/PWG/PWK.
- First generated 50-entry sample.
- TEI and OntoLex mapping notes for the first 5 cases.

Work packages:

1. Stabilize hard-case signatures: `L.`, roots, compounds, continuations, citation compression.
2. Parse MW/PWG/PWK records from local `csl-orig`.
3. Match records by `k1` headword key.
4. Score candidates by interoperability stress.
5. Publish generated JSON plus a minimal public browser.
6. Generate the all-dictionary coverage layer: records, entry length, block population, block character mass, type counts, and fit bands.
7. Start manual mapping notes for the top cases.

Milestone:

> Atlas v0.0.1: public page + generated hard-case sample + model draft.
> Atlas v0.0.2: all-dictionary coverage page + generated coverage JSON.

## Month 2: TEI/OntoLex Workbench

Goal: make the atlas show actual interoperability, not only records.

Deliverables:

- TEI archival-profile export for the full 50-case pilot, with a deterministic 15-case initial review slice preserved.
- OntoLex/FrAC JSON-LD plus RDF/Turtle export for the full 50-case pilot.
- Project ODD/profile and SHACL/profile validators for TEI XML and OntoLex/FrAC/RDF artifacts.
- Loss-report schema.
- Public entry pages or richer client-side explorer.
- English/Russian UI labels in locale files.

Work packages:

1. Implement neutral-model-to-TEI serializer for a constrained subset.
2. Implement neutral-model-to-OntoLex serializer for the same subset.
3. Select 15 hard cases deterministically from roots, compounds, continuations, and hedge-only records.
4. Define evidence classes:
   - named textual citation
   - named kosha citation
   - generic lexicographer hedge
   - editorial self-reference
   - catalogue/bibliographic reference
   - unresolved/ambiguous source
5. Add compound relation types:
   - archival subentry
   - lexical decomposition
   - unresolved segmentation
6. Add root relation types:
   - lexical root entry
   - derivational base
   - preverb construction
   - grammatical class carrier
7. Produce loss reports for at least 15 entries.
8. Validate the selected TEI profile and OntoLex/FrAC profile reproducibly.
9. Extend machine review, ODD/profile validation, RDF/Turtle export, and SHACL/profile validation to all 50 cases.

Milestone:

> Atlas v0.1: first TEI/OntoLex comparative views with explicit loss reports.

## Month 3: Argument And Public Research Release

Goal: turn the tool into an argument.

Deliverables:

- Paper abstract.
- Detailed paper outline.
- Figures for the core argument.
- Reviewed 50-case dataset.
- Public release notes.

Work packages:

1. Analyze successful mappings versus lossy mappings.
2. Classify failures by cause:
   - model vocabulary gap
   - CDSL markup gap
   - print compression
   - Sanskrit-specific lexicographic convention
   - unresolved data quality issue
3. Compare MW/PWG/PWK transformations:
   - PWG named evidence retained or lost
   - PWK abbreviation/compression
   - MW `L.` conversion or collapse
4. Use all-dictionary coverage to identify which non-MW/PWG/PWK dictionaries deserve the next curated chapters.
5. Draft the TEI/OntoLex extension proposal.
6. Add Russian abstract and terminology review layer.
7. Prepare a small public demo narrative.

Milestone:

> Atlas v0.2: public research demo + paper skeleton + extension proposal.

## Non-Negotiables

- Keep every generated dataset reproducible.
- Do not hide model failures.
- Keep TEI archival and OntoLex semantic roles separate.
- Keep English/Russian labels decoupled from data.
- Keep public pages static unless interactivity clearly earns its weight.
