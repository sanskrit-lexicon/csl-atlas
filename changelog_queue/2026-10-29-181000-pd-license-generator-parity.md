# PD licence-envelope parity in two generators

`pd_canon_ledger.py` and `pd_aob_sigla_reconciliation.py` now emit the shared
`license` / `licenseUrl` fields through `scripts/lib/dataset_meta.py`, so their
`--check` modes no longer erase the licence stamp added by the dataset-wide
licence backfill. The canon ledger's input hashes are regenerated against the
current licensed inputs. Both PD parity checks, the AOB selftest and the full
dataset licence validator pass.
