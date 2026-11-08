# Stage 4b — Russian Словарь XI–XVII: executability assessment + pre-registration

_Created: 30-10-2026 · Last updated: 30-10-2026_

H7518 · PWG-NWS-PD-DCS Stage 4b · protocol §9+§13 (hyperresearch run 8294e5,
`research/notes/final_report_pwg-nws-pd-dcs-8294e5.md`, committed before Stage 1) ·
successor to the
[H7507 Stage 4 census](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/stage4_portability/stage4_gate_census.json)
that licensed this stage · executor GLM-5.3 (ZCode), effort medium.

## Verdict (dated 2026-10-30)

**A structured-data path EXISTS — the Russian analogue is not query-only — but it is
executable only WITH CONSTRAINTS, and a qualified negative component is printed alongside,
never absorbed (§9 discipline):**

1. **The interface's own open-code project carries the app's database.** The H7507
   census's "linked open-code GitHub project" resolves to
   [Sokureo/RusDict](https://github.com/Sokureo/RusDict), tied to the deployed
   `web-corpora.net/wsgi/oldrus.wsgi` by three independent strands: (a) every repo
   template's footer link («Проект на GitHub») matches the live footer; (b) the deployed
   `style.css` is byte-identical to the repo file (2,262 B); (c) the repo DB and the live
   `/lists` endpoint are the same data generation (С…Т + «Дополнения», 6,307 vs 6,284
   headwords — −23 rows drift over 8.7 years).
2. **The structured path** = `user_interface/RusDict.db`, a 25,174,016-byte SQLite file
   committed in that repo (sha256
   `532cad47eb4e3a2c12161a2402ae645d166ea35dcf96d2a7429c8e84400685fc`, last DB commit
   2018-02-21). Four tables — `Words` (6,307; full entry text inline), `Meanings` (8,858),
   `Examples` (24,405; the citation table), `Sources` (8,400; sigla, bibliography, 9 genre
   flags, dates, original-language axis). The wsgi app itself has **no export/API route**
   (route set read from source): the repo clone **is** the bulk path.
3. **Three gating constraints** (machine form in the
   [verdict JSON](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/stage4b_russian/stage4b_executability_verdict.json)):
   - **Licence gap** — no licence in the repo; the dictionary is ИРЯ РАН's; free online
     access (EURALEX 2020–2021: vols 28–30 digitized) ≠ reuse licence. A full run needs a
     dated permission — the same gate shape that holds ONP at rank-1-conditional.
   - **Partial apparatus** — 2 letters of the alphabet (С, Т) + addenda. The exact
     partial-apparatus class P3 warns about; R3 below turns this into the in-dump test.
   - **Stale + incompletely joined** — dump frozen 2018 vs live 2026; only 42.3% of
     examples join to `Sources`; genre flags cover 31.8% of source rows; the translated/
     Lang axis the UI advertises is sparsely populated dump-side.

The §13 kill-exit condition ("query-only interface, no dump, no licence") **did not
fire**: its conjunctive premise fails on the dump arm. The honest reading is the
protocol's own portability truth: *as of 2026-10-30 there is no licensed,
full-alphabet, machine-readable path — any run executed today would be an unlicensed
two-letter slice.*

## Join substrate

`Words ← Meanings ← Examples → Sources` — dictionary headwords with per-citation source
attribution against the dictionary's own declared source list (8,400 bibliographic rows
with genre/date/language metadata). **There is no independent external corpus in this
candidate**: unlike ONP↔Menota, the corpus side is the dictionary's own source inventory,
so the independence premise weakens and every R-hypothesis below is scoped to
internal-consistency claims unless an independent old-Russian corpus is later joined.

Two unit facts the run must respect: the citation-mass unit is the **siglum**
(`Sokr`), not `Sources.Id` (sigla repeat across rows — «Библ.» alone spans ≥2 rows, 428+8
joined citations); and the declared-vs-exercised asymmetry is extreme — 11,477 distinct
source Ids exercised vs 8,400 declared rows, 14,087 of 24,405 examples unjoined.

## Pre-registration R1–R5 (P1–P5 analogues, fixed in advance, UNEXECUTED)

No hypothesis-testing query has run against the dump; only schema/count/join-integrity
probes. Unit convention: mass by normalised siglum; denominators recomputed on a dated
re-clone at run time.

