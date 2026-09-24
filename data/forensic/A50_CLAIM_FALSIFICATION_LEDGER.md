# A50 claim-falsification ledger — does the citation graph identify what the paper says it identifies?

_Created: 24-09-2026 · Last updated: 24-09-2026_

**Handoff:** [H5295](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5295-Fable_csl-atlas_research-claim-falsification-preflight_23.09.26.md)
(Fable 5.1 `claude-fable-5-1`). **Target:**
[`docs/articles/A50_ls_citation_frequency_graph.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/A50_ls_citation_frequency_graph.md)
(*The Citation Canon of the Sanskrit Dictionary Tradition*). **Question asked of every
claim:** what does the paper *measure*, what does it *infer*, what else would produce the
same measurement, and does a constructed graph with **no** such mechanism produce it too?
**Harness:** [`scripts/forensic/f12_a50_claim_ledger.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f12_a50_claim_ledger.py)
(descriptive re-derivation over the committed TSVs, the variant-fold map, and the
committed-vs-regenerated drift block) and
[`scripts/forensic/f12_a50_topology_arms.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f12_a50_topology_arms.mjs)
(the committed topology test re-run on eight matrices, three of them constructed, plus a
12-run seed × fraction sweep of the constructed control). Pins:
[`tests/forensic/test_f12_a50_claim_ledger.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_f12_a50_claim_ledger.py).
Independent logic critic on the pre-merge head: §5 (all 25 findings adjudicated: 24 fixed in
this pass, 1 deferred to merge — P8; the key unification I4 asks for is forwarded to H5407).
A delta pass over those fixes (§5.1) returned 22 further findings, all fixed in this pass.

## 0 Verdict in one table

| # | Claim (A50 location) | Verdict | What changed in the paper |
|---|---|---|---|
| C1 | "the tradition's citation mass is heavily concentrated: top 10 = 33.7%, top 50 = 71.0%" (Abstract, §3) | **narrows** | Restated as a pooled figure of which 64.7% is PWG's; PWG-excluded shares added; no per-dictionary comparison (top-*k* shares are breadth-dependent) |
| C2 | "No text is cited by all 11 dictionaries" (Abstract, §3, §6) | **withdraws** | *Ṛgveda* reaches all 11 once the paper's own §5.5 variant `Rigveda` is folded; four texts reach every usable row. Sentence replaced in all three places and in the hypothesis index |
| C2′ | "608 of 912 texts (66.7%) are private to a single dictionary" (Abstract, §3) | **narrows** | Labels, not texts: 31 private labels are variants of shared texts, 9 more merge with another private label; folded floor 568 of 875 (64.9%) stated beside the raw figure |
| C3 | Modular, not nested: Q = 0.4995 vs null 0.4295, p = 0.001 (Abstract, §4) | **survives** | Reproduced byte-identically; the *margin over the null* (0.070, z ≈ 84) is unchanged under the §5.5 fold, thin-row removal and regeneration, and is far beyond anything the label-privacy control produces |
| C4 | "the dictionaries fall into partly disjoint citation communities — Buddhist, classical-kāvya, Vedic, Petersburg" (Abstract, §4, §6; contribution 3) | **narrows** | The optimiser's modules are `ap+ap90`, `pwkvn+sch` and seven singletons — the two pairs are exactly the key-borrow pairs of §2; the four names come from the tradition map. §4 now reports the partition, the key-borrow alternative and the control; six contradicting passages elsewhere rewritten |
| C5 | "the Western dictionaries cite the Indian dictionaries, descent made visible as citation" (§3) | **narrows** | 89–99.5% of each kośa's citations are PWG's; the sentence now names PWG |
| C6 | Folding variants "would only sharpen" the modularity result (§5.5) | **narrows** | Raw Q falls with folding (0.4995 → 0.4972 → 0.4759) but so does the null; the margin is unchanged under the §5.5 fold (0.070 → 0.070) and 0.0035 lower under the 37-pair fold. "Sharpen" is unsupported in either direction; the sentence now states the measured margins |
| C7 | "a shared canon predicts a *nested* matrix … the arrangement of citations runs the other way" (§1, §4) | **narrows** | A rank-biased one-canon draw with the same breadths sits on the fixed-fixed null on both statistics (A3: NODF p 0.95, Q p 0.39). NODF below the null means less nested than a one-canon draw, not "the opposite of a shared canon" |
| P | TSVs rebuild "against sibling `csl-orig` and `csl-guides` checkouts" (Data availability, README) | **narrows** | No revision recorded at the 06-07-2026 freeze; a rebuild at `csl-orig@f4c08c57` + `csl-guides@64c967d` moves six percentage figures by ≤ 0.2 points (top-50 share 71.0 → 71.2) and four counts (−1,753 citations, −2 edges, −1 node, −1 private label) (§2 P). Builder now writes a sidecar; re-freeze minted as H5407 |

Nothing in the paper's *descriptive* layer was wrong as arithmetic: every number reproduces
from the committed TSVs. What did not survive is the step from measurement to mechanism —
once outright (C2), seven times as an overreach.

## 1 Candidate census and selection

`git log --since=2026-09-01 --name-only` over `docs/articles/*.md`, `docs/A*.md` and
`data/forensic/*.md` (24-09-2026, `origin/main` at `bbca791`) lists 38 changed files.
Excluding the H4092 mechanical byline pass (touches every file, no claims) and the H3857
author-voice sign-off stubs leaves five substantive candidates:

