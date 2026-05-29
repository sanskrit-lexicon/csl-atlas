# Sanskrit Evidence Atlas Use Cases

Date: 2026-05-29

Status: comprehensive use-case inventory for planning. This document is intentionally broad. It should guide documentation, implementation, review queues, and future product decisions.

## Purpose

The Sanskrit Evidence Atlas connects three evidence domains:

```text
corpus evidence + grammar + lexicography
```

The use cases below describe how different users should be able to move from a question to evidence:

```text
question -> atlas view -> evidence object -> source link -> review status
```

No use case should require the user to trust an untraceable claim.

## Priority Legend

| Priority | Meaning |
|---|---|
| `P0` | Needed for the first credible public research atlas |
| `P1` | Important after the first MW and dictionary-comparison layers exist |
| `P2` | Valuable once corpus ingestion is stable |
| `P3` | Later expansion or specialized expert workflow |

## Evidence Labels

Every use case should preserve the evidence label where relevant:

| Label | Meaning |
|---|---|
| `observed` | directly present in a dictionary, corpus export, or source file |
| `derived` | computed by deterministic rule |
| `inferred` | heuristic and uncertain |
| `reviewed` | checked or corrected by a human reviewer |

## Entry Modes

The atlas should support several entry modes that share the same underlying evidence model.

| Mode | Main user question | Main output |
|---|---|---|
| Reader mode | What does this Sanskrit word mean, and which dictionary evidence supports it? | clear dictionary-first lemma view |
| Research mode | What pattern can be seen across dictionaries, corpora, genres, or periods? | dashboards and linked evidence |
| Developer mode | Which parser, mapping, or generated dataset should I improve? | validation reports and implementation tasks |
| Review mode | Which machine-generated claims need human judgment? | review queues |
| Teaching mode | How can I explain a grammar or lexicographic pattern to students? | examples, glossaries, and visual summaries |
| Data reuse mode | How can I reuse the generated data elsewhere? | compact JSON, RDF/Turtle, schemas, and provenance |

## Reader And Dictionary Use Cases

These use cases serve a reader who wants to use Sanskrit dictionaries without first learning the whole pipeline.

### UC-RD-01 Basic Word Lookup `P0`

- Actor: reader, student, translator.
- Goal: enter a Sanskrit headword or form and find dictionary evidence.
- Atlas response: show matching dictionary entries, normalized lemma candidates, dictionary coverage, and source links.
- Evidence: dictionary records, line links, confidence for normalization.

### UC-RD-02 Choose Which Dictionary To Use `P0`

- Actor: new dictionary user.
- Goal: understand whether to start with MW, AP, PWG, PWK, WIL, VCP, or SKD.
- Atlas response: show "best for" notes, language of definitions, coverage, source style, and known limitations.
- Evidence: dictionary metadata and coverage summaries.

### UC-RD-03 Multi-Dictionary Lemma View `P0`

- Actor: reader, Sanskritist.
- Goal: see all available dictionary records for one lemma side by side.
- Atlas response: display aligned entries, dictionary-specific senses, citations, POS/gender, and warnings.
- Evidence: normalized dictionary alignment and source record links.

### UC-RD-04 No Result Or Ambiguous Result `P0`

- Actor: student or reader.
- Goal: recover from a failed lookup.
- Atlas response: suggest transliteration variants, normalized forms, likely compounds, sandhi splits, and nearby dictionary forms.
- Evidence: headword normalization, dictionary coverage, uncertainty flags.

### UC-RD-05 Transliteration Support `P0`

- Actor: reader using SLP1, IAST, Harvard-Kyoto, or Devanagari.
- Goal: search without knowing the repository's internal encoding.
- Atlas response: normalize input, show the normalized form, and preserve the original query.
- Evidence: deterministic transliteration rules and warnings for ambiguous mappings.

### UC-RD-06 Understand A Dictionary Abbreviation `P0`

- Actor: reader.
- Goal: understand `MW`, `PWG`, `PWK`, `L.`, source abbreviations, and technical tags.
- Atlas response: show glossary popovers or a linked explanatory page.
- Evidence: maintained abbreviation map and source-layer map.

### UC-RD-07 Interpret A German Dictionary Entry `P1`

- Actor: English/Russian reader using PWG or PWK.
- Goal: understand the value of German lexicographic evidence.
- Atlas response: preserve German wording, show dictionary metadata, and provide optional English/Russian interface explanation.
- Evidence: original dictionary record and dictionary metadata.

### UC-RD-08 Beginner-Safe Lemma Summary `P1`

- Actor: student.
- Goal: get a compact answer before seeing complex dictionary data.
- Atlas response: show a cautious summary with "dictionary says", "corpus evidence", and "uncertain" sections.
- Evidence: dictionary alignment, corpus frequency, evidence labels.

### UC-RD-09 Follow A Source Citation `P1`

- Actor: Sanskritist.
- Goal: see where a cited source abbreviation comes from.
- Atlas response: link source abbreviation to source-layer metadata and corpus passages when available.
- Evidence: `<ls>` tags, source maps, corpus metadata.

### UC-RD-10 Compare English Glosses `P1`

- Actor: translator.
- Goal: compare English definitions across dictionaries.
- Atlas response: display gloss snippets, dictionary source, and sense segmentation warnings.
- Evidence: dictionary senses, raw snippets, parser confidence.

