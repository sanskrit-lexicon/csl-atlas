---
title: PWK — Böhtlingk Kürzeres PW (1879–1889)
---

# PWK — Sanskrit-Wörterbuch in kürzerer Fassung (1879–1889)

*Chapter authored per [Decision 29 Tier A](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#decision-29--phase-4-dictionary-ordering-chapter-templates-minimum-data-added-2026-05-27). Position 3 in the atlas ordering — the **missing link** between PWG's kosha-rich apparatus and MW's hedge-collapsed apparatus.*

## 1. Overview

[Otto von Böhtlingk](https://en.wikipedia.org/wiki/Otto_von_B%C3%B6htlingk)'s own one-volume abridgement of PWG, published St. Petersburg 1879–1889 in seven slim *Lieferungen*. Where PWG (1855–1875) ran to seven folio volumes and 570,817 source citations, PWK condenses the same lexical material into a single volume by **dropping nearly all of PWG's indigenous-kosha apparatus**: the top PWG sigla `ŚKDR.` (20,109×), `MED.` (7,176×), and `H. an.` (6,619×) all collapse to zero in PWK. The result is a dictionary with *more headwords than PWG* (170,556 vs 123,366 — Böhtlingk added new material in 14 years of intervening scholarship) but *fewer citations per headword* (0.51 vs PWG's 4.63 — an order-of-magnitude reduction). PWK is therefore the **missing link** in the European-Sanskrit-lexicography lineage: the editorial moves that MW 1899 would complete (collapse named-kosha sigla, compact into a single volume) are first attempted by PWG's own editor, here.

| | |
|---|---|
| **Records** | 170,556 |
| **Volumes** | 1 (single-volume) |
| **Year** | 1879–1889 |
| **Editor** | Otto von Böhtlingk (without Roth) |
| **Publisher** | Kaiserliche Akademie der Wissenschaften, St Petersburg |
| **Source language** | Sanskrit |
| **Target language** | German |
| **Genre** | Structured bilingual scholarly dictionary (single-volume reduction) |
| **`<ls>` citations total** | 86,750 |
| **`<ls>` citations/record** | 0.51 (vs PWG 4.63 — 9× sparser) |
| **`<ls>L.</ls>` hedges** | 0 (but typographic `*` prefix used as hedge — see §3) |
| **License** | CC-BY-SA-4.0 |
| **Repo** | [sanskrit-lexicon/PWK](https://github.com/sanskrit-lexicon/PWK) |
| **Source file** | [`csl-orig/v02/pwk/pwk.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwk/pwk.txt) |

## 2. Profile table (5 primary types × profile)

Per [PAPER.md §5](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#5-profiles-as-the-unit-of-typology), restricted to the types PWK's data supports:

| Primary type | Count | % corpus | cite% | etym% | Mean common-blocks |
|---|--:|--:|--:|--:|--:|
| Nominal — noun_m | 47,304 | 27.7 % | 37.6 % | 0.0 % | 3.38 |
| Nominal — noun_f | 18,882 | 11.1 % | **42.1 %** | 0.1 % | 3.42 |
| Nominal — noun_n | 20,995 | 12.3 % | **41.7 %** | 0.4 % | 3.42 |
| Adjective | 46,265 | 27.1 % | **45.2 %** | 0.1 % | 3.45 |
| Indeclinable | 87 | 0.05 % | 21.8 % | 0.0 % | 3.22 |
| Other | 37,023 | 21.7 % | 22.7 % | 11.2 % | 2.10 |

**Citation profile spread: 7.7 pts** — between PWG's 0.4 (uniform) and MW's 11.3 (most selective). PWK is the **single-volume midpoint** of the type-citation differentiation effect: dropping from PWG's near-uniform 98 % citation rate to ~40 % across most types, with adjectives slightly favoured (45.2 %) and noun-m slightly disfavoured (37.6 %).

Block-presence by name (cross-dict-common subset):

```js
const cross = FileAttachment("../data/cross-dict.json").json();
```

```js
const d = cross.dicts.find(d => d.code === "PWK");
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

## 3. Citation density and apparatus

**0.51 `<ls>` per record** — sparser than MW (1.09) and 9× sparser than PWG (4.63). Top 12 sigla ([analysis/LS_HEDGE_CHECK.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md)):

| Tag | Source | Count |
|---|---|--:|
| `<ls>GAL.</ls>` | Galanos's Greek Sanskrit dictionary | 1,736 |
| `<ls>OPP. CAT. 1</ls>` | Oppert *Catalogus catalogorum* | 1,727 |
| `<ls>BURNELL, T.</ls>` | Burnell's Tanjore catalogue | 971 |
| `<ls>ĀPAST.</ls>` | *Āpastamba-sūtra* | 622 |
| `<ls>NIGH. PR.</ls>` | *Nighaṇṭu-prākṛti* | 577 |
| `<ls>GAUT.</ls>` | *Gautama-sūtra* | 539 |
| `<ls>ĀRṢ. BR.</ls>` | *Ārṣa-Brāhmaṇa* | 418 |
| `<ls>ebend.</ls>` | *ebendaselbst* ("ibidem", editorial back-reference) | 387 |
| `<ls>VAITĀN.</ls>` | *Vaitāna-sūtra* | 375 |
| `<ls>NĪLAK.</ls>` | Nīlakaṇṭha (commentator) | 291 |
| `<ls>ṚV.</ls>` | *Ṛgveda* | 288 |
| `<ls>PAÑCAD.</ls>` | *Pañcadaṇḍacchattraprabandha* | 282 |

**Compare to PWG's top 12**: PWK's top sigla are *completely different* from PWG's. PWG's top three were all indigenous Sanskrit lexicons (ŚKDR, MED, H. an.); PWK's top three are an indological catalogue (GAL.), a manuscript catalogue (OPP. CAT. 1), and a Tanjore manuscript inventory (BURNELL, T.) — **none indigenous-kosha**. Böhtlingk's editorial choice for PWK was to **drop the named-kosha apparatus** in favour of textual and cataloguing references that had emerged in the 14 years between PWG vol. 7 and PWK vol. 1.

This is the central PWK finding: **PWK already collapsed PWG's indigenous-lexicon apparatus before MW did** ([Phase 3.10 finding](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/HANDOFF.md)). MW's `<ls>L.</ls>` is not the first compression — it is a *re-introduction* of a compressed indigenous-lexicon marker that PWK had effectively eliminated.

| Top kosha siglum | PWG | PWK | MW |
|---|--:|--:|--:|
| `<ls>ŚKDR.</ls>` *(Śabdakalpadruma)* | 20,109 | 0 | 0 |
| `<ls>MED.</ls>` *(Medinīkośa)* | 7,176 | 0 | 0 |
| `<ls>H. an.</ls>` *(Hemacandra)* | 6,619 | 0 | 0 |
| `<ls>L.</ls>` *(generic lexicographer hedge)* | 0 | 0 | **40,212** |

The arc: PWG kept the named-kosha apparatus (high cost, high fidelity); PWK dropped it (the editor's own retraction); MW re-introduced an *aggregate marker* that says "the evidence is kosha but I don't say which" (a third compromise).

## 4. Hedge analysis — PWK uses typographic `*` prefix

PWK has 0 tagged `<ls>L.</ls>` instances but does use a typographic asterisk `*` as an entry-initial mark (the digitisation preserves these inline in the headword field, not as tagged `<ls>`). The asterisk semantics in PWK is *not the same* as Cappeller's 1891 asterisk: PWK uses `*` to mark **words that occur only in lexicons or grammarians** — the same general meaning — but applied less systematically than Cappeller and **never tagged**. PWK therefore sits *between* the typographic discipline of CAE 1891 and the no-hedge discipline of PWG: it has the *concept* of a hedge but neither systematic typographic application nor any tagged implementation.

## 5. Lineage statement

PWK occupies the **abridgement node** in the European-Sanskrit-lexicography lineage. It is **derivative-by-design**: Böhtlingk's stated intention was to produce a single-volume working reference for scholars who could not afford or carry the seven-volume PWG. The abridgement strategy — keep PWG's lemma set, drop most of PWG's citation apparatus, expand selectively where new scholarship demanded — is what MW 1899 would later adopt for English-language users. PWK predates MW 1899 by 10–20 years and demonstrates that the *editorial moves* MW would make were already on Böhtlingk's mind a decade earlier.

Full lineage in [PWK/DICT_PROFILE.md](https://github.com/sanskrit-lexicon/PWK/blob/docs-pass/DICT_PROFILE.md).

## 6. Cross-references — divergence/convergence with adjacent chapters

| Adjacent chapter | Convergence | Divergence |
|---|---|---|
| **← prior: [BEN](ben)** | Both 19th-century works contemporary with PWG | BEN is small (5,186 records), IE-comparative, single-author English; PWK is large (170,556), single-author German, abridgement-by-design; BEN has 14,708 tagged `<ls>` (no hedge), PWK has 86,750 tagged `<ls>` (no hedge but typographic `*`) |
| **next →: [AP](ap)** | Both single-volume; both have moderate `<ls>` density (PWK 0.51, AP 0.69) | AP is 20th-century English practical (1957); PWK is 19th-century German scholarly (1879–89); AP has 1× `<ls>L.</ls>`, PWK has 0 (typographic `*` only); AP type-citation spread 15.2 vs PWK 7.7 (AP more selective) |

## 7. Decisions log

- **5-type profile** (not 8+1) per same reason as PWG: PWK lacks `<info>`, `<bot>`, `<bio>`, `<lang>` so encyclopedic / IE / verbal-lemma primary types from MW's [refactored typology](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#5-profiles-as-the-unit-of-typology) cannot be detected.
- **No `<ls>L.</ls>` but typographic `*` exists** — PWK uses asterisk *less systematically* than Cappeller (CAE); the digitisation preserves these in the headword field, not as tagged `<ls>`.
- **The "missing link" finding** is the chapter's central narrative: PWK drops PWG's kosha apparatus *before* MW; MW's `<ls>L.</ls>` is a re-introduction in compressed form.
- **Effect-size threshold** ([D19](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md)): all numerical claims on this page exceed |Δ| ≥ 5 pt threshold.

## 8. Data dictionary + reproducibility manifest

- **[`DATA_DICTIONARY.md`](https://github.com/sanskrit-lexicon/PWK/blob/docs-pass/DATA_DICTIONARY.md)** — full tag inventory
- **Source file**: [`csl-orig/v02/pwk/pwk.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwk/pwk.txt)
- **Block-detector script**: [`figures/scripts/export_data.py`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/scripts/export_data.py)
- **Per-dict matrix JSON**: [`data/pwk_blocks.json`](../data/pwk_blocks.json) (note: `csl_code='pw'` but filename is `pwk_blocks.json` — Round 1 S6 bug fix)
- **Cross-dict aggregate**: [`data/cross-dict.json`](../data/cross-dict.json)
- **License**: [CC-BY-SA-4.0](https://github.com/sanskrit-lexicon/PWK/blob/master/LICENSE)

## See also (tools)

- [Cross-dictionary comparison](../tools/cross-dict)
- [Lineage Sankey](../tools/lineage-sankey) — PWG → PWK → MW kosha-collapse arc
- [PWK#115 — docs-pass tracking issue](https://github.com/sanskrit-lexicon/PWK/issues/115)

---

Source: CDSL `pwk.txt` 2026-05-23 · MWS docs-pass commit reflects audit pipeline as of 2026-05-27 · CC-BY-SA-4.0
