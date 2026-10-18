# Printed AOB authority vs harvested PD sigla — reconciliation

_Created: 17-10-2026 (H6720) · updated 18-10-2026 (H6941 printed-text confirmation) · DeepSeek v4.1 Flash (`deepseek-flash`) via DSH_

The PD sigla harvest (`pd_siglum_families.tsv`, 5,106 sigla from PDScan's letter-`a-`
text) and the printed *Abbreviations of Books Quoted* (PD repo `AOB.md`, 42 pp OCR of
the official KoshaSHRI PDF) describe one citation universe from two sides. H6707 joined
every harvested siglum to an AOB title; this pass asks the two questions that join cannot
answer (grill Q6, closing H1336's parked follow-up):

1. **What share of harvested families is present in the printed AOB**, and how much
   citation mass do they carry?
2. **Which printed AOB entries were never exercised under letter `a-`?**

Artifacts: `data/pd/pd_aob_entries.tsv` (printed entry inventory + match),
`data/pd/pd_aob_sigla_reconciliation.tsv` (the discrepancy list),
`data/pd/pd_aob_sigla_reconciliation.json` (aggregates + method + input hashes).
Script: `scripts/pd_aob_sigla_reconciliation.py` (`--check`, `--selftest`).

## Method

- **AOB universe.** One entry per printed row: the siglum opens a backticked cell, and the
  bibliographic tail is **reassembled across OCR wraps** (without that, tails truncate
  mid-word — `Padmapi` / `urana` — and title matching collapses). `## Page N` markers are
  recorded, not boundaries. Parsed: **1,430 entries**, of which **1,423 usable** (7 junk)
  and **1,362 well-formed** (a tail of ≥15 letters, ≥2 words, not starting mid-number);
  61 backticked rows are wrap fragments or garble and are reported, never counted as gaps.
  623 tokens are OCR-merged `Siglum Title` rows (`AllaU. Allopanisad`); 15 rows whose
  siglum the OCR mangled into Devanagari (`श्प, Visnup | urana` for *ViṣṇuP.*) are kept,
  flagged, for the title route.
- **Harvest universe.** `pd_siglum_families.tsv` unchanged: 5,106 sigla, 398,359
  occurrences.
- **Route A — siglum identity.** Casefold + punctuation trim, then a diacritic-free
  skeleton (`MahāBhā.` → `mahabha`). Skeleton matches need ≥3 letters and a unique
  answer; edition-suffixed groups (`RajTa,(Ka.)`, `RajTa.(Jo.)`) answer the bare printed
  `RājTa.` through a base key; one/two-letter sigla match only a clean short form whose
  tail opens a title — without that guard a mangled `A.) Tantrasara…` cell silently
  absorbs the harvested `A.` (6,451 occurrences).
- **Route B — title identity.** The H6707 adjudicated title (non-`census_unmatched` rows)
  against entry tails: skeleton containment ≥12 chars, else a ratio ≥0.85 among
  same-initial, length-comparable entries.
- **Trap.** `MahāBhā.` (Mahābhārata, 9,337) and `MahāBh.` (Mahābhāṣya, 1,934) never share a
  skeleton (`mahabha` vs `mahabh`) and land on different entries (`MahaBha,` / `MahaBh,`,
  both page 18); `--selftest` asserts it.

## Results

### Q1 — share of harvested families present in AOB

| Measure | Families | Share | Occurrences | Mass share |
|---|---:|---:|---:|---:|
| H6707 join claim (frozen) | 3,233 | **63.32 %** | 310,863 | **78.04 %** |
| + H6720 siglum-identity corrections | 3,313 | **64.88 %** | 318,997 | **80.08 %** |
| Entry-located in this pass (independent lower bound) | 2,632 | 51.55 % | 271,784 | 68.23 % |

The join reproduces exactly (63.32 / 78.04 vs the published 63.3 / 78.0). H6720 adds
**80 harvested sigla the join left `census_unmatched` whose siglum equals a printed entry**
(+1.56 pp of families, +2.04 pp of mass): `Yādavā.` (928) → `Yadava,`, `Hastyāyur.` (925),
`TattvSaṃ.` (703), `RāghPāṇ.` (641) → `RaghPan.(Dha.)`, `MediK.` (640), `Bhā.` (479),
`VidhiRa.` (439), `SiddhāLeSaṃ.` (366), `Ekāva.` (344), `Śāk.` (329) … (full list in the TSV,
kind `join_miss_siglum_equal`).

The third row is the honest lower bound: 681 joined sigla (21 %) **cannot be re-located at
entry level from the AOB.md OCR alone** — the H6707 join also drew on the official-PDF
ground truth and a second OCR pass, and many printed cells are OCR-garbled. They are listed
as `join_unconfirmed_at_entry`, never silently dropped.

### Q2 — AOB entries never exercised under `a-`

| | Entries | Share |
|---|---:|---:|
| Well-formed entries | 1,362 | 100 % |
| Exercised (route A or B) | 1,003 | **73.64 %** |
| Never cited | 359 | **26.36 %** |
| — hard gaps (no route, no near variant) | 223 | 16.37 % |
| — near-miss OCR variants of a cited siglum (ratio ≥0.85) | 136 | 9.99 % |

Plus 34 never-cited rows that are OCR fragments/garble (excluded from the denominator) and
7 junk tokens. The hard-gap list is dominated by minor works — `Mandāv.` (Māṇḍūkyopaniṣad),
`DevīPañ.`, `Nṛtya.`, `Sadācāra…`, `ApaSu8.` (Āpastambáśulbasūtra) — not by famous texts.

### Discrepancy list (5 classes, one TSV)

| Kind | Rows | What it means |
|---|---:|---|
| `harvest_not_in_aob` | 1,793 | harvested sigla with no printed entry and no join match |
| `join_unconfirmed_at_entry` | 681 | join says present; entry not re-locatable from this OCR |
| `aob_never_cited` | 223 | printed entry never exercised under `a-` |
| `aob_never_cited_near_miss` | 136 | printed entry with only an OCR-variant citation |
| `join_miss_siglum_equal` | 80 | printed entry the join missed; siglum identity proves it |
| `aob_fragment_or_garble` / `junk_ocr` | 34 / 7 | OCR artefacts, reported not counted |

## H6941 — printed-text confirmation of the join's unconfirmed rows

The 681 `join_unconfirmed_at_entry` rows were not left as a shrug. The printed book has two
further machine witnesses on the same disk: the **PDF/A text layer** of `AOB.pdf` (poppler
`pdftotext`, 162,027 chars — both columns legible, cleaner than the AOB.md tesseract pass)
and the **second OCR** `AOB_ocr.md` (166,348 chars, column-per-line). For each unconfirmed
row the H6707 adjudicated title is matched against both witness texts by skeleton coverage
(longest common substring in a window anchored on the title or its longest words; ≥0.85 of
the title, short titles <8 chars only on exact containment).

| | Rows | Share of the join's 3,233 |
|---|---:|---:|
| confirmed at entry level (H6720) | 2,552 | 78.94 % |
| **+ confirmed in a printed-text witness (H6941)** | **2,821** | **87.26 %** |
| still unconfirmed | 412 | 12.74 % |

**269 rows recovered** (`join_confirmed_printed_text`, 203 in the PDF text layer, 66 in the
second OCR). Presence itself does not move — the join's 63.32 % / 78.04 % and the corrected
64.88 % / 80.08 % stand; what moves is how much of that join this repository can *re-verify
independently*.

The 412 residuals share one cause: **the adjudicated title itself is OCR-broken at a wrap**
(`Jainend lravyikarana` for *Jainendravyākaraṇa*, `Nyayava irttika` for *Nyāyavārttika*,
`Pauskar rasarhhita`), so no witness contains that string and coverage lands at 0.75–0.84 —
below the bar. Repairing H6707's titles is a different job (it is the join's own authority,
not the printed book's text); lowering the threshold would trade a verifiable 269 for an
unverifiable one.

## Caveats

- **Letter `a-` only.** Q2 answers "not cited in the published `a-` volumes", not "not
  cited in PD".
- **The entry inventory is not H6923's R1 line count.** R1 counts entry-like lines (1,476);
  this parser folds 61 wrap fragments and recovers 15 garbled-start rows, giving 1,362
  well-formed entries. Neither number is the printed census (1,464 books).
- **The H6707 join is not re-adjudicated.** Route A is an independent witness that can only
  *add* sigla; it cannot invalidate a fuzzy title match. The 681 unconfirmed rows are an
  OCR-reproducibility limit, not proof of a false match.
- **Frozen headline values untouched:** 25.2 % / 77.9 % are not re-derived here and
  `pd_dcs_metrics.json` is unchanged.
- Comparison with the declared canon (`pd_aob_declared_works.tsv`, 1,118 edition rows) is
  H6923's territory; this table's `entries_wellformed` is deliberately not that denominator.

## Reproduce

```sh
python3 scripts/pd_aob_sigla_reconciliation.py --selftest
python3 scripts/pd_aob_sigla_reconciliation.py --aob ../PD/AOB.md \
  --witness ../PD/AOB.pdf --witness ../PD/AOB_ocr.md
python3 scripts/pd_aob_sigla_reconciliation.py --check --aob ../PD/AOB.md \
  --witness ../PD/AOB.pdf --witness ../PD/AOB_ocr.md
```

_Dr. Mārcis Gasūns_
