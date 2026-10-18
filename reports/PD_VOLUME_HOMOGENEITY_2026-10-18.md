# H6947 — PD volume-level homogeneity: entry size, blocks and source marking across the 35 fascicle-volumes

_Created: 18-10-2026 (H6947) · DeepSeek v4.1 Flash (`deepseek/flash`)_

**Verdict.** The 18-10-2026 three-volume spot check extends to the whole
machine-readable range without a surprise in entry size: the **median entry is
3 printed lines in every one of the 24 measured fascicle-volumes and in all 8
bound volumes**. The mean is not the 4.4–5.7 range the spot check reported — that
was a three-volume sample; over the full text it runs **4.36–6.21 lines by bound
volume** and **4.22–7.56 by fascicle**.

The marking share does fall, from **2.06 % in vol. 1 to 0.39 % in vol. 8**, but
it is **not a clean step after vol. 6**: the pre-v7 average is **1.94 %**, v7 is
**0.88 %**, v8 is **0.39 %**, and the fascicle series is non-monotonic (7.2 =
1.88 %, 8.3 = 0.99 % against 7.1 = 0.53 %, 8.1 = 0.22 %, 8.2 = 0.17 %).

**On the machine text alone the fall is editorial/content, not a conversion
artefact** (medium-high confidence): the cheap conversion signatures are absent
— general bracket use is stable at 11–17 % of entries, long source brackets are
29 in the whole corpus (1 in v7, 0 in v8), OCR near-misses of the seven source
sigla are 3 in the whole corpus and none in v7/v8, and the fall survives the
uncapped rule. What the text cannot see is the printed page: a print check of
one v7 and one v8 page is the falsification test, specified in §7.

Artifacts:

| File | What it is |
|---|---|
| [`data/pd/pd_volume_homogeneity.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_volume_homogeneity.tsv) | 35 ledger rows (24 measured, 11 print-only): entries, mean/median lines, chars, blocks, H6949 quotations, marking share and source breakdown |
| [`data/pd/pd_volume_homogeneity_bound.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_volume_homogeneity_bound.tsv) | the 8 measured bound volumes, same measures |
| [`data/pd/pd_volume_homogeneity.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_volume_homogeneity.json) | totals, H6942/H6949 canaries, source decomposition and the diagnostics in §6 |
| [`data/pd/pd_publication_ledger.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_publication_ledger.tsv) | the Deccan College ledger transcription: 35 rows, year, general editor, opening/closing entry, pp |
| [`data/pd/pd_publication_ledger.meta.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_publication_ledger.meta.json) | ledger source URL, bytes and SHA-256, plus the known quirks |
| [`scripts/pd_volume_homogeneity.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_volume_homogeneity.py) | parser, ledger join, TSV/JSON writer, `--check` |
| [`scripts/lib/pd_marked_sources.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/pd_marked_sources.py) | the H6942 bracketed-source rule, shared |
| [`tests/forensic/test_pd_volume_homogeneity.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_pd_volume_homogeneity.py) | hand-derived pins on the rule and the ledger |

## 1. Scope and the ledger join

The 35 rows are the Deccan College ledger's own fascicle-volumes: 1.1–8.3
(1976–2008), 9.1–9.3 (2009–2011), 10.1 = Vol. 28 (2012), and Vols 29–35
(2013–2019), ending at p. 6,056. The Cologne PDScan 2020 machine text carries
page codes `1-0001a` through `8-4327a`, i.e. **pp. 1–4,327 = ledger rows
1.1–8.3**. The ledger's 8.3 close is p. 4,328, one page beyond the text. Rows
9.1–35 are print-only and carry no measurements in the TSV.

| ledger rows | years | general editor(s) | pp | in the machine text |
|---|---|---:|---:|---|
| 1.1–8.3 | 1976–2008 | Ghatage, S.D. Joshi, Gandhe/Ranade, Ranade/Bhatta, Bhatta | 1–4,328 | **measured** (pp. 1–4,327) |
| 9.1–9.3 | 2009–2011 | Bhatta; Bhatta/Sathe | 4,329–4,808 | print-only |
| 10.1 (= Vol. 28) | 2012 | Sathe | 4,809–5,008 | print-only |
| 29–32 | 2013–2016 | Sathe | 5,009–5,708 | print-only |
| 33–35 | 2018–2019 | P.P. Joshi | 5,709–6,056 | print-only |

