# Metadoc — CITATION_VERIFICATION_ROADMAP_2026_2027.md

_Created: 11-07-2026 · Last updated: 11-07-2026_

Companion record for
[`docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md)
— the program plan for verifying PWG/MW literary citations against digital corpora.

## Purpose and audience

The subject doc is the plan-of-record for the citation-verification program (waves W0–W3,
method invariants, decision log D1–D4 + rulings R1–R4). Audience: future agent sessions
executing wave handoffs (H610, H611, H662, …), and MG when re-ruling scope. It is the
program spine; per-text results live in `data/forensic/*_CENSUS.md` files.

## Provenance

| Date | Model | Handoff | What |
|---|---|---|---|
| 11-07-2026 | Fable 5 (`claude-fable-5`) | [H602](https://github.com/gasyoun/Uprava/blob/main/handoffs/H602-Fable_csl-atlas_citation-verification-roadmap_11.07.26.md) | Initial audit-first roadmap ([PR #245](https://github.com/sanskrit-lexicon/csl-atlas/pull/245)) |
| 11-07-2026 | Fable 5 (`claude-fable-5`) | [H661](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H661-Fable_csl-atlas_citation-roadmap-acl-uplift_11.07.26.md) | §2a ACL-lineage uplift, rulings R1–R4, this metadoc |
| 11-07-2026 | Fable 5 (`claude-fable-5`) | [H662](https://github.com/gasyoun/Uprava/blob/main/handoffs/H662-Fable_csl-atlas_embedding-retrieval-lane-plan_11.07.26.md) | R1 embedding-lane plan ([`EMBEDDING_RETRIEVAL_LANE_PLAN.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EMBEDDING_RETRIEVAL_LANE_PLAN.md)); backlog rows 1–2 closed, row 5 gate marked satisfied |

## The improvement analysis behind §2a (ACL Anthology crosswalk, 11-07-2026)

Four weaknesses were identified in the H602 draft, each mapped to an ACL-lineage remedy;
MG ruled on all four the same day (answers recorded in §2a of the subject doc):

1. **Evidence model too thin.** "Headword within ±3 of fitted locus" is weak per-ref
   evidence for common lemmas; the shuffled null controls aggregate enrichment only. Remedy
   (per [FEVER, NAACL 2018](https://aclanthology.org/N18-1074/): separate evidence
   *retrieval* from verdict *classification*): a quote-retrieval lane over the entries'
   quoted pratīkas, deterministic character-fuzzy first
   ([LaTeCH-CLfL 2019 allusive-reuse lesson](https://aclanthology.org/W19-2514/): normalize
   before matching), embeddings later
   ([SansTib LREC 2022](https://aclanthology.org/2022.lrec-1.724/) /
   [NLP4DH 2024 Vedic similarity](https://aclanthology.org/2024.nlp4dh-1.12/) /
   BuddhaNexus-class NN search). → **R1**: fuzzy lane in W1a; embedding lane planned in
   [H662](https://github.com/gasyoun/Uprava/blob/main/handoffs/H662-Fable_csl-atlas_embedding-retrieval-lane-plan_11.07.26.md).
2. **No measured classifier precision.** H488's gates validate the index fit, not the
   per-ref taxonomy; "how often is `absent` really an edition variant?" had no answer.
   Remedy (FEVER annotation discipline): stratified ~200-ref gold set, blind LLM second
   annotator (A44 precedent), agreement + confusion reported. → **R2**: in W2, retro-fitted
   onto W1 censuses.
3. **Benchmark genre missed.** The ACL Anthology's deepest lesson is infrastructural:
   benchmark datasets with stable IDs, documented schema, baselines, datasheets are the
   most citable output genre. The verdict layer is plausibly the first citation-verification
   benchmark for historical lexicography; venues
   [LaTeCH-CLfL](https://aclanthology.org/volumes/2025.latechclfl-1/) / NLP4DH. → **R3**:
   schema fields (per-ref stable ID, evidence tier, verdict class, cascade tier) mandatory
   from W1; article ID minted after W1 numbers exist; supersedes the open D4 fork.
4. **No baselines.** One unbaselined method invites the circularity objection. Remedy:
   fitted-index-only vs retrieval-only vs hybrid comparison — nearly free once R1 lands.
   → folded into R1/W1a deliverables.

Also ruled: **R4** — DharmaMitra outreach only after W1a pilot numbers exist
(`/outreach-draft`, never auto-sent); local deterministic tools until then.

## Ranked improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | Character-fuzzy quote lane + benchmark schema fields in W1a | ✅ done 11-07-2026 ([H610](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H610-Opus_csl-atlas_mbh_citation_census_11.07.26.md), [PR #247](https://github.com/sanskrit-lexicon/csl-atlas/pull/247)) — 956/2,466 notes confirmed |
| 2 | Embedding retrieval lane plan (Fable) | ✅ done 11-07-2026 (H662) — [`docs/EMBEDDING_RETRIEVAL_LANE_PLAN.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EMBEDDING_RETRIEVAL_LANE_PLAN.md); embedding pilot itself mints at W2 time per its §8 |
| 3 | Gold-standard set + per-class precision (W2) | queued (mint at W2 handoff time) |
| 4 | Benchmark datasheet + resource-paper article ID | gated on W1 numbers (R3) |
| 5 | DharmaMitra outreach draft | **gate satisfied** (W1a numbers exist, R4) — brief ready in [plan §6](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EMBEDDING_RETRIEVAL_LANE_PLAN.md); recommended timing: after the §5 embedding pilot |
| 6 | D2 (article-site badges) / D3 (Manipal tier) rulings | open `@DECIDE` in [GTD](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) |

## Known limitations / caveats

- The subject doc's per-siglum counts come from
  [`lsextract_pwg_06.txt`](https://github.com/sanskrit-lexicon/literarysource/blob/main/pwg/lsextract_pwg_06.txt)
  and fold sigla variants differently than `data/citations/` — do not mix the two series in
  one table without saying which is which.
- W1 censuses ship **without** measured per-class precision until the W2 gold set lands (R2
  ruling accepted this risk explicitly).
- The vulgate↔critical concordance dead end
  ([DEAD_ENDS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md))
  constrains every wave — DCS is reading evidence, never locus arithmetic.

## Related documents

- [`data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md) — the executed H488 model census
- [`docs/CITATION_REGISTERS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_REGISTERS.md) · [`docs/FOUR_AXIS_CITATION_INDEPENDENCE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/FOUR_AXIS_CITATION_INDEPENDENCE.md)
- [`Uprava/ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) — A50, the count consumer

## Revision history (subject doc)

| Date | Change | PR |
|---|---|---|
| 11-07-2026 | Initial roadmap (H602) | [#245](https://github.com/sanskrit-lexicon/csl-atlas/pull/245) |
| 11-07-2026 | §2a rulings R1–R4, wave amendments, D4 ruled (H661) | [#246](https://github.com/sanskrit-lexicon/csl-atlas/pull/246) |
| 11-07-2026 | R1 embedding-lane plan delivered as [`docs/EMBEDDING_RETRIEVAL_LANE_PLAN.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EMBEDDING_RETRIEVAL_LANE_PLAN.md); §2a link added (H662) | this PR |

_Dr. Mārcis Gasūns_
