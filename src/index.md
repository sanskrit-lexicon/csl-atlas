---
title: csl-atlas
toc: false
---

# Atlas of the Cologne Digital Sanskrit Lexicons

A comparative microstructural atlas of **nine** Sanskrit dictionaries spanning the indigenous *kośa* tradition (~6th c.) through to the [Cologne Digital Sanskrit Lexicon](https://www.sanskrit-lexicon.uni-koeln.de/) (2024). Each chapter analyses one dictionary under an [18-block formal apparatus](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#3-the-five-grounded-constructs) developed for MW; the atlas reveals where the apparatus generalises, where it stops, and what the three-stage lineage of the `<ls>L.</ls>` lexicographer hedge looks like.

<!-- Русская версия → /ru/ — re-enable once the RU locale routes are wired (see I18N.md / DOUBTS D11). -->

---

## How to read this atlas

Chapters are ordered to mirror the [paper's argument arc](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md) per [Decision 29](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#decision-29--phase-4-dictionary-ordering-chapter-templates-minimum-data-added-2026-05-27):

1. **Framework-fit first** — chapters 1–4 (MW, PWG, PWK, AP): structured bilingual dictionaries that exercise the full 18-block apparatus. Read these to learn how the framework works.
2. **Typographic precedents** — chapters 5–6 (BEN, CAE): 19th-century single-volume works whose typographic markers (`†`, `*`) are the historical precedents for MW's tagged `<ls>L.</ls>` hedge. Read these to learn where the hedge came from.
3. **The base** — chapter 7 (WIL): the earliest CDSL dict (1832), Wilson's Amarakośa-derived word list with effectively no source apparatus. Read this to see where the European tradition begins.
4. **The genre limit** — chapters 8–9 (SKD, VCP): Sanskrit-Sanskrit *kośa* works where the 18-block apparatus stops applying (no `<lex>`/`<ls>` tags, inline `iti` citation instead). Read these to learn where the framework ends.

The arc — framework-fit → precedent → base → genre-limit — is the same arc as [PAPER.md §§3–8](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md). A reader following the 9 chapters in order learns the framework, then learns its history, then learns its limits.

---

## Start here

<div class="card-grid">

### Read the paper

One consolidated study of Monier-Williams 1899 — a data-grounded body, triangulated against three external frameworks:

- **[Grounded framework (body)](/paper/grounded)** — five constructs built from MW outward (block, slot, profile, hedge, infrastructure) + the block-economy thesis
- **[Triangulation (§7)](/paper/triangulation)** — how Wiegand, Atkins–Rundell and Hausmann converge as three witnesses to one analysis
- **[Framework appendices A·B·C](/paper/appendices)** — the condensed Wiegand / Atkins–Rundell / Hausmann readings (incl. the proposed *Provenienz-Komment*)

### Explore the tools

- **[Cross-dictionary comparison](/tools/cross-dict)** — nine dicts: citation density + common-block population
- **[Matrix explorer](/tools/matrix-explorer)** — 18 formal blocks × primary article types
- **[Lineage Sankey](/tools/lineage-sankey)** — PWG → PWK → MW kosha-citation collapse
- **[Typology treemap](/tools/typology-treemap)** — 286,561 MW entries by article type
- **[Lexicographic timeline](/tools/timeline)** — 6th c. — 2024
- **[Type comparator](/tools/type-comparator)** — pick two types, see block differences
- **[Citation tracer](/tools/citation-tracer)** — click a source, see all entries

### Browse the 9 dictionaries (Decision 29 order)

| # | Code | Year | Tier | One-line summary |
|--:|---|---|---|---|
| 1 | **[MW](/dicts/mw)** | 1899 | A | Standard single-volume Sanskrit-English reference; 286,561 records; framework's home dictionary |
| 2 | **[PWG](/dicts/pwg)** | 1855–75 | A | 7-volume Sanskrit-German *Grosses PW*; densest `<ls>` apparatus (4.63/record); 0 hedges |
| 3 | **[PWK](/dicts/pwk)** | 1879–89 | A | Böhtlingk's own one-volume abridgement; dropped PWG's kosha apparatus *before* MW |
| 4 | **[AP](/dicts/ap)** | 1890 / 1957 | A | Apte's *Practical Sanskrit-English Dictionary*; only post-MW dict with any `<ls>L.</ls>` (1×) |
| 5 | **[BEN](/dicts/ben)** | 1866 | B | Benfey 1866; earliest typographic hedge precedent (`†` = "no authoritative references") |
| 6 | **[CAE](/dicts/cae)** | 1891 | B | Cappeller 1891; **first systematic typographic precedent** (`*` for kosha-only); MW 1899 co-editor |
| 7 | **[WIL](/dicts/wil)** | 1832 | B | Wilson 1832; earliest CDSL dict; the base from which the European tradition departs |
| 8 | **[SKD](/dicts/skd)** | 1822–58 | C | *Śabdakalpadruma*; first Sanskrit-Sanskrit *kośa*; **the genre boundary** — framework stops here |
| 9 | **[VCP](/dicts/vcp)** | 1873–84 | C | *Vācaspatyam*; final chapter; confirms genre limit; atlas closes here |

Tier A = full template (8 sections); Tier B = compact + typography section; Tier C = genre-bound, prose-pattern analysis. Audit report: [`_consistency_audit.md`](/dicts/_consistency_audit).

**Kośa-resolution repos** (sources MW's `<ls>L.</ls>` hedge points back to, *not* atlas chapters): [ARMH](https://github.com/sanskrit-lexicon/armh) (Halāyudha) · [ABCH](https://github.com/sanskrit-lexicon/abch) (Hemacandra) · [ACPH](https://github.com/sanskrit-lexicon/acph) · [ACSJ](https://github.com/sanskrit-lexicon/acsj). A future Phase-5 project would extend the framework to these.

</div>

---

## The central finding — three-stage `<ls>L.</ls>` lineage

The single most striking pattern in the atlas is the **three-stage lineage** of MW's lexicographer-only hedge (per the [2026-05-27 MW 1872 preface read](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md#mw-1872-preface-and-body-check-added-2026-05-27-d21-resolution)):

| Year | Source | Marker | Meaning | Scale |
|--:|---|---|---|--:|
| 1866 | **[Benfey](/dicts/ben)** | `†` | "no authoritative references" (weaker, methodological) | ~900 typographic |
| 1872 | **MW 1st edn** | declares L. in preface § II | "*only in native lexicons*" | preface-only; ≈ 0 in body |
| 1891 | **[Cappeller](/dicts/cae)** | `*` | "*taught only by grammarians or lexicographers*" | **1,370 typographic — first systematic** |
| 1899 | **[MW 2nd edn](/dicts/mw)** (w/ Cappeller as co-editor) | `<ls>L.</ls>` | "*lexicographer-only attestation*" | **40,212 tagged + scaled** |

None of the four stages is fully derivative of the others. MW 1872 is first with the *concept* (declared in MW's own preface, in his own words); Cappeller 1891 is first with the *systematic typographic implementation*; MW 1899 is first with the *tagged + scaled* implementation. [PWG](/dicts/pwg), the other major 19th-century dictionary, sits *outside* this lineage — it kept the named-kosha apparatus (top 5 sigla all named indigenous Sanskrit lexicons: `<ls>ŚKDR.</ls>`, `<ls>MED.</ls>`, `<ls>H. an.</ls>`, etc.) and never used a hedge.

The [Lineage Sankey](/tools/lineage-sankey) visualises this collapse — MW's 40,212 hedges *summarise* what PWG distributed across 821 named-kosha sigla.

---

## Companion documents on GitHub

- [PAPER.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md) — the full IJL paper draft (~8,700 words; [submission-v1 tag](https://github.com/sanskrit-lexicon/MWS/releases/tag/submission-v1))
- [IJL_COVER_LETTER.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/IJL_COVER_LETTER.md) — submission cover letter
- [PAPER_RU.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER_RU.md) — Russian companion paper (Vostok·Oriens target)
- [DICT_PROFILE.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/DICT_PROFILE.md) — narrative profile of MW1899
- [ENTRY_GUIDE.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/ENTRY_GUIDE.md) — how to read an MW entry
- [MICROANALYSIS.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/MICROANALYSIS.md) — block-level working notes
- [DOUBTS.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/DOUBTS.md) — 22 doubts, of which D2/D5/D17/D18/D19/D20/D21/D22 closed
- [Decision 29 — atlas chapter ordering](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/decisions/MICROSITE.md#decision-29--phase-4-dictionary-ordering-chapter-templates-minimum-data-added-2026-05-27) — the order this atlas is built in

---

<div class="footer-attribution">
Source: CDSL · CC-BY-SA-4.0 · build {sha}
</div>
