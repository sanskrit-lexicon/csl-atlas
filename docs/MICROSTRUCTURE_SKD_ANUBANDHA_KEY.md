_Created: 04-06-2026 · Last updated: 05-09-2026_

# SKD anubandha key — the authoritative Dhātudīpikā decode (issue #30)

> **Status: VERIFIED & APPLIED.** This key is no longer a proposal. It is taken from
> the **Śabdakalpadruma front matter** (`docs/refs/SKD_Front pages.docx`), which
> reproduces **Durgādāsa Vidyāvāgīśa's *Dhātudīpikā*** — his commentary on Vopadeva's
> *Kavikalpadruma* — listing the *phala* (effect) of each of the **46 anubandha-letters**
> over SKD's **1754 roots**. `m4_indigenous.py` decodes SKD's per-entry anubandha slot
> with this key (`decode_anubandhas`).

## What SKD encodes, and where

SKD writes each root's it-letters in a **slot right after `¦`**, before the locative
meaning: `aka¦, i ka lakzmaRi` = anubandhas `i`, `ka`. The front matter states the
convention outright (the *grantha-paripāṭī*):

> *"प्रत्येक-धातोरनुबन्धञ्च निर्णीतवान्। येषां धातूनामनुबन्धो नास्ति तत्स्थानं बिन्दुयुक्तमथवा शून्यमास्ते।"*
> — "the anubandha of each root is determined; **roots that have no anubandha get a dot or a zero**."

That is a **primary-source footing for the whole "0 ≠ absent content" methodology**
([MICROSTRUCTURE_ZERO_MEANING.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ZERO_MEANING.md)): a `0` in the slot is
"no anubandha," never "no verb."

## The key — anubandhas encode GAṆA + OPERATIONS, not pada

SLP1: ṅ=`N` ñ=`Y` ṇ=`R` ṭ=`w` ḍ=`q` ś=`S` ṣ=`z` ṛ=`f` ṝ=`F` ḷ=`x` ā=`A` ī=`I` ū=`U` ai=`E` au=`O`.

**Gaṇa markers** (the avāntara sub-gaṇas fold into the 10 main classes):

| it-letter | gaṇa | | it-letter | gaṇa |
|---|---|---|---|---|
| `ka`, `ki` | curādi (10) | | `na` | svādi (5) |
| `ga`, `gi` | kryādi (9) | | `ya`, `Ba`(bha) | divādi (4) |
| `da` | tanādi (8) | | `li` | juhotyādi (3) |
| `Da`(dha) | rudhādi (7) | | `la`, `lu`, `Ga`(gha), `kza`(kṣa) | adādi (2) |
| `Sa`(śa), `Si`(śi), `pa` | tudādi (6) | | `ja`,`Ja`,`Ra`,`Wa`,`mi`,`va` | bhvādi (1) |

**Pada markers — only two:** `N` (ṅ) → **ātmanepada**; `Y` (ñ) → **ubhayapada**
(*ātmane* when the fruit accrues to the agent, else *parasmai*). **Parasmaipada is the
unmarked default** and is deliberately *not* asserted by the decoder.

**Operation-its** (morphophonemic behaviour; no gaṇa/pada): `i`=num(idit) · `A`(ā)=niṣṭhā-veṭ ·
`u`=ktvā-veṭ · `U`(ū)=veṭ · `I`(ī)/`O`(au)=aniṭ · `o`=niṣṭhā -na · `e`=sic a-vṛddhi ·
`f`(ṛ)=caṅ a-hrasva (Pāṇ 7.4.2) · `F`(ṝ)=optional caṅ a-hrasva · `x`(ḷ)=aṅ aorist ·
`m`(ma)=**mit / nici-hrasva** (penultimate shortens before ṇic, Pāṇ 6.4.92 *mitāṃ hrasvaḥ*) ·
`ir`=āḍ · `E`(ai)=yajādi · `Yi`(ñi)=present-sense niṣṭhā · `wu`(ṭu)=athu · `qu`(ḍu)=kṛtrima ·
`za`(ṣ)=kṛt-aṅ · `ta`(t)=adanta marker · `ra`=Vedic-only · `a`=ease of pronunciation only.

## How the cross-walk got it (and where the source corrected it)

The earlier SKD∩VCP cross-walk (`_xwalk_skd_vcp.py`) was an **empirical recovery** that
the primary source then **refined** — a clean methodological arc, not a wasted step:

| cross-walk found | Dhātudīpikā says | verdict |
|---|---|---|
| `N`→ātmane 82%, `Y`→ubhaya 96%, `i`→idit 90%, `u`/`U`→veṭ | ṅ→ātmane, ñ→ubhaya, i→num, ū/u→veṭ | **direct hits** — the four Pāṇinian-anchored markers, recovered exactly |
| `ka`→"ubhaya" 92%, `Sa`→"para" 90%, `ya`→"para" 76%, `na`→"para" 75% | `ka`=curādi, `Sa`=tudādi, `ya`=divādi, `na`=svādi | **mis-attributed** — these are **gaṇa** markers; the pada % was a *shadow* of the gaṇa→pada correlation (curādi tends ubhaya; tudādi/divādi tend parasmai) |
| `f`(ṛ) split 50/39 para/ātma — "no pada signal" | ṛ = caṅ a-hrasva (an operation) | **explained** — ṛ never marked pada |

The maintainer's decision to **hold the key for verification** was exactly right: the
cross-walk recovered the *structure*, the *Dhātudīpikā* corrected the *interpretation*.

## Applied — SKD coverage gains

`m4_indigenous.py` now decodes the slot for SKD (`gaṇa` = anubandha ∨ visarga-prose;
`pada` = prose ∨ ṅ/ñ; raw slot kept in the new `anubandhas` column):

| | before | after |
|---|---:|---:|
| SKD gaṇa resolved | 1,117 | **1,737** |
| SKD pada resolved | 1,167 | **1,498** |

1,925 of 2,544 SKD roots carry a slot; the gaṇa distribution is linguistically correct
(bhvādi ≫ rest once the unmarked default is restored from the visarga prose).

## `ma` — resolved (Palsule's KKD)

The one residual slot token, **`ma` (72×)**, is the **`m` / mit anubandha**: per
G.B. Palsule's edition of the *Kavikalpadruma* (Appendix III, pp. 95–100), `m` is one of
the **17 anubandhas Vopadeva keeps with their Pāṇinian significance** — *mit* → the root's
penultimate vowel **shortens before the causative ṇic** (Pāṇ 6.4.92 *mitāṃ hrasvaḥ*). It is
an operation-it (now in `_ANU_OP`), which is exactly why it never resolved to a gaṇa or pada.

Palsule's account also **corroborates this whole key**: he notes Vopadeva repurposes
`k`, `ṇ`, `p` (Pāṇini used them differently) — matching our **k→curādi, ṇ→phaṇādi(bhvādi),
p→mucādi(tudādi)** — and borrows `au`=aniṭ from the Jainendra Dhātupāṭha (our `O`→aniṭ).
(Palsule counts **43** code-letters; the SKD front matter says 46 — a difference in how
variants are tallied, not in substance.)

## Provenance

Key: `docs/refs/SKD_Front pages.docx` (Dhātudīpikā anubandha-phala table). Decode:
`scripts/lexico/m4_indigenous.py` (`_ANU_KEY`, `decode_anubandhas`) → `indigenous_roots.csv`
(`gana`, `pada`, `anubandhas`). Empirical antecedent: `scripts/lexico/_xwalk_skd_vcp.py`.

_Dr. Mārcis Gasūns_
