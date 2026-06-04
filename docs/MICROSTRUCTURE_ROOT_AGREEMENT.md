# Cross-dictionary verbal-feature agreement (m7, Article 9)

> **Status: BUILT & validated.** `scripts/lexico/m7_root_agreement.py` →
> `data/lexico/root_agreement.json` + `root_feature_conflicts.csv`. Reads m4's
> `indigenous_roots.csv`; `validate_lexico.py` checks it.

## The question

m4 recovers each root dictionary's per-root grammar — **gaṇa** (conjugation class),
**pada** (parasmai/ātmane/ubhaya), **transitivity** — from five *different* in-dict
conventions:

| dict | convention m4 reads |
|---|---|
| SKD | Vopadeva anubandha slot, decoded via the Dhātudīpikā key |
| VCP | `0`-marked forms (`BvA0`, `para0`, `saka0`) |
| KRM | parenthesised grammar cluster (`(I-BvAdiH-792 saka-sew-para)`) |
| YAT | class-digit conjugation block (`{#(O-x) gacCati#} 1. {%a.%}`) |
| SHS | Wilson-tradition prose |

If those five independent extractors, over five independent source traditions, **agree**
on a root's grammar where they overlap, that is strong end-to-end evidence the parses are
real and not artifacts of any one regex. m7 measures it.

## Result — the traditions broadly agree

Over **3,692** distinct roots (SLP1 headword); a root counts toward a feature when **≥2**
dicts give it a label:

| feature | roots ≥2 opinions | unanimous (one label) | **compatible** (multi-class-tolerant) | conflict |
|---|---:|---:|---:|---:|
| **gaṇa** | 1,483 | 1,025 (69.1%) | **1,275 (86.0%)** | 208 |
| **pada** | 1,402 | 878 (62.6%) | **1,055 (75.2%)** | 347 |
| **transitivity** | 1,254 | 871 (69.5%) | **1,015 (80.9%)** | 239 |

- **unanimous** — every dict gives the *same single* label.
- **compatible** — a single label is shared by *every* dict, tolerating roots a dict
  legitimately lists in more than one class (Sanskrit `BUza` is bhvādi *and* curādi). This
  is the fair measure of cross-tradition consensus.

**86% gaṇa compatibility across five independent traditions** is the headline: the
dhātupāṭha class of a root is highly stable across the lexicographic record, and the m4
parses corroborate one another.

## The conflicts are an artifact worth keeping

The 208 / 347 / 239 incompatible roots are **not** flagged as errors. They conflate two
things, both interesting:

1. **Genuine cross-tradition disagreement** — e.g. `BAja` SKD parasmaipada vs VCP/KRM
   ubhayapada; `aka` KRM bhvādi vs SKD curādi.
2. **Legitimate homonymy** — the same SLP1 spelling covering different roots assigned to
   different classes by different editors.

m7 therefore reports them as **analysis, not a review queue** — exactly the call made for
the homonym-split work (differing classification is usually legitimate lexicography). The
full list is in `root_feature_conflicts.csv` (`feature, root, skd, vcp, krm, yat, shs`),
with `|`-joined sets where a dict itself gives several labels.

## Side finding — YAT cites bare stems, the kośa tradition keeps the *uccāraṇārtha* -a

Aligning the root sets surfaced a citation-convention difference worth recording. The
Sanskrit kośa tradition (SKD/VCP/KRM) cites a root **with** Vopadeva's *uccāraṇārtha* -a —
the bare "for-pronunciation" vowel — so `bhāj` appears as `BAja`, `bhram` as `Brama`.
**Yates strips it**, citing the bare stem `BAj`, `Bram`. Consequence:

- **513** YAT roots match a Sanskrit-dict root exactly;
- **+953** more match *only* after restoring a trailing -a.

So YAT's cross-dict agreement above is **conservative** — it undercounts, because most
YAT roots fail the exact-key match. A uniform -a strip would recover them, but it also
**collides homographs** (gaṇa compatibility falls 86.0% → 81.2% in testing, i.e. it
manufactures false conflicts). Normalising root identity across citation conventions is a
lexicographic judgement, so it is **left to the maintainer** (the same gate applied to the
`di0`/`sO0` gaṇa short-forms and the siglum-alias table) and is reported in
`root_agreement.json → yat_citation_convention`, not folded into the measure.

## Method & caveats

Group m4 rows by SLP1 root; per `(dict, root)` collect the **set** of labels (union over
that dict's entries, so a multi-class root is never a self-conflict). `compatible` =
intersection across the participating dicts is non-empty. SKD/SHS contribute fewer
opinions than VCP/KRM/YAT because their feature coverage is lower (SKD pada from the
anubandha slot; SHS prose). Deterministic, no LLM; provenance-stamped.
