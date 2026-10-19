_Created: 19-10-2026 · Last updated: 19-10-2026_

---
title: Benchmark v2 · held-out tasks
toc: false
---

# Benchmark v2 · held-out tasks

This is the public scoreboard for three review-driven atlas tasks. It reports
**only held-out, double-keyed gold**; a reviewer approving the machine's own
proposal is not a benchmark label. Read the
[task cards](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BENCHMARK_TASK_CARDS.md),
[datasheet](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BENCHMARK_DATASHEET.md)
and [licence](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BENCHMARK_LICENCE.md)
before citing anything here.

```js
const report = FileAttachment("../data/benchmark-report.json").json();
const manifest = FileAttachment("../data/benchmark/split-manifest.json").json();
```

```js
display(html`<div style="display:flex;gap:24px;flex-wrap:wrap;margin:8px 0 16px">
  ${[
    ["Tasks", report.summary.taskCount],
    ["Held-out rows", report.summary.totalHeldOut.toLocaleString()],
    ["Train rows", report.summary.totalTrain.toLocaleString()],
    ["Double-keyed gold", report.summary.totalGold.toLocaleString()],
    ["Gold coverage", `${(report.summary.goldCoverage * 100).toFixed(1)}%`],
    ["Target", `${(report.summary.goldCoverageTarget * 100).toFixed(0)}%`]
  ].map(([label, value]) => html`<div><div style="font-size:1.5rem;font-weight:700">${value}</div><div style="color:var(--theme-foreground-muted);font-size:.85rem">${label}</div></div>`)}
</div>`);
```

## Honest status

```js
display(html`<div class="warning" label="Evidence: ${report.summary.status}">
  <b>${report.summary.status}</b>. ${report.summary.blockingReason}
  No task score is reported while gold coverage is below the 10% floor. The
  report names the blocking rows and the number of independent keys still needed.
</div>`);
```

## Task splits

```js
display(Inputs.table(report.tasks.map(task => ({
  task: task.title,
  heldOut: task.split.heldOutRows,
  train: task.split.trainRows,
  gold: task.gold.goldRows,
  coverage: `${(task.gold.coverage * 100).toFixed(1)}%`,
  status: task.evaluation.status,
  keysNeeded: task.gold.additionalKeysNeeded
})), {
  header: {
    task: "Task",
    heldOut: "Held-out",
    train: "Train",
    gold: "Gold",
    coverage: "Coverage",
    status: "Evaluation",
    keysNeeded: "Keys needed"
  },
  width: { task: 280 }
}));
```

## Blockers and recruitment need

```js
for (const task of report.tasks) {
  display(html`<details style="margin:8px 0">
    <summary><b>${task.title}</b> — ${task.gold.recruitmentNeed}</summary>
    <p>${task.gold.note}</p>
    ${Inputs.table(task.gold.blockingRows, {
      header: { reviewId: "Blocking row", reason: "Reason", reviewStatus: "Status" },
      width: { reviewId: 380 }
    })}
  </details>`);
}
```

## Baselines and negative control

```js
display(Inputs.table(report.tasks.map(task => ({
  task: task.taskId,
  rule: task.baselines.rule.description,
  ruleStatus: task.baselines.rule.status,
  negative: task.baselines.negativeControl.status,
  canaryF1: task.baselines.negativeControl.canary.observed.macroF1,
  canaryPasses: task.baselines.negativeControl.canary.passes
})), {
  header: {
    task: "Task",
    rule: "Rule/parser baseline",
    ruleStatus: "Baseline status",
    negative: "Negative control",
    canaryF1: "Canary F1",
    canaryPasses: "Canary fails as expected"
  },
  width: { rule: 360 }
}));
```

> The canary is synthetic machinery verification, not evidence about the data.
> It deliberately predicts the opposite label and must fail; a passing canary
> score would mean the scorer is broken.

## Frozen split manifest

```js
display(Inputs.table(manifest.tasks.flatMap(split => split.strata.map(stratum => ({
  task: split.taskId,
  stratum: stratum.stratum,
  population: stratum.population,
  sampled: stratum.sampled
}))), {
  header: { task: "Task", stratum: "Stratum", population: "Population", sampled: "Sampled" },
  width: { stratum: 260 }
}));
```

The sampling algorithm, seed and every held-out `reviewId` are in
`src/data/benchmark/split-manifest.json`. Rebuild with
`npm run build-benchmark-report`; score with `npm run score-benchmark`.

## What this page does not do

- It does not print the old `overallPrecision`: that was the machine-verdict
  accept rate over self-reviewed rows, not classifier precision.
- It does not train on the held-out split (`trainRows` is 0 everywhere).
- It does not turn a single-key review into gold.
