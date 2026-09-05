_Created: 04-06-2026 · Last updated: 05-09-2026_

# Concordance — dimension numbering across schemes

**Purpose**: decouple our **operational** fingerprint numbering (the `dim_1…dim_30`
keys baked into every CSV, script, and tree) from **Dhaval Patel's 2016** convention
numbering (the citable source for conventions 1–7). The pipeline is stable on the
L0 IDs; this file is the only place the mapping to external schemes lives, so Patel's
paper order can be confirmed or revised here **without touching code or data**.

**Companion**: [`fingerprint_conventions.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/refs/fingerprint_conventions.md) (definitions),
[`../L0_DESIGN.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/L0_DESIGN.md) §2 (rationale).

---

## Stability contract

1. **`L0-dim-N` is canonical.** Every `data/L0/*.csv` column (`dim_N_value`,
   `dim_N_source`, `dim_N_confidence`), `dim_schema.json` entry, and script keys on
   the integer N. These IDs are **frozen** — never reused or reordered in place.
2. **Human-facing names/order may change freely** — they live in `dim_schema.json`
   (the `name` field) and in this concordance, not in the column keys.
3. **External numbering (Patel 2016, future standards mappings) is recorded here only.** If Patel's
   paper turns out to order his 7 conventions differently from our `dim_1…dim_7`, we
   update the `Patel2016 §` column below — the fingerprint matrix is unaffected.
4. **Retiring a dimension**: mark it `deprecated` in this table and in `dim_schema.json`;
   do not delete the column or renumber survivors (keeps old trees reproducible).

---

## Master concordance (all 30 L0 dimensions)

| L0 dim | CSV column key | slug | category | Patel2016 § | #opts | status |
|---:|---|---|---|:---:|:---:|---|
| 1 | `dim_1_*` | anusvara-before-cons | Patel-orthography | **conv. 1** ✅ | 6 | patel2016 |
| 2 | `dim_2_*` | r-duplication | Patel-orthography | **conv. 2** ✅ | 2 | patel2016 |
| 3 | `dim_3_*` | at-ending (śatṛ/vatup) | Patel-orthography | **conv. 3** ✅ | 5 | patel2016 |
| 4 | `dim_4_*` | inflected-headword | Patel-orthography | **conv. 4** ✅ | 2 | patel2016 |
| 5 | `dim_5_*` | verb-anusvara | Patel-orthography | **conv. 5** ✅ | 3 | patel2016 |
| 6 | `dim_6_*` | rkaranta | Patel-orthography | **conv. 6** ✅ | 3 | patel2016 |
| 7 | `dim_7_*` | vas-yas-suffix | Patel-orthography | **conv. 7** ✅ | 4 | patel2016 |
| 8 | `dim_8_*` | sandhi-compound-boundary | sandhi/compound | — | 3 | gate |
| 9 | `dim_9_*` | compound-hw-separation | sandhi/compound | — | 3 | auto |
| 10 | `dim_10_*` | variant-hw-k2 | sandhi/compound | — | 3 | auto |
| 11 | `dim_11_*` | sense-numbering | polysemy | — | 5 | auto |
| 12 | `dim_12_*` | sense-separator | polysemy | — | 4 | auto |
| 13 | `dim_13_*` | subsense-indentation | polysemy | — | 2 | auto |
| 14 | `dim_14_*` | citation-depth | citation | — | 4 | auto |
| 15 | `dim_15_*` | citation-format | citation | — | 3 | auto |
| 16 | `dim_16_*` | mahabharata-edition | citation | — | 2 | gate |
| 17 | `dim_17_*` | grammar-marker | grammar | — | 3 | auto |
| 18 | `dim_18_*` | verbclass-marker | grammar | — | 3 | auto |
| 19 | `dim_19_*` | etymology-presence | etymology/xref | — | 3 | auto |
| 20 | `dim_20_*` | xref-syntax | etymology/xref | — | 4 | auto |
| 21 | `dim_21_*` | loanword-marker | etymology/xref | — | 2 | auto |
| 22 | `dim_22_*` | vedic-accent | vedic/accent | — | 2 | auto |
| 23 | `dim_23_*` | vedic-only-marker | vedic/accent | — | 2 | auto |
| 24 | `dim_24_*` | frequency-marker | loose-ends | — | 2 | auto |
| 25 | `dim_25_*` | indeclinable-marker | loose-ends | — | 4 | auto |
| 26 | `dim_26_*` | panini-sutra-ref | loose-ends | — | 2 | auto |
| 27 | `dim_27_*` | source-lang-id | loose-ends | — | 2 | auto |
| 28 | `dim_28_*` | etym-presence-rate | etym-richness | — | 2 | auto |
| 29 | `dim_29_*` | etym-mean-length | etym-richness | — | 3 | auto |
| 30 | `dim_30_*` | etym-marker-patterns | etym-richness | — | 3 | auto |
| 31 | `dim_31_*` | takārānta (mahat) | Patel-open §TODO | TODO ✅ | 4 | patel-open |
| 32 | `dim_32_*` | sakārānta | Patel-open §TODO | TODO (new) | 2–3 | patel-open |
| 33 | `dim_33_*` | rephānta | Patel-open §TODO | TODO (new) | 2 | patel-open |

