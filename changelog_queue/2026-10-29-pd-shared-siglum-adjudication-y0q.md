- **PD shared-siglum adjudication (Y0Q).**

Added a claim-level overlay for all **57 shared siglum folds / 230 registry records**
in the H7296 PD work registry. The first manual pass marks **55 folds resolved** and
**2 partial**, adjudicating **228 records** and leaving only two evidence-poor AOB
claims unresolved: `AOB:aryasiddhantamahasiddhanta148` and `AOB:1962`. The overlay
adds 22 author/qualifier splits and 50 explicit alias groups while keeping the
ordinary fold join blocked for every shared fold; two OCR/editor fragments are
quarantined as `aob_ocr_non_work`, not promoted to works.

Regenerated registry: **1,867 work identities**, **418 unresolved registry rows**
(409 blank cells + 7 structural sigla + 2 OCR non-work), **6,069 edition-map rows**,
**236 bibliography attachments** (PWG 114, PW 122). Added the deterministic evidence
exporter; updated the registry report and
`data/pd/README.md` in the same pass. The completed M1 v1 annotation packet stays
frozen (its 200 B decisions are not overwritten); a future v2 frame has no Index-row
shared stratum because both residue claims are AOB-only. C1 edition availability was
rebuilt against the new registry with unchanged headline measures (45.11 % work-level,
5.52 % AOB-exact). Verification: builder `--check` green on all four artifacts,
C1 `--check` PASS, M1 `--check --complete` PASS, and **245 forensic tests passed,
4 skipped**. Q5 remains unchanged: all records are
`unvalidated_pending_double_annotation`, kappa is `null`, adjudicated rows 0.
