_Created: 20-09-2026 · Last updated: 20-09-2026_

# Evidence-dependence audit — are A10's three strongest descent signals independent? (H5073)

Executor: Claude Code Opus 5 (`claude-opus-5`), 20-09-2026. Handoff: Uprava
[H5073](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5073-Opus_csl-atlas_forensic-combined-evidence-dependence-audit_17.09.26.md)
(minted by Codex Astra `gpt-6-astra`, 16-09-2026). Predecessor:
[`FORENSIC_CLAIM_PINS_COVERAGE_08-09-2026.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/FORENSIC_CLAIM_PINS_COVERAGE_08-09-2026.md)
(H4352), which pinned the *arithmetic* of the nine highest-claim scripts.

## Why this audit exists

H4352 proved each forensic number is computed correctly. That is a different
question from whether the numbers are **independent evidence**. A10
([`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md))
stacks several individually valid signals into one historical conclusion. If two
signals read the same underlying events, or one witness is counted twice, the
*combination* overstates the case while every single figure stays right. That is
the failure mode this audit tests for — and it is the failure mode a reader of a
published paper about a named scholar would find first.

Everything below is deterministic, offline and seeded
(`seed = 20260920`, 200 permutation replicates), and regenerates with:

```bash
python scripts/forensic/parse_cslorig.py mw pwg pw ap ben sch pwkvn ae ap90 bhs bor gra lrv skd vcp
```

```bash
python scripts/forensic/f11_evidence_dependence.py
```

