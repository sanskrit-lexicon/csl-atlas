# Learning from Dharmamitra

[Dharmamitra](https://github.com/dharmamitra) is the computational/NLP counterpart to
Cologne's philological/source strength: an organization doing Sanskrit segmentation,
lemmatization, morphology, parallel-text alignment, and text dating with trained models.
Both sides ship under **CC-BY-SA-4.0** and are Sanskrit-first, so their model outputs and
our deterministic source analysis interoperate cleanly — *as long as we keep the boundary
below.*

This document records what we have already wired in, the rule that governs any further
integration, and the remaining opportunities mapped to concrete atlas structures.

---

## The architectural rule (non-negotiable)

Dharmamitra outputs are **probabilistic model predictions**. They enter the atlas as
**review evidence only** — feeding a review queue or an external snapshot a human reads —
and **never as a silent input to the deterministic figure build**. This preserves the
reproducibility guarantee in [the README](../README.md): every figure regenerates from
committed JSON plus `csl-orig`, with no LLM inference in the build path.

Concretely, every integration follows the **two-step pattern**:

1. A networked **`import-*` step** that calls the model/API once and writes a committed
   snapshot under `src/data/external/` (created on first run), stamped with provenance
   (model, revision, date, license). Normal builds never re-call it.
2. A deterministic **`build-*-review.mjs` step** that joins that snapshot to atlas data and
   emits a schema-conforming review queue via [`scripts/lib/review-report.mjs`](../scripts/lib/review-report.mjs),
   preserving human decisions by `reviewId`.

---

## Already wired

| Capability | Source repo | Import step | Consumer |
|---|---|---|---|
| **Gender cross-check** | [byt5-sanskrit-analyzers](https://github.com/dharmamitra/byt5-sanskrit-analyzers) | [`scripts/import-dharmamitra-morphology.py`](../scripts/import-dharmamitra-morphology.py) → `src/data/external/dharmamitra-morphology.json` | [`scripts/build-gender-model-crosscheck.mjs`](../scripts/build-gender-model-crosscheck.mjs) → `pos-gender-model-crosscheck` review queue |

> **Prior art:** a chronology importer (`import-dharmamitra-chronology.mjs` →
> `src/data/external/dharmamitra-chronology.json`, from [sanskrit-dating](https://github.com/dharmamitra/sanskrit-dating))
> was prototyped earlier and established the two-step pattern, but is **not currently in the
> tree**. Opportunity 1 below is the path to reinstating it.

The gender cross-check adds an **independent third vote** to the existing cross-dictionary
gender-conflict queue: for each conflicted headword, the ByT5 morphosyntax model's predicted
gender is compared against each dictionary's asserted gender (`model-favors` / `model-diverges`
/ `model-concurs` / `model-pending`). It runs `chronbmm/sanskrit5-multitask` either via the
PyPI `dharmamitra-sanskrit-grammar` remote API or a pinned local HF model, with
[`scripts/sanskrit_tags.tsv`](../scripts/sanskrit_tags.tsv) vendored for fully offline tag
expansion. (Currently isolated in its own PR off `main`.)

---

## Opportunities (not yet built)

Ordered roughly by value-to-effort. Each maps a Dharmamitra asset to a *specific* atlas or
Cologne structure, with the caveat that matters.

### 1. Anchor source layers with `sanskrit-dating` — highest value

**Maps to:** the MW source-layer seed map [`src/data/mw-source-layers.json`](../src/data/mw-source-layers.json)
and its `unknown` review queue (`build-source-layer-review.mjs`).

The atlas currently buckets MW citation sources into coarse diachronic layers from a
hand-seeded map; everything unmapped falls to `unknown`. [sanskrit-dating](https://github.com/dharmamitra/sanskrit-dating)
produces `dated_gibbs_full.tsv` — Gibbs-sampled posterior dates for ~1,600 texts, anchored on
externally-dated works, with archive.org links. Two steps: (a) reinstate the chronology
`import-*` step (see Prior art above) to snapshot the TSV into `src/data/external/`, then
(b) a `build-source-layer-anchoring-review.mjs` that joins it to the `unknown` sources by
siglum and proposes anchored dates as a review queue.

**Caveat (theirs, and it's the right one):** a dictionary citation mixes *authorial*
chronology (when the cited text was composed) with *editorial* compilation (when MW wrote the
entry). Keep those two axes separate; the dates anchor the *cited source*, not the entry.

### 2. Validate compound-segment depth with ByT5 `unsandhied`

**Maps to:** the MW compound-segment-depth metric in
[`scripts/lib/mw-parser.mjs`](../scripts/lib/mw-parser.mjs) / `mw-classifiers.mjs`.

The atlas splits compounds heuristically. Running `mode="unsandhied"` (segmentation) over the
same `<k2>` bases gives the model's segment count; disagreements become a review queue —
exactly the pattern of the gender cross-check, reusing the same importer with a different mode.

### 3. Cross-check lemma normalization with ByT5 `lemma`

**Maps to:** [`src/lib/lookup-normalize.js`](../src/lib/lookup-normalize.js).

Run `mode="lemma"` over inflected forms found in citations to validate the deterministic
SLP1 normalizer against an independent lemmatizer. Flag disagreements; do not auto-apply.

### 4. Separate German metalanguage in PWG/PWK with `detect-language`

**Maps to:** the Petersburg parsers ([`scripts/lib/dict-parser.mjs`](../scripts/lib/dict-parser.mjs)
for `pwg`/`pw`).

PWG/PWK interleave German metalanguage with Sanskrit headwords and citations.
[detect-language](https://github.com/dharmamitra/detect-language) is a lightweight
SentencePiece classifier (English / Sanskrit / IAST); retrained or extended for German it
would cleanly separate metalanguage tokens from object-language tokens during parsing —
improving citation and gender extraction quality for the two densest dictionaries.

### 5. Automate DTB link-targets with `mitra-aligner`

**Maps to:** the org-wide **Dictionary-to-Book** milestone (`link-target` / `link-splitting`),
i.e. linking `<ls>` abbreviations to scanned source pages.

[mitra-aligner](https://github.com/dharmamitra/mitra-aligner) (bertalign-buddhist) plus
Dharmamitra's archive.org scan metadata is a citation→passage alignment engine — the missing
automated half of the link-target work. This is a Cologne-wide opportunity, not atlas-specific;
outputs would feed the `csl-corrections` audit-trail workflow, reviewed before commit.

### 6. Ship a StarDict / GoldenDict distribution

**Lesson from:** [dharmamitra-stardict-dictionaries](https://github.com/dharmamitra/dharmamitra-stardict-dictionaries).

They build ~4M GoldenDict headwords from parallel data, shipped with an explicit
*"automatically generated, use with caution"* disclaimer. Two takeaways: (a) StarDict is a
cheap, high-reach distribution format the CDSL could also emit from existing data; (b) their
caution-labeling validates our own [evidence-labels](EVIDENCE_LABELS.md) discipline — provenance
honesty is the norm in this space.

### 7. Benchmark with `dharmamitra-leaderboard`

A benchmarking harness that could evaluate dictionary-lookup / segmentation quality against a
shared baseline, if we ever expose a lookup or segmentation service.

### 8. Read the agentic starter

[dharmamitra-claude-code-agent](https://github.com/dharmamitra/dharmamitra-claude-code-agent)
("starter pack for agentic translation") is worth reading given this repo is already worked
agentically — patterns for driving Sanskrit NLP from an agent loop.

---

## What *not* to import

Their assets are model-generated and probabilistic; the atlas's value is determinism. Consume
Dharmamitra outputs as **external evidence / priors feeding review queues**, never as silent
build inputs. Do not let a posterior date rewrite a source layer, a predicted gender overwrite
a dictionary's `<lex>`, or a model segmentation replace a counted metric. The model breaks
ties for a human reviewer; it does not settle them.

---

## Repository reference

| Repo | Relevance |
|---|---|
| [byt5-sanskrit-analyzers](https://github.com/dharmamitra/byt5-sanskrit-analyzers) | unified segmentation / lemma / morphosyntax (ByT5). [arXiv:2409.13920](https://arxiv.org/abs/2409.13920) |
| [sanskrit-dating](https://github.com/dharmamitra/sanskrit-dating) | Gibbs-sampled text chronology with archive.org links |
| [detect-language](https://github.com/dharmamitra/detect-language) | SPM English / Sanskrit / IAST classifier |
| [mitra-aligner](https://github.com/dharmamitra/mitra-aligner) · [mitra-parallel](https://github.com/dharmamitra/mitra-parallel) | parallel-text / citation alignment |
| [dharmamitra-stardict-dictionaries](https://github.com/dharmamitra/dharmamitra-stardict-dictionaries) | StarDict packaging from parallel data |
| [dharmamitra-leaderboard](https://github.com/dharmamitra/dharmamitra-leaderboard) | benchmarking harness |
| [dharmamitra-claude-code-agent](https://github.com/dharmamitra/dharmamitra-claude-code-agent) | agentic-translation starter |

Package: `dharmamitra-sanskrit-grammar` (PyPI, MIT) — remote API wrapper. Models:
`buddhist-nlp/byt5-sanskrit`, `chronbmm/sanskrit5-multitask` (HuggingFace).
Paper: Nehrdich, Hellwig & Keutzer, *One Model is All You Need: ByT5-Sanskrit*, EMNLP
Findings 2024.

## Licensing

Dharmamitra repos are CC-BY-SA-4.0 (matching the atlas and MWS); the PyPI wrapper is MIT;
model cards live on HuggingFace and the training data derives from DCS. We consume predictions
as review evidence and do not redistribute them as atlas data, which sidesteps most concerns —
but record provenance (model, revision, license) in every imported snapshot, as the existing
import steps do.
