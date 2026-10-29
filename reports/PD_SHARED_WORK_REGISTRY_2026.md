# PD shared work-and-edition identity registry (H7296, Q3)

_Created: 26-10-2026 · Updated: 29-10-2026 (Y0Q) · Handoff: [H7296](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7296-DeepSeek_csl-atlas_pd-shared-work-registry_26.10.26.md)_

This is the shared PD ↔ PWG / MW work-and-edition identity layer ruled in Q3. It is
an **identity consumer**: it reads H6992's printed Index (2,031 rows), H6720's
printed-vs-harvested reconciliation, H6707's AOB declared-work / edition census,
the PD harvested siglum families, and the PW / PWG bibliographies. It does not
transcribe a new Index, does not fuzzy-match titles, and does not rerun any
downstream coverage claim.

## Headline

| Measure | Value |
|---|---|
| Index rows preserved | **2,031** |
| Printed blank abbreviation cells preserved | **409** |
| `vision-low` rows preserved | **434** |
| AOB declared works / editions | **1,112 / 1,118** |
| Work identities (`PDW-…`) | **1,867** |
| Unresolved registry rows | **418** (409 blank cells + 7 structural sigla + 2 OCR non-work fragments) |
| Edition-map records | **6,069** |
| Cross-dictionary siglum folds shared by >1 work | **57** — 55 resolved, 2 partial after Y0Q |
| `shared_siglum` registry records | **228 / 230 adjudicated**, 2 unresolved |
| PW / PWG bibliography sigla attached to a PD work | **236** (PWG 114, PW 122) |

## Identity rule (no guessing)

1. **Index claim** = folded printed siglum **plus folded printed Devanagari title**
   (`title_deva`; IAST only when the Devanagari cell is blank). Two different
   printed works under one abbreviation therefore stay separate (the `AVPari.`
   family); two rows that print the same Devanagari title collapse unless Y0Q
   explicitly splits them by printed author or qualifier.
2. **Cross-source join** = exact folded-siglum equality, and only when that fold
   names one work in the Index and one work in the AOB census. A fold naming
   several works still blocks the ordinary join. After Y0Q, only an explicit
   source-evidenced alias group in `pd_shared_siglum_adjudications.tsv` may join
   claims inside such a fold.
3. **Bibliography attachment** = the PW/PWG reference string must contain the
   work's sourced title (or vice versa). Siglum equality alone is refused:
   PWG prints `MAHĀBH.` for the epic while PD prints `MahāBh.` for the
   Mahābhāṣya — the folds collide, the references do not.
4. **Work ID** = `PDW-` + `sha256(canonical seed)[:10]`, seed chosen by fixed
   source priority (Index > AOB > PWG bib > PW bib > harvested). Adding a
   lower-priority source cannot move an existing ID.
5. **Labels** are copied verbatim from a source cell and carry `label_kind` /
   `label_source`. This script never writes a title. Blank-siglum rows keep their
   printed title but an **empty `work_id`**.

## Y0Q shared-fold adjudication

All **57 folds** have a claim-level overlay row with evidence and rationale:
**55 resolved** and **2 partial**. Of the original **230 registry records**, **228**
were adjudicated; the two unresolved claims are deliberately not guessed:

- `AOB:aryasiddhantamahasiddhanta148` — the combined Aryasiddhānta/Mahāsiddhānta
  entry cannot be assigned to only one of the two distinct Index works.
- `AOB:1962` — only the year fragment survives; the three printed Tantra works
  remain split, with no title evidence for the AOB claim.

The overlay makes **22 author/qualifier splits**, **50 explicit alias groups** and
quarantines **2 OCR/editor fragments** as `aob_ocr_non_work`. The overlay itself is
the evidence packet; `scripts/pd_shared_siglum_review.py` regenerates the full source
export on demand. This is a single-annotator review, not double annotation: it does
not change the Q5 validation contract.

## Unresolved classes (explicit, no silent promotion)

| Class | Rows | Meaning |
|---|---|---|
| `blank_abbreviation_cell` | 409 | printed abbreviation cell is blank; title preserved, identity unresolved |
| `structural_siglum` | 7 | `A.` / `B.` structural sigla in the Index, not works |
| `shared_siglum` | 2 | two AOB claims remain without enough title evidence after Y0Q |
| `aob_ocr_non_work` | 2 | OCR/editor fragments quarantined without a work ID |
| `aob_join_aob_never_cited` | 149 | AOB work has no harvested citation partner (H6720 class) |
| `aob_join_aob_never_cited_near_miss` | 78 | only a near-miss partner exists; never merged |
| `aob_join_join_miss_siglum_equal` | 9 | siglum equal, printed join missed |
| `aob_join_aob_fragment_or_garble` | 7 | AOB fragment / OCR garble |

