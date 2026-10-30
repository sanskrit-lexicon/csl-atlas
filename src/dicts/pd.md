_Created: 24-10-2026 · Last updated: 31-10-2026_

---
title: PD — Poona Dictionary / EDSHP (1948–, unfinished)
---

# PD — *An Encyclopaedic Dictionary of Sanskrit on Historical Principles* (1948–)

*The atlas's first **unfinished** dictionary. Every other chapter measures a finished artefact; this one measures a fragment — 35 fascicle-volumes, 6,056 pages, still inside the first letter — and asks what a dictionary 4–6 % done can nonetheless tell us. Chapter built from the committed `data/pd/` family; no source edition is re-parsed here.*

## Trust Block

- **Evidence:** committed `data/pd/` artifacts — `pd_quotations_vs_pwg.tsv` (4,093 shared lemmas), `pd_volume_homogeneity.tsv` (35 ledger rows, 24 measured), `pd_dcs_metrics.json`, `pd_canon_ledger.tsv`. The machine text is the Cologne PDScan 2020 edition of fascicles 1976–2008.
- **Limitations:** letter *a-* only, machine text to ~*apaca-* (2008); print runs to 2019. PD is not comparable to a finished dictionary on coverage — only on the span it has covered.
- **Validation:** `npm run build`; the numbers below are re-derivable from the committed TSVs, and the canon bases are gated in `pd_canon_ledger.tsv` (`--check` green).
- **Owner repo:** `csl-atlas`.
- **Next use:** open [PDScan](https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/web/index.php) for an entry, then the canon ledger before quoting any coverage percentage.

## 1. Overview

*An Encyclopaedic Dictionary of Sanskrit on Historical Principles* — the "Poona Dictionary", PD/EDSHP — is a Deccan College project conceived by **S. M. Katre in 1948** on the OED model: senses in chronological development, each carried by dated citations from a paper corpus of quotation slips. It is the most granular Sanskrit dictionary ever attempted, and it is nowhere near finished.

| | |
|---|---|
| **Machine-readable records** | 107,630 (`<L>` entries), 104,959 lemmas |
| **Machine-readable span** | fascicles 1976–2008, *a-* to ~*apaca-* |
| **Printed to date** | 35 fascicle-volumes / 6,056 pp by 2019, still inside *a-* |
| **Alphabet covered** | ~4–6 % of the headword span of a complete dictionary |
| **Editorial model** | quotation-slip corpus lexicography, senses in historical order |
| **Machine text** | Cologne [PDScan 2020](https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/web/index.php), © 2014 The Sanskrit Library / Thomas Malten, CC BY-NC-SA 3.0 |
| **Relevant repos** | [PD](https://github.com/sanskrit-lexicon/PD) (front-matter OCR) · [`csl-atlas/data/pd/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/pd) (measurements) |

The chapter runs two registers. The **comparative** one asks what can be said against finished dictionaries on the span PD covers; the **fragment** one asks what an unfinished dictionary can still measure about itself. Neither substitutes for a chapter a finished dictionary would get.

## 2. Comparative register — how dense, on the span it covers

PD has traversed only ~4–6 % of the alphabet a complete dictionary covers, but on that span it is far denser than any of them. In each reference's Sanskrit-collated headword list, the position of `apaca` (PD's frontier) gives the headwords in the same range ([HeadwordLists/now-2026](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026)):

| Reference (whole alphabet) | Headwords, whole | Headwords, *a-*…*apaca-* | PD lemmas, same range | PD is denser by |
|---|---:|---:|---:|---:|
| MW — Monier-Williams 1899 | 194,084 | 7,856 | 104,959 | **13.4×** |
| AP — Apte 1890 | 88,867 | 5,414 | 104,959 | **19.4×** |
| PWG — Böhtlingk–Roth (gr.) | 106,082 | 4,519 | 104,959 | **23.2×** |

