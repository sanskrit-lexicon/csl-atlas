# Xref shared-core: label taxonomy and sampling method

_Created: 25-07-2026 · Last updated: 25-07-2026_

The decision rules behind the MW/PWG shared-core review sheet
([`csl-atlas-xref-shared-core_40edges_review.html`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-review-sheets.py),
generated into the gitignored `review/`): what each label means, when to reach for it,
and how the 40 edges on the sheet were chosen.

Written because the sheet asked a reviewer to reject an edge into one of three named
buckets while defining none of them, and disclosed no sampling method
([H1646](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1646-Opus_csl-atlas_xref-sheet-reviewability-40edges_25.07.26.md)).
The canonical machine-readable copy of everything below is
`packetLabelVocabulary` + `selectionPolicy` in
[`data/lexico/xref_source_check_packet.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_source_check_packet.json),
emitted by
[`scripts/build-xref-source-check-packet.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-xref-source-check-packet.mjs);
this document is the prose companion, not a second source of truth.

## What the sheet actually asks

For each edge `source → target`, the machine proposes `lexical-shared-core` and asks
whether the MW and PWG source records support it **as a meaningful shared lexical
cross-reference rather than a normalization or convention artifact**.

The question is *not* whether the two words mean the same thing. Confirming an edge
asserts only that both dictionaries independently printed a cross-reference between
these two headwords and that the target is a real lemma. A vṛddhi derivative, a `-ka`
suffix formation, a dialectal by-form and an etymological cognate all confirm equally —
the classification does not record *which* of those it is, and does not claim the two
are synonyms.

## The four labels in play

Two further labels — `edition-continuity` and `lexical-target` — exist in the vocabulary
but are not answer options here: the first is for within-family edges (this sheet is
cross-family by construction), the second describes a *target string* in the hub profile
and is carried on each row as `hubClass`, i.e. it is the reason a row reached the sheet,
not a verdict on it.

### `lexical-shared-core` — confirm

Both dictionaries, independently, print a cross-reference from this headword to this
target, and the target is a real lemma rather than a markup convention. Two editorial
traditions made the same link.

| Example | Why |
|---|---|
| `mw-pwg-shared:09` — `Awi → Aqi` (āṭi → āḍi) | MW prints `(cf. Aqi and Ati)`, PWG prints `Vgl. Aqi und Ati`, for the same bird name (*Turdus Ginginianus*). Two independent editors recorded the same by-form link. |
| `mw-pwg-shared:14` — `BI → Byas` (bhī → bhyas) | A derivational/etymological relation between the root *bhī* 'fear' and *bhyas*, carried by both dictionaries. Not synonyms — and that does not matter; the edge is still lexical rather than an artifact. |

### `prefix-convention` — reject

The target is not a headword at all but part of the dictionary's own abbreviation
machinery: a truncated compound member, or a prefix cited as a form. This says nothing
against the entry; it says the reference is house style for compressing compounds and so
carries no evidence about lexical descent.

| Example | Why |
|---|---|
| `xref-prefix-control:pwg:01` — target `a˚` (320 references in PWG) | `˚` is CDSL's truncation ring: `a˚` abbreviates "the compound beginning in *a-*", not a lemma. |
| `xref-prefix-control:mw:05` — target `aBi-` (11 references in MW) | The trailing hyphen marks a prefix cited as a compound-forming element — same class, different mark. |

Both examples are drawn from the ten prefix controls the packet auto-resolves on the
marker alone, so they are proven members of the class rather than illustrations.

### `normalization-risk` — reject

The edge may exist only because the pipeline folded MW and PWG spellings together.
[`scripts/lexico/m6_xref_lineage.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m6_xref_lineage.py)
strips MW's `-` and accent marks and PWG's `°` ring before intersecting the two edge
sets, so two headwords the dictionaries spelt differently can meet in the middle. Reach
for this label when source and target differ **only** in vowel length, accent, or a
diacritic the normaliser touches.

This is not a claim that the words are unrelated — a length variant is often a genuine
by-form. It flags that *this edge* is not independent evidence, because the matching step
could have manufactured it.

| Example | Why |
|---|---|
| `mw-pwg-shared:30` — `BuHKAra → BUHKAra` (buhkāra → būhkāra) | Differs only in the length of the first vowel, and the reciprocal edge `mw-pwg-shared:15` runs the other way. Plausibly an artifact of which form each dictionary chose as headword. |
| `mw-pwg-shared:21` — `BastrakA → BastrAkA` (bhastrakā → bhastrākā) | Same shape: only the placement of vowel length distinguishes the two strings. |

### `too-sparse` — reject

The evidence on the card is too thin to answer either way: typically only one
dictionary's record is attached (`missingExactEdgeDictionaries` is non-empty), so the
"shared" in shared-core is not demonstrated. This is not a rejection of the edge — it is
the honest answer when the card does not contain what the question asks about. **Four of
the forty rows are in this state** and now say so on the card.

| Example | Why |
|---|---|
| `mw-pwg-shared:07` — `ArAt → Are` (ārāt → āre), PWG only | PWG's record shows an ablative adverb pointing at a locative-shaped one; MW has no exact edge row, so there is no second side to corroborate a shared editorial judgement. |
| `mw-pwg-shared:03` — `Akzit → anAkzit` (ākṣit → anākṣit), PWG only | Single-dictionary evidence again. |

## How the 40 edges were sampled

Three deterministic stages — no RNG anywhere, so a re-run reproduces the same 40 cards in
the same order.

1. **Candidate pool.**
   [`scripts/lexico/m6_xref_lineage.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m6_xref_lineage.py)
   reads MW's and PWG's cross-reference edges, normalises each target (see
   `normalization-risk` above), and writes the MW ∩ PWG set to
   `data/lexico/xref_shared_edges.csv` — **642 edges**.
2. **The sample.** `buildSharedCoreSample()` in
   [`scripts/build-xref-hub-review.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-xref-hub-review.mjs)
   takes `sharedEdges.slice(0, 40)` — the **first 40 rows of that CSV in file order**.
3. **Evidence.**
   [`scripts/build-xref-source-check-packet.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-xref-source-check-packet.mjs)
   re-slices to 40, freezes the `sampleId` order (`validatePayload` rejects any reorder),
   and attaches the exact MW/PWG source records per edge plus Cologne entry and scan links
   for both ends of the edge.

### The bias, stated plainly

**This is not a random sample.** The CSV is in headword order, so all 40 cards are Ā-, B-,
C-, D- or G-initial headwords. A confirm/reject rate measured on these 40 describes the
head of the alphabet, not the 642. Re-running over a random or stratified draw is a
separate job that has not been started.

Alongside the 40, ten `prefix-control` rows (the top five prefix-convention targets in
each of PWG and MW, with up to three source examples each) are carried as a contrast
class. All ten auto-resolve on their truncation marker and are never put to a reviewer.

## Reading the cards

Each card shows, per dictionary record: a link to the **Cologne entry display**
(`indexcaller.php`, which auto-searches the headword), a link to the **printed scan page**
(`servepdf.php`), and the csl-orig blob line — plus the raw CDSL record with its markup
colour-coded by part class and every occurrence of the cross-reference target outlined. A
separate panel links the **target** headword in both dictionaries, since an edge has two
ends and only the source end used to be shown.

Cologne entry links resolve a *headword*, not one exact record: where a dictionary has
homonyms the lookup shows all of them. The csl-orig link remains the pointer to the precise
record.

_Dr. Mārcis Gasūns_
