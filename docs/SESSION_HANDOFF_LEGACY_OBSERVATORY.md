# Session handoff — read this first in a new chat

## ⏩ 2026-06-02 — current state (START HERE; the 2026-05-16 research handoff follows below)

**First action in a new chat:** read [`DECISIONS_NEEDED.md`](DECISIONS_NEEDED.md) and resurface the open items to the maintainer. Two parallel streams are active:

**A · Engineering / data-quality** — journal: [`csl-corrections/.ai_state.md`](https://github.com/sanskrit-lexicon/csl-corrections/blob/master/.ai_state.md).
- Done: markup fixes for 10 csl-orig dicts; issue taxonomy on 6 dict repos (BOR/BUR/INM/KRM/BOP/MW72); full README+CLAUDE+citation/community docs for those 6; org-wide [`CONTRIBUTOR_STATS.md`](CONTRIBUTOR_STATS.md); ecosystem [`ROADMAP.md`](ROADMAP.md) + 7 tracked issues; **quick wins Q1–Q6 shipped** — hw.py BOM `utf-8-sig` fix (csl-pywork#50), `.gitattributes`×7, csl-orig encoding+`<L>/<LEND>` CI guard, contributor-identity map, Mermaid validator, AI-contribution policy, `clone_org.py`.
- Remaining (human/scope): **Q7 taxonomy FULLY DONE 2026-05-31** — 24 dictionary repos (786 issues) + 4 tooling repos csl-apidev/cologne-stardict/GreekInSanskrit/ArabicInSanskrit (153 issues) all verified all-clean (type+severity+milestone+project). A2 closed. **M3 full-runbook README/CLAUDE DONE 2026-05-31** for **15 stub repos** (WIL + ACC, BEN, BHS, CAE, CCS, LRV, MCI, SCH, SKD, STC, VCP, VEI + **ApteES, SHS**), matching the BOR-group gold standard (live counts, validated Mermaid, source bibliography, data-format example); pushed to each repo's default branch. ApteES got hand-built reverse-direction docs (`{@en@}`/`<s>skt</s>`); SHS author corrected to Jibananda Vidyāsāgara (B4/B5 both resolved). All M3 dict gaps now closed (repos with pre-existing real READMEs — incl. PWG/PWK's lowercase `readme.md` — were already done). NB: the org-wide `docs-pass` branches are a *separate* microanalysis effort (DICT_PROFILE.md etc.), still awaiting maintainer review — not M3. **B3 issue templates DONE 2026-06-02** — all 8 files pushed to BOR/BUR/INM/KRM/BOP/MW72 via gh api (48 files total). Other remaining: dependabot rebase mop-up (loop running, job `b27c7a5e`; 27 PRs merged, 14 conflicting awaiting rebase; re-run merger via `10m` cron), M1 refresh-script modernization, M4 refresh automation (needs token), M7 KRM license decision, #51 XML-parse tail.

**B · Research / practitioner layer** — additive to the existing genealogy + typology program. **L0/lexicography-genealogy stream: start at [`L0_HANDOFF.md`](L0_HANDOFF.md)** (Phase L0 fully built; key open issue = the size-confounded MW content figure + the precision ladder).
- Existing: [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md) (L0–L10), [`MICROSTRUCTURE-MACROSTRUCTURE.md`](MICROSTRUCTURE-MACROSTRUCTURE.md) (typology + 50-viz catalog).
- New: [`RESEARCH_LAYER_ROADMAP.md`](RESEARCH_LAYER_ROADMAP.md) — 7 hypotheses, practitioner tools (students/makers/researchers), and 2 working prototypes: `scripts/lexico/micro_entry.py` (`python … Darma` → one lemma × dicts) and `scripts/lexico/macro_profile.py` (43-dict structural profile). Outputs in `data/lexico/`.
- **Phase L0 cladogram — DONE 2026-06-03, gate CLOSED via Patel gold** ([`L0_RESULTS.md`](L0_RESULTS.md)): full pipeline (`scripts/L0/s2*.py`, `s3_cladogram.py`) over 32 dicts × **25** dims. The **Patel 2016 PDF** (`refs/Patel_2016_Normalizing_headwords.pdf`) gave the convention author's own per-dict assignments for all 7 conventions → ingested as gold (`s2d_patel_gold.py`), closing the annotation gate for 30/32 dicts. Recovery **27%→55%**; **PWG→PW 0.79, PWG→SCH 0.70, WIL→SHS 0.81** bootstrap; 6/6 families cohere; Petersburg formatting family (PWG/PW/SCH/CCS) razor-sharp. **Key finding:** convention-lineage ≠ content-lineage — MW reformatted PWG conventions (so PWG→MW misses, correctly). Taxonomy + concordance in [`refs/`](refs/). Remaining `gate`: LRV/FRI (not in Patel's 36); KNA/KOW/AMAR need Cologne sources. **Dashboard page** `observatory/site/src/conventions.md` (nav "Conventions (L0)") + **Paper H §5 draft** [`articles/paper_H_convention_vs_content_lineage.md`](articles/paper_H_convention_vs_content_lineage.md) both shipped 2026-06-03 (build verified, exit 0); refresh workflow copies `data/L0/` into the site.
- **Next research build: R2 — a per-dict sense splitter** (gates hypotheses H1–H3 and the maker worklist); needs decisions A6/A7.
- ⚠️ **Lesson (2026-05-30):** *validate heuristic detectors against real entries before trusting numbers.* A `<ls>`-only citation detector wrongly called SKD/VCP "citation-free"; they cite densely via `“…”` + `…0` authorities (`jE0`,`BA0`,`amara0`) + `iti` — fixed (VCP 95%, SKD 51% cited). Test on **mid-alphabet** lemmas (`dharma`=`Darma`); resolve Patel headword-convention variants (doubled-`r` → `Darmma`, inflected visarga → `DarmmaH`) and concatenate homonyms.

