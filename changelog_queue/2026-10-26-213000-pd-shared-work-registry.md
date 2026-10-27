# PD shared work-and-edition identity registry (H7296, Q3)

One conservative identity layer over H6992's 2,031-row printed Index, H6707's
1,112 AOB declared works / 1,118 editions, H6720's printed-vs-harvested
reconciliation, the PD harvested siglum families and the PW / PWG bibliographies:
**1,923 work IDs** (`PDW-…`), **6,072 edition-map records**, **416 explicit
unresolved rows** (409 printed blank abbreviation cells + 7 structural sigla),
**57 shared siglum folds never merged**. Blank, `vision-low` and one seeded
ordinary control stay `unvalidated_pending_double_annotation`; kappa is `null`,
adjudicated rows 0. Canaries: `MahāBhā.` ≠ `MahāBh.`, 142 near-homograph pairs
(32 skeleton collisions) with 0 merges, 6 repeated-edition works joined without
losing a siglum, `AmaKoUd.` as a `commentary_on` relation. Builder
`scripts/pd_shared_work_registry.py` (`--check`), bibliography extractor
`scripts/pd_pwbib_extract.py`, 8 pins in
`tests/forensic/test_pd_shared_work_registry.py`, write-up
`reports/PD_SHARED_WORK_REGISTRY_2026.md`. The 3.11 % / 4.03 % and breadth/depth
figures remain **preliminary until rerun** — this unit does not recompute them.
