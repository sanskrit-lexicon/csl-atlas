# L0 / Lexicography-Genealogy Stream Handoff

**Date**: 2026-06-03 · **Model used**: Opus · **Stream**: the dictionary-genealogy research
(separate from the measurement/Paper-1 stream). Consolidated cross-stream handoff:
[`SESSION_HANDOFF_LEGACY_OBSERVATORY.md`](archive/SESSION_HANDOFF_LEGACY_OBSERVATORY.md).

Boundary update 2026-06-04: this handoff now belongs to `csl-atlas` because it
starts from dictionary headword conventions and dictionary genealogy. The old
mixed observatory decision file is preserved as
[`DECISIONS_NEEDED_LEGACY_OBSERVATORY.md`](archive/DECISIONS_NEEDED_LEGACY_OBSERVATORY.md);
do not treat it as the active atlas decision queue.

---

## 1. State — Phase L0 is fully built and validated

The convention-fingerprint cladogram (L0_DESIGN) and all four post-L0 decisions are done.

| Phase | What | Status |
|---|---|---|
| L0 | convention fingerprint → distances → UPGMA/NJ trees + RF + bootstrap + validation | ✅ |
| (gold) | Patel 2016 PDF ingested — his per-dict assignments for conventions 1–7 | ✅ |
| L0.7 | content↔convention **reformatting residual** | ✅ |
| L0.9 | Patel's open conventions (dims 31–33) + **hwnorm1#21** contribution | ✅ |
| L0-rigor | **Bayesian Mk MCMC** + NJ bootstrap; three-algorithm comparison | ✅ |
| L0.8 | **content-magnitude de-confound** — lift + rare-lemma containment + exclusive-pair (`s6`) | ✅ |

Read in order: [`L0_DESIGN.md`](L0_DESIGN.md) → [`L0_RESULTS.md`](L0_RESULTS.md) →
[`refs/fingerprint_conventions.md`](refs/fingerprint_conventions.md) +
[`refs/concordance.md`](refs/concordance.md). Live dashboard page:
**`/tools/lexicographic-conventions`**.

### Headline finding (the publishable result)
**Convention-lineage ≠ content-lineage.** The convention fingerprint recovers *formatting*
genealogy (who adopted whose house style): PWG→PW→SCH and WIL→SHS are razor-sharp (bootstrap
0.79/0.70/0.81; Bayesian 1.00/1.00). It does **not** recover *content* lineages where the heir
reformatted: PWG→MW, MW72→MW score ~0. Monier-Williams imported the Petersburg lexicon but
recoded its conventions (ṛ-stems `-ṛ` not `-ar`, etc.). Quantified as the **reformatting
residual** = content_containment − convention_similarity (top: CAE→MW 0.68, MD→MW 0.65,
CCS→MW 0.62, WIL→YAT 0.54). Robust across UPGMA/NJ/Bayesian (L0_RESULTS §4b). → **Paper H §5**
([`articles/paper_H_convention_vs_content_lineage.md`](articles/paper_H_convention_vs_content_lineage.md))
+ **standalone methods note, PUBLICATIONS Article 20**.

## 2. Scripts & data map

Pipeline order (all under `scripts/L0/`, outputs under `data/L0/`):
```
s2_fingerprint.py    dims 9–30 auto-extracted from csl-orig sources
s2b_patel_auto.py    dims 2,4 mechanical (for dicts Patel doesn't cover: LRV/FRI)
s2d_patel_gold.py    dims 1–7 from Patel 2016 gold → patel2016_assignments.csv
s2e_patel_open.py    dims 31–33 (takārānta/sakārānta/rephānta) → patel_open_assignments.csv
s3_cladogram.py      encodings × metrics → UPGMA+NJ (8 trees) + RF + bootstrap + validation
s4_residual.py       content↔convention reformatting residual + scatter
s5_bayesian.py       NJ/UPGMA bootstrap + Bayesian Mk MCMC; algorithm_support_comparison.csv
```
Key data: `convention_fingerprint.csv`, `distances/B_whamming.csv`,
`trees/canonical_consensus.{newick,png}`, `bootstrap_support.csv`,
`content_convention_residual.csv`, `algorithm_support_comparison.csv`, `validation_report.json`,
`bayesian_report.json`. Atlas-facing dashboard data is committed as compact
generated files under `src/data/lexicographic-structure/`.

