---
title: CAE — Cappeller 1891
---

# CAE — Cappeller *Sanskrit-English Dictionary* (1891)

*Chapter authored per [Decision 29 Tier B](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#decision-29--phase-4-dictionary-ordering-chapter-templates-minimum-data-added-2026-05-27). Position 6 in the atlas ordering — the **first systematic typographic implementation** of the lexicographer-only hedge that MW 1899 would scale and tag.*

## 1. Overview

[Carl Cappeller](https://en.wikipedia.org/wiki/Carl_Cappeller)'s *A Sanskrit-English Dictionary, Based Upon the St. Petersburg Lexicons*, published Strassburg 1891 by Karl J. Trübner. A single-volume reduction of PWG + PWK aimed at English-reading Sanskritists, intended as a practical reference rather than a research instrument. **Cappeller went on to co-edit MW 1899** (with Ernst Leumann), making the lineage from CAE 1891's typographic asterisk to MW 1899's tagged `<ls>L.</ls>` direct rather than merely parallel. CAE's record count (40,069) is close to a tenth of MW's (286,561) — it is deliberately compact, omitting most of MW's encyclopedic apparatus and all of PWG's named-kosha citations.

| | |
|---|---|
| **Records** | 40,069 |
| **Volumes** | 1 (single-volume) |
| **Year** | 1891 |
| **Editor** | Carl Cappeller (later MW 1899 co-editor) |
| **Publisher** | Karl J. Trübner, Strassburg |
| **Source language** | Sanskrit (Devanāgarī in print) |
| **Target language** | English |
| **Genre** | Structured bilingual dictionary (compact) |
| **`<ls>` citations total** | **0** (no tagged source apparatus) |
| **Typographic markers** | `*` 1,370× · `†` 903× · `†...†` (combination) |
| **License** | CC-BY-SA-4.0 |
| **Repo** | [sanskrit-lexicon/CAE](https://github.com/sanskrit-lexicon/CAE) |
| **Source file** | [`csl-orig/v02/cae/cae.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/cae/cae.txt) |
| **CDSL display** | [sanskrit-lexicon.uni-koeln.de/scans/CAEScan/2014](https://www.sanskrit-lexicon.uni-koeln.de/scans/CAEScan/2014/web/index.php) |

## 2. Structural features (Tier B: in place of profile table)

CAE's digitisation carries **no `<ls>` tags at all** — Cappeller's source apparatus is exclusively typographic. The conventional 18-block profile is therefore degenerate (the citation column is empty). The structural features that *are* present:

| Feature | Population |
|---|--:|
| Headwords (Devanāgarī) | 40,069 |
| `<lex>` grammatical tags (noun_m/f/n, adj-mfn, ind.) | partial (gender often inline in prose) |
| Asterisk `*` (lexicographer-only marker) | 1,370 (≈ 3.4 % of entries) |
| Dagger `†` (Prakrit-translation-only) | 903 (≈ 2.3 %) |
| `<ls>` tagged source citations | **0** |
| Inline literary citations (prose, not tagged) | many (cited as e.g. "*Mbh.*", "*R.*" in glosses) |

Block-presence by name (cross-dict-common subset):

```js
const cross = FileAttachment("../data/cross-dict.json").json();
```

```js
const d = cross.dicts.find(d => d.code === "CAE");
const LABEL = {head:"head",body:"body (¦)",gram:"gram (lex)",cite:"cite (ls)",hom:"homograph",etym:"etymology",xref:"cross-ref",hedge:"L. hedge",info:"info (digit.)"};
const bars = cross.blocks.map(b => ({block: LABEL[b] ?? b, pct: d.blocks_pct[b]}));
display(Plot.plot({
  width: 580, height: 240, marginLeft: 90,
  x: {label: "% of entries", domain: [0, 100], grid: true},
  y: {label: null},
  marks: [
    Plot.barX(bars, {y: "block", x: "pct", fill: "#1f78b4"}),
    Plot.text(bars, {y: "block", x: "pct",
      text: d => d.pct >= 0.5 ? d.pct.toFixed(1)+"%" : "",
      dx: 4, textAnchor: "start", fontSize: 10}),
    Plot.ruleX([0])
  ]
}));
```

## 3. Citation strategy (or lack of tagged apparatus)

CAE's digitisation carries **zero `<ls>` tags** — the Cologne workflow chose not to extract Cappeller's typographic markers as `<ls>` citations because they are not source citations in the named-work sense. The result: the cross-dict comparison sees CAE as a "no apparatus" dictionary, but the print volume *does* carry an active source-discipline — it is simply typographic rather than tagged. The two markers, from Cappeller's own preface (verbatim, [analysis/LS_HEDGE_CHECK.md §"Print-preface read"](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md#print-preface-read-added-2026-05-27-closes-the-digital-only-gap)):

> *"`*` denotes a word taught only by grammarians or lexicographers."*
> *"`†` denotes a word which occurs only in a translation from Prakrit."*
> (*"`†...†`"* combines both.)

And the principle: *"On the whole, it offers only authenticated matter, i.e. such words…as are actually found in the works of Sanskrit writers."*

## 3a. Typography & precedent — the asterisk as systematic lexicographer hedge

This is the **central CAE finding** and the reason CAE sits at position 6 in the Decision 29 ordering.

Cappeller's `*` is **semantically the exact analogue** of MW 1899's `<ls>L.</ls>`: both mark words attested *only* in indigenous Sanskrit lexicons (Amarakośa, Hemacandra, Medinīkośa, Halāyudha, etc.) and *not* in literary works. The lineage is direct in three senses:

1. **Cappeller co-edited MW 1899** (with Leumann), so the convention travelled with the editor from Strassburg to Oxford.
2. **The 8-year gap** (1891 → 1899) is short enough that the typographic-to-tagged transition happens in one editorial career.
3. **The semantic content is identical** — the asterisk means in CAE 1891 what `<ls>L.</ls>` means in MW 1899.

### Three-stage hedge lineage (per [DOUBTS D21 resolution](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md#d21--cappeller-precedent-narrative-checked-against-mw-1872--partially-resolved-2026-05-27-finding-three-stage-lineage--was-blocking-now-closed))

| Year | Source | Marker | Implementation |
|--:|---|---|---|
| 1866 | Benfey | `†` "no authoritative references" (weaker, methodological) | ~900 typographic |
| 1872 | MW 1st edn | declares L. in preface § II | preface-only; ≈ 0 body |
| **1891** | **Cappeller** | **`*` "taught only by grammarians or lexicographers"** | **1,370 typographic — first systematic** |
| 1899 | MW 2nd edn (w/ Cappeller as co-editor) | `<ls>L.</ls>` | 40,212 tagged + scaled |

CAE 1891 is the **systematic-typographic** node — the first dictionary in the European-Sanskrit lineage to apply the lexicographer-only mark at a scale that makes it a structural feature of every reading rather than an occasional editorial aside. Without CAE, MW 1899's 40,212-instance apparatus would have no methodological precedent; without MW 1899, CAE's asterisk would be a curiosity rather than a tool.

### Note on the dagger `†`

Cappeller's dagger marks a *different* phenomenon (Prakrit-translation-only attestation) and has no MW-1899 successor — MW does not have a Prakrit-attestation tag. The dagger belongs to the same general typographic family as the asterisk but is a content-specific marker, not a generalisable hedge.

## 5. Lineage statement

CAE occupies the **typographic-precedent position** in the European-Sanskrit-lexicography lineage. It draws on [PWG 1855–75](pwg) and [PWK 1879–89](pwk) for its lexical material (the subtitle is explicit: "Based Upon the St. Petersburg Lexicons") and on MW 1872 for the *concept* of the lexicographer-only mark (which MW had declared in his preface but not systematically implemented). It synthesises both into a single-volume work that, for the first time, applies the mark at scale. Its direct successor is **[MW 1899](mw)** — which preserves the convention but promotes it from typographic `*` to tagged `<ls>L.</ls>`, increasing scale ~30-fold and integrating it with the named-source citation apparatus.

Full lineage in [CAE/DATA_DICTIONARY.md](https://github.com/sanskrit-lexicon/CAE/blob/master/DATA_DICTIONARY.md) (note: as of 2026-05-27 the CAE DATA_DICTIONARY does *not* document the asterisk/dagger conventions; this is a tracked editorial gap, [LS_HEDGE_CHECK.md §"Print-preface read"](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md)).

## 6. Cross-references — divergence/convergence with adjacent chapters

| Adjacent chapter | Convergence | Divergence |
|---|---|---|
| **← prior: [BEN](ben)** | Both 19th-century single-volume European works; both rely on typographic (not tagged) markers; both have `*` and `†` glyphs in their preface inventories | Benfey's `*` means *fictitious forms* (Proto-IE reconstruction, NOT a hedge precedent); Benfey's `†` means *no authoritative references* (weaker hedge); CAE's `*` is the *semantic equivalent* of MW's `<ls>L.</ls>` (the actual precedent). See [PAPER.md Appendix C.2](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#appendix-c--the-hausmann-wiegand-comment-class-reading-condensed) per D22 honesty |
| **next →: [WIL](wil)** | Both single-volume; both have effectively zero `<ls>` tagged apparatus | WIL has no systematic hedge convention in print or digital record; CAE has 1,370-instance systematic typographic hedge. WIL is the *base* of the European tradition (1832); CAE is the *systematic-precedent* node (1891) |

## 7. Decisions log

- **No conventional profile table (Tier B)** — CAE has 0 `<ls>` tags, so the cite-rate column would be all-zero. Replaced §2 with a "structural features" table.
- **§3a typography section is mandatory** per [Decision 29 Tier B](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#292--chapter-template-variants-three-tiers); the precedent finding from [D21](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md) is the chapter's centre.
- **Three-stage lineage rendered** per [D21 resolution](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md#d21--cappeller-precedent-narrative-checked-against-mw-1872--partially-resolved-2026-05-27-finding-three-stage-lineage--was-blocking-now-closed).
- **CAE dagger explicitly distinguished from MW's hedge** — the dagger marks Prakrit-translation-only attestation, not lexicographer-only; it has no MW successor.
- **CAE's missing DATA_DICTIONARY documentation** of the asterisk/dagger is named as an editorial gap and a future issue.
- **[D19 effect-size threshold](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md)**: numerical claims (1,370 asterisks, 903 daggers, 0 `<ls>` tags) are large effects.

## 8. Data dictionary + reproducibility manifest

- **[`DATA_DICTIONARY.md`](https://github.com/sanskrit-lexicon/CAE/blob/master/DATA_DICTIONARY.md)** — full tag inventory (note: asterisk/dagger conventions are not yet documented; tracked as editorial gap)
- **Source file**: [`csl-orig/v02/cae/cae.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/cae/cae.txt)
- **Block-detector script**: [`figures/scripts/export_data.py`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/scripts/export_data.py)
- **Cross-dict aggregate JSON**: [`src/data/cross-dict.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/interoperability-handoff/src/data/cross-dict.json) (includes CAE block matrix data)
- **License**: [CC-BY-SA-4.0](https://github.com/sanskrit-lexicon/CAE/blob/master/LICENSE)

## See also (tools)

- [Cross-dictionary comparison](../tools/cross-dict) — CAE alongside all 8 other CDSL dicts
- [Lineage Sankey](../tools/lineage-sankey) — Cappeller's typographic asterisk → MW's tagged hedge
- [LS_HEDGE_CHECK.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md) — full hedge analysis including the Cappeller preface read

---

Source: CDSL `cae.txt` 2026-05-23 · MWS docs-pass commit reflects audit pipeline as of 2026-05-27 · CC-BY-SA-4.0
