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
| [`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md) | Which text can adjudicate a **wrong** `HARIV. N` citation. PWG (15,415 numbered refs) and MW (1,053) both cite the **Calcutta vulgate** by continuous śloka; DCS carries the **critical edition** (1/587 resolve). A vulgate↔critical **concordance cannot fix this** — it presupposes the address under test is correct. The reachable route is the vulgate e-text (474/565, 83.9%). Feeds [H488](https://github.com/gasyoun/Uprava/blob/main/handoffs/H488-Opus_csl-atlas_harivamsa_vulgate_citation_resolution_10.07.26.md); negative result in [`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §8. |

## Key datasets

| File | What |
|---|---|
| [`shared_rare_citations.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/shared_rare_citations.csv) | The A10 candidate pool — 587 rare references shared between MW and a Petersburg dictionary for the same headword (565 are `HARIV.`). |
| [`citation_pair_overlap.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/citation_pair_overlap.csv) | Per-dictionary-pair citation source-Jaccard (the F1 apparatus signal). |
| [`homonym_concordance.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/homonym_concordance.csv) | Shared deep-homonym splits (F2 structure). |
| [`shared_corrections.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/shared_corrections.csv) · [`pair_shared_typo_counts.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/pair_shared_typo_counts.csv) | Shared print-error / correction evidence. |
| `ahlborn_mw_comparison.csv`, `f*_report.json` | Per-signal reports; provenance in the `.source.json` sidecars. |

_Dr. Mārcis Gasūns_
