# PD vs PWG: breadth of works and loci per work

_H7095 · 19-10-2026 · data: `data/pd/pd_attestation_decomposition.tsv`_

## Question

The committed per-lemma table (`data/pd/pd_quotations_vs_pwg.tsv`) gives an
aggregate attestation ratio of **8.55×** over the 4,093 lemmas both dictionaries
treat, with a median of 4.0×. The split between the two ways PD can be denser —
citing **more distinct works** (breadth) or **more loci per work** (depth) — was
unmeasured. This report measures it on the same quotation unit used for the
committed table.

## Population and reconciliation

All 4,093 shared lemmas; no sampling. PDScan 2020 machine text (107,630 `<L>`
entries) and `csl-orig/v02/pwg/pwg.txt` (123,366 entries), read-only.

| | PD | PWG |
|---|---:|---:|
| Attestations (= loci) | 157,480 | 18,423 |
| Quotations | 97,413 | 10,225 |
| Distinct primary works, raw sigla | 3,186 | 675 |
| Distinct primary works, folded sigla | 2,409 | 644 |

The reconciliation targets are met exactly (`within_tolerance` = true), and
`attestations = loci` holds on both sides because a locus *is* an attestation in
the shared H6949 unit. PWG quotations and attestations also reproduce the
committed `pd_quotations_vs_pwg.tsv` row for row.

**The two distinct-siglum totals must not be confused.** The per-lemma sum of
distinct-siglum counts is larger than the aggregate distinct count, because the
same work recurs under many lemmas. On the raw convention the per-lemma sum is
80,652 (PD) and 10,769 (PWG), against aggregate unions of 3,186 and 675; on the
folded convention it is 80,065 and 10,767 against 2,409 and 644. The per-lemma
sum is reported only for completeness; the breadth ratio uses the aggregate
union, never the sum.

## Conventions

- **PD works.** Only A68 §4.2 class `primary` sigla in
  `data/pd/pd_siglum_families.tsv`; a trailing commentary qualifier is stripped
  to its base work (e.g. `PadmP.(Ra.)` → `PadmP.`). Loci are all 157,480
  attestations, including semicolon continuations.
- **PWG works.** The siglum of each `<ls>` tag counted as a locus: the `n`
  attribute is joined to the payload and the prefix before the first digit is the
  siglum (`<ls n="P. 6,2,">155</ls>` → `P.`).
- **Raw.** No variant merging. This is an upper bound on PD breadth.
- **Fold (headline).** A diacritic/case/punctuation skeleton
  (`fold_siglum`) applied to both sides. It approximates A68 §5.2's
  skeleton-merged count (2,409 here against the ~2,445 estimate there) and is the
  fairer breadth convention, because PD's 4,988 raw sigla contain many
  orthographic variants of the same abbreviation. Even the folded skeleton does
  **not** merge abbreviation families such as `R.` / `Rāmā.`; the residual is
  therefore a lower bound on true PD breadth and an upper bound on depth.

## Decomposition

**Answer, folded convention: of the 8.55×, breadth contributes 3.74× and depth
2.29×.** PD cites 3.74 times as many distinct works over the shared lemmas, and
each cited work carries 2.29 times as many loci. Breadth is the larger factor,
but depth is not negligible: roughly two-fifths of the log-ratio is loci per
work. The identity is exact within rounding:

```
breadth 3.7407 × depth 2.2851 = 8.548011 ≈ 8.55
```

| Aggregate | PD | PWG | ratio |
|---|---:|---:|---:|
| Folded works (union) | 2,409 | 644 | **3.74×** |
| Loci per folded work | 65.3715 | 28.6071 | **2.29×** |
| Loci / attestations | 157,480 | 18,423 | **8.55×** |

The raw convention gives the same qualitative answer, with more of the ratio
attributed to breadth: **4.72× breadth and 1.81× depth** (3,186 / 675 works;
49.4288 / 27.2933 loci per work), again multiplying to 8.548011. So under either
convention breadth exceeds depth; the honest range is breadth 3.74–4.72× and
depth 1.81–2.29×.

### Per-lemma distribution

Medians with IQR, folded convention, over lemmas with a defined denominator:

