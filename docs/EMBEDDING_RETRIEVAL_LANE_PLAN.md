# Embedding quote-retrieval lane plan — semantic retrieval for citation verification (W2+)

_Created: 11-07-2026 · Last updated: 11-07-2026_

**What this is.** The plan-of-record for the **embedding lane** of the citation-verification
program's quote-retrieval track — ruling **R1** of
[`docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md)
§2a deliberately kept embeddings **out** of W1a (the pipeline stays deterministic) and ordered
this lane *planned from the start, adopted where character-fuzzy saturates* (MG: "do Fable
planning for Embeddings from the start as Dharmamitra has"). This is a plan, not a pipeline:
no code ships with it. Executed under
[H662](https://github.com/gasyoun/Uprava/blob/main/handoffs/H662-Fable_csl-atlas_embedding-retrieval-lane-plan_11.07.26.md).

## 1. Where character-fuzzy saturates — the measured target population

The W1a MBH census
([`data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md),
H610) ran the deterministic lane — SLP1-normalized 4-gram fuzzy search of each note's quoted
pratīka across the whole BORI text (72,771 verses), locus-free — over **2,466** Böhtlingk
correction notes:

| Evidence tier (W1a, deterministic) | Notes | Share |
|---|--:|--:|
| quote-exact | 648 | 26.3 % |
| quote-fuzzy (≥ 0.85 4-gram coverage) | 308 | 12.5 % |
| lemma (≥ 0.50) | 422 | 17.1 % |
| **none (< 0.50)** | **1,088** | **44.1 %** |

The **1,088 `none` notes are the embedding lane's target population**, and they conflate two
states the deterministic lane cannot separate:

- **(a) recension gap** — BORI, a shorter critical recension, genuinely lacks the parallel.
  No retrieval method recovers these; they are the
  [DEAD_ENDS §8/§8b](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)
  structural residue, addressable only by a vulgate e-text (D3 / Calcutta OCR).
- **(b) paraphrase-level reuse** — the parallel *is* in BORI but beyond 4-gram reach:
  inflectional variance across several words, pāda-order permutation, synonym substitution in
  formulaic verse. This is precisely what dense retrieval recovers and n-grams do not.

