# SIGNOFF A50 — author-voice pass

_Created: 06-09-2026 · Last updated: 06-09-2026_

**Scope.** Manuscript [A50_ls_citation_frequency_graph.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/A50_ls_citation_frequency_graph.md) ("What the Sanskrit lexicographic tradition cites: a citation-frequency graph of `<ls>` source tags across 11 Cologne dictionaries"), readiness 3/5. Pass executed 06-09-2026 by Fable 5.1 (`claude-fable-5-1`) under [H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md). Voice, register and framing only; no number, claim or citation altered; mechanical drift gate CLEAN (`voice_drift_check.py --git origin/main`: numbers 390/390, URLs 32/32, IAST 80/80, headings 12/12, table rows 57/57). No review memo and no prior signoff existed for this paper.

## 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Header | Added the academic byline line (Mārcis Gasūns, independent scholar, ORCID, gasyoun@ya.ru) under the dated header; `Last updated` bumped to 06-09-2026 | Byline was absent; the status paragraph itself lists "byline" as an open gate |
| 2 | Status paragraph | Appended "author-voice pass 06-09-2026 (SIGNOFF link)" after the H677 prose-pass note | Brief's manuscript header note |
| 3 | Abstract, first sentence | "do not merely define words — they cite authorities" → "Besides defining words, … dictionaries cite authorities" | The "not merely X — Y" opener is the "not X, it's Y" cliché; the content (definition plus citation) is unchanged. Veto if the original antithesis is preferred |
| 4 | Abstract | "We extract" → "I extract"; "Three findings." → "Three findings follow." | Sole-author first person; the verbless two-word sentence was telegram syntax |
| 5 | §1, closing question | "lets us ask" → "lets me ask"; bold removed from the research question | First person singular; the question is carried by its position, not by bold |
| 6 | §1 | "We test both" → "I test both" | First person singular |
| 7 | §1 Contributions | Prefixed one singular contribution sentence: "The contribution is one artifact, the citation-frequency graph released as a documented, reproducible dataset, and what the sections below read from it. In detail: (1) …" | REVERTED after adversarial verify: the added preamble was a voice regression (restated the abstract, paraphrased the numbered items as "in detail"); the paragraph again opens "**Contributions.** (1) A documented, reproducible…" as on origin/main |
| 8 | §1 Related work | "we are not aware" → "I am not aware" | First person singular |
| 9 | §3 | Inline bold removed from "33.7%", "71.0%", "No text is cited by all 11 dictionaries.", "608 of 912 texts (66.7%) are private to a single dictionary" | Bold scatter; the numbers are unchanged. Run-in paragraph leads ("**Concentration.**") kept |
| 10 | §4 | "we compute NODF" → "I compute NODF"; bold removed from "p = 0.001" | First person; bold scatter |
| 11 | §4 | "not merely unsupported — the arrangement … runs the other way" → same words with a colon in place of the em-dash | Em-dash-as-copula; claim wording and strength identical |
| 12 | §5.1 | "— a worklist, not a mystery." → "— a worklist." | Decorative antithesis |
| 13 | §6, first paragraph | "a thin universal head — … — that no single text of which reaches all eleven dictionaries" → "of which no single text reaches all eleven dictionaries" | Grammar repair of a broken relative clause; claim unchanged |
| 14 | §6, opening | Added one lead sentence: "The question posed in the introduction, what the Sanskrit lexicographic tradition cites, has a two-part answer." before the existing "Read as a citation network …" | REVERTED after adversarial verify: the added opener was a voice regression (an announcing sentence in front of the answer); the conclusion again opens "Read as a citation network, the Sanskrit dictionary tradition is not one tradition." as on origin/main |

Not changed, on purpose: the bold cell "**buddhist 98%**" in Table 3 (a table cell is out of scope); "almost hermetically Buddhist" and "omnivorous Petersburg lineage" (magnitude words attached to measured effects); every "X, not Y" antithesis that carries a claim (modular not nested; per text not per locus; tagged residue not true canon; union not intersection).

## 2. Substance flags carried (not fixed)

1. **§5.6 arithmetic is one off.** 2,621 corroborated + 443 mismatches + 3,255 verse-without-quote = 6,319, but the sentence says "the 6,320 second-edition references". Either one reference falls in a fourth category or one count is a typo; check against [SPRUECHE_CITATION_VERIFICATION_CENSUS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SPRUECHE_CITATION_VERIFICATION_CENSUS.md).
2. **§6 promotes "a Vedic profile" to one of four communities** while §4 and §5.2 say the Vedic reading rests on MW's unrepresentative tagged residue and Macdonell's 47 citations. The conclusion is more confident than the caveat; a human should decide whether to soften the conclusion or keep it with a pointer to §5.2.
3. **§4 caveat is still blocking:** the 119-row tradition map is 0/119 human-reviewed; Table 3 community names and the §6 naming depend on it. Not a voice matter, but it is the stated gate before 4/5.
4. **Table 3 `sch` tagged share:** 9,944 ÷ 11,496 = 86.5%, printed as 86%; rounding is at the boundary, fine either way but worth a glance if the table is regenerated.
5. **Five `[author-verify]` reference entries** (Apte 1957–1959, Benfey 1866, Böhtlingk 1870–1873, Schmidt 1928, Vaidya 1889) still await the physical-copy check.
6. **Status paragraph lists "byline/venue" as an open gate.** The byline is now present (call 1); the venue half remains open.
7. Checked and found consistent (no action): `% text` column of Table 1 recomputes from raw and filtered counts; the reach table sums to 912; 29 texts at k ≥ 7 carry 44.1% and the 608 private texts 11.1% of volume (recomputed from `ls_citation_nodes.tsv`); Aṣṭādhyāyī 21,509 is PWG's third-largest edge (recomputed from `ls_citation_edges.tsv`).

## 3. Read-and-sign

About 30 minutes: read the abstract, §1 Contributions, and §6 in full (calls 3, 7, 14 are the only ones that add or reshape a sentence), skim the rest for the first-person switch. Proposed readiness: stay at 3/5 until the tradition-map review (flag 3) lands; 4/5 is then reasonable without further prose work. Venue: the manuscript's own candidates (DSH, Cultural Analytics, or JOHD with the Zenodo release) remain apt; a data-journal route fits the paper's "built to be consumed" framing best. Recommendation only; no submission before 2026-11-01.

_Dr. Mārcis Gasūns_