### UC-RD-11 See Related Forms `P1`

- Actor: reader.
- Goal: discover derivatives, compounds, root relations, and related entries.
- Atlas response: show a lexical family panel with confidence labels.
- Evidence: MW depth outputs, dictionary alignment, inferred family graph.

### UC-RD-12 Understand Whether A Word Is A Compound `P1`

- Actor: reader or student.
- Goal: determine whether a lemma is simple, derived, compound, or continuation.
- Atlas response: show article type, compound components if available, and source examples.
- Evidence: MW classifier, dictionary markup, compound heuristic.

### UC-RD-13 Copy A Citation Or Permalink `P1`

- Actor: scholar, student.
- Goal: cite a dictionary entry or atlas view.
- Atlas response: provide stable links, dictionary record IDs, and recommended citation text.
- Evidence: generated IDs and source links.

### UC-RD-14 Compare Dictionary Entry With Corpus Attestation `P2`

- Actor: reader, translator.
- Goal: see whether a dictionary word is attested in corpus data.
- Atlas response: show corpus examples, genre/period, and whether the lemma is dictionary-only or corpus-attested.
- Evidence: DCS/GRETIL occurrence data and dictionary alignment.

### UC-RD-15 Reader Warning For Weak Evidence `P2`

- Actor: reader.
- Goal: avoid over-trusting a weakly attested or lexicographer-only entry.
- Atlas response: show visible warnings for `lexicographer-only`, low-confidence alignment, or unknown period.
- Evidence: lexicographer-only classifier, review reports.

## Lexicographic Research Use Cases

These use cases serve Sanskrit lexicographers and dictionary historians.

### UC-LX-01 MW Article Anatomy `P0`

- Actor: lexicographer.
- Goal: quantify how MW is structured.
- Atlas response: article-type treemap, counts, examples, overlap tables.
- Evidence: MW parser and classifier.

### UC-LX-02 Lexicographer-Only Vocabulary `P0`

- Actor: lexicographer.
- Goal: identify entries whose only citation is `L.` or equivalent.
- Atlas response: list and visualize lexicographer-only records by type, domain, and depth.
- Evidence: `<ls>` extraction and normalized source values.

### UC-LX-03 Root Family Analysis `P1`

- Actor: lexicographer, grammarian.
- Goal: inspect root-centered lexical families.
- Atlas response: root -> derivative -> compound family summaries and source links.
- Evidence: root tags, derivational heuristics, review status.

### UC-LX-04 Compound Productivity `P1`

- Actor: lexicographer.
- Goal: identify productive compound bases and members.
- Atlas response: compound leaderboards, component networks, examples.
- Evidence: compound classifier, k2 markers, e-code patterns.

### UC-LX-05 Derivational Productivity `P1`

- Actor: lexicographer, grammar researcher.
- Goal: measure suffix and derivative patterns.
- Atlas response: derivative counts, suffix candidates, root/base families.
- Evidence: derived article types, headword patterns, inferred morphology.

### UC-LX-06 Citation Density `P1`

- Actor: lexicographer.
- Goal: compare source-rich and source-poor entries.
- Atlas response: citation-count distribution, top cited entries, source-layer summary.
- Evidence: `<ls>` extraction.

### UC-LX-07 Botanical And Technical Domains `P1`

- Actor: domain specialist.
- Goal: inspect botanical, medical, ritual, grammatical, astronomical, or poetic vocabulary.
- Atlas response: domain dashboards by dictionary, source layer, and corpus evidence.
- Evidence: dictionary tags, source-layer map, corpus genre metadata.

### UC-LX-08 Vedic-Accented Layer `P1`

- Actor: Vedic specialist.
- Goal: inspect entries carrying Vedic accent markers.
- Atlas response: Vedic-accented entry explorer with family and source links.
- Evidence: k2 accent marker and source citations.

### UC-LX-09 Sense Inventory Comparison `P2`

- Actor: lexicographer.
- Goal: compare how dictionaries split or merge senses.
- Atlas response: sense-depth comparison with parser confidence.
- Evidence: dictionary parsers, sense segmentation, review queue.

### UC-LX-10 Homonym Split Comparison `P2`

- Actor: lexicographer.
- Goal: see whether dictionaries split one form into multiple entries differently.
- Atlas response: homonym alignment view with conflict status.
- Evidence: record IDs, headword normalization, alignment confidence.

### UC-LX-11 German-English Lexicographic Lineage `P2`

- Actor: dictionary historian.
- Goal: inspect how PWG/PWK evidence relates to MW and later dictionaries.
- Atlas response: lineage visualizations and aligned records.
- Evidence: dictionary coverage, citation overlap, sense depth.

### UC-LX-12 Kosha And Traditional Provenance `P2`

- Actor: lexicographer.
- Goal: detect entries grounded in traditional lexicons or named lexicographic sources.
- Atlas response: source provenance view and evidence class.
- Evidence: source abbreviation map and citation extraction.

### UC-LX-13 Dictionary-Unique Vocabulary `P2`

- Actor: lexicographer.
- Goal: find lemmas present in one dictionary but absent from others.
- Atlas response: unique vocabulary lists by dictionary and domain.
- Evidence: comparative dictionary alignment.

### UC-LX-14 Lexical Evidence Ladder `P2`