Ledger quirks, recorded rather than silently repaired: 5.3's range overlaps 5.2
by three pages (the parser assigns 2,687–2,689 to 5.2 by first match); 6.1 starts
at p. 2,889, leaving p. 2,888 unassigned; Vol. 33 repeats Vol. 32's
5,609–5,708 range. None of these touches the measured aggregates beyond three
pages in fascicle 5.2.

## 2. Definitions and canaries

The unit is the `<L>…<LEND>` entry. **Printed lines** are body lines between
`<L>` and `<LEND>` (the H6949 definition, so the two reports agree); **chars**
are the body characters after joining lines and removing `<div n="lb">`;
**blocks** are `{#...#}` SLP1 blocks (the H6949 block unit); **quotations** are
the H6949 quotation unit. A **marked entry** is an entry with at least one
bracketed dictionary source under the H6942 capped rule (`[DBHS]`, `[PW]`,
`[APTE]`, `[MW]`, `[VISVA]`, `[NT]`, `[VAC]`; 40-character cap; the two DBHS
gloss exclusions).

The same parser reproduces both locked baselines on the same text:

| canary | expected | measured |
|---|---:|---:|
| H6942 entries | 107,630 | **107,630** |
| H6942 marked entries | 1,801 (1.67 %) | **1,801** |
| H6942 marks | 1,956 | **1,956** |
| H6942 marks by source | DBHS 852, PW 399, APTE 264, MW 245, VISVA 101, NT 84, VAC 11 | **identical** |
| H6949 blocks | 621,100 | **621,100** |
| entries unassigned to a ledger row | 0 | **0** |

## 3. Entry size is homogeneous at the median

Median lines = **3.00 in every measured fascicle and every bound volume**; median
blocks = **3.00** and median quotations = **1.00** everywhere. The mean moves
with the alphabet, not with a volume policy.

| bound vol. | fascicles | years | entries | lines mean/median | chars mean/median | blocks mean/median | quotations mean/median |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 1.1–1.3 | 1976–78 | 20,748 | 4.48 / 3.00 | 338.69 / 197.00 | 5.10 / 3.00 | 2.50 / 1.00 |
| 2 | 2.1–2.3 | 1979–81 | 22,446 | 4.36 / 3.00 | 326.63 / 188.00 | 5.12 / 3.00 | 2.55 / 1.00 |
| 3 | 3.1–3.3 | 1982–89 | 11,288 | 5.51 / 3.00 | 419.00 / 218.50 | 6.17 / 3.00 | 3.01 / 1.00 |
| 4 | 4.1–4.3 | 1990–92 | 11,565 | 5.46 / 3.00 | 411.07 / 231.00 | 5.88 / 3.00 | 2.69 / 1.00 |
| 5 | 5.1–5.3 | 1994–97 | 9,836 | 5.81 / 3.00 | 442.50 / 225.00 | 6.40 / 3.00 | 3.12 / 1.00 |
| 6 | 6.1–6.3 | 1998–2003 | 9,828 | 6.21 / 3.00 | 481.54 / 234.00 | 6.78 / 3.00 | 3.29 / 1.00 |
| 7 | 7.1–7.3 | 2003–05 | 11,498 | 5.23 / 3.00 | 403.26 / 213.00 | 5.71 / 3.00 | 2.78 / 1.00 |
| 8 | 8.1–8.3 | 2006–08 | 10,421 | 5.75 / 3.00 | 449.43 / 217.00 | 6.49 / 3.00 | 3.18 / 1.00 |

The spot check's **median 3 lines in every volume is confirmed** on the full
range. Its **mean 4.4–5.7** was a three-volume sample: the full bound-volume
range is 4.36–6.21, and the fascicle range is 4.22 (7.1) to 7.56 (8.3). The
long-entry stretches are 3.2, 5.2, 6.2–6.3, 7.2 and 8.3; 8.3 is the longest
(mean 7.56 lines, 610 chars, 8.95 blocks).

## 4. Marking: the fall is real, but not a volume-step

