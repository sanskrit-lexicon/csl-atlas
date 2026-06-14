# Dharmamitra integration — monthly plan

A detailed, sequenced programme for integrating [Dharmamitra](https://github.com/dharmamitra)
assets into the Cologne dictionaries via this atlas. Companion to
[DHARMAMITRA_INTEGRATION.md](DHARMAMITRA_INTEGRATION.md) (the architecture + opportunity list)
and [MITRA_ALIGNER_HANDOFF.md](MITRA_ALIGNER_HANDOFF.md) (the DTB spec).

Dates are relative ("Month 1" = the first month work resumes). Each month is scoped to land at
least one mergeable PR with a measurable definition of done. Everything obeys the
**non-negotiable rule**: model output is *review evidence*, never a silent input to the
deterministic build, and the atlas never edits `csl-orig` directly.

---

## Where we are (baseline)

Already merged to `main` (six PRs):

| Capability | Tool | State |
|---|---|---|
| Gender cross-check (#89) | ByT5 morphosyntax | scaffold, **model-pending** |
| Source-layer anchoring (#90) | sanskrit-dating | **real data** (1,618 works) |
| Compound-depth cross-check (#91) | ByT5 `unsandhied` | scaffold, **model-pending** |
| Lemma-normalization cross-check (#92) | ByT5 `lemma` | scaffold, **model-pending** |
| Shared `dharmamitra_infer.py` (#94) | — | done |
| PWG markup cross-check (#95) | detect-language | **real data**, low precision (demonstrator) |

**The single biggest gap:** three queues are scaffolds with zero findings until someone runs
the ByT5 model on a GPU. Month 1 fixes that. **The biggest external blocker:** DTB link-targets
need digital source corpora the repo doesn't have (Month 2 / handoff).

---

## Cross-cutting principles (apply every month)

1. **Two-step pattern**: networked `import-*` → committed snapshot under `src/data/external/`;
   deterministic `build-*-review.mjs` → schema-conforming review queue.
2. **Each integration is its own PR off `main`** (isolated; compose on merge). Batch schema-enum
   PRs to avoid repeated one-line conflicts.
3. **Gitignore large intermediates**; commit the review queue (the durable artifact).
4. **Pin model/data revisions** in snapshot provenance for reproducibility.
5. **Every queue ships a trust block**: evidence, method, a measured precision/coverage number,
   and limitations. No queue is presented as confirmed errors.
6. **Reuse the shared module**; grow `scripts/lib/dharmamitra_infer.py` rather than duplicate.

---

## Month 1 — Activate the model-pending queues (highest value)

**Objective:** turn the gender, compound-depth, and lemma scaffolds from `model-pending` into
real findings by running the ByT5 model once each, then triaging.

**Tasks**
- Provision a GPU (Colab/HF Spaces/local) or use the PyPI remote API for a first pass.
- Run, pinning a commit revision of `chronbmm/sanskrit5-multitask`:
  - `import-dharmamitra-morphology.py --source local --revision <sha>` → gender snapshot.
  - `import-dharmamitra-segmentation.py --source local --revision <sha>` → segmentation snapshot.
  - `import-dharmamitra-lemma.py --source local --revision <sha>` → lemma snapshot.
- Re-run the three `build-*-crosscheck.mjs`; commit the now-populated review queues.
- Decide snapshot policy: commit if small, else gitignore (lemma 1,913 and gender 4,556 are
  committable; segmentation 3,496 likely too, with `segments` arrays — measure).
- Manually score the top confidence band of each (≥100 items) → write precision into trust blocks.

**Deliverables:** 3 PRs (or one batched), each flipping a queue to real verdicts with a measured
precision number. **DoD:** `model-favors`/`agree`/`disagree`/etc. counts are non-zero and
schema-valid; gender cross-check resolves a documented share of the 4,556 conflicts.

**Risks:** ByT5 output format drift (tighten `extract_gender` / `head_gender` after eyeballing
`raw`); remote API rate limits → prefer local. **No new external data needed** — lowest-risk,
highest-value month.

---

## Month 2 — DTB link-targets pilot (mitra-aligner)

**Objective:** prove the citation→passage pipeline end-to-end for **one** source. Driven by
[MITRA_ALIGNER_HANDOFF.md](MITRA_ALIGNER_HANDOFF.md).

> **Pilot DONE (2026-06-14, PR #102) — and it reframed the problem.** The first source (Ṛgveda)
> showed that the *high-value* link-target path needs **no alignment at all**: MW cites RV with
> an **explicit locus** (`<ls>RV. v, 86, 5</ls>` = 5.86.5), so the link is just locus-parsing →
> a stable digital-edition URL. [`build-citation-link-pilot.mjs`](../scripts/build-citation-link-pilot.mjs)
> parses MW's 15,916 RV citations and emits **3,996 distinct verse links** to **VedaWeb**
> (`vedaweb.uni-koeln.de`, zero-padded `MMHHHVV` stanza id; a sampled link resolves 200) as a
> `citation-link-target` review queue, range-checked against the RV maṇḍala/hymn structure.
> Breakdown of the 15,916: 5,738 explicit-verse, 9,707 bare `RV.` (work-level), 354 hymn-level,
> 79 maṇḍala-only, ~38 malformed/out-of-range. **So mitra-aligner is NOT needed for
> explicit-locus citations** — it is for the *residual* (quote-only / vague citations) and for
> sources without a clean locus scheme, which still need the source corpus + the alignment API
> below. Remaining pilot work: a per-hymn verse-count table (tighten verse validation),
> link-splitting for combined refs, and extending to a non-explicit-locus source to exercise
> mitra-aligner proper.

**Tasks**
- Resolve the open question: does Dharmamitra expose a retrieval/embedding endpoint or only
  pairwise bertalign? Choose the importer design accordingly.
- Inventory digital source texts (GRETIL/DCS/SARIT); pick one dense, well-digitized source
  (RV or MBh) using `citation-apparatus.json`.
- Build `build-citation-link-candidates.mjs` (extract `<ls>` + `{#quote#}` + locus, resolve
  siglum, keep sources with a known text).
- Build `import-dharmamitra-alignment.py` (retrieve/align quotes vs source) and
  `build-citation-link-review.mjs` (emit `citation-link-target` queue).
- Normalize SLP1↔IAST and sandhi on both sides; measure top-band precision on 100 items.

**Deliverables:** one source's `citation-link-target` review queue + schema additions
(`citation-link-target`, `citation` kind). **DoD:** §7 of the handoff.

**Risks:** source-text availability is the gate; encoding/sandhi/locus-scheme mismatch; client
throughput. If blocked on source texts, this month becomes "secure + normalize the source
corpus" and the alignment slips to Month 3.

---

## Month 3 — Deepen chronology + corpus-frequency evidence

**Objective:** push source-layer dating from coarse bands to per-source anchoring, and add
corpus-frequency evidence from the dharmanexus datasets.

**Tasks**
- **Per-siglum dating:** join `dharmamitra-chronology.json` to individual `<ls>` sources (not
  just the 6 layer bands) via a siglum→work-title match (reuse the alias table); emit a
  `source-date-anchor` review queue proposing a date per resolved siglum, with the
  authorial-vs-editorial caveat. Shrinks the 449 `unknown` source-layer items.
- **Corpus frequency:** evaluate [dharmanexus-sanskrit](https://github.com/dharmamitra/dharmanexus-sanskrit)
  / dharmanexus for a committable per-lemma frequency band; if usable, wire a
  `import-dharmamitra-frequency` snapshot feeding the learner/lemma pages (coordinate with the
  existing `dcs_lemma_summary.json` consumer to avoid duplication).

**Deliverables:** `source-date-anchor` review queue; a frequency snapshot + one page or queue.
**DoD:** measurable reduction in `unknown` source layers; frequency bands shown with provenance.

**Risks:** siglum→work-title matching is fuzzy (keep it review-gated); dharmanexus licensing and
format must be verified before redistribution.

---

## Month 4 — Distribution: StarDict / GoldenDict export

**Objective:** emit the Cologne dictionaries (or the atlas's comparative layer) in
StarDict/GoldenDict format, learning from
[dharmamitra-stardict-dictionaries](https://github.com/dharmamitra/dharmamitra-stardict-dictionaries).

**Tasks**
- Add `build-stardict-export.mjs` (or Python via `pyglossary`) that reads `csl-orig`/atlas JSON
  and writes `.ifo/.idx/.dict` (or a `pyglossary`-driven build).
- Ship with an explicit *"generated, verify before scholarly use"* disclaimer, matching the
  atlas [evidence-labels](EVIDENCE_LABELS.md) discipline.
- CI artifact + a download page; CC-BY-SA-4.0 attribution to CDSL.

**Deliverables:** a reproducible StarDict build for ≥1 dictionary (MW first) as a release
artifact. **DoD:** the file opens in GoldenDict with correct headwords/senses; build is in CI.

**Risks:** sense/markup → gloss flattening fidelity; size. This is **independent of the model
work** — good buffer month if GPU/source-text access slips.

---

## Month 5 — Fix detect-language precision (German/Sanskrit model)

**Objective:** replace the off-the-shelf eng-vs-skt classifier (PWG markup check, #95, is a
low-precision demonstrator) with a model that actually separates German from Sanskrit.

**Tasks**
- Train/extend a SentencePiece (or small classifier) with a **German** model alongside
  eng/skt, or a 3-way Sanskrit/German/other classifier, using PWG's own `{#...#}` (Sanskrit) and
  `{%...%}` (German) as labeled data — the markup *is* the training set.
- Swap it behind `import-dharmamitra-langdetect.py` (the infrastructure already exists); re-run
  both directions; re-measure precision.
- Promote the PWG markup queue from "demonstrator" to a real QA queue if precision clears a bar
  (e.g. ≥80% top band), feeding `csl-corrections`.

**Deliverables:** a German-aware classifier + a re-measured, higher-precision
`langdetect-markup-crosscheck` queue. **DoD:** documented precision lift vs the #95 baseline.

**Risks:** training effort/scope; this is the most research-y month. The PWG markup is
conveniently self-labeling, which de-risks it. Could be deferred if lower priority than Months
1–4 outcomes.

---

## Month 6 — Benchmarking, syntax enrichment, consolidation

**Objective:** measure quality, add one new ByT5 capability, and harden the programme.

**Tasks**
- **Benchmark:** stand up evaluation against
  [dharmamitra-leaderboard](https://github.com/dharmamitra/dharmamitra-leaderboard) for the
  lemma/segmentation cross-checks (precision/recall on a gold sample).
- **Dependency parsing:** evaluate the `applications/dependency-parsing` model from
  byt5-sanskrit-analyzers to enrich compound/syntactic analysis (e.g. validate compound *head*
  detection used in the gender cross-check's `head_gender`).
- **Consolidation:** refactor the langdetect importer onto a shared SPM helper if a second SPM
  use appears; add a CI check that re-runs `validate-review-reports`; refresh
  [DHARMAMITRA_INTEGRATION.md](DHARMAMITRA_INTEGRATION.md) status; consider a TEI/OntoLex export
  of the review decisions to `csl-standards`.

**Deliverables:** a benchmark report; a dependency-parse pilot or a documented decision to skip;
a consolidated, CI-guarded integration surface. **DoD:** every queue has a quality number; docs
current; CI green.

---

## Backlog (unscheduled / opportunistic)

- **Agentic translation** — [dharmamitra-claude-code-agent](https://github.com/dharmamitra/dharmamitra-claude-code-agent)
  patterns for driving these pipelines from an agent loop.
- **Parallel data** — [mitra-parallel](https://github.com/dharmamitra/mitra-parallel) /
  Sanskrit-Tibetan pairs for cross-lingual sense validation of dictionary glosses.
- **Pāli** — `paltok` / dharmanexus-pali; out of scope for the Sanskrit lexica unless a
  Pāli-adjacent dictionary is added.
- **link-splitting** — the second half of DTB (split combined `<ls>` refs), naturally follows
  Month 2's link-target pilot.

---

## Risk register (programme-level)

| Risk | Impact | Mitigation |
|---|---|---|
| No GPU access | Months 1, 6 stall | PyPI remote API for a first pass; pin a revision later |
| No digital source corpora | Month 2 blocked | Inventory GRETIL/DCS first; StarDict (M4) as buffer |
| Model output format drift | wrong verdicts | tighten post-processing after eyeballing `raw`; pin revisions |
| Large snapshots in git | repo bloat | gitignore intermediates; commit only review queues |
| Schema-enum merge conflicts | rebase churn | batch schema-touching PRs |
| Over-trusting model output | bad corrections | review-gate everything; never auto-edit `csl-orig` |
| Licensing of redistributed data | compliance | verify upstream terms; consume as evidence, not redistribution |

## Sequencing rationale

Month 1 first because it converts existing, merged scaffolding into value with **no external
dependency** — pure upside. Month 2 (DTB) is highest *strategic* value but gated on external
corpora, so it runs second and can slip without stalling the programme. Months 3–6 are ordered
to keep an unblocked, independently-valuable task available each month (chronology, distribution,
model-quality, measurement), so the programme never idles waiting on one blocker.