| Report | Changed since 01-09 by | Prior independent review | Selected? |
|---|---|---|---|
| `article_21_apparatus_not_errors.md` (A10) | H5050, H5073, H5260, H5264 — 12 commits | H5073 evidence-dependence audit (20-09-2026) — the handoff excludes it | no |
| `paper_citation_registers.md` (A08) | H4092 only | June referee pass (`REFEREE_OBS_RC.md`) | no |
| `paper_redundancy_and_descent.md` (A07) | H4092 only | June referee pass | no |
| `paper_kosha_macrostructure.md` (A09) | H4092 only | already self-narrowed in its own §6 | no |
| **`A50_ls_citation_frequency_graph.md`** | **H3857 author-voice pass (#448, 06-09-2026)** — rewritten Abstract, §4, §6 | prose: none. The hypothesis *row* had two: [#336](https://github.com/sanskrit-lexicon/csl-atlas/pull/336) (H1866 hostile referee, 04-08-2026) and the H1866 caveat in `HYPOTHESIS_INDEX.md` that "none by all 11" is partly a thin-row artefact — a caveat the paper never absorbed | **yes** |

**Why A50.** It is the only candidate whose abstract makes an identification claim
("the dictionaries fall into partly disjoint citation communities") on top of a statistic,
whose causal vocabulary ("descent made visible as citation") has never been challenged, and
which is the paper vehicle of the citation-verification roadmap (§5.6, companion censuses
H488/H5264). No merged PR since #448 audits its prose (`gh pr list --state merged --search
"A50 OR citation-canon OR ls_citation"`: #448, #336, #276, #256, #232, #225, #221, #220 —
builds, drafts, and the hypothesis-row referee).

## 2 The ledger

Format per claim: **source sentence** (verbatim) · **evidence measured** · **inferential
step** · **strongest alternative** · **counterexample** (constructed or found) ·
**provenance binding** · **verdict** · **patch**. All figures: `f12_a50_report.json`
(descriptive) and `f12_a50_topology_arms.json` (topology; seed `0x5eedca11`, 1,000 nulls per
arm, null mean, SD, z and p recorded per arm).

### C1 — concentration

- **Source (Abstract):** "the tradition's citation mass is heavily concentrated: the top 10
  texts (led by the Mahābhārata, Ṛgveda, Rāmāyaṇa, and Manusmṛti) carry 33.7% of all
  citations and the top 50 carry 71.0%."
- **Evidence measured:** pooled top-*k* volume share over 828,505 citations. Reproduced:
  top-10 33.7%, top-20 49.7%, top-50 71.0%, top-100 84.9%.
- **Inferential step:** "the tradition's" — a property attributed to eleven dictionaries.
- **Strongest alternative:** the pool is dominated by one dictionary. PWG contributes 64.7%
  of all citations (next: ap 6.9%, pw 6.1%, ben 5.9%), so the pooled shares are mostly a
  statement about PWG's volume weighting, not about a tradition-wide tendency. (Per-dictionary
  top-10 shares — 38.6% for PWG's 475 texts, 100% for md's 4 — are *not* comparable with each
  other or with the pool: a top-*k* share depends on how many texts are in the pool, and the
  pooled 33.7% sits below PWG's own 38.6%, so "the pooled top-*k* is PWG's top-*k*" would be
  wrong too.)
- **Counterexample (found):** the PWG-excluded pool (657 texts): top-10 37.7%, top-50 73.4%
  — the same order of concentration, so the *direction* survives without PWG; the number the
  Abstract quotes is a volume-weighted mixture the reader cannot un-weight.
- **Provenance:** `ls_citation_edges.tsv` (SHA-256 `6c7f7065…3491`), `f12_a50_report.json`
  `C1_concentration`.
- **Verdict: narrows.** The number survives as a pool property; "the tradition's" does not.
- **Patch:** Abstract says "the pooled citation mass … a pool that is 64.7% PWG's"; §3 gives
  the PWG share and the PWG-excluded shares and says why per-dictionary shares are not
  compared.

### C2 — "no text is cited by all 11 dictionaries"

- **Source (§3):** "No text is cited by all 11 dictionaries. The widest-reach texts, at 9 of
  11, are the Rāmāyaṇa, the Kathāsaritsāgara, the Bhagavadgītā, and the Mārkaṇḍeya-Purāṇa."
  Repeated in the Abstract, in §6 ("of which no single text reaches all eleven"), in
  `docs/HYPOTHESIS_INDEX.md` (CANON-CORE row) and in the generated verdict text of
  `citation_canon.json`.
- **Evidence measured:** column reach over the committed node labels: reach 9 → 4 texts, 8 →
  13, 7 → 12, …, 1 → 608.
- **Inferential step:** a node label is a text.
- **Strongest alternative:** two labels are one text. The paper's own §5.5 says so for four
  names — and one of them, `Rigveda` (837 citations; ben, bhs, lrv, md), is *Ṛgveda* (ap,
  ap90, mw, pw, pwg, pwkvn, sch). Union: **11 of 11**.
- **Counterexample (found in the paper's own data):** fold only the four §5.5 pairs
  (`f12_a50_variant_fold.tsv`, tier `named`) and *Ṛgveda* is cited by every dictionary.
  Two honest qualifiers travel with the repaired sentence: the eleventh and tenth rows are the
  thin ones (Monier-Williams 5 nodes, Macdonell 4 — the paper's §5.2 and §5.4), so "all 11"
  rests on rows the paper itself calls unrepresentative; and the "9 of 11" ceiling was
  mechanical for the same reason — no text could reach 11 unless it was one of Macdonell's
  four. Over the nine dictionaries with a usable yield, Rāmāyaṇa, Kathāsaritsāgara,
  Bhagavadgītā and Mārkaṇḍeya-Purāṇa each reach *every* row; that is the sturdier statement.
- **Provenance:** `f12_a50_report.json` `C2_reach`, `C2b_variant_fold.named_variants.Rigveda`.
- **Verdict: withdraws.** The sentence is false under the paper's own identification of
  `Rigveda`.
- **Patch:** Abstract, §3, §6, the CANON-CORE row in `HYPOTHESIS_INDEX.md`, the verdict
  strings in `build-citation-canon.mjs` (and the regenerated `citation_canon.json`), and the
  `/tools/citation-canon` page restated: one text (*Ṛgveda*) reaches all 11 once its §5.5
  variant is folded, including the two thin rows; four texts reach all nine usable rows.

### C2′ — the private tail

- **Source (§3):** "608 of 912 texts (66.7%) are private to a single dictionary, jointly
  carrying 11.1% of the volume."
- **Evidence measured:** reproduced exactly.
- **Inferential step:** private label = private text.
- **Strongest alternative:** unfolded labels. The fold map has 37 rows: 4 named in §5.5 and
  33 found by a label fold that collapses diacritics, `sh/ś`, `ri/ṛ`, `ch/c`, vowel length,
  doubled consonants and a parenthetical author (`Nirukta (Yāska)`, `Mugdhabodha (Vopadeva)`,
  `Wilson (dictionary)`); `ṃ/n` is deliberately *not* collapsed, which is why `Raghuvanśa`
  needs the hand tier. The 33 are label-variant pairs, not all transliteration pairs, and
  one identity (`WILSON` = Wilson's dictionary) is a judgement, so A1b below is an *upper
  bound* on curated folding.
- **Accounting (from `C2b_variant_fold`):** 31 private labels are variants of texts cited by
  another dictionary (2 named — `Raghuvanśa`, `Manusmṛiti`; 29 ASCII), and 9 private labels
  merge with another private label (e.g. `Chandrāloka → Candrāloka`, `Chāṇakya → Cāṇakya`);
  608 − 31 − 9 = 568 private labels of 875 (64.9%); the private share of citation volume falls
  from 11.1% to 9.8% (`private_after_fold_volume_pct`).
- **Verdict: narrows.** The paper already says the tail is inflated (§5.5); it now says by how
  much, and calls the 608 labels rather than texts.
- **Patch:** §3 states the folded floor beside the raw figure; §4 and §5.5 point at the fold
  table rather than claiming §5.5 lists 31 pairs.

### C3 — modular, not nested (the statistic)

- **Source (§4):** "the matrix is significantly modular and, if anything, *less* nested than
  chance. NODF = 24.44 vs. null mean 28.98 (p = 1.0); Barber Q = 0.4995 (9 modules) vs. null
  mean 0.4295 (p = 0.001)."
- **Evidence measured:** reproduced byte-identically by re-running
  `scripts/build-citation-canon.mjs` on the committed TSVs (arm A0; `validate-citation-canon
  OK`).
- **Robustness arms** (same test, same seed, same 1,000-sample fixed-fixed null; the
  comparison is always observed-vs-null *within* an arm, since relabelling or dropping rows
  changes the margins and therefore the null):

| Arm | Matrix | NODF (null, p) | Q (null) | Q − null · z · p | Verdict |
|---|---|---|---|---|---|
| A0 committed | 11 × 912 | 24.441 (28.976, 1) | 0.4995 (0.4295) | 0.0700 · 83.8 · 0.001 | modular |
| A1a fold the four §5.5 names | 11 × 908 | 24.649 (29.184, 1) | 0.4972 (0.4272) | 0.0700 · 89.5 · 0.001 | modular |
| A1b fold all 37 pairs | 11 × 875 | 26.819 (31.316, 1) | 0.4759 (0.4094) | 0.0665 · 83.5 · 0.001 | modular |
| A2 drop mw, md | 9 × 909 | 24.602 (29.150, 1) | 0.4989 (0.4277) | 0.0712 · 108.2 · 0.001 | modular |
| A5 regenerated at `csl-orig@f4c08c57` | 11 × 911 | 24.475 (29.021, 1) | 0.5003 (0.4295) | 0.0708 · 89.3 · 0.001 | modular |

- **Verdict: survives** — as a statement about the arrangement of the committed matrix under
  its degree-preserving null, with a margin that none of the perturbations move by more than
  0.004. What it *means* is C4 and C7.

### C4 — "partly disjoint citation communities"

- **Source (Abstract):** "the dictionaries fall into partly disjoint citation communities —
  Buddhist (Edgerton), classical-kāvya (the Apte line), Vedic (Monier-Williams' tagged
  residue, Macdonell), and the Petersburg lineage — rather than strata of one shared reading
  list." §6: "a Buddhist lexicon, a kāvya-schoolroom line, a Vedic profile, and the
  omnivorous Petersburg lineage each kept their own authorities". Contribution (3): "with the
  communities named by a curated text→tradition map". Table 3 lead-in: "makes the modules
  legible"; after it: "The communities are exactly the ones a historian … would draw".
- **Evidence measured:** Q above its degree-preserving null (C3), plus Table 3 (tradition
  shares per dictionary from the unreviewed 119-row map).
- **Inferential step:** significant modularity ⇒ the dictionaries partition into the four
  named communities, and the map names the modules.
- **Found counterexample 1 — the modules are not the named communities.** The optimiser's
  9 modules on the committed matrix (same seed as the committed run) are `ap+ap90` ·
  `pwkvn+sch` · `ben` · `bhs` · `lrv` · `md` · `mw` · `pw` · `pwg`. The "Petersburg lineage
  (pwg, pw, pwkvn, sch)" is *not* a module — PWG and pw are singletons; there is no "Vedic"
  pair — mw is a singleton in every real-data arm that keeps it (A0, A1a, A1b, A5), and md pairs with `bhs` (not mw)
  after the §5.5 fold and in the regenerated matrix (where the count drops to 8 modules). Seven
  of eleven dictionaries are their own module — and a constructed one-canon matrix with no
  communities at all (A3) also yields 9 modules with 8 singletons, so neither the module count
  nor the singleton pattern says anything about communities. The read-out is one run of a
  heuristic label-propagation optimiser (the paper's own §5.7 caveat) and moves under the input
  drift of §2 P; it is quoted as the partition the statistic *found*, not as a fact about the
  dictionaries.
- **Strongest alternative — shared resolver keys.** The only two non-singleton modules are
  exactly the pairs that *share an abbreviation key* by construction (§2 step 5: `ap` borrows
  `ap90`'s key; `sch` and `pwkvn` borrow PWG's; the H213 change-log entry). A dictionary pair
  resolved through one key is co-cited under one set of canonical labels while every other
  pair is resolved through two — a resolver artefact that is sufficient for both observed
  pairs and that covers spelling privacy as a special case. Until keys are unified (H5407),
  "citation community" and "shared key" are not distinguishable in this graph.
- **Constructed control (arms A3/A4 and the sweep):** one ranked canon of 912 texts; each
  dictionary samples its *real* breadth (155, 149, 96, 136, 106, 4, 5, 243, 475, 172, 160
  texts) from that one list with weight 1/(rank + 1) — one reading list read to different
  depths, no communities by construction. Then relabel a fraction *f* of each row's texts to
  a dictionary-private spelling (`Text@dict`): the text and every row breadth are unchanged,
  only the label; the column margins change, so the null is re-drawn on the new margins.

  | seed | f | matrix (private cols) | NODF / null / p | Q / null | Q − null | z | p | verdict |
  |---|---|---|---|---|---|---|---|---|
  | 1 | 0.05 | 11 × 766 (369) | 39.615 / 39.520 / 0.101 | 0.3549 / 0.3537 | 0.0012 | 1.54 | 0.064 | neither |
  | 1 | 0.1 | 11 × 847 (480) | 33.894 / 33.689 / 0.010 | 0.3977 / 0.3962 | 0.0015 | 1.93 | 0.024 | nested-and-modular |
  | 1 | 0.2 | 11 × 989 (665) | 25.478 / 25.094 / 0.002 | 0.4746 / 0.4720 | 0.0026 | 3.18 | 0.002 | nested-and-modular |
  | 1 | 0.3 | 11 × 1111 (812) | 19.648 / 19.348 / 0.014 | 0.5395 / 0.5376 | 0.0019 | 2.45 | 0.012 | nested-and-modular |
  | 2 | 0.05 | 11 × 754 (370) | 40.785 / 40.689 / 0.122 | 0.3470 / 0.3467 | 0.0003 | 0.37 | 0.354 | neither |
  | 2 | 0.1 | 11 × 826 (452) | 35.328 / 35.153 / 0.028 | 0.3866 / 0.3853 | 0.0013 | 1.66 | 0.048 | nested-and-modular |
  | 2 | 0.2 | 11 × 966 (653) | 26.335 / 26.179 / 0.167 | 0.4594 / 0.4590 | 0.0004 | 0.40 | 0.356 | neither |
  | 2 | 0.3 | 11 × 1074 (774) | 21.237 / 20.892 / 0.007 | 0.5183 / 0.5175 | 0.0008 | 1.09 | 0.145 | nested |
  | 3 | 0.05 | 11 × 765 (392) | 40.048 / 39.898 / 0.049 | 0.3535 / 0.3527 | 0.0008 | 1.15 | 0.126 | nested |
  | 3 | 0.1 | 11 × 824 (473) | 35.632 / 35.309 / 0.002 | 0.3852 / 0.3834 | 0.0018 | 2.27 | 0.016 | nested-and-modular |
  | 3 | 0.2 | 11 × 970 (637) | 26.403 / 26.141 / 0.023 | 0.4634 / 0.4619 | 0.0015 | 1.83 | 0.038 | nested-and-modular |
  | 3 | 0.3 | 11 × 1082 (787) | 20.591 / 20.486 / 0.270 | 0.5225 / 0.5216 | 0.0009 | 1.01 | 0.160 | neither |
  | arm | 0.1 | 11 × 805 (425) | 36.638 / 36.666 / 0.646 | 0.3760 / 0.3742 | 0.0018 | 2.33 | 0.011 | **modular** |
  | arm | 0.3 | 11 × 1081 (774) | 20.927 / 20.653 / 0.021 | 0.5223 / 0.5215 | 0.0008 | 1.07 | 0.149 | nested |

  (14 constructed runs, 1,000 nulls each: the 12-run `sweep` plus the two A4 arms in `arms`,
  which use the arm seed — all in `f12_a50_topology_arms.json`.)

  What the control shows is narrower than "label privacy manufactures communities": the
  margin it produces is tiny in every run (max Q − null 0.0026, max z 3.18, against
  0.070 and z ≈ 84 in the real graph — a Q − null comparison across matrices, defensible here
  because both sides have 11 rows, 1,701 edges and null SDs of ~0.0008), and the *verdict* at
  that margin is seed- and fraction-sensitive — of the 14 constructed runs, 1 is called
  modular alone (the A4 arm at f = 0.1, p 0.011), 6 nested-and-modular, 3 nested, 4 neither;
  at f = 0.3 the three sweep seeds return three different readings. So (i) the real graph's
  modularity is not an artefact of the 37 known variants (A1a/A1b: the margin is flat after
  folding) nor of uniform per-dictionary spelling privacy (this sweep: ~27× smaller margin,
  z ≤ 3.2 against 84); group- or key-shared labelling — the resolver-key alternative above,
  where one variant is shared by several rows — is not modelled here and stays untested
  until the keys are unified (H5407); (ii) *raw* Q is label-sensitive
  (it rises with private columns in observed and null alike), which is why folding lowers raw
  Q while leaving the margin flat (C6); (iii) a p-value near 0.05 on a matrix like this is not
  evidence of a mechanism. The A4 arm does not explain the result away; it disqualifies raw-Q
  comparisons and verdict-only readings.
- **Provenance:** `f12_a50_topology_arms.json` (`arms`, `sweep`, `sweepSummary`; input
  SHA-256s in `inputs`); `modularity()` in `build-citation-canon.mjs` returns row labels for
  the read-out.
- **Verdict: narrows.** Q is high and significant (C3); "partly disjoint communities" is an
  interpretation the statistic under-determines: the partition it finds is two key-sharing
  pairs plus singletons, and the four community names come from the map, not from the test.
- **Patch:** Abstract, §1 contribution (3), §4 heading and result paragraph, the Table 3
  lead-in and follow-on, §6, `HYPOTHESIS_INDEX.md`, the `build-citation-canon.mjs` verdict
  strings and the `/tools/citation-canon` page all restated in the same terms: "clusters
  beyond what breadth and popularity force; the partition found is `ap+ap90`, `pwkvn+sch` and
  singletons; the tradition profiles are read from the map".

### C5 — "the Western dictionaries cite the Indian dictionaries"

- **Source (§3):** "The indigenous lexica — Śabdakalpadruma, Amarakoṣa, Abhidhānacintāmaṇi,
  Medinīkośa — are themselves among the most-cited *sources*: the Western dictionaries cite
  the Indian dictionaries, descent made visible as citation."
- **Evidence measured:** the four kośas' totals in Table 2.
- **Inferential step:** a pooled total ⇒ a habit of "the Western dictionaries".
- **Counterexample (found):** Śabdakalpadruma 20,232 citations, 99.5% PWG (next: ben 27);
  Amarakoṣa 14,918, 97.3% PWG (ap 187, ap90 125); Medinīkośa 13,246, 98.8% PWG;
  Abhidhānacintāmaṇi 18,073, 88.9% PWG, the rest Schmidt's *Nachträge* (2,000). Only PWG (and
  for one kośa its own supplement) cites the kośas at scale; the paper's §4 already says so
  ("alone in citing the indigenous kośas at scale") — §3 contradicted §4.
- **Verdict: narrows.** "Descent made visible" is Böhtlingk's method made visible.
- **Patch:** the §3 sentence names PWG and the per-kośa PWG share.

### C6 — folding "would only sharpen" the modularity result

- **Source (§5.5):** "the modularity result (§4) is computed on the matrix as committed and
  would only sharpen if variants of shared texts were folded."
- **Evidence measured:** none — a direction asserted without a run.
- **Measurement (arms A1a/A1b):** raw Q falls 0.4995 → 0.4972 → 0.4759 as folding widens —
  but the null falls with it (0.4295 → 0.4272 → 0.4094), because the matrices have different
  margins. The comparable quantity is the margin over the null: **0.0700 → 0.0700 → 0.0665**;
  z *rises* under the four-name fold (83.8 → 89.5). NODF's gap to its null is flat
  (−4.54, −4.54, −4.50). The verdict is unchanged in both arms.
- **Verdict: narrows.** "Would only sharpen" is not contradicted on the fold §5.5 actually
  names (margin equal, z up) and is mildly contradicted on the 37-pair upper bound (margin
  −0.0035); the honest statement is "does not move the verdict; the margin is flat to slightly
  lower". (A first draft of this ledger called the claim withdrawn on the raw-Q drop; the
  logic critic — §5, I1 — caught the wrong comparand.)
- **Patch:** the §5.5 sentence now reports the measured margins and z, and the unchanged
  verdict.

### C7 — "a shared canon predicts a nested matrix; the arrangement runs the other way"

- **Source (§1):** "a shared canon predicts a *nested* matrix (small dictionaries cite subsets
  of what large ones cite), while communities predict a *modular* one". **§4:** "The
  shared-canon hypothesis is not merely unsupported: the arrangement of citations runs the
  other way."
- **Evidence measured:** NODF below its degree-preserving null (p = 1).
- **Inferential step:** NODF below null ⇒ the opposite of a shared canon.
- **Strongest alternative:** the fixed-fixed null is the margins-only ensemble — each text's
  popularity and each dictionary's breadth held fixed, assignment randomised — and a
  rank-biased one-canon draw with the same breadths is indistinguishable from it: arm A3, a
  one-canon matrix by construction, lands exactly on the null on both statistics (NODF 46.40 vs 46.58, p 0.95;
  Q 0.310 vs 0.310, p 0.39): the test cannot call a sampled shared canon "nested". Only a
  stricter-than-random subset structure would; a *perfectly* nested (Ferrers) matrix is the
  unique realisation of its margins, so under this null its p is a point mass — and the
  harness's swap loop never terminates on it (first run of the arms, 24-09-2026).
- **Verdict: narrows.** "Less nested than a one-canon random draw with the same breadths and
  popularities" is what NODF < null says; it is consistent with clustering (C3) but does not
  make the shared-canon reading "run the other way".
- **Patch:** §1's prediction sentence and §4's "runs the other way" sentence restated.

### P — provenance of the committed TSVs

- **Source (Data availability):** "The graph rebuilds in ~1 minute with `python
  data/citations/build_ls_citation_graph.py` against sibling `csl-orig` and `csl-guides`
  checkouts". README: same, no revision named.
- **Finding:** the TSVs were frozen on 06-07-2026 (#219/#220) with **no recorded revision** of
  either sibling; the builder wrote no sidecar. `citation_canon.json`'s sidecar names the
  TSVs (csl-atlas paths) but not the sibling revisions — the same gap H5073/H5260 closed for
  the A10 stages ("a date is not a pin"). The nearest leads, not bindings: the last commits
  before the freeze day ended — `csl-orig@75b229ac90351d3ae54d2b487ab2ffbed3120854`
  (06-07-2026 21:59 +0530, "BEN LS bare references added", BEN issue #22 — Benfey's `<ls>`
  tags were being edited on the freeze day itself) and
  `csl-guides@9e8f4c8e9b9c6e37093e8eff5d827344ebcb1542` (06-07-2026 09:00 +0300). Whether the
  freeze ran before or after `75b229a` is exactly what the missing sidecar would have said.
- **Regeneration (bound):** builder re-run on 24-09-2026 against
  `csl-orig@f4c08c578b330e2379e38f54d3a541f1564b8eee` (clean) and
  `csl-guides@64c967d1d08d26868bbbc289b4aacec7f4a8f3ff` (clean, `abbreviations.json` SHA-256
  `dfd9fb68…8a48`), builder file SHA-256 `af12dcb9…0371`; output byte-identical to the first rebuild of this pass (24-09)
  run, kept as
  [`f12_a50_regen_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f12_a50_regen_edges.tsv)
  (SHA-256 `02891158…fec95`) with its sidecar
  [`f12_a50_regen_edges.source.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f12_a50_regen_edges.source.json).
- **Measured drift** (`f12_a50_report.json` `drift`, every headline figure recomputed on both
  edge lists by the same code):

| Figure | committed | regenerated |
|---|--:|--:|
| citations / edges / nodes | 828,505 / 1,701 / 912 | 826,752 / 1,699 / 911 |
| top-20 / top-50 share (Abstract quotes top-50) | 49.7 / 71.0 | 49.8 / 71.2 |
| PWG share of pool | 64.7 | 64.9 |
| private labels | 608 (66.7%), 11.1% of volume | 607 (66.6%), 10.9% |
| ≥ 7-dictionary texts | 29, 44.1% of volume | 29, 44.2% |
| NODF (null) | 24.441 (28.976) | 24.475 (29.021) |
| Q (null), modules | 0.4995 (0.4295), 9 | 0.5003 (0.4295), 8 |
| dictionaries with changed totals | — | ben 49,003 → 47,251 (96 → 94 texts); ap 57,113 → 57,112 |
| edges changed | — | 30; largest: ben `my Sanskrit Chrestomathy` 3,017 → 1,599, ben `Gaspare Gorresio` 347 → 16, `Weber` → `WEBER` (pwg 350, pw 66; ben's 11-cite `Weber` edge gone), ben `Kullūka Schol` 27 → 0 |

  Six percentage figures move, all by ≤ 0.2 points (top-20, top-50, PWG share, private-label
  share, private volume, ≥7-dict volume), and four counts move (−1,753 citations, −2 edges,
  −1 node, −1 private label); the topology verdict and every p-value are
  unchanged; the module count is not (9 → 8). The drift sits in Benfey's resolution (plus one
  Apte citation and a key-case change in the `csl-guides` key), i.e. in the inputs, not in
  the paper's arithmetic — but "stable" would be the wrong word for a headline that moves.
- **Verdict: narrows.** The paper's numbers are bound to the committed TSVs (hashes in §4)
  and reproduce from them byte-for-byte; they are not reproducible from the *named* procedure
  without a revision, and a revision-bound rebuild moves the Abstract's top-50 figure.
- **Patch (this PR):** the builder writes `ls_citation_graph.source.json` (csl-atlas revision
  and builder hash; both sibling revisions with dirty flags; abbreviations-key SHA-256; output
  SHA-256s; git failures recorded as `unavailable: <error>`, never as null); the
  Data-availability section states the freeze gap and the drift; the citations README records
  both. **Not done here, deliberately:** re-freezing the TSVs at a recorded revision and
  extending `CANON_ALIAS` with the 37 fold pairs — both change the dataset the paper cites and
  belong to one residual mint so code, data, sidecar and prose move together:
  [H5407](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5407-Fable_csl-atlas_a50-citation-graph-refreeze-recorded-revision-alias-fold_24.09.26.md).

## 3 What the constructed control changes and what it leaves alone

Per the handoff's fail condition ("counterexample changes more than the claimed mechanism"):
between A3 and A4 every cell keeps its dictionary and its text (a shared text's column is
split into private `T@dict` columns), every row keeps its breadth, the
edge count stays 1,701, and no citation moves between dictionaries — only node labels
change, the single thing an unfolded variant changes in the real graph. The column margins
therefore change (683 → 805 → 1,081 columns), and the null is re-drawn on the new margins —
which is why every comparison above is observed-vs-null within an arm and never raw Q across
arms. What the control isolates is the effect of label privacy on the *test's output*, not a
community mechanism.

## 4 Reproduction

```sh
python scripts/forensic/f12_a50_claim_ledger.py          # → data/forensic/f12_a50_report.json, f12_a50_variant_fold.tsv
node scripts/forensic/f12_a50_topology_arms.mjs          # → data/forensic/f12_a50_topology_arms.json (~15 min: 8 arms + 12 sweep runs × 1,000 nulls; --quick skips the sweep)
npm run test-forensic-pins -- tests/forensic/test_f12_a50_claim_ledger.py
node scripts/validate-citation-canon.mjs                 # committed topology payload unchanged
```

Inputs (SHA-256, 24-09-2026): `ls_citation_edges.tsv`
`6c7f7065c0e6445eb100f71aadc6f0cfde6b0871563b058d6e4c571693453491` ·
`ls_citation_nodes.tsv` `29d1b588e9b4b1dca7d6dbffea74c6d1a9ee442d071f42d37b437dd2f2898711` ·
`src/data/citations/citation_canon.json`
`663f90248ec4bb175da5070b2ff11b9d31550175d813667b8b051e047b325c02` (before this PR's
verdict-string regeneration; the post-regeneration hash is in `f12_a50_report.json`). The
ledger script never opens `../csl-orig`; the arms script never opens anything outside
`data/` and `scripts/`; the regeneration behind `f12_a50_regen_edges.tsv` is the one external
run, and its sidecar binds it.

## 5 Independent logic-critic verdict (pre-merge head, 24-09-2026)

Critic: an isolated read-only Explore agent (Claude Code, Fable 5.1 `claude-fable-5-1`
session, no shared context beyond the file list), asked for three separate verdicts. It
returned **FAIL / FAIL / FAIL — 2 blockers, 11 majors, 12 minors**, recomputed the drift and
fold figures from the TSVs and confirmed all four input hashes. Every finding and its
disposition:

| # | Severity | Finding (abridged) | Disposition |
|---|---|---|---|
| I1 | blocker | C6 compared raw Q across matrices with different columns; margin over null is flat under the §5.5 fold, z rises | **Fixed** — C6 → narrows; margins/z now the comparand in ledger and §5.5 |
| I2 | major | C1's alternative wrong (pooled 33.7 < PWG's 38.6); per-dictionary top-*k* not comparable; Abstract kept "the tradition's" | **Fixed** — C1 rewritten; Abstract and §3 say "pooled"; per-dictionary comparison dropped |
| I3 | major | Nestedness inference never audited; A3 (one canon) sits on the null | **Fixed** — new row C7; §1 and §4 sentences restated |
| I4 | major | Stronger alternative for C4: the two modules are the key-borrow pairs | **Fixed** — adopted as C4's strongest alternative; §4 says so |
| I5 | major | New prose contradicts §4 heading, Table 3 lead-in/follow-on, contribution (3), §6, "firmer than its names" | **Fixed** — all six passages rewritten; delta pass D1.5 found five more community/module phrasings (Table 3 commentary, §6, Abstract, canon page, tradition-tags builder), also rewritten |
| I6 | major | "mw and md join after the fold" false; `bhs+md` also in the unfolded regen; read-out is one heuristic run | **Fixed** — sentence corrected; heuristic/instability stated |
| I7 | minor | Thin rows used both ways; "§5.1–5.2" wrong pointer | **Fixed** — qualifier added to C2 and §3; pointer → §5.2/§5.4 |
| I8 | minor | 31 = 2 named + 29 ASCII, not 4 + 27; 608 − 31 ≠ 568; "§5.5 lists 31" | **Fixed** — accounting block added to the script and ledger; prose corrected |
| I9 | minor | Fold is not purely transliteration; eye-check unrecorded; A1b is an upper bound | **Fixed** — called label-variant pairs; parenthetical/doubling rules named; upper bound stated in ledger and §5.5 |
| I10 | major | Stale copies: `HYPOTHESIS_INDEX.md`, `citation_canon.json` verdict string, `/tools/citation-canon` page, `build-tradition-tags.mjs` comment | **Fixed** — all four edited; canon payload regenerated |
| I11 | minor | "No prior review" too strong (H1866 caveat exists) | **Fixed** — §1 cites it |
| X1 | blocker | Control not robust: f = 0.3 flips to nested; one seed; favourable arm alone reported | **Fixed** — 12-run seed × fraction sweep added; C4 and §4 report all runs and the max margin |
| X2 | major | "does not alter the null" false (margins change) | **Fixed** — §3 and C4 say the null is re-drawn |
| X3 | major | "private columns are redistributed" mechanism story wrong | **Fixed** — story dropped; control now reported as a statement about the test's output |
| X4 | minor | z-scores and f = 0.3 should sit beside the effect size | **Fixed** — table |
| X5 | minor | Ferrers claim correct; "no null at all" → point mass | **Fixed** — C7 |
| X6 | pass | Found counterexamples verified from the TSVs | — |
| X7 | minor | Arms header stale; no pins on the arms JSON | **Fixed** — header; `test_arms_json_pins` |
| P1 | pass | Hashes real; sidecar binds revisions | — |
| P2 | major | "Lead, not binding" named a checkout without a hash; regen inputs short SHAs, no dirty flag/key hash/sidecar | **Fixed** — full SHAs, dirty flags, key hash, builder hash; regen sidecar committed |
| P3 | major | "Stable to the second decimal" false (top-50 71.0 → 71.2, nine figures move) | **Fixed** — drift block computed by the script; table; prose says nine figures move |
| P4 | minor | "all in ben" false (ap −1; `Weber` drop is not pure case) | **Fixed** |
| P5 | major | Arms JSON stored existence booleans, not hashes | **Fixed** — SHA-256 inputs |
| P6 | minor | Sidecar lacked csl-atlas HEAD / builder hash; silent null on git failure | **Fixed** |
| P7 | minor | Drift figures had no machine-readable home | **Fixed** — `drift` block in the report |
| P8 | minor | Blob links 404 until merge; `.githooks/pre-push` mode change in the diff | Deferred to merge (links); mode change reverted in the tree before the commit (`git status` clean on that path) |
| P9 | minor | Summary counts (7 claims / 4 narrows) wrong; §5 placeholder | **Fixed** — 9 rows: 7 narrow, 1 withdraws, 1 survives; this section |

**Forwarded, not fixed here (1):** unifying the borrowed resolver keys so that "shared key"
and "citation community" become distinguishable (I4's consequence) — dataset change,
[H5407](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5407-Fable_csl-atlas_a50-citation-graph-refreeze-recorded-revision-alias-fold_24.09.26.md).
### 5.1 Delta pass over the fixes (same critic contract, final head)

A second read-only critic (Explore agent, no edits, no sub-agents) re-judged the three axes on
the fixed head: IDENTIFICATION FAIL / COUNTEREXAMPLES FAIL / PROVENANCE FAIL — 0 blockers,
10 majors, 12 minors. It confirmed every hash and sibling commit, every figure in the C3,
sweep and drift tables against the two JSON reports, every pin, and the §0 counts. All 22
findings adopted and fixed in this pass:

| # | sev | finding | disposition |
|---|---|---|---|
| D1.1 | major | "mw is a singleton in every one of the eight arms" false (A3, A4 pair it; A2 drops it) | **Fixed** — "every real-data arm that keeps it (A0, A1a, A1b, A5)"; pin narrowed likewise |
| D1.2 | major | "at f = 0.2 the three seeds return all three readings" — that is f = 0.3 | **Fixed** |
| D1.3 | major | "two orders of magnitude" overstates 0.070 / 0.0026 ≈ 27× | **Fixed** — "~27×", z 84 vs ≤ 3.2 |
| D1.4 | major | "Refuted, and in the opposite direction" survived in `HYPOTHESIS_INDEX.md` and the canon builder's verdict string; "608 of the 912 cited texts" should be labels | **Fixed** — both rewritten ("not supported: less nested than a one-canon draw with the same margins, more modular than it"); `citation_canon.json` regenerated |
| D1.5 | major | I5/I10 incomplete: "Buddhist community", "classical-kāvya school", "broad-spectrum community" (Table 3 commentary), "union of school reading lists" (§6), "profiles behind the clustering" (Abstract), "Modular (tradition communities)" label + "Tradition communities" heading + "Distinct blocks" blockquote (canon page), "named-community reading" / "names the modular citation communities" (tradition-tags builder + payload) | **Fixed** — all rewritten as profiles; `tradition_tags.json` regenerated |
| D1.6 | minor | "the fixed-fixed null *is* a one-canon model" overstates: the null is the margins-only ensemble; A3 shows one one-canon generator is indistinguishable from it | **Fixed** — premise reworded in §0, C7, paper §1/§4, README, changelog; conclusion unchanged |
| D1.7 | minor | HYPOTHESIS_INDEX "dominated by private tails … so the arrangement clusters" non sequitur | **Fixed** — "so" dropped |
| D1.8 | minor | Abstract mixes folded and unfolded frames ("29 texts (3.2%)") | **Fixed** — "29 labels (3.2%; 38 of 875 after folding)" |
| D1.9 | minor | §0 "five sentences" vs I5 "six passages" | **Fixed** — six |
| D1.10 | minor | "moves under the ben drift alone" — ap and the key case move too | **Fixed** — "under the input drift of §2 P" |
| D2.1 | major | "Is the modular margin a spelling artefact? No." overclaims: the sweep models uniform per-dictionary privacy, not the group-shared variants (`Rigveda` in four rows) nor pair-shared keys | **Fixed** — heading and claim scoped: not of the 37 known variants (A1a/A1b), nor of per-dictionary privacy (sweep); group/key-shared labelling untested until H5407 |
| D2.2 | major | 14 constructed runs, not 12: the two A4 arms were never tabulated, and A4 f = 0.1 is verdict **modular** (p 0.011) — the unfavourable arm omitted | **Fixed** — both A4 rows added to the table; counts now 1 modular / 6 nested-and-modular / 3 nested / 4 neither of 14, in ledger and paper |
| D2.3 | minor | control-vs-real (0.070 vs 0.0026) is itself a cross-matrix Q − null comparison | **Fixed** — stated once with why it is defensible (11 rows, 1,701 edges, null SD ~0.0008 on both sides) |
| D2.4 | minor | "relabelling is one-to-one" — columns split (683 → 805 → 1,081) | **Fixed** — "a shared text's column is split into private columns" |
| D3.1 | major | P4 regression: `data/citations/README.md` still "all in `ben`"; rebuild dated 23-09 vs 24-09 elsewhere | **Fixed** — "almost all in ben; plus one ap citation and the key case"; 24-09 everywhere (the arms script's A5 note and its JSON caught by the confirmation pass, fixed in the follow-up commit) |
| D3.2 | major | "nine headline figures by ≤ 0.2 points" matches neither the JSON (10 keys) nor the units (three are counts) | **Fixed** — "six percentage figures ≤ 0.2 points; four counts (−1,753 / −2 / −1 / −1)" in ledger, paper, README, changelog |
| D3.3 | major | `citation_canon.source.json` records the commit but no dirty flag; payload came from the modified builder | **Fixed** — builder sidecar now carries `dirty` and `builderSha256`; regenerated |
| D3.4 | minor | arms and report JSON record script paths only, no script hash or atlas HEAD/dirty | **Fixed** — `scriptSha256` + `cslAtlas {revision, dirty}` (arms), `script_sha256` + `csl_atlas` (report); both regenerated |
| D3.5 | minor | "Volume unchanged to the tenth of a point" (folded private tail) had no field behind it | **Fixed** — field `private_after_fold_volume_pct` added: it *falls* 11.1 → 9.8%, sentence corrected, pinned |
| D3.6 | minor | "24 fixed, 1 forwarded" miscounts: P8 is deferred, the forwarded item is I4's consequence | **Fixed** — restated in §1, changelog, meta |
| D3.7 | minor | `.githooks/pre-push` mode change still in the tree | **Fixed** in the follow-up commit — `git checkout --` had not restored the mode and the first commit carried 100644 → 100755 (confirmation pass caught it); mode set back to 100644 |
| D3.8 | minor | changelog "Data unchanged" while two payloads are regenerated | **Fixed** — "TSVs unchanged; payloads regenerated (strings only)" |

A third, confirmation-only pass on the committed head (same contract) passed 20 of the 22 rows
and found: the paper still said `mw` is a singleton "in every perturbation tried" (fixed: "every
real-data arm that keeps it"), the pre-push mode change had been committed (fixed), a 23-09 date
in the arms script's A5 note (fixed, JSON regenerated), a canon-page reading rule and a
HYPOTHESIS_INDEX history line still saying "disjoint communities" / "refuted-modular" (fixed),
a stray quote in the second canon verdict string (fixed, payload regenerated), "12-run" where 14
constructed runs are tabulated (fixed). All three passes are recorded verbatim in the PR thread
and in the handoff's `## Verifier` section.

_Гасунс_
