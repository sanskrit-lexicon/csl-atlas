# Interoperability Model

This is the neutral layer between CDSL source data, TEI archival XML, and OntoLex semantic graph output.

## Why A Neutral Model

Direct CDSL-to-TEI and CDSL-to-OntoLex conversions would confuse two different tasks:

- preserving the dictionary as an edited historical text;
- representing lexicographic meaning as a graph.

The neutral model keeps the scholarly interpretation visible. TEI and OntoLex exports are views over that interpretation.

## Core JSON Shape

```json
{
  "id": "mw-pwg-pwk:aMSa",
  "key": "aMSa",
  "phenomena": ["hedge", "root", "compound", "continuation"],
  "records": {
    "mw": {},
    "pwg": {},
    "pwk": {}
  },
  "forms": [],
  "senses": [],
  "citations": [],
  "relations": [],
  "loss": []
}
```

## Core Entities

| Entity | Meaning | Notes |
|---|---|---|
| `dictionaryRecord` | One CDSL `<L>...<LEND>` record | Keeps source identity and line pointer |
| `form` | Headword, variant, inflected form, compound member | May come from `<k1>`, `<k2>`, `<s>`, or inferred segmentation |
| `sense` | Lexicographic meaning unit | May be explicit, compressed, or inferred |
| `citation` | Reference to source/evidence | Includes source label, coordinates, and evidence class |
| `relation` | Directed relation among forms, senses, entries, or sources | Used for derivation, compound decomposition, continuation, cross-reference |
| `loss` | Model adequacy note | Records semantic pressure or conversion failure |

## Evidence Classes

| Class | Definition | Example |
|---|---|---|
| `textual-source` | Named literary or scholastic source | `RV.`, `MBh.`, `Pāṇ.` |
| `coordinate-source` | Source plus book/chapter/verse/page coordinate | `RV. v, 86, 5` |
| `named-kosha` | Named indigenous lexicon or lexicographer source | PWG `AK.`, `H.`, `MED.` |
| `generic-lexicographer` | Generic lexicographer-only hedge | MW `<ls>L.</ls>` |
| `editorial-reference` | Dictionary/editorial self-reference | `W.`, `MW.`, `ib.` |
| `catalogue-reference` | Catalogue/bibliographic evidence | `Cat.` |
| `ambiguous-source` | Source label unresolved or mixed | malformed or context-dependent `<ls>` |

## TEI Mapping

TEI is the archival model. It should preserve printed/digitized structure.

| Neutral Model | TEI Target | Notes |
|---|---|---|
| dictionaryRecord | `<entry>` or `<entryFree>` | Use `<entry>` where structure is clear; `<entryFree>` for difficult records |
| form | `<form>`, `<orth>` | `@type` distinguishes lemma, display, variant, inflected, compound-member |
| grammar | `<gramGrp>`, `<gram>` | Normalize only when confidence is high |
| sense | `<sense>` | Preserve implicit and inferred status with `@cert` or `@type` |
| citation | `<cit>`, `<ref>`, `<bibl>` | `L.` may require custom `@type="generic-lexicographer"` |
| compound relation | `<re>` plus decomposition annotation | TEI archival and semantic decomposition may diverge |
| continuation | `<entry type="continuation">` with pointer to parent | Adjacency must be made explicit |
| loss report | `<note type="model-loss">` | For reviewed samples only |

## OntoLex Mapping

OntoLex is the semantic/web model. It should expose reusable graph relations.

| Neutral Model | OntoLex Target | Notes |
|---|---|---|
| dictionaryRecord | `lexicog:Entry` | Entry as lexicographic object |
| form | `ontolex:Form` | Written representation from SLP1/IAST/Devanagari as separate reps |
| lexical item | `ontolex:LexicalEntry` | May be one per lemma or per homograph |
| sense | `ontolex:LexicalSense` | Links to definition and evidence |
| citation | `frac:Attestation` or related evidence node | FrAC is the best fit for source/evidence |
| compound decomposition | `decomp:Component` | Better semantic fit than TEI |
| variant/translation relation | `vartrans:` relation where appropriate | Use sparingly |
| root relation | custom Sanskrit extension until OntoLex-Morph fit is settled | Must not hide ambiguity |

## Stress Points

### `L.` Hedge

TEI can archive it as a citation-like string. OntoLex needs an evidence/provenance node. Neither should treat it as a normal textual citation.

### Named Kosha Evidence

PWG names specific lexicographic sources. MW often collapses that class into `L.`. The atlas should model this as transformation, not just difference.

### Roots

Roots are simultaneously headwords, derivational bases, grammatical carriers, and sometimes lexicographer-only constructs. They need multiple relation types.

### Compounds

Compounds are printed as subentries but semantically as decomposable lexical constructions. TEI and OntoLex should intentionally diverge here.

### Continuations

Continuation entries suppress the headword and depend on adjacency. The neutral model must reconstruct the parent relation before either TEI or OntoLex can represent the entry adequately.

## Model Adequacy Scale

| Status | Meaning |
|---|---|
| `clean` | TEI/OntoLex mapping preserves the intended meaning |
| `partial` | Meaning is mostly preserved but requires conventions |
| `lossy` | Important meaning is flattened or only preserved in a note |
| `failure` | Target model lacks a plausible representation without extension |

The public atlas should show this status per case and per target model.
