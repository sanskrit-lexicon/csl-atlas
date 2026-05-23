---
title: Type comparator
---

# Type comparator

Pick two article types and see how their block profiles differ side-by-side.

```js
const matrix = FileAttachment("../../data/block-by-type-matrix.json").json();
```

```js
const types = matrix.types;
const typeA = view(Inputs.select(types, {label: "Type A", value: "root"}));
const typeB = view(Inputs.select(types, {label: "Type B", value: "compound"}));
```

```js
const blocks = matrix.blocks;
const rowA = matrix.matrix.find(r => r.type === typeA);
const rowB = matrix.matrix.find(r => r.type === typeB);

const diff = blocks.map(b => ({
  block: b,
  [typeA]: rowA[b + "_pct"],
  [typeB]: rowB[b + "_pct"],
  delta: rowA[b + "_pct"] - rowB[b + "_pct"]
}));

display(
  Plot.plot({
    width: 900,
    height: 600,
    marginLeft: 80,
    x: {label: "% of entries", domain: [-100, 100]},
    y: {label: null, domain: blocks},
    marks: [
      Plot.barX(diff, {y: "block", x: "delta", fill: d => d.delta > 0 ? "#1f78b4" : "#e31a1c"}),
      Plot.ruleX([0]),
      Plot.text(diff, {y: "block", x: "delta", text: d => d.delta.toFixed(0), dx: d => d.delta > 0 ? 5 : -5, fill: "black"})
    ]
  })
);
```

---

**Reading:** the bar shows the difference in block-presence percentage between Type A and Type B. Positive (blue, right): Type A has this block more often. Negative (red, left): Type B has this block more often.

Source: CDSL mw.txt 2026-05-23 · CC-BY-SA-4.0