Since the fuzzy lane already searched the **whole corpus** for the **best** match, anything it
scored `none` has 4-gram coverage < 0.50 against every BORI verse — so every genuinely new
embedding recovery is, by construction, a paraphrase-class hit that no threshold tuning of the
character lane could reach. Secondary target: upgrading the 422 weak `lemma` hits to verse-level
evidence. The Harivaṃśa census's 37.7 % corroboration ceiling (H488) shows the same saturation
shape. How much of the 1,088 is (b) rather than (a) is **unknown and is the pilot's first
measurable** — the honest expectation is modest (BORI's cuts are real), which is why the lane is
adopted only if the §5 criterion is met.

## 2. Tech survey — consume, don't rebuild

| Stack | What it is | Weights/code | Local? | License | Fit |
|---|---|---|---|---|---|
| **MITRA-E** ([arXiv 2601.06400](https://arxiv.org/abs/2601.06400), 01-2026) | Gemma-2-9B contrastively fine-tuned sentence embedder for Sanskrit/Pāli/Buddhist-Chinese/Tibetan; SOTA on 7 retrieval tasks (Sanskrit→Sanskrit and cross-lingual, P@1 up to 95) | [`buddhist-nlp/gemma-2-mitra-e`](https://huggingface.co/buddhist-nlp/gemma-2-mitra-e) via [dharmamitra/mitra-parallel](https://github.com/dharmamitra/mitra-parallel) | **yes** (downloadable) | repo + corpus CC BY-SA 4.0; weights additionally under Gemma Terms of Use (Gemma-2 derivative) | **primary candidate** — the exact "as Dharmamitra has" tech, current generation |
| ByT5-Sanskrit ([EMNLP 2024 Findings](https://aclanthology.org/2024.findings-emnlp.805/); Nehrdich, Hellwig, Keutzer) | byte-level multitask model: segmentation, lemmatization, morphosyntax | [`chronbmm/sanskrit5-multitask`](https://huggingface.co/chronbmm/sanskrit5-multitask), **already vendored in-house** at pinned revision `c0d2ada` via [`scripts/lib/dharmamitra_infer.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/dharmamitra_infer.py) | yes (in use) | CC BY-SA 4.0 side | not an embedder — the **preprocessing normalizer** (sandhi segmentation before embedding, §4 ablation) |
| BuddhaNexus → DharmaNexus | production million-scale intertextuality graph (the operational proof the approach scales); frontends archived, relaunched as DharmaNexus 07-2025 within the [MITRA tool suite](https://dharmamitra.github.io/dharmamitra-guides/news/) | [BuddhaNexus org](https://github.com/BuddhaNexus/) — backend GPL-3.0; inputs are **segmented** text ([segmented-sanskrit](https://github.com/BuddhaNexus/segmented-sanskrit)) | service, no public API | GPL-3.0 (code) | **reference architecture, not a dependency** — query/compare, never vendor GPL code (house rule, cf. the Samsaadhanii/SCL precedent); no API ⇒ not pipeline-usable anyway |
| SansTib ([LREC 2022](https://aclanthology.org/2022.lrec-1.724/)) | Sanskrit–Tibetan bilingual sentence embeddings + the alignment method behind BuddhaNexus's Sanskrit side | per paper | yes | research release | superseded by MITRA-E (same lineage, same author); cite as method ancestry |
| Vedic similarity measures ([NLP4DH 2024](https://aclanthology.org/2024.nlp4dh-1.12/); Miyagawa et al.) | word2vec + stylometry + TRACER compared on Vedic intertextuality | per paper | yes (word2vec-class) | research release | two transferable lessons: **smaller chunks detect parallels better** (embed at verse/pāda granularity, not entry level), and cheap word2vec-class vectors are a legitimate **CPU-only floor baseline** for the pilot |
| FAISS | exact/ANN vector search | [faiss](https://github.com/facebookresearch/faiss) (`faiss-cpu`) | yes | MIT | index layer; at our scale **exact search only** (§3) |

**API-only vs downloadable.** The MITRA *services* (Explore/Search, Deep Research, DharmaNexus)
have **no public API** — but this costs nothing: house invariants (§3) forbid runtime service
calls in the pipeline anyway. The *models* are downloadable, and local frozen inference is the
only house-compatible route. **Nothing needs to be built from scratch**: model (MITRA-E),
normalizer (in-house ByT5 harness), index (FAISS), corpus (the W1a frozen BORI harvest), and
query set (the 2,466-note verdict CSV) all exist.

## 3. Fit to house invariants — offline, versioned, cached; never a runtime service

The atlas already has the governing rule and the working pattern, both from
[`docs/DHARMAMITRA_INTEGRATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/DHARMAMITRA_INTEGRATION.md):
model outputs are **probabilistic** and enter the atlas as **review evidence only, never a
silent input to the deterministic figure build**; every integration is a networked one-off
`import-*` step writing a committed, provenance-stamped snapshot, then a deterministic
`build-*` step over that snapshot (five such integrations merged: PRs
[#89](https://github.com/sanskrit-lexicon/csl-atlas/pull/89) ·
[#90](https://github.com/sanskrit-lexicon/csl-atlas/pull/90) ·
[#91](https://github.com/sanskrit-lexicon/csl-atlas/pull/91) ·
[#92](https://github.com/sanskrit-lexicon/csl-atlas/pull/92) ·
[#95](https://github.com/sanskrit-lexicon/csl-atlas/pull/95)). The embedding lane instantiates
the same two steps:

1. **Import (one-off, GPU, outside every build path).** `import-embedding-retrieval.py`
   embeds the **frozen corpus** (the W1a-normalized BORI verse file, content-hashed) and the
   **frozen query set** (quoted pratīkas from
   [`mbh_note_verdicts.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_note_verdicts.csv))
   with a **pinned model revision** (the `PINNED_REVISION` discipline of
   [`dharmamitra_infer.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/dharmamitra_infer.py)
   — never a moving `main`), runs **exact** (flat, non-approximate) cosine search, and writes:
   - *gitignored*: the embedding matrices (~0.5 GB fp16 for 73k verses, dim 3584);
   - *committed*: a **numbers-only neighbor table** (note ID → top-k BORI locus IDs + scores,
     rounded to a stated tolerance) plus a manifest stamping model ID, revision, corpus SHA-256,
     query-set SHA-256, k, metric, library versions.
2. **Build (deterministic).** A `build-*-review.mjs` step joins the committed neighbor table to
   the verdict layer and emits a **review queue** via the existing
   [`review-report.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/review-report.mjs)
   schema — candidates for humans, not verdicts.

**Reproducibility contract.** Frozen (model revision, corpus hash, query hash, k, metric) →
identical ranks. Exact search removes ANN nondeterminism entirely — at 73k vectors a flat
cosine scan is a single small matrix product, so approximate indexes (IVF/HNSW) are banned at
this scale, revisited only if the corpus grows a hundredfold. Float nondeterminism across
GPUs is real but sub-tolerance; scores are committed **rounded**, and rank ties are broken by
locus ID. Re-import is a deliberate act that bumps the manifest, exactly like a `PINNED_REVISION`
bump.

**Verdict-layer discipline (extends R3, does not bend it).** Embedding rank is **retrieval,
not evidence**. A semantic candidate enters the committed verdict layer only after passing a
**deterministic or adjudicated** confirmation:

- retrieved verse re-scored by the *existing* W1a 4-gram scorer against the quote — a
  candidate that lands ≥ 0.50 coverage upgrades along the **existing** tiers (`lemma`);
- below that, only R2-style adjudication (blind LLM second annotator + human, the A44
  discipline) can confirm it, and a confirmed paraphrase-class hit takes a **new evidence
  tier `quote-semantic`**, ranked between `quote-fuzzy` and `lemma`, carrying *both* the
  embedding score *and* the deterministic coverage in the benchmark schema. Unadjudicated
  candidates never leave the review queue.

**Never a runtime service.** No embedding call in `npm run build`/`sync-site-data`; the site
consumes committed JSON only. The DEAD_ENDS §8 invariant carries over verbatim: embeddings
supply **reading evidence, never locus arithmetic**.

## 4. Where it beats character-fuzzy — expected gains per text class

- **MBH `none`-tier re-scan (first pilot, cheapest).** Corpus and queries are already frozen;
  the run is pure §3 import. Payoff: splits §1's (a) from (b) and produces the first measured
  paraphrase-recovery rate. Formulaic epic verse (repeated pādas, one-synonym substitutions)
  is embedding-friendly; the counterweight is that many of the 1,088 are true recension gaps.
- **W2 Rāmāyaṇa (the roadmap's named adoption point).** Three edition families
  (Schlegel/Gorresio/Bombay) whose divergence *is* variant-reading and paraphrase — the case
  §2a's R1 names ("paraphrase-level reuse, W2+"). PWG's 23,286 `R.` + `R. GORR.` refs give the
  lane its first *designed-for* workload rather than a salvage pass.
- **Sprüche cross-edition (W1b follow-on).** ed.1/ed.2 verse variants where 4-grams fray;
  small corpus, near-zero cost once the harness exists.
- **Weak fits, named honestly:** kośa/definitional strings and *single-word* corrections (the
  `abravat → abravīt` class) — spans too short for sentence embeddings to discriminate; these
  stay with the deterministic lane and the D3 spot-check cascade. Cross-lingual retrieval
  (MITRA-E's Sanskrit↔Tibetan/Chinese strength) is out of program scope; noted only as a
  future affordance.
- **Input-form ablation (pilot decides, not assumed):** raw continuous SLP1→IAST vs
  ByT5-segmented input. BuddhaNexus embeds **segmented** text; our quotes are unsegmented
  print-form. The pilot runs both on the parity set (§5) and keeps the winner — one more reuse
  of the in-house ByT5 harness, zero new tooling.

## 5. Evaluation design — silver data from W1a, baselines per R3

The W1a verdict layer is the free silver standard; no annotation is needed to *start*.

1. **Parity gate (trust check).** Queries = the 956 fuzzy-confirmed notes (648 quote-exact +
   308 quote-fuzzy), gold = the BORI locus the fuzzy lane found. Metric: recall@1/5/10.
   **Gate: embedding recall@10 ≥ 0.95 on quote-exact notes** — a dense retriever that cannot
   re-find verbatim quotes is misconfigured (wrong input form, wrong pooling) and the lane
   stops there. Run once per input-form ablation arm (§4).
2. **Payoff run (the actual question).** Queries = 1,088 `none` + 422 `lemma` notes; top-k
   candidates → deterministic re-score → adjudication subsample: ~100 candidates stratified by
   score band, blind LLM second annotator per R2/A44, agreement + confusion reported.
   Deliverables: paraphrase-recovery count, precision per score band, and a calibrated score
   threshold for the review queue.
3. **Baselines table (R3's anti-circularity requirement).** `fuzzy-only` (exists) vs
   `embedding-only` vs `hybrid` (union; embeddings retrieve → determinism verifies) on the
   same 2,466 refs — plus the **word2vec-class CPU floor** (§2, NLP4DH 2024 lesson) so the
   9B model's margin over a trivial baseline is measured, not presumed. Publishable
   numbers-only, feeding the R3 benchmark datasheet and A50.
4. **Adoption criterion (what "clears it" means for W2).** Adopt the lane if the pilot
   (i) passes the parity gate, and (ii) confirms **≥ 25 genuinely new paraphrase-class
   parallels** (≈ 2.3 % of the `none` tier) at ≥ 60 % adjudicated precision in the top score
   band. Below that, the lane is shelved with its numbers written back here — a measured
   dead end beats a standing aspiration (the DEAD_ENDS discipline).

## 6. DharmaMitra engagement plan (R4)

R4's gate — "after W1a produces concrete pilot numbers" — **is now satisfied**. The engagement
brief for [`/outreach-draft`](https://github.com/gasyoun/claude-config/blob/main/commands/outreach-draft.md)
(never auto-sent; MG sends):

- **Who:** Sebastian Nehrdich (Distinguished Assistant Professor, Tohoku University, since
  10-2025; [sebastian-nehrdich.github.io](https://sebastian-nehrdich.github.io/)) — DharmaMitra
  lead; note the existing touchpoint: five merged atlas integrations of their models
  ([`docs/DHARMAMITRA_INTEGRATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/DHARMAMITRA_INTEGRATION.md)),
  and that his [ISCLS 2026 gloss-WSD paper](https://aclanthology.org/2026.iscls-1.2/) with
  Hellwig works the DCS side of the same lexicographic ground.
- **The opener (numbers, not intentions):** 66,103 PWG + 29,178 MW MBH loci censused; 2,466
  Böhtlingk correction notes mined; 956 (39 %) confirmed against BORI by deterministic
  retrieval; 1,088 paraphrase-or-gap notes as the embedding target; MITRA-E already selected
  as primary candidate.
- **The asks:** (i) domain-shift guidance — MITRA-E is trained Buddhist-corpus-heavy; any
  known behavior on classical/epic Sanskrit, and is a small contrastive fine-tune on epic
  parallels sensible? (ii) pooling/input-form recommendation for unsegmented print-form
  quotes (§4 ablation); (iii) any Sanskrit-only retrieval eval sets beyond the MITRA paper's
  5,552 pairs; (iv) interest in the R3 benchmark as a co-authored resource paper
  (LaTeCH-CLfL / NLP4DH venues) — a citation-verification benchmark is adjacent to, not
  competitive with, their intertextuality graph.
- **The offers:** the frozen benchmark dataset (numbers-only, public-domain gloss text); the
  CDSL-side citation graph as a DharmaNexus layer candidate; adjudicated paraphrase pairs as
  contrastive training data (CC BY-SA-compatible both ways).
- **Timing judgment:** the gate is open now, but the letter is strictly stronger *after* the
  §5 pilot — "here is what your model recovered on our data" beats "we plan to try your
  model". Recommended order: pilot first, then draft. If W2 scheduling forces earlier contact,
  the W1a numbers above already carry the letter.

## 7. Cost / dependency ledger

| Item | Estimate | Notes |
|---|---|---|
| MITRA-E weights | ~18–20 GB (bf16, Gemma-2-9B) | needs ≥ 24 GB VRAM GPU for comfortable batched inference; int8 (~10 GB) feasible but quantization changes scores — if used, the quantization method+version joins the manifest (§3) |
| Embedding pass | 73k verses + ~2.5k queries ≈ 1–2 GPU-hours, one-off | **no suitable local GPU assumed**: one-off cloud run (Colab/RunPod-class, ~$5–15) or a DharmaMitra collaboration run (§6 ask) — the artifact is what's kept, not the machine |
| CPU floor baseline | minutes, local | word2vec/fastText-class (§5.3); no GPU dependency |
| Search | trivial | 73k × 3584 flat cosine = CPU-fine with `faiss-cpu` (MIT) or plain NumPy |
| Storage | ~0.5 GB fp16 matrices, **gitignored** | committed: neighbor table + manifest only (KB–MB). If released as a dataset, it routes through the [kosha manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) + [`/publish-safety-check`](https://github.com/gasyoun/claude-config/blob/main/commands/publish-safety-check.md) |
| New Python deps | `torch`, `transformers`, `faiss-cpu` | import-step only, never in the site build; pinned in the import script header per house pattern |
| Rights | carried over unchanged | harvested e-text bytes stay gitignored; embedding **matrices of** those bytes stay gitignored with them (conservative reading); published artifacts are numbers-only (locus IDs, scores, verdicts). Model side: CC BY-SA 4.0 (DharmaMitra) + Gemma Terms of Use (weights) — both compatible with local research inference and numbers-only publication |

## 8. Sequencing and non-goals

**Sequencing:** this plan (done) → §5 pilot as a W2-entry handoff (mint at W2 time, per the
roadmap's wave discipline) → adoption iff §5.4 clears → Rāmāyaṇa as first designed-for
workload → outreach draft after pilot numbers (§6).

**Non-goals:** no embedding lane in W1 (deterministic-only, per R1); no runtime semantic-search
service on the atlas; no GPL code vendored from BuddhaNexus; no locus arithmetic from
embeddings (DEAD_ENDS §8); no model training (fine-tuning is a §6 conversation, not a plan
item); no rebuilding of segmenters/lemmatizers/transcoders the org already owns.

## 9. Provenance

Authored 11-07-2026 by Fable 5 (`claude-fable-5`) under
[H662](https://github.com/gasyoun/Uprava/blob/main/handoffs/H662-Fable_csl-atlas_embedding-retrieval-lane-plan_11.07.26.md)
(minted by H661's §2a ruling round). Evidence: the W1a census + verdict CSV (H610), the five
merged DharmaMitra integration PRs, [DEAD_ENDS §8/§8b](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md),
and a same-day web survey of [arXiv 2601.06400](https://arxiv.org/abs/2601.06400),
[dharmamitra/mitra-parallel](https://github.com/dharmamitra/mitra-parallel),
[BuddhaNexus](https://github.com/BuddhaNexus/), the
[DharmaMitra news feed](https://dharmamitra.github.io/dharmamitra-guides/news/), and
[sebastian-nehrdich.github.io](https://sebastian-nehrdich.github.io/). Improvement backlog for
this doc lives with the program metadoc,
[`CITATION_VERIFICATION_ROADMAP_2026_2027.meta.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.meta.md).

_Dr. Mārcis Gasūns_