- Actor: lexicographer.
- Goal: rank entries by evidence strength.
- Atlas response: evidence ladder from corpus-attested to lexicographer-only.
- Evidence: dictionary citations, corpus occurrences, review status.

### UC-LX-15 Correct A Dictionary Alignment `P2`

- Actor: reviewer.
- Goal: correct a bad machine alignment between dictionaries.
- Atlas response: review form/report with before/after and source links.
- Evidence: low-confidence alignment report.

## Comparative Dictionary Use Cases

These use cases become central after MW Quantitative Depth exists.

### UC-CD-01 Coverage Matrix `P1`

- Actor: researcher.
- Goal: see which dictionaries cover which lemmas.
- Atlas response: dictionary x lemma/type coverage matrix.
- Evidence: parsed dictionary records and normalized headwords.

### UC-CD-02 Pairwise Dictionary Overlap `P1`

- Actor: researcher.
- Goal: compare MW vs AP, MW vs PWG, PWG vs PWK, etc.
- Atlas response: pairwise overlap charts and examples.
- Evidence: dictionary alignment outputs.

### UC-CD-03 All-Dictionary Intersection `P1`

- Actor: lexicographer.
- Goal: find lemmas present in all target dictionaries.
- Atlas response: full-intersection list with source links.
- Evidence: dictionary coverage matrix.

### UC-CD-04 POS Disagreement Review `P1`

- Actor: reviewer, grammarian.
- Goal: find lemmas where dictionaries disagree on part of speech.
- Atlas response: disagreement table with source snippets and confidence.
- Evidence: parsed POS/gender tags.

### UC-CD-05 Gender Disagreement Review `P1`

- Actor: lexicographer, grammarian.
- Goal: find nouns with conflicting gender labels.
- Atlas response: gender conflict table and review queue.
- Evidence: dictionary grammar labels.

### UC-CD-06 Sense Depth Comparison `P2`

- Actor: dictionary historian.
- Goal: compare which dictionary gives the richest sense treatment.
- Atlas response: sense-count and gloss-depth ranking with caveats.
- Evidence: sense segmentation parser and raw snippets.

### UC-CD-07 Citation Apparatus Comparison `P2`

- Actor: lexicographer.
- Goal: compare how dictionaries cite sources.
- Atlas response: citation density and source overlap charts.
- Evidence: citation extraction by dictionary.

### UC-CD-08 Dictionary Recommendation For A Task `P2`

- Actor: user, teacher.
- Goal: choose the right dictionary for translation, philology, grammar, or historical research.
- Atlas response: task-based recommendation backed by coverage and evidence metrics.
- Evidence: dictionary metadata and quantitative summaries.

### UC-CD-09 Alignment Confidence Dashboard `P2`

- Actor: developer, reviewer.
- Goal: inspect high, medium, low, and needs-review alignments.
- Atlas response: confidence distribution and review queue.
- Evidence: alignment algorithm output.

### UC-CD-10 Dictionary Change Across Versions `P3`

- Actor: dictionary historian.
- Goal: compare revisions or edition changes if multiple versions are available.
- Atlas response: added/removed/changed records and examples.
- Evidence: versioned source files.

## Corpus Grammar Use Cases

These use cases start with DCS and later expand through GRETIL, Ambuda, and Sanskrit Library.

### UC-CG-01 Corpus Inventory `P2`

- Actor: corpus linguist.
- Goal: see what texts are available, in which genres and periods.
- Atlas response: corpus manifest, genre coverage, period coverage.
- Evidence: corpus metadata.

### UC-CG-02 Lemma Frequency `P2`

- Actor: corpus linguist.
- Goal: count lemma frequency across texts, genres, and periods.
- Atlas response: frequency tables and charts.
- Evidence: DCS lemma annotations.

### UC-CG-03 POS Distribution By Genre `P2`

- Actor: corpus linguist.
- Goal: compare part-of-speech profiles by genre.
- Atlas response: POS heatmap by genre and period.
- Evidence: corpus morphology tags.

### UC-CG-04 Nominal Inflection Profiles `P2`

- Actor: grammarian.
- Goal: inspect case, number, and gender distributions.
- Atlas response: inflection dashboard by genre and period.
- Evidence: DCS morphology.

### UC-CG-05 Case Function Research `P2`

- Actor: grammarian.
- Goal: study case functions and karaka-linked patterns.
- Atlas response: case distribution and construction examples.
- Evidence: morphology tags and construction heuristics.

### UC-CG-06 Finite Verb Morphology `P2`

- Actor: grammarian.
- Goal: inspect tense, mood, voice, person, number patterns.
- Atlas response: finite verb morphology explorer.
- Evidence: corpus morphology tags.

### UC-CG-07 Participles And Krdanta Forms `P2`

- Actor: grammarian.
- Goal: study participial derivations and their distribution.
- Atlas response: participle dashboard by genre, period, and lemma.
- Evidence: morphology tags and dictionary forms.

### UC-CG-08 Absolutive Chains `P2`

- Actor: syntactician.
- Goal: inspect absolutive usage and chains.
- Atlas response: examples and frequency by genre.
- Evidence: morphology/construction tags.

### UC-CG-09 Compound Density In Corpus `P2`

- Actor: corpus linguist.
- Goal: compare compound density across genres and periods.
- Atlas response: compound density chart and text ranking.
- Evidence: corpus segmentation and dictionary compound evidence.

