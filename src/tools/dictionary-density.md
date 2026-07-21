---
title: Dictionary density fingerprint
toc: false
---

# How deep is each Cologne dictionary? — a density fingerprint

Three per-entry signals across six dictionaries: **chars/entry** (definition length),
**Sanskrit spans/entry** (glosses/citations), and **markup tags/entry** (editorial apparatus).
Because SKD/VCP are heavy-tailed (single articles > 100k chars), **median** is the robust
depth measure. Full write-up:
[LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md §7.3](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md).

```js
const density = FileAttachment("../data/pd/density_fingerprint.tsv").tsv({typed: true});
```

```js
const dictRows = density.filter(d => d.letter_slp1 === "ALL");
```

```js
Inputs.table(dictRows, {
  columns: ["dict", "n_entries", "chars_mean", "chars_median", "sanskrit_spans_mean", "markup_tags_mean"],
  header: {dict: "Dict", n_entries: "Entries", chars_mean: "chars/entry (mean)",
           chars_median: "chars/entry (median)", sanskrit_spans_mean: "Skt spans/entry",
           markup_tags_mean: "markup tags/entry"},
  sort: "chars_median", reverse: true
})
```

## Median entry length — the robust depth signal

```js
Plot.plot({
  marginLeft: 56,
  x: {label: "median chars per entry (robust to heavy tails)", grid: true},
  y: {label: null},
  marks: [
    Plot.barX(dictRows, {x: "chars_median", y: "dict", fill: "#2c7fb8", sort: {y: "-x"}}),
    Plot.text(dictRows, {x: "chars_median", y: "dict", text: d => d.chars_median,
                         textAnchor: "start", dx: 4, fill: "var(--theme-foreground-muted)"}),
    Plot.ruleX([0])
  ]
})
```

The Sanskrit→Sanskrit encyclopedics (SKD, VCP) carry the longest articles; the terse working
dictionaries (MW, and PWK the *kürzere Fassung*) the shortest.

## Editorial apparatus — markup tags per entry

Markup density reflects the *digitisation apparatus* a dictionary received, not only its
lexicographic depth: PWG carries the richest apparatus; SKD/VCP are plain text (≈ 0 Cologne
markup), so this axis separates the marked-up EN/DE tradition from the plain-text Skt→Skt one.

```js
Plot.plot({
  marginLeft: 56,
  x: {label: "markup tags per entry (mean)", grid: true},
  y: {label: null},
  marks: [
    Plot.barX(dictRows, {x: "markup_tags_mean", y: "dict", fill: "#41ab5d", sort: {y: "-x"}}),
    Plot.text(dictRows, {x: "markup_tags_mean", y: "dict", text: d => d.markup_tags_mean,
                         textAnchor: "start", dx: 4, fill: "var(--theme-foreground-muted)"}),
    Plot.ruleX([0])
  ]
})
```

<div class="note">Data:
<a href="https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/density_fingerprint.tsv">density_fingerprint.tsv</a> ·
generator <a href="https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/density_fingerprint.py">density_fingerprint.py</a> ·
entry bodies from <a href="https://github.com/sanskrit-lexicon/csl-orig/tree/master/v02">csl-orig v02</a>.
H1423, Opus 4.8 (<code>claude-opus-4-8</code>).</div>
