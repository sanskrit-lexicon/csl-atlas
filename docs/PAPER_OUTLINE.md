# Paper Outline

Working title:

**Sanskrit Lexicography Between TEI and OntoLex: Evidence, Derivation, and Compression in MW, PWG, and PWK**

## Abstract Draft

This paper uses three related CDSL Sanskrit dictionaries, Monier-Williams 1899 (MW), the large Petersburg dictionary (PWG), and the shorter Petersburg dictionary (PWK), as a stress test for lexicographic interoperability. Rather than converting dictionary XML mechanically, it asks whether the lexicographic meaning of these works can be preserved across two complementary models: TEI as an archival representation of dictionary text and OntoLex as a semantic graph representation of lexical knowledge. The test sample is deliberately composed of difficult cases: MW's generic lexicographer-only hedge `L.`, PWG's named kosha citations, verbal roots, compounds, continuation entries, and citation-compression patterns between PWG and PWK. The paper argues that Sanskrit lexicography exposes a class of evidential and derivational structures that are only partially captured by current dictionary standards. The accompanying public atlas publishes the raw CDSL snippets, a neutral JSON model, TEI/OntoLex views, and explicit loss reports for each case.

## Argument

The main argument is not that TEI or OntoLex fails. It is that they succeed differently:

- TEI is strong for preserving the dictionary as an edition.
- OntoLex is strong for exposing reusable semantic relations.
- Sanskrit lexicography needs an explicit evidence/provenance layer between them.

## Section Plan

### 1. Introduction

- Historical Sanskrit dictionaries as dense, compressed knowledge systems.
- Why MW/PWG/PWK are a good test group.
- Why interoperability must preserve lexicographic meaning, not just tags.

### 2. Data And Prior Work

- CDSL source data.
- MW microanalysis as immediate background.
- TEI dictionary encoding.
- OntoLex-Lexicog and FrAC.
- Previous MW/PWG/PWK lineage findings: PWG named apparatus, MW `L.`, PWK compression.

### 3. Method

- Automatic hard-case sampling.
- Neutral model.
- TEI archival mapping.
- OntoLex semantic mapping.
- Loss-report method.

### 4. Evidence And Provenance

Core cases:

- MW `L.` hedge.
- PWG named kosha citation.
- PWK retained/dropped source evidence.

Claim:

> The evidence class is not a decorative citation layer; it is part of lexical meaning in Sanskrit lexicography.

### 5. Roots And Derivation

Core cases:

- MW roots marked with `<info verb="genuineroot"/>`.
- PWG/PWK counterparts with different citation density.
- Root as lexical entry versus derivational infrastructure.

Claim:

> A Sanskrit root cannot be modeled only as a lexical entry without losing its grammatical and derivational function.

### 6. Compounds And Continuations

Core cases:

- MW `<e>3*` compound subentries.
- `k2` compound segmentation.
- `<e>1A` continuation entries.

Claim:

> TEI should preserve subentry/adjacency structure; OntoLex should expose decomposition and parent relations. A single flat entry model loses both.

### 7. PWG To PWK To MW Transformations

- PWK as abridgement and reinterpretation.
- MW as English recomposition and evidential simplification.
- Compression is semantically meaningful.

### 8. Standards Critique

- What maps cleanly.
- What maps partially.
- What becomes lossy.
- Proposed Sanskrit lexicographic extension layer:
  - evidence class;
  - root relation type;
  - compound decomposition status;
  - continuation parent status;
  - source-collapse relation.

### 9. The Atlas

- Public site.
- Generated sample.
- Reproducibility.
- Bilingual interface.
- Future full-dictionary scaling.

### 10. Conclusion

Sanskrit dictionaries are not edge cases to be normalized away. They reveal where dictionary interoperability needs finer concepts of evidence, derivation, and editorial compression.

## Figures

1. Three-view architecture: CDSL -> neutral model -> TEI/OntoLex.
2. Evidence-class comparison: PWG named kosha citations vs MW `L.`.
3. Root modeling diagram.
4. Compound archival/semantic split.
5. Loss-report distribution across pilot cases.

## Minimum Submission Dataset

- 50 generated hard cases.
- 15 manually reviewed mappings.
- 5 fully discussed paper cases.
- Public archive of JSON, TEI, and OntoLex outputs.
