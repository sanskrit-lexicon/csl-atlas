---
title: Per-letter anatomy & the entry-size decay test
toc: false
---

# Why is `a` the letter of compounds — and do dictionary entries shrink over time?

Every Sanskrit dictionary is largest at `a`, and the H1336 study found that **83 %** of
Monier-Williams's `a`-entries are dash-marked compounds, not roots. This page asks whether that
is unique to `a` (it is not), *why* some letters balloon (they head **preverb families**), and
tests a historical claim raised for **Śabdakalpadruma** and **Vācaspatyam**: do entries get
**shorter toward the end of the work** as funding fell? Full write-up:
[LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md).

```js
const anatomy = FileAttachment("../data/pd/letter_anatomy.tsv").tsv({typed: true});
const byPos = FileAttachment("../data/pd/entry_size_by_position.tsv").tsv({typed: true});
const stats = FileAttachment("../data/pd/letter_anatomy_stats.json").json();
```

```js
function tile(label, value, sub, accent) {
  return htl.html`<div style="border:1px solid var(--theme-foreground-faint);border-radius:8px;padding:0.75rem 1rem">
    <div style="font-size:0.8rem;color:var(--theme-foreground-muted)">${label}</div>
    <div style="font-size:1.9rem;font-weight:700;line-height:1.1;color:${accent ?? "inherit"}">${value}</div>
    <div style="font-size:0.8rem;color:var(--theme-foreground-muted)">${sub}</div>
  </div>`;
}
```

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:0.75rem;margin:1rem 0">
${tile("MW ‘a/ā’ compounds", "83.1%", "dash-marked samāsas — highest, but not unique")}
${tile("‘u’ upasarga-initial", "62.3%", "ud- (34%) + upa- (28%)")}
${tile("SKD / VCP decay", "none", "funding hypothesis refuted for both", "var(--theme-foreground-muted)")}
${tile("PWG / PWK / GRA decay", "strong", "later entries really are shorter", "#d95f0e")}
</div>

## Q1 — Samāsa share per letter (Monier-Williams)

`a` is the most compound-dense letter — but `u`, `p`, `s`, `v` are right behind it, and `k`
(which heads no preverb) falls away. Compound-heaviness is **not an `a`-anomaly**; it tracks
whether a letter heads a productive preverb family.

```js
const mwComp = anatomy
  .filter(d => d.dict === "MW" && d.pct_compound !== "" && d.pct_compound != null && d.n_headwords >= 300)
  .sort((a, b) => b.pct_compound - a.pct_compound);
```

```js
Plot.plot({
  marginLeft: 60,
  height: 40 + mwComp.length * 22,
  x: {label: "% of headwords that are dash-marked compounds", grid: true, domain: [0, 100]},
  y: {label: null},
  marks: [
    Plot.barX(mwComp, {x: "pct_compound", y: "letter_iast", fill: "#2c7fb8", sort: {y: "-x"}}),
    Plot.text(mwComp, {x: "pct_compound", y: "letter_iast", text: d => d.pct_compound + "%",
                       textAnchor: "start", dx: 4, fill: "var(--theme-foreground-muted)"}),
    Plot.ruleX([0])
  ]
})
```

## Q2 — Upasarga profile: the mechanism

Each large letter is large because it heads a preverb family: `v` = *vi-*, `u` = *ud-/upa-*,
`s` = *sam-/su-*, `p` = *pra-/pari-/prati-*, `a` = *ā-/abhi-/anu-/apa-/ava-*. `k` heads none.

```js
const mwUps = anatomy
  .filter(d => d.dict === "MW" && d.pct_upasarga !== "" && d.pct_upasarga != null && d.n_headwords >= 2000)
  .sort((a, b) => b.pct_upasarga - a.pct_upasarga);
```

