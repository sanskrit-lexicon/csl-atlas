# H1684 — В2 agent adjudication: SKD *iti*-units + tradition tags

_Created: 27-07-2026 · Last updated: 27-07-2026_

Agent adjudication of the two csl-atlas В2 review sheets, with the human ask reduced to a
stratified blind spot-check under a Wilson-95% promotion gate. Mandated by
[VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md §11](https://github.com/gasyoun/Uprava/blob/main/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md);
in-repo precedent is H1621 (89/89 H4 semantic-field rows).

Model: **Opus 5 1M (`claude-opus-5[1m]`)**.

## What changed

| | before | after |
|---|---:|---:|
| rows owed to a human | 221 | **61** |
| SKD *iti*-units with an agent verdict | 0 | 102 / 102 |
| tradition tags with an agent verdict | 0 | 119 / 119 |
| rows promoted to `reviewed=yes` | 0 | 0 — **gated**, see below |

Nothing is stamped reviewed without the human arm. The agent stage produces verdicts and
evidence; promotion happens only in
[`scripts/apply_h1684_spotcheck.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/apply_h1684_spotcheck.py),
per stratum, after the spot-check clears the gate.

## Sheet 1 — `csl-atlas-skd-iti_100units` (102 units)

[`scripts/adjudicate-h1684-skd-iti.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/adjudicate-h1684-skd-iti.mjs)
→ [`data/lexico/h1684_skd_iti_adjudication_packet.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/h1684_skd_iti_adjudication_packet.json).

Every unit is **re-derived from local `csl-orig/v02/skd`** rather than read from the sample:
the packet's own `text` is `cleanText(…, 200)`-truncated, and **29 of 102** units are longer
than that, so the sampled excerpt alone cannot settle them.

| proposed class | n | confirm | corrected | uncertain |
|---|---:|---:|---:|---:|
| `authority-terminal` | 34 | 24 | 7 | 3 |
| `separable` | 34 | 28 | 0 | 6 |
| `other-no-authority` | 34 | 25 | 9 | 0 |
| **total** | **102** | **77** | **16** | **9** |

| decision rule | rows |
|---|---:|
| `authority-leads-unit` → separable | 45 |
| `content-then-authority` → authority-terminal | 27 |
| `no-authority-signal` → other-no-authority | 25 |
| `grammatical-formula-only` → other-no-authority | 5 |

### The 16 corrections are two defects in the shipped classifier

**False negatives (9).** `SKD_AUTHORITY_HINTS` in
[`build-r2-source-anchors.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-source-anchors.mjs)
is a 17-entry curated list dominated by *text* citations. Bare kośa authorities opening a tail
unit match neither it nor the `ity[a-zA-Z]{3,}` fused pattern, so they were filed
`other-no-authority`: **halāyudhaḥ · trikāṇḍaśeṣaḥ · rājanighaṇṭuḥ (×3) · medinīkara-hemacandrau ·
durgādāsaḥ (Mugdhabodha-ṭīkā) · saṃkṣiptasāra-uṇādivṛttiḥ · sāyaṇaḥ (tad-bhāṣye)**. All are
`separable`.

**False positives (7).** `ity[a-zA-Z]{3,}` also fires on *grammatical* formulae — `ityarthaḥ`
("such is the meaning"), `ityādi`, `ityuktāni`, `ityabhidhīyate`, `ityantam`, `ityavyayaṃ`.
Those are explanatory boundaries, not citational ones — exactly the distinction the sheet puts
to the reviewer — so they are `other-no-authority`. The one genuinely mixed case,
`ityādigopīnāthatarkācāryyaḥ`, *is* a citation (Gopīnātha Tarkācārya behind an `ity-ādi`) and is
read as such.

Consequence for A02/A08: `other-no-authority` is **inflated** and `separable` **under-counted**
in the shipped `pctFusedAmongAuthorityMarked` / `pctSeparableAmongAuthorityMarked` figures.

### The 9 uncertains are all one thing

Every one sits in the 12–30 content-character band around `FUSION_MIN_CONTENT_CHARS = 20` — a
cut point [`build-r2-kosa-fusion.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-kosa-fusion.mjs)
itself documents as "a threshold, not a calibrated cut point". In all nine the agent and the
classifier **agree on the label**; what cannot be certified is the boundary. No other kind of
row was left undecided.

## Sheet 2 — `csl-atlas-tradition-tags_119texts` (119 texts)

[`scripts/adjudicate-h1684-tradition-tags.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/adjudicate-h1684-tradition-tags.mjs)
→ [`data/citations/h1684_tradition_adjudication_packet.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/h1684_tradition_adjudication_packet.json).

Result: **114 confirm · 0 correct · 5 uncertain.** No seed tag was wrong; the value added is
cited evidence plus five named policy questions.

Evidence comes from **both** catalogues, joined through the H1657 ACC↔NCC crosswalk at
**Tier A/B only** — Tiers C (prefix) and D (edit distance) are marked "flagged for adjudication,
not auto-merged" in
[`P1_COUNTS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/P1_COUNTS.md)
and that adjudication has not run.

| evidence class | rows |
|---|---:|
| `crosswalk-pair-corroborated` (both catalogues, joined as one work) | 22 |
| `catalogue-corroborated` (siglum agrees, unpaired) | 21 |
| `catalogue-hit-no-siglum` | 41 |
| `catalogue-absent` | 29 |
| `catalogue-conflict` (known homonym, recorded) | 6 |

| ruling | rows |
|---|---:|
| `canonical-attribution` (default) | 76 |
| `homonym-conflict-canonical-stands` | 14 |
| `ocr-variant` | 9 |
| `not-a-work` → `other` | 7 |
| `commentator-follows-base-text` | 4 |
| `generic-tradition-label` | 2 |
| `nearest-bucket-vocabulary-gap` | 1 |
| `work-named-via-modern-anthology` | 1 |
| policy forks (→ human) | 5 |

### The five forks

| row | seed | the question |
|---|---|---|
| `Mahāvyutpatti` | `buddhist` | kośa **genre** vs textual **community** |
| `Hemacandra` | `lexical-kosa` | the same fork, decided the other way in the seed data (`jain` exists in the vocabulary) |
| `Bhartṛhari` | `classical-kavya` | two namesakes — the śataka poet vs the Vākyapadīya grammarian; ACC's entry is the **grammarian** |
| `Āpastamba` | `dharma-sastra` | Dharmasūtra vs Śrautasūtra; ACC enumerates the **śrauta** work first |
| `Indische Sprüche` | `classical-kavya` | modern anthology (→ `other`, as for Benfey's reader) vs its classical content |

One human ruling settles the first two together.

## The trap this had to be built around

**Title-only matching into ACC/NCC is homonym-dense.** Both catalogues list many distinct works
under one title, so the first folded-key hit is often a different work. Measured:

| row | first catalogue hit | actually |
|---|---|---|
| `Lalitavistara` | a **Śaiva** Śiva–Pārvatī dialogue | the Mahāyāna sūtra |
| `Bhāvaprakāśa` | Śāradātanaya's **alaṃkāra** work | Bhāvamiśra's āyurveda |
| `Līlāvatī` | **Nyāya**līlāvatī | Bhāskara's gaṇita |
| `Bṛhatsaṃhitā` | a **dharma** text "by Vyāsa" | Varāhamihira's |
| `Ratnāvalī` | "an elementary grammar" | Harṣa's nāṭikā |
| `Hitopadeśa` | "med. See Vaidyahitopadeśa" | Nārāyaṇa's fables |
| `Saddharmapuṇḍarīka` | an āyurvedic text from Central Asia | the Mahāyāna sūtra |

So a hit **corroborates only when its subject siglum agrees** with the ruled tradition, and an
unanticipated conflict **demotes the row to human review** rather than being confirmed silently.
Sigla from an ACC entry and an NCC entry may be pooled as one work's evidence **only** when a
crosswalk pair asserts they are one work.

Two extractor bugs were found and fixed by that same safety property, not by inspection:

- **Case-insensitive siglum matching** read the Paris Grantha shelfmark `(Gr. I. II)` in
  `Taittirīya Saṃhitā` as the grammar siglum `gr.`. Matching is now case-sensitive and
  windowed to the first 40 characters (where the subject siglum always sits; past that is the
  manuscript-reference run).
- **A short-circuited Tier-B lookup** meant an ACC record whose raw key matched *some* query key
  was never delivered to a *spelling-variant* query key — so the sheet's OCR row `Raghuvanśa`
  saw nothing while `Raghuvaṃśa` got everything. The two lookups are now additive
  (ACC coverage 81 → 83 keys, NCC 33 → 43).

## Review provenance — why a boolean was not enough

`tradition_tags.tsv` gains a **`reviewed_by`** column, and
[`build-tradition-tags.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-tradition-tags.mjs)
gains a third review state.

The old derivation was `allReviewed ? "human-reviewed" : "inferred-pending-review"`. Promoting
agent verdicts into that boolean would have made the packet claim **`human-reviewed` for rows no
human ever read** — the evidence label silently upgrading itself. Now:

| `reviewed_by` on the reviewed rows | `reviewStatus` | `evidenceLabel` |
|---|---|---|
| — (some rows unreviewed) | `inferred-pending-review` | `inferred` |
| all `human` | `human-reviewed` | `human-verified` |
| any `agent-h1684` | `agent-adjudicated-human-gated` | `agent-adjudicated` |

[`validate-tradition-tags.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-tradition-tags.mjs)
fails the build on a reviewed row with no provenance, a provenance with no review, and on any
packet claiming `human-reviewed` while carrying agent-attributed rows.

## The remaining human ask — 61 rows

Built by
[`scripts/build_h1684_spotcheck_sheet.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build_h1684_spotcheck_sheet.py)
into `review/csl-atlas-h1684-spotcheck_61rows_review.html`. `review/` is gitignored, so the
sheet and its manifest are local artefacts — both regenerate identically from the committed
packets (the sample is systematic, not random).

- **14 forks** — shown *with* the agent's analysis; the reviewer rules. Not gated.
- **47 blind rows** — shown *without* the agent verdict, exactly as the original sheet showed
  them. A reviewer told what the agent decided cannot independently measure whether it is right.

Sizes are derived, not chosen. Promotion needs the Wilson 95% lower bound of human–agent
agreement to reach **0.80**; `n` is the smallest sample whose *unanimous* agreement clears that,
with a finite-population correction (the strata are small and sampled without replacement):

> n ≥ π₀·z²·N / ((1−π₀)·(N−1) + π₀·z²)

| stratum | N | n | unanimous lower bound |
|---|---:|---:|---:|
| `skd-iti/agent-confirmed` | 77 | 13 | 0.801 |
| `skd-iti/agent-corrected` | 16 | 9 | 0.834 |
| `tradition/canonical-attribution` | 76 | 13 | 0.801 |
| `tradition/ruled-override` | 38 | 12 | 0.816 |

Strata are gated **independently**: one that fails, or that has too few resolved votes after
defers to meet its `n`, is not promoted and its rows return to the queue. Wilson form matches
[`scripts/compound_share.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/compound_share.py).

## Reproduce

```
node scripts/adjudicate-h1684-skd-iti.mjs          # needs ../csl-orig/v02/skd
node scripts/adjudicate-h1684-tradition-tags.mjs   # needs ../SanskritLexicography works_catalogue
python scripts/build_h1684_spotcheck_sheet.py
# vote in review/csl-atlas-h1684-spotcheck_61rows_review.html, save decisions.json beside it
python scripts/apply_h1684_spotcheck.py
node scripts/build-tradition-tags.mjs && node scripts/validate-tradition-tags.mjs
```

Both adjudicators are read-only against `csl-orig` and the works catalogue.

_Dr. Mārcis Gasūns_
