# `<ls>` cross-dictionary citation graph

_Created: 06-07-2026 · Last updated: 06-07-2026_

**What this is.** A first-pass **citation-frequency graph** over the Cologne dictionaries:
which classical Sanskrit texts each dictionary quotes (via its `<ls>` source-citation tags)
and how often. Built by resolving each dictionary's own abbreviations to a shared canonical
text node, so `MBH`/`MBh`/`MAHĀBHĀRATA` all fold into one *Mahābhārata* node comparable
across dictionaries. Complements the *forensic* citation work in
[`data/forensic/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/forensic)
(shared-rare / shared-erroneous citations) — this is the *frequency* layer.

## Files

| File | What |
|---|---|
| [`ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv) | the graph edge list — `dict · canonical_text · count` |
| [`ls_citation_nodes.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nodes.tsv) | node table — `canonical_text · total_cites · n_dicts · variant_forms` (the raw expansions that folded into it) |
| [`ls_citation_unresolved_top.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_unresolved_top.tsv) | top unresolved raw keys per dict — the QA worklist for extending coverage |
| [`build_ls_citation_graph.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/build_ls_citation_graph.py) | the builder (reproduce below) |

## Method

1. Extract every `<ls>…</ls>` from `csl-orig/v02/<dict>/*.txt`.
2. Resolve the leading abbreviation by **longest-prefix match** against that dictionary's own
   abbreviation key from [`csl-guides/src/data/abbreviations.json`](https://github.com/sanskrit-lexicon/csl-guides/blob/main/src/data/abbreviations.json)
   (`works` + `mixed` lists), case-insensitive fallback.
3. Reduce each expansion to a text name (drop editorial tails: `, ed.…`, `nach…`, `in der…`).
4. **Fold** nodes by a diacritic- and case-insensitive key so spelling/casing variants merge
   (`ṚGVEDA`≡`Ṛg-veda`≡`Ṛgveda`); the surviving display name is the least-caps / shortest form,
   with all merged variants preserved in the `variant_forms` column.

## Coverage

Only the 8 dictionaries that have a populated abbreviation key *and* csl-orig text are resolved
here. `<ls>`-bearing dicts without a key yet (`ap`, `sch`, `pwkvn`, `ieg`, `gra`, `ae`, `bor`)
are the first coverage-extension target.

| Dict | raw `<ls>` | resolved | % | distinct texts |
|---|--:|--:|--:|--:|
| pwg | 801,790 | 568,162 | 70.9% | 504 |
| mw | 320,830 | 83,832 | 26.1% | 16 |
| pw | 98,484 | 50,701 | 51.5% | 243 |
| ben | 49,234 | 49,003 | 99.5% | 96 |
| bhs | 48,419 | 42,183 | 87.1% | 138 |
| ap90 | 43,894 | 37,993 | 86.6% | 149 |
| lrv | 16,650 | 16,469 | 98.9% | 106 |
| md | 58 | 47 | 81.0% | 4 |
| **total** | **1,379,359** | **848,390** | **61.5%** | **1,124** |

## Most-cited texts across the tradition (folded)

| cites | #dicts | text |
|--:|--:|---|
| 51,140 | 5 | Mahābhārata |
| 36,456 | 4 | Ṛgveda |
| 35,293 | 6 | Rāmāyaṇa (most widespread) |
| 21,509 | 1 | Pāṇini (Aṣṭādhyāyī) |
| 20,948 | 3 | Bhāgavata-Purāṇa |
| 20,196 | 4 | Śabdakalpadruma *(a dictionary cited as a source)* |
| 17,746 | 2 | Indische Sprüche |
| 16,433 | 6 | Kathāsaritsāgara |
| 14,718 | 5 | Amarakoṣa |
| 14,268 | 4 | Raghuvaṃśa |

## Known issues (this is a first pass — do not treat as final)

- **🔴 MW `<ls>` is polluted by non-text markers.** MW reuses `<ls>` for grammatical/attribution
  abbreviations, so its top "texts" resolve to `lexicographers` (40,213, = the `L.` marker),
  `ibidem` (10,100), `masculine or neuter`, `catalogue`. MW needs a citation-vs-grammatical
  filter before its edges are trustworthy — treat MW rows as suspect for now.
- **🔴 PWG editorial placeholder.** `? [Cologne Addition]` (34,635) is an editorial marker, not a
  text; filter it out.
- **🟠 Unresolved tail (38.5%).** pw/mw carry long abbreviation tails absent from the key; see
  `ls_citation_unresolved_top.tsv`. Some expansions (e.g. `HEMACANDRA'S ABHIDHĀNACINTĀMAṆI`) keep
  a possessive/description because the editorial-tail cut misses `'S …`.
- **🟠 No per-locus resolution.** Counts are per source-text only; the locus (book/verse) is
  discarded. Locus→scan-URL resolution already exists in
  [`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py).

## Reproduce

```sh
python data/citations/build_ls_citation_graph.py    # reads ../csl-orig + ../csl-guides
```

Requires `csl-orig` and `csl-guides` as siblings of `csl-atlas`. ~1 min.

**Provenance:** derived from [`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig)
`<ls>` tags + [`csl-guides`](https://github.com/sanskrit-lexicon/csl-guides) abbreviation keys.
Spun out of the [`DATA_LAYERS_CENSUS.md`](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md)
(06-07-2026); full task in handoff [H213](https://github.com/gasyoun/Uprava/blob/main/handoffs/H213-Opus_csl-atlas_ls_citation_graph_canonicalization_06.07.26.md).

_Dr. Mārcis Gasūns_