| bound vol. | entries | marked | share | marks | DBHS | PW | APTE | MW | VISVA | NT | VAC | marks/1,000 lines |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20,748 | 428 | **2.06 %** | 490 | 106 | 131 | 136 | 74 | 6 | 30 | 7 | 5.27 |
| 2 | 22,446 | 393 | 1.75 % | 449 | 63 | 145 | 95 | 93 | 10 | 40 | 3 | 4.59 |
| 3 | 11,288 | 167 | 1.48 % | 179 | 74 | 44 | 19 | 31 | 6 | 4 | 1 | 2.88 |
| 4 | 11,565 | 209 | 1.81 % | 220 | 145 | 41 | 5 | 22 | 6 | 1 | 0 | 3.49 |
| 5 | 9,836 | 201 | 2.04 % | 205 | 156 | 23 | 6 | 15 | 4 | 1 | 0 | 3.59 |
| 6 | 9,828 | 261 | **2.66 %** | 264 | 208 | 9 | 2 | 7 | 37 | 1 | 0 | 4.33 |
| 7 | 11,498 | 101 | **0.88 %** | 107 | 81 | 3 | 0 | 0 | 18 | 5 | 0 | 1.78 |
| 8 | 10,421 | 41 | **0.39 %** | 42 | 19 | 3 | 1 | 3 | 14 | 2 | 0 | 0.70 |

The fascicle series shows why "after vol. 6" is a misleading cut:

| fascicle | 6.1 | 6.2 | 6.3 | 7.1 | 7.2 | 7.3 | 8.1 | 8.2 | 8.3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| marking share | 2.51 % | **3.25 %** | 2.25 % | 0.53 % | **1.88 %** | 0.55 % | 0.22 % | **0.17 %** | 0.99 % |

7.2 sits under the same editor (V.P. Bhatta) as 7.1 and 7.3 and is 3.5× their
share; 8.3 is 4.6× 8.2. A volume-level editorial switch cannot produce that
pattern, and the fall is already visible in 3.1 (0.98 %) and 2.3 (1.19 %) before
recovering in 5–6. The **source mix** also moves: DBHS rises from 63 marks in
vol. 2 to 208 in vol. 6 and then falls to 81 and 19; PW/APTE/MW fall from 341
marks in vol. 1 to 7 in vol. 8; VISVA persists into v8 (14 marks). This is a
change in which sources the later fascicles acknowledge, not one uniform
"marking" behaviour.

The exact spot-check endpoints are reproduced: vol. 1 = 428/20,748 = **2.06 %**
(the spot check printed 2.07 %, 0.01 points above the H6942-rule value), vol. 8 =
41/10,421 = **0.39 %**. The pre-v7 aggregate is **1.94 %** (1,659/85,711), not
2.07 %; v7+v8 = **0.65 %** (142/21,919).

## 5. The confound, named

The volume-level share is a ratio between a **source-specific editorial act**
(an explicit bracketed acknowledgement) and **all entries**. Its movement
confounds three things:

1. **Which source dictionaries the later alphabet needs to acknowledge.** DBHS
   is 44 % of all marks and is concentrated in the earlier stretches; PW, APTE
   and MW also cluster early. The later fascicles may simply have less to
   attribute.
2. **Whether the editorial team kept the bracket convention.** The convention
   could have been relaxed after 6.3 without any change in what was inherited.
3. **Whether the 2020 conversion preserved the exact sigla.** This is the only
   conversion hypothesis left after §6, and it is the one a print check can
   falsify.

The data cannot separate (1) from (2): both are "editorial/content" against the
mission's dichotomy, and both predict the same machine-text pattern. They can be
separated from (3), and §6 does so. The fall is therefore **editorial/content,
not a conversion artefact**, with the print check as the one remaining
falsifier.

## 6. What the fall is not

| conversion hypothesis | test | result |
|---|---|---|
| brackets were lost in later scans | share of entries with any `[...]` bracket | 15.10, 12.69, 13.90, 14.68, 15.44, 17.40, 11.26, 12.19 % by volume — no collapse |
| the 40-character cap suppresses later marks | source-leading brackets longer than 40 chars | **29** in the whole corpus: 3, 9, 11, 3, 1, 1, 1, 0 by volume |
| the DBHS gloss exclusion suppresses later marks | excluded `[DBHS …]` gloss brackets | **2** in the whole corpus, both in vol. 1 |
| OCR garbled the sigla | near-miss source-like brackets | **3** in the whole corpus (all in vols 1–2); **none in v7/v8** |
| longer entries dilute the per-entry share | marks per 1,000 printed lines | 5.27 → 0.70; the fall is steeper per unit text, not an entry-length artefact |
| the capped rule is doing the work | uncapped marked entries | 1,804 vs 1,801; the volume pattern is unchanged |

