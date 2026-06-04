# Proposed SKD anubandha → property key (PROPOSED — awaiting verification)

> **Status: PROPOSED, not applied.** Per [issue #30](https://github.com/sanskrit-lexicon/csl-atlas/issues/30)
> decision round 3 (`MICROSTRUCTURE_DECISIONS.md` #8), SKD pada decoding is **held**
> until the maintainer verifies this key against Vopadeva's *Kavikalpadruma*
> paribhāṣā and Durgādāsa's commentary. `m4_indigenous.py` does **not** yet infer
> SKD pada/veṭ from anubandhas. This file is the artifact to verify.

## What this is

SKD records the dhātupāṭha annotation as **Vopadeva/Kavikalpadruma anubandhas** —
single romanized it-letters immediately after the `¦` headword separator
(`aka¦, i ka lakzmaRi .`). VCP records the **same** grammar explicitly in
`0`-abbreviations (`aGa¦ idit … BvAdi0 Atma0 saka0 sew`). Where a root appears in
**both** dictionaries, VCP tells us what SKD's it-letter *means*.

## Method

`scripts/lexico/_xwalk_skd_vcp.py` aligns the **763 roots that occur exactly once
in each** of SKD and VCP (unambiguous 1:1), and tallies — per SKD anubandha — the
distribution of VCP's explicit pada / transitivity / idit / veṭ. Conservative by
design: homonym sets (>1 entry either side) are excluded so no alignment is guessed.

## The result — it reproduces Pāṇini from raw co-occurrence

This is the validation: four Pāṇinian sūtras fall out of dictionary co-occurrence
without being told to.

| SKD anu | reading | n | VCP pada (para/ātma/ubha) | idit | veṭ | proposed property | basis |
|---|---|---:|---|---:|---:|---|---|
| `Na` | ṅ-it | 232 | 13 / **82** / 4 | 8% | 1% | **ātmanepada** | Pāṇ 1.3.12 anudāttaṅita |
| `Ya` | ñ-it | 67 | 3 / 0 / **96** | 2% | 5% | **ubhayapada** | Pāṇ 1.3.72 svaritañitaḥ |
| `ka` | — | 150 | 0 / 7 / **92** | 8% | 0% | **ubhayapada** | Vopadeva (empirical) |
| `t` | — | 59 | 0 / 5 / **94** | 0% | 0% | **ubhayapada** | Vopadeva (empirical) |
| `ki` | — | 23 | 13 / 0 / **86** | 30% | 0% | **ubhayapada** (+ idit) | empirical |
| `Sa` | ś- | 63 | **90** / 0 / 10 | 0% | 1% | **parasmaipada** | empirical |
| `Si` | ś-i | 15 | **92** / 0 / 7 | 0% | 0% | **parasmaipada** | empirical |
| `ir` | — | 31 | **96** / 0 / 3 | 3% | 25% | **parasmaipada** + veṭ | irit (cf. Pāṇ 7.2.44) |
| `ga` | — | 13 | **80** / 0 / 20 | 0% | 15% | parasmaipada | empirical (low n) |
| `gi` | — | 13 | **75** / 0 / 25 | 0% | 0% | parasmaipada | empirical (low n) |
| `ya` | — | 55 | **76** / 22 / 2 | 0% | 12% | parasmaipada | empirical |
| `O` | au | 44 | **71** / 0 / 28 | 2% | 2% | parasmaipada | empirical |
| `na` | — | 22 | **75** / 5 / 20 | 9% | 13% | parasmaipada | empirical |
| `ma` | — | 23 | **70** / 20 / 10 | 0% | 0% | parasmaipada | empirical |
| `la` | — | 28 | **68** / 13 / 18 | 7% | 3% | parasmaipada | empirical (mixed) |
| `x` | ḷ | 12 | **70** / 0 / 30 | 0% | 8% | parasmaipada | empirical (low n) |
| `i` | i-it | 82 | 60 / 14 / 25 | **90** | 0% | **idit** (num-infix) | Pāṇ 7.1.58 idito num |
| `u` | ū-it | 40 | 69 / 8 / 22 | 0% | **40** | **veṭ** | Pāṇ 7.2.44 …ūdito veṭ |

### Markers this method does NOT resolve — need the maintainer

| SKD anu | reading | n | observation | question |
|---|---|---:|---|---|
| `f` | ṛ-it | **133** | pada splits 50 / 39 / 10 — does **not** fix pada | round 3 #9: ṛ "marks something specific" — **what?** (reserve its own column) |
| `I` | ī-it | 25 | ātma 55 / para 44 — weak ātmane lean | ī-it → ātmanepada? (cf. Pāṇ 1.3.12 set) |
| `o` | au/o | 12 | the **only** transitivity-skewed marker (aka 66%) + idit 16% | does `o` mark akarmaka / a derivation? |

## Transitivity is NOT in the anubandhas

`saka` (transitive) runs 60–95% across **every** marker — i.e. no anubandha
selects transitivity; the corpus is simply transitive-dominant. SKD transitivity
lives in the **Durgādāsa prose** (`sakarmmaka` / `akarmmaka`), handled by a
separate prose detector, not this key.

## How to verify (maintainer)

1. Check `Na`→ātmane, `Ya`→ubhaya, `i`→idit, `u`→veṭ against the Kavikalpadruma's
   own paribhāṣā verses (these are the Pāṇinian-anchored four — should be safe).
2. Adjudicate the **Vopadeva-specific** `ka`/`t`/`ki`→ubhaya assignment — strong
   empirically (86–94%) but not Pāṇinian; confirm it matches the Kavikalpadruma key.
3. Tell me what `f` (ṛ) marks — it is the single most frequent it-letter (133×) and
   currently yields no pada; it deserves its own column.
4. Once confirmed/corrected, I bake the key into `m4_indigenous.py` to emit SKD pada
   (with a `pada_confidence` flag) and lift SKD's coverage toward VCP's.