| ID | Analogue | Hypothesis (falsifier) | Denominators |
|---|---|---|---|
| **R1** | P1 right-skewed citation mass | Mass per cited siglum is extreme-right-skewed; Biblical/Psalter-class sigla concentrate in the top decile, near-zero tail. (Falsifier: top-decile share <2× uniform, or linear decile profile.) | 24,405 examples; joined 10,318; siglum universe from joined subset |
| **R2** | P2 complete-vs-selective density | Declared-complete canonical texts (Библ.-class) show an order-of-magnitude density advantage over same-genre selective sources. **No declared complete-excerption list exists in the dump — if none is recoverable from the printed front matter, R2 is reclassified UNTESTABLE-ON-THIS-SUBSTRATE before the run, never silently adapted.** | Библ.-group vs Bible-genre-flagged non-canonical rows |
| **R3** | P3 partial-apparatus artefact | Source-density rankings on the С-half vs Т-half of the SAME dump diverge materially (Spearman ρ « 1 on shared sigla) — demonstrating that partial-apparatus results are apparatus artefacts (the direct in-dump analogue of the ONP a–em 2.6× lesson). | С-prefix vs Т-prefix word subsets; shared-siglum vectors |
| **R4** | P4 weighting divergence | Headword-, meaning-, example- and siglum-weighted rankings diverge materially. (Falsifier: coincidence — metric choice then carries no information.) | 6,307 / 8,858 / 24,405 / siglum universe; Spearman ρ + top-100 Jaccard |
| **R5** | P5 absence predictability | Which declared sources are never exercised is predictable from genre/date/Lang profile (logistic model), not random; the 14,087-example unjoined residue is systematic, not noise. | 8,400 declared; exercised sigla; residue 24,405−10,318 |

**Gate before any run fires:** a dated permission / written licence for the ИРЯ РАН
data, or an explicit MG ruling that hash-verified private analysis of the unlicensed repo
dump is in scope. Without one of these the run does not fire — mirroring ONP's
rank-1-conditional posture.

## Bias register — §11 adaptations for this source class

1. **Scrape-vs-deposit provenance**: the structured path is a code-repo artefact, not a
   published dataset; the identity tie (footer + style.css + data generation) must be
   re-verified at run time because the repo can silently diverge from the deployed DB.
2. **Licence ambiguity**: free access ≠ reuse rights; gate above.
3. **Anti-bot fragility**: the executing LAN cannot reach web-corpora.net at all
   (documented interference); reader services suffice today but rotate — every live
   verdict needs ≥2 external networks (H7507 precedent); `/lists` is a single-point
   bulk surface.
4. **Catalogue rot**: live count drifts (6,307→6,284 over 8.7 y); a run pins to the dump
   hash, not the live count.
5. **Siglum-vs-Id duality**; 6. **join incompleteness as structure** (no genre/date claim
   on the unjoined subset without mining `Words.Full`); 7. **partial apparatus** (С–Т
   only); 8. **sparse axes dump-side** (genre 31.8%, Time1 27.4%, Lang ~0.2% — the live
   DB may be richer; unverifiable without the licence gate).

## Probe index (all dated; bodies in [probe_evidence/](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/stage4b_russian/probe_evidence/))

- GitHub repo search + code search (LAN, gh) — did not surface the project; the
  interface-credit path resolved it.
- Repo metadata + clone + DB sha256 (LAN, GitHub reachable) —
  [github_repo_census_2026-10-30.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/stage4b_russian/probe_evidence/github_repo_census_2026-10-30.md).
- Deployed↔repo identity, three strands —
  [deployed_code_identity_2026-10-30.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/stage4b_russian/probe_evidence/deployed_code_identity_2026-10-30.md).
- Live `/` (axis-set stability vs census fetch) —
  [oldrus_wsgi_live_2026-10-30.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/stage4b_russian/probe_evidence/oldrus_wsgi_live_2026-10-30.md).
- Live `/lists` (6,284 headwords, span, footer) —
  [oldrus_lists_live_2026-10-30.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/stage4b_russian/probe_evidence/oldrus_lists_live_2026-10-30.md).
- Dead-path `/about`: reader 500 / fetcher timeout — no verdict either way; route absent
  from source; not load-bearing.

Reversal conditions from §9 stay live; the ONP gate stays independently monitored (not
this stage). The committed DB is **not** redistributed here (no licence) — hash, schema
and counts only.

_Dr. Mārcis Gasūns_
