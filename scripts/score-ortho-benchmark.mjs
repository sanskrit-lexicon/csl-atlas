// Score the de/ru historical-normalization benchmark (H7103).
//
// CI-safe: reads only the committed gold TSV and (for --check) the committed
// benchmark JSON. No sibling checkout, network or reform map is required.
//
// Usage:
//   npm run score-ortho-benchmark                         # check committed baselines
//   npm run score-ortho-benchmark -- --predictions p.tsv  # score a model
//   npm run score-ortho-benchmark -- --json               # machine-readable output
//
// Predictions format: TSV with header `id<TAB>prediction` (header optional);
// every gold id must be present exactly once.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const GOLD = path.resolve(process.cwd(), "data", "ortho", "gold.tsv");
const BENCH = path.resolve(process.cwd(), "data", "ortho", "normalization_benchmark.json");

/** Generic legislated-reform rewrite rules; deliberately map-independent. */
export function normalizeRule(lang, token) {
  let out = String(token ?? "").normalize("NFC").toLowerCase();
  if (lang === "de") {
    out = out.replace(/th/g, "t");
    out = out.replace(/ß/g, "ss");
    out = out.replace(/iren$/, "ieren");
    out = out.replace(/([a-zäöüß])irt$/, "$1iert");
    out = out.replace(/irt(e|en|est|et)$/, "iert$1");
  } else if (lang === "ru") {
    out = out.replace(/[ѣѢ]/g, "е");
    out = out.replace(/[іІ]/g, "и");
    out = out.replace(/[ѳѲ]/g, "ф");
    out = out.replace(/[ѵѴ]/g, "и");
    out = out.replace(/[ъЪ]$/g, "");
  }
  return out;
}

export function levenshtein(a, b) {
  const left = Array.from(String(a ?? ""));
  const right = Array.from(String(b ?? ""));
  if (!left.length) return right.length;
  if (!right.length) return left.length;
  let prev = Array.from({ length: right.length + 1 }, (_, i) => i);
  for (let i = 1; i <= left.length; i++) {
    const cur = [i];
    for (let j = 1; j <= right.length; j++) {
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (left[i - 1] === right[j - 1] ? 0 : 1));
    }
    prev = cur;
  }
  return prev[right.length];
}

export function cer(prediction, target) {
  const t = Array.from(String(target ?? "").normalize("NFC").toLowerCase());
  if (!t.length) return prediction === target ? 0 : 1;
  return levenshtein(String(prediction ?? "").normalize("NFC").toLowerCase(), t.join("")) / t.length;
}

function round(value) {
  return Number(value.toFixed(6));
}

function aggregate(rows) {
  const n = rows.length;
  const correct = rows.filter((r) => r.pred === r.target).length;
  const charDistance = rows.reduce((sum, r) => sum + levenshtein(r.pred, r.target), 0);
  const targetChars = rows.reduce((sum, r) => sum + Array.from(r.target).length, 0);
  const accuracy = n ? round(correct / n) : null;
  return {
    n,
    accuracy,
    wer: accuracy === null ? null : round(1 - accuracy),
    cer: targetChars ? round(charDistance / targetChars) : n ? round(rows.reduce((s, r) => s + cer(r.pred, r.target), 0) / n) : null,
    macroCer: n ? round(rows.reduce((s, r) => s + cer(r.pred, r.target), 0) / n) : null
  };
}

function lcg(seed) {
  let state = seed >>> 0;
  return () => {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    return state / 4294967296;
  };
}

function percentile(sorted, q) {
  return sorted[Math.min(sorted.length - 1, Math.max(0, Math.floor(q * sorted.length)))];
}

/** Fixed-seed row-level bootstrap 95% CIs for accuracy, WER and CER. */
export function bootstrapMetricCis(rows, { b = 1000, seed = 7103 } = {}) {
  if (!rows.length) return null;
  const rand = lcg(seed);
  const draws = { accuracy: [], wer: [], cer: [] };
  for (let i = 0; i < b; i++) {
    const sample = Array.from({ length: rows.length }, () => rows[Math.floor(rand() * rows.length)]);
    const m = aggregate(sample);
    draws.accuracy.push(m.accuracy);
    draws.wer.push(m.wer);
    draws.cer.push(m.cer);
  }
  const ci = (values) => {
    const sorted = values.slice().sort((a, b2) => a - b2);
    return [round(percentile(sorted, 0.025)), round(percentile(sorted, 0.975))];
  };
  return { accuracy: ci(draws.accuracy), wer: ci(draws.wer), cer: ci(draws.cer) };
}

