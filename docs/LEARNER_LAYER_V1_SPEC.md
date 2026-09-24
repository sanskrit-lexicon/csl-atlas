# Learner reading layer v1 — the per-lemma card and the join contract

_Created: 24-09-2026 · Last updated: 24-09-2026_

Specification for **v1** of the learner's reading layer: what one per-lemma card
contains, which files it is joined from, on what key, how homonyms are handled, how
much of the lemma set each layer actually reaches (measured, not assumed), and which
five readers the card is built for.

Parent handoff: [H5317](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5317-Opus_csl-atlas_learner-layer-v1-card-and-join-spec_23.09.26.md)
(epic [E014](https://github.com/gasyoun/Uprava/blob/main/handoffs/epics)). This document is a
**specification, not an implementation** — nothing here is built yet beyond the v0
index described in §2.

Boundary: [`docs/BOUNDARY_RULES.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BOUNDARY_RULES.md).
The card's primary object is a **dictionary headword**, so it belongs here; the corpus
morphology and frequency behind it belong to
[VisualDCS](https://github.com/gasyoun/VisualDCS) and are **consumed, never re-derived**.

## 1. What the card is

One lemma, one card, four evidence layers around a single organising question — *is
this word worth learning yet, and what do I need to know to read it?*

| Layer | Answers | Comes from |
|---|---|---|
| **Frequency band** | is it worth learning yet | DCS corpus summary (VisualDCS) |
| **Best-attested senses** | what does it mean, ranked by survival | atlas R2 sense-survival (P2) |
| **Root + gaṇa** | what verb is it built on, which class | WhitneyRoots crosswalk |
| **Paradigm link** | how does it inflect, attested | VisualDCS learner-contracts-v1 |

Plus the v0 substrate already shipped: cross-dictionary coverage, representative
gender, and a source pointer that opens the exact line.

## 2. What already exists (v0)

[`scripts/build-learner-index.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-learner-index.mjs)
→ `src/data/learner/learner-index.json`, rendered by
[`src/tools/learner-reading-layer.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/learner-reading-layer.md).
It joins the reader lemma-lookup with the DCS frequency band and stops there — its own
header says *"Whitney roots / gaṇa and per-sense survival are NOT joined here"*. v1 is
exactly the closing of that sentence.

Measured v0 base (probe run 24-09-2026 against the working tree):

```text
learner-index lemmas ......... 52,934
  with a DCS frequency band .. 28,538 (53.9%)
  band 5 / 4 / 3 / 2 / 1 / 0 .. 640 / 3,095 / 7,880 / 9,976 / 6,947 / 24,396
```

Band 0 means **not attested in the DCS corpus** — uncorroborated by this corpus, not
"unused". That distinction is load-bearing for every persona in §3 and must survive
into the UI copy.

## 3. The five audience personas

The card is one artifact; these five read it differently, and each row below is a
hard constraint on the design, not a description.

1. **First-year student (Sanskrit 1, reading a graded reader).** Needs the band and
   one gloss, in IAST, and nothing else on screen by default. Constraint: the default
   card collapses to frequency + top sense + paradigm link; everything else is behind
   a disclosure.
2. **Reading-course student (reading an unedited text with a teacher).** Needs "which
   dictionary do I trust for *this* word" and the exact source line. Constraint: the
   grammar-reliable dictionary count and the `src` pointer stay on the collapsed card.
3. **Teacher / course author (Systema-Sanscriticum).** Needs to filter a text's
   vocabulary by band to build a word list, and to know which cards are sparse before
   assigning them. Constraint: the completeness tier (§8) is a first-class, filterable
   field, not a rendering detail.
4. **Lexicographer / researcher.** Needs the survival ranking to be *legible as
   evidence* — threshold, edge, panel size — never as a bare confidence number.
   Constraint: every ranked sense carries its provenance triple (§6) and the panel
   caveat travels with it.
5. **Integrator / developer (Systema importer, third-party reuse).** Needs a stable
   key, a declared schema and fail-closed behaviour on a version bump. Constraint: the
   join key (§5) and the VisualDCS stable IDs are contract surface — they may not
   change without a migration map, per the
   [VisualDCS architecture](https://github.com/gasyoun/VisualDCS/blob/main/docs/ARCHITECTURE_VISUALDCS_SYSTEMA_LEARNER_CONTRACTS.md).

## 4. Inputs — every file, named and pinned

| # | Input | Path | Key scheme | Role |
|---|---|---|---|---|
| I1 | Reader lemma-lookup | [`src/data/dicts/lemma-lookup.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/lemma-lookup.json) (chunked twin `src/data/dicts/core-lookup/`) | SLP1 | the lemma set + dictionary coverage + gender |
| I2 | Lemma dossier | [`src/data/dicts/lemma-dossier.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/lemma-dossier.json) (28,512 lemmas, `minDicts` 5) | SLP1 | per-dictionary record counts + first line, for the source pointer |
| I3 | DCS lemma summary | `data/dcs/dcs_lemma_summary.json` (sync output, gitignored) | SLP1 | `freqBand` 0–5, `attested` — **consumed, never recomputed** |
| I4 | VisualDCS nominal trainer | [`visual/contracts/v1/nominal-trainer.json`](https://github.com/gasyoun/VisualDCS/blob/main/visual/contracts/v1/nominal-trainer.json) — 31,753 lemmas | **IAST** | paradigm link (`vdcs:v1:nominal:<lemmaId>:<cell>`) |
| I5 | VisualDCS verb trainer | [`visual/contracts/v1/verb-trainer.json`](https://github.com/gasyoun/VisualDCS/blob/main/visual/contracts/v1/verb-trainer.json) — 7,689 roots | **IAST** | root paradigm link (`vdcs:v1:verb:<rootId>:<cell>`) |
| I6 | VisualDCS release envelope | [`visual/contracts/envelopes/learner-contracts-v1-2026-08-09.envelope.json`](https://github.com/gasyoun/VisualDCS/blob/main/visual/contracts/envelopes/learner-contracts-v1-2026-08-09.envelope.json) | — | the pin: `releaseId vdcs-learner-v1-20260809`, commit `6d19eed1`, per-payload sha256 |
| I7 | Whitney roots | [`crosswalk/roots.csv`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.csv) — 930 roots | SLP1 (`root_slp1`) + IAST | root identity, homonym index, short gloss, DCS freq/rank |
| I8 | Whitney gaṇa | [`crosswalk/root_class.csv`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/root_class.csv) — 741 rows | `whitney_no` | gaṇa (I–X) + `certainty` |
| I9 | P2 sense survival (panel) | [`data/lexico/r2_h2h3.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h2h3.json) | SLP1 | panel (28 lemmas), survival threshold, edge statistics |
| I10 | P2 per-sense rows | [`data/lexico/r2_h2_senses.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h2_senses.json) — 807 rows | SLP1 lemma + edge | the ranked senses themselves (`cited`, `survived`, `overlap`, `position`) |
| I11 | Homonym candidates | [`src/data/dicts/homonym-split.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/homonym-split.json) — 9,839 candidates, **400 shipped** | SLP1 | per-dictionary homonym counts, for the ambiguity warning |

**Pin rule.** I4–I6 are consumed at the envelope's `releaseId`, and the build records
that id in the payload. A VisualDCS release bump is a deliberate, reviewed change: the
builder verifies the declared sha256 of each payload it reads and **fails closed** on a
mismatch rather than best-effort parsing (the failure behaviour the VisualDCS
architecture already mandates on the Systema side).

## 5. The join key

**The key is the normalised SLP1 lemma.** One key, four joins, three of which need a
transliteration hop:

```text
I1 lemma (SLP1)
  │ normalizeLemma()      → I3 dcs_lemma_summary  (SLP1, direct)
  │ (identity)            → I7 roots.csv root_slp1 (SLP1, direct) → I8 via whitney_no
  │ slp1ToIast()          → I4 nominal-trainer .lemma  (IAST)
  │ slp1ToIast()          → I5 verb-trainer .rootId    (IAST)
  │ (identity)            → I9/I10 panel lemma, I11 candidate lemma (SLP1)
```

`slp1ToIast` and `normalizeSlp1Lemma` come from
[`src/lib/lookup-normalize.js`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/lookup-normalize.js)
— the repo's single normaliser. The builder must not hand-roll a second one; the
xref-normaliser twin rule in
[`CLAUDE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/CLAUDE.md)
is the precedent for what a second copy costs.

**Direction matters.** The join converts atlas SLP1 *to* IAST, never VisualDCS IAST
back to SLP1: the IAST→SLP1 direction is lossy over accent and anusvāra variants that
the DCS keys carry, and the atlas lemma set is the authority for what a card exists
for. Measured consequence: I4 ships 31,753 lemmas but only **30,182 distinct IAST
strings** — 1,571 of them already collide before the atlas is involved (§7).

## 6. Sense ranking — what "survival-ranked best-attested" means

A ranked sense is a triple, and it is only ever rendered as a triple:

```text
{ text, survived: bool, overlap: float, edge: "<ancDict>→<desDict>", position: int }
```

Rank order: `survived` desc, then `overlap` desc, then `position` asc (earlier senses
in the ancestor article first). Ties break on `position` — never on gloss length, which
correlates with the parser's semicolon behaviour rather than with sense importance.

**Survival is defined, not intuited:** max gloss-word Jaccard ≥ **0.15** against any
descendant sense, the threshold pinned in
[`scripts/build-r2-h2h3.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-h2h3.mjs)
and swept 0.10–0.25 in the paper's sensitivity grid. The card shows the threshold, not
a derived "confidence %".

**What the card must not claim.** The P2 analysis found the cited→survived effect
*edge-concentrated* (essentially all cited senses sit on `ap90→ap`); the pooled odds
ratio is unstable and the clean within-edge test is **not significant** (z = 1.80,
p = 0.072). So the card may say "this sense survives into the later dictionary" — a
per-sense fact — and may **not** say "cited senses survive more often", which is the
population claim the paper reports as an honest null. Persona 4's constraint in §3 is
this sentence.

## 7. Homonym handling

Three distinct ambiguities, three rules:

1. **Dictionary homonyms** (MW `aja` 1 / 2 …). The lemma-lookup key is homonym-blind,
   so one card may cover several dictionary articles. Rule: the card stays one card,
   and when I11 reports `maxHomonyms > 1` it carries a **split warning** with the
   per-dictionary counts and the source links, rather than silently merging senses.
   Measured: 9,839 candidate lemmas, of which only **400 are shipped** in the current
   payload and **332** of those match a learner lemma — so the warning is *advisory
   and incomplete by construction* and must be labelled as such. Raising the shipped
   400 is a separate unit; it is not a v1 blocker.
2. **Whitney root homonyms** (`akṣ` 1 / 2, `root_slp1` shared). Measured: 855 distinct
   SLP1 strings over 930 root rows; **61** atlas lemmas hit more than one root row.
   Rule: show *all* matching roots with their `whitney_no`, homonym index and gaṇa —
   never pick one. `root_alignment.csv` `basis` values (`unique-slp1` vs
   `slp1-shared`) are the audit trail for why.
3. **VisualDCS lemmaId collisions.** Measured: **1,351** matched atlas lemmas map to
   more than one `lemmaId`. Rule: the paradigm link resolves to the highest-`tokens`
   lemmaId, and the card discloses the alternatives; the stable ID recorded on the card
   is the resolved one, so a later re-resolution is visible as an ID change rather than
   a silent re-point.

**The gaṇa is never inferred.** I8 carries `certainty`; `class_uncertain` in I7 marks
the rest. DCS cannot distinguish class I from VI, or IV from the passive, at the
root-class level — the VisualDCS `ceilingNote` says so — so an absent gaṇa is rendered
absent, never guessed from the corpus.

## 8. Measured coverage — what a v1 card actually gets

Measured by
[`scripts/measure-learner-layer-coverage.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/measure-learner-layer-coverage.mjs)
over the working tree, 24-09-2026, against the 52,934-lemma learner index.

| Layer | Lemmas reached | % of index | Note |
|---|---:|---:|---|
| Frequency band (I3) | 28,538 | 53.9% | band 0 = not in corpus, not "unused" |
| Nominal paradigm (I4) | 16,450 | 31.1% | 1,351 with >1 `lemmaId` |
| Verb paradigm (I5) | 778 | 1.5% | root-form headwords only |
| Whitney root (I7) | 690 | 1.3% | 61 homonym-ambiguous |
| …of those, with gaṇa (I8) | 586 | 1.1% | 85% of matched roots |
| Sense survival (I9/I10) | **28** | **0.053%** | the P2 panel, nothing more |
| Homonym warning (I11) | 332 | 0.6% | of 9,839 candidates, 400 shipped |

### Card completeness tiers

| Tier | Definition | Lemmas | Share |
|---|---|---:|---:|
| **A** — full evidence | survival senses present | 28 | 0.05% |
| **B** — grammar-complete | paradigm **and** Whitney root | 541 | 1.0% |
| **C** — partial | paradigm **or** root | 16,508 | 31.2% |
| **D** — frequency + dictionaries only | neither | 35,857 | 67.7% |

Of tier D, 12,236 still carry a frequency band; the remaining 23,621 are the v0 card
unchanged.

**The headline finding, stated plainly: zero lemmas carry all four layers.** All 28
survival-panel lemmas are nominals or derived stems — **none of them is a Whitney
root** — while 27 of the 28 do have a paradigm. So tier A and the root layer are
disjoint today, and the "complete card" that the v1 design implies exists for **no
lemma in the corpus**. v1 must therefore be designed as a **sparse card with named
absences**, not as a full card with occasional gaps. Rendering an empty root slot as
"—" without saying *why* it is empty would make the most common card a silent lie.

**Expected coverage estimate for v1:** ~32% of cards gain at least one new layer over
v0 (tiers A+B+C = 17,077 of 52,934); ~1% become grammar-complete; the survival layer
reaches 0.05% and will stay there until the P2 panel is widened beyond 28 lemmas —
which is a research unit with its own review sheet, not a build step.

## 9. Sparse-state and failure behaviour

1. **Missing layer → named absence**, with the reason from a closed vocabulary:
   `not-in-dcs`, `no-paradigm-contract`, `not-a-root`, `outside-survival-panel`,
   `homonym-payload-truncated`. The v0 page's Trust Block is the precedent.
2. **Digest mismatch on a VisualDCS payload → build fails.** Never a partial card set.
3. **Unknown `contractVersion` → reject**, keep the previous pin. Mirrors the consumer
   rule in the VisualDCS architecture.
4. **A survival claim without its edge and threshold is a defect**, not a rendering
   shortcut.
5. **CSV download** for the card table, per the repo convention.

## 10. Non-goals for v1

1. Widening the P2 panel past 28 lemmas — research, not build.
2. Re-deriving any frequency, paradigm or attestation figure inside csl-atlas.
3. Raising the 400-row homonym payload.
4. Progress tracking, spaced repetition, entitlement — those are
   Systema-Sanscriticum's, per the consumer-ownership split.
5. A search backend; the layer stays exact/prefix lookup over a static payload.

## 11. Acceptance for the implementing unit

Whoever builds v1 is done when:

1. `npm run build-learner-index` emits the card payload with all four layers, each
   absence carrying a reason code from §9.1, and the VisualDCS `releaseId` recorded.
2. A `validate-learner-index` script asserts the §8 tier counts within tolerance and
   **fails** if any card claims a survival rank without `edge` + `threshold`.
3. The page renders tier D (the 67.7% majority) as a legible card, verified on a
   band-0 tier-D lemma — the worst case, not the showcase.
4. `npm test` and `npm run validate-review-reports` stay green.

## Provenance

Numbers in §2, §7 and §8 come from
[`scripts/measure-learner-layer-coverage.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/measure-learner-layer-coverage.mjs),
run against the working tree on 24-09-2026. It reads two sibling repos
(`VDCS_REPO`, `WHITNEY_REPO`), so it is not wired into CI: the implementing unit
re-runs it rather than trusting these figures after any input refresh. The
VisualDCS side is consumed at envelope `vdcs-learner-v1-20260809`
(commit `6d19eed1`, GitHub release `learner-contracts-v1-2026-08-09`).

_Dr. Mārcis Gasūns_
