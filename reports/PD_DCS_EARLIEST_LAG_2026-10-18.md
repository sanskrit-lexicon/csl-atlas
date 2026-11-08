# PD first citation vs DCS earliest dated attestation — the letter-`a` lag

_Created: 18-10-2026 · Last updated: 18-10-2026_

**Handoff:** H6944 · **Executor:** DeepSeek v4.1 Flash (`deepseek/deepseek-flash`) · **Scope:** PD letter-`a` headwords (107,620 printed entries — with headword blocks, of 107,630 `<L>` entries; see [PD_QUOTATION_UNIT_2026-10-18.md](PD_QUOTATION_UNIT_2026-10-18.md))

Artifacts: [data/pd/pd_dcs_earliest_lag.tsv](../data/pd/pd_dcs_earliest_lag.tsv) (2,458 rows) ·
[data/pd/pd_dcs_earliest_lag.json](../data/pd/pd_dcs_earliest_lag.json) (joins + distribution) ·
[scripts/pd_dcs_earliest_lag.py](../scripts/pd_dcs_earliest_lag.py) (`--check` green).

## 1. What is measured

PD's preface (pp. V-VI) warns that the earliest occurrence it records should not be accepted
with absolute finality. This measures how far that caution is observable against an independent
corpus. For each letter-`a` headword that has **both** a datable first citation in PD and a
datable attestation in DCS, the row records:

| column | meaning |
|---|---|
| `pd_first_siglum` / `pd_first_work` | the first known source siglum in the PD entry, and the dated work it resolves to |
| `pd_date_estimate` | Dharmamitra chronology posterior median for that work |
| `dcs_earliest_text` | the oldest Dharmamitra-dated DCS text (VisualDCS 2021 token dump) containing the lemma |
| `dcs_earliest_date_estimate` | Dharmamitra posterior median for that text |
| `lag_years` | `pd_date_estimate − dcs_earliest_date_estimate`; **positive means DCS is earlier** |

Both sides are dated in the **same** chronology (the committed Dharmamitra snapshot), so the
lag is not an artefact of switching date ladders. Multi-part works are dated at the median of
their parts; a generic siglum (`MahāBhā.`, `Rāmā.`) and a generic DCS title therefore receive
the same work-level estimate.

## 2. Join

| stage | count | why dropped |
|---|---:|---|
| printed `<L>` entries scanned | 107,620 | — |
| unique headwords | 104,950 | homograph repeats collapse |
| … no known source siglum in the entry | 1,567 | entry has no harvested siglum |
| … first siglum not resolvable to a dated work | 72,518 | mostly post-classical commentaries and the Padmapurāṇa, absent from the Dharmamitra snapshot |
| headwords with a dated PD first citation | **30,865** | — |
| … headword absent from the DCS lemma inventory | 27,251 | PD's compound-rich headword list exceeds DCS vocabulary |
| … in DCS, but no dated DCS attestation | 1,156 | lemma occurs only in DCS texts without a Dharmamitra date |
| **joined lemmas** | **2,458** | 2.3 % of unique PD headwords |

DCS side: 246 texts and 4,174,702 tokens in the VisualDCS token dump; 132 of those texts have a
Dharmamitra date. A DCS text without a date is skipped, and a lemma's earliest *datable* text is
used. This can only push the DCS side **later**, so the DCS-earlier shares below are floors.

PD date sources in the joined set: DCS crosswalk 2,306, printed AOB title 136, curated siglum
alias 16.

## 3. Distribution

Point-estimate lag in years (`PD − DCS`):

| statistic | all joined (n = 2,458) | non-ties only (n = 994) |
|---|---:|---:|
| median | 0.0 | −190.0 |
| Q1 | 0.0 | −706.25 |
| Q3 | 0.0 | 121.25 |
| mean | −102.61 | — |
| min / max | −2,232.0 / 2,014.0 | — |

| outcome | share of all joined |
|---|---:|
| tie (same work-level estimate) | **59.56 %** |
| DCS earlier (lag > 0) | **15.50 %** |
| PD earlier (lag < 0) | **24.94 %** |
| DCS earlier among non-ties | **38.33 %** |

## 4. Reading

The median offset is zero, but that zero is not a date and not evidence that PD and DCS agree on
a year: in three-fifths of the joined lemmas both sides resolve to the same work, and a
work-level estimate then cancels. The informative signal is in the 994 lemmas where the two
sides name different works: there the point estimates put PD's first citation about 190 years
earlier than DCS's earliest datable text, with a wide and asymmetric spread (quartiles −706 and
+121 years), and DCS still names an older text in 38.3 % of those cases. That is the measured
form of PD's own warning: its first citation is an editorial selection, often a commentary or a
canonical text chosen for lexicographic convenience, and for a substantial minority of checkable
lemmas an older attestation exists. The asymmetry (PD earlier more often than DCS, 24.9 % vs
15.5 % overall) is consistent with PD citing works outside DCS's 246-text horizon; it is not
evidence that PD's chronology is wrong, because the DCS side deliberately discards undated
attestations and therefore cannot claim the true earliest occurrence either.

## 5. What this does not say

- It does **not** date any lemma. Every number is an offset between two posterior medians from
  the Dharmamitra model, not a historical date for a text or a word.
- It does **not** cover PD's non-`a` volumes, or the 72,518 headwords whose first citation the
  Dharmamitra snapshot cannot date.
- It does **not** treat a tie as agreement in a manuscript: a tie means the same work-level
  estimate was used on both sides.
- It does **not** claim DCS's earliest attestation is complete: 114 of the 246 dumped texts and
  25 DCS text directories have no date here.

## 6. Reproduce

```bash
python3 scripts/pd_dcs_earliest_lag.py \
  --inputs /path/to/dir-with-pd.txt-0.csv-dictionary.csv \
  --out-dir data/pd
python3 scripts/pd_dcs_earliest_lag.py --check   # PASS on the committed TSV
```

Pinned inputs (sha256):

| input | sha256 |
|---|---|
| PDScan 2020 `pd.txt` (107,630 `<L>` entries) | `4ee75e6619ee2bd86a331586bb922101e0ae090f9edd981752cfac36ed724442` |
| VisualDCS `0.csv` (token dump) | `bf0f687ba1bc8272b2bcd709f092c70364709c4b063d178f6fb30529d9291107` |
| VisualDCS `dictionary.csv` | `95172e5a626ada6322ec67173657b834b7f2bbe1db71250b8b2551c07feb60cd` |
| `src/data/external/dharmamitra-chronology.json` | `e8ad4988651b179a3e63d8a61928e6f240758c7dfa6d22d81e3b7a4d7df201e5` |

_Dr. Mārcis Gasūns_