**Legend.** `Patel2016 §` — the convention's number in Dhaval Patel's 2016 paper;
`✅` = confirmed against the PDF. `—` = a project addition, not in Patel 2016.
`#opts` — option count (see `fingerprint_conventions.md`). `patel2016` status = the
cell is populated from Patel's own per-dict assignments.

---

## Patel 2016 ⟶ L0 (confirmed 2026-06-03)

Confirmed against `refs/Patel_2016_Normalizing_headwords.pdf`: Patel's conventions
appear in his paper in the **same order** as our `dim_1…dim_7`. The numbering coincides.

| our L0 dim | our short name | Patel 2016 conv. # | Patel's own title | confirmed |
|---:|---|:---:|---|:---:|
| 1 | anusvara-before-cons | 1 | Treatment of anusvāra before consonants | ✅ |
| 2 | r-duplication | 2 | Duplication of consonants after 'r' | ✅ |
| 3 | at-ending | 3 | Treatment of words ending with 'at' | ✅ |
| 4 | inflected-headword | 4 | Uninflected / inflected forms | ✅ |
| 5 | verb-anusvara | 5 | Treatment of anusvāra of verb | ✅ |
| 6 | rkaranta | 6 | Treatment of ṛkārānta words | ✅ |
| 7 | vas-yas-suffix | 7 | Treatment of words ending with vas/yas (kvasu/vasu/īyasun) | ✅ |

> **Reference**: Dhaval Patel. 2016. *Normalizing headwords of Cologne digital dictionaries.*
> PDF: `docs/refs/Patel_2016_Normalizing_headwords.pdf`. Living version + issues:
> `https://github.com/sanskrit-lexicon/hwnorm1`. Per-dict assignments transcribed into
> `scripts/L0/s2d_patel_gold.py` → `data/L0/patel2016_assignments.csv`.
> Coverage: all 36 Cologne-2016 dicts. **Not** covered (still `gate`): LRV, FRI, KNA, KOW, AMAR.

---

## Reserved for future external schemes

When `csl-standards` needs a TEI Lex-0 or OntoLex-Lemon mapping for these
dimensions, add reference columns here and keep the export/validation code in
`csl-standards`. This atlas file remains the dictionary-convention concordance.

---

## Change log

| Date | Change |
|---|---|
| 2026-06-03 | Concordance created. Adopted `L0-dim-N` as the frozen operational numbering, decoupled from Patel 2016 (recorded here for citation). No code/data renumbered. |

_Dr. Mārcis Gasūns_
