# PD knowledge index — parity report, 24-10-2026

_Created: 24-10-2026 · Scope: the Poona Dictionary's knowledge surface — public page, canon ledger, atlas chapter, gate — and what remains before it can be called research-grade · Status: 8 of 10 checks pass, two open with named owners._

**What this report is.** On 24-10-2026 the PD knowledge page was a private working document with a
gated number set, five silent canon denominators, no human-verified claim, and no place in the
dictionary atlas. This report records the programme that changed that, the numbers it produced, and
— with equal care — the three things it did **not** do.

## 1. What shipped

| Unit | Artifact | Number | Where |
|---|---|---|---|
| Gate | `MISSING-OWNER` separated from `UNMAPPED`; owner-path resolution live; three tests | 489/489, exit 0; negative control 16 MISSING-OWNER / 473 PASS / exit 1 | the working repository |
| Canon ledger | [`pd_canon_ledger.tsv`](../data/pd/pd_canon_ledger.tsv) + [§9](PD_DCS_CORPUS_COVERAGE_2026.md) of the coverage report | the two printed counts differ by **562 rows (38.3 %)**; Index→AOB join **981 / 1,622 = 60.5 %** | this repository |
| Public page | [`PD_KNOWLEDGE.md`](https://github.com/sanskrit-lexicon/PD/blob/main/PD_KNOWLEDGE.md) | 13 / 13 sections labelled; **0** links into private repositories; **0** handoff IDs | PD repository |
| Atlas chapter | [`src/dicts/pd.md`](../src/dicts/pd.md) | **23.2×** denser than PWG on the covered span; median **4.0×** attestations on the 4,093 shared lemmas | this repository |
| This report | here | — | this repository |

The gate's `MISSING-OWNER` class exists because the two failures need different repairs: *"no spec
owns this number"* is a page defect, *"the owner moved"* is a bookkeeping defect. A red run on
24-10-2026 was first read as the former and was in fact neither — the checkout was two commits behind
`origin/main`. That correction is recorded in the parity report's §18; the lesson is that a shared
checkout is not evidence.

## 2. The canon finding

Five bases had been quoted for the same 118 covered works, each in a document that did not say which
base it used. They are now derived, labelled and checked in one table:

| Base | Rows | 118 / base |
|---|---:|---:|
| AOB entry-like lines (structural) | 1,476 | 7.99 % |
| AOB rows, repeated headers removed | 1,469 | 8.03 % |
| AOB print census | 1,464 | 8.06 % |
| AOB pass-1 parse (not reproducible) | 1,419 | 8.32 % |
| AOB re-parse, raw entries | 1,517 | 7.78 % |
| Edition-level inventory | 1,437 | 8.21 % |
| Clean-subset edition rows — a floor | 1,118 | 10.55 % |
| **Index of Works, all rows** | **2,031** | **5.81 %** |
| Index rows printing a siglum | 1,622 | 7.27 % |
| Index rows with no siglum | 409 | — |

The two printed counts — **1,469** and **2,031** — differ by **562 rows**. Of the 1,622
siglum-bearing Index rows, **981** find an AOB row and **641** do not; **497** AOB sigla never appear
in the Index. The rule now enforced: no percentage without its base in the same row, and 1,118 is a
floor that must never be quoted as the declared canon.

## 3. The atlas chapter's two registers

The chapter is the atlas's first **unfinished** dictionary, and it says so instead of pretending
otherwise. The comparative register measures density on the span PD covers: **23.2×** PWG, 13.4× MW,
19.4× AP, with PD's first letter holding as many lemmas as the entire Petersburg dictionary
(104,959 against 106,082). The fragment register measures stability across PD's own production: the
median entry is **3 printed lines in every one of the 24 measured volumes**, while acknowledged
inheritance thins from **2.06 % to 0.39 %** of entries — non-monotonically, and not a conversion
artefact.

## 4. The parity checklist

| # | Check | State | Closes with |
|---|---|---|---|
| 1 | Public page resolves | **pass** | — |
| 2 | A DOI for the data | **pass** | [`10.5281/zenodo.23613057`](https://doi.org/10.5281/zenodo.23613057) (release v0.21.0) |
| 3 | Every section evidence-labelled | **pass** | 13 / 13 |
| 4 | At least one human-`reviewed` claim | **open** | 200-row double-coded κ study, second coder human |
| 5 | Canon ledger with labelled bases | **pass** | `--check` green |
| 6 | PD is an atlas chapter | **pass** | `npm run build` exit 0 |
| 7 | Edition availability by citation mass | **open** | the campaign ladder's first unit |
| 8 | Every number gated | **pass** | 489 / 489 |
| 9 | Mirror in sync | **pass** | 24-10-2026 |
| 10 | A published report | **pass** | this file |

**Score: 8 / 10.** The two open rows are the honest part of the report, not an appendix.

## 5. The DOI — minted after the report

**Resolved, 24-10-2026 08:19Z.** Release v0.21.0 was cut after the ledger and the chapter merged and minted **[10.5281/zenodo.23613057](https://doi.org/10.5281/zenodo.23613057)** (version 0.21.0; concept DOI [10.5281/zenodo.21419691](https://doi.org/10.5281/zenodo.21419691)). Checklist row 2 is now pass, and the score above reads 8/10.

The three facts below are why the DOI could not be minted *first*, and they remain the reasons the order matters:

The repository's Zenodo machinery mints a DOI **per tagged release** (concept DOI
`10.5281/zenodo.21419691`; the v0.20.0 version DOI is `10.5281/zenodo.23536487`). Three facts made a deposit *before* the merge wrong or premature:

1. **Ordering.** A release cut now would not contain the canon ledger or the PD chapter, both still
   in open pull requests. A DOI that resolves to a tree without the artifacts it is cited for is
   worse than no DOI.
2. **Licence.** The deposit is CC BY-SA 4.0, while the PD machine text it derives from is CC BY-NC-SA
   3.0. Whether the siglum-level join tables are a derivative work or uncopyrightable facts is a
   rights call, not a build step.
3. **Version drift.** `CITATION.cff` says 0.20.0 while `package.json` says 0.18.0 — a release would
   have to settle which is true first.

**What happened:** the ledger and the chapter merged (24-10-2026), one release was cut, and the
version DOI was minted — items 1 (ordering) and 3 (version drift) are closed by that order, not argued
away. **Item 2 is not closed:** v0.21.0 ships under the repository's existing CC BY-SA 4.0, and whether the
siglum-level PD join tables are a derivative of the CC BY-NC-SA 3.0 machine text remains an open
rights question. **Ruled 24-10-2026:** no standalone PD deposit and no separate licence — the atlas's CC BY-SA 4.0
stands for these tables. The rights question is recorded, not reopened.

## 6. What this programme does not claim

- **No peer review.** The report route makes the work citable and checkable, not refereed. The
  checklist's row 4 is the gap that a referee would press hardest on.
- **No κ.** The 398,359-occurrence instrument still has no inter-annotator control; it is named on
  the public page rather than implied away.
- **No availability number.** What share of PD's 419,890 attestations sit on a machine-readable
  edition is still unmeasured; it is the campaign ladder's first unit, because it is the number that
  would make the citation apparatus usable rather than merely counted.
- **No browser verification of the chapter's charts.** `npm run build` proves syntax and data
  resolution; it does not prove every mark draws.

## 7. Reproduce

```sh
python3 scripts/pd_canon_ledger.py --check     # 14 rows, 0 drift; asserts 118/N against recorded values
npm run build                                  # exit 0; dist/dicts/pd.html emitted
```

The gate and its tests live in the working repository and are not public; the numbers they check are
all present in `data/pd/`.

## Sources

- `data/pd/pd_canon_ledger.tsv` / `.json` — the bases, their 118/N, input SHA-256s.
- `reports/PD_DCS_CORPUS_COVERAGE_2026.md` §8.5 / §9 — the density yardsticks and the canon rule.
- `reports/PD_VOLUME_HOMOGENEITY_2026-10-18.md` — entry size and marking across 24 measured volumes.
- `data/pd/pd_quotations_vs_pwg.tsv` — 4,093 shared lemmas, one quotation rule on both sides.
- [`PD_KNOWLEDGE.md`](https://github.com/sanskrit-lexicon/PD/blob/main/PD_KNOWLEDGE.md) — the public
  knowledge page this programme exists to make citable.

_24-10-2026 — DeepSeek Flash (`deepseek-flash`) via DSH; no earlier number edited, two open rows
left open on purpose (κ and edition availability); the DOI and the chapter closed after first publication._
