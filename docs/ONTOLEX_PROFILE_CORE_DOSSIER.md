_Created: 19-10-2026 · Last updated: 19-10-2026_

# OntoLex-Lemon application profile — csl-atlas core dossier

Status: **release candidate** for dataset `csl-atlas-core-dossier` v1.0.0,
shipped with repo release `v0.20.0`.

This is an **application profile**, not an exporter and not a new ontology. The
normative RDF serialization remains in
[`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards); this
document states exactly what that exporter may read from this dataset and what
it must not invent.

## 1. Dataset scope

| Item | Value |
|---|---|
| Dataset | `src/data/dicts/core-dossier/` |
| Records | 28,524 lemmas attested in at least 5 of 7 target dictionaries |
| Frozen data revision | [`12bd3d1`](https://github.com/sanskrit-lexicon/csl-atlas/commit/12bd3d1c7e698d9c508267ceac4ac2b834db1f88) (2026-09-24) |
| csl-orig revision | `f4c08c578b330e2379e38f54d3a541f1564b8eee` |
| Builder | `npm run build-dict-comparison` (`scripts/build-dictionary-comparison.mjs`) |
| Provenance sidecar | [`src/data/dicts/core-dossier/.source.json`](../src/data/dicts/core-dossier/.source.json) |
| Licence | CC BY-SA 4.0, inherited from `csl-orig` |

The dataset is a **coverage dossier**: it records which of seven dictionaries
attest a normalized headword, how many dictionary records each dictionary has
for that headword, the first source line of the block, and a compact grammar
token. It does **not** carry definitions, senses, examples, etymology, or
citation links. The profile is therefore deliberately narrower than a full
OntoLex lexicon.

Target model: the OntoLex-Lemon core (`ontolex:`) as used by the LDL 2026
retrodigitized-dictionary core. Where the 2026 requirement set names a
requirement but this dataset has no value for it, the requirement is listed in
§6 rather than satisfied with a placeholder. DMLex and TEI-Lex0 equivalents are
named only where the source field genuinely maps; no DMLex or TEI serialization
is produced here.

## 2. Namespaces

```turtle
@prefix ontolex: <http://www.w3.org/ns/lemon/ontolex#> .
@prefix lexinfo: <http://www.lexinfo.net/ontology/3.0/lexinfo#> .
@prefix dct:     <http://purl.org/dc/terms/> .
@prefix prov:    <http://www.w3.org/ns/prov#> .
@prefix skos:    <http://www.w3.org/2004/02/skos/core#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .
@prefix atlas:   <https://sanskrit-lexicon.github.io/csl-atlas/dataset/core-dossier/> .
```

`atlas:` is a **URI minting base**, not an ontology namespace. This profile does
not define classes or properties in it.

## 3. Dataset-level mapping

| JSON path | Meaning | RDF target | Card. | Req. | Note |
|---|---|---|---|---|---|
| `manifest.schemaVersion` | payload schema | `dct:conformsTo` | 1 | yes | object is the profile URI below |
| `manifest.scope` | `coreDossier` | `dct:type` | 0..1 | no | literal, not a controlled vocabulary |
| `manifest.license` | licence id | `dct:license` | 1 | yes | CC BY-SA 4.0 |
| `manifest.licenseUrl` | licence URI | `dct:license` | 1 | yes | same value as above |
| `manifest.generatedAt` | build time | `prov:generatedAtTime` | 1 | yes | `xsd:dateTime` |
| `manifest.generatedBy` | build command | `prov:wasGeneratedBy` | 1 | yes | activity label `npm run build-dict-comparison` |
| `manifest.sourceRoot` | textual source root | `prov:used` | 1 | yes | `csl-orig/v02` |
| `manifest.hrefBase` | source-link base | `prov:hadPrimarySource` | 1 | yes | base URI of `csl-orig` `v02` |
| `manifest.count` | record count | `dct:extent` | 1 | yes | literal; see §6 for the count caveat |
| `manifest.minDicts` | inclusion threshold | `dct:description` | 1 | yes | constraint prose, not a count |
| `manifest.dictionaries[].code` | dictionary code | `dct:source` | 1..n | yes | part of each source URI |
| `manifest.dictionaries[].label` | display label | `rdfs:label` | 1..n | no | label on the source-dictionary resource |
| `manifest.assumptions[]` | build assumptions | `dct:description` | 0..n | no | prose |
| `manifest.warnings[]` | build warnings | `dct:description` | 0..n | no | prose |

The profile URI to use in `dct:conformsTo` is the published URL of this file.

## 4. Entry-level mapping

Every entry lives in one shard. The shard id for a lemma is the hex code of its
first character plus the special `other` shard; the manifest indexes every
shard. Paths below are relative to `src/data/dicts/core-dossier/`.

| JSON path | Meaning | RDF target | Card. | Req. | Note |
|---|---|---|---|---|---|
| `entries[].l` | normalized headword (SLP1) | `ontolex:canonicalForm` → `ontolex:Form` → `ontolex:writtenRep` | 1 | yes | one `LexicalEntry` per `l`; literal `@sa` |
| `entries[].c` | number of dictionaries attesting `l` | — | 1 | yes | **no OntoLex equivalent**, §6.1 |
| `entries[].d[].code` | source dictionary code | `prov:wasDerivedFrom` | 1 | yes | to the source line URI |
| `entries[].d[].records` | dictionary records for `l` in that dictionary | — | 1 | yes | **no OntoLex equivalent**, §6.2 |
| `entries[].d[].firstLine` | first `csl-orig` line of the record block | `prov:wasDerivedFrom` | 1 | yes | URI fragment `#L<firstLine>` |
| `entries[].d[].gender` | grammar token from `<lex>` | `lexinfo:gender` and/or `lexinfo:partOfSpeech` | 0..n | no | composite tokens, §5.3 |
| `entries[].d[]` (whole tuple) | per-dictionary attestation | `prov:wasDerivedFrom` on the entry | 5..7 | yes | at least `minDicts = 5` |

An entry therefore has exactly one `ontolex:LexicalEntry` and one
`ontolex:Form` (its canonical form). It may have up to seven
`prov:wasDerivedFrom` source links. It has **no** `ontolex:Sense` from this
dataset.

## 5. Sense mapping (companion join only)

The frozen core dossier contains no sense text. A worked Sense is possible only
by joining the committed companion file
[`data/lexico/r2_align_iti.json`](../data/lexico/r2_align_iti.json), keyed on
`lemma = "iti"`. That companion has its own provenance and is **not** part of
the core-dossier release payload; it is used here to show the shape an exporter
would use once sense data is in scope.

| JSON path | Meaning | RDF target | Card. | Req. | Note |
|---|---|---|---|---|---|
| `senses.<dict>[].text` | dictionary sense/definition text | `ontolex:Sense` + `skos:definition` | 0..n | no | plain literal; language not tagged because the source mixes Sanskrit and English |
| `senses.<dict>[].sense` | source sense label | `dct:identifier` | 0..n | no | e.g. `bundle` |
| `senses.<dict>[].cluster` | project alignment cluster | — | 0..n | no | **no OntoLex equivalent**, §6.8 |
| `senses.<dict>[].n_anchor` | project anchor count | — | 0..n | no | **no OntoLex equivalent**, §6.8 |

Do not emit `ontolex:reference` or a `ontolex:LexicalConcept` from this join:
the companion does not assert a concept, only a source-specific gloss.

## 6. Deliberate no-equivalent list

These are stated rather than forced into a predicate. An exporter must leave
them out, or carry them as documented dataset columns, until a standard term is
agreed.

1. **`entries[].c` — coverage breadth.** OntoLex has no "attested in N
   dictionaries" property. It is a property of this study, not of a lexical
   entry.
2. **`entries[].d[].records` — dictionary record/homonym count.** DMLex models
   dictionary entries, but this dataset stores only the count and the block's
   first line, not the entries themselves.
3. **Composite grammar tokens.** Tokens are sorted concatenations of
   `m`, `f`, `n`, `adj`, `ind` (for example `find` = `f` + `ind`, `adjm` =
   `adj` + `m`). `adj` and `ind` are parts of speech, not genders. Anything
   that is not one of the five atomic tokens is dropped, not guessed. Empty
   tokens produce no triple.
4. **Senses and definitions.** The core dossier has none. No `ontolex:Sense`
   node may be minted from `l`, `c`, `records`, or `gender`.
5. **Source line as citation.** `firstLine` is a line number in a `csl-orig`
   `v02` plain-text file. It is a provenance anchor, not a permanent citation
   and not a scan page. Emit it as `prov:wasDerivedFrom`; do not call it a
   bibliographic citation.
6. **Transliteration and phonology.** `l` is SLP1 only. There is no IAST,
   Devanagari, IPA, or pronunciation field in this dataset, so no additional
   `ontolex:Form` may be invented.
7. **Lexical-entry identity.** `l` is a normalized headword, and the dossier
   aggregates across dictionaries and possible homonyms. It is not a
   dictionary-level entry identifier. An exporter needs a stable URI policy
   before minting entry URIs.
8. **Project-specific sense fields.** `cluster` and `n_anchor` in the companion
   R2 file are alignment-methodology fields, not OntoLex terms.
9. **Etymology, examples, citations, review status, evidence labels.** None are
   present in the core dossier; none are exported here.
10. **Full LDL 2026 core.** The fifteen-requirement core asks for more than
    this dataset can supply (notably senses, examples, and concept links).
    This profile satisfies the lexical-entry/form/source part and names the
    rest as out of scope.

## 7. Worked example — one real lemma, one real sense

### 7.1 Source JSON (verbatim, frozen)

Entry `iti` from
[`shards/69.json`](../src/data/dicts/core-dossier/shards/69.json), located by
`entries[].l == "iti"`:

```json
{
  "l": "iti",
  "c": 7,
  "d": [
    ["mw", 4, 100917, "find"],
    ["ap", 1, 93443, "ind"],
    ["pwg", 4, 48220, "find"],
    ["pw", 6, 64270, "findm"],
    ["wil", 1, 48403, "ind"],
    ["vcp", 1, 85845, "ind"],
    ["skd", 1, 40325, "ind"]
  ]
}
```

Companion sense from
[`data/lexico/r2_align_iti.json`](../data/lexico/r2_align_iti.json),
`senses.mw[0]`:

```json
{
  "sense": "bundle",
  "text": "1. iti ¦ f. ityE/ ( dat. ) See √ i above",
  "cluster": "western",
  "n_anchor": 1
}
```

### 7.2 RDF envelope

```turtle
atlas:lemma-iti
  a ontolex:LexicalEntry ;
  rdfs:label "iti"@sa ;
  ontolex:canonicalForm atlas:form-iti ;
  lexinfo:partOfSpeech lexinfo:indeclinable ;
  lexinfo:gender lexinfo:feminine, lexinfo:masculine ;
  prov:wasDerivedFrom
    <https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt#L100917>,
    <https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ap/ap.txt#L93443>,
    <https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt#L48220>,
    <https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pw/pw.txt#L64270>,
    <https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/wil/wil.txt#L48403>,
    <https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/vcp/vcp.txt#L85845>,
    <https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/skd/skd.txt#L40325> ;
  ontolex:sense atlas:sense-iti-mw-0 .

atlas:form-iti
  a ontolex:Form ;
  ontolex:writtenRep "iti"@sa ;
  dct:format "SLP1" .

atlas:sense-iti-mw-0
  a ontolex:Sense ;
  dct:identifier "bundle" ;
  skos:definition "1. iti ¦ f. ityE/ ( dat. ) See √ i above" ;
  dct:source <https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt#L100917> .
```

Notes on this envelope:

- `find` on the MW tuple expands to `f` + `ind`: the lexical entry gets
  `lexinfo:gender lexinfo:feminine` and `lexinfo:partOfSpeech
  lexinfo:indeclinable`. The `ind` tokens on AP/WIL/VCP/SKD add the same part of
  speech; the `findm` on PWK adds `lexinfo:masculine` as well. Duplicate triples
  collapse.
- `c = 7` and `records` (4, 1, 4, 6, 1, 1, 1) do **not** appear in the RDF.
- The sense node is from the companion join. Without it, the entry stops at
  `ontolex:canonicalForm`; that is the honest core-dossier shape.

## 8. Conformance checks for a reviewer

1. Resolve the profile's JSON paths against the frozen revision
   `12bd3d1`; every path in §3–§5 must exist.
2. Recompute `.source.json` `outputs` hashes and `treeSha256`; they must match.
3. Check the worked example `entries[].l == "iti"` is present in
   `shards/69.json` with the exact tuple values above.
4. Check the companion sense `senses.mw[0]` is present in
   `data/lexico/r2_align_iti.json`.
5. Confirm that no `ontolex:Sense`, `ontolex:LexicalConcept`, or
   `ontolex:reference` triple is claimed from the core dossier alone.

## 9. Normative owner

RDF export, SHACL validation, and OntoLex/DMLex/TEI serialization are owned by
[`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards). This atlas
artifact publishes the profile and the data; it does not ship an exporter. The
handoff pointer is tracked in `csl-standards` issue
[#165](https://github.com/sanskrit-lexicon/csl-standards/issues/165).