**Conventions for a new agent (also saved as memories):**
- **Document first** — update `.ai_state.md` + touched docs and commit (`ai-wip:`) as each deliverable lands; don't ask, don't defer.
- **Commit trailers** — dictionary/data repos: NO Claude trailer; infra repos (csl-observatory, csl-pywork, csl-corrections): `Co-Authored-By` is the convention.
- **Comment-noise** — maintainers dislike bot comment/commit volume on dict repos; keep minimal, edit-in-place.
- **csl-orig** — corrections go copy→edit→XML-validate→audit; never write a BOM (`utf-8`, not `utf-8-sig`).
- **Artefact refresh** is server-side (Cologne cron) — push csl-orig and let it propagate.

---

**Date**: 2026-05-16
**Previous session ended due to**: API stream idle timeout (likely context-density)
**For**: any new Claude Code session picking up the csl-observatory work

This doc gives a new chat session everything needed to continue without losing momentum.

---

## 1. What this project is

**csl-observatory** — a measurement-and-analysis layer for the Cologne Digital Sanskrit Lexicon (CDSL). Open-source, unfunded, run by M. Gasūns (project lead, working toward higher-doctorate qualification).

End-products planned by 2035:
- **19 peer-reviewed articles** (per [`PUBLICATIONS.md`](PUBLICATIONS.md) — 15 originally scheduled + 4 added 2026-05-16)
- **Scientific monograph** (the Book, 2033)
- **Practical manual** for Sanskrit lexicographers (2034)
- **New corpus-based Sanskrit-Russian dictionary** (~50k headwords, 2035)
- **Higher-doctorate defense** (2035)

Live dashboard: **https://sanskrit-lexicon.github.io/csl-observatory/**
Repository: **https://github.com/sanskrit-lexicon/csl-observatory**

---

## 2. Read these docs FIRST (in order)

