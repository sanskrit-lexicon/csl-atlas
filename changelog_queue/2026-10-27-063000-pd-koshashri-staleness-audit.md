- **PD KoshaSHRI staleness audit: Cologne digital ends 2008, print reaches 2019 (H7300).**

Three panels, four separate verdicts. **Markup capability:** Cologne PDScan = one
flat record per entry (107,630 `<L>`; `<ls>`/`<ab>`/`<info>` = 0 — the 25-10
correction holds) + open bulk text (CC BY-NC-SA 3.0); KoshaSHRI = typed per-volume
JSON (33/35 ids answer, the 12/14 gap unchanged), no public entry artefact, no
export, all rights reserved. **Dated content coverage:** the Cologne machine text
ends at vol 24 (2008, p. 4328); the print record runs to vol 35 (2019, p. 6056) —
the Pune-only tail is 11 volumes / 1,728 distinct pages / 2009–2019, so every
machine-text number is a floor on the dictionary. **Same-print-page fidelity:**
the v7/v8 bracketed-source-mark control (4 Cologne scan pages, 20 marks, incl.
bare-vs-bracketed DBHS. negative controls) finds 20/20 consistent — no conversion
loss, no editorial divergence in sample; the 2009–2019 print panel is
**STOP_NO_PRINT_ACCESS** (H7275 precedent), and no editorial claim is made from
tags alone. Source anomalies are explicit: portal ids 12/14 error (ledger
fallback, marked), portal vols 31/32 overlap by 88 pages, ledger rows 32/33
double-list pp. 5609–5708, vol-year disagreements (6, 32, 33). Five canaries
pinned. Builder `scripts/pd_koshashri_staleness_audit.py` (`--check`), 7 pins in
`tests/forensic/test_pd_koshashri_staleness_audit.py`, rights note
`data/pd/pd_koshashri_rights_provenance.md`, write-up
`reports/PD_KOSHASHRI_STALENESS_AUDIT_2026.md`.
