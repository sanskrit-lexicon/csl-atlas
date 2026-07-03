# A05 (P5 Pointing Inward) — Hostile Pre-Submission Review

_Created: 03-07-2026 · Last updated: 03-07-2026_

**Paper:** [docs/articles/paper_xref_lineage.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_xref_lineage.md)
**Reviewer:** Fable 5 (`claude-fable-5`), adversarial referee pass per H119 (Fable window S13), in the A01/A03/A06 mold.
**Verdict: MAJOR (one factual defect) → fixed same pass** — the headline results all verify exactly, but the abstract and Table 1 **swap the two Apte editions** and print two raw counts in a table headed "(normalised)". Plus the recurring apparatus defects. All agent-doable; applied in this pass.

---

## 1. Figure re-verification

Against [`xref-lineage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/xref-lineage.json) (normalised graphs) and [`xref_hub_review.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_hub_review.json) (raw scans):

**Confirmed exact:** PWG 22,937 edges / 11,857 sources; MW 7,637 / 6,974; MW×PWG shared sources 2,538, MW edges 2,946, PWG 7,022, overlap **641**, rates **0.2176 / 0.0913**, J **0.0687**; control AP×AP90 182 edges, **0.8545 / 0.8465**, J **0.7398**; all six sparse pairs in Table 2 (23/19/11/11/10/7 edges with their rates and Jaccards); prefix hubs *a°* 320, *mahā°* 254, *su°* 160; PWG 123,366 entries scanned / 12,283 with a cross-reference; the 40-edge shared-core sample (`counts.sharedCoreSample`); density ratio 3.0×; "four in five" = 1 − 0.218.

**FAILED verification (fixed):** see M1.

## 2. Major findings

**M1 — The abstract and Table 1 swap the two Apte editions, and mix raw with normalised counts.** In CDSL, **AP90 is the 1890 edition** (34,882 entries) and **AP is the 1957 revision** (90,843) — settled usage everywhere else in the series, including this paper's own P2/P3 companions. The abstract said "609 + 446 clean lemma edges for AP 1890 and the revised Apte", and Table 1 listed "Apte 1890 (AP) … 609" and "Apte revised (AP90) … 446": both attributions are backwards (the artifact has AP = 609, AP90 = 444). On top of the swap, 446 and 196 (CAE) are the **raw** scan counts from the hub packet; the normalised graph the whole analysis runs on has AP90 = 444 and CAE = 190, and Table 1's own header says "(normalised)". A referee who opens either artifact catches both immediately, and the swap corrupts the paper's central calibration narrative (which edition contains which). *Fix (applied):* labels corrected (AP = revised 1957, AP90 = 1890), normalised counts throughout (444, 190), and a table note stating the raw-vs-normalised distinction (raw 446/196 in the hub packet; matching AP 609 = 609 both ways).

**M2 — The two `[author to add]` reference slots are fillable, and the paper had zero in-text citations.** *Fix (applied):* Jaccard (1912) added for the overlap coefficient and Andrews & Macé (2013) for structural descent evidence in digital stemmatology (the same anchor P3 now uses — series-consistent); the three listed-but-unused references wired in (Zgusta 1971 §1; Wiegand 1989 and Atkins & Rundell 2008 at the entry-structure/cross-reference-practice anchors).

**M3 — Anti-salami: the companion list omits P1**, which owns the cross-reference-overlap metric definition (P1 §3.6) that this paper instantiates — and whose §3.6 quotes this paper's own headline numbers (182 / J 0.74 / 0.069). *Fix (applied):* P1 added to the companion block with the ownership note; §3.1 cross-cites it.

## 3. Minor findings

**m1 — "every measurable dictionary pair" (Table 2) silently drops two packet rows** — AP×CAE (1 edge) and AP90×CAE (0 edges). Defensible, but say so. *Fix (applied):* table note: the two ≤1-edge CAE–Apte pairs are omitted as empty.

**m2 — "a lexicon of some 300,000 headwords" (§4.2)** is the MW∪PWG union key space, but reads like a corpus figure (the corpus has ~410k distinct lemmas). *Fix (applied):* "in the ≈300,000-headword union of the two dictionaries' key spaces".

**m3 — Relative artifact links** in the preamble and both table sources. *Fix (applied):* full blob URLs.

## 4. Fixes applied in this pass

All M/m findings above, same branch/PR as this review. Remaining gates: **author** byline + venue; the second edition-continuity control (§6) stays honest future work.

## 5. Checked and sound (no action)

- The calibration argument (§5.1) is the paper's real contribution and survives scrutiny: 21.8 % is meaningless uncalibrated, decisive against the 85 % ceiling.
- The prefix-hub control is verified in the committed packet (`hubClass: "prefix-convention"` with exactly the counts quoted) and correctly framed as P3's convention axis intruding on content.
- Benfey's zero (§4.4) is documented in the lineage doc and correctly presented as a content fact, not a parser gap — the P4 zero-meaning move applied in reverse.
- Directed-edge, floor-not-ceiling, and density-asymmetry limitations are all stated before a referee could demand them.

_Dr. Mārcis Gasūns_