## 3. ⚠️ The MW "content-absorption" precision problem (KEY open issue)

Paper-H/L0_RESULTS state MW "absorbed 89–94% of PWG/MW72 content (sanhw1 containment)".
**This number is size-confounded and must not be read as content-copying.** Evidence
(`data/sanhw1_inheritance_edges.csv`, all edges → MW):

| source→MW | containment | source size | lineage? |
|---|---|---|---|
| BOP→MW | **0.94** | 8,505 | unrelated (Latin etymological) |
| BEN→MW | 0.94 | 17,036 | weak |
| MD→MW | 0.93 | 20,103 | — |
| CCS→MW | 0.90 | 28,751 | German |
| MW72→MW | 0.90 | 51,159 | direct (same author) |
| PWG→MW | 0.89 | 106,083 | direct |
| PW→MW | 0.85 | 151,349 | direct |

Containment **falls monotonically with source size** and is *highest* for the unrelated BOP.
MW (194k lemmas) contains almost any older dict's mostly-common-core vocabulary regardless of
descent. So raw containment measures *MW's coverage × the source's rarity profile*, **not**
inheritance. The convention≠content finding is unaffected (it never relied on the %), but the
magnitude claim needs replacing.

### What's needed to make "MW absorbed PWG content" precise — a ladder (cheap → strong)

1. ✅ **Size-corrected association** — `s6_content_lift.py` computes **lift** = |A∩B|·N/(|A|·|B|)
   (PMI) over `observatory/snapshots/sanhw1.txt` (~470k lemmas — present locally but **gitignored**
   / regenerable-from-API, so usable here with no fetch; this handoff's "fetch" note holds only for a
   fresh clone, where the snapshot must be regenerated first). Result: **lift fails**
   to de-confound — BOP→MW has the *highest* lift into MW (2.28); the common core inflates everything ~2×.
2. ✅ **Rare-lemma containment** — `rare@k` = fraction of the source's df≤k headwords recurring in the
   inheritor (common core dropped). **This is the fix.** It inverts the raw ranking: PWG→MW rare@3 0.70 /
   rare@5 0.82, PW→MW 0.71, MW72→MW 0.57; the unrelated **BOP→MW collapses to 0.35**. Bonus exclusive-pair
   (df=2): **17,007 headwords unique to MW∩PW**, 48 to BOP∩MW. (`data/L0/content_lift.csv`,
   `content_lift_report.json`, `exclusive_pair_lemmas.csv`; loader validated exactly vs committed edges.)
3. **Citation-set overlap** (Phase L6, needs corpus parse): do MW and PWG cite the *same* `<ls>`
   references for the same lemma? Language-neutral, strong copy signal.
4. **Entry-text similarity** (Phase L4): for shared lemmas, definition/gloss string similarity
   (post-normalisation) — distinguishes "both list *gam*" from "MW copied PWG's *gam* entry".
5. **Forensic** (Phase L3): shared rare typos / idiosyncratic abbreviations / **citation
   truncation** (PWG `Rv. 1.22.16` → MW `RV.` is one-directional evidence of flow).
6. **Per-volume temporal restriction**: PWG is 7 vols (1855–75); MW72 (1872) could use only
   vols 1–4 (≈ letters a–p). Compute PWG→MW72 containment *restricted to PWG's pre-1872 letters*
   (L0_DESIGN §13). Makes the directed claim historically exact.