/** rows: [{lang, dict, split, target, pred}] */
export function computeMetrics(rows) {
  const metricRows = rows.map((r) => ({
    ...r,
    target: String(r.target ?? "").normalize("NFC").toLowerCase(),
    pred: String(r.pred ?? "").normalize("NFC").toLowerCase()
  }));
  const grouped = (key) => {
    const out = {};
    for (const value of [...new Set(metricRows.map((r) => r[key]))].sort()) {
      out[value] = aggregate(metricRows.filter((r) => r[key] === value));
    }
    return out;
  };
  return { ...aggregate(metricRows), byLang: grouped("lang"), byDict: grouped("dict"), bySplit: grouped("split") };
}

export function readGoldTsv(file = GOLD) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/).filter((line) => line.trim());
  const header = lines[0].split("\t");
  if (header[0] !== "id" || !header.includes("target")) throw new Error(`unexpected gold header in ${file}`);
  return lines.slice(1).map((line, index) => {
    const cells = line.split("\t");
    if (cells.length !== header.length) throw new Error(`gold line ${index + 2}: ${cells.length} cells, expected ${header.length}`);
    return Object.fromEntries(header.map((key, i) => [key, cells[i]]));
  });
}

export function readPredictions(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/).filter((line) => line.trim());
  const first = lines[0].split("\t");
  const hasHeader = first[0]?.toLowerCase() === "id" && first.length >= 2;
  const body = hasHeader ? lines.slice(1) : lines;
  const predictions = new Map();
  for (const [index, line] of body.entries()) {
    const [id, ...rest] = line.split("\t");
    if (!id) throw new Error(`prediction line ${index + 1}: missing id`);
    if (predictions.has(id)) throw new Error(`prediction line ${index + 1}: duplicate id ${id}`);
    predictions.set(id, rest.join("\t"));
  }
  return predictions;
}

export function scorePredictions(rows, predictions) {
  const scored = rows.map((row) => {
    if (!predictions.has(row.id)) throw new Error(`missing prediction for gold id ${row.id}`);
    return { lang: row.lang, dict: row.dict, split: row.split, target: row.target, pred: predictions.get(row.id) };
  });
  return computeMetrics(scored);
}

function committedBaseline() {
  const bench = JSON.parse(fs.readFileSync(BENCH, "utf8"));
  return bench.metrics?.ruleMap ?? null;
}

function sameMetrics(a, b) {
  if (!a || !b) return false;
  const keys = ["n", "accuracy", "cer", "macroCer"];
  return keys.every((key) => Math.abs((a[key] ?? 0) - (b[key] ?? 0)) < 1e-9);
}

function main() {
  const args = process.argv.slice(2);
  const predictionsFile = args.includes("--predictions") ? args[args.indexOf("--predictions") + 1] : null;
  const jsonOut = args.includes("--json");
  const rows = readGoldTsv();
  let metrics;
  let name;
  if (predictionsFile) {
    metrics = scorePredictions(rows, readPredictions(predictionsFile));
    name = path.basename(predictionsFile);
  } else {
    metrics = scorePredictions(rows, new Map(rows.map((row) => [row.id, normalizeRule(row.lang, row.token)])));
    name = "rule-map rewrite baseline";
    const expected = committedBaseline();
    if (!sameMetrics(metrics, expected)) {
      console.error(`score-ortho-benchmark: recomputed baseline (${metrics.accuracy}/${metrics.cer}) disagrees with committed JSON (${expected?.accuracy}/${expected?.cer})`);
      process.exit(1);
    }
  }
  if (jsonOut || predictionsFile) {
    console.log(JSON.stringify({ name, ...metrics }, null, 2));
  } else {
    console.log(`score-ortho-benchmark: ${name}`);
    console.log(`  n=${metrics.n} accuracy=${(metrics.accuracy * 100).toFixed(1)}% WER=${(metrics.wer * 100).toFixed(1)}% CER=${metrics.cer.toFixed(4)} macroCER=${metrics.macroCer.toFixed(4)}`);
    for (const [lang, m] of Object.entries(metrics.byLang)) {
      console.log(`  ${lang}: n=${m.n} accuracy=${(m.accuracy * 100).toFixed(1)}% WER=${(m.wer * 100).toFixed(1)}% CER=${m.cer.toFixed(4)}`);
    }
    console.log("  committed baseline matches.");
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
