# PD M1 — independent annotator-B pass on 200 siglum→work claims

_Created: 29-10-2026 · Annotator B: Kimi Work (Kimi; exact model version not exposed in the session) · Status: B complete, κ pending a genuine annotator-A pass_

## Blind frame and labels

`data/pd/pd_siglum_work_m1_frame.tsv` freezes 200 unique claims selected with
seed `PD-M1-siglum-work-v1|29-10-2026`: 100 ordinary, 40 shared-siglum, 40
`vision-low`, and 20 AOB-join rows. The frame carries the candidate work and the
printed evidence, but no annotator-A label. Duplicate record/claim pairs were
removed before annotation.

**Frozen after Y0Q.** This completed v1 packet remains a pre-Y0Q sample and is
not regenerated against the adjudicated registry: its annotations would be lost.
`--check --complete` validates the frozen IDs, v1 strata and B annotations without
rebuilding the candidate frame. A future blank frame uses v2 quotas (140 ordinary,
0 shared-siglum, 40 `vision-low`, 20 AOB-join): the two remaining `shared_siglum`
claims are AOB-only, so no Index-row shared stratum remains.

Annotator B checked every row against the printed Index page images. The label
schema is `confirmed`, `wrong_work`, `wrong_siglum`, `ambiguous`. Decisions are
stored separately in `data/pd/pd_siglum_work_m1_annotator_b.tsv`; they were not
copied from the registry and have not been applied back to it.

## Annotator-B result

| Label | Rows |
|---|---:|
| `confirmed` | 194 |
| `wrong_work` | 5 |
| `wrong_siglum` | 1 |
| `ambiguous` | 0 |
| **Total** | **200** |

The five `wrong_work` decisions concern two identity collapses: one candidate
`work_id` covers both Jainendra's and Hemacandra's distinct *Dhātupāṭha* works
(M1-078/079), and another covers the distinct *Liṅgānuśāsana* works by
Paramānanda, Vāmana and Harṣavardhana (M1-149–151). These are B's rulings, not
yet gold. M1-159 records a transcription error: the frame has `AVPari,` while
the printed abbreviation is `AVPari. 24`.

## Reliability status

**Cohen's κ is not computed.** A genuine independent annotator-A reading pass on
the same 200 IDs is not present in the repository or an open PR. The registry's
rule-derived output is not a substitute for such a pass. The status file
`data/pd/pd_siglum_work_m1_status.json` therefore keeps `annotator_a: null`,
`kappa: null`, and `adjudicated_rows: 0`.

Once pass A exists, the protocol is: validate both reading passes and their
schemas, compute agreement and the confusion matrix, adjudicate every
disagreement from the printed source, and spot-check 10 % of agreements.
The script refuses missing, partial, or mismatched passes.

```bash
python3 scripts/pd_siglum_work_m1.py --check --complete
python3 scripts/pd_siglum_work_m1.py --kappa <annotator-a.tsv> data/pd/pd_siglum_work_m1_annotator_b.tsv
python3 -m pytest tests/forensic/test_pd_method_ladder_annotations.py -q
```

The test's perfect-agreement κ run is explicitly a synthetic fixture, not a
research result.

_Dr. Mārcis Gasūns_