(1)–(2) **landed 2026-06-03** (`s6`). Phrase results as **rare-lemma containment** ("MW carries
**70–82%** of PWG's *rare* headwords") or lift — never raw "absorbed X% of content". See L0_RESULTS §3.8.
Steps 3–6 (citation-set / entry-similarity / forensic) remain → §4(D).

## 4. Queued next work (pick up here)

- **(A) ✅ DONE (2026-06-03)** — `s6_content_lift.py`: size-corrected lift + rare-lemma containment +
  exclusive-pair, de-confounding the MW magnitude (→ L0_RESULTS §3.8). Ladder steps 1–2 complete.
  *Next on this thread*: feed the corrected numbers into (B); optionally re-axis the s4 residual on
  rare-lemma containment instead of raw containment.
- **(B) Write Article 20 / Paper H §5 in full** — all convention-side numbers are in hand;
  the content side should use (A)'s corrected numbers, not raw containment.
- **(C) Complete the dict set** — investigated 03-07-2026 (Opus 4.8 `claude-opus-4-8`), now
  **H137** ([`Uprava/handoffs/H137-Opus_csl-atlas_lrv_fri_patel_annotation_and_dictset_blockers_03.07.26.md`](https://github.com/gasyoun/Uprava/blob/main/handoffs/H137-Opus_csl-atlas_lrv_fri_patel_annotation_and_dictset_blockers_03.07.26.md)).
  NOT a clean s2*→s3→s5 re-run: it splits three ways.
  - **LRV/FRI** (the only sourced dicts outside Patel gold) — completable now via a human-gate
    annotation of dims 1,3,5,6,7. Interactive sheet built (`scripts/L0/gen_lrv_fri_annotation_sheet.py`
    → `review/lrv_fri_patel_annotation.html`); votes → `scripts/L0/apply_lrv_fri_annotation.py --rerun`
    (durable overlay `data/L0/manual_annotations.csv`; new order **s2→s2b→s2d→apply→s3→s5**). Awaiting MG votes.
  - **KNA/KOW** — metadata-only stubs, no digitized source anywhere reachable (`git ls-tree HEAD v02/`
    empty); blocked on Cologne digitization (@WAITING).
  - **AMAR** — source present (`../AMAR/amar.txt`) but verse-kosha `;c{}`/`<s>` format; `s2` detectors
    score ~0 by construction (SKD/VCP trap). Do NOT fingerprint as-is — @DECIDE whether a thesaurus
    belongs in a prose-dict tree + a kosha parser.
- **(D) Phases L3/L4/L6** — forensic + entry-similarity + citation-set: the real content-copy
  evidence (and Paper M's spine).

## 5. Conventions & norms (do not relearn)

- **Document first**: update touched atlas docs as each deliverable lands. Commit
  conventions depend on the target repository; do not inherit the old
  observatory convention automatically.
- **Comment-noise**: Cologne maintainers dislike bot noise on dict repos; keep issue comments
  minimal, edit-in-place. The hwnorm1#21 contribution was one substantive issue as gasyoun — that's the bar.
- **Push pattern (Windows/PowerShell)**: `git pull origin <branch> --rebase` then push; native
  `git push` stderr trips PS error-detection harmlessly. No script-blocks/subexpressions in PS.
- **Site builds**: run atlas checks from the repo root: `npm test`,
  `npm run validate-review-reports`, and `npm run build`.
- **csl-orig** sources are at `../csl-orig/v02/<code>/<code>.txt`; 32 of 37 present locally
  (KNA/KOW/AMAR absent). Scan FULL files for mid/late-alphabet probe lemmas (the s2e CAP lesson).
- **Validate detectors against real entries** before trusting numbers (the recurring lesson —
  it caught the s2e CAP bug and the s5 exact-cherry-metric issue).

## 6. Decisions

Resolved 2026-06-03 (DECISIONS_NEEDED "Post-L0"): next=L0.7 ✅ · Patel-open→hwnorm1 ✅ ·
paper=both (Article 20 + Paper H §5) ✅ · rigor=Bayesian MCMC+NJ ✅.
Open/human: complete-dict-set sourcing (Cologne); whether to gate the paper-final tree on all 37.
