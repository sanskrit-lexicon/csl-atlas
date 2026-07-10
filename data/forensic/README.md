# `data/forensic/` — dictionary-descent evidence

_Created: 10-07-2026 · Last updated: 10-07-2026_

The datasets and topic docs behind the **MW-vs-Petersburg descent** analysis
([`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md), paper A10).
Datasets regenerate from [`scripts/forensic/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/scripts/forensic)
(run `parse_cslorig.py --all` first). This index exists so a topic doc here is reachable from a
list, not only from a cross-link inside the paper.

## Topic docs (read these, not just the raw tables)

| Doc | What it establishes |
|---|---|
| [`CITATION_TAGGING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/CITATION_TAGGING.md) | `<ls>`-count = 0 does **not** mean "citation-free": SKD/VCP cite densely in the indigenous `iti <authority>` / quote / `X0`-abbreviation style, which carries no `<ls>` tag. Corrects the F1 framing. |
| [`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md) | Which text can adjudicate a **wrong** `HARIV. N` citation, **and the H488 result (§6).** PWG (15,415 numbered refs) and MW both cite the **Calcutta vulgate** by continuous śloka; DCS (critical edition) resolves 1/587. Resolved against the Kinjawadekar vulgate e-text (93.8% coverage): held-out MW check **PASSED** (68.4% vs 2.1% null); **206/565 shared refs corroborate at the exact cited śloka (37.7% vs 0.5% null, ≈75×)** — verse-level shared apparatus — but the shared-**error** test is a **measured null** (no copied wrong numbers). Executed [H488](https://github.com/gasyoun/Uprava/blob/main/handoffs/H488-Opus_csl-atlas_harivamsa_vulgate_citation_resolution_10.07.26.md); dead-end record [`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §8. |

## Key datasets

| File | What |
|---|---|
| [`shared_rare_citations.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/shared_rare_citations.csv) | The A10 candidate pool — 587 rare references shared between MW and a Petersburg dictionary for the same headword (565 are `HARIV.`). |
| [`harivamsa_shared_citation_resolution.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/harivamsa_shared_citation_resolution.csv) · [`harivamsa_continuous_index_offsets.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/harivamsa_continuous_index_offsets.csv) | H488 outputs: per-ref resolution (corroborated / displaced / absent + δ) of the 565 shared `HARIV.` refs against the vulgate, and the per-adhyāya continuous-index offsets. Regenerate via [`f7_harivamsa_harvest.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f7_harivamsa_harvest.py) → [`f7_harivamsa_resolve.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f7_harivamsa_resolve.py) (harvested e-text gitignored per rights). |
| [`citation_pair_overlap.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/citation_pair_overlap.csv) | Per-dictionary-pair citation source-Jaccard (the F1 apparatus signal). |
| [`homonym_concordance.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/homonym_concordance.csv) | Shared deep-homonym splits (F2 structure). |
| [`shared_corrections.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/shared_corrections.csv) · [`pair_shared_typo_counts.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/pair_shared_typo_counts.csv) | Shared print-error / correction evidence. |
| `ahlborn_mw_comparison.csv`, `f*_report.json` | Per-signal reports; provenance in the `.source.json` sidecars. |

_Dr. Mārcis Gasūns_
