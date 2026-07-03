# A01 (P1 Measurement Framework) — Hostile Pre-Submission Review

_Created: 03-07-2026 · Last updated: 03-07-2026_

**Paper:** [docs/articles/paper_measurement_framework.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_measurement_framework.md)
**Reviewer:** Fable 5 (`claude-fable-5`), adversarial referee pass per H113 (Fable window S11), in the A16/A35/A36 mold.
**Prior passes:** data-verification + references ([PR #186](https://github.com/sanskrit-lexicon/csl-atlas/pull/186)), §3 artifact tail ([PR #187](https://github.com/sanskrit-lexicon/csl-atlas/pull/187) `citation_registers.json`, [PR #192](https://github.com/sanskrit-lexicon/csl-atlas/pull/192) `headword_collapse.json`, merged 03-07-2026).
**Verdict: MINOR REVISION** — every quantitative anchor re-verified clean against the committed artifacts; all findings are scholarly-apparatus and consistency defects, all agent-doable, applied in the same pass (see "Fixes applied" below).

---

## 1. Figure re-verification — all anchors CONFIRMED

Every number in §3 and §6 was independently re-derived from the committed artifacts (not from the paper's own prior text). No discrepancies found.

| Paper claim | Committed artifact value | Artifact |
|---|---|---|
| §3.1/§6 AP90×AP Jaccard 0.269 | 0.2688 | [pairwise-overlap.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/pairwise-overlap.json) |
| §3.1/§6 intersection 26,055; AP90 34,277; AP 88,667; 76 % containment | 26,055 / 34,277 / 88,667 → 76.01 % | same |
| §3.2 1,496,157 entries → 410,259 lemmas, 3.65 : 1 | exact match | [headword_collapse.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/headword_collapse.json) |
| §3.3 survival 0.762 vs 0.705; within-edge *p* ≈ 0.07 | 0.762 (64/84) vs 0.705 (510/723); *z* = 1.80 → two-sided *p* ≈ 0.072 | [paper_sense_inheritance.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md) + [r2_h2_senses.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h2_senses.json) |
| §3.3 granularity proxy ±13 % | "within 13 % of the archived baseline" (P2 §appendix; R2 contract ≤13 %) | [R2_REBUILD_CONTRACT.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_REBUILD_CONTRACT.md) |
| §3.4 1,245,644 `<ls>`; 59.3 % locator-bearing | 1,245,644; 738,173/1,245,644 = 59.26 % | [citation_registers.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json) |
| §3.4 iti: SKD 80,164 / VCP 15,619 / KRM 12,359, all at zero `<ls>` | exact match, `ls: 0` for all three | same |
| §3.5 15,916 RV citations; 3,942 distinct verse loci; 60 rejected | `totalRvCitations` 15,916; `distinctVerseLoci` 3,942; `verseExceedsHymn` 60 | [citation-link-pilot-review.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/review/citation-link-pilot-review.json) |
| §3.6/§6 182 shared edges, J 0.74, ≈85 % mutual inheritance, positive control | 182; 0.7398; 0.8545/0.8465; `reading: "positive-control"` | [xref-lineage.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/xref-lineage.json) |
| §3.6 MW×PWG J 0.069 | `jaccardOnSharedSources` 0.0687 | same |
| §3.9 gaṇa 85.5 % / pada 75.3 % / transitivity 81.4 % | exact match (M7-ROOT-AGREE, Supported) | [HYPOTHESIS_INDEX.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md) → [MICROSTRUCTURE_ROOT_AGREEMENT.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ROOT_AGREEMENT.md) |
| §6 sense drift "−3 revision" | −3.07 (Apte 1890 → 1957, P2 Table) | [paper_sense_inheritance.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md) |

Framing check (DSH primary vs IJL alternate): the paper is method-first throughout — abstract leads with the framework, Sanskrit is the instantiation, §7 argues transferability. Correct posture for DSH; an IJL resubmission would need §6 promoted and §4 compressed, which the venue note already implies. No change required.

Related-work adequacy: Zgusta 1988, Hanneder 2020, ELEXIS MWSA (Ahmadi et al. 2020), and MUDIDI (Setiawan et al. 2026) are all genuinely *used* in §7 — each is positioned against a specific framework mechanism, not listed. FAIR/PROV/data-statement/reproducibility block (§7 last para) likewise load-bearing. Adequate. (But see m1: three references are listed and never used.)

## 2. Major findings

**M1 — The traceability paper does not practice per-row traceability.** §3's preamble asserts "Every row already has a generator under `scripts/`, a committed artifact", and the closing data note claims "every §3 anchor is now walkable" — yet 8 of the 10 metric rows carry **no link to their artifact**; only §3.2 and §3.4 are walkable, and only via the endnote. A referee of *this* paper — whose thesis is that every published number must be walkable to its source — will check exactly this and find the paper failing its own governing commitment. *Fix (applied):* every §3 Output row now links its committed artifact directly.

**M2 — The companion-series map omits the two papers whose headline results §3.2 and §3.4 reproduce.** The closing companion list names P2–P6 but not *Redundancy and Descent* (OBS-R), whose headline is precisely §3.2's 1,496,157 → 410,259 collapse, nor *Two Citation Registers* (OBS-C), whose headline is §3.4's register split. As written, P1 presents these two results with no pointer to the empirical papers that own them — the exact salami-slicing exposure the routing layer (§5) claims to prevent, and an easy "how does this differ from your other submission?" desk-reject trigger at IJL (OBS-R and OBS-C are both IJL-targeted). *Fix (applied):* both added to the companion list with their instantiated metrics named.

## 3. Minor findings

**m1 — Three references are listed but never cited in the text:** Atkins & Rundell 2008, Wiegand 1989, Zgusta 1971. Copy-editors and referees at both target venues flag unused references. All three have natural anchor points. *Fix (applied):* Atkins & Rundell cited in §1 (the practical-lexicography toolkit the opening paragraph paraphrases), Wiegand 1989 in §2 (the term *microstructure* is his), Zgusta 1971 in §3.3 (sense-division practice).

**m2 — Abstract vs §4 mechanism count.** The abstract enumerates five traceability items ("envelope, three graded evidence levels, page-level trust statements, a no-inference-at-build-time rule, and a human review gate"); §4 announces "Four mechanisms" (the no-inference rule lives inside the evidence levels). A referee counting along will trip. *Fix (applied):* abstract now folds the rule into the evidence-levels item, matching §4's four.

**m3 — Corpus span basis is inconsistent across the series.** P1 says "print sources 1832–1993" (digitised-edition basis: Wilson 1832 → MCI 1993); P2's title says "1822–1957" (first-publication basis: SKD 1822). Both are defensible; stating neither basis invites a cross-reading referee to call one of them wrong. *Fix (applied):* §1 now states the basis (digitised editions; first publications reach back to 1822 for the Śabdakalpadruma).

**m4 — §3.5's 3,942 invites a wrong denominator.** "Of 15,916 Ṛgveda `<ls>` citations, 3,942 distinct verse loci link" reads as a 25 % resolution rate; per the artifact, only 5,682 of the 15,916 are verse-level to begin with (9,707 are work-level, 354 hymn-level, 79 maṇḍala-only, 24 unparseable, 69 out-of-range). *Fix (applied):* the verse-level base is now stated.

**m5 — "40+ / more than forty" never anchored.** The committed envelope says `dictionaryCount: 44`. A traceability paper should pin the count once to its envelope date. *Fix (applied):* §1 states 44 as of the 2026-07 envelope.

## 4. Fixes applied in this pass

All M/m findings above, applied to [paper_measurement_framework.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_measurement_framework.md) in the same branch/PR as this review. Remaining gates to submission are the two **author** gates only: byline and venue pick (DSH primary recommended on the framing check above).

## 5. What was checked and found sound (no action)

- No-inference-at-build-time, envelope idempotence (`generatedAt` stability), and review-gate `reviewId` stability claims all match the implemented discipline ([scripts/lib/dataset_meta.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/dataset_meta.py) envelope; PR #192 verified idempotent re-run).
- §5's boundary paragraph (project-KPI programme routed out) is consistent with the hypothesis index's one-owner routing.
- Limitations (§8) are honest — including the admission that the worked example is a positive control and the cross-tradition hard case is carried by companions.
- Scope discipline: no claim in the paper exceeds its stated floor/ceiling bounds; the three anti-over-claim rules of §5 are actually obeyed in §§3, 6.

_Dr. Mārcis Gasūns_
