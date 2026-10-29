# PD KoshaSHRI fixture dataset registration (H7316)

- **PD KoshaSHRI fixture dataset registration (H7316).** Registered the exact H7316 dataset
  paths `data/pd/pd_koshashri_entries.tsv` and `data/pd/pd_koshashri_citations.tsv` across
  the repository and estate surfaces. Added per-file metadocs with schemas, rights, provenance
  and regeneration commands; linked the fixture from the root README and agent orientation;
  recorded the sync rule that adapter or exporter changes regenerate both TSVs and rerun
  `--check` plus offline tests in the same PR. The all-rights-reserved full source response
  remains local and uncommitted. Dataset bytes and canaries are unchanged from v0.21.2 / PR #653.
