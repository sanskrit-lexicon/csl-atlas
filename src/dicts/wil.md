---
title: WIL — Wilson Sanskrit-English Dictionary (1832)
---

# WIL — Wilson *A Dictionary in Sanscrit and English* (1832, 2nd edn)

*Chapter authored per [Decision 29 Tier B](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#decision-29--phase-4-dictionary-ordering-chapter-templates-minimum-data-added-2026-05-27). Position 7 in the atlas ordering — the **base** from which the European Sanskrit-lexicography tradition departs; no systematic hedge convention.*

## 1. Overview

[Horace Hayman Wilson](https://en.wikipedia.org/wiki/Horace_Hayman_Wilson)'s *A Dictionary in Sanscrit and English; translated, amended, and enlarged, from an original compilation prepared by learned natives for the College of Fort William*, 2nd edition Calcutta 1832 (the first dictionary in Devanāgarī printed in India; 1st edn 1819, also Calcutta). The **earliest CDSL dictionary** and the **base** from which the European Sanskrit-lexicography tradition departs. Wilson's compilation rests on an indigenous-Indian word list prepared by Calcutta College *paṇḍits* (chiefly an Amarakośa-derived inventory) which Wilson then translated, annotated, and supplemented with citations from the Roxburgh botanical catalogue. The structural-features story is therefore *inverted* compared to MW: where MW has 18 blocks and a 6-block kernel, WIL has effectively *one* citation source (Roxburgh) and otherwise relies on bare glosses. WIL is what comes *before* the European editorial apparatus is layered on.

| | |
|---|---|
| **Records** | 44,577 |
| **Volumes** | 1 (single-volume) |
| **Year** | 1832 (2nd edn); 1819 (1st edn, also Calcutta) |
| **Editor** | H. H. Wilson (with the Calcutta College *paṇḍits*) |
| **Publisher** | Education Press, Calcutta |
| **Source language** | Sanskrit |
| **Target language** | English |
| **Genre** | Structured bilingual scholarly dictionary (earliest CDSL) |
| **`<ls>` citations total** | **230** (essentially no apparatus) |
| **`<ls>` citations/record** | 0.005 |
| **`<ls>L.</ls>` hedges** | 0 (no systematic convention attested in print or digital record) |
| **License** | CC-BY-SA-4.0 |
| **Repo** | [sanskrit-lexicon/WIL](https://github.com/sanskrit-lexicon/WIL) |
| **Source file** | [`csl-orig/v02/wil/wil.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/wil/wil.txt) |

## 2. Structural features (Tier B: in place of profile table)

WIL has `<lex>` tagged grammar (the gender / part-of-speech apparatus) but essentially **no `<ls>` source citations** — 230 tags total across 44,577 records, of which 224 are `<ls>Rox.</ls>` (Roxburgh's *Hortus Bengalensis* / *Flora Indica* botanical catalogue). The full table of `<ls>` markers ([analysis/LS_HEDGE_CHECK.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md)):

| `<ls>` siglum | Source | Count |
|---|---|--:|
| `<ls>Rox.</ls>` | Roxburgh's botanical catalogue | **224** |
| `<ls>Rox. Catalogue</ls>` | (longer form) | 1 |
| `<ls>Roxburgh's Catalogue</ls>` | (full form) | 1 |
| `<ls>ROXBURGH'S catalogue</ls>` | (caps variant) | 1 |
| `<ls>Rox.'s {%Catalogue%}</ls>` | (italic variant) | 1 |
| `<ls>Rox.'s Cata.</ls>` | (abbrev variant) | 1 |
| `<ls>{%As. R.%} {%Vol.%} viii. p. 442</ls>` | *Asiatic Researches* vol. VIII | 1 |

This is the **base case** of Sanskrit-English lexicography: a dictionary with a defined word list (the Amarakośa-derived Calcutta inventory), translation glosses, and one specialised citation apparatus (Roxburgh for botany). Everything else — the philological scholarly apparatus, the kosha-tradition naming, the lexicographer hedge — is *added* by later editors (Böhtlingk-Roth in PWG, Monier-Williams in MW).

Block-presence by name:

```js
const cross = FileAttachment("../data/cross-dict.json").json();
```

```js
const d = cross.dicts.find(d => d.code === "WIL");
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

## 3. Citation strategy — single-source

WIL's apparatus is **single-source** (Roxburgh). Every entry of botanical character carries `<ls>Rox.</ls>` (or one of the formatting variants above); other entries carry no `<ls>` citation at all. This is *not* a sign of poor scholarship — Wilson's design choice was to publish the Calcutta College's Amarakośa-derived inventory + English glosses as a working reference for Company Bahadur officers and missionaries, not to compete with the European philological tradition. The detailed apparatus came later: PWG (1855–75) is the first European Sanskrit dictionary with a systematic citation discipline.

WIL's type-citation profile is therefore mostly flat at zero. Where the citation rate is non-zero (botanical entries), it is 100 % `<ls>Rox.</ls>` — a single-source apparatus on a sub-population.

## 3a. Typography & precedent — *no* systematic hedge convention

Per the 2026-05-27 print-preface and digital-record read ([analysis/LS_HEDGE_CHECK.md "Wilson 1832"](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md)):

- The Wilson 1832 print preface (OCR-fetched in part) shows **no systematic convention** marking words attested only in indigenous lexicons. The Calcutta College compilation Wilson worked from *is* an Amarakośa-derived inventory; the distinction Wilson cared about was "the inventory" vs "additional Wilson material", not "kosha-only vs literary-attested".
- The digital record carries 0 `<ls>L.</ls>` hedges and 0 typographic asterisks / daggers in the tagged data.
- The closest thing to a hedge in WIL is the *implicit* fact that any entry without a citation is implicitly lexicographer-attested — but the dictionary does not mark this; the reader must infer it.

**WIL is therefore *not* part of the three-stage hedge lineage** (Benfey 1866 † → MW 1872 preface → Cappeller 1891 `*` → MW 1899 `<ls>L.</ls>`). WIL belongs to the *pre-hedge* tradition of Sanskrit lexicography — the base before the European typographic apparatus was added.

## 5. Lineage statement

WIL occupies the **base position** in the European-Sanskrit-lexicography lineage. It is the *first* English-Sanskrit dictionary printed in India and the *earliest* CDSL dictionary. Its word list comes from the Calcutta College's indigenous-*paṇḍit* compilation (essentially Amarakośa + Hemacandra material, the same indigenous-kosha tradition that PWG would later cite by name and MW would later compress into `<ls>L.</ls>`). The European Sanskrit-lexicography lineage that comes after — PWG 1855–75, PWK 1879–89, Benfey 1866, Cappeller 1891, MW 1872/1899, Apte 1890/1957 — *all* draw on Wilson directly (PWG cites `<ls>WILS.</ls>` 2,014×; MW cites `<ls>W.</ls>` 8,285×) and *all* add layers of apparatus that Wilson did not.

Full lineage in [WIL/DICT_PROFILE.md](https://github.com/sanskrit-lexicon/WIL/blob/docs-pass/DICT_PROFILE.md).

## 6. Cross-references — divergence/convergence with adjacent chapters

| Adjacent chapter | Convergence | Divergence |
|---|---|---|
| **← prior: [CAE](cae)** | Both single-volume; both have effectively zero `<ls>` tagged apparatus | CAE has 1,370-instance systematic typographic hedge (`*` for lexicographer-only); WIL has no systematic hedge convention at all. CAE is the *systematic-precedent* node (1891), WIL is the *base* node (1832); 59 years and an entire methodology separate them |
| **next →: [SKD](skd)** | Both 1820–30s compilations rooted in indigenous-Indian scholarship (WIL from Calcutta College, SKD from Bengal Sanskrit scholarship) | WIL is bilingual (Sanskrit → English); SKD is monolingual Sanskrit-Sanskrit (the *kośa* tradition itself, not a European reading of it); WIL is structured-bilingual genre, SKD is genre-bound `iti`-citation. The genre boundary in the atlas falls here: WIL is the last structured bilingual chapter, SKD is the first genre-bound chapter |

## 7. Decisions log

- **Tier B template** per Decision 29 (compact + typography slot optional). Since WIL has *no* systematic hedge convention, §3a is reduced to the negative finding (no marker found in print preface or digital record).
- **Single-source apparatus narrative** is the chapter's structural centre: Roxburgh-botany only, 224 of 230 `<ls>` tags.
- **No participation in the three-stage hedge lineage** — explicit per [D21 resolution](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md). WIL's word list *is* the kosha tradition; WIL just doesn't *mark* it as such.
- **Effect-size threshold** ([D19](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md)): numerical claims (224 of 230, 100 % botanical-`<ls>` rate) exceed the threshold trivially.

## 8. Data dictionary + reproducibility manifest

- **[`DATA_DICTIONARY.md`](https://github.com/sanskrit-lexicon/WIL/blob/docs-pass/DATA_DICTIONARY.md)** — full tag inventory
- **Source file**: [`csl-orig/v02/wil/wil.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/wil/wil.txt)
- **Block-detector script**: [`figures/scripts/export_data.py`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/scripts/export_data.py)
- **Per-dict matrix JSON**: [`data/wil_blocks.json`](../data/wil_blocks.json)
- **Cross-dict aggregate**: [`data/cross-dict.json`](../data/cross-dict.json)
- **License**: [CC-BY-SA-4.0](https://github.com/sanskrit-lexicon/WIL/blob/master/LICENSE)

## See also (tools)

- [Cross-dictionary comparison](../tools/cross-dict)
- [Lineage Sankey](../tools/lineage-sankey) — WIL as the base from which the European tradition departs
- [WIL#18 — docs-pass tracking issue](https://github.com/sanskrit-lexicon/WIL/issues/18)

---

Source: CDSL `wil.txt` 2026-05-23 · MWS docs-pass commit reflects audit pipeline as of 2026-05-27 · CC-BY-SA-4.0
