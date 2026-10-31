# The PD quotation-level unit, and what it does to the twelvefold basis

_Created: 18-10-2026 (H6949) · DeepSeek v4.1 Flash (`deepseek-flash`) via DSH_

PD — *An Encyclopaedic Dictionary of Sanskrit on Historical Principles* (Poona: Deccan
College, 1976–) — is a quotation dictionary: its whole claim to being "on historical
principles" is that every meaning is carried by a numbered, located quotation. The
published measurements of PD so far (H1336 and everything downstream) count **citation
sigla**, never quotations, because the machine text offers no explicit quotation tag and
its obvious-looking unit, the `{#...#}` block, is not one.

This note does three things: it **defines** the quotation unit on the text's own
typographic conventions, **counts** it over the whole machine-readable range
(107,630 entries), and **tests** J. C. Wright's 1978 "twelvefold increase in bulk"
against PWG measured the same way.

Artifacts:

| File | What it is |
|---|---|
| [`data/pd/pd_quotations_by_entry.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_by_entry.tsv) | 107,630 rows — one per entry: blocks, quotations, siglum loci, further references, attestations |
| [`data/pd/pd_quotations_vs_pwg.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_vs_pwg.tsv) | 4,093 rows — one per lemma present in both PD and PWG, with both counts and the ratios |
| [`data/pd/pd_quotations_summary.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_summary.json) | totals, distribution, top-20, the comparison block, input hashes |
| [`scripts/lib/quotation_units.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/quotation_units.py) | the rule itself, shared by both dictionaries |
| [`scripts/pd_quotation_units.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_quotation_units.py) | PD parser → the per-entry TSV |
| [`scripts/pd_quotations_vs_pwg.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_quotations_vs_pwg.py) | the PWG measurement and the join |
| [`tests/forensic/test_quotation_units.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_quotation_units.py) | 10 hand-derived pins on the rule |

## 1. Why the block is not the unit

In the PDScan 2020 machine text (`txt/pd.txt` inside
[pdtxt.zip](https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/downloads/pdtxt.zip),
55,122,076 B, 107,630 `<L>` entries) Sanskrit is wrapped in `{#...#}` SLP1 blocks. Counting
those blocks overcounts quotations in three independent ways:

1. **The headword is a block.** 107,620 of the 107,630 entries open with one; in 107,479
   it is literally `<k1>`/`<k2>`, and the residue are OCR and variant forms
   (`agnikarzu, agnikarzU`, `agnizwi(? zWi)kAdAna`).
2. **Etymologies are blocks.** `akāmatas` opens
   `({#a#} + {#kAmatas#})` — two morphemes, no citation, no quotation.
3. **One printed quotation is routinely split across blocks at a line wrap.**
   `akāmataḥ` alone has `{#kAmato'kAmato vApi na kftaM niyatArcanam.kenacidviGnadozeRa#}`
   followed by `{#mayA yatparameSvara#}` — one passage, two blocks.

The block total is 621,100; the worst single entry (`anya`, `L=97714`) holds **3,904
blocks** — the figure the handoff flagged — while carrying 2,329 quotations. A block count
is therefore an upper bound on nothing in particular; 78.4 % of all blocks do sit inside
quotations, and the remaining fifth is headwords, morphemes and cross-referenced forms.

## 2. The unit

Three nested units; only the middle one is counted.

| Unit | Definition | Corpus count |
|---|---|---|
| **block** | one `{#...#}` SLP1 payload | 621,100 |
| **quotation** | a maximal run of consecutive blocks separated **only by whitespace**, immediately followed by a citation marker | **302,442** |
| **attestation** | one citation marker, plus each further reference that inherits a siglum after a `;` | 419,890 |

The citation marker differs by dictionary only: **PD** puts its siglum and locus inline in
roman type (`ManuSm. 2. 181`), **PWG** wraps the locus in an `<ls>…</ls>` tag. The same
rule therefore measures both, which is what makes §4 a like-for-like comparison rather
than a juxtaposition.

Details that change counts and are therefore pinned by test:

- **Block 1 is never a quotation** — it is the headword; a boundary is forced after it.
- **A gap joins a run only if it is whitespace.** `({#a#} + {#kAmatas#})` and
  `{#q#} {%gloss%} Siglum` are boundaries, not joins.
- **A siglum ends in a period, either bare (`ManuSm.`) or inside its qualifier
  (`PāñcaRā(Nā.)`);** a second form puts the qualifier after the period
  (`VīraMi. (Saṃskāra.)`). Both count once, as one siglum.
- **Lowercase roman numerals are locus numbers, not sigla** (`SuśruS. iii. 3. 15`,
  `SkandP. iii(3). 3. 131`, `vii (1). 98. 21`). Uppercase ones are left alone, because
  `M.`, `V.`, `X.` are real abbreviations.
- **A sense marker `{@n@}` ends the citation tail** — what follows belongs to the next
  sense.
- **Further references are attestations.** The Reader's Guide (X.v) allows one siglum to
  carry a run of further loci — `ManuSm. 2. 181; 9. 242; 11. 45;` is one quotation with
  three attestations. PWG's `<ls>` tags count each locus separately, so PD's
  continuations must be counted too or the comparison silently understates PD by 35,673
  loci.

Scope, unchanged from every other PD number: **letter *a* only, up to ~*apaca-*** (the
fascicles issued 1976–2008). Every figure below is a floor on the dictionary, not a
description of it.

## 3. What the corpus says

Over 107,630 entries and 554,243 printed lines:

| Metric | Value |
|---|---:|
| quotations | **302,442** |
| attestations | **419,890** (384,217 siglum loci + 35,673 further references) |
| blocks | 621,100 |
| blocks per quotation | 2.05 |
| quotations per printed line | 0.55 |
| median quotations per entry | 1 |
| p90 / p99 / max | 4 / 30 / 2,329 |
| entries with no quotation at all | 1,686 (1.6 %) |

The 1,686 quotation-free entries are the cross-reference and formal entries — the
dictionary's own internal pointers, not failed measurements.

The 384,217 siglum loci are an **independent corroboration** of H1336's 398,359 citation
occurrences: two different definitions of "a citation sits here" agreeing to 96.5 % on the
same text. The 14,142-locus difference is the sigla H1336 counted anywhere in the entry
but that no quotation tail here covers.

### Top 20 entries by quotation count

| # | `L` | page | headword | quotations | attestations | printed lines |
|---:|---:|---|---:|---:|---:|---:|
| 1 | 97714 | 8-3866a | anya | 2,329 | 3,458 | 2,796 |
| 2 | 9424 | 1-0329a | agni | 1,503 | 1,926 | 1,424 |
| 3 | 106685 | 8-4266b | ap | 1,463 | 2,526 | 1,554 |
| 4 | 96442 | 7-3813b | anna | 967 | 1,500 | 1,048 |
| 5 | 90876 | 7-3549b | antar | 856 | 1,708 | 1,070 |
| 6 | 90880 | 7-3559a | antara | 742 | 1,317 | 905 |
| 7 | 99041 | 8-3951a | anyathā | 697 | 835 | 897 |
| 8 | 91942 | 7-3618a | antarikṣa | 601 | 1,154 | 651 |
| 9 | 70339 | 5-2628b | anu | 596 | 1,143 | 704 |
| 10 | 91398 | 7-3588a | antarā | 544 | 820 | 672 |
| 11 | 98921 | 8-3941a | anyatra | 531 | 701 | 595 |
| 12 | 95623 | 7-3775b | aṇḍa | 497 | 813 | 610 |
| 13 | 89506 | 7-3491a | anta | 495 | 1,145 | 615 |
| 14 | 105002 | 8-4169a | anvaya | 485 | 634 | 631 |
| 15 | 77807 | 6-2979b | anubhū | 475 | 630 | 553 |
| 16 | 48533 | 3-1691b | ādhī | 467 | 661 | 528 |
| 17 | 25 | 1-0003a | aṃśa | 449 | 520 | 571 |
| 18 | 106329 | 8-4242a | anvita | 445 | 508 | 521 |
| 19 | 92218 | 7-3636b | antareṇa | 424 | 858 | 534 |
| 20 | 54601 | 4-1964a | ananta | 405 | 589 | 454 |

The largest entries are the productive bases (`anya`, `agni`, `ap`, `antar`), where the
dictionary treats whole compound families under one lemma — the same design that makes the
`anya` entry 2,796 printed lines long.

## 4. PD against PWG, same unit, same rule

PWG (Böhtlingk–Roth, *Sanskrit-Wörterbuch*) over its whole alphabet: 123,366 entries,
**801,788 raw `<ls>` tags**, of which **729,719 close a quotation** and are the unit's
attestations, 329,623 quotations. The two counts are different objects and this report
earlier used one word for both; the split is measured by
[`scripts/pwg_quotation_linked_tags.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pwg_quotation_linked_tags.py)
and pinned in [`data/pd/pwg_quotation_linked_tags.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pwg_quotation_linked_tags.json):
the 72,069 tags that do not close a quotation (8.99 % of the raw count) sit in 33,577
entries and are references, not citations.

**Aggregate.** PD's letter-*a* fragment alone carries **419,890 attestations = 52.4 % of
PWG's entire-alphabet 801,788 raw tags — and 57.5 % of the 729,719 that close a
quotation**, and **302,442 quotations = 91.8 % of PWG's 329,623** — for
the ~4–6 % of the alphabet PD has covered. Whatever else the twelvefold claim means, the
dictionary is not merely denser per headword; it has, inside its first letter, already
quoted nearly as many passages as the finished Petersburger Wörterbuch quotes in its
entirety.

**Per lemma.** 4,093 lemmas occur in both. Over those:

| Measure | Value |
|---|---:|
| aggregate PD : PWG attestations | **8.55 ×** (157,480 : 18,423) |
| aggregate PD : PWG quotations | **9.53 ×** (97,413 : 10,225) |
| per-lemma attestation ratio, median | **4.0 ×** |
| mean / p25 / p75 | 8.97 × / 2.0 × / 9.75 × |
| lemmas at ≥ 12 × | 710 (19.7 %) |
| lemmas below parity (< 1 ×) | 340 (8.3 %) |

Distribution of the per-lemma attestation ratio: 340 below 1×, 967 at 1–3×, 1,586 at
3–12×, 710 at ≥12×.

## 5. The twelvefold basis: what survives and what does not

Wright 1978 (*BSOAS* 41(2), 388–389) puts PD's `akāmataḥ` against PW's: "Three lines of
print in the PW were used to inform us of six attestations in Manu … In the new
dictionary, 47 lines add, besides much similar material, some attestation of
*akāma-tah* 'without desire'", and asks "can one really welcome wholeheartedly a
**twelvefold increase in bulk**". Every element of that is now checkable on the text.

| Measure at `akāmataḥ` | PW/PWG | PD | ratio |
|---|---:|---:|---:|
| printed lines | 3 (Wright's count of PW) | 47 | **15.7 ×** |
| quotations | 2 | 31 | **15.5 ×** |
| attestations | 6 | 75 | **12.5 ×** |

**Verdict: the twelvefold basis holds as an order of magnitude and is best measured on
attestations; it does not hold as a typical per-headword ratio.**

1. At the entry Wright chose, the multiple is real and reproducible from the machine text
   of both dictionaries: **12.5 × on attestations**, 15.5 × on quotations, 15.7 × on the
   printed lines he himself counted. His "twelvefold" is the conservative end of a
   12–16 × band, not a figure pulled from bulk alone.
2. Across the 4,093 shared lemmas the **aggregate** multiple is 8.5 × on attestations and
   9.5 × on quotations — the same order of magnitude, slightly under twelve.
3. But the **median** lemma is only 4.0 × denser, and 8.3 % of shared lemmas carry *fewer*
   attestations in PD than in PWG. Twelvefold is the story of the heavy entries and of the
   aggregate, not of the typical headword. A sentence of the form "PD quotes twelve times
   more per headword than PWG" is wrong; "PD's letter-*a* fragment alone holds 52 % of
   PWG's entire attestation mass, and where both dictionaries treat a lemma PD carries
   8.5 × the attestations (median 4 ×)" is what the text supports.

### The omission Wright reported is still there

Wright's second complaint about that entry is specific: "The sixth and last of the PW
attestations from Manu (11.127) has been omitted." The machine text confirms it exactly.

- PWG, `akāmatas` (`L=99`): `M.2,181` · `M.9,242` · `M.11,45` · `M.11,46` · `M.11,89` ·
  **`M.11,127`** — six.
- PD, `akāmatas` (`L=1531`, 1-0067a): ManuSm. `2.181` · `9.242` · `11.45` · `11.46` ·
  `11.89` — **five, and 11.127 is absent.**

Half a century after the review, in a text digitised from a different printing, the
missing sixth Manu attestation is still missing. That is a small thing to measure and a
useful one: it shows the quotation-level unit keys on the same evidence a reviewer's eye
uses, not on a proxy for it.

## 6. Reproduce

```sh
# PD: stage the text once (SanskritSpellCheck, detectors/get_external_source.py PD), then
python scripts/pd_quotation_units.py --pd "$PD_TXT"
python scripts/pd_quotations_vs_pwg.py --pd "$PD_TXT" --pwg ../csl-orig/v02/pwg/pwg.txt
python -m pytest tests/forensic/test_quotation_units.py -q
```

Input hashes are recorded in `pd_quotations_summary.json` (`source.sha256` for PD,
`comparison_pwg.inputs.pwg_sha256` for PWG), so the two sides of the comparison are
pinned to the revisions they were measured on.

## 7. Caveats

- **Scope.** Letter *a* to ~*apaca-* only, 1976–2008 fascicles. The printed record has
  since reached Vol. 35 / 6,056 pp, still inside *a*; that material is not in the text and
  not in any number here.
- **Unit boundary cases.** A quotation whose Sanskrit is interrupted by an italic gloss or
  a tag is counted as two runs when the interruption is not pure whitespace; this is
  conservative in both directions and affects entries with intra-quotation glosses. The
  shared rule makes the two dictionaries equally affected, which is what the comparison
  needs.
- **Siglum parsing.** The rule is typographic (`Letter.` + locus), not a lookup against
  the printed Abbreviations of Books Quoted. A siglum absent from the AOB would still be
  counted here; the AOB join is H6720's separate measurement.
- **PWG's `<ls>` count** here is the raw tag count in `pwg.txt` (801,788, verified with
  `grep -o '<ls' | wc -l`). Of those, 729,719 close a quotation and are the unit's
  attestations; the remaining 72,069 are references that do not close a block run
  (`scripts/pwg_quotation_linked_tags.py`). Any ratio that divides PD's 419,890 by
  PWG's mass must name which of the two it uses — 52.4 % against the raw tags, 57.5 %
  against the quotation-linked ones. The committed citation graph
  ([`data/citations/ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv))
  totals 536,172 for PWG because it filters non-text markers and unresolved targets — a
  different question, answered elsewhere.
- **PD printed lines** are machine-text file lines (one `<div n="lb">` per printed line),
  which is why `akāmataḥ`'s 47 agrees with the printed count. PWG's machine text has no
  line-break markup (one long line per entry), so no PWG line ratio is reported; PW's
  three printed lines come from Wright, not from the text.

_Dr. Mārcis Gasūns_
