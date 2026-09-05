_Created: 17-06-2026 · Last updated: 05-09-2026_

# Dharmamitra GPU runbook — activate the gender (#89) + lemma (#92) cross-checks

**Status:** ready to run. The atlas-side scaffolding is complete and pinned; the only missing piece is one GPU (or patient CPU) pass of the pinned model. Run this on a box with a GPU, commit the two snapshots + regenerated review queues, open a PR. The deterministic build NEVER calls the model — these snapshots are review evidence only.

See also: [`DHARMAMITRA_MONTHLY_PLAN.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/DHARMAMITRA_MONTHLY_PLAN.md), [`DHARMAMITRA_INTEGRATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/DHARMAMITRA_INTEGRATION.md).

## What this unblocks

Gender (#89) and lemma (#92) are the two cross-checks still `model-pending` because the live API's morphosyntax/lemma modes are degraded and there was no in-session GPU. Both import scripts already have a reproducible `--source local` path; this runbook just executes it.

## Model (pinned)

- **Model:** `chronbmm/sanskrit5-multitask` (ByT5-Sanskrit multitask), **pinned revision `c0d2ada54f3d19903149425aa888a203601423f8`** (2024-05-09). The pin is the *default* `--revision` in both `scripts/import-dharmamitra-morphology.py` and `scripts/lib/dharmamitra_infer.py` — keep those two constants equal.
- **Tags:** `scripts/sanskrit_tags.tsv` is vendored (640 short→UD tags), so the run is fully offline and the revision pins **only** the model weights.
- **Decoding:** greedy (`num_beams=1`), so output is byte-stable for a given model + input — the committed snapshot is reproducible.

## Prerequisites

1. A machine with a CUDA GPU (CPU works but is slow). The scripts auto-pick `cuda` if available; override with `--device`.
2. `pip install torch transformers` (the only extra deps; the scripts exit with this hint if missing).
3. Network on first run to download the pinned model into the HF cache; offline thereafter. (`chronbmm/sanskrit5-multitask` is a public HF model.)
4. The committed input queues are already in the repo — **no sibling `csl-orig` needed** for this step.

## Steps

### A. Gender (#89) — 4,556 conflict lemmas

Input (committed): `src/data/review/gender-conflicts-review.json`.

```sh
# 1. Run the pinned model over the gender-conflict headwords -> snapshot
npm run import-dharmamitra-morphology -- --source local
#    (writes src/data/external/dharmamitra-morphology.json; --limit N for a pilot)

# 2. Join the model verdict against each dict's asserted gender -> review queue
npm run build-gender-model-crosscheck
#    (rewrites src/data/review/gender-model-crosscheck-review.json; 4,556 items)
```

Expect: `import` prints `Wrote 4556 morphology rows (<N> with a gender)`; the cross-check verdict breakdown moves off `{"model-pending": 4556}` to real verdicts (agree / model-disagrees / etc.).

### B. Lemma (#92) — 1,913 all-7-dict lemmas

Input (committed): `src/data/external/lemma-normalization-candidates.json` (produced by `npm run build-lemma-normalization-crosscheck`; regenerate first if stale).

```sh
npm run import-dharmamitra-lemma -- --source local
#    (writes src/data/external/dharmamitra-lemma.json)

npm run build-lemma-normalization-crosscheck
#    (rewrites src/data/review/lemma-normalization-crosscheck-review.json; 1,913 items)
```

Expect: the verdict breakdown moves off `{"model-pending": 1913}`.

## Verify, then commit

```sh
npm run validate-review-reports        # both queues stay schema-valid
npm test                               # unaffected (build never calls the model)
```

Commit **the two snapshots** (`src/data/external/dharmamitra-morphology.json`, `dharmamitra-lemma.json`) **+ the two regenerated review queues**, each as its own PR off `main`. Snapshots are large but are committed by design (review evidence); the model itself stays in the HF cache, never in the repo.

## Notes / caveats

- A pilot first: add `-- --source local --limit 50` to sanity-check the model loads and the verdict shape looks right before the full pass.
- The model is a **probabilistic posterior** — it breaks gender/lemma ties as a third vote, it does not settle them. Never auto-rewrite any dictionary's asserted value from the snapshot.
- To intentionally move the pin to a newer model commit, bump `PINNED_REVISION` in **both** files and note why; don't point it at a moving `main`.
- Re-running a full pass replaces #100-style degraded-API output with reproducible, junk-free data.

_Dr. Mārcis Gasūns_
