# Pre-registration — review-pool α on the H4 semantic-field packet (U4)

_Created: 18-11-2026 · Last updated: 18-11-2026_

Protocol: [PROTOCOL_BLIND_LLM_SECOND_ANNOTATOR_RELIABILITY_2026](https://github.com/gasyoun/Uprava/blob/main/docs/PROTOCOL_BLIND_LLM_SECOND_ANNOTATOR_RELIABILITY_2026.md) (C3 discipline, ACTIVE).
This file is checklist step 3 (§5) — **committed before Pass B runs**; the commit timestamp is
the pre-registration evidence. Nothing below may be edited after Pass B starts; corrections go
in a dated appendix.

## 1. Instrument and items

- **Instrument:** the H4 semantic-field review packet,
  [`data/lexico/h4_semantic_field_review_packet.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/h4_semantic_field_review_packet.json),
  `generatedAt 2026-10-30T09:46:59.130Z`, `sha256` recorded in the committed blind view.
- **Items:** the **89** `reviewStatus: reviewed-ok` rows. The 16 `auto-resolved` rows are
  excluded: they were resolved mechanically (variant-headword self-resolution), so they carry no
  annotator decision to agree with.
- **Strata (packet sample types, 5):** `skd-false-low` 10 · `vcp-high-coverage` 20 ·
  `ap-ap90-delta` 19 · `specialized-baseline` 20 · `index-reverse-control` 20.

## 2. Codebook (§2.1)

Frozen from the packet itself, one row at a time: the annotator may emit **only** the row's own
`expectedDecisionLabels`, which the packet groups into five disjoint 3–4-label sets:

| Stratum | Allowed labels |
|---|---|
| skd-false-low | `true-low` · `variant-headword` · `prose-present` · `parser-gap` |
| vcp-high-coverage | `true-covered` · `thin-entry` · `normalization-risk` |
| ap-ap90-delta | `edition-delta` · `parser-gap` · `normalization-risk` · `true-delta` |
| specialized-baseline | `scope-match` · `incidental-match` · `scope-mismatch` |
| index-reverse-control | `direction-artifact` · `index-artifact` · `meaningful-exception` |

A row's `reviewQuestion` (carried in the blind view) states the boundary in words; there is no
separate prose codebook, and none is invented here. The packet's `labelVocabulary` (the five
`proposedLabel` meanings) is the stratum-level statement of what each sample is testing.

**Axis check (§2.1 blocking-defect probe).** The column being predicted is `reviewedValue`, an
adjudicated **decision** label, not the `proposedLabel` hypothesis; `proposedLabel` is a
machine proposal and is stripped from the blind view so that it cannot be echoed. No mismatch
between the codebook and the label set actually present was found — the packet's own
`expectedDecisionLabels` are exactly the values `reviewedValue` takes.

## 3. Pass A — provenance (§2.2)

- **Model:** `grok-4.5`, recorded in-packet as
  `reviewer: "grok-4.5 (H1621 agent; evidence: local csl-orig + packet pointers)"`,
  `reviewedAt: 2026-07-24` (H1621 agent adjudication of 89 rows; see
  [H1684_B2_ADJUDICATION.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H1684_B2_ADJUDICATION.md)
  on why the packet's evidence label is `agent-adjudicated`, never `human-reviewed`).
- Provenance is **recorded and codebook-compliant** (a model annotation over a stated label
  set), so the column is pairable and both passes are not re-run from scratch.
- Pass A is **historical and not re-runnable**, so its flip-rate (§2.7) cannot be measured. This
  is a stated limitation, not a waived requirement.

## 4. Pass B — blind second annotator (§2.3)

- **Model:** DeepSeek V4.1 Flash (`deepseek-v4.1-flash`, `opencode-go`).
- **Blind input (committed before the pass):**
  `data/review/pool_blind/h4_semantic_field_89rows_blind_2026-11-18.json` — per row only
  `reviewId`, dictionary code, field, lemma (SLP1 + raw forms), `machineState`, coverage
  numbers, the row's `reviewQuestion`, its `allowed` labels, and the packet's own
  `bodyExcerpt` evidence. Stripped: `reviewStatus`, `reviewedValue`, `reviewer`, `reviewedAt`,
  `note`, `autoTriage`, `proposedLabel`, `sampleType`/`sampleLabel`, `rank`. Row order is the
  packet's canonical order, which is not label-ordered.
- **Format:** one label per row from `allowed`, written to a separate file, joined to Pass A
  only by the scoring script.
- **Pre-registered asymmetry (stated now, not after seeing the number):** Pass A additionally
  read the local `csl-orig` full texts; Pass B sees only the packet's committed evidence. For
  the 10 rows whose `machineState` is `missing` and whose packet carries no excerpt, Pass B
  decides from the coverage row and lemma form alone. Any low α is therefore *jointly* a
  codebook finding and an evidence-sufficiency finding; the two are separated in the report by
  the per-stratum table and the excerpt-presence split.
- **Orchestrator disclosure:** the executor had seen the label vocabulary, the aggregate label
  distribution and one row's decision (`item 1`) while designing this instrument. Blindness is
  therefore **mechanical and per-row**, not absolute.

## 5. Statistic, CI, gate (§2.4–§2.5)

- **Statistic:** Krippendorff's α, nominal metric, coincidence-matrix method — the same
  estimator the committed `scripts/lexico/review_pool_kappa.py` already implements, reused and
  extended rather than rewritten.
- **CI:** bootstrap over items, **2,000** resamples, seed **20261118**, 95 % percentile
  interval, reported beside the point estimate.
- **Granularity:** **L0 only**, the exact label. No coarser level is pre-registered, so the
  RESTATE path of the §4 ladder is deliberately unavailable in this run.
- **Gate:** CLEAR if the α CI **lower bound ≥ 0.80**; BLOCK if the point estimate < 0.40; else
  the §2.6 failure rule (publish the measured α, demote any dependent headline, write the
  disagreement rows out as a named artifact).
- **Per-stratum α** is reported descriptively with its own n. It is **not** gated: at n = 10–20
  a stratum interval cannot clear anything.

## 6. Flip-rate (§2.7)

- Fixed 30-row subsample: every 3rd item of the 89 (`items 3, 6, …, 87`), deterministic and
  reproducible from the blind file.
- **3 runs**, Pass B only (run 1 = the main pass). Flip-rate = fraction of (row × run-pair)
  label changes; the §2.7 10 % `provisional-unstable` flag applies to Pass B.
- Pass A: not measurable (historical pass) — stated above.

## 7. Channel label — human anchor explicitly NOT claimed

The agenda's "Wave-2 61-row human residue" was checked, not assumed:
[H1684_B2_ADJUDICATION.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H1684_B2_ADJUDICATION.md)
§ *The remaining human ask — 61 rows* describes the 61-row sheet as **still owed** (14 forks +
47 blind rows; promotion needs a Wilson 95 % lower bound of human–agent agreement ≥ 0.80). It
is an outstanding human **ask**, not a set of human labels; the sheet and its manifest live in
gitignored `review/`. It is also a *different* packet (tradition-tags / skd-iti spot-check), not
this one.

Therefore this run reports **channel = model × model** (`grok-4.5` × `deepseek-v4.1-flash`), and
the human anchor stays a GTD @WAITING residual. No `human × model` figure is quoted anywhere.

## 8. Denominators

n = 89 rows of 105 in the packet; 89 of 89 are scored by both passes (no key rotation in a
two-annotator packet, so the whole set is the denominator). Pooled nominal space = the 15
distinct labels; per-stratum spaces are the sets in §2.

_Dr. Mārcis Gasūns_
