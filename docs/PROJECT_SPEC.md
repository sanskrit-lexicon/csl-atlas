# MW-PWG-PWK Interoperability Atlas

Date: 2026-05-28

## Mission

Build a public, bilingual research atlas that compares the lexicographic meaning encoded in three related Sanskrit dictionaries:

- MW: Monier-Williams, *A Sanskrit-English Dictionary* (1899).
- PWG: Boehtlingk and Roth, *Sanskrit-Woerterbuch* (large Petersburg dictionary).
- PWK: Boehtlingk, *Sanskrit-Woerterbuch in kuerzerer Fassung* (shorter Petersburg dictionary).

The atlas will become both a digital research tool and the empirical base for a paper on Sanskrit lexicographic interoperability.

## Core Claim To Test

TEI and OntoLex can represent much of the dictionary structure, but Sanskrit lexicography stresses both models in specific places: evidential hedges, named kosha provenance, root-based derivation, compound decomposition, compressed citations, and adjacency-based continuations.

The project should not merely ask whether CDSL data can be converted. It should ask what is lost, what must be extended, and what Sanskrit lexicography teaches general dictionary models.

## Scope

### In Scope

- MW, PWG, and PWK only for the first phase.
- Difficult entries selected automatically from hard-case signatures.
- TEI as archival encoding.
- OntoLex/Lexicog/FrAC as semantic web representation.
- Optional external validation harness for TEI ODD/RELAX NG and SHACL-engine checks.
- Bilingual English/Russian public interface from the beginning.
- Static public site first; deeper interactive graph tooling later.
- All-dictionary coverage inventory as the bridge from the MW/PWG/PWK pilot to a broader CDSL atlas.

### Out Of Scope For The First 3 Months

- Full-dictionary conversion.
- Manual selection as the primary sampling method.
- Production RDF endpoint.
- Exhaustive TEI customization.
- Corpus attestation verification beyond dictionary-internal citations.
- Full philological typology for every CDSL dictionary; the first pass is heuristic coverage and size measurement.

## Standards Roles

| Standard | Project Role | What It Should Preserve |
|---|---|---|
| TEI Dictionaries | Archival/textual model | Entry order, headword form, hierarchy, source wording, editorial compression, citations as printed |
| OntoLex-Lexicog | Semantic dictionary model | Lexical entries, components, senses, subcomponents |
| OntoLex-FrAC | Evidence and attestation model | Citation/provenance relations, source pointers, evidence classes |
| ISO LMF | Background reference | Interchange vocabulary and model comparison, not the v0.1 implementation target |

## Research Questions

1. Which MW/PWG/PWK structures map cleanly to TEI?
2. Which structures map more naturally to OntoLex than to TEI?
3. Is MW's `L.` best modeled as citation, provenance, usage/register, or a separate evidential class?
4. How does PWK transform PWG's citation apparatus and sense structure?
5. Can compound entries be represented at once as archival subentries and semantic decomposition graphs?
6. Are roots lexical entries, derivational nodes, grammatical infrastructure, or all three?
7. What minimum Sanskrit-specific extension layer is needed above TEI/OntoLex?
8. Which CDSL dictionaries fit the MW-derived block scheme fully, partially, or only as prose/genre-bound boundary cases?

## Digital Tool

The public atlas should present each selected lemma with five synchronized views:

1. **Raw CDSL**: original record snippets from MW, PWG, and PWK.
2. **Normalized Model**: neutral JSON representation of forms, senses, citations, and relations.
3. **TEI View**: archival XML preserving the dictionary-as-edition.
4. **OntoLex View**: RDF/JSON-LD graph showing semantic relations.
5. **Loss Report**: explicit notes on what the target model cannot express cleanly.

## Paper Shape

Working title:

> Sanskrit Lexicography Between TEI and OntoLex: Evidence, Derivation, and Compression in MW, PWG, and PWK

Paper sections:

1. Problem: why Sanskrit dictionaries are a hard interoperability case.
2. Data: CDSL MW/PWG/PWK and the hard-case sampling method.
3. Method: neutral model, TEI mapping, OntoLex mapping, loss reports.
4. Findings: evidential hedges, kosha provenance, roots, compounds, continuation entries.
5. Standards critique: what TEI captures well, what OntoLex captures well, and where both need extension.
6. Tool: atlas design and reproducible public dataset.
7. Conclusion: Sanskrit lexicography as a stress test for digital dictionary models.

## Success Criteria

By the end of month 3:

- 50 automatically sampled hard cases are public.
- All available CDSL v02 dictionaries with main source files have a reproducible coverage and size inventory.
- Each case has MW/PWG/PWK raw snippets where available.
- Each case has a normalized JSON record.
- All 50 cases have strict, reproducible TEI archival-profile mappings and machine-review reports.
- All 50 cases have OntoLex/FrAC JSON-LD, RDF/Turtle mirrors, and machine-review reports.
- The project includes a TEI ODD/profile file and an OntoLex/FrAC SHACL/profile file for reproducible validation.
- The project records optional external validator status for TEI ODD/RELAX NG and SHACL engines separately from the canonical local profile validators.
- The atlas exposes loss reports, not just successful mappings.
- A paper abstract and detailed outline exist in the repo.
- English and Russian labels are both present in the public interface.

## Working Principle

The atlas must make failure productive. A lossy conversion is not a bug in the research; it is a finding.
