# Two citation registers, quantified (OBS-C)

Date: 2026-06-10

Corpus-wide measurement of source citations across all 43 `csl-orig` dicts. This
**quantifies** the correction already recorded qualitatively in
[`MICROSTRUCTURE_ZERO_MEANING.md`](MICROSTRUCTURE_ZERO_MEANING.md) (the
`INDIG-CITE` finding): *"SKD/VCP are among the densest citers in CDSL (indigenous
`iti` + quotation style) yet score 0 on an `<ls>`-based counter."* It supplies the
numbers behind that statement and extends the `<ls>` apparatus side with a
resolvability band.

## Trust Block

- Evidence: `<ls>…</ls>` tag extraction and word-boundary `iti`/`ity` counts over
  `../csl-orig/v02/*/*.txt`; siglum normalisation (case + diacritic fold);
  resolvability = numeric locator presence (+ established-siglum membership).
  Extends `build-citation-apparatus.mjs` and the `review-source-siglum` queue.
- Limitations: the `iti` count is a **word-boundary proxy** for indigenous
  citation (it includes some grammatical/derivational `iti`); it is a register
  *indicator*, not a precise citation count. `<ls>` resolvability is "locator
  present", an upper bound on linkability, not a verified link.
- Validation: re-run the per-dict counts; the register split (near-zero `<ls>`
  vs. thousands of `iti` for SKD/VCP/KRM) must hold.
- Owner repo: `csl-atlas`.
- Next use: never report a single `<ls>`-only citation density — always per
  register; build per-dictionary citation-format normalisers (as
  `MICROSTRUCTURE_ZERO_MEANING.md` already calls for) before kośa citation claims.

## Register A — `<ls>`-tagged (European critical-apparatus tradition)

| Measure | Value |
|---|---|
| Total `<ls>` citations | 1,234,530 (~0.83 per entry) |
| With locator (book/chapter/verse/page digits) | **59.8 %** |
| Bare abbreviation (siglum only) | 40.2 % |
| Raw distinct sigla → normalised true sources | 13,021 → 9,180 (1.4×) |
| Sources cited ≥10× (the working apparatus) | **2,166** |
| **Resolvability band** (locator-only → established-siglum+locator) | **59.8 % → 59.1 %** |
| Dictionary-to-book gap (bare-abbrev, unresolvable) | ~41 % ≈ 496,000 citations |

Densest `<ls>` citers: PWG 4.63/entry (570,830), BEN 2.81, BHS 2.71, MW 1.09
(311,933), AP 0.69. Big variant merges: `MBH.`+`MBh.` = 75,548; `ṚV.`+`RV.` =
32,316 — these are already handled by the diacritic/case `foldSiglum()` layer in
[`scripts/lib/source-siglum.mjs`](../scripts/lib/source-siglum.mjs).

The remaining engineering is **abbreviation-family merging** — `R.` = `Rām.` =
`Rāmāy.` → Rāmāyaṇa — which the fold cannot catch.
[`scripts/obs/siglum_families.py`](../scripts/obs/siglum_families.py) generates
**review candidates** for this (it does not auto-merge, respecting the curated
[`dict-source-aliases.json`](../src/data/dict-source-aliases.json) discipline):
folding gives 8,922 fold-keys; 265 prefix-clustered families (e.g. `kathas`/
`kath`/`kathop` → Kathāsaritsāgara; `susr`/`susri` → Suśruta) would collapse to
~8,238 if accepted. The tool deliberately surfaces false merges too (`rajan`
Rājanighaṇṭu vs `rajatar` Rājataraṅgiṇī cluster on the `raja` prefix) — exactly
why merges feed the human-reviewed alias table rather than apply automatically.
The fully reviewed true-source count converges toward the ~2,166 works cited ≥10×.

## Register B — indigenous `iti`/`ity` quotative (Sanskrit-Sanskrit kośas)

These dictionaries cite by quoting a source work followed by the quotative `iti`
(`iti SabdaratnAvalI`, `ityamaraH`, `iti viSvamedinyO`) — and use **zero** `<ls>`
tags. An `<ls>`-only counter therefore mis-ranks them as citation-poor when they
are among the densest.

| Dict | `<ls>` | `iti` citations | iti / entry |
|---|---:|---:|---:|
| KRM | 0 | 6,449 | **3.13** (densest in corpus) |
| SKD | 0 | **69,215** | 1.63 |
| VCP | 0 | **22,070** | 0.44 |
| MCI | 0 | 245 | 0.09 |
| GST | 0 | 236 | 0.03 |
| ARMH | 0 | 181 | 0.02 |

SKD/VCP/KRM cite indigenous authorities (Amara, Trikāṇḍaśeṣa, Śabdaratnāvalī,
Viśva, Medinī, Manu, …) through `iti <source>`. Their dictionary-to-book problem
is **different in kind** from Register A: linking `iti <work>` to indigenous source
lexica, not resolving a page/verse locator.

## Consequence for the apparatus

CDSL contains **two disjoint citation systems**. The 59 % resolvability result and
the source-siglum registry apply to **Register A only**. Per-dictionary citation
density must be reported per register; the existing `review-source-siglum`
normaliser covers Register A, while Register B needs the indigenous
`iti`-source normaliser that `MICROSTRUCTURE_ZERO_MEANING.md` flagged.

## Reproduction

```sh
# Per-dict register counts (<ls> vs iti):
awk '/^<L>/{ent++}
  { s=$0; while(match(s,/<ls>[^<]*<\/ls>/)){ls++; s=substr(s,RSTART+RLENGTH)}
    c=gsub(/[ ”"(]it[iy]/,"&",$0); iti+=c }' ../csl-orig/v02/<dict>/<dict>.txt
# Register-A abbreviation-family merge candidates (review worklist):
python scripts/obs/siglum_families.py    # -> data/obs/siglum_family_candidates.csv
```

_Cross-repo provenance: `csl-observatory/reports/obs_rc_atlas_bridge.md`._