That is the headline: **PD's first letter already holds as many lemmas as the entire Petersburg dictionary** (104,959 against 106,082), for about 4 % of the alphabet. The density is not an artefact of counting homographs — it is the dictionary's method: every attested compound and derivative gets its own entry and its own citations.

**On the lemmas both dictionaries share, the density shows up in citations too.** The 4,093 lemmas present in both PD and PWG, measured with one quotation rule on both sides: PD carries a **median 4.0×** the attestations (mean 8.97×, p25 2.0×, p75 9.75×; 19.7 % of shared lemmas at 12× or more), and **8.55× in aggregate** (157,480 PD attestations against 18,423 PWG). Below parity: 340 of the 4,093 lemmas, where PWG is the denser entry.

```js
import * as Plot from "npm:@observablehq/plot";

const shared = FileAttachment("../data/pd/pd_quotations_vs_pwg.tsv").tsv({typed: true});
const ratios = shared.filter(d => Number.isFinite(d.attestation_ratio));
```

```js
display(Plot.plot({
  title: "PD ÷ PWG attestations per shared lemma (4,093 lemmas; values above 20 clipped)",
  marks: [
    Plot.barY(ratios, Plot.binX({y: "count"}, {
      x: d => Math.min(d.attestation_ratio, 20), thresholds: 40, fill: "#1f78b4"
    })),
    Plot.ruleX([4], {stroke: "#d62728", strokeDasharray: "4 3"})
  ],
  x: {label: "PD ÷ PWG attestations per lemma (median 4.0, mean 8.97)"},
  y: {label: "shared lemmas", grid: true},
  width: 760, height: 320
}))
```

The red line is the median. The distribution is long-tailed: most shared lemmas sit between 1× and 5×, but a fifth are at 12× or more, and the tail is where PD's encyclopaedic ambition lives.

## 3. Fragment register — what an unfinished dictionary can still measure

A fragment cannot be profiled like a completed dictionary, but it can be tested for **editorial stability across its own production**. Three measures, all from the 24 fascicle-volumes the machine text carries:

1. **Entry size is stable.** The **median entry is 3 printed lines in every one of the 24 measured volumes** and in all 8 bound volumes. The mean runs 4.22–7.56 lines by fascicle — variation in tail length, not in the typical entry.
2. **Source marking declines, and not in a clean step.** The share of entries carrying a bracketed dictionary source falls from **2.06 % in vol. 1 to 0.39 % in vol. 8**, but the series is non-monotonic (pre-v7 average 1.94 %, v7 0.88 %, v8 0.39 %; fascicle 7.2 = 1.88 % against 7.1 = 0.53 %). The cheap conversion signatures are absent — general bracket use is stable at 11–17 % of entries, long source brackets number 29 in the whole corpus, OCR near-misses of the seven source sigla number 3 — so the fall reads as **editorial/content, not a conversion artefact** (medium-high confidence; a print check of one v7 and one v8 page is the falsification test still owed).
3. **Citation mass per page is high and steady.** 419,890 attestations over the 4,327 printed pages the machine text actually covers is **≈97 attestations per printed page**. The oft-quoted ≈69 per page divides the same numerator by the full 6,056-page print extent — a catalogue-extent normalisation that spreads the text over ~1,700 pages (2009–2019) it does not occupy (`pd_publication_ledger.meta.json` pp_lo/pp_hi; the two bases are separated in `page_economics.tsv` and [PD_PAGE_ECONOMICS_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_PAGE_ECONOMICS_2026.md)).

```js
const vols = FileAttachment("../data/pd/pd_volume_homogeneity.tsv").tsv({typed: true});
const measured = vols.filter(d => d.in_digital_text === "yes");
```

```js
display(Plot.plot({
  title: "Mean printed lines per entry, by fascicle-volume year (24 measured volumes)",
  marks: [
    Plot.dot(measured, {x: "year", y: "mean_lines", fill: "#1f78b4", r: 4, tip: true}),
    Plot.ruleY([3], {stroke: "#d62728", strokeDasharray: "4 3"})
  ],
  x: {label: "fascicle-volume year"},
  y: {label: "mean lines per entry", grid: true},
  width: 760, height: 260
}))
```