### UC-CG-10 Vedic Vs Classical Grammar Shift `P2`

- Actor: historical linguist.
- Goal: compare grammar patterns across period layers.
- Atlas response: period-layer dashboards with caveats.
- Evidence: corpus metadata and morphology tags.

### UC-CG-11 Genre-Specific Grammar `P2`

- Actor: Sanskritist.
- Goal: compare kavya, epic, Vedic, sastra, puranic, tantric, and scholastic usage.
- Atlas response: genre dashboards with examples.
- Evidence: corpus metadata and tagged occurrences.

### UC-CG-12 Corpus Examples For A Grammar Chapter `P2`

- Actor: grammar author, teacher.
- Goal: gather examples for a construction.
- Atlas response: ranked examples with source links and metadata.
- Evidence: corpus occurrence data.

### UC-CG-13 Dictionary Claim Vs Corpus Usage `P2`

- Actor: lexicographer, corpus linguist.
- Goal: see whether dictionary claims are supported by corpus usage.
- Atlas response: side-by-side dictionary evidence and corpus attestations.
- Evidence: dictionary alignment and corpus occurrences.

### UC-CG-14 Corpus Orphans `P2`

- Actor: lexicographer.
- Goal: identify corpus lemmas not covered or poorly covered by dictionaries.
- Atlas response: orphan lemma list with frequency and examples.
- Evidence: corpus lemma list and dictionary coverage.

### UC-CG-15 Dictionary-Only Vocabulary `P2`

- Actor: lexicographer.
- Goal: identify dictionary lemmas not found in current corpus data.
- Atlas response: dictionary-only lists with caveats.
- Evidence: dictionary coverage and corpus lemma index.

### UC-CG-16 Sandhi And Segmentation Ambiguity `P3`

- Actor: computational linguist, student.
- Goal: inspect forms with multiple possible segmentations.
- Atlas response: ambiguity dashboard and examples.
- Evidence: corpus tokenizer/segmenter outputs.

### UC-CG-17 Formulaic Or Repeated Expressions `P3`

- Actor: philologist.
- Goal: discover repeated formulae across texts.
- Atlas response: n-gram or phrase recurrence explorer.
- Evidence: corpus text and metadata.

## Diachronic And Source-History Use Cases

These use cases must be conservative. They expose period layers, not exact dates.

### UC-DIA-01 Earliest Source Layer `P1`

- Actor: Sanskritist.
- Goal: see the earliest layer associated with a lemma or family.
- Atlas response: earliest layer with source abbreviation and warning.
- Evidence: dictionary citations and source-layer map.

### UC-DIA-02 Lexical Growth By Period `P2`

- Actor: historical linguist.
- Goal: inspect vocabulary expansion by period layer.
- Atlas response: layer counts, domain timelines, source caveats.
- Evidence: source-layer mapping and corpus metadata.

### UC-DIA-03 Vedic Retention `P2`

- Actor: Vedic/classical specialist.
- Goal: see which Vedic vocabulary continues into later layers.
- Atlas response: Vedic-to-classical continuity dashboard.
- Evidence: source layers and corpus occurrences.

### UC-DIA-04 Vedic-Only Or Early-Layer Vocabulary `P2`

- Actor: historical linguist.
- Goal: find vocabulary limited to early layers in available data.
- Atlas response: Vedic-only candidate list with caveats.
- Evidence: source-layer and corpus metadata.

### UC-DIA-05 Technical Vocabulary Emergence `P2`

- Actor: history of science/sastra researcher.
- Goal: inspect when technical domains become dense.
- Atlas response: domain by period chart.
- Evidence: dictionary domain tags and corpus genre metadata.

### UC-DIA-06 Lexicographic Layer Visibility `P2`

- Actor: lexicographer.
- Goal: isolate late or lexicographic-only evidence.
- Atlas response: lexicographic layer dashboard.
- Evidence: source abbreviation map and `L.` classifiers.

### UC-DIA-07 Source Abbreviation Review `P1`

- Actor: reviewer.
- Goal: improve the mapping from source abbreviations to period layers.
- Atlas response: unknown source list and review form/report.
- Evidence: source abbreviation extraction.

### UC-DIA-08 Diachronic Uncertainty Explanation `P1`

- Actor: reader.
- Goal: understand why the atlas avoids exact dating.
- Atlas response: caveat page and warnings near charts.
- Evidence: period-layer policy.

### UC-DIA-09 Source-Layer Sankey `P2`

- Actor: researcher.
- Goal: see flow from source layer to article type to semantic domain.
- Atlas response: Sankey diagram with examples.
- Evidence: type classifier, source layers, domain tags.

### UC-DIA-10 Compare Dictionary Chronology With Corpus Chronology `P3`

- Actor: historical linguist.
- Goal: compare dictionary citation layers with corpus metadata layers.
- Atlas response: mismatch and agreement dashboard.
- Evidence: dictionary source layers and corpus metadata.

## Evidence Dossier Use Cases

These use cases become possible after MW, dictionary comparison, and corpus outputs exist.

### UC-ED-01 Lemma Evidence Dossier `P2`

- Actor: Sanskritist.
- Goal: see all evidence for a lemma in one place.
- Atlas response: dictionary entries, corpus occurrences, source layers, family relations, review status.
- Evidence: LexemeHub or equivalent alignment layer.

