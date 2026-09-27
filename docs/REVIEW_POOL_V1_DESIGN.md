# Community review pool v1 — design: submission path, double-keying, κ report

_Created: 24-09-2026 · Last updated: 24-09-2026_

Status: design of record for the roadmap item «Community review pool v1»
([ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md),
Q3 2026), closing gap **G4 — single-reviewer bottleneck**. Nothing below is built yet: this
document names what is reused, what is missing, and the four rules the missing code must
implement (identity, assignment, adjudication, κ). Handoff
[H5307](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5307-Opus_csl-atlas_review-pool-v1-double-keying-design_23.09.26.md),
epic E014.

## 1. What G4 actually says

> **Single-reviewer bottleneck = methodological weakness, not just a queue**: 10 R2 checkpoint
> rows, 105 H4 rows, 50 xref rows blocked on one person. With n=1 there is no inter-annotator
> agreement, so reviewed claims have unmeasurable reliability.

The fix is not "more reviewers". It is: **every row gets two independent keys, disagreements
are adjudicated by reading the source, and the agreement rate is published with its chance
correction.** A pool that produces 105 more single-keyed rows leaves G4 exactly where it is.

## 2. Reuse inventory — what exists and is NOT rebuilt

Probed live on this branch, 24-09-2026.

| Component | What it already gives the pool | Where | Verdict |
|---|---|---|---|
| Sheet emitter | Single-file HTML review sheet on the org V1–V8 standard, Russian chrome, per-card source links, `decisions.json` download | [`scripts/build-review-sheets.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-review-sheets.py) → `npm run build-review-sheets`, via `csl_pyutil.render_review_sheet` ≥ 0.16.0 | **Reuse**, two narrow patches (§7) |
| Export format | `{sheet_id, reviewer, reviewedAt, decided, complete, items:[{id, decision, note}]}`; verdicts `approve`/`reject`/`defer`; a reject carries `corrected-label: rationale` | emitter output, consumed by the validator below | **Reuse unchanged** — the pool needs no new export schema |
| Export validator | 1:1 row-ID match against the committed packet, closed-vocabulary check on corrected labels, UTC-timestamp check | [`scripts/validate_review_decisions.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate_review_decisions.py) → `npm run validate-review-decisions` | **Reuse**, extend to pool mode (§7) |
| Packets | The three blocked queues, already enveloped, with per-row closed label vocabularies and source pointers | [`data/lexico/r2_checkpoint_review_packet.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_checkpoint_review_packet.json), [`h4_semantic_field_review_packet.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/h4_semantic_field_review_packet.json), [`xref_source_check_packet.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_source_check_packet.json) | **Reuse unchanged** — the pool never re-cuts a packet |
| Overlay layer | «machine output → review report → trusted claim»: six-status vocabulary, reports keyed by stable IDs, generated data never edited in place | [`docs/REVIEW_REPORTS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_REPORTS.md), [`data/schema/review-report.schema.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/schema/review-report.schema.json), `src/data/review/*.json`, `npm run validate-review-reports` | **Reuse** — pool results land here, as one more overlay |
| κ method | Cohen's κ from the two marginal distributions, modal-class base rate stated beside it, Landis–Koch bands | [`scripts/lexico/root_agreement_kappa.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/root_agreement_kappa.py), rendered in [`docs/ROOT_AGREEMENT_KAPPA.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ROOT_AGREEMENT_KAPPA.md) | **Reuse the method and the banding**, not the data path (§8) |
| Annotator training | Per-packet card anatomy, label vocabularies in plain Russian, worked examples, the no-peeking rule | [`docs/REVIEW_POOL_STUDENT_GUIDE.ru.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_STUDENT_GUIDE.ru.md) (H5310) | **Reuse unchanged** — it was written for this pool |
| Adjudication precedent | Disagreement resolved by reading the source line and recording a rationale, not by vote | [`docs/H1684_B2_ADJUDICATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H1684_B2_ADJUDICATION.md), [`docs/SIGLUM_ADJUDICATION_2026-07.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/SIGLUM_ADJUDICATION_2026-07.md) | **Reuse the shape** (§6) |
| Privacy regime | 152-ФЗ handling for student participants, consent wording, what may not enter a public repo | [`USER_STUDY_PROTOCOL_LEARNER_LAYER_G7_24-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/USER_STUDY_PROTOCOL_LEARNER_LAYER_G7_24-09-2026.md) (H5336) | **Reuse** — the pool sits under the same regime (§4) |

Nothing in the list above is a stub: all four sheets render today, and the validator runs in
CI-adjacent form via `npm run validate-review-decisions`.

## 3. The three packets as they actually are (live counts, 24-09-2026)

| Packet | Rows | Sheet today | Label vocabulary | Current key count |
|---|---:|---|---|---|
| R2 checkpoint | 10 (`checkpointRows`) | **none** — never had a sheet | per-packet `proposedParserLabels`, e.g. `target-primary-series`, `same-headword-supplement`, `separate-homonym` | n=1 — all 10 recorded `reviewed-ok`, reviewer `gasyoun`, in [`src/data/review/r2-checkpoint-review.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/review/r2-checkpoint-review.json) |
| H4 semantic field | 105 `sampleRows` (89 `reviewed-ok`, 16 `auto-resolved`) | `csl-atlas-h4-semantic-field_89rows`, 89 cards | `false-low-risk`, `high-coverage-check`, `edition-delta-check`, `scope-baseline-check`, `direction-index-control` | n=1 — agent adjudication (H1621), no human key |
| xref shared core | 40 `sharedCoreRows` + 10 `prefixControlRows` = 50 | `csl-atlas-xref-shared-core_40edges`, 40 cards | `lexical-shared-core`, `prefix-convention`, `normalization-risk`, `too-sparse` (+ `edition-continuity`, `lexical-target` in the packet vocabulary) | n=0 — no human decision recorded; re-dealt to the 694-edge pool by H5453 |

The roadmap's «R2 ×10, H4 ×105, xref ×50» is therefore **145 rows of which 139 are keyable
cards** (105 H4 rows minus the 16 auto-resolved = 89; 50 xref minus the 10 auto-resolved
prefix controls = 40; R2 10). Double-keying them costs **278 keys**, i.e. 28–56 keys per
student at the roadmap's 5–10 recruits.

### 3.1 Two blockers found while probing, both must be fixed before any student sees a sheet

1. **The validator's H4 expected set is empty.** [`expected_sheets()`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate_review_decisions.py)
   selects H4 rows with `reviewStatus == "needs-review"`; H1621 flipped all 105 rows to
   `reviewed-ok` / `auto-resolved`, so the validator expects **0** rows while the builder emits
   **89 cards** (probed 24-09-2026: `csl-atlas-skd-iti_100units` 102, `csl-atlas-tradition-tags_119texts`
   114, `csl-atlas-h4-semantic-field_89rows` **0**, `csl-atlas-xref-shared-core_40edges` 40).
   Every returned H4 export would fail on `decided must equal the full sheet count`. The fix is
   the fallback the builder already has: open rows if any, else the `reviewed-ok` set.
2. **The H4 card shows the agent's answer.** `h4_items()` renders an `Agent decision: <label>`
   line on every card. For a single-reviewer QA pass that is context; for a double-keyed
   reliability measurement it is contamination — both keys would be measuring agreement with a
   visible prior, which is precisely the failure the student guide's «не подсматривайте»
   section warns about. Pool sheets must render **blind** (§7).

## 4. Annotator identity without personal data in the repo

1. **Pseudonym only.** Each recruit gets a stable opaque ID `pool-a01 … pool-aNN`, assigned in
   recruitment order. That string is the *only* annotator token that ever enters csl-atlas —
   in the assignment manifest, in the merged overlay, in the κ report, in a filename.
2. **The roster lives off-repo.** Pseudonym → name, contact, consent date, and course is held
   by the pool coordinator in the private Uprava estate, under the same 152-ФЗ regime as the
   G7 user-study protocol. It is never committed to csl-atlas, never pasted into an issue, and
   never reconstructible from committed data.
3. **Raw exports are never committed.** `review/` is gitignored; incoming files land in
   `review/incoming/` and stay local. Only the merged, pseudonymous overlay is committed.
4. **Timestamps are coarsened.** The export's `reviewedAt` is a full UTC timestamp (the
   validator requires it); the committed overlay keeps the **UTC date only**. κ needs no clock,
   and a per-second timeline of one student's evening is re-identifying detail with no
   scholarly use.
5. **Free-text notes are the real privacy surface.** Students are told to write what they saw
   in the source; some will write «спросила у преподавателя Иванова» or leave a handle. The
   merge script therefore **refuses** any note matching an e-mail, an `@handle`, a `t.me/`
   or other user-bearing URL, and the coordinator reads every note before the merge commit.
   At 278 keys this is minutes of work, not a pipeline.
6. **Credit is opt-in and separate.** Being named in the release acknowledgements or
   `CITATION.cff` (optionally with ORCID) is a *publication* consent collected at recruitment,
   independent of the pseudonymous keying data. A student may key anonymously and still be
   thanked, or be thanked and still have their rows carry only `pool-a07`.
7. **Withdrawal is mechanical.** Re-running the merge with a pseudonym excluded drops that
   annotator's keys; affected rows fall back to single-key state, are marked `single-key`,
   leave the κ input, and are re-dealt to another annotator. No row is silently promoted
   because a key disappeared.

## 5. Assignment — every row gets two independent keys

**Inputs:** the packet's rows in canonical order (sorted by `reviewId` / `sampleId` /
`checkpointId`), and the sorted list of `n` active pseudonyms.

**Rule (rotating-offset blocks).** For row index `i` (0-based), let `b = i // n` (block) and
`p = i % n` (position). Let the block offset be `k_b = 1 + (b mod (n − 1))`. The two keys of
row `i` are

```
key A  =  annotator[p]
key B  =  annotator[(p + k_b) mod n]
```

**Why this rule and not round-robin pairs.** It is deterministic (recomputable from the
manifest, no RNG, no seed to lose), it never assigns the same annotator twice to one row
(`k_b` is never `0 mod n`), it balances load exactly — each annotator keys one row as A and
one as B per block, so `2R/n` rows overall, ±2 in the final partial block — and, critically,
**it rotates partners**: over `n − 1` consecutive blocks each annotator is paired with every
other annotator. A fixed-offset scheme would freeze the pool into `n` dyads and turn the
agreement measurement into a statement about a handful of pairs.

**Minimum pool: n ≥ 4.** At n = 2 there is one dyad and no rotation; at n = 3 each annotator
carries two thirds of the packet. The roadmap's 5–10 recruits sit comfortably above the floor.

**Worked example — xref, 40 rows, n = 6.** Blocks 0–5 are full, block 6 holds rows 36–39.
Offsets run 1, 2, 3, 4, 5, 1, 2. Row 0 → `a01 + a02`; row 7 (`b=1, p=1, k=2`) → `a02 + a04`;
row 38 (`b=6, p=2, k=2`) → `a03 + a05`. Each annotator ends with 13–14 of the 40 rows and has
worked opposite all five colleagues.

**Manifest.** The deal is committed as `data/review/pool_assignment.json`:

```json
{
  "schemaVersion": "1.0.0",
  "poolVersion": "v1",
  "generatedAt": "<ISO-8601 UTC>",
  "generatedBy": "npm run build-review-pool-assignment",
  "rule": "rotating-offset-blocks; keys(i) = [A[i%n], A[(i%n + 1 + (i//n) % (n-1)) % n]]",
  "annotators": ["pool-a01", "pool-a02", "..."],
  "packets": {
    "csl-atlas-xref-shared-core_40edges": {
      "sourcePacket": "data/lexico/xref_source_check_packet.json",
      "rows": { "mw-pwg-shared:01": ["pool-a01", "pool-a02"] }
    }
  }
}
```

It carries no personal data, it is the validator's authority for «is this reviewer allowed to
key this row», and it makes the deal auditable by anyone reading the repo.

**Blindness.** A student receives only their own slice, rendered as their own sheet file. The
card never names the partner, never shows a prior decision (§3.1 item 2), and the sheets are
delivered privately, not published to a hub.

## 6. Submission path

The atlas has no backend and will not grow one for this (`CLAUDE.md`,
[`docs/BOUNDARY_RULES.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BOUNDARY_RULES.md)).
v1 is therefore **file-return over the channel the student was recruited on**:

1. The coordinator builds the per-annotator sheets and sends each student their single HTML
   file plus the student guide link.
2. The student keys their slice offline and presses «Скачать decisions.json».
3. The student returns that one file to the coordinator (Telegram or e-mail — the same channel
   used for recruitment; no new data processor is introduced).
4. The coordinator files it as `review/incoming/<sheet_id>__<pool-id>__<YYYY-MM-DD>.json`
   (gitignored) and runs `npm run validate-review-decisions -- <file>` in pool mode.
5. PASS → the file joins the merge input. FAIL → the validator's message goes back to the
   student verbatim (a missing row, a corrected label outside the vocabulary, a rejection with
   no rationale); they fix and resend. The validator, not the coordinator's patience, is the
   quality gate.

**Rejected alternatives**, recorded so they are not re-proposed:

1. *Student opens a PR / attaches the file to a GitHub issue.* Requires every student to have a
   GitHub account, publishes their identity and their free-text notes, and points write traffic
   at a `sanskrit-lexicon` org repo. Rejected on privacy and on repo hygiene.
2. *Third-party form with file upload.* Adds an external processor for files containing
   free-text notes under a 152-ФЗ regime, for the sole benefit of saving the coordinator a
   file-copy. Rejected.
3. *A small submission backend (Netlify/Cloudflare function).* Out of scope by
   `BOUNDARY_RULES.md`, and it would have to be maintained by a bus-factor-1 project (G8) to
   serve at most a few hundred file transfers. Reconsider only if round 2's «300 entries × 7
   dicts» scale (Q1 2027) makes manual intake the bottleneck — with a measured intake cost from
   v1 as the evidence.

## 7. What must be built — the gap, in dependency order

Each item is small and named; none of them is a new framework.

| # | Change | File | Why |
|---|---|---|---|
| B1 | H4 expected-sheet fallback: open rows if any, else `reviewed-ok` — mirroring `h4_items()` | [`scripts/validate_review_decisions.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate_review_decisions.py) + [`scripts/test_validate_review_decisions.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/test_validate_review_decisions.py) | §3.1(1): today every H4 export fails |
| B2 | Pool mode `--pool data/review/pool_assignment.json`: `reviewer` must be a known pseudonym (replacing the hard-pinned `REVIEWER = "gasyoun"`), and the item set must equal **that annotator's assigned rows**, not the whole packet; `defer` requires a note | same two files | a per-annotator slice is a partial sheet; the whole-sheet 1:1 check would reject every pool export |
| B3 | Blind rendering: suppress the `Agent decision:` line and any recorded prior when building a pool sheet | [`scripts/build-review-sheets.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-review-sheets.py) | §3.1(2): independence is the whole measurement |
| B4 | `--annotator <pool-id>` slice mode: emit only the assigned rows and write the pseudonym into the export's `reviewer` field. **`sheet_id` keeps its stem** — it is the filename/localStorage/validator contract (the same reason H5407 kept `_119texts` at 114 rows) | same file | identity travels in `reviewer`, so no emitter change is needed |
| B5 | An R2 sheet (`r2_items()`, 10 cards from `r2_checkpoint_review_packet.json`, vocabulary = the row's `proposedParserLabels`), with MG's recorded decisions withheld from the card | same file | R2 has no sheet at all today |
| B6 | Assignment builder → `data/review/pool_assignment.json` + `data/schema/pool-assignment.schema.json` | `scripts/build-review-pool-assignment.mjs`, `npm run build-review-pool-assignment` | §5 |
| B7 | Merge + adjudication: two keys per row → overlay record, disagreements → adjudication packet; note-scrub refusal (§4.5); `single-key` marking | `scripts/merge-review-pool-decisions.py`, `npm run merge-review-pool-decisions` | §8 |
| B8 | κ report → `data/review/pool_kappa_report.json` + generated `docs/REVIEW_POOL_KAPPA_REPORT.md` with a Chart Trust Block | `scripts/lexico/review_pool_kappa.py`, `npm run build-review-pool-kappa` | §9 |
| B9 | Tests: assignment properties (two distinct keys per row, load within ±2, every pair realised for n ≥ 4), merge truth table, κ against a hand-computed fixture | `test/review-pool-assignment.test.mjs`, `scripts/test_validate_review_decisions.py` | the assignment rule is the one place a silent bug would quietly destroy the measurement |

B1 is a live defect and should land first, independently of the rest.

## 8. Merge and adjudication

Agreement is judged on the **resolved label**, not on the button, because two annotators can
both press ❌ and still disagree about the correction:

```
resolved(key) = proposedLabel        if decision == approve
                corrected label      if decision == reject   (parsed from "label: rationale")
                __defer__            if decision == defer
```

| Case | Both keys | Overlay `reviewStatus` | Note |
|---|---|---|---|
| A1 | same label, both `approve` | `reviewed-ok` | the machine label is confirmed by two independent readers |
| A2 | same corrected label, both `reject` | `reviewed-corrected` | `reviewedValue` = the corrected label |
| A3 | both `defer` | `deferred` | excluded from the promoted claim, kept as its own κ category |
| A4 | anything else | `needs-review` → adjudication queue | includes reject/reject with different corrections |
| A5 | one key missing (dropout, withdrawal) | `needs-review`, flagged `single-key` | never promoted, never counted in κ |

**Adjudication rules.**

1. Disagreements are resolved by **reading the source line**, in the shape the repo already
   uses for H1684 and the siglum aliases — not by adding a third blind key, and never by
   majority vote. Two readers who disagree have found an ambiguity; a third button does not
   resolve it, an argument from the source does.
2. The adjudicator sees both anonymised notes (`pool-a03` said X, `pool-a07` said Y), the
   proposed machine label, and the source pointers. The verdict carries a rationale and lands
   as `reviewed-ok` / `reviewed-corrected` with `adjudicated: true` and an `adjudicatedBy`
   pseudonym (`pool-adj01`; MG or a named senior annotator).
3. The adjudicator may return **`blocked`** when the source genuinely cannot settle the row
   (damaged OCR, missing record, a label vocabulary that does not fit). That is a finding, not
   a failure: it feeds the taxonomy revision and is reported as its own count.
4. **A tie never defaults to the machine's proposed label.** Defaulting toward the generator
   would re-import exactly the bias the double-keying exists to measure.
5. κ is computed on the **pre-adjudication** keys. Post-adjudication agreement is 1.0 by
   construction and says nothing about anything.

## 9. The κ report

**Statistic.** Because partners rotate (§5), the raters are *not* fixed across items, so a
single Cohen's κ over the packet is the wrong instrument. The report carries, per packet:

1. **Krippendorff's α (nominal)** as the headline — it is defined for varying rater sets,
   unequal loads and missing keys, which is exactly this design.
2. **Cohen's κ per dyad**, reported only where the dyad shares **≥ 30** rows; below that the
   report prints `n` and suppresses the point estimate rather than publishing a number with a
   ±0.4 interval.
3. **Raw observed agreement**, **chance-expected agreement**, and the **modal-label share** —
   the base-rate control that [`docs/ROOT_AGREEMENT_KAPPA.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ROOT_AGREEMENT_KAPPA.md)
   already insists on, because a packet where 80% of rows carry one label can show high
   agreement and no reliability.
4. **Button-level 3-way agreement** (approve/reject/defer) as a secondary, interpretable
   figure alongside the label-level one.
5. A **bootstrap 95% CI** over rows (2,000 resamples) on every reported α.
6. **Landis–Koch bands** reused verbatim: `slight` · `fair` · `moderate` · `substantial` ·
   `almost-perfect`.

**Honesty rules, fixed before any data exists.**

1. **R2 is 10 rows.** Its α gets an interval and a plain sentence that n = 10 cannot support a
   reliability claim; it is a pilot of the *machinery*, not a measurement of the packet.
2. **No pooled α across packets** — three different label spaces, three different tasks.
   A single "the atlas scores κ = 0.7" number would be meaningless.
3. **Expert baseline, reported separately.** MG's 10 recorded R2 decisions are a held-out
   expert key: agreement of each pool key against it is reported as `expertBaseline` and never
   mixed into the pool-internal α.
4. **Contamination is stated, not claimed away.** The R2 and H4 prior decisions are public in
   this repo. The guide forbids consulting them; nothing enforces it. The limitation is named
   in the report, and a note containing no source evidence is treated as a quality signal.

**Artifact shape** — `data/review/pool_kappa_report.json`:

```json
{
  "schemaVersion": "1.0.0",
  "poolVersion": "v1",
  "generatedAt": "<ISO-8601 UTC>",
  "generatedBy": "npm run build-review-pool-kappa",
  "evidenceLabel": "derived",
  "reviewStatus": "machine-reviewed",
  "packets": [
    {
      "packetId": "csl-atlas-xref-shared-core_40edges",
      "rows": 40,
      "rowsDoubleKeyed": 38,
      "rowsSingleKey": 2,
      "categories": ["lexical-shared-core", "prefix-convention", "normalization-risk", "too-sparse", "__defer__"],
      "observedAgreement": 0.0,
      "chanceAgreement": 0.0,
      "modalLabelShare": 0.0,
      "krippendorffAlpha": 0.0,
      "alphaCI95": [0.0, 0.0],
      "band": "moderate",
      "buttonLevelAgreement": 0.0,
      "cohenKappaByDyad": [{ "dyad": ["pool-a01", "pool-a04"], "n": 0, "kappa": null, "band": null }],
      "disagreements": 0,
      "adjudicated": 0,
      "blockedByAdjudicator": 0,
      "expertBaseline": null
    }
  ],
  "limitations": ["..."],
  "warnings": []
}
```

The generated `docs/REVIEW_POOL_KAPPA_REPORT.md` renders the same numbers under the house
Chart Trust Block (Claim · Evidence label · Source files · Generated by · Validation · Known
false positives/negatives · Review status · Owner repo · Next use · Boundary note), so the κ
figure is citable in P1/P2/P5 the way every other atlas number is.

## 10. Rollout

| Phase | Deliverable | Gate to the next phase |
|---|---|---|
| P1 | B1 landed (validator H4 fallback) | `npm run validate-review-decisions` accepts a synthetic full H4 export |
| P2 | B6 assignment builder + B9 property tests | manifest for a synthetic n = 6 pool passes the load/pairing properties |
| P3 | B3–B5 sheet slicing, blind mode, R2 sheet | two per-annotator R2 sheets render and their exports validate in pool mode (B2) |
| P4 | B7 merge + adjudication packet | the R2 pilot merges: agreements promoted, disagreements queued |
| P5 | B8 κ report | R2 pilot α computed with CI and the n = 10 caveat printed |
| P6 | Recruit 5–10 students; deal H4 (89) and xref (40) | κ report published; G4 closed with a measured number |

**Pilot on R2 first**, all ten rows, with two students: it is the smallest packet, it has an
expert baseline to compare against, and it exercises every piece of machinery end to end
before 258 keys are dealt to people whose time is a favour.

## 11. Risks and limitations

1. **Dropout leaves single-keyed rows.** Handled by A5 (never promoted) plus re-dealing; the
   real mitigation is over-recruiting relative to the 2R/n load.
2. **Prior decisions are public.** See §9 honesty rule 4 — measurable-looking agreement could
   be agreement with a copied answer. Unenforceable; stated.
3. **Vocabulary ambiguity inflates disagreement.** This is a feature: a label whose
   disagreement rate is high is a badly-defined label, and the adjudicator's `blocked` verdicts
   are the evidence for revising it.
4. **Selection bias in the xref shared core** (the deterministic first-40 slice, re-dealt by
   H5453) is already documented in
   [`docs/XREF_SHARED_CORE_LABEL_TAXONOMY.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_SHARED_CORE_LABEL_TAXONOMY.md);
   the κ describes the slice, not the 694-edge pool.
5. **Student skill is uneven** — second-year students, one evening of training. Low α on H4 may
   measure the task's difficulty rather than the data's reliability; the report must not
   collapse those two readings into one sentence.
6. **152-ФЗ exposure lives in free-text notes**, not in the verdicts (§4.5).
7. **Bus factor.** The coordinator is a single human doing manual intake (G8). v1 accepts that
   deliberately: 278 keys is a few evenings, and a backend built now would be maintained by the
   same single human.

## 12. Sync rules

1. **Packet counts and label vocabularies** are pinned to the committed packets. If a packet is
   re-cut (as H5453 re-dealt the xref slice), §3's table, the assignment manifest, and the
   student guide's matching tables change in the same PR — the `CLAUDE.md` H5310 rule.
2. **This document is design, not record of results.** Measured α, disagreement counts and
   adjudication outcomes live in the generated κ report and its docs page, never inlined here.
3. **The submission path is v1.** Replacing it with a backend requires a measured intake cost
   from v1 (§6, rejected alternative 3), recorded as a decision, not an improvisation.

_Гасунс_
