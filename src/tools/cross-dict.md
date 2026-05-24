---
title: Cross-dictionary comparison
toc: false
---

# Cross-dictionary comparison

The atlas's core comparison: nine CDSL dictionaries on a **format-robust common-block vocabulary** (blocks detectable regardless of each dict's markup). It shows source-citation density and the population of each structural block, per dictionary. Data: the [cross-dict audit](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/CROSS_DICT.md) in the MWS docs-pass branch.

```js
const cross = FileAttachment("../data/cross-dict.json").json();
```

```js
const dicts = cross.dicts;
const blocks = cross.blocks;
const BLOCK_LABEL = {
  head: "head", body: "body (¦)", gram: "gram (lex)", cite: "cite (ls)",
  hom: "homograph", etym: "etymology", xref: "cross-ref",
  hedge: "L. hedge", info: "info (digit.)"
};
```

## Source-citation density (`<ls>` per record)

Multi-volume PWG is ~4× denser per entry than single-volume MW; the Sanskrit-Sanskrit lexica (SKD, VCP) and Cappeller carry no `<ls>` apparatus at all.

```js
display(Plot.plot({
  width: 900,
  height: 300,
  marginLeft: 50,
  x: {label: "Dictionary", domain: [...dicts].sort((a, b) => b.ls_per_record - a.ls_per_record).map(d => d.code)},
  y: {label: "<ls> per record", grid: true},
  marks: [
    Plot.barY(dicts, {
      x: "code", y: "ls_per_record",
      fill: d => d.genre === "sanskrit" ? "#999999" : (d.volumes > 1 ? "#33a02c" : "#1f78b4"),
      tip: {format: {code: true, ls_per_record: ".2f", records: ",d", volumes: true}}
    }),
    Plot.text(dicts, {x: "code", y: "ls_per_record", text: d => d.ls_per_record.toFixed(2), dy: -6, fontSize: 10}),
    Plot.ruleY([0])
  ]
}));
```

## Common-block population (% of entries)

The `L. hedge` and `info` (digitisation) rows are lit for **MW alone**; citation is near-universal in PWG; the Sanskrit-Sanskrit lexica SKD/VCP show only head + body, marking their different genre.

```js
const cells = dicts.flatMap(d => blocks.map(b => ({
  dict: d.code, block: BLOCK_LABEL[b] ?? b, pct: d.blocks_pct[b]
})));
display(Plot.plot({
  width: 900,
  height: 360,
  marginLeft: 90,
  color: {type: "linear", scheme: "ylorrd", domain: [0, 100], legend: true, label: "% of entries"},
  x: {label: "Dictionary", domain: dicts.map(d => d.code)},
  y: {label: "Common block", domain: blocks.map(b => BLOCK_LABEL[b] ?? b)},
  marks: [
    Plot.cell(cells, {x: "dict", y: "block", fill: "pct", tip: {format: {dict: true, block: true, pct: ".1f"}}}),
    Plot.text(cells, {x: "dict", y: "block", text: d => d.pct >= 0.5 ? d.pct.toFixed(0) : "",
                      fill: d => d.pct > 60 ? "white" : "black", fontSize: 9})
  ]
}));
```

## Per-dictionary summary

```js
display(Inputs.table(dicts, {
  columns: ["code", "name", "volumes", "genre", "records", "ls_per_record", "modal_blocks", "mean_blocks"],
  header: {code: "Dict", name: "Edition", volumes: "Vols", genre: "Genre", records: "Records",
           ls_per_record: "ls/rec", modal_blocks: "Modal", mean_blocks: "Mean blocks"},
  format: {records: x => x.toLocaleString()},
  sort: "ls_per_record", reverse: true
}));
```

---

## Reading the comparison

- **Block economy is general.** Every single-volume dict reuses a small modal kernel (2–5 blocks) with a long tail — not unique to MW. Multi-volume PWG is denser. See [PAPER.md §9.3](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md#9-methodological-limitations).
- **The `L.` hedge is MW-specific.** Of all nine, only MW carries the generic lexicographer-hedge (14% of entries); PWG cites *named* koshas instead. See the [D2 audit](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/LS_HEDGE_CHECK.md).
- **`info` is a digitisation trace.** The near-universal MW `info` block (96%) has no analogue elsewhere — it is the infrastructure layer added by CDSL, not part of the print dictionary.
- **SKD/VCP are a different genre.** No `<lex>`/`<ls>`; they mark gender inline and cite via inline `iti <source>`. The block apparatus does not transfer to them.

Static figures: [cross-dict-density](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/cross-dict-density-en.svg) · [cross-dict-blocks](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/figures/cross-dict-blocks-en.svg).

Source: CDSL 2026-05-24 · CC-BY-SA-4.0