### UC-ED-02 Lexical Family Dossier `P2`

- Actor: lexicographer.
- Goal: inspect a whole family rather than one lemma.
- Atlas response: family graph, member list, deepest branches, source links.
- Evidence: MW depth and dictionary comparison outputs.

### UC-ED-03 Construction Dossier `P3`

- Actor: grammarian.
- Goal: inspect a grammatical construction across corpus and dictionaries.
- Atlas response: definition, examples, frequency, source layers, related lexical entries.
- Evidence: corpus construction tags and grammar metadata.

### UC-ED-04 Domain Dossier `P3`

- Actor: domain specialist.
- Goal: inspect a domain such as botany, ritual, grammar, medicine, astronomy, or poetics.
- Atlas response: domain vocabulary, corpus usage, source layers, dictionary coverage.
- Evidence: domain tags, corpus genres, source layers.

### UC-ED-05 Source Dossier `P3`

- Actor: philologist.
- Goal: inspect all dictionary and corpus evidence tied to one source.
- Atlas response: source metadata, cited lemmas, corpus passages, period-layer notes.
- Evidence: source map and corpus metadata.

## Review And Quality-Control Use Cases

Review is not optional. It is how machine-derived data becomes reliable scholarship.

### UC-RV-01 Low-Confidence Alignment Queue `P1`

- Actor: reviewer.
- Goal: review dictionary alignments marked low confidence.
- Atlas response: queue with source snippets and suggested action.
- Evidence: alignment confidence output.

### UC-RV-02 POS/Gender Conflict Queue `P1`

- Actor: reviewer.
- Goal: inspect grammar conflicts across dictionaries.
- Atlas response: conflict table and review status.
- Evidence: parsed grammar labels.

### UC-RV-03 Source-Layer Unknown Queue `P1`

- Actor: reviewer.
- Goal: classify source abbreviations currently marked unknown.
- Atlas response: unknown source table with examples.
- Evidence: extracted `<ls>` values.

### UC-RV-04 Corpus Lemma Mismatch Queue `P2`

- Actor: reviewer.
- Goal: inspect corpus lemmas that fail to align with dictionaries.
- Atlas response: mismatch list with examples.
- Evidence: corpus lemma and dictionary normalization.

### UC-RV-05 Encoding/OCR Problem Queue `P2`

- Actor: maintainer.
- Goal: detect suspicious mojibake, broken markup, or OCR artifacts.
- Atlas response: source-quality warning list.
- Evidence: parser warnings.

### UC-RV-06 Review A Generated TEI Entry `P1`

- Actor: TEI reviewer.
- Goal: inspect whether generated TEI preserves source evidence.
- Atlas response: TEI file link, validation status, loss report.
- Evidence: TEI output and validation report.

### UC-RV-07 Review An OntoLex/RDF Graph `P1`

- Actor: semantic web reviewer.
- Goal: inspect whether OntoLex/FrAC graph captures entry evidence.
- Atlas response: JSON-LD, Turtle, SHACL-style report, loss report.
- Evidence: graph output and validation report.

### UC-RV-08 Record A Human Correction `P2`

- Actor: reviewer.
- Goal: save a correction without editing generated source directly.
- Atlas response: review JSON report with corrected value and provenance.
- Evidence: review report schema.

### UC-RV-09 Track Reviewed Vs Machine Status `P2`

- Actor: project maintainer.
- Goal: know which claims are machine-only and which are reviewed.
- Atlas response: review coverage dashboard.
- Evidence: review report statuses.

## Developer And Maintainer Use Cases

These use cases help contributors choose the next engineering task.

### UC-DEV-01 Rebuild Pilot Data `P0`

- Actor: developer.
- Goal: regenerate the pilot dataset deterministically.
- Atlas response: documented command pipeline.
- Evidence: `npm run build-pilot` and generated reports.

### UC-DEV-02 Validate Local Profiles `P0`

- Actor: developer.
- Goal: check TEI/OntoLex profile validation.
- Atlas response: validation scripts and reports.
- Evidence: `validate-tei-profile`, `validate-ontolex-profile`.

### UC-DEV-03 External Validator Availability `P1`

- Actor: developer.
- Goal: know whether external TEI/SHACL tools are installed.
- Atlas response: external validation report with passed/skipped status.
- Evidence: `validate-external-profiles`.

### UC-DEV-04 Add A New Dictionary Parser `P2`

- Actor: developer.
- Goal: add another CDSL dictionary.
- Atlas response: parser contract, dictionary manifest, coverage output.
- Evidence: dictionary source file and parser validation.

### UC-DEV-05 Improve MW Parser `P1`

- Actor: developer.
- Goal: handle more MW markup without breaking outputs.
- Atlas response: parser tests, validation report, example diffs.
- Evidence: MW source records and generated summaries.

### UC-DEV-06 Add DCS Corpus Ingestion `P2`

- Actor: developer.
- Goal: ingest DCS exports once local schema is known.
- Atlas response: corpus manifest, parser, validation report.
- Evidence: DCS files and metadata.

### UC-DEV-07 Add GRETIL Inventory `P3`

- Actor: developer.
- Goal: add broad text inventory and raw counts.
- Atlas response: GRETIL manifest and metadata warnings.
- Evidence: GRETIL files.

