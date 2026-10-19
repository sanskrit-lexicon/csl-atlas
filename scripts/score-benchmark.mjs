// Score a frozen Atlas benchmark v2 split (H7099).
//
// Reads the committed split manifest, the source review queues, and any gold
// rows (pool merge reports + optional src/data/benchmark/gold.json). Prints the
// task metrics; when no double-keyed gold exists it prints INSUFFICIENT GOLD and
// exits 0 without inventing a score. This is the published scoring script the
// task cards point at.
//
// Usage:
//   npm run score-benchmark
//   npm run score-benchmark -- --gold path/to/gold.json --out /tmp/scores.json

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { evaluatePredictions } from "./lib/benchmark-metrics.mjs";
import {
  TASKS,
  goldLabelFor,
  loadExplicitGold,
  loadPoolIndex,
  readJson
} from "./build-benchmark-report.mjs";

const ROOT = process.cwd();
const MANIFEST = path.resolve(ROOT, "src", "data", "benchmark", "split-manifest.json");

function parseArgs(argv) {
  const args = { gold: null, out: null };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--gold") args.gold = argv[++i];
    else if (argv[i] === "--out") args.out = argv[++i];
  }
  return args;
}

function explicitGoldWithOverride(overridePath) {
  const map = loadExplicitGold();
  if (!overridePath) return map;
  const doc = readJson(path.resolve(ROOT, overridePath));
  for (const row of doc.rows ?? []) {
    if (!row?.taskId || !row?.reviewId || !row?.label) continue;
    if (!map.has(row.taskId)) map.set(row.taskId, new Map());
    map.get(row.taskId).set(row.reviewId, row.label);
  }
  return map;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!fs.existsSync(MANIFEST)) {
    console.error("No split manifest. Run: npm run build-benchmark-report");
    process.exit(2);
  }
  const manifest = readJson(MANIFEST);
  const poolIndex = loadPoolIndex();
  const explicitGold = explicitGoldWithOverride(args.gold);
  const sourceCache = new Map();
  const result = { schemaVersion: "2.0.0", manifest: "src/data/benchmark/split-manifest.json", tasks: [] };

  for (const taskDef of TASKS) {
    const split = manifest.tasks.find(task => task.taskId === taskDef.taskId);
    if (!split) continue;
    if (!sourceCache.has(taskDef.source)) {
      const doc = readJson(path.resolve(ROOT, taskDef.source));
      sourceCache.set(taskDef.source, new Map((doc.items ?? []).map(item => [item.reviewId, item])));
    }
    const source = sourceCache.get(taskDef.source);
    const goldRows = [];
    for (const row of split.rows) {
      const item = source.get(row.reviewId);
      if (!item) continue;
      const label = goldLabelFor(taskDef, item, poolIndex, explicitGold);
      if (label != null && taskDef.labels.includes(label)) {
        goldRows.push({ reviewId: row.reviewId, label, prediction: taskDef.rule(item) });
      }
    }
    if (goldRows.length === 0) {
      result.tasks.push({
        taskId: taskDef.taskId,
        heldOutRows: split.rows.length,
        goldRows: 0,
        status: "INSUFFICIENT GOLD",
        metrics: null
      });
      continue;
    }
    const goldLabels = goldRows.map(row => row.label);
    const majorityLabel = [...goldRows.reduce(
      (counts, row) => counts.set(row.label, (counts.get(row.label) || 0) + 1),
      new Map()
    )].sort((a, b) => (b[1] - a[1]) || a[0].localeCompare(b[0]))[0][0];
    result.tasks.push({
      taskId: taskDef.taskId,
      heldOutRows: split.rows.length,
      goldRows: goldRows.length,
      status: "evaluated",
      rule: evaluatePredictions(goldRows.map(row => row.prediction), goldLabels, taskDef.labels),
      trivial: evaluatePredictions(goldRows.map(() => majorityLabel), goldLabels, taskDef.labels)
    });
  }

  const text = JSON.stringify(result, null, 2);
  if (args.out) fs.writeFileSync(path.resolve(ROOT, args.out), `${text}\n`);
  console.log(text);
  for (const task of result.tasks) {
    console.log(`${task.taskId}: ${task.status} (${task.goldRows}/${task.heldOutRows} gold)`);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
