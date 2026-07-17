# Two citation registers, quantified (OBS-C)

_Created: 10-06-2026 · Last updated: 17-07-2026_

Corpus-wide measurement of source citations across all 44 `csl-orig` dicts. This
**quantifies** the correction already recorded qualitatively in
[`MICROSTRUCTURE_ZERO_MEANING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ZERO_MEANING.md) (the
`INDIG-CITE` finding): *"SKD/VCP are among the densest citers in CDSL (indigenous
`iti` + quotation style) yet score 0 on an `<ls>`-based counter."* It supplies the
numbers behind that statement and extends the `<ls>` apparatus side with a
resolvability band.

**Snapshot.** All register counts below are regenerated (2026-07-17, H1086) from the
committed artifact
[`data/obs/citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json),
built by
[`scripts/obs/citation_register_gaps.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/obs/citation_register_gaps.py)
over current `csl-orig` (post the 2026-06 dangling-`<ls>` merges; BOR added
upstream 2026-06-14, hence 43 → 44 dicts). The original 2026-06-10 pass used a
space-or-quote `iti` rule that undercounted markup-wrapped kośas (KRM by ~3×:
`<s>iti` was invisible to it); the artifact uses a Latin-letter word boundary
instead. Rows explicitly marked *2026-06 siglum pass* come from the separate
siglum-normalisation analysis and have not been re-run.

**H1086 (2026-07-17) re-derivation:** `<ls>` extraction previously matched only
the bare shape (`<ls>Pāṇ. vi, 2, 161</ls>`); MW's (and other dicts') attributed
shape (`<ls n="RV.">vii, 96, 3</ls>`, locator sometimes split further across
the attribute) went uncounted, and the locator rule only recognised arabic
digits, missing dictionaries whose locators are lowercase roman numerals
(`ŚBr. xiv`). Both are fixed corpus-wide (not MW-only) in
`scripts/forensic/parse_cslorig.py` / `scripts/obs/citation_register_gaps.py` —
every number below moved. PWG dominates the corpus aggregate (`<ls>` count
+41%, 568,730 → 801,788) so the corpus-wide headline shifted materially, from
~59%/41% to ~67%/33%. See `FINDINGS.md` for the defect-class writeup.

## Trust Block

- Evidence: `<ls>…</ls>` tag extraction (via `parse_cslorig.iter_entries`) and
  word-boundary `iti`/`ity` counts (not adjacent to a Latin letter, so
  markup-/punctuation-adjacent quotatives count) over `../csl-orig/v02/*/*.txt`;
  siglum normalisation (case + diacritic fold); resolvability = numeric locator
  presence (+ established-siglum membership). Extends
  `build-citation-apparatus.mjs` and the `review-source-siglum` queue.
- Limitations: the `iti` count is a **word-boundary proxy** for indigenous
  citation (it includes some grammatical/derivational `iti`, and fires on quoted
  running text — FRI, a reader, scores 376 hits without being a citing kośa); it
  is a register *indicator*, not a precise citation count. `<ls>` resolvability
  is "locator present", an upper bound on linkability, not a verified link.
- Validation: re-run `citation_register_gaps.py`; the committed artifact must
  reproduce, and the register split (zero `<ls>` vs. tens of thousands of `iti`
  for SKD/VCP/KRM) must hold.
- Owner repo: `csl-atlas`.
- Next use: never report a single `<ls>`-only citation density — always per
  register; build per-dictionary citation-format normalisers (as
  `MICROSTRUCTURE_ZERO_MEANING.md` already calls for) before kośa citation claims.

## Register A — `<ls>`-tagged (European critical-apparatus tradition)

| Measure | Value |
|---|---|
| Total `<ls>` citations | 1,517,609 (~1.01 per entry) |
| With locator (arabic digit or lowercase roman numeral) | **66.8 %** (1,013,996) |
| Bare abbreviation (siglum only) | 33.2 % (503,613) |
| Raw distinct sigla → normalised true sources (*2026-06 siglum pass*) | 13,021 → 9,180 (1.4×) |
| Sources cited ≥10× — the working apparatus (*2026-06 siglum pass*) | **2,166** |
| **Resolvability band** (locator-only → established-siglum+locator) | **66.8 % → not yet re-run** (the *2026-06 siglum pass* measured −0.7 pp off the old 59.3 % baseline; that pass predates the H1086 extraction fix and needs re-running against the corrected baseline) |
| Dictionary-to-book gap (bare-abbrev, unresolvable) | ~33 % ≈ 503,600 citations |

Densest `<ls>` citers: PWG 6.50/entry (801,788), BEN 2.84 (49,234), BHS 2.71
(48,419), MW 1.12 (320,828), AP 0.75 (68,273). Big variant merges (*2026-06 siglum pass*): `MBH.`+`MBh.` =
75,548; `ṚV.`+`RV.` = 32,316 — these are already handled by the diacritic/case
`foldSiglum()` layer in
[`scripts/lib/source-siglum.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/source-siglum.mjs).

The remaining engineering is **abbreviation-family merging** — `R.` = `Rām.` =
`Rāmāy.` → Rāmāyaṇa — which the fold cannot catch.
[`scripts/obs/siglum_families.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/obs/siglum_families.py) generates
**review candidates** for this (it does not auto-merge, respecting the curated
[`dict-source-aliases.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dict-source-aliases.json) discipline):
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
are among the densest. (KRM additionally wraps its Sanskrit in `<s>…</s>`, so its
sūtra-citing `iti` sits directly after markup — the reason the earlier
space-or-quote rule missed two-thirds of its citations.)

| Dict | `<ls>` | `iti` citations | iti / entry |
|---|---:|---:|---:|
| KRM | 0 | 12,359 | **6.00** (densest in corpus) |
| SKD | 0 | **80,164** | 1.88 |
| VCP | 0 | **15,619** | 0.31 |
| MCI | 0 | 282 | 0.11 |
| GST | 0 | 166 | 0.02 |
| ARMH | 0 | 69 | 0.01 |

SKD/VCP/KRM cite indigenous authorities (Amara, Trikāṇḍaśeṣa, Śabdaratnāvalī,
Viśva, Medinī, Manu, …) through `iti <source>`; KRM cites Pāṇini's sūtras
(`‘sanāśaṃsabhikṣa uḥ’ (3-2-168) iti uḥ pratyayaḥ`). Their dictionary-to-book
problem is **different in kind** from Register A: linking `iti <work>` to
indigenous source lexica, not resolving a page/verse locator.

## Consequence for the apparatus

CDSL contains **two disjoint citation systems**. The ~67 % resolvability result
and the source-siglum registry apply to **Register A only** — and 27 of the 44
dictionaries carry no `<ls>` at all. Per-dictionary citation density must be
reported per register; the existing `review-source-siglum` normaliser covers
Register A, while Register B needs the indigenous `iti`-source normaliser that
`MICROSTRUCTURE_ZERO_MEANING.md` flagged.

## Reproduction

```sh
# Regenerate the committed artifact (per-dict <ls>/locator/iti counts + density ranks):
python scripts/obs/citation_register_gaps.py   # -> data/obs/citation_registers.json
# Register-A abbreviation-family merge candidates (review worklist):
python scripts/obs/siglum_families.py    # -> data/obs/siglum_family_candidates.csv
```

_Cross-repo provenance: `csl-observatory/reports/obs_rc_atlas_bridge.md`._

_Dr. Mārcis Gasūns_