### UC-DEV-08 Add A New Visualization `P1`

- Actor: developer.
- Goal: create a new Observable page from generated data.
- Atlas response: page template, data contract, build verification.
- Evidence: generated JSON and `npm run build`.

### UC-DEV-09 Diagnose Build Failure `P0`

- Actor: maintainer.
- Goal: find which generated data or page broke Observable build.
- Atlas response: clear validation output and page load logs.
- Evidence: build output and validation reports.

### UC-DEV-10 Schema Version Migration `P2`

- Actor: maintainer.
- Goal: update generated JSON schemas safely.
- Atlas response: schemaVersion fields and migration notes.
- Evidence: data contracts and validation reports.

### UC-DEV-11 Data Size Control `P1`

- Actor: developer.
- Goal: prevent huge source data from entering `src/data`.
- Atlas response: compact output policy and validation warning.
- Evidence: file size checks and source path policy.

### UC-DEV-12 Source Path Discovery `P1`

- Actor: developer.
- Goal: find local dictionaries and corpora without hard-coding too much.
- Atlas response: manifest and warning when a path is missing.
- Evidence: filesystem checks.

### UC-DEV-13 Add CI Checks `P2`

- Actor: maintainer.
- Goal: run build and validation in GitHub Actions.
- Atlas response: workflow with deterministic commands.
- Evidence: CI logs.

### UC-DEV-14 Debug A Metric From A Source Link `P1`

- Actor: developer.
- Goal: trace an odd chart count back to source records.
- Atlas response: examples with source links in every summary.
- Evidence: source line hrefs.

### UC-DEV-15 Prepare A Handoff For Another Agent `P1`

- Actor: project lead.
- Goal: give Gemini or another assistant a bounded implementation task.
- Atlas response: detailed handoff with phase, files, commands, and acceptance criteria.
- Evidence: docs and current validation status.

## Standards And Interoperability Use Cases

These use cases support TEI, OntoLex, Lexicog, FrAC, RDF, and data-model research.

### UC-ST-01 TEI Archival Preservation `P1`

- Actor: TEI researcher.
- Goal: preserve dictionary-as-edition structure.
- Atlas response: TEI files, ODD/profile, validation report.
- Evidence: generated TEI and source snippets.

### UC-ST-02 OntoLex Semantic Modeling `P1`

- Actor: semantic web researcher.
- Goal: represent lexical entries, senses, citations, and relations.
- Atlas response: JSON-LD and Turtle outputs.
- Evidence: OntoLex/FrAC graph files.

### UC-ST-03 Loss Report Inspection `P1`

- Actor: standards researcher.
- Goal: see what TEI/OntoLex cannot represent cleanly.
- Atlas response: machine-generated and reviewed loss reports.
- Evidence: loss report JSON.

### UC-ST-04 RDF Reuse `P2`

- Actor: data engineer.
- Goal: reuse generated RDF/Turtle outside the atlas.
- Atlas response: downloadable Turtle files and namespace policy.
- Evidence: RDF files and validation report.

### UC-ST-05 FrAC Evidence Modeling `P2`

- Actor: evidence/provenance researcher.
- Goal: model source citations and attestations explicitly.
- Atlas response: FrAC-style evidence nodes.
- Evidence: OntoLex/FrAC outputs.

### UC-ST-06 Compare TEI And OntoLex Suitability `P2`

- Actor: digital lexicography researcher.
- Goal: compare archival and semantic models on Sanskrit dictionary data.
- Atlas response: synchronized views and loss reports.
- Evidence: generated TEI, RDF, and neutral model.

### UC-ST-07 Export Neutral JSON `P1`

- Actor: developer, researcher.
- Goal: use a simpler model before TEI/RDF.
- Atlas response: neutral-model JSON and schema.
- Evidence: generated neutral model.

## NLP And Computational Linguistics Use Cases

These use cases support downstream computational work without making the atlas an NLP product.

### UC-NLP-01 Lemma Lexicon Export `P2`

- Actor: NLP developer.
- Goal: export normalized Sanskrit lemma lists with dictionary coverage.
- Atlas response: compact lexeme list with source dictionaries.
- Evidence: dictionary alignment.

### UC-NLP-02 POS/Gender Lexicon Export `P2`

- Actor: NLP developer.
- Goal: use dictionary grammar labels as features.
- Atlas response: POS/gender summary with conflicts and confidence.
- Evidence: dictionary labels and review status.

### UC-NLP-03 Morphology Benchmark Seeds `P2`

- Actor: computational linguist.
- Goal: create benchmark seeds from dictionary and corpus evidence.
- Atlas response: reviewed examples and morphology tags.
- Evidence: DCS tags and dictionary grammar labels.

### UC-NLP-04 Compound Segmentation Support `P2`

- Actor: NLP developer.
- Goal: use compound family data to improve segmentation.
- Atlas response: compound candidates with confidence.
- Evidence: MW compound classifier and corpus segmentation.

### UC-NLP-05 Sandhi Ambiguity Data `P3`

- Actor: NLP developer.
- Goal: collect hard examples for sandhi and segmentation.
- Atlas response: ambiguity queue and examples.
- Evidence: corpus segmenter output.

### UC-NLP-06 Domain Vocabulary Lists `P2`

