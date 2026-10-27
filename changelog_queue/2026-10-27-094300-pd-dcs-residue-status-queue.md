# PD × DCS residue status queue: H6722's acquisition queue becomes status-aware (H7298)

The 44 named-residue works (PD-cited, absent from DCS) now carry DCS / GRETIL /
wisdomlib-portal / wisdomlib-estate state, rights, annotation and fragment status, and
route into three action lanes: **ingest-annotate** 9 works / 10,262 cites (GRETIL full or
embedded), **acquire-digitise** 6 / 9,229 (H6722's missing-everywhere class, membership
unchanged), **fragment-completion** 6 (5 GRETIL-partial + the covered-but-fragmentary
Skandapurāṇa context row, 5,348 expected gain); the 24 GRETIL-uncrossed rows (9,685
cites) stay `unverified` rather than guessed. New evidence: the MSI wisdomlib store was
re-located (`E:\Tools\wisdomlib-scrape`; the D: path is gone) and probed — Padmapurāṇa,
Bhaviṣyapurāṇa, Naiṣadhīyacarita, Bṛhatsaṃhitā and Skandapurāṇa all have manifest entries
but **link indexes only, no chapter bodies** (CF-blocked since 23-07-2026). Skandapurāṇa
verdict: portal Sanskrit edition `skanda-purana-sanskrit` (95,556 chapters) identified,
print-edition identity INCONCLUSIVE (live probe CF-blocked), rights = derived layers
CC BY 4.0 (Zenodo 10.5281/zenodo.22117833), annotation none; DCS holds fragments only
(SkPuR 113,333 + SkPu 16,479 tok). Five-row spot checks PASS. Deliverables:
`data/pd/pd_residue_source_status.tsv` (frozen evidence input),
`data/pd/pd_dcs_residue_status_queue.{tsv,json}`, deterministic
`scripts/pd_dcs_residue_status_queue.py` (`--check` parity + lane invariants),
`tests/forensic/test_pd_dcs_residue_status_queue.py` (8 pins), dated report
`reports/PD_DCS_RESIDUE_STATUS_QUEUE_2026.md`. No corpus ingestion, no KoshaSHRI bulk
text, no publication. H6722's queue and C5/C6 sweeps unchanged (read-only).