| Order | Doc | What it tells you |
|---|---|---|
| 1 | [`SESSION_HANDOFF.md`](SESSION_HANDOFF.md) | THIS doc — orientation |
| 2 | [`OBSERVATORY_DESIGN.md`](OBSERVATORY_DESIGN.md) | Architecture: Observable Framework, GitHub Actions, snapshot strategy, KPI catalog |
| 3 | [`OBSERVATORY_ROADMAP.md`](OBSERVATORY_ROADMAP.md) | Phases A-H for the measurement framework |
| 4 | [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md) | Phases L0-L10 for the dictionary-comparison research stream |
| 5 | [`L0_DESIGN.md`](L0_DESIGN.md) | The first cladogram phase: 30 fingerprint dims, 27 trees, validation. Also includes Phase L0.5 (Nirukta), L0.6 (subentries), L1.5 (KOW⇄WIL), M3-Bopp, Phase P (preface analysis) |
| 6 | [`METALEXICOGRAPHY_ROADMAP.md`](METALEXICOGRAPHY_ROADMAP.md) | Data-richness typology L0-L10, MW-attention hypothesis, multi-volume year handling, KCH inclusion |
| 7 | [`MICROSTRUCTURE-MACROSTRUCTURE.md`](MICROSTRUCTURE-MACROSTRUCTURE.md) | 24 verb-entry dimensions + 10 nominal + 20 macrostructure; 50+ visualisations |
| 8 | [`PUBLICATIONS.md`](PUBLICATIONS.md) | The 15-article plan, book, manual, dictionary, trends-tracking |
| 9 | [`PAPER_1_OUTLINE.md`](PAPER_1_OUTLINE.md) | Paragraph-by-paragraph outline of Paper 1 |
| 10 | [`articles/article_1_methods.md`](articles/article_1_methods.md) | Draft Methods section (1700 words) |
| 11 | [`trends/2026-Q2.md`](trends/2026-Q2.md) | First quarterly trends digest (skeleton) |

Reference data (read as needed):
- [`data/dictionary_inventory.csv`](../data/dictionary_inventory.csv) — 47 dicts with year ranges, families, sanhw1 lemma counts
- [`data/sanhw1_inheritance_edges.csv`](../data/sanhw1_inheritance_edges.csv) — empirical inheritance edges
- [`data/sanhw1_distance_matrix.csv`](../data/sanhw1_distance_matrix.csv) — 41×41 Jaccard
- [`data/etymology_marker_preliminary.csv`](../data/etymology_marker_preliminary.csv) — WIL/MW/AP etymology markers

---

## 3. What's DONE (don't redo)

### Infrastructure
- ✅ Dashboard live at sanskrit-lexicon.github.io/csl-observatory/
- ✅ GitHub Actions monthly auto-refresh workflow
- ✅ Zenodo + Software Heritage + Crossref archival plan
- ✅ CONTRIBUTING.md with 6 open roles + named-attribution policy
- ✅ All 34 dict repos have enriched CITATION.cff (year + author + preferred-citation)

### Data foundation
- ✅ 12-year backfill: 77 repos × 6 data types = 4.4MB raw, 7 CSVs derived
- ✅ sanhw1.txt (10MB master headword index, 469k lemmas × 41 dicts) — analysed
- ✅ Per-letter coverage extracted empirically from sanhw1
- ✅ 41×41 Jaccard distance matrix + UPGMA cladogram (Newick)
- ✅ 33 inheritance edges with ≥85% containment (source → inheritor, temporal-plausible)
- ✅ Contributor specialisation (entropy + family focus per contributor)

### Key empirical findings (from cladogram + per-letter + etymology scans)
- **WIL (1832) → SHS (1900)**: 0.953 containment ✓ confirms claim
- **WIL (1832) → YAT (1846)**: 0.926 ✓ NEW finding
- **PWG (1855) → PW (1879)**: 0.938 ✓ PWG→PWK abridgement
- **MW72 (1872) → MW (1899)**: 0.896 ✓ Monier-Williams self-expansion
- **CCS (1887) → CAE (1891)**: 0.940 ✓ Cappeller siblings
- **ARMH (1861) → MW**: 0.928, **ABCH (1896) → MW**: 0.925 (Hemacandra kośas absorbed into MW)
- **WIL Nirukta `.E.`**: 88.9% of entries (top tokens: aff. 14665, neg. 1509, fem. 539, etc.)
- **MW "relies on Bopp"**: 0 direct citations of Bopp in MW (need indirect cognate-set test)
- **MW72 → MW expansion**: mean 4× per letter, peak 9.9× for `z` (ṣ)
- **GST: only 2% letter coverage** (a- only) ✓ confirms incomplete
- **PD: only 2% letter coverage** ✓ ongoing 37-vol project