| Per-lemma ratio | n | median | p25–p75 |
|---|---:|---:|---:|
| Breadth | 3,603 | 3.8× | 1.0–8.1 |
| Depth | 3,396 | 1.15× | 1.0–1.5 |
| Attestations | 3,603 | **4.0×** | 2.0–9.75 |

The attestation median reproduces the committed 4.0× (IQR 2.0–9.75). The raw
convention leaves the breadth median at 3.8× and moves the depth median only to
1.14×. The per-lemma medians are not multiplicative in the aggregate way: median
breadth × median depth (3.8 × 1.15) is not the median attestation ratio (4.0),
which is why the aggregate identity is stated separately from the distribution.

## The 8.3 % below parity

**340 of 4,093 lemmas (8.31%)** have PD below PWG. They are explained by two
different mechanisms, not by a failure of the decomposition:

- **191 lemmas have zero PD attestations** (313 PWG attestations in total). These
  are PD entries that define or cross-refer the lemma but quote nothing — PD's
  quotation practice is not uniform across its entry types. PWG supplies the only
  citations.
- **149 lemmas have PD > 0 but PD/PWG < 1.** This is overwhelmingly a one- or
  two-locus difference: 131 of the 149 differ by at most 2 loci (104 by exactly
  1, 27 by 2). These are small-denominator cases where PWG's one extra citation
  outweighs any breadth difference; they do not reverse the aggregate.

For context, 490 shared lemmas have zero PWG attestations (and therefore no
defined ratio), so the 340 below-parity cases are not an artefact of a tiny
numerator population.

## A68 §6.2

**No change.** The decomposition confirms rather than revises the current
sentence: the aggregate remains 8.55× and the median remains 4.0×. The new
breadth/depth split is additive detail, not a correction, so no paragraph was
inserted into
`Uprava/papers/A68/A68_DCS_REPRESENTATIVENESS_PD_CANON.md` and that file is
untouched.

## Caveats

- PD is measured only on the published letter-*a* fascicules; the shared set is
  the 4,093 lemmas where both dictionaries have an entry.
- Sigla are compared as each dictionary's own citation inventory, not resolved to
  a common work registry. PD's `MahāBhā.` and PWG's `MBH` are two sigla even
  though they denote one work; this affects both sides and is not corrected here.
- PWG `<ls>` tags occasionally name modern/secondary references (e.g.
  `Ind.St.`); they are counted as cited sigla because PWG has no committed §4.2
  class table.
- PD sigla outside the committed class table (183 raw forms over the shared
  set, mostly `comm.`, `cf.`, `pl.`, plus OCR fragments such as `māṇḍP.`) do not
  enter breadth; the measure is conservative for PD. The table also classes the
  single-letter sigla `P.`, `A.`, `B.`, `I.`, `V.`, `X.` as structural, so
  Pāṇini citations stay out of the PD breadth count by the A68 rule.
- The folded convention removes orthographic variants only. Abbreviation-family
  merging (`R.` / `Rāmā.`) would lower the breadth ratio further and raise the
  depth ratio; the raw convention bounds it from the other side.

## Reproduction and verification

```
python3 scripts/pd_attestation_decomposition.py --pd /tmp/txt/pd.txt \
    --pwg /tmp/h6963/csl-orig/v02/pwg/pwg.txt
python3 scripts/pd_attestation_decomposition.py --check --pd /tmp/txt/pd.txt \
    --pwg /tmp/h6963/csl-orig/v02/pwg/pwg.txt
```

`--check` regenerates the TSV and summary, verifies the 157,480 / 18,423
reconciliation and the attestations = loci identity, re-derives every number
pinned above, cross-checks all 4,093 rows against the two committed source
tables, and validates the 20 gold rows in
`tests/forensic/h7095_pd_attestation_decomposition_gold.tsv`.

The handoff names `akAmataH` and `Darma` as gold lemmas. Neither spelling is a
shared `k1`: the A68 anchor is `akAmatas` (PD's SLP1 headword), and `Darma`
(*dharma*) is outside PD's letter-*a* scope; the gold file uses `akAmatas` and
`aDarma` (*adharma*) and labels both.