- Actor: NLP developer, domain researcher.
- Goal: build lists for botany, medicine, ritual, grammar, astronomy, etc.
- Atlas response: domain vocabulary exports with evidence levels.
- Evidence: dictionary tags and corpus genre metadata.

### UC-NLP-07 Dictionary-Corpus Gap Dataset `P2`

- Actor: NLP researcher.
- Goal: study what dictionaries cover or miss relative to corpora.
- Atlas response: corpus orphan and dictionary-only lists.
- Evidence: dictionary alignment and corpus lemma index.

### UC-NLP-08 Translation Support Data `P3`

- Actor: MT researcher.
- Goal: use dictionary glosses and corpus examples for translation experiments.
- Atlas response: cautious export of gloss snippets and source links.
- Evidence: dictionary senses and corpus examples.

## Teaching And Student Use Cases

These use cases make the atlas useful beyond specialist research.

### UC-TEACH-01 Explain Dictionary Differences `P1`

- Actor: teacher.
- Goal: show students why MW, AP, PWG, and others differ.
- Atlas response: side-by-side examples and dictionary guide.
- Evidence: dictionary metadata and aligned entries.

### UC-TEACH-02 Teach Compounds `P1`

- Actor: teacher.
- Goal: teach compound density and dictionary structure.
- Atlas response: compound examples, treemap, family graph.
- Evidence: MW type classifier.

### UC-TEACH-03 Teach Evidence Strength `P1`

- Actor: teacher.
- Goal: explain why not all dictionary entries are equally supported.
- Atlas response: observed/derived/inferred/reviewed examples.
- Evidence: evidence-label policy.

### UC-TEACH-04 Build A Grammar Lesson From Corpus Examples `P2`

- Actor: teacher.
- Goal: collect examples for cases, participles, absolutives, or compounds.
- Atlas response: filtered examples with source references.
- Evidence: DCS/GRETIL corpus data.

### UC-TEACH-05 Russian Student Glossary `P1`

- Actor: Russian-reading student.
- Goal: understand English/German/Sanskrit technical terms.
- Atlas response: bilingual glossary with traditional terms.
- Evidence: terminology policy and locale files.

### UC-TEACH-06 Assignment Dataset `P2`

- Actor: teacher.
- Goal: assign students review tasks or data interpretation tasks.
- Atlas response: curated review queues and exportable examples.
- Evidence: review reports.

## Publication And Scholarly Communication Use Cases

These use cases help turn the atlas into publishable research.

### UC-PUB-01 Cite A Quantitative Finding `P1`

- Actor: researcher.
- Goal: cite a chart or table in an article.
- Atlas response: stable chart/page link, generation date, source paths, assumptions.
- Evidence: generated metadata.

### UC-PUB-02 Reproduce A Chart `P1`

- Actor: reviewer.
- Goal: reproduce the data behind a visualization.
- Atlas response: data file path, build script, validation report.
- Evidence: generated JSON and script.

### UC-PUB-03 Export A Table `P2`

- Actor: researcher.
- Goal: use a table in an article or appendix.
- Atlas response: downloadable compact JSON/CSV where appropriate.
- Evidence: generated summaries.

### UC-PUB-04 Peer Review Appendix `P2`

- Actor: author.
- Goal: provide method notes and validation reports for peer review.
- Atlas response: docs, reports, source links, and caveats.
- Evidence: documentation and validation outputs.

### UC-PUB-05 Paper Argument Support `P1`

- Actor: author.
- Goal: support claims about Sanskrit lexicographic interoperability.
- Atlas response: loss reports, TEI/OntoLex outputs, hard-case examples.
- Evidence: pilot data and validation reports.

### UC-PUB-06 Release Notes And Data Versioning `P2`

- Actor: maintainer.
- Goal: document what changed between atlas releases.
- Atlas response: changelog, schema version, generatedAt fields.
- Evidence: git history and generated metadata.

## Access, Licensing, And Reuse Use Cases

These use cases keep the project safe and usable.

### UC-ACCESS-01 Static Public Site `P0`

- Actor: public user.
- Goal: use the atlas without installing tools.
- Atlas response: GitHub Pages or static Observable site.
- Evidence: built site.

### UC-ACCESS-02 Local Reproducibility `P0`

- Actor: developer.
- Goal: reproduce outputs locally.
- Atlas response: documented commands and source path requirements.
- Evidence: scripts and validation reports.

### UC-ACCESS-03 Raw Data Boundary `P0`

- Actor: maintainer.
- Goal: avoid committing full raw dictionaries or corpora.
- Atlas response: source path policy and compact generated outputs.
- Evidence: repo layout and validation.

### UC-ACCESS-04 License-Aware Corpus Expansion `P2`

- Actor: maintainer.
- Goal: add Ambuda or Sanskrit Library data safely.
- Atlas response: license/access notes and derived-data policy.
- Evidence: corpus manifest.

### UC-ACCESS-05 Offline Scholar Workflow `P3`

- Actor: researcher.
- Goal: use generated data locally without the public site.
- Atlas response: documented JSON files and scripts.
- Evidence: data contracts.

### UC-ACCESS-06 Stable IDs `P1`

- Actor: developer, researcher.
- Goal: refer to entries, cases, lemmas, and reviews across releases.
- Atlas response: stable IDs and version notes.
- Evidence: ID policy.