### Runbooks applied (org-wide)
- ✅ 35 dictionary repos: phases 1-16 of cologne-issue-runbook
- ✅ 28 tooling repos: phases 1-17 of cologne-tooling-runbook
- ✅ Tooling Roadmap org-project (#9) created

### Locked decisions (from many rounds of Q&A)
- L0 fingerprint: 30 dimensions (Patel's 7 + 23 added incl. etymology)
- 3 encodings × 3 metrics × 3 algorithms = 27 candidate trees
- Validation: known-edge recovery + LOO + 1000 bootstrap CIs
- Multi-volume year ranges (start_year, end_year, n_volumes, letter_coverage)
- Co-annotation with Cohen's κ on overlap sample
- Russian/Czech in main tree with caveat; specialised in supplementary
- Petersburg tradition annotated first
- Per-tradition split CSVs with file-header author + ORCID metadata
- Schemas: native CDSL + TEI Lex-0 + OntoLex-Lemon (all three exports)
- L0 + L1.5 + M0a run in parallel when execution starts
- Paper E merged into Paper M (one stronger paper)
- Cologne Matomo analytics: full access, Phase 12 ingest planned
- Public data API: yes, full CSV/JSON/Parquet with stable URLs
- 4 papers: M (methodology), L (linguistic), H (historical), Paper N (Nirukta) possibly separate
- All three phylogenetic algorithms (UPGMA + NJ + Bayesian) for comparison
- Authorship: M. Gasūns + named CDSL maintainers + Claude with disclosure
- Russian co-author per article + Amba Kulkarni for Apte-Hindi data + Article 9
- Article 1: draft Methods now; Results when L0/M1 land
- Dictionary scope: ~50k headwords (1.7× Kochergina)
- Funding: entirely unfunded
- Trend digest: markdown in `docs/trends/YYYY-QN.md`, tiered bibliography (top-20 + appendix)
- Manuscript split: MICROSTRUCTURE-MACROSTRUCTURE.md + PUBLICATIONS.md (was combined; user renamed)
- `docs/outreach/` is gitignored (email drafts stay local only)

---

## 4. What's PENDING (the actual next work)

### Done in session 2026-05-16
- [x] **Asked 4-8 prompting questions** to extract M. Gasūns's research questions (8 prompts in 2 rounds via `AskUserQuestion`)
- [x] **Captured answers** in [MICROSTRUCTURE-MACROSTRUCTURE.md §5.2](MICROSTRUCTURE-MACROSTRUCTURE.md) (Round 1, structure/lineage) and [PUBLICATIONS.md §6.2](PUBLICATIONS.md) (Round 2, publication strategy / methodology)

### Immediate (~next session)
- [ ] **Pandanus brief**: one-page summary of the Prague Pandanus project (scope, status, dataset) — M.G. asked to include it in the non-CDSL comparison thread but is not yet familiar with the project
- [ ] **Phase L0.7 design**: hapax-legomena overlap study — chosen as the forensic instrument for derivation claims (Round 1 Q2). Add as a new phase in [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md).
- [ ] **Integrate Articles 16-19 into the §1 schedule**: PWG-backbone, hapax-methodology, grammatical-coding variation, CCS→KCH (currently in §6.2 only — needs cadence/timing slots in §1's main table)
- [ ] **Name the "Petersburg Thread"** explicitly in PUBLICATIONS.md §1 — it spans Articles 6, 11, 14, 16, 19 per Round 2 Q8

### Near-term (~next few sessions)
- [ ] **Phase L0 execution**: extract Patel's 7 conventions + 20 added dimensions × 41 dicts → cladogram
- [ ] **Phase L1.5 execution**: KOW⇄WIL focused study (test cross-language inheritance)
- [ ] **Phase M0a execution**: scrape sanskrit-lexicon.uni-koeln.de for CDSL features inventory
- [ ] **Phase A execution**: compute volunteer-hours equivalent (the headline number)
- [ ] **Article 1 Results**: add to article_1_methods.md once L0/M1 data lands

### Awaiting external input
- [ ] **M. Gasūns to provide**: classical lexicography manuals as .txt (next week-ish)
- [ ] **M. Gasūns to send**: Amba Kulkarni email (draft in `docs/outreach/amba_kulkarni_email_draft.md` — gitignored)
- [ ] **Cologne web team**: Matomo access (for Phase 12)

### Medium-term (~Q3-Q4 2026)
- [ ] **Phase L0.5**: WIL Nirukta deep-dive (token extraction + Pāṇinian classification + classical comparison)
- [ ] **Phase L0.6**: subentry analysis (15 categories from `gam` analysis)
- [ ] **Phase L2-full**: full per-family cladograms
- [ ] **Trends Q3 digest**: end of September 2026
- [ ] **Article 1 first complete draft**: ~Q4 2026

---

## 5. The 4-8 prompting questions — asked and answered 2026-05-16

**Status**: ✅ Completed. Both rounds (4+4) asked via `AskUserQuestion` and answered by M. Gasūns. Captured at:
- [MICROSTRUCTURE-MACROSTRUCTURE.md §5.2](MICROSTRUCTURE-MACROSTRUCTURE.md#52-new--added-by-author-captured-2026-05-16-prompting-round-1) — Round 1 (lineage + structure)
- [PUBLICATIONS.md §6.2](PUBLICATIONS.md#62-additional-research-questions-captured-2026-05-16-prompting-round-2) — Round 2 (publication strategy + methodology)

The 8 prompts are preserved below for reference / re-use.

User explicitly requested these to extract their research questions. Per-doc placement:
- Structure-related questions → `MICROSTRUCTURE-MACROSTRUCTURE.md §5`
- Publication-strategy questions → `PUBLICATIONS.md §6`

The 8 prompts (use AskUserQuestion 4 at a time):

**Round 1** (concrete dictionary-pair / lineage questions):
1. Beyond what we've already captured (WIL→YAT, WIL→SHS, ARMH→MW, ABCH→MW), what other specific dictionary-pair derivation hypotheses do you suspect?
2. Are there specific lemmas, concepts, or word-families (e.g. dharma, brahman, ātman, technical terms) you want to use as case-study comparisons across dicts?
3. What specific editorial decisions (inclusion criteria, normalisation choices) of individual dicts do you want examined?
4. Are there specific lexicographers or editors (Wilson, Böhtlingk, Monier-Williams, Apte, Kochergina, Patel) whose biographical/intellectual influence you want studied?

**Round 2** (publication-strategy and methodology questions):
5. Beyond the 15 articles already in PUBLICATIONS.md, what other paper topics interest you (could shift to articles 16, 17, 18, …)?
6. Are there comparison studies with non-CDSL Sanskrit projects (Sanskrit Heritage / DCS / GRETIL / Pandanus / Hyderabad) you want to formalise?
7. Are there specific methodological questions (e.g. about clustering algorithms, normalisation choices, citation parsing) you want explicitly tested in articles?
8. Are there specific Russian-tradition questions (about Indology in Russia, the IVRAN tradition, Soviet-era Sanskrit work) you want to investigate?

---

## 6. Workflow tips for the new session

### When making changes
- ALWAYS push to GitHub via `gh api PUT` with base64-encoded content + sha
- Workflow file in `.github/workflows/` is configured for monthly + manual refresh
- Dashboard auto-deploys after each push if workflow runs (~6 min)

### When running scripts
- Source files (csl-orig/v02/*.txt) are large (10-50MB each); fetch on demand via `curl -s "raw.githubusercontent.com/..."`
- Python in PowerShell uses Windows path semantics (`C:\\Users\\user\\AppData\\Local\\Temp` not `/tmp`)
- For interactive bash work, paths are `/c/Users/user/...`
- Bash subprocess from Python: use `["gh", "api", url]` argument list, NOT shell=True (Windows cmd.exe mangles quotes)
- Adaptive sampling preferred (sample until 95% confidence) over fixed sample sizes

### When user dismisses questions
- They explicitly chose not to answer — DO NOT proceed in a direction; wait for further instruction
- Sometimes they meant to answer; offer to re-ask

### Communication style preferred
- Terse, no preamble, no end-of-turn summaries
- Brief updates between tool calls (1 sentence)
- AskUserQuestion is the preferred way to clarify; max 4 questions per call
- User is comfortable with very long sessions and lots of design rounds before execution

### Token budget
- User has been deeply engaged; they want substantive design
- BUT prefers concrete deliverables (data files, charts, dashboard pages) when execution time comes
- Bias toward producing files + pushing > talking about it

---

## 7. Critical context the new session must know

- **User is M. Gasūns**, project lead, working toward higher-doctorate qualification in Russia
- **gasyoun = gasyoun@gmail.com** (GitHub username + email)
- The user **knows CDSL deeply** — has been involved for years; many domain-specific corrections + insights
- The work is **entirely unfunded**; this is itself a key narrative for Paper 1
- Cologne University is the canonical host; sanskrit-lexicon GitHub org is where the project's code lives
- The user prefers **methodologically rigorous** choices when offered (always picks "all three" / "tiered" / "comprehensive" options)
- The user has corrected several of my mistakes (terminology "Sanskrit-Russian" not "Russian-Sanskrit", naming "AND_CAREER_PLAN" felt strange)
- Don't refer to the work as "career" in doc titles or section names — it sounds presumptuous in Russian academic context
- Use **"higher-doctorate qualification"** rather than direct Russian terms when in English context (matches user's framing)

---

## 8. Recent corrections / clarifications

| When | Correction | Source of error |
|---|---|---|
| 2026-05-16 | "Sanskrit-Russian" not "Russian-Sanskrit" — the source language is Sanskrit | I had reversed direction |
| 2026-05-16 | FRI is Sanskrit-Czech-Russian (reader, not lexicon); KNA/KOW are pure Sanskrit-Russian | I had grouped FRI with KNA/KOW |
| 2026-05-16 | KOW is a Russian translation of WIL (hypothesis to verify) | M.G. domain knowledge |
| 2026-05-16 | WIL's `.E.` is Nirukta, NOT Western etymology — 89% of entries; uses Pāṇinian framework | I initially called it "etymology" |
| 2026-05-16 | MW's "Bopp dependence" can't be tested by direct citation (0 mentions); needs cognate-set comparison | Empirical finding |
| 2026-05-16 | AP frequency markers are minimal; AP's Sanskrit-Hindi dict (not in CDSL) has the derivation data — need Amba Kulkarni | M.G. domain knowledge |
| 2026-05-16 | Many dicts are multi-volume (PWG 7 vols 1855-1875, PW 7 vols 1879-1889, etc.) — affects temporal plausibility | M.G. correction |
| 2026-05-16 | KCH = Kochergina 1978 — the standard modern Sanskrit-Russian dict; add to inventory | M.G. addition |
| 2026-05-16 | "AND_CAREER_PLAN" naming feels strange for Russian academic context → renamed to BOOK → PUBLICATIONS | M.G. preference |
| 2026-05-16 | Email drafts (`docs/outreach/`) stay local-only; gitignored | M.G. privacy |

---

## 9. How to start the new session

Suggested opening from the new Claude session:

> "I've read SESSION_HANDOFF.md. Picking up where we left off — you'd asked me to extract 4-8 prompting questions to surface your research questions. Ready to ask round 1 (4 questions about dictionary-pair lineage hypotheses, case-study lemmas, editorial decisions, lexicographer influences). Should I proceed?"

If user says yes → ask round 1 via AskUserQuestion
If user redirects → follow their lead; reference this handoff for context as needed
