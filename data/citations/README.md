# `<ls>` cross-dictionary citation graph

_Created: 06-07-2026 · Last updated: 24-09-2026_

**What this is.** A **citation-frequency graph** over the Cologne dictionaries: which
classical Sanskrit texts each dictionary quotes (via its `<ls>` source-citation tags) and
how often. Built by resolving each dictionary's own abbreviations to a shared canonical text
node, so `MBH`/`MBh`/`MAHĀBHĀRATA` all fold into one *Mahābhārata* node comparable across
dictionaries. Complements the *forensic* citation work in
[`data/forensic/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/forensic)
(shared-rare / shared-erroneous citations) — this is the *frequency* layer.

**Second pass (06-07-2026, [H213](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H213-Opus_csl-atlas_ls_citation_graph_canonicalization_06.07.26.md)):**
the MW grammatical-marker pollution is now filtered, the `? [Cologne Addition]`
unidentified-source placeholder is dropped, three keyless dicts (`ap`, `sch`, `pwkvn`) are
resolved by borrowing a same-tradition key, and the top author's-genitive / title-synonym
node forms are folded. See [Method](#method) and [Change log](#change-log).

## Files

| File | What |
|---|---|
| [`ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv) | the graph edge list — `dict · canonical_text · count` |
| [`ls_citation_nodes.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nodes.tsv) | node table — `canonical_text · total_cites · n_dicts · variant_forms` (the raw expansions that folded into it) |
| [`ls_citation_unresolved_top.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_unresolved_top.tsv) | top unresolved raw keys per dict — the QA worklist for extending coverage |
| [`ls_citation_nontext_filtered.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nontext_filtered.tsv) | audit trail of `<ls>` markers filtered as non-bibliographic (grammatical/editorial) — MW only |
| [`ls_citation_graph.source.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_graph.source.json) | provenance sidecar written on every run — csl-atlas / `csl-orig` / `csl-guides` revisions with dirty flags, abbreviations-key SHA-256, builder SHA-256, SHA-256 of each output (the revision binding of the committed TSVs) |
| [`build_ls_citation_graph.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/build_ls_citation_graph.py) | the builder (reproduce below) |

## Method

1. Extract every `<ls>…</ls>` from `csl-orig/v02/<dict>/*.txt`.
2. Resolve the leading abbreviation by **longest-prefix match** against that dictionary's own
   abbreviation key from [`csl-guides/src/data/abbreviations.json`](https://github.com/sanskrit-lexicon/csl-guides/blob/main/src/data/abbreviations.json)
   (`works` + `mixed` lists), case-insensitive fallback.
3. **Non-text filter (MW).** MW reuses `<ls>` for grammatical voice/case markers
   (`A.`=Active, `mn.`=masculine or neuter, `ind.`), editorial reference markers
   (`ibid.`, `Cat.`=catalogue, `col.`=column), and the `L.`=lexicographers tag. These resolve
   to non-bibliographic "texts", so a stoplist (`NONTEXT_NODES`) excludes them from the graph
   and records the per-dict count in `ls_citation_nontext_filtered.tsv` — an auditable exclusion,
   not a silent drop. Coarse genre labels a dict genuinely cites (Brāhmaṇa, Buddhist,
   Inscriptions) are **kept**.
4. **Placeholder filter.** An abbreviation whose Cologne expansion is `? [Cologne Addition]`
   (or the OCR variant `{Cologne Addition]`) is one Cologne itself could not identify — it is
   treated as **unresolved**, not a text. Compounds like `Divyāvadāna ? [Cologne Addition]`
   recover to their real text (`Divyāvadāna`).
5. **Key-borrow.** Three `<ls>`-bearing dicts have no abbreviation key of their own but a
   documented shared convention, so they borrow one (resolved-% measured, see below):
   `ap`←`ap90` (both Apte, same abbreviation system), `pwkvn`←`pwg` and `sch`←`pwg`
   (PW-*Nachträge* tradition).
6. Reduce each expansion to a text name (drop editorial tails: `, ed.…`, `nach…`, `in der…`,
   `in the…`, leading article `The/die/der`).
7. **Fold** nodes by a diacritic- and case-insensitive key so spelling/casing variants merge
   (`ṚGVEDA`≡`Ṛg-veda`≡`Ṛgveda`); the surviving display name is the least-caps / shortest form,
   with all merged variants preserved in the `variant_forms` column.
8. **Curated alias fold.** A small, hand-verified table (`CANON_ALIAS`) folds the highest-count
   author's-genitive and German-description forms, plus a few title-synonyms, to one standard
   text name — e.g. `MANU'S Gesetzbuch` + `Mānavadharmaśāstra` → *Manusmṛti*;
   `PĀṆINI'S acht Bücher grammatischer Regeln` → *Aṣṭādhyāyī (Pāṇini)*;
   `The ŚATAPATHABRĀHMAṆA in the Mādhyandina-Śākhā` → *Śatapatha-Brāhmaṇa*. Every mapping is a
   well-established identification, never a guess. Since the 24-09-2026 re-freeze the table
   also carries the 37 eye-checked transliteration-variant pairs of the H5295 fold table
   (`Raghuvanśa` → Raghuvaṃśa, `Rigveda` → Ṛgveda, `Naishadhacharita` → Naiṣadhacarita, …);
   the long tail of title-synonymy beyond transliteration is left as a documented residual.

## Coverage

11 dictionaries have a populated abbreviation key (own or borrowed) *and* csl-orig text.
`% text` is text-citations ÷ (raw − non-text markers). `*` marks a borrowed key.

| Dict | raw `<ls>` | non-text filtered | resolved | % text | distinct texts |
|---|--:|--:|--:|--:|--:|
| pwg | 801,790 | 0 | 536,172 | 66.9% | 481 |
| mw | 320,830 | 63,582 | 20,250 | 7.9% | 5 |
| pw | 98,484 | 0 | 50,701 | 51.5% | 243 |
| ap\* | 68,273 | 0 | 57,112 | 83.7% | 155 |
| ben | 49,389 | 0 | 47,251 | 95.7% | 94 |
| bhs | 48,419 | 0 | 40,875 | 84.4% | 136 |
| ap90 | 43,894 | 0 | 37,993 | 86.6% | 149 |
| sch\* | 31,041 | 0 | 11,496 | 37.0% | 161 |
| pwkvn\* | 17,629 | 0 | 8,386 | 47.6% | 173 |
| lrv | 16,650 | 0 | 16,469 | 98.9% | 106 |
| md | 58 | 0 | 47 | 81.0% | 4 |
| **total** | **1,496,457** | **63,582** | **826,752** | **57.7%** | **874** |

## Most-cited texts across the tradition (folded)

| cites | #dicts | text |
|--:|--:|---|
| 56,822 | 8 | Mahābhārata |
| 39,025 | 11 | Ṛgveda (cited by every dictionary) |
| 38,154 | 9 | Rāmāyaṇa |
| 28,140 | 8 | Manusmṛti *(incl. Mānavadharmaśāstra / Manu's Gesetzbuch / Manusmṛiti)* |
| 24,300 | 8 | Bhāgavata-Purāṇa |
| 24,025 | 8 | Raghuvaṃśa |
| 21,791 | 3 | Aṣṭādhyāyī (Pāṇini) |
| 20,232 | 7 | Śabdakalpadruma *(a dictionary cited as a source)* |
| 18,073 | 3 | Abhidhānacintāmaṇi |
| 18,030 | 4 | Indische Sprüche |
| 17,015 | 9 | Kathāsaritsāgara |
| 14,918 | 8 | Amarakoṣa |

## Known issues (still a derived dataset — read the caveats)

- **🟠 MW citation yield is genuinely low (7.9%).** After filtering 63,582 grammatical/editorial
  markers, only ~20k of MW's `<ls>` are text citations resolvable from its key; most of the rest
  are the untracked `L.`=lexicographers convention or unkeyed abbreviations. MW's *text* edges are
  now trustworthy, but MW is a poor `<ls>` frequency source overall.
- **🟠 Borrowed-key dicts resolve partially.** `sch` (37.0%) and `pwkvn` (47.6%) share only part
  of the PW abbreviation set; unresolved keys stay in `ls_citation_unresolved_top.tsv`. `ap`
  (83.7%) borrows `ap90` cleanly.
- **🟠 Keyless dicts still excluded.** `ap` is now resolved, but `sch`/`pwkvn` aside, the
  remaining `<ls>`-bearing dicts without a usable key — `gra` (Vedic-specific, PW key only 30%),
  `ae`, `bor` (tiny, single-letter keys) — are not resolved. `ieg` is an **epigraphic outlier**:
  it cites inscription corpora (`EI`=Epigraphia Indica, `SII`=South Indian Inscriptions, `IA`),
  not classical texts, and belongs to a separate epigraphic citation universe — left out of the
  text graph on purpose.
- **🟠 Title-synonymy tail.** The curated alias folds the largest author's-genitive and
  synonym forms and, since 24-09-2026, the 37 transliteration-variant pairs the A50 ledger
  listed (its residual fold table is now empty); the long tail (a text under a second
  lesser-used title) is unmerged. `AUFRECHT`
  (12,718, a scholar/editor shorthand of ambiguous referent) is deliberately left unresolved
  rather than guessed.
- **🟠 No per-locus resolution.** Counts are per source-text only; the locus (book/verse) is
  discarded. Locus→scan-URL resolution already exists in
  [`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py).

## Change log

- **24-09-2026 (v3, re-freeze at a recorded revision, [H5407](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5407-Fable_csl-atlas_a50-citation-graph-refreeze-recorded-revision-alias-fold_24.09.26.md)):**
  `CANON_ALIAS` extended with the 37 eye-checked transliteration-variant pairs of the H5295
  fold table (with a chain guard: an alias target is never itself an alias key); TSVs rebuilt
  against `csl-orig@f4c08c578b330e2379e38f54d3a541f1564b8eee` + 
  `csl-guides@64c967d1d08d26868bbbc289b4aacec7f4a8f3ff` (both clean; `abbreviations.json`
  SHA-256 `dfd9fb68…8a48`) and the first `ls_citation_graph.source.json` committed beside them;
  two builder runs at that pair are byte-identical (`ls_citation_edges.tsv` SHA-256
  `41bee931…3bd0`, `ls_citation_nodes.tsv` `6039af4d…e474`). 828,505 citations / 912 nodes /
  1,701 edges → **826,752 / 874 / 1,699**. The non-fold part of the move is entirely Benfey:
  `csl-orig` `v02/ben/ben.txt` was edited after the 06-07-2026 freeze —
  [`056acf4`](https://github.com/sanskrit-lexicon/csl-orig/commit/056acf4) (06-07-2026, "BEN now
  has PWG style references", BEN #19: bare `Chr.` tags for *my Sanskrit Chrestomathy* 3,017 →
  1,602), [`d1d0a18`](https://github.com/sanskrit-lexicon/csl-orig/commit/d1d0a18) (07-07-2026,
  "BEN LS Gorr. handled", BEN #21: `Gorr.` 347 → 29) and
  [`45d6907`](https://github.com/sanskrit-lexicon/csl-orig/commit/45d6907) (09-07-2026, BEN #27:
  → 15); ben raw `<ls>` 49,234 → 49,389, resolved 49,003 → 47,251. The `csl-guides` key is
  unchanged since `cd79a7b` (03-07-2026) apart from the `Weber` → `WEBER` case change. Five
  duplicate variant rows dropped from `tradition_tags.tsv` (119 → 114). A50, the claim ledger
  §P (`narrows` → `survives`) and the forensic pins updated in the same PR.
- **24-09-2026 (provenance sidecar, H5295, no data change):** the builder now writes
  `ls_citation_graph.source.json` next to the TSVs on every run (first committed copy lands
  with the H5407 re-freeze) — sibling `csl-orig`/`csl-guides` `HEAD` revisions, dirty flags, the
  abbreviations-key SHA-256 and the SHA-256 of each output. The committed TSVs were frozen on
  06-07-2026 **without** a recorded sibling revision; a rebuild at `csl-orig@f4c08c57` +
  `csl-guides@64c967d` (24-09-2026) drifts to 826,752 citations / 911 nodes / 1,699 edges
  (almost all in `ben`: `my Sanskrit Chrestomathy` 3,017 → 1,599, `Gaspare Gorresio` 347 → 16;
  plus one `ap` citation and a `Weber` → `WEBER` key case). The TSVs are left as committed so the A50 figures stay bound to
  them by hash; the re-freeze at a recorded revision plus the 37-pair alias extension is
  [H5407](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5407-Fable_csl-atlas_a50-citation-graph-refreeze-recorded-revision-alias-fold_24.09.26.md).
  Claim ledger: [`data/forensic/A50_CLAIM_FALSIFICATION_LEDGER.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/A50_CLAIM_FALSIFICATION_LEDGER.md).
- **06-07-2026 (v2, H213):** MW non-text filter (−63,582 markers); `? [Cologne Addition]`
  placeholder dropped (was a spurious ~39k-cite node); `ap`/`sch`/`pwkvn` added via key-borrow
  (8→11 dicts); curated alias fold (Manusmṛti/Aṣṭādhyāyī/Śatapatha-Brāhmaṇa/… merged);
  duplicate `ls_canon_*` files removed in favour of the documented `ls_citation_*` names.
- **06-07-2026 (v1):** first canonicalized build, 8 dicts, 848,390 resolved
  ([PR #219](https://github.com/sanskrit-lexicon/csl-atlas/pull/219)).

## Reproduce

```sh
python data/citations/build_ls_citation_graph.py    # reads ../csl-orig + ../csl-guides
```

Requires `csl-orig` and `csl-guides` as siblings of `csl-atlas` (or `SIBLING_ROOT=<dir>`).
~1 min. The committed TSVs reproduce byte-for-byte at the revision pair recorded in
`ls_citation_graph.source.json` — currently `csl-orig@f4c08c57` + `csl-guides@64c967d`
(`git -C ../csl-orig checkout f4c08c57`, `git -C ../csl-guides checkout 64c967d`); at any other
revision compare the sidecar's output hashes before trusting a diff.

**Provenance:** derived from [`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig)
`<ls>` tags + [`csl-guides`](https://github.com/sanskrit-lexicon/csl-guides) abbreviation keys.
Spun out of the [`DATA_LAYERS_CENSUS.md`](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md)
(06-07-2026); full task in handoff [H213](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H213-Opus_csl-atlas_ls_citation_graph_canonicalization_06.07.26.md).

_Dr. Mārcis Gasūns_
