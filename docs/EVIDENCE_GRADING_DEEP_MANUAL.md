# csl-atlas — Evidence-Grading Methodology & Human-Review Deep Manual

_Created: 21-07-2026 · Last updated: 21-07-2026_

> Deep manual for the org's flagship epistemic architecture: how a claim in csl-atlas is
> born, labeled, provenance-stamped, routed to human review, statistically tested,
> preserved across rebuilds, registered as a hypothesis, and consumed by papers — and
> every documented way that machinery has failed. Authored under handoff H1408 by
> Fable 5 (`claude-fable-5`) against repo state `6956469` (21-07-2026); the org
> deep-manual template is
> [ARCHITECTURE_ORG_DEEP_MANUALS_FABLE_WAVES.md](https://github.com/gasyoun/Uprava/blob/main/docs/ARCHITECTURE_ORG_DEEP_MANUALS_FABLE_WAVES.md).
> Companion metadoc:
> [EVIDENCE_GRADING_DEEP_MANUAL.meta.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_GRADING_DEEP_MANUAL.meta.md).

## 1. Orientation — the whole system on one screen

csl-atlas is a static, Observable-Framework site making claims about nine Sanskrit
dictionaries. Its epistemic contract is: **no claim without a label, no dataset without
provenance, no chart without a trust block, no heuristic without a review queue, no
human decision lost to a rebuild, no result without a registered hypothesis verdict —
and no failure silently forgotten.**

The life of one claim:

1. A builder (`npm run build-*`, one of 61) parses `../csl-orig/v02/<dict>/<dict>.txt`
   deterministically and emits JSON wearing the **provenance envelope** (§4).
2. Every emitted claim carries an **evidence label** from the four-label ladder (§3):
   `observed` → `derived` → `inferred`, with `reviewed` sitting on top.
3. `inferred` (and low-confidence `derived`) claims are routed into **review queues**
   (§6) — never asserted as fact on a page.
4. Deterministic **auto-triage** (§7) resolves the mechanically provable subset;
   everything else waits for a human in a **review packet** or queue page.
5. A human decision (`reviewed-ok` / `reviewed-corrected` / `blocked` / `deferred`)
   becomes an **overlay keyed by stable `reviewId`/`checkpointId`** that every rebuild
   re-attaches (§8). Wiping it requires an explicit `--reseed` flag that is registered
   org-wide as a do-not-run danger fact.
6. Public pages surface the claim inside a **Chart Trust Block** (§5).
7. The claim's research-level fate — supported, refuted, replaced — is registered in
   the **hypothesis index** (§9); refutations stay visible forever.
8. Papers P1–P6 and the A-series (§10) consume only what survived 1–7, with hostile
   pre-submission review and reproducibility audits closing the loop.

Operator cheat sheet (the release checks from
[ARCHITECTURE.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/ARCHITECTURE.md);
CI itself runs them wrapped in one gate, `npm ci` → `npm run verify` — see §16.2):

```sh
npm test                          # 245 node tests (see §16.4 for the one local-only guard)
npm run validate-review-reports   # schema + link-safety over all 14 review reports
npm run build                     # observable build (prebuild runs sync-site-data)
```

The one forbidden flag: **never pass `--reseed` to `build-r2-checkpoint-review`** — it
blanks the human review overlay (§8.3, §14). Registered in
[Uprava DANGER_FACTS.md](https://github.com/gasyoun/Uprava/blob/main/DANGER_FACTS.md)
and mirrored publicly in
[AGENTS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/AGENTS.md).

## 2. Component map

| Subsystem | Contract / spec | Implementation | Enforcement |
|---|---|---|---|
| Evidence ladder | [docs/EVIDENCE_LABELS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS.md) | `evidenceLevel` field on review items; `evidenceLabel` on dataset files (§3.2) | `evidenceLevel` enum in [data/schema/review-report.schema.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/schema/review-report.schema.json); `evidenceLabel` unenforced |
| Provenance envelope | [ARCHITECTURE.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/ARCHITECTURE.md) § Core Data Shapes | [scripts/lib/dataset-meta.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/dataset-meta.mjs) (+ Python twin [scripts/lib/dataset_meta.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/dataset_meta.py)) | by constructor use, not by validator (§4.4) |
| Trust blocks | [docs/CHART_TRUST_TEMPLATE.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CHART_TRUST_TEMPLATE.md) | hand-written page sections + 2 generated/JS variants (§5.2) | convention only — no validator, no CI check (§5.4) |
| Review reports | [docs/REVIEW_REPORTS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_REPORTS.md) | [scripts/lib/review-report.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/review-report.mjs) + 14 reports under [src/data/review/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/src/data/review) | [scripts/validate-review-reports.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-review-reports.mjs), run before build inside CI's `verify` gate (§16.2) |
| Queue-proof contract | [docs/REVIEW_QUEUE_PROOFS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_QUEUE_PROOFS.md) | queue pages under [src/tools/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/src/tools) | convention only (§5.4 item 7) |
| Packets + auto-triage | [docs/R2_REVIEW_PACKETS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_REVIEW_PACKETS.md) | packet builders under `scripts/` (§7) | packet-internal validators (§7.3) |
| Decision persistence | [docs/REVIEW_REPORTS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_REPORTS.md) rule: "A rebuild must not discard reviews" | `loadPreserved`/`reviewFields` by `reviewId`; `checkpointId` carry-over (§8) | [scripts/regen-review-artifacts.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/regen-review-artifacts.mjs) before/after snapshot, hard-throw on drift |
| Hypothesis registry | [docs/HYPOTHESIS_INDEX.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md) | 29 rows + 6 proposed (§9) | maintenance rules in the file; no mechanical check |
| Statistics | in-script, per analysis (§11) | [scripts/build-r2-h2h3.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-h2h3.mjs), [scripts/build-citation-canon.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-citation-canon.mjs), [scripts/build-four-axis-independence.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-four-axis-independence.mjs) | uneven — from full payload re-derivation to a single smoke test (§11.4) |
| Papers | [docs/PUBLICATIONS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PUBLICATIONS.md) | drafts + reviews + sign-offs under [docs/articles/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/docs/articles) (§10) | hostile Fable reviews + reproducibility audits (§10.3, §13.1) |

## 3. The evidence ladder

### 3.1 The four labels

From [docs/EVIDENCE_LABELS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS.md)
(dated 2026-05-29):

| Label | Reader name | Meaning | Example |
|---|---|---|---|
| `observed` | in the source | Directly present in a dictionary source record | An MW record contains a `<lex>m.</lex>` tag |
| `derived` | computed | Produced by a fixed, reproducible rule from observed data | The record is classified `noun-m` because of that tag |
| `inferred` | probable | A useful heuristic that has not been verified; may be wrong | A lexical family inferred from a shared headword prefix |
| `reviewed` | checked | A human has confirmed or corrected the value | A reviewer accepted a dictionary alignment |

Strength ordering: `observed` and `derived` are strong (the source says so, or a rule
restated it), `inferred` is "a guess the atlas is being honest about", and `reviewed`
is strongest of all — but **`reviewed` does not replace the other labels; it sits on
top of them**. "Derived, and then reviewed-ok" is a coherent and common state. The
label answers *where the value came from*; the review status (§6.1) answers *whether a
human has looked*. Promotion happens on the review axis, never by relabeling:
`inferred` → `needs-review` → `reviewed-ok`/`reviewed-corrected`/`blocked`, while the
evidence label stays what it always was.

The queue-entry heuristic
([docs/REVIEW_REPORTS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_REPORTS.md)):
"A claim labeled `observed` rarely needs a queue. A claim labeled `inferred` almost
always does."

### 3.2 The two field names — one enforced, one drifting

The ladder reaches code under **two different field names**, and only one is guarded:

- **`evidenceLevel`** (review items): enum-locked to the four labels in
  [data/schema/review-report.schema.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/schema/review-report.schema.json)
  and validated in CI. 15+ queue builders set it; the only *dynamic* assignment in the
  repo is [scripts/build-h5-anomaly-review.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-h5-anomaly-review.mjs)
  (`sampleClass === "known-correction" ? "observed" : "inferred"`); everything else is
  a per-queue constant chosen at authoring time.
- **`evidenceLabel`** (file-level, ~20 non-review dataset builders, e.g.
  [scripts/build-citation-canon.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-citation-canon.mjs),
  [scripts/build-semantic-fields.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-semantic-fields.mjs),
  [scripts/build-xref-lineage.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-xref-lineage.mjs)):
  **not schema-checked anywhere**, and it has drifted five off-ladder values into the
  data: `machine-review-sample`
  ([build-h4-review-packet.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-h4-review-packet.mjs)),
  `source-check-derived`
  ([build-h5-maker-correction-proposal.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-h5-maker-correction-proposal.mjs)),
  `review-derived`
  ([build-h5-maker-qa-candidates.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-h5-maker-qa-candidates.mjs)),
  `source-vs-archive`
  ([build-r2-parser-diagnostics.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-parser-diagnostics.mjs)),
  `derived-source-pointers`
  ([build-xref-source-check-packet.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-xref-source-check-packet.mjs)).

A third spelling exists only as a ghost: `docs/EVIDENCE_LABELS.md` promises a plural
per-field `evidenceLevels` map, but **no live script emits it** — the plural survives
only in docs and two archived legacy documents. When reading or extending this system:
the implemented reality is the singular pair; treat any doc mention of `evidenceLevels`
as stale (metadoc backlog item B1).

### 3.3 Where labels surface

Site pages render, never compute, labels:
[src/tools/semantic-fields.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/semantic-fields.md),
[src/tools/xref-lineage.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/xref-lineage.md),
[src/tools/structural-register.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/structural-register.md)
show `["Evidence label", data.evidenceLabel]` rows;
[src/tools/citation-canon.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/citation-canon.md) and
[src/tools/descent-axes.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/descent-axes.md)
interpolate label + review status into their trust blocks. The reader-facing rule
([src/researcher-dashboard.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/researcher-dashboard.md)):
"Student-facing simplification must not hide observed, derived, inferred, or reviewed
status."

## 4. Provenance envelopes

### 4.1 The canonical shape

Every generated dataset wears the envelope specified in
[ARCHITECTURE.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/ARCHITECTURE.md):
`schemaVersion`, `license` (SPDX `CC-BY-SA-4.0`) + `licenseUrl`, `generatedAt`,
`sourcePath`, `recordCount`, `assumptions[]`, `warnings[]`, then the payload
(`items`/`rows`/`data`). In practice a tenth field rides along, absent from the
spec but near-universal among the review-queue and research pipelines (36/59 builders,
§4.3): **`generatedBy`** — the literal invocation (`npm run build-learner-index`),
which is what makes the A10-style claim→artifact walk (§13.1) possible. Committed
example: the head of
[src/data/learner/learner-index.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/learner/learner-index.json).

### 4.2 The constructor library

[scripts/lib/dataset-meta.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/dataset-meta.mjs)
(27 importers; Python twin for the `.py` pipelines) contributes two deliberate
behaviors beyond field assembly:

- **Reproducible timestamps**: `generatedAtNow()` honors `CSL_ATLAS_GENERATED_AT` /
  `SOURCE_DATE_EPOCH`, so a pinned environment reproduces byte-identical output.
- **Diff-noise suppression**: `generatedAtForPayload()` keeps the *old* timestamp when
  the payload is canonically unchanged — a rebuild that changes nothing produces no
  git diff. This is why the §8.5 idempotency proof can demand an *empty* diff rather
  than "diff only in timestamps".

Chained pipelines carry provenance *through*: downstream builders record
`sourceGeneratedBy` (e.g.
[scripts/build-r2-checkpoint-packet.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-checkpoint-packet.mjs),
[scripts/build-r2-label-proposals.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-label-proposals.mjs))
or a per-input `sources: {…generatedBy}` map
([scripts/build-r2-drift-explanation.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-drift-explanation.mjs)),
and several **verify the upstream's `generatedBy` before consuming it**
([scripts/build-h5-maker-correction-proposal.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-h5-maker-correction-proposal.mjs)
requires its input packet to come from `build-h5-maker-qa-candidates`;
[scripts/build-r2-drift-explanation.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-drift-explanation.mjs)
verifies both of its upstreams) — a builder refusing to run on data produced by the
wrong generator. ([scripts/build-h4-review-packet.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-h4-review-packet.mjs)
asserts `generatedBy` on its *own output*, a self-check, not an upstream check.)

### 4.3 Coverage census (21-07-2026, grep over the 59 committed `build-*.mjs`)

`generatedBy` 36/59 · `schemaVersion` 41/59 · `warnings` 30/59 · `assumptions` 24/59 ·
`sourcePath` 19/59 · license fields 17/59. The gap is structured, not random: the 14
review-queue builders get their envelope from `reviewPayload()` (§6.3) wholesale, and
the R2/lexico/Python research pipelines are near-universal adopters, while older
display-oriented builders
([build-r2-pages.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-pages.mjs),
[build-review-sheets.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-review-sheets.mjs),
[build-stardict-export.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-stardict-export.mjs))
carry none of the tested fields. Foreign payloads synced from sibling repos default to
`generatedBy: "VisualDCS"` in
[scripts/sync-site-data.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/sync-site-data.mjs).

### 4.4 The enforcement asymmetry

There is **no generic envelope validator**. Review reports are the only directory
whose files are checked file-by-file in CI, and even there the schema's top-level
`required` is just `["license", "items"]` — the full envelope is guaranteed by the
shared constructor, not by validation. Non-review datasets are covered only where a
paired `validate-*` script exists. Consequence for maintainers: an envelope regression
in a display-oriented builder will not fail CI; it will be caught, if at all, by the
next reader of the JSON (metadoc backlog item B2).

## 5. Chart Trust Blocks

### 5.1 The two templates

[docs/CHART_TRUST_TEMPLATE.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CHART_TRUST_TEMPLATE.md)
(2026-06-04) mandates the **Short Block** on every public page — five bullets in fixed
order `Evidence → Limitations → Validation → Owner repo → Next use`, where Owner repo
is exactly one of `csl-atlas` / `VisualDCS` / `csl-standards` / `csl-observatory` —
and the **Extended "Chart Trust Block"** (12 fields, adding `Claim`, `Evidence label`,
`Source files`, `Generated by`, `Known false positives`, `Known false negatives`,
`Review status`, `Next action`, `External dependencies`, `Boundary note`) on research
charts and generated-data pages. Review-queue pages additionally owe a leading
"`This queue proves: …`" sentence.

### 5.2 Three coexisting implementations

1. **Hand-written markdown sections** — 51 of 64 pages under `src/`, 50 of them fully
   canonical. Chart pages interpolate live data into the bullets
   ([src/tools/descent-axes.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/descent-axes.md)).
2. **JS-rendered localized sections** — 3 reader pages
   ([src/tools/reader-lookup.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/reader-lookup.md),
   [src/tools/dictionary-dossier.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/dictionary-dossier.md),
   [src/tools/learner-reading-layer.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/learner-reading-layer.md))
   build the same five fields from `locales-en.json`/`locales-ru.json` keys, with the
   block CSS copy-pasted per page.
3. **Generator-emitted prose paragraphs** — the 3 R2 pages get a one-paragraph trust
   note between `R2-GEN:START/END` markers from
   [scripts/build-r2-pages.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-pages.mjs).

### 5.3 Coverage census (21-07-2026)

61 of 64 `src/**/*.md` pages carry some trust block (50 canonical short + 1
rogue-styled + 4 extended + 3 JS + 3 generated). The three with **none**:
[src/tools/source.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/source.md),
[src/tools/dictionary-density.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/dictionary-density.md),
[src/tools/letter-anatomy.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/letter-anatomy.md).

### 5.4 Template-vs-reality drift census

Eight documented divergences, all live at `6956469`:

1. The 4 extended-block pages drop the "mandatory everywhere" short block.
2. 2 of 4 extended blocks mutate fields — merged `Evidence label`+`Review status`,
   a non-template `Known limitation` replacing the false-positive/negative pair, an
   invented `n =` bullet.
3. One rogue block
   ([src/tools/pd-dcs-coverage.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/pd-dcs-coverage.md))
   in period-styled bold form (`**Evidence.**` / `**Limitations.**` /
   `**Owner repo.**`) with `Validation` and `Next use` truly absent.
4. The generated R2 paragraphs are lossy (no Limitations / Next use) and use prose,
   not the mandated heading+list.
5. The JS variant is invisible to any grep keyed on `## Trust Block`.
6. Three pages uncovered entirely (§5.3).
7. The Review Queue Addendum's proof sentence is implemented in substance — all four
   public queue pages open with a "This queue proves …" sentence, and
   [src/tools/review-source-siglum.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/review-source-siglum.md)
   has a literal `## This Queue Proves` section — but never in the template's exact
   colon form, so a grep for the template string returns nothing (a lint-vs-reality
   nit, not a coverage gap; the doc-of-record sentences live in
   [docs/REVIEW_QUEUE_PROOFS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_QUEUE_PROOFS.md)).
8. No mechanical enforcement of any of the above — conformance of the 50 canonical
   blocks is purely conventional (metadoc backlog item B3 proposes a validator).

## 6. Review queues and reports

### 6.1 The status vocabulary

Six statuses, defined in
[docs/REVIEW_REPORTS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_REPORTS.md)
and enum-locked in the schema: `machine`, `needs-review`, `reviewed-ok`,
`reviewed-corrected`, `blocked`, `deferred`. The last four are **human statuses** —
their presence (or a non-empty `reviewer`) is what the persistence layer (§8) treats
as sacred. Downstream builds prefer `reviewedValue` over `machineValue`.

### 6.2 The queues

Four public, page-backed queues (item counts from the committed reports, verified by
the validator run of 21-07-2026 — note
[README.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/README.md)
still carries stale counts for two of them, 4,556 and 151; the 4,556 coincides with
the *gender-model-crosscheck* count, a trap for future audits):

| Queue (`queue` enum) | Builder | Report | Page | Items |
|---|---|---|---|---|
| `pos-gender-conflict` | [build-gender-conflict-review.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-gender-conflict-review.mjs) | [gender-conflicts-review.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/review/gender-conflicts-review.json) | [review-gender-conflicts](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/review-gender-conflicts.md) | 4,543 |
| `unknown-source-layer` | [build-source-layer-review.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-source-layer-review.mjs) | [unknown-source-layers-review.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/review/unknown-source-layers-review.json) | [review-source-layers](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/review-source-layers.md) | 449 |
| `low-confidence-alignment` | [build-alignment-review.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-alignment-review.mjs) | [low-confidence-alignment-review.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/review/low-confidence-alignment-review.json) | [review-alignment](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/review-alignment.md) | 7 (all reviewed-ok) |
| `source-siglum-alias` | [build-citation-apparatus.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-citation-apparatus.mjs) | [source-siglum-review.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/review/source-siglum-review.json) | [review-source-siglum](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/review-source-siglum.md) | 158 |

Beyond the four, the schema's `queue` enum admits 16 values and **14 report files** are
committed under
[src/data/review/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/src/data/review)
— including the page-less decision-bearing `r2-checkpoint` (10 items, all
`reviewed-ok`) and `encoding-ocr` H5 queue (130 items, all `reviewed-ok`), plus eight
crosscheck/pilot queues in pure `needs-review` state. When a doc says "the four review
queues" it means the public four; the review *architecture* is the 16-value enum.

### 6.3 The item and file contract

Item required fields: `reviewId`, `queue`, `subject` (kind ∈ 9 values),
`sourcePointers`, `machineValue`, `evidenceLevel`, `reviewStatus`. The file envelope is
assembled by `reviewPayload()` in
[scripts/lib/review-report.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/review-report.mjs).
New queues must use that library — "instead of inventing local review formats"
([ARCHITECTURE.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/ARCHITECTURE.md)).

### 6.4 The validator

[scripts/validate-review-reports.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-review-reports.mjs)
(dependency-free; reads the schema's own `required`/`enum` lists) checks every report
for required item fields, enum membership, and the **link-safety rule**: every item
needs either a GitHub `href` or the local-only escape
(`sourceLinkMode: "local-only"` + `sourcePath` + a finite positive `line`) — the
accommodation for dictionaries whose multi-MB sources GitHub refuses to render (the
[/tools/source](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/source.md)
viewer serves those lines instead). Run 21-07-2026 in this pass: all 14 files ok,
exit 0. A separate Python pair
([scripts/validate_review_decisions.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate_review_decisions.py))
validates downloaded decisions files from review sheets — do not confuse the two.

## 7. Review packets and auto-triage

### 7.1 Packets

A *packet* is a reviewer-facing bundle under `data/lexico/`, organized so "review can
proceed by parser decision rather than by isolated lemma/dictionary rows". The five R2
packets
([scripts/build-r2-review-packets.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-review-packets.mjs),
doc [docs/R2_REVIEW_PACKETS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_REVIEW_PACKETS.md)):
`div-source-scope`, `marker-run-scope`, `ae-reverse-bands`, `indigenous-iti-authority`,
`source-gap-controls` — each declaring `proves / doesNotProve / nextDecision /
paperTarget`. The 10-row checkpoint packet
([scripts/build-r2-checkpoint-packet.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-checkpoint-packet.mjs))
**validates that its own human fields are empty** — decisions live only in the overlay
report, never in the packet. Other packet families: H4 semantic fields (105 rows),
xref source-check (40 + 10 controls), H5 maker QA.

### 7.2 Auto-triage — deterministic, mechanical-proof-only

Two rules exist, both marked `reviewStatus: "auto-resolved"` with a full
`autoTriage: {resolved, proposedDecision, basis, evidence}` block:

- **H4 loose-fold match** ([build-h4-review-packet.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-h4-review-packet.mjs)):
  an apparently missing AMAR lemma that IS present under the looser `slp1_form_key`
  fold is a normalization variant, not a real gap — 16/105 rows resolved. The three
  `covered` sample types are "genuine judgement with no mechanical proof, so they are
  deliberately left for human review".
- **Xref truncation-ring** ([build-xref-source-check-packet.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-xref-source-check-packet.mjs)):
  a cross-reference target carrying the CDSL truncation ring `˚` or trailing `-` is a
  prefix-convention hub by the dictionary's own markup — 10/50 resolved, string-only,
  no source read.

The design principle: **auto-triage may only claim what a dictionary's own markup or a
committed fold table mechanically proves**; judgment rows always reach a human.
[scripts/build-review-worksheets.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-review-worksheets.mjs)
renders worksheets *only* for rows auto-triage did not resolve.

### 7.3 Packet-internal validation

Builders enforce that `reviewStatus` and `autoTriage.resolved` agree and that any
proposed decision is inside the row's declared decision vocabulary. Because CI has no
`../csl-orig`, H4 auto-triage is itself **preservable**: committed `autoTriage` blocks
are reused by `reviewId` when the source is absent rather than recomputed.

## 8. Human-decision persistence across rebuilds

The single most protected invariant in the repo
([ARCHITECTURE.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/ARCHITECTURE.md)):
"Review reports are overlays on generated data. Re-running a generator must not erase
human decisions."

### 8.1 The `reviewId` overlay (the general mechanism)

[scripts/lib/review-report.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/review-report.mjs):
`loadPreserved(outputPath)` re-reads the existing output *before* regeneration and
harvests every item whose `reviewStatus` is a human status (or that names a
`reviewer`) into a `Map<reviewId, decision>`; `reviewFields(preserved, reviewId)`
re-attaches the decision to each newly generated item, defaulting fresh items to
`needs-review`. The `reviewId` is derived from content (lemma + dict + diagnostic
kind), never from array position. 18 builders import this.

Semantics when the candidate set changes: persisting IDs keep their decisions; new
items enter as `needs-review`; **decisions whose `reviewId` vanishes from the new
candidate set are silently dropped** — nothing writes them back. That is the one soft
edge of the mechanism (metadoc backlog item B4: an orphaned-decision report).

### 8.2 The `checkpointId` variant (packet layer)

The semicolon-counter packet
([scripts/build-r2-semicolon-counter-packet.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-semicolon-counter-packet.mjs))
carries adjudications by `checkpointId` (`checkpoint:semicolon-counter:<stem>:<code>`),
with the carry-over triggered by `reviewedValue != null` rather than the status set —
a decision survives only if the reviewer actually filled `reviewedValue`. History
correction worth pinning: the org memory shorthand "checkpointId idempotency = PR #132"
is precise only for this packet guard; the r2-checkpoint *overlay* wipe was fixed
earlier in PR #82 (commit `f052974`), and the general `reviewId` overlay predates both.

### 8.3 The escape hatch and the danger fact

[scripts/build-r2-checkpoint-review.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-checkpoint-review.mjs)
separates a machine-only `buildPayload` (which *validates* that human fields are
blank) from a CLI that re-applies the overlay. Deliberate wiping requires
`npm run build-r2-checkpoint-review -- --reseed`. That flag is the concrete referent of
the org danger fact "the R2 seeder wipes human review overlays" — never pass it;
[scripts/regen-review-artifacts.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/regen-review-artifacts.mjs)
"never calls the R2 `--reseed` escape hatch" by design.

### 8.4 The backstop

`regen-review-artifacts` snapshots 15 named human fields across the 6 decision-bearing
review files before and after a full regeneration and **hard-throws** on any drift:
"Refusing to continue: regeneration changed preserved human review fields." The
release-grade gate [scripts/verify.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/verify.mjs)
runs the whole regeneration **twice** as an idempotency check, inside a
clean-tree → tests → validators → regen ×2 → build → audit sequence.

### 8.5 Live proof (this pass, 21-07-2026, worktree at `6956469`)

```text
$ npm run build-r2-checkpoint-review
Wrote 10 R2 checkpoint review items (10 human reviews preserved) to:
- src\data\review\r2-checkpoint-review.json
$ git status --porcelain src/data/review/   # (empty — byte-identical, invariant held)
```

A plain rebuild of the decision-bearing checkpoint queue preserved all 10 human
decisions and produced a byte-identical file — no diff at all, thanks to §4.2's
payload-unchanged timestamp behavior. This is the spike H1408 queued ("confirm the
review-data preservation invariant across rebuilds"): confirmed.

## 9. The hypothesis registry

[docs/HYPOTHESIS_INDEX.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md)
is the boundary-aware registry of research claims: 29 rows + 6 proposed, in **three
types** (not two — the "Type-1/Type-2" shorthand in org docs undercounts):

- **Type 1 — Evidence-backed findings** (18 rows): supported *or refuted* by current
  or archived atlas evidence.
- **Type 2 — Strong testable hypotheses** (6 rows): data and method exist; the next
  implementation can test them.
- **Type 3 — Exploratory / external** (5 rows): blocked by new data, another repo, or
  a future contract — each row names exactly one owner repo, and implementation
  belongs there.

Plus the **Proposed lane** (PH3–PH8), spec'd with data/join-keys/method/readiness in
[docs/ATLAS_RESEARCH_AGENDA.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ATLAS_RESEARCH_AGENDA.md) §2.

Promotion ladder: **Proposed → tested by a build session → Type 1**, keeping the
verdict even when negative (PH1 CANON-CORE entered Type 1 as "Refuted, and in the
opposite direction"); Type 2 → Type 1 by the same route (THREE-AXIS-INDEP). Refuted
hypotheses are never deleted: "a negative result is still evidence" — H1 and H3 were
replaced in place by replacement-ID rows H1R/H3R. Every row wires into the rest of
this manual: Evidence cells point at review packets with deliberately empty human
fields, Next-test cells at queue adjudications, and the Paper/dashboard target column
at §10. The registry even carries a meta-hypothesis about this manual's subject:
REVIEW-PROOF — "Review queues can be treated as proof instruments, not only cleanup
lists" ([docs/REVIEW_QUEUE_PROOFS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_QUEUE_PROOFS.md)).

## 10. The paper pipeline (P1–P6 and the A-series)

### 10.1 The series

Per [docs/PUBLICATIONS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PUBLICATIONS.md),
drafts under [docs/articles/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/docs/articles):

| P# | A-ID | Title | Draft | Anchor evidence |
|---|---|---|---|---|
| P1 | A01 | Measuring the Dictionary Family | [paper_measurement_framework.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_measurement_framework.md) | 10-metric catalog, AP90→AP worked example |
| P2 | A02 | Condensation, Not Inflation | [paper_sense_inheritance.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md) | R2 sense survival; H2/H3 arcs (§11.1, §13.2) |
| P3 | A03 | Three Axes of Descent | [paper_three_axes_descent.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_three_axes_descent.md) | THREE-AXIS-INDEP |
| P4 | A04 | Grammar Without Tags | [paper_indigenous_microstructure.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_indigenous_microstructure.md) | M7-ROOT-AGREE, SKD-ANU |
| P5 | A05 | Pointing Inward | [paper_xref_lineage.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_xref_lineage.md) | XREF-CORE; AP×AP90 positive control |
| P6 | A06 | Order Is the Dictionary | [paper_kosha_macrostructure.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_kosha_macrostructure.md) | KOSHA-MACRO |

Consumers beyond the core six: A07 (OBS-R redundancy), A08 (OBS-C citation registers —
numbers flagged stale post-H1086, human-gated re-sync), A10 (apparatus-not-errors,
§13.1), A50 (citation-frequency graph feeding A10/A08). Known internal inconsistency:
OBS-R is "(A07)" in PUBLICATIONS.md but "(A01)" in a HYPOTHESIS_INDEX row — resolve
against [Uprava ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)
before citing (metadoc backlog item B5).

### 10.2 The tour pages are not the papers

The four pages under
[src/paper/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/src/paper) tour a
*different, external* paper — the consolidated MW microanalysis paper canonical in
`sanskrit-lexicon/MWS` (`docs-pass` branch). All four carry a Short Trust Block;
three of them disclaim exactly this — "tour page only; the canonical paper text and
submission package live outside this repo" — while
[src/paper/related-work.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/paper/related-work.md)
carries a MUDIDI-specific Limitations line instead. P1–P6 connect to the site through
the hypothesis registry's target column, not through `src/paper/`.

### 10.3 The apparatus around a paper

Each near-ready paper accumulates: a hostile pre-submission review
(`A0x_review_fable5.md`, all by Fable 5 `claude-fable-5`), an author-pass sign-off
(`SIGNOFF_A0x_author_pass.md`), referee/revision documents (P2 has all three), and —
the strongest instrument — a reproducibility audit walking every headline number back
to a committed generator (§13.1). This is the evidence ladder applied to the papers
themselves: a paper claim is `derived` from committed artifacts or it does not ship.

## 11. The statistics machinery

All three engines are plain-JS, in-script, dependency-free — there is deliberately no
shared `scripts/lib/stats.mjs` (§12 R6 discusses the trade).

### 11.1 Logistic IRLS + CR1 cluster-robust sandwich — `build-r2-h2h3.mjs`

[scripts/build-r2-h2h3.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-h2h3.mjs):
`fitLogistic` (Newton/IRLS, convergence max |step| < 1e-9, cap 50 iterations, **no
ridge** — a singular Hessian returns `null` via the Gauss-Jordan `matInv` and the
caller bails), `clusterRobustSE` (sandwich with **CR1 adjustment
`(G/(G-1))·((n-1)/(n-k))`**, clusters = lemmas, negatives clamped to 0), p-values from
a hand-coded Zelen–Severo normal tail (Wald-normal, not t on G−1 df — an undiscussed
choice worth knowing). Model: `survived ~ 1 + cited + position_z + glossLen_z +
crossDict_z + edge FE`. The header states the whole point: "so the 'cited senses
survive better' gap is tested … without the pseudoreplication of treating senses
within an entry as independent." Consumed by
[src/tools/r2-h2h3.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/r2-h2h3.md)
and P2.

### 11.2 Degree-preserving permutation null — `build-citation-canon.mjs`

[scripts/build-citation-canon.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-citation-canon.mjs):
NODF nestedness (32-bit bitmask popcount, valid for ≤32 rows — 11 dicts here), Barber
bipartite modularity via LPAwb+ label propagation (best of 6 restarts), and the
**fixed-fixed null**: `trySwap` exchanges columns exclusive to two rows, preserving
every row and column degree exactly; burn-in 20·E successful swaps, E swaps between
samples, N=1,000, seeded mulberry32 (`0x5eedca11`) so the nulls reproduce; add-one
p-value `(#null ≥ obs + 1)/(N+1)` per the Dror et al. (2018) protocol. Verdict (PH1):
the citation matrix is **modular, not nested** — refuted in the opposite direction,
and the registry row itself warns "read the direction, not the third decimal of p."

### 11.3 Exact small-n permutation — `build-four-axis-independence.mjs`

[scripts/build-four-axis-independence.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-four-axis-independence.mjs):
`exactPermutationP` enumerates all n! permutations (hard guard: throws above n=8; the
real n is 5 → 120 permutations). The honesty posture is the design: at n=5 nothing is
"significant"; the exact test plus a printed critical-|r| line keeps the page
descriptive.

### 11.4 The validation asymmetry

Strongest to weakest: four-axis has a validator that **re-derives the entire payload
with a pinned timestamp and fails on any drift**, plus unit tests asserting the 120
count and the throw; citation-canon's validator recomputes matrix marginals, enforces
`nNull ≥ 1000`, and re-derives the verdict string from the reported stats — but
`nodf`/`modularity`/`trySwap` have **no unit tests against known fixtures**; h2h3 has
one smoke test (recovers a known coefficient, 40 synthetic clusters) and **no paired
validator at all**, and no engine is cross-checked against a reference implementation
(R/statsmodels) anywhere (metadoc backlog items B6–B7).

## 12. Design rationale — why the machinery is shaped this way

**R1 — Git is the review database.** With no backend, the only durable, auditable,
concurrent-session-safe store for human decisions is the repo itself. Hence decisions
live *in* the generated JSON as an overlay (§8) rather than beside it: one file is the
whole truth of a queue, every decision has a commit, and a PR diff is the review audit
trail. The cost — rebuilds must actively preserve the overlay — is paid by the
`loadPreserved` contract and the regen backstop, and the two historical wipers (§13.4)
are exactly the two builders written before that contract hardened.

**R2 — Labels are a frozen vocabulary because drift is the observed failure mode, not
a hypothetical.** The schema-locked `evidenceLevel` has held at four values for the
system's whole life; the unlocked `evidenceLabel` drifted to five off-ladder values
(§3.2) and the doc-only plural `evidenceLevels` never materialized. Same repo, same
authors, same weeks — the only difference is the enum check. This is the cleanest
internal experiment the org has on "convention vs validator".

**R3 — `reviewed` sits on top rather than replacing, because provenance and
verification are different questions.** A reviewed value whose label became `reviewed`
would erase *what kind of machine claim was verified* — and the promotion experiment
(§7, [scripts/build-r2-promotion-experiment.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-promotion-experiment.mjs))
needs precisely that distinction to measure how often `derived` vs `inferred` claims
survive review.

**R4 — Parser promotions are review-gated, never silent** ("parser promotions are
reviewed before adoption, never applied silently" —
[docs/R2_SEMICOLON_COUNTER_REVIEW.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_SEMICOLON_COUNTER_REVIEW.md)).
The YAT arc (§13.2) is the reason: a parser change can *create or destroy* published
findings, so it is treated epistemically like a finding — packet, adjudication,
per-row decisions, and an implementer rule extracted from the one rejected row.
Corollary: "archive parity is a regression signal, not the optimization target" — when
recovered fixtures disagree with the print, the print wins (§13.3).

**R5 — Auto-triage claims only what markup proves.** Both rules (§7.2) rest on the
dictionary's own printed conventions (a truncation ring; a committed fold table), not
on model output or plausibility. The org's Dharmamitra rule generalizes it: "model
output is review evidence only, never a build input."

**R6 — From-scratch statistics is the static-first doctrine applied to math.** No
comment in the code states it (a gap worth fixing), but the shape is consistent:
no runtime backend, no build-time stats dependency, seeded reproducible nulls, and
methods simple enough to audit by reading (~50 lines each). The accepted costs are
§11.4's asymmetry and per-script duplication of numerics; the compensating control is
that the *outputs* are validated (payload re-derivation, verdict re-derivation) even
where the *algorithms* are not unit-tested.

**R7 — Negative results are registry citizens.** Refuted hypotheses keep their rows
with replacement IDs (§9); the retraction→un-retraction of YAT is documented in both
directions; A10's audit records "the numbers were always correct" as the *outcome of
checking*, not an assumption. The register the system optimizes for is trust under
audit, not headline strength.

**R8 — Provenance is chained, not just stamped.** `generatedBy` plus
`sourceGeneratedBy` plus upstream-verification (§4.2) means a wrong number can be
walked back through the exact generator chain that made it — which is what turned the
A10 incident from "unverifiable paper" into "one missing commit, found in a sibling
repo" (§13.1).

## 13. The incident corpus

The system's failure history, previously scattered across
[.ai_state.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.ai_state.md)
prose (bulk now in
[docs/archive/AI_STATE_2026-07-17.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/archive/AI_STATE_2026-07-17.md))
and issue threads. Each entry: what happened → detection → what changed.

### 13.1 A10 — the uncommitted generator (reproducibility)

Paper A10 published size-corrected rare-lemma containment ratios whose generator
(`scripts/L0/s6_content_lift.py`) was **never committed** — `git log --all` empty,
output CSV absent. Detected by the 03-07-2026 reproducibility audit
([docs/A10_REPRODUCIBILITY_AUDIT.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/A10_REPRODUCIBILITY_AUDIT.md)):
five of six headline signals reproduced to the digit from committed artifacts; §3.1
alone resisted every faithful reconstruction (the df universe could not be guessed).
Resolution: the generator was found alive in sibling `csl-observatory` and migrated in
(PR #202) — after which the CSV regenerates **byte-identically** and the published
ratios reproduce to the digit. "The numbers were always correct"; the defect was
walkability. Same-day hostile review (PR #204) separately caught content defects
(§3.2's "occur nowhere else" false for 65% of rows; stale bootstrap; wrong counts in
the abstract). Lesson pair: envelope provenance makes audits possible; audits find
what provenance cannot.

### 13.2 YAT — parser artifact, retraction, gated un-retraction (#125→#134)

H3R's flagship "drastic condensation" (wil→yat, 9 senses → 1) was an **extraction
artifact**: YAT packs ~5.71 meanings into semicolon run-ons, and the inline splitter
mistook noun-class digits for sense numbers. Proven by a dedicated evidence script
([scripts/verify-yat-sense-artifact.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/verify-yat-sense-artifact.mjs)),
the exemplar was retracted from the P2 manuscript (#125/#130). The fix was **not**
applied silently: a 26-row packet with a detection gate (mean inline < 1.5 AND mean
semicolon ≥ 3; SHS as control) went to adjudication (#132: 25 promote / 1 retain — the
one retain, `avaṣṭabdha`, yielding the rule "do not semicolon-split inside a lone
adjectival/participial section"). Applying the split made wil→yat a genuine ~9→5.7
condensation — **un-retracted** in #133/#134, strengthening the thesis it had
originally threatened. Side effect: recomputation exposed H2's edge concentration
(next).

### 13.3 H2 — pseudoreplication and edge composition (#123, #129, #133)

The naive "cited senses survive better" result (0.762 vs 0.591, z=3.0, p≈0.002)
treated every sense as independent; senses nested in a lemma share a fate. The §11.1
machinery was built to fix exactly this: controlled OR 1.75, p=0.16 — "it was
pseudoreplication." A referee-driven threshold sweep (#129) showed the attenuation
robust across cutoffs (OR 1.44–1.75, p 0.16–0.35). Then the YAT recomputation revealed
82/84 cited senses sit on the single ap90→ap edge — the pooled controlled OR moved
1.75→3.0 from an unrelated edge's parser change, so the paper now rests on the honest
within-edge test: 0.768 vs 0.661, z=1.80, p=0.07, not significant, and stated as an
upper bound. Mid-implementation gotcha preserved for posterity: without edge fixed
effects, a spurious *negative* `crossDict` coefficient appears (edge baselines 90% vs
7%); with them it collapses to ~0.

### 13.4 The overlay-wipe class

The R2 checkpoint builder originally wrote its machine seed straight over the
committed review file — "a plain `npm run build-r2-checkpoint-review` silently blanked
the committed human review pass" (fixed in PR #82, commit `f052974`); the
semicolon-counter packet had the same defect ("a regenerate would have silently wiped
this review", fixed in #132, commit `98fd135`). Documentary near-miss from before the
hardening: a licence-slice migration deliberately edited review files **in place,
bypassing the builders**, "since `build-r2-checkpoint-review` re-seeds empty and would
wipe the 10 decisions". A third instance lives in the L0 lane: re-running the Patel
gold step resets five annotation dimensions to `unknown`, mitigated by a committed
manual-overlay CSV re-applied every run. This class is why §8.4's backstop exists and
why `--reseed` is a registered danger fact.

### 13.5 The R2 archive loss — and the archive that was wrong

The ur-incident ([docs/R2_REBUILD_CONTRACT.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_REBUILD_CONTRACT.md),
2026-06-05): the original R2 generator package was deleted/never committed; only
static pages survived. `npm run recover-r2-archive` scraped two machine-fixture files
back out of the two committed static pages, and the four generators were re-run
byte-identical, with per-value drift against the archive documented. The twist that
reshaped the epistemics: in three documented cases **the archive itself was the
artifact** (PWG depth inflation, BEN's arbitrary cut, the SKD register limit) —
recovery was reframed as "more faithful to the print than
the counts it is checked against", and archive parity demoted to a regression signal
(R4).

### 13.6 Extraction under-counts (regex class)

Two corpus-scale instances: the A02/OBS-C *iti*-count non-reproducibility (the
space-or-quote rule missed markup-adjacent quotatives — KRM wraps Sanskrit in
`<s>…</s>`, hiding ~2/3 of its *iti*; fixed with a Latin-letter word boundary, moving
KRM to densest-in-corpus and swapping SKD's rank), and the H1086 MW `<ls>` regex
under-count (attributed citations `<ls n="RV.">…</ls>` missed; corpus-wide fix moved
**PWG +41%**, aggregate locator share 59/41→67/33). Both were detected by
re-derivation attempts, not by readers. Policy consequence: downstream papers (A08,
A01) were explicitly left stale and **flagged for human-gated re-sync, "not silently
rewritten"**.

### 13.7 Smaller entries, same registers

Journal loss (#148: a hygiene sweep restored an older `.ai_state.md`, silently
dropping a paragraph — the journal stays tracked); wrong-branch commit (#181 — always
`git branch --show-current` first); A05's edition-label swap fixed once and
**resurfacing** in a later author pass with pre- and post-fix wording spliced together
(partial-fix propagation); A03's "independent control" that wasn't (bootstrap ≈
convention, r=0.92); A06 using "lexeme" for four granularities; the Sprüche roadmap's
own validation example misattributed (measured error floor ~1 in 7); kosa-fusion
corpus counts inverting the exemplar's direction and being *reported as such* per the
pre-registered contingency ("no classifier tuning to force the expected direction");
GitHub write-API TLS false-successes (verify destructive remote ops against
`git ls-remote`, never the API response); Dharmamitra's degraded live API filtered to
`model-pending` rather than ingested.

## 14. Failure modes — symptom → cause → cure

| Symptom | Likely cause | Cure |
|---|---|---|
| Committed review JSON shows human decisions gone after a rebuild | A builder outside the `loadPreserved` contract, or `--reseed` was passed | Restore the file from git history; re-run the plain builder; if the builder is new, wire it through [scripts/lib/review-report.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/review-report.mjs); never commit the wiped state |
| `regen-review-artifacts` throws "Refusing to continue: regeneration changed preserved human review fields" | Exactly what it says — some step mutated a human field | Diff the named file against HEAD; find the offending step in the regen order; the throw is the system working, not the bug |
| A decision you know was made is absent from the rebuilt report | Its `reviewId` changed or its candidate row left the set — vanished IDs drop silently (§8.1) | Recover the decision from git history of the report; if id derivation changed, migrate ids deliberately in the same PR |
| `validate-review-reports` fails on enum or link-safety | Off-vocabulary status/label, or an item without `href`/local-only pointer | Fix the builder, not the JSON — generated files are never hand-edited |
| A published number cannot be regenerated | Uncommitted generator (§13.1, §13.5) or an input snapshot owned by a sibling repo | Search sibling repos before reconstructing (`csl-observatory` precedent); once found, commit the generator and prove byte-identical regeneration |
| A cross-dictionary count looks impossibly low for one dict | Extraction regex blind to that dict's markup convention (§13.6) | Test the extractor against a dict-specific sample; after fixing, flag downstream papers stale for human-gated re-sync — do not silently rewrite them |
| A dramatic structural finding on one edge/dict | Parser artifact until proven otherwise (§13.2) | Write an evidence script; route the parser change through a packet + adjudication; check whether *other* findings' compositions shift after the fix (§13.3's H2 lesson) |
| A significant pooled effect | Check pseudoreplication and composition first | Cluster-robust SEs by the natural unit; edge/dict fixed effects; report the within-stratum test when one stratum dominates |
| Trust block missing or mutated on a page | No mechanical enforcement (§5.4) | Follow the template by hand; if adding many pages, consider the B3 backlog validator first |
| Local `npm test` fails on "vendored sanskrit-util.js matches the canonical source" while CI is green | Sibling `../sanskrit-util` moved; the guard self-skips on CI | Re-vendor from the sibling (`/cologne-sanskrit-util-sync`); pre-existing on `6956469`, see metadoc verification block |
| Same work appearing twice / foreign commits on your branch | Concurrent session (H214/H919 class) | Stop; reconcile per the org shared-tree protocol; csl-atlas is a guarded repo — worktrees only |

## 15. Provenance and rights

Generated datasets are stamped `CC-BY-SA-4.0` by the shared meta libraries; the site
publishes to GitHub Pages from `main`. Upstream dictionary text stays outside the repo
(`../csl-orig/v02/`, never committed); DCS-derived and Dharmamitra-derived inputs are
synced as gitignored site copies with `generatedBy` marking their foreign origin.
Destructive-risk facts are registered centrally in the org-private
[Uprava DANGER_FACTS.md](https://github.com/gasyoun/Uprava/blob/main/DANGER_FACTS.md)
with the public-safe subset mirrored in
[AGENTS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/AGENTS.md)'s
generated block. Nothing in this manual is publish-gated: every quoted number, path,
and incident is already in the public repo.

## 16. Operator appendix — the pipeline estate

### 16.1 Script census (21-07-2026, `package.json` at `6956469`)

**93 script entries** (the census row's "73" is stale): 61 `build-*` dataset pipelines,
9 `validate-*`, 6 `import-*`, and 17 lifecycle/orchestration/tooling entries —
`predev`/`dev`, `prebuild`/`build`/`postbuild`, `predeploy`/`deploy`, `test`,
`verify`, `sync-site-data`, `regen-review-artifacts`, `recover-r2-archive`,
`train-langdetect-german`, `install-review-tools`, `test-review-decisions`,
`audit-analysis-capabilities`, and `verify-yat-sense-artifact` (§13.2's evidence
script). Do not guess a script name — grep `package.json`.

### 16.2 Order contracts

- **Site lifecycle**: `predev`/`prebuild`/`predeploy` all run `sync-site-data` first
  (the only path by which canonical `data/` artifacts reach the gitignored
  `src/data/` site copies); `postbuild` copies manifest/service-worker/robots into
  `dist/`.
- **CI** ([.github/workflows/test.yml](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.github/workflows/test.yml),
  triggers: `pull_request` + `workflow_dispatch`): `npm ci` → **`npm run verify`** —
  one gate wrapping tests → Python unittest → 8 validators → regen ×2 idempotency →
  build → `npm audit`. The same wrap runs in
  [build-and-deploy.yml](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.github/workflows/build-and-deploy.yml).
  Note: the repo's own
  [CLAUDE.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/CLAUDE.md)
  still describes the older unbundled sequence (`npm test` →
  `validate-review-reports` → build) — stale, metadoc backlog item B9.
- **Review regeneration**
  ([scripts/regen-review-artifacts.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/regen-review-artifacts.mjs)):
  `build-r2-label-proposals → build-r2-checkpoint-packet → build-r2-checkpoint-review
  → build-r2-drift-explanation`, then (only when `../csl-orig/v02/mw/mw.txt` exists)
  the H5 and H4/xref source-derived steps, then `build-review-worksheets`.
- **R2 research lane**: the numbered rebuild order in
  [docs/R2_REBUILD_CONTRACT.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_REBUILD_CONTRACT.md)
  (recover fixtures → anchors → parser families → explorer → h1 → h2h3), with
  `build-r2-drift-explanation` re-run "before any public R2 claim changes".
- **L0 lane**: `s2 → s2b → s2d → apply_lrv_fri_annotation → s3 → s5` (the annotation
  overlay must follow the gold step it protects, §13.4).

### 16.3 Review-preserving vs review-destroying

Preserving by construction: the 18 `loadPreserved` importers, the checkpointId packet,
H4's preservable auto-triage, and `regen-review-artifacts` (which also proves it).
Destroying: `build-r2-checkpoint-review -- --reseed` (the registered danger flag) and
a bare re-run of the L0 Patel gold step without its overlay CSV. Historical wipers
now fixed: §13.4. House rule: if you write a new queue builder, it imports
`review-report.mjs` or it does not merge.

### 16.4 Verification gates and their measured state (this pass)

Commands run 21-07-2026 in the H1408 worktree at `6956469`, outputs recorded in the
metadoc verification block: `npm run validate-review-reports` — all 14 reports ok;
`npm run build-r2-checkpoint-review` — 10/10 human reviews preserved, byte-identical
(§8.5); `npm test` — **245 tests, 244 pass, 1 fail**, the failure being the local-only
vendored-`sanskrit-util` drift guard (pre-existing on `origin/main`, self-skipped on
CI, tracked as its own follow-up task). The heavier
[scripts/verify.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/verify.mjs)
gate (clean tracked tree → tests → 8 validators → regen ×2 idempotency → build →
audit) was not run *locally* in this pass — it requires a clean tree, which an
authoring branch is not — but it runs in CI on every PR, including the one delivering
this manual; its source-derived regen steps self-skip when `../csl-orig` is absent
(as on CI runners). §8.5's spike is the targeted local proof of the same
idempotency property on the decision-bearing queue.

## 17. Maintainer appendix — keeping this manual true

- **Staleness**: the sibling metadoc carries the `LAST_VERIFIED` block read by
  [Uprava/tools/manual_staleness.py](https://github.com/gasyoun/Uprava/blob/main/tools/manual_staleness.py);
  after any substantive refresh, bump the block and re-run the detector.
- **What invalidates which section**: a new queue or enum value → §6; a new packet or
  auto-triage rule → §7; any change to `review-report.mjs` semantics → §8 (and re-run
  the §8.5 spike); hypothesis rows added/promoted → §9; paper status changes → §10; a
  new stats engine or validator → §11; any new incident → §13 + a row in §14; script
  count/order changes → §16. Trust-block or label drift beyond §3.2/§5.4's census →
  update the censuses, don't average over them.
- **The censuses in §4.3, §5.3–5.4, §16.1 are dated point-in-time greps** — cite them
  with their date, and re-derive rather than increment when refreshing.
- **Incident intake**: when a new epistemic incident closes, add it to §13 in the same
  pass that closes it (the previous home, `.ai_state.md` prose, gets archived and
  truncated — this manual is now the durable registry).

_Dr. Mārcis Gasūns_