**Corpus revision pinned for this run:** `csl-orig` at
[`30b2ae7b`](https://github.com/sanskrit-lexicon/csl-orig/commit/30b2ae7b3c6619b1ac6a417a02e4af907c1dd9d4)
(2026-08-29). Per-input SHA-256 hashes are in the `source_hashes` block of
[`f11_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f11_report.json).
Arithmetic pins: [`tests/forensic/test_f11_evidence_dependence.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_f11_evidence_dependence.py)
(13 tests, hand-derived fixture, null fixture asserting exactly zero).

## 1. The three claims, their signals and their loci

| Claim | A10 § | Signals | Locus set | n |
|---|---|---|---|---|
| `A10-C1` citation apparatus | 3.2 | `S-F1-JACC` per-lemma source-Jaccard · `S-F1-RARE` corpus-rare shared exact references | `L-CIT-LEMMA` headwords both MW and PWG cite | 80,600 |
| | | | `L-RARE-EVENT` (lemma, reference, witness) triples | 598 |
| `A10-C2` citation order | 3.4 | `S-F5-ORDER` sequence concordance · `S-F5-IDENT` perfectly-identical share | `L-ORD-ENTRY` entries sharing ≥ 3 citation sigils | 3,583 |
| `A10-C3` shared omission | 3.5 | `S-F9-GAPSENS` gap-sensitivity ratio | `L-ANCHOR-WORD` SKD ∩ VCP indigenous-attested words | 6,941 |

Graph edges are emitted as
[`evidence_dependence_graph.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/evidence_dependence_graph.csv);
pairwise locus overlap as
[`evidence_dependence_loci.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/evidence_dependence_loci.csv).

## 2. Deduplicated evidence accounting

| Quantity | Value |
|---|---|
| `L-CIT-LEMMA` + `L-ORD-ENTRY` + `L-ANCHOR-WORD`, naively summed | 91,124 |
| distinct loci in the union | 83,844 |
| **double-counted by the naive sum** | **7,280** |
| `L-ORD-ENTRY` loci absent from `L-CIT-LEMMA` | **0** |
| `L-ANCHOR-WORD` loci absent from both citation sets | 3,244 |

And at the level of individual source events in the rare-reference pool:

| Quantity | Value |
|---|---|
| naive witness events (lemma, reference, witness) | 598 |
| **independent source events** (lemma, reference) | **574** |

## 3. What the controls found

### 3.1 `A10-C2` is a nested refinement of `A10-C1`, not a second signal

**Every one of the 3,583 order-bearing entries is already an `A10-C1` locus**
(3,583 / 3,583 = 100 %). This is forced by construction — an entry cannot share
three citation sigils with PWG unless both works cite the headword — but A10
never says so, and §3.4 is introduced as though it were an additional
observation: "Sharing *which* texts to cite (§3.2) is consistent with merely
using the same sources; sharing their *order* is not."

That sentence is correct about what the order signal *adds* (a stronger
inference from the same events). It is wrong if read as two independent bodies
of evidence. C2 re-reads a 4.4 % subset of C1's loci and asks a sharper question
of them. The right summary is one evidence base, two questions — not two
corroborations.

### 3.2 `A10-C3` is the claim that genuinely adds loci

| Overlap | n | share |
|---|---|---|
| `L-ANCHOR-WORD` ∩ `L-CIT-LEMMA` | 3,697 | 53.3 % |
| `L-ANCHOR-WORD` ∩ `L-ORD-ENTRY` | 340 | 4.9 % |
| **`L-ANCHOR-WORD` touching neither** | **3,244** | **46.7 %** |

The shared-omission test rests on words chosen precisely because they lie
outside the European lineage, and the measurement confirms it: nearly half its
anchor is invisible to the citation signals. `A10-C3` is the load-bearing
independent leg of the combination, which is the opposite of how §3.5 presents
itself ("corroborates rather than proves").

### 3.3 The rare-reference pool is one text (`CTRL-ABL-H`)

| | n | share |
|---|---|---|
| rare shared exact references | 598 | — |
| of which `HARIV.` | 565 | **94.5 %** |
| residue after ablating Harivaṃśa | 33 | over 18 distinct sigils |

A10 §3.2 presents "**587 rare exact references shared for the same headword**"
as a mass observation and §6 presents the Harivaṃśa vulgate resolution
("206/565 corroborated at the exact cited śloka, ≈ 75× the shuffled null") as the
decisive run-to-ground. **These are the same source events.** Ablate one text and
the idiosyncratic-shared-apparatus mass falls to 33 events. The §6 result is not
independent corroboration of §3.2's pool; it is a deeper examination of 94.5 % of it.

This does not weaken §6 — resolving those 565 against the vulgate is exactly the
right thing to have done — but the two must not be added together.

### 3.4 Witness duplication (`CTRL-DUP`, `CTRL-PWDUP`)

`CTRL-DUP` is the acceptance control: a **verbatim duplicate of the PWG witness**
is injected into the evidence pool and the accounting must not reward it.

| | naive witness events | independent source events |
|---|---|---|
| before seeding | 598 | 574 |
| after seeding a verbatim PWG duplicate | 1,125 | **574** |
| delta | +527 (+88.1 %) | **0** |

**Control passes.** A duplicated witness inflates the naive count by 88 % and
moves independent support by exactly zero.

`CTRL-PWDUP` measures the *real* partial duplicate already in the evidence base:
PW is Böhtlingk's own abridgement of PWG, so PWG/MW and PW/MW are not two
independent corroborations.

| | n |
|---|---|
| PWG witness events | 527 |
| PW witness events | 71 |
| carried by both Petersburg witnesses | 24 (**33.8 %** of PW's) |
| independent source events in the union | 574 (naive 598, −4.0 %) |

The inflation here is small (4 %) because PW contributes few rare references at
all. The same caution applies with more force to the §3.1 containment gradient
(PWG→MW 0.70, PW→MW 0.71) and the §3.4 gradient (PWG 0.81 > PW 0.73), where two
numbers from one author's two editions read as two data points.

### 3.5 `A10-C1` survives ablation of the common texts (`CTRL-ABL-S`)

If the 0.16–0.19 Jaccard were carried by the handful of texts every Sanskritist
cites, it would be convergence, not transfer. Dropping the 25 most widely cited
sigils:

| pair | mean source-Jaccard | top-25 ablated |
|---|---|---|
| PWG/MW | 0.1579 | 0.0684 |
| PW/MW | 0.1791 | 0.1564 |
| AP/MW (null) | 0.0163 | 0.0042 |
| BEN/MW (intermediate) | 0.1016 | 0.0494 |

Lineage-over-null separation **rises** from 9.69× to 16.29×. The control could
have killed the claim and did not: `A10-C1` is not riding on shared common texts.

### 3.6 `A10-C2` survives the convention control (`CTRL-CONV`) — the sharp test

A10 §3.4 asserts the order agreement is "Petersburg-*specific*, not a shared
scholarly ordering convention", and supports that with a gradient whose
independent arm is admittedly thin (Apte n = 8 entries). A gradient built on
8 entries cannot carry that weight, so this audit tests the assertion directly.

For each dictionary, derive its **global** ordering convention — the mean
normalised position of every sigil across all its entries — then partition the
scored pairs by whether MW's and PWG's global conventions already agree on that
pair's direction:

| pair class | pairs | MW follows PWG's per-entry order |
|---|---|---|
| conventions agree | 20,363 | 0.8006 |
| **conventions disagree** | **4,685** | **0.7518** |
| within-entry permutation floor (`CTRL-PERM`, 200 reps) | — | 0.5004 (range 0.4890–0.5117) |

On the 4,685 pairs where the two dictionaries' *habits* point in opposite
directions, MW still follows PWG's particular article 75.2 % of the time. Only
≈ 0.05 of the 0.811 is attributable to convention agreement. **§3.4's central
assertion survives its sharpest available control**, and now rests on 4,685
convention-defying pairs rather than an 8-entry null.

The Apte arm under the same control is 0.2308 on 13 discordant pairs — the right
direction, still far too thin to cite. It should be reported as thin, not as a
null.

`CTRL-PERM` also reproduces A10's quoted baseline from an actual permutation
rather than assertion: 0.5004 concordance, 10.14 % chance-identical, against the
article's "0.50 concordance and only ~5–17 % chance-identical".

## 4. Reproduction against the frozen figures — a pinning gap

| signal | published (2026-06-03) | this run (`csl-orig` 30b2ae7b) | delta |
|---|---|---|---|
| `S-F1-RARE` rare shared references | 587 | 598 | **+11** |
| `S-F1-RARE` of which Harivaṃśa | 565 | 565 | 0 |
| `S-F5-ORDER` entries | 3,593 | 3,583 | −10 |
| `S-F5-ORDER` concordance | 0.8107 | 0.8108 | +0.0001 |
| `S-F5-IDENT` identical share | 47.8 % | 47.73 % | −0.07 pt |
| `S-F9-GAPSENS` MW | 12.336 | 12.336 | **0** |
| `S-F9-GAPSENS` AP | 1.51 | 1.51 | **0** |

The pattern is diagnostic. **F9 reproduces to the digit because it reads frozen
`key1` headword exports; F1 and F5 drift because they read `../csl-orig`
directly, and no `.source.json` sidecar records which revision of it.** The
sidecars pin the *csl-atlas* commit only (`commit`, `utc_iso`, `script`), and
A10 §7 says "over `../csl-orig`" with no revision. Three months of upstream
corrections moved the rare-reference residue: this run gains 12 `PAÑCAT. I–IV`
and 2 `HIT.` events and loses 3 `KAUŚ`.

Nothing here contradicts the H4352 arithmetic pins — those run against fixtures
and still pass (61 tests). The gap is provenance, not correctness: **a published
forensic figure over a moving upstream is not reproducible until the upstream
revision is recorded.** `f11_report.json` records it; the other `f*_report.json`
files do not.

## 5. Verdicts

| Claim | Verdict | Basis |
|---|---|---|
| `A10-C1` §3.2 citation apparatus | **Survives** | separation rises to 16.3× after ablating the 25 commonest texts (`CTRL-ABL-S`). |
| `A10-C1` rare-reference sub-signal | **Weakens** | 94.5 % one text; 33 events survive Harivaṃśa ablation; same event set as §6, not a second line (`CTRL-ABL-H`). |
| `A10-C2` §3.4 citation order | **Survives, but is not independent of C1** | 0.7518 on 4,685 convention-discordant pairs vs a 0.5004 permutation floor (`CTRL-CONV`, `CTRL-PERM`); 100 % of its loci are C1 loci. |
| `A10-C3` §3.5 shared omission | **Survives; the only independent leg** | 46.7 % of its anchor is untouched by either citation signal; reproduces to the digit. |
| Combination as published | **Overstated in framing, not in arithmetic** | 7,280 loci double-counted by a naive sum; §3.2 + §6 are one stratum; PW is a partial duplicate of PWG. |

No claim was refuted, and no published number was found wrong. What the audit
changes is how the signals may be *combined*: the conclusion should rest on
**two** independent evidence bases (the citation apparatus, examined twice at
different resolutions; and the omission anchor), not four or five.

## 6. Edits owed to A10

Landed with this audit, minimal and sourced:

1. §3.2 — state that the rare-reference pool is 94.5 % Harivaṃśa and is the same
   event set §6 resolves.
2. §3.4 — state that the order-bearing entries are a subset of §3.2's shared
   cited lemmas, and cite the convention control instead of leaning on the
   8-entry Apte null.
3. §7 — record that `.source.json` sidecars do not pin the `csl-orig` revision,
   and name the revision this audit ran against.

Not done, and deliberately: no published figure was revised, because none
changed for a reason other than upstream corpus drift, and re-freezing A10's
numbers against a newer `csl-orig` is a separate, larger job than this handoff's
scope (it would move every `f*_report.json` at once).

## 7. Limitations

1. The `A10-C2` verdict rests on a global-convention estimator (mean normalised
   sigil position). A compiler whose convention is *conditional* — Veda first in
   grammatical entries, epic first in narrative ones — would be scored as
   convention-defying here. The 0.7518 is therefore an upper bound on
   article-level copying and a lower bound on convention; disentangling them
   needs an entry-type covariate this repo does not yet carry.
2. `CTRL-ABL-S` ablates by corpus document-frequency, which correlates with (but
   is not) "texts everyone cites".
3. The Apte arms of both `S-F5-ORDER` and `CTRL-CONV` rest on 8 entries / 13
   pairs. They are reported, not relied on.
4. `L-ANCHOR-WORD` independence is measured at the level of *loci*, not of
   underlying historical decisions: MW's decision to enter a word and its
   decision to cite a text for that word are not statistically independent even
   when the locus sets are disjoint.
5. Sub-`<L>` entries are folded per `k1`, matching F1/F5; MW's habit of splitting
   one word across several `<L>` records is therefore invisible here, as it is
   in the signals being audited.
6. Every figure describes the Cologne digitizations, not the printed pages.

## 8. Related

- Arithmetic pins: [`FORENSIC_CLAIM_PINS_COVERAGE_08-09-2026.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/FORENSIC_CLAIM_PINS_COVERAGE_08-09-2026.md) (H4352).
- The paper under audit: [`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md) (A10).
- The Harivaṃśa stratum: [`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md).
- The omission anchor: [`SHARED_OMISSION_TEST.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SHARED_OMISSION_TEST.md).
- Citation-tag scope: [`CITATION_TAGGING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/CITATION_TAGGING.md).

_Dr. Mārcis Gasūns_