The general-bracket control is the important one: the conversion is still
producing `[Loc.]`, `[Inst.]`, `[irr.]`, page markers and editorial brackets in
v7/v8 at the same density as earlier. A conversion that preserved brackets but
selectively dropped only the seven dictionary sigla is possible; it is not
supported by any near-miss evidence in the text, and it is exactly what the
print check tests.

## 7. The print check that would settle it

The machine text is zero-mark on both chosen pages while still carrying
non-source brackets, so the check is one-sided: a printed source mark falsifies
the editorial reading.

| volume | page | machine text | what to count in print |
|---|---:|---|---|
| v7 | **p. 3,525** (both columns) | 29 entries, 126 lines, **0 source marks**, 10 non-page bracket pairs (`[Loc.]`, `[Inst.]`, …) | any `[DBHS]`, `[PW]`, `[APTE]`, `[MW]`, `[VISVA]`, `[NT]` or `[Vācas.]` |
| v8 | **p. 3,989** (both columns) | 36 entries, 129 lines, **0 source marks**, 16 non-page bracket pairs (`[irr.]`, `[Inst.]`, …) | the same seven sigla |

**Decision rule.** If either printed page carries a bracketed dictionary
source, the machine text has lost marks and the fall is (at least partly) a
**conversion artefact**; the v7/v8 shares in §4 must then be treated as floors,
and the H6942 1.67 % baseline as volume-dependent. If both printed pages carry
only the grammatical/editorial brackets that the machine text also carries, the
absence is **editorial/content**, and the volume series in §4 stands as a
description of PD's explicit acknowledgement practice.

To calibrate the comparison, also open one page where the machine text does
carry a mark — e.g. v7 p. 3,529 (7.2 opens, 1.88 % share) or v8 p. 4,169 (8.3
opens, 0.99 %) — and confirm that print and text agree on the marks that are
present. That control distinguishes "print has no marks" from "the checker is
looking at the wrong place".

## 8. Reproduction

```bash
python3 scripts/pd_volume_homogeneity.py --pd /path/to/pdtxt/txt/pd.txt
python3 scripts/pd_volume_homogeneity.py --check --pd /path/to/pdtxt/txt/pd.txt
```

`--check` recomputes both TSVs and the JSON, verifies the H6942 (1,801 entries /
1,956 marks / source split) and H6949 (621,100 blocks) canaries, and exits 0
with `PASS`. The source is the Cologne PDScan 2020 `pdtxt.zip` (19,018,957 B,
SHA-256 `b3b9c9ffc82219e204ce83143acd30cd6b5343593dcb3bc7649e8cea1cda30cc`;
member `txt/pd.txt`, 55,122,076 B, SHA-256
`4ee75e6619ee2bd86a331586bb922101e0ae090f9edd981752cfac36ed724442`). The ledger
PDF is fetched and hashed but not committed; its transcription is pinned by
`pd_publication_ledger.meta.json`.

## 9. Limits

- **Letter *a* only, through 2008.** The 11 print-only ledger rows (9.1–35,
  2009–2019) are outside the machine text. Every measured number is a floor on
  the dictionary and a description of the 2020 text, not of the 2019 print.
- **Marking is a floor.** The H6942 rule counts explicit bracketed sources only;
  silent inheritance is H6948's question. 1.67 % is not an inheritance rate.
- **The ledger has three print quirks** (5.2/5.3 overlap, the p. 2,888 gap, the
  Vol. 33 repeated range); they are recorded in the meta and affect only the
  three-page 5.2/5.3 boundary.
- **The print check is not performed here.** It is specified, with pages and a
  decision rule, because it needs the printed fascicles; the machine text alone
  cannot see whether the printer's bracket was there.

_Dr. Mārcis Gasūns_