```js
display(Plot.plot({
  title: "Share of entries carrying a bracketed dictionary source, by fascicle-volume",
  marks: [
    Plot.barY(measured, {x: "ledger_id", y: "marking_share_pct", fill: "#1f78b4", tip: true})
  ],
  x: {label: "fascicle-volume (Deccan College ledger id)", tickRotate: -60},
  y: {label: "% of entries", grid: true},
  width: 760, height: 300
}))
```

The flat median in the first figure and the falling bars in the second are the same finding from two sides: PD's entry **shape** is remarkably constant across four decades of production, while its **acknowledged inheritance** from earlier dictionaries thins out — a fact about the dictionary's sources, not about its ambition.

## 4. What this chapter cannot tell you

- **It cannot rank PD against a finished dictionary on coverage.** Only ~4–6 % of the alphabet exists; §2's ratios are density on the covered span, not completeness.
- **Its denominators are not interchangeable.** "118 covered works" divides by anything from 1,118 to 2,031 depending on the base; the [canon ledger](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_canon_ledger.tsv) labels every one, and a percentage without its base is a defect.
- **It cannot see print pages 2009–2019.** The machine text stops at `8-4327a` (~*apaca-*); the printed record goes further into *a-*.
- **It inherits a known trap.** `MahāBhā.` is the Mahābhārata, `MahāBh.` is the Mahābhāṣya — similarity clustering fuses them; only the locator shape separates them.

## 5. State of the lane (30-10-2026)

The headline numbers above are two-layer validated and policy-matched: the DCS coverage headline recomputes to **25.36 %** against the pinned 25.16 % ([two-layer validation](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_TWO_LAYER_VALIDATION_2026-10-26.md), fascicle range 16.9–36.9 %), and the PD÷PWG attestation multiple standardises to **8.41×** against the raw 8.55× ([policy-matched density](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_POLICY_MATCHED_DENSITY_2026.md)). Four evidence packets landed 29–30 October: [C1](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_EDITION_AVAILABILITY_C1_2026-10-29.md) edition availability (45.11 % work-level lower bound), [C2](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_LOCUS_FIELDS_C2_2026-10-29.md) locus fields (391,444 pairs), [C3](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_AOB_SCAN_LINKS_C3_2026-10-30.md) scan links, and the M1/M2 annotation packets. The lane's open items live in the [parity report](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_KNOWLEDGE_INDEX_PARITY_2026-10-24.md) — its one open row is the human-κ double-coding study.

## 6. Read next

- [PD × DCS coverage report](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md) — what the largest lemmatised Sanskrit corpus does and does not hold of PD's canon.
- [`pd_canon_ledger.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_canon_ledger.tsv) — every canon base and its 118/N.
- [PD knowledge page](https://github.com/sanskrit-lexicon/PD/blob/main/PD_KNOWLEDGE.md) — source-exhaustive facts, do-not-quote list, three verbatim entries.
- [PDScan 2020](https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/web/index.php) — the machine text itself.

## Sources

- `data/pd/pd_quotations_vs_pwg.tsv`, `pd_quotations_summary.json` — the 4,093-lemma comparison, one quotation rule on both sides.
- `data/pd/pd_volume_homogeneity.tsv` + [H6947 report](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_VOLUME_HOMOGENEITY_2026-10-18.md) — 35 ledger rows, 24 measured.
- `data/pd/pd_dcs_metrics.json`, `pd_canon_ledger.tsv` — coverage and canon bases.
- `reports/PD_DCS_CORPUS_COVERAGE_2026.md` §8.2/§8.5 — the density yardsticks and the completion horizon.

_Chapter added 24-10-2026 — DeepSeek Flash (`deepseek-flash`) via DSH; figures read the committed TSVs, no number is typed into prose that is not in `data/pd/`._
