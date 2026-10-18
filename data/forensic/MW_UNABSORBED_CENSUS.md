# The MW-unabsorbed census — what the Petersburg Nachträge hold that Monier-Williams never took

_Created: 17-09-2026 · Last updated: 17-09-2026_

**What this is.** The full census behind the **571** figure folded into Article 21
([`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md))
§3.5, same companion pattern as [`SHARED_OMISSION_TEST.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SHARED_OMISSION_TEST.md)
and [`SENSE_ORDER_TEST.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SENSE_ORDER_TEST.md).
Where F9 measures the *omission* clause of Böhtlingk's 1883 charge on real indigenous words, this
census measures, entry by entry, what the Petersburg **Nachträge** — the seven supplement volumes
of Böhtlingk's `pw`, and above all volume 7 (35,581 entries) — hold that MW never absorbed.
External to this repo's forensic suite: built and frozen in
[`gasyoun/SanskritLexicography/HeadwordLists/`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-WIDENED-16-09-2026.md)
(frozen, verifier-PASSed 16-09-2026; archived here 17-09-2026 per the 17-09-2026 routing ruling).

## Method (canary-locked)

Base: every `pw.txt` entry whose `<pc>` begins `7-` — the Nachträge volume. A **homonym-extension**
is a volume-7 entry with an explicit `<hom>N.</hom>`, N ≥ 2 (hom 1 is the base word), whose word
MW99 already heads and whose N **exceeds MW's main-body maximum** `<h>` for that `k1` (the MW
annexure, `<info n="sup"/>`, excluded from the max and reported as a per-row sensitivity flag).
**Canary `kārin`:** MW main body tops out at homonym 2, the Nachträge record homonym 3 at
`7-331-d` ([`pw.txt` line 620966](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pw/pw.txt#L620966))
⇒ extension. The *kārin*³ in MW's own annexure ("scattering, destroying," fr. √kṛ) is a
**different derivation** — a numbering coincidence, not absorption; exactly 8 of the 571 carry
such an annexure number, the other **563 none at all**. POS from entry `<lex>` tags, normalised;
same-tradition corroboration (`sch`, `pwg`) excluded. Corroboration scan over 36 dictionaries
outside the Böhtlingk tradition: **517/571 (90.5 %)** attested by ≥1 outside-tradition
dictionary; DCS corpus attestation: 374 (65.5 %).

## Result

**Headline: 571 homonym-extensions.** The rest of the volume-7 unabsorbed residual, by class:
**8,406** headwords new to the Petersburg main body · **4,112** absent from *both* MW editions ·
**27** present in MW72 but dropped by MW99 · **610** absorbed only as variant/fold-twin forms ·
**2,743** confirmed-missing residue of the starred sweep.

**All supplement layers** (unique headwords per layer; `skipped by both` = absent from MW72 and
MW99):

| layer | entries (unique) | in PW main body (extensions) | new headwords | `<hom>`-tagged | in MW72 | in MW99 | skipped by both |
|---|--:|--:|--:|--:|--:|--:|--:|
| `sup_1` | 1,755 | 765 | 990 | 62 | 342 | 991 | 758 |
| `sup_2` | 1,464 | 530 | 934 | 40 | 259 | 757 | 703 |
| `sup_3` | 1,712 | 707 | 1,005 | 70 | 361 | 1,136 | 573 |
| `sup_4` | 1,016 | 359 | 657 | 45 | 180 | 669 | 347 |
| `sup_5` | 2,192 | 1,056 | 1,136 | 140 | 564 | 1,568 | 615 |
| `sup_6` | 1,229 | 522 | 707 | 70 | 264 | 808 | 420 |
| **`sup_7`** | **13,094** | **4,688** | **8,406** | **541** | **2,892** | **8,955** | **4,112** |

**Part-of-speech cross-cut** (the informative cut is the homonym-extension class: adjectives
first, by a wide margin; the broad extension class is 85.6 % untagged, so its POS distribution is
reported as sparsity, not claimed):

| class | POS | n | share % |
|---|---|--:|--:|
| homonym-extension (`sup_7`) | adj. | 296 | 51.8 |
| homonym-extension (`sup_7`) | (no lex) | 129 | 22.6 |
| homonym-extension (`sup_7`) | m. | 69 | 12.1 |
| homonym-extension (`sup_7`) | f. | 28 | 4.9 |
| homonym-extension (`sup_7`) | n. | 27 | 4.7 |
| homonym-extension (`sup_7`) | adv. | 20 | 3.5 |
| homonym-extension (`sup_7`) | other | 2 | 0.4 |
| extension-of-PW-main-body (`sup_7`) | (no lex) | 4,011 | 85.6 |
| extension-of-PW-main-body (`sup_7`) | m. | 228 | 4.9 |
| extension-of-PW-main-body (`sup_7`) | n. | 150 | 3.2 |
| extension-of-PW-main-body (`sup_7`) | f. | 144 | 3.1 |
| extension-of-PW-main-body (`sup_7`) | adj. | 141 | 3.0 |
| extension-of-PW-main-body (`sup_7`) | adv. | 14 | 0.3 |
| new-headword (`sup_1`) | (not tabulated) | 990 | — |
| new-headword (`sup_2`) | (not tabulated) | 934 | — |
| new-headword (`sup_3`) | (not tabulated) | 1,005 | — |
| new-headword (`sup_4`) | (not tabulated) | 657 | — |
| new-headword (`sup_5`) | (not tabulated) | 1,136 | — |
| new-headword (`sup_6`) | (not tabulated) | 707 | — |
| new-headword (`sup_7`) | (not tabulated) | 8,406 | — |
| never-seen-MW72-and-MW99 (`sup_7`) | (all) | 4,112 | — |
| dropped-between-editions (`sup_7`) | (all) | 27 | — |

## Reading

The class is the negative space of Article 21 §3.3: there MW matches the Petersburg homonym
divisions 64–77 % of the time on the deep splits both works carry; here, on splits only the
Nachträge carry, the match fails outright. The inventory inheritance of §3.1 has a precise edge —
it thins exactly at the supplements' newest stratum. The class is disjoint from every prior
missing-candidate pool (0/571 overlap): these are words MW *already heads*, resolved by numbering
rather than by headword absence. Corroboration is strong on two independent axes (DCS 374;
outside-tradition dictionaries 517) and genuinely sparse on a third (only 10/571 pw bodies cite
the MAHĀVYUTPATTI).

## Caveats

1. **Numbering comparability.** MW `<h>` vs pw `<hom>` is unproven 1:1; the count moves within a
   **498–626** band across defensible definitions (main-body max 571 · annexure-inclusive 563 ·
   `<h>`-attribute base 507 · entry-own-marker 498 · MW-headedness not required 626).
2. **Annexure coincidence.** `annexure_covers = yes` (8 rows) is a numbering accident, not
   semantic coverage (`kārin` is the proof — see Method).
3. **Digitization provenance.** Every figure describes the **Cologne digitizations** (`csl-orig`),
   not the printed page; canary `kāritra` (`pw.txt` line 620963, `7-331-d`) reproduces from the
   digitized source alone.
4. DCS coverage bias (texts skew Buddhist/epic; band ≥ 1 ≠ "well attested"); deliberate-exclusion-
   vs-oversight for the Buddhist/Mahāvyutpatti layer remains undecided.

## Reproduction

```sh
python HeadwordLists/mw_unabsorbed_census.py
# in gasyoun/SanskritLexicography; reads csl-orig/v02/{pw,mw,mw72}/… (CSL_ORIG_V02)
# + VisualDCS/dcs_lemma_summary.json + HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv
# ~8 s, stdlib only
```

Frozen machine-readable outputs (committed beside the builder):
[HOMONYM-EXTENSIONS (571 rows, full per-entry table)](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-HOMONYM-EXTENSIONS-16-09-2026.tsv) ·
[POS-CLASS](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-POS-CLASS-16-09-2026.tsv) ·
[ALL-LAYERS](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-ALL-LAYERS-16-09-2026.tsv).
Posted upstream: [csl-corrections#119, comment 5704062630](https://github.com/sanskrit-lexicon/csl-corrections/issues/119#issuecomment-5704062630).
