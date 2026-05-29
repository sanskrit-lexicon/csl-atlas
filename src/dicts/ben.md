---
title: BEN — Benfey 1866
---

# BEN — Benfey *Sanskrit-English Dictionary* (1866)

*Chapter authored per [Decision 29 Tier B](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#decision-29--phase-4-dictionary-ordering-chapter-templates-minimum-data-added-2026-05-27). Position 5 in the atlas ordering — the **earliest typographic precedent** for the lexicographer-only mark, in a weaker methodological form.*

## 1. Overview

[Theodor Benfey](https://en.wikipedia.org/wiki/Theodor_Benfey)'s *A Sanskrit-English Dictionary, with References to the Best Editions of Sanskrit Authors and Etymologies and Comparisons of Cognate Words, chiefly in Greek, Latin, Gothic, and Anglo-Saxon*, published London 1866 by Longmans, Green, Reader, and Dyer. A compact one-volume work aimed at university-level Sanskritists with comparative-philology training, distinctive for two design choices: (1) a heavy investment in **Indo-European cognate comparisons** (the subtitle's "chiefly in Greek, Latin, Gothic, and Anglo-Saxon") and (2) a **typographic source-discipline** that anticipates the kind of source-marking convention MW would systematise 33 years later. Benfey's record count in the CDSL digitisation is small (5,186) relative to PWG (123,366) or MW (286,561), reflecting the compact print volume rather than incomplete digitisation.

| | |
|---|---|
| **Records** | 5,186 |
| **Volumes** | 1 (single-volume) |
| **Year** | 1866 |
| **Editor** | Theodor Benfey |
| **Publisher** | Longmans, Green, Reader, and Dyer, London |
| **Source language** | Sanskrit |
| **Target language** | English |
| **Genre** | Structured bilingual dictionary (compact, IE-comparative) |
| **`<ls>` citations total** | 14,708 |
| **`<ls>` citations/record** | 2.84 |
| **Typographic markers (preface)** | `*` (fictitious forms) · `†` (no authoritative references) · `§` (compound position) |
| **License** | CC-BY-SA-4.0 |
| **Repo** | [sanskrit-lexicon/BEN](https://github.com/sanskrit-lexicon/BEN) |
| **Source file** | [`csl-orig/v02/ben/ben.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ben/ben.txt) |

## 2. Structural features (Tier B: in place of profile table)

BEN's digitisation **has `<ls>` tagged citation apparatus** (14,708 instances, 2.84/record) — denser than MW (1.09) but a tenth of PWG (4.63). It does *not* have `<lex>` tags, which means the standard primary-type classification cannot run and the entire corpus falls into "other" in [analysis/CROSS_DICT_PROFILES.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/CROSS_DICT_PROFILES.md). This is a *digitisation* artefact (the print volume marks gender inline rather than in a separate field) rather than a print-Benfey design choice.

Block-presence by name (cross-dict-common subset):

```js
const cross = FileAttachment("../data/cross-dict.json").json();
```

```js
const d = cross.dicts.find(d => d.code === "BEN");
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

## 3. Citation strategy

**2.84 `<ls>` per record** — moderately dense. Top 12 sigla ([analysis/LS_HEDGE_CHECK.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md)):

| Tag | Source | Count |
|---|---|--:|
| `<ls>MBh.</ls>` | *Mahābhārata* | 2,508 |
| `<ls>Rām.</ls>` | *Rāmāyaṇa* | 2,297 |
| `<ls>Man.</ls>` | *Manu-smṛti* | 2,159 |
| `<ls>Pañc.</ls>` | *Pañcatantra* | 1,019 |
| `<ls>Chr.</ls>` | *Chrestomathie* (Benfey's own Sanskrit reader) | 860 |
| `<ls>Bhāg. P.</ls>` | *Bhāgavata-purāṇa* | 668 |
| `<ls>Rājat.</ls>` | *Rājataraṅgiṇī* | 384 |
| `<ls>Daśak.</ls>` | *Daśakumāracarita* | 365 |
| `<ls>Śāk.</ls>` | *Abhijñāna-Śākuntalam* | 340 |
| `<ls>Suśr.</ls>` | *Suśrutasaṃhitā* | 322 |
| `<ls>Ragh.</ls>` | *Raghuvaṃśa* | 315 |
| `<ls>Bhartṛ.</ls>` | *Bhartṛhari* | 289 |

**No generic-hedge tag exists**: 0 of 14,708 `<ls>` are a generic `<ls>L.</ls>`-equivalent. Benfey's source apparatus is entirely *named*: every citation points to a specific literary work. The hedge concept — when it does appear — is *typographic* (the dagger `†`), not tagged.

## 3a. Typography & precedent — three markers, three meanings

Benfey's preface (section *"Contractions and Signs"*, pp. ix–xi) explicitly defines three typographic markers. **Per [DOUBTS D22 honesty](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md), they should not be lumped together — only one is a precedent for MW's hedge:**

| Marker | Benfey's definition | Modern analogue | Precedent for MW's `<ls>L.</ls>`? |
|---|---|---|---|
| `*` | "*denotes fictitious forms*" (reconstructed / hypothetical) | Proto-IE asterisk convention (still used today) | **No** — different convention entirely |
| `†` | "*denotes verbs or meanings for which there are no authoritative references*" | MW's `<ls>L.</ls>` (weaker variant) | **Yes** — earliest typographic precedent |
| `§` | "*when before, denotes that the word occurs only as latter part of a compound; when after, as former*" | structural compound-position marker | **No** — orthogonal feature |

The **asterisk `*` is NOT a hedge precedent**. Benfey uses it for *reconstructed* forms — the convention that Proto-IE linguists today still write *\*ph₂tér* "father" — not for under-attested Sanskrit lemmas. The precedent for MW's hedge is **only** Benfey's dagger `†`.

### Where the dagger sits in the three-stage hedge lineage

The dagger is the *earliest* but *weakest* precedent. It marks "no authoritative reference" (a methodological hedge: the editor couldn't find a source) — semantically narrower than Cappeller's `*` 1891 ("taught only by grammarians or lexicographers") or MW's `<ls>L.</ls>` 1899 (specifically *attested in indigenous lexicons*).

| Year | Source | Marker | Semantic content | Scale |
|--:|---|---|---|--:|
| **1866** | **Benfey** | **`†`** | **"no authoritative references" (weaker, methodological)** | **~900 typographic** |
| 1872 | MW 1st edn | declares L. in preface § II | "*only in native lexicons*" | preface-only |
| 1891 | Cappeller | `*` | "*taught only by grammarians or lexicographers*" (semantic equivalent of MW) | 1,370 typographic |
| 1899 | MW 2nd edn | `<ls>L.</ls>` | "*lexicographer-only attestation*" | 40,212 tagged |

The Benfey dagger establishes the *type* of intervention (an inline mark for under-attested entries) 33 years before MW's tagged apparatus. The semantic content matures progressively: methodological caution (1866) → kosha-specific (1891) → integrated source-citation (1899).

## 5. Lineage statement

BEN occupies the **IE-comparative-philology position** in the European-Sanskrit-lexicography lineage. Benfey (1809–1881) was a comparative philologist as much as a Sanskritist; his dictionary is unusual in that ~38 % of root entries carry IE-cognate fields (Greek, Latin, Gothic, Anglo-Saxon, Old High German) — a higher etymological density than PWG, MW, or any other CDSL bilingual dict. BEN draws on the existing literature (Wilson 1832, Bopp, Roth) and on Benfey's own Sanskrit *Chrestomathie* (cited as `<ls>Chr.</ls>` 860×). Its successors are indirect: MW 1899 incorporated some of BEN's IE comparanda but expanded them substantially; Cappeller 1891 acknowledged BEN's typographic discipline without imitating its IE-cognate focus.

## 6. Cross-references — divergence/convergence with adjacent chapters

| Adjacent chapter | Convergence | Divergence |
|---|---|---|
| **← prior: [AP](ap)** | Both compact single-volume modern reference works; both significantly fewer records than MW | BEN is 19th-century philological; AP is 20th-century practical (1957); AP keeps `<lex>` tags, BEN drops them; AP has 1× `<ls>L.</ls>`, BEN has 0 |
| **next →: [CAE](cae)** | Both 19th-century single-volume European works; both use `*` and `†` typographic markers in their prefaces | **The `*` markers mean different things**: Benfey `*` = "fictitious forms" (Proto-IE), CAE `*` = "taught only by grammarians or lexicographers" (semantic equivalent of MW's hedge). Only Benfey's `†` is a precedent for MW's hedge, and it is *semantically weaker* than CAE's `*` (no-authority vs kosha-only). See [PAPER.md Appendix C.2](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#appendix-c--the-hausmann-wiegand-comment-class-reading-condensed) and [D22](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md) honesty |

## 7. Decisions log

- **No conventional profile table (Tier B)** — BEN has no `<lex>` tags, so the standard primary-type classification cannot run; all 5,186 records classify as "other". The structural-features table replaces §2.
- **§3a typography mandatory** per [Decision 29 Tier B](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#292--chapter-template-variants-three-tiers).
- **D22 marker-distinction honesty** explicitly rendered as a 3-row table — Benfey's asterisk is *not* a hedge precedent (it's a Proto-IE-reconstruction marker); only the dagger is.
- **IE-cognate density** is the chapter's distinguishing structural feature (vs other Tier B chapters).
- **[D21 three-stage hedge lineage](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md#d21--cappeller-precedent-narrative-checked-against-mw-1872--partially-resolved-2026-05-27-finding-three-stage-lineage--was-blocking-now-closed)** places Benfey 1866 `†` as the *earliest but weakest* precedent (semantic content is "no authoritative references", not specifically kosha-only).
- **[D19 effect-size threshold](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md)**: numerical claims (~900 dagger instances, 38 % IE-cognate density in roots) exceed |Δ| ≥ 5 pt threshold trivially.

## 8. Data dictionary + reproducibility manifest

- **`DATA_DICTIONARY.md`** — tag inventory (BEN does not have a docs-pass branch as of 2026-05-27; tracked in Phase 4 wave 1 work)
- **Source file**: [`csl-orig/v02/ben/ben.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ben/ben.txt)
- **Block-detector script**: [`figures/scripts/export_data.py`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/scripts/export_data.py)
- **Cross-dict aggregate JSON**: [`src/data/cross-dict.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/interoperability-handoff/src/data/cross-dict.json) (includes BEN block matrix data)
- **License**: [CC-BY-SA-4.0](https://github.com/sanskrit-lexicon/BEN/blob/master/LICENSE)

## See also (tools)

- [Cross-dictionary comparison](../tools/cross-dict)
- [Lineage Sankey](../tools/lineage-sankey)
- [LS_HEDGE_CHECK.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md) — full hedge analysis including the Benfey preface read

---

Source: CDSL `ben.txt` 2026-05-23 · MWS docs-pass commit reflects audit pipeline as of 2026-05-27 · CC-BY-SA-4.0