```js
Plot.plot({
  marginLeft: 60,
  height: 40 + mwUps.length * 26,
  x: {label: "% of the letter's headwords that begin with a preverb (surface match)", grid: true},
  y: {label: null},
  marks: [
    Plot.barX(mwUps, {x: "pct_upasarga", y: "letter_iast", fill: "#41ab5d", sort: {y: "-x"}}),
    Plot.text(mwUps, {x: "pct_upasarga", y: "letter_iast", text: d => d.pct_upasarga + "%",
                      textAnchor: "start", dx: 4, fill: "var(--theme-foreground-muted)"}),
    Plot.ruleX([0])
  ]
})
```

<div class="note">Surface longest-prefix matching over-counts preverbs that are also common
stem-initials (<code>ā, vi, ni, su</code>); the ranking of which preverb dominates a letter is
robust to this. The privative <code>a-/an-</code> is a negation, not a preverb, and is not
surface-separable — see the report.</div>

### Every preverb, every dictionary

Each preverb's total sits entirely under its own initial letter, so these are exact counts.
`vi-` leads in every dictionary; the `sam`/`su` order flips in Vedic Grassmann (`su` > `sam`).

```js
const upa = FileAttachment("../data/pd/upasarga_counts.tsv").tsv({typed: true});
```

```js
const upaDicts = ["MW","AP","PWG","PWK","SKD","VCP","GRA","VEI"];
const upaRows = upa.filter(d => d.upasarga && !d.upasarga.startsWith("ALL_") && !d.upasarga.startsWith("TOTAL_"));
```

```js
Inputs.table(upaRows, {
  columns: ["upasarga", ...upaDicts],
  header: Object.fromEntries([["upasarga", "upasarga"], ...upaDicts.map(d => [d, d])]),
  sort: "MW", reverse: true,
  width: {upasarga: 90}
})
```

```js
// long-form grouped bars for the four biggest dictionaries
const upaLong = upaRows.flatMap(r => ["MW","PWG","PWK","AP"].map(d => ({upasarga: r.upasarga, dict: d, n: r[d]})));
```

```js
Plot.plot({
  marginLeft: 60,
  height: 520,
  x: {label: "headwords beginning with the preverb (surface match)", grid: true},
  y: {label: null, domain: upaRows.slice().sort((a,b) => b.MW - a.MW).map(d => d.upasarga)},
  color: {domain: ["MW","PWG","PWK","AP"], range: ["#2c7fb8","#41ab5d","#7fcdbb","#d95f0e"], legend: true},
  marks: [
    Plot.barX(upaLong, {x: "n", y: "upasarga", fill: "dict", fy: "dict", sort: null}),
    Plot.ruleX([0])
  ]
})
```

## Q4 — Do entries shrink toward the end of the dictionary?

The **funding-decay** test. Naïvely regressing entry size on alphabetical position confounds the
funding signal with the fact that later letters host shorter words (Q3). The verdict below uses
an **outlier-robust per-letter rank test** (each letter analysed on its own, then aggregated) —
mandatory because the encyclopaedic dictionaries have single articles over 300,000 characters.

```js
const order = ["PWK","GRA","PWG","AP","MW","SKD","VCP"];
const q4rows = order.map(id => {
  const r = stats.q4_regression[id]?.robust;
  return r ? {
    dict: id, label: stats.dicts[id]?.label ?? id,
    rho: r.rho_combined, ci: `[${r.rho_ci_lo.toFixed(2)}, ${r.rho_ci_hi.toFixed(2)}]`,
    neg: `${r.neg_letters}/${r.n_letters}`, verdict: r.verdict
  } : null;
}).filter(Boolean);
```

```js
Inputs.table(q4rows, {
  columns: ["dict", "label", "rho", "ci", "neg", "verdict"],
  header: {dict: "Dict", label: "Dictionary", rho: "Robust ρ", ci: "95% CI",
           neg: "Letters neg.", verdict: "Verdict"},
  format: {rho: x => x.toFixed(3)},
  width: {label: 260}
})
```

