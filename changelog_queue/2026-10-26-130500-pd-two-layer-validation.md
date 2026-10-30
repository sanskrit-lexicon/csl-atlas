- **PD two-layer validation: letter-a strata are heterogeneous, print-only tail stops (H7275).**

The 25.2 % citation-weighted coverage is recomputed from the H6949 quotation unit
at 88,363 / 348,430 = 25.36 % over mapped primary sigla (pinned H1336 point:
88,929 / 353,512 = 25.16 %). Stratified, it is **not stable across fascicles**:
the 24 measured rows range 16.9–36.9 % (12 outside ±2 pp), while
leave-one-fascicle-out stays 24.9–25.6 % and a work-level bootstrap gives
19.2–31.5 %. The class split (simplex 29.1 %, derivative 17.7 %, compound-other
21.6 %, privative 28.1 %, preverb 32.3 %) is citation-weighted, not
entry-weighted. The 11 print-only ledger rows (2009–2019, 1,552 of 5,880 pages)
carry no machine text and no page images are reachable, so a 300-slot sample
(100 per period) is frozen from the ledger alone and the second verdict is
**STOP_NO_PRINT_ACCESS** — no machine-text row is substituted. Builder
`scripts/pd_two_layer_validation.py` (`--manifest` / `--check`), 5 pins in
`tests/forensic/test_pd_two_layer_validation.py`, write-up
`reports/PD_TWO_LAYER_VALIDATION_2026-10-26.md`.