## Canaries (all green)

| Canary | Result |
|---|---|
| `MahāBhā.` ≠ `MahāBh.` | distinct works `PDW-17d11a8946` / `PDW-1413815235`; not merged |
| Near-homographs | 142 near-miss pairs, **32 consonant-skeleton collisions**, **0 merged** |
| Repeated editions | 6 works / 12 edition rows, one work each; `AtmaU.1` + `AtmaU` both preserved |
| Commentary-inherited siglum | `AmaKoUd.` → `commentary_on` the Amarakośa work; own printed title, distinct ID |
| Blanks / `vision-low` | 2,031 / 409 / 434 exact |

## Validation contract (Q5)

Every registry and edition-map record is
`unvalidated_pending_double_annotation`. The 409 blank cells, the 434
`vision-low` rows and one **seeded ordinary control** (`XCIII:4`, selected by
`sha256("H7296-control|page|row")`) are visible as such. **Kappa is `null`**
(`not_measured_no_double_annotation`) and **adjudicated rows = 0**. No human
judgement or agreement statistic is fabricated.

## Preliminary figures (do not quote as rerun)

The earlier **3.11 %**, **4.03 %** and the breadth/depth headline bands remain
**preliminary until rerun**. This unit builds identity only; it does not rerun
effective coverage, breadth/depth or any downstream inheritance claim. The
diagnostics file records `preliminary_figures.status = preliminary_until_rerun`
and `rerun_in_this_unit = false`.

## Files

| File | Rows | What it is |
|---|---|---|
| `data/pd/pd_work_registry.tsv` | 2,285 | one row per work + one per unresolved identity claim |
| `data/pd/pd_work_edition_map.tsv` | 6,069 | every Index row, AOB edition, bibliography siglum, harvest attestation and commentary relation |
| `data/pd/pd_work_registry.json` | — | machine-readable works + unresolved arrays + counts |
| `data/pd/pd_work_registry_diagnostics.json` | — | inputs (sha256), counts, classes, canaries, validation, preliminary-figure status |
| `data/pd/pd_shared_siglum_adjudications.tsv` | 57 | Y0Q claim-level decisions, evidence, rationale and residue |
| `data/pd/pd_pwgbib_sigla.tsv` | 2,601 | PWG bibliography sigla + verbatim reference strings |
| `data/pd/pd_pwbib_sigla.tsv` | 776 | PW bibliography sigla + verbatim reference strings |
| `scripts/pd_shared_work_registry.py` | — | deterministic builder / `--check` |
| `scripts/pd_shared_siglum_review.py` | — | read-only shared-fold evidence exporter |
| `scripts/pd_pwbib_extract.py` | — | bibliography extractor (`--write` / `--check`) |
| `tests/forensic/test_pd_shared_work_registry.py` | 10 tests | acceptance pins incl. Y0Q residue and mutated-unresolved-cell check |

Inputs pinned by sha256 in the diagnostics file: Index `44ef8d2aa6fb`,
AOB works `686f75d2601a`, families `d5d0b32ae2f3`, reconciliation `ffaca8a29a8a`,
PWG bib `a56732bde7a6`, PW bib `5aba81881090`, Y0Q overlay `c3186e768903`.

## Reproduce

```bash
python3 scripts/pd_shared_work_registry.py --check
python3 -m pytest tests/forensic/test_pd_shared_work_registry.py -q
```

`--check` rebuilds all four artifacts in memory and exits 0 only on byte
equality; one changed unresolved cell exits 1 and names the first differing line
(`test_changed_unresolved_cell_fails_check`).

## Limits

- Identity is **siglum-and-title evidence**, not a bibliographic authority
  record. Two AOB claims still carry `shared_siglum` and need source evidence
  beyond this first manual pass.
- AOB joins inherit H6720's classes; 243 AOB works carry an unconfirmed or
  absent join class and are never promoted.
- One harvest-only work (`ĀtmaU.`) has no sourced title in any input and stays
  unlabelled rather than guessed.
- Bibliography attachment is deliberately conservative: 2371 PWG and 538 PW
  sigla carry no usable reference string (`? [Cologne Addition]` etc.) and stay
  out of the PD scope.

_Dr. Mārcis Gasūns_