```js
// per-letter rho small bars for the three decaying dicts + one null (VCP) for contrast
const perLetter = ["PWG","PWK","GRA","VCP"].flatMap(id =>
  (stats.q4_regression[id]?.robust?.per_letter ?? []).map(p => ({dict: id, ...p})));
```

```js
Plot.plot({
  marginLeft: 44,
  height: 260,
  fx: {label: null},
  x: {label: "per-letter Spearman(position, entry size)", domain: [-1, 1], grid: true},
  y: {label: "letters", ticks: null},
  color: {domain: ["PWG","PWK","GRA","VCP"], range: ["#d95f0e","#e6550d","#fd8d3c","#9e9ac8"], legend: true},
  marks: [
    Plot.tickX(perLetter, {x: "rho", fx: "dict", stroke: "dict", strokeOpacity: 0.6, y: () => Math.random()}),
    Plot.ruleX([0], {stroke: "var(--theme-foreground)"})
  ]
})
```

Each tick is one initial letter. **PWG / PWK / GRA lean overwhelmingly negative** (later entries
shorter within every letter); **VCP scatters symmetrically around zero** — no decay.

### Mean entry size by decile of the alphabet

Raw decile means (below) are *confounded* by letter composition — VCP's fall and SKD's rise both
vanish once each letter is controlled. Shown to make the confounder visible, not as the test.

```js
const decs = byPos.filter(d => typeof d.position_decile === "number");
```

```js
Plot.plot({
  marginLeft: 44,
  x: {label: "decile of the alphabet (1 = first entries → 10 = last)", domain: [1,10], grid: true, ticks: 10},
  y: {label: "mean entry length (chars, tag-stripped)", grid: true},
  color: {legend: true},
  marks: [
    Plot.lineY(decs, {x: "position_decile", y: "mean_entry_chars", stroke: "dict", marker: "circle"}),
    Plot.ruleY([0])
  ]
})
```

### Wave B — PWG entry size vs *real* publication year

H1416 measured decay against alphabetical position. PWG's `<pc>` field encodes the volume
(1–7), each with a known year, so every entry maps to a real year — **PWG entries shrank
−14.3 %/decade**, and the counter-test shows it is a *smooth* fade (volumes 2–7 still
−15.3 %/decade after dropping the over-detailed vol-1), not a one-time policy break.

```js
const byYear = FileAttachment("../data/pd/entry_size_by_year.tsv").tsv({typed: true});
const pwgYears = byYear.filter(d => d.dict === "PWG" && typeof d.year === "number");
```

```js
Plot.plot({
  marginLeft: 52,
  x: {label: "PWG publication year (volume)", grid: true, tickFormat: "d"},
  y: {label: "mean entry length (chars)", grid: true, domain: [0, null]},
  marks: [
    Plot.lineY(pwgYears, {x: "year", y: "mean_entry_chars", stroke: "#d95f0e", marker: "circle"}),
    Plot.text(pwgYears, {x: "year", y: "mean_entry_chars", text: d => "v" + d.volume,
                         dy: -10, fill: "var(--theme-foreground-muted)", fontSize: 10}),
    Plot.ruleY([0])
  ]
})
```

<div class="note">Data:
<a href="https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/letter_anatomy.tsv">letter_anatomy.tsv</a> ·
<a href="https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/entry_size_by_position.tsv">entry_size_by_position.tsv</a> ·
generator <a href="https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/letter_anatomy.py">letter_anatomy.py</a>.
Sources: MW/AP/PWG/PWK/SKD/VCP/GRA headwords from
<a href="https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026">HeadwordLists/now-2026</a>,
entry bodies from <a href="https://github.com/sanskrit-lexicon/csl-orig/tree/master/v02">csl-orig v02</a>.
Opus 4.8 (<code>claude-opus-4-8</code>), H1416.</div>
