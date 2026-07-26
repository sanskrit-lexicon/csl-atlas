# Xref shared-core: label taxonomy and sampling method

_Created: 25-07-2026 · Last updated: 26-07-2026_

Russian version: [XREF_SHARED_CORE_LABEL_TAXONOMY.ru.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_SHARED_CORE_LABEL_TAXONOMY.ru.md).
Both files say the same thing; their figures are checked against the data automatically
([`test/xref-taxonomy-docs.test.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/xref-taxonomy-docs.test.mjs)),
so they cannot drift apart numerically.

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
asserts only that the cross-reference is **real and lexical**: the target is an actual
lemma rather than a piece of markup convention, and the link between the two words is a
linguistic one. A vṛddhi derivative, a `-ka` suffix formation, a dialectal by-form and an
etymological cognate all confirm equally — the classification does not record *which* of
those it is, and does not claim the two are synonyms.

## ⚠ What a shared reference does *not* prove

An earlier version of this document (and of the sheet) justified a confirm on the grounds
that "both dictionaries, **independently**, print a cross-reference … two editorial
traditions made the same link". **That is wrong, and MG rejected it on 26-07-2026: MW
depends on PWG and PW.** Monier-Williams 1899 was built on Böhtlingk–Roth; a reference
shared between them may be one tradition copied, not two traditions agreeing.

The edge data says the same thing without appeal to the bibliography.
[`scripts/lexico/m9_xref_marker_agreement.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m9_xref_marker_agreement.py)
compares MW's `cf.` targets against PWG's `Vgl.`/`s.` targets for the same headword,
against a null that reshuffles MW's targets while preserving each headword's out-degree:

| Measure | Value |
|---|---|
| Headwords cross-referenced in **both** dictionaries | 2,750 |
| MW `cf.` edges on those headwords | 3,184 |
| …whose target PWG also points to | **694 (21.8%)** |
| Expected by chance (200 null draws, seed 20260726) | 0.235 (0.007%) |
| Enrichment | **≈2,953×** |
| Null draws ≥ observed | 0 / 200 (p < 0.005) |

For scale: MW carries 7,637 normalized `cf.` edges and PWG 25,766. The raw containment
asymmetry (11.2% of MW's edges appear in PWG vs 3.5% the other way) is ~3.2×, almost
exactly the 3.4× edge-count ratio — **that asymmetry is a set-size artifact and is not
directional evidence.** The agreement enrichment is the result that carries weight.

What this changes in practice: confirm an edge because the reference is *real and
lexical*, not because it is *doubly attested*. Full measurement and its limitations:
[`data/lexico/xref_marker_agreement.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_marker_agreement.json).

## The four labels in play

Two further labels — `edition-continuity` and `lexical-target` — exist in the vocabulary
but are not answer options here: the first is for within-family edges (this sheet is
cross-family by construction), the second describes a *target string* in the hub profile
and is carried on each row as `hubClass`, i.e. it is the reason a row reached the sheet,
not a verdict on it.

### `lexical-shared-core` — confirm

The cross-reference is real and lexical: the target is an actual lemma, not a piece of
markup convention, and the link between the two words is a linguistic one. See the
section above for what this deliberately no longer claims.

| Example | Why |
|---|---|
| `mw-pwg-shared:09` — `Awi → Aqi` (āṭi → āḍi) | MW prints `(cf. Aqi and Ati)`, PWG prints `Vgl. Aqi und Ati`, for the same bird name (*Turdus Ginginianus*). A real by-form link — though not, on this evidence alone, two independent records of it. |
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

Both examples are drawn from the 10 prefix controls the packet auto-resolves on the
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

#### How artifacts get made: the documented MW↔PWG convention divergences

Before judging whether an edge is an artifact, know the mechanisms that produce one.
Dhaval Patel's *Normalizing headwords of Cologne digital dictionaries* (2016,
[`docs/refs/Patel_2016_Normalizing_headwords.pdf`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/refs/Patel_2016_Normalizing_headwords.pdf))
catalogues the per-dictionary headword conventions. Four of them put **MW and PWG on
opposite sides**, and this pipeline reconciles none of them:

| Patel convention | MW writes | PWG writes | Example |
|---|---|---|---|
| 3.1 / 3.2 — *śatṛ* present participles | `-at` | `-a` + virāma | गच्छत् vs अनागच्` |
| 3.4 / 3.5 — *vatup* / *matup* stems | `-vat` / `-mat` | `-v` / `-m` | भगवत् vs भगव् |
| 6.1 / 6.2 — ṛ-final stems | `-ṛ` | `-ar` | कर्तृ vs पितर् |
| 7.1 / 7.4 — *vas* / *yas* stems | `-vas` / `-yas` | `-vaṃs` / `-yaṃs` | विद्वस् vs विद्वंस् |

So the risk runs in **both** directions:

- **Created.** The accent/`°`/hyphen stripping in `m6_xref_lineage.py` can fold two
  genuinely distinct spellings onto one key — the mechanism behind the two examples above.
- **Hidden.** The four divergences above mean a real shared edge on, say, a ṛ-stem *can
  never intersect*, because MW's `-ṛ` key and PWG's `-ar` key never match. **The 641-edge
  intersection is therefore an undercount**, and a whole-alphabet re-run that first
  normalises per Patel would be expected to find more, not fewer, shared edges.

### `too-sparse` — reject

The evidence on the card is too thin to answer either way: typically only one
dictionary's record is attached (`missingExactEdgeDictionaries` is non-empty), so the
"shared" in shared-core is not demonstrated. This is not a rejection of the edge — it is
the honest answer when the card does not contain what the question asks about. **4 of the
40 rows are in this state** and now say so on the card.

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
   `data/lexico/xref_shared_edges.csv` — **641 edges**. (Quoted as "642" until 26-07-2026:
   a `wc -l` that counted the CSV header as a data row. The packet now computes this figure
   rather than carrying it as a literal, and
   [`test/xref-taxonomy-docs.test.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/xref-taxonomy-docs.test.mjs)
   pins both prose companions to it.)
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
head of the alphabet, not the 641. Re-running over a random or stratified draw is a
separate job that has not been started.

Alongside the 40, 10 `prefix-control` rows (the top 5 prefix-convention targets in each
of PWG and MW, with up to 3 source examples each) are carried as a contrast class. All 10
auto-resolve on their truncation marker and are never put to a reviewer.

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

**The sheet is in Russian** (26-07-2026, H1648) — question, label definitions, worked
examples, sampling method, markup legend, and the emitter's own chrome (toolbar button,
keyboard hint, save banner, vote legend, translated through
[`csl-pyutil` 0.4.0's `ui_strings`](https://github.com/sanskrit-lexicon/csl-pyutil/pull/9)).
The only non-Russian prose left on a card is the dictionary text itself, which is quoted
verbatim and stays German for PWG and English for MW. This document is kept in both English
(repo-facing record) and [Russian](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_SHARED_CORE_LABEL_TAXONOMY.ru.md)
(reviewer-facing); the sheet itself is self-sufficient and requires neither.

_Dr. Mārcis Gasūns_