## Visualization Use Cases

These use cases describe visual forms and the questions they answer.

### UC-VIZ-01 Treemap `P0`

- Question: what large categories make up a dictionary?
- Data: article type counts.
- Example: MW typology treemap.

### UC-VIZ-02 Matrix `P1`

- Question: which dictionaries cover which lemmas or features?
- Data: dictionary x lemma/type matrix.

### UC-VIZ-03 UpSet Or Overlap Chart `P2`

- Question: which dictionary combinations share vocabulary?
- Data: dictionary coverage sets.

### UC-VIZ-04 Sankey `P2`

- Question: how do source layers flow into types and domains?
- Data: source layer, article type, domain tags.

### UC-VIZ-05 Network Graph `P2`

- Question: how are roots, derivatives, compounds, and lemmas related?
- Data: lexical family graph.

### UC-VIZ-06 Heatmap `P2`

- Question: where are grammar features concentrated?
- Data: POS/case/construction by genre and period.

### UC-VIZ-07 Timeline `P2`

- Question: how do layers or domains change over time?
- Data: period-layer summaries.

### UC-VIZ-08 Review Queue Table `P1`

- Question: what should humans review next?
- Data: low-confidence or conflicting machine outputs.

### UC-VIZ-09 Evidence Dossier `P2`

- Question: what evidence supports one lemma, family, construction, domain, or source?
- Data: cross-track evidence summary.

### UC-VIZ-10 Validation Dashboard `P1`

- Question: is generated data trustworthy enough to publish?
- Data: validation reports, warnings, skipped checks.

## Anti-Use Cases And Non-Goals

These are tempting, but should not be treated as goals in early phases.

### AUC-01 Exact Dating From Dictionary Citations

The atlas should not claim exact word dates from dictionary source abbreviations. It may provide conservative period layers with warnings.

### AUC-02 Runtime LLM Classification

The atlas should not depend on Gemini, OpenAI, or another LLM for runtime classification. LLMs may help write code or documentation, but generated claims must be deterministic or reviewed.

### AUC-03 Full Paninian Derivation Engine

The atlas should not attempt full Paninian derivation before the evidence model, dictionary comparison, and corpus ingestion are stable.

### AUC-04 Replacing Philological Judgment

Review queues support experts. They do not replace expert judgment.

### AUC-05 Hiding Weak Evidence

Inferred families, uncertain period layers, low-confidence alignments, and dictionary-only claims must be visibly marked.

### AUC-06 Committing Full Raw Sources

Full dictionary and corpus source files should remain outside the repository unless a future license and storage decision explicitly allows it.

### AUC-07 Building A Backend Too Early

The current architecture is static-first. A backend should only be considered after static generated data is proven insufficient.

### AUC-08 One Giant Universal Model First

Do not build `LexemeHub` as a giant abstraction before MW depth, dictionary comparison, and corpus evidence produce real constraints.

### AUC-09 Treating German Evidence As Secondary

PWG/PWK and German lexicographic traditions must be preserved as scholarly evidence, not flattened into English-only summaries.

### AUC-10 Treating Search As The Whole Product

Lookup is important, but the atlas is also for comparison, evidence review, grammar research, and data reuse.

## Phase Mapping

| Phase | Use cases unlocked |
|---|---|
| Phase 0: documentation | reader/developer critique, use-case map, architecture, handoffs |
| Phase 1: MW Quantitative Depth | UC-RD-12, UC-LX-01, UC-LX-02, UC-LX-03, UC-LX-04, UC-DIA-01, UC-VIZ-01 |
| Phase 2: Comparative Dictionary Lab | UC-RD-03, UC-CD-01 through UC-CD-09, UC-LX-09 through UC-LX-15 |
| Phase 3: DCS Corpus Grammar | UC-CG-01 through UC-CG-15, UC-RD-14, UC-CG-13 |
| Phase 4: GRETIL Expansion | broader corpus inventory, raw token coverage, genre/period expansion |
| Phase 5: Ambuda/Sanskrit Library | additional corpus evidence, licensing-aware expansion |
| Cross-track dossiers | UC-ED-01 through UC-ED-05 |

## First Product Milestones

### Milestone A: Reader Can Start

- dictionary user guide;
- basic dictionary lookup path;
- dictionary comparison guide;
- evidence labels explained;
- source links visible.

### Milestone B: Developer Can Contribute

- one clear phase handoff;
- build and validation commands;
- generated reports;
- source path policy;
- review queue policy.

### Milestone C: Researcher Can Trust A Chart

- generated metadata;
- source links;
- assumptions and warnings;
- validation report;
- reproducible command.

### Milestone D: Reviewer Can Improve Data

- low-confidence queue;
- source snippets;
- review JSON schema;
- reviewed/corrected status;
- visible effect on downstream outputs.

## Shortlist For Immediate Documentation Follow-Up

The following docs should be created before the atlas becomes reader-facing:

- `docs/DICTIONARY_USER_GUIDE.md`
- `docs/EVIDENCE_LABELS.md`
- `docs/REVIEW_REPORTS.md`
- `docs/DICTIONARY_COMPARISON_PLAN.md`
- `docs/DCS_CORPUS_INGESTION_PLAN.md`

These are not implementation blockers for MW Quantitative Depth, but they are important for turning the atlas from an expert workbench into a usable public research tool.
