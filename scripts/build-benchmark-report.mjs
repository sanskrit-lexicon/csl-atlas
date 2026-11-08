// Atlas benchmark v2 (H7099) — held-out splits, real gold, honest metrics.
//
// v1 called the machine-verdict accept rate "precision" and reported
// overallPrecision 1.0 over 147 self-reviewed rows. That is not a benchmark:
// a reviewer approving the machine's own proposal is not an independent gold
// label. v2 removes that number, freezes three task samples, defines gold as
// two independent keys (or an explicit expert gold file), and reports every
// score as not-evaluable until the gold exists.
//
// The honest outcome today is gold insufficiency. The report names the task,
// the frozen rows, the missing keys, and the recruitment need instead of
// printing a number that cannot support it.
//
// Deterministic, reads committed review JSON. Usage: npm run build-benchmark-report.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { generatedAtForPayload, licenseFields, readJsonIfExists } from "./lib/dataset-meta.mjs";
import { DEFAULT_SEED, evaluatePredictions, negativeControlCanary, round } from "./lib/benchmark-metrics.mjs";

const ROOT = process.cwd();
const REVIEW_DIR = path.resolve(ROOT, "src", "data", "review");
const POOL_MERGE_DIR = path.resolve(ROOT, "data", "review", "pool_merge");
const LANGDETECT_METRICS = path.resolve(ROOT, "src", "data", "external", "langdetect-german-metrics.json");
const GOLD_FILE = path.resolve(ROOT, "src", "data", "benchmark", "gold.json");
const MANIFEST_DIR = path.resolve(ROOT, "src", "data", "benchmark");
const MANIFEST = path.join(MANIFEST_DIR, "split-manifest.json");
const OUTPUT = path.resolve(ROOT, "src", "data", "benchmark-report.json");
const TASK_CARDS = path.resolve(ROOT, "docs", "BENCHMARK_TASK_CARDS.md");
const DATASHEET = path.resolve(ROOT, "docs", "BENCHMARK_DATASHEET.md");
const LICENCE = path.resolve(ROOT, "docs", "BENCHMARK_LICENCE.md");

const SAMPLE_SIZE = 100;
const GOLD_COVERAGE_TARGET = 0.10;
const SEED = DEFAULT_SEED;

const TASKS = [
  {
    taskId: "encoding-ocr",
    title: "Encoding/OCR anomaly triage",
    question: "Is an observed MW↔Petersburg entry difference a parser/OCR artifact, a possible typo, a variant convention, a legitimate form, or lineage-only?",
    source: "src/data/review/h5-anomaly-review.json",
    sourceQueue: "encoding-ocr",
    labels: ["parser-artifact", "possible-typo", "variant-convention", "legitimate-form", "lineage-only"],
    labelOf: item => item.reviewedValue ?? null,
    stratumOf: item => item.machineValue?.sampleClass ?? "unknown",
    rule: item => {
      const sampleClass = item.machineValue?.sampleClass;
      if (sampleClass === "known-correction") return "parser-artifact";
      if (sampleClass === "null-control") return "legitimate-form";
      return "possible-typo";
    },
    ruleDescription: "known-correction → parser-artifact; null-control → legitimate-form; every other class → possible-typo.",
    trivialDescription: "Majority class in the gold rows (fit only after gold exists)."
  },
  {
    taskId: "gender-conflict",
    title: "Cross-dictionary gender conflict adjudication",
    question: "Is a disjoint gender assertion between two dictionaries a real conflict, or a convention/evidence artifact?",
    source: "src/data/review/gender-conflicts-review.json",
    sourceQueue: "pos-gender-conflict",
    labels: ["real-conflict", "convention-or-artifact"],
    labelOf: item => item.reviewedValue ?? null,
    normalizeGold: label => (label === "real-conflict" || label === "convention-or-artifact" ? label : null),
    stratumOf: item => {
      const typology = item.machineValue?.typology ?? {};
      return `${typology.genderPair ?? "?"} · ${typology.basis ?? "?"}`;
    },
    rule: item => {
      const typology = item.machineValue?.typology ?? {};
      return typology.basis === "lex" && typology.overlap === "disjoint"
        ? "real-conflict"
        : "convention-or-artifact";
    },
    ruleDescription: "lex-basis + disjoint overlap → real-conflict; every prose-mixed or partial row → convention-or-artifact.",
    trivialDescription: "Majority class in the gold rows (fit only after gold exists)."
  },
  {
    taskId: "citation-link-target",
    title: "Citation-link target verification",
    question: "Does the proposed VedaWeb URL for an RV locus resolve to the intended stanza?",
    source: "src/data/review/citation-link-pilot-review.json",
    sourceQueue: "citation-link-target",
    labels: ["link-correct", "link-wrong"],
    labelOf: item => item.reviewedValue ?? null,
    normalizeGold: label => (label === "link-correct" || label === "link-wrong" ? label : null),
    stratumOf: item => {
      const mandala = item.machineValue?.mandala;
      return mandala == null ? "unknown-mandala" : `mandala-${mandala}`;
    },
    rule: () => "link-correct",
    ruleDescription: "Accept every machine-proposed VedaWeb link (the current machine verdict).",
    trivialDescription: "Majority class in the gold rows (fit only after gold exists)."
  }
];

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function countKeys(item, poolIndex) {
  if (poolIndex.has(item.reviewId)) return poolIndex.get(item.reviewId).keys;
  return item.reviewer ? 1 : 0;
}

function loadPoolIndex() {
  const index = new Map();
  if (!fs.existsSync(POOL_MERGE_DIR)) return index;
  for (const file of fs.readdirSync(POOL_MERGE_DIR).filter(name => name.endsWith(".json")).sort()) {
    const doc = readJson(path.join(POOL_MERGE_DIR, file));
    for (const record of doc.records ?? []) {
      const annotators = new Set((record.keys ?? []).map(key => key.annotator));
      const label = record.reviewedValue || (record.keys ?? []).map(key => key.resolvedLabel).find(Boolean) || "";
      index.set(record.reviewId, {
        keys: annotators.size,
        label,
        status: record.reviewStatus,
        singleKey: Boolean(record.singleKey)
      });
    }
  }
  return index;
}

function loadExplicitGold() {
  const map = new Map();
  if (!fs.existsSync(GOLD_FILE)) return map;
  const doc = readJson(GOLD_FILE);
  for (const row of doc.rows ?? []) {
    if (!row?.taskId || !row?.reviewId || !row?.label) continue;
    if (!map.has(row.taskId)) map.set(row.taskId, new Map());
    map.get(row.taskId).set(row.reviewId, row.label);
  }
  return map;
}

function goldLabelFor(task, item, poolIndex, explicitGold) {
  const explicit = explicitGold.get(task.taskId);
  if (explicit?.has(item.reviewId)) {
    const label = explicit.get(item.reviewId);
    return task.normalizeGold ? task.normalizeGold(label) : label;
  }
  const pooled = poolIndex.get(item.reviewId);
  if (pooled && pooled.keys >= 2 && (pooled.status === "reviewed-ok" || pooled.status === "reviewed-corrected")) {
    const raw = pooled.label || task.labelOf(item);
    return task.normalizeGold ? task.normalizeGold(raw) : raw;
  }
  return null;
}

function freezeSample(task, items, poolIndex) {
  const byStratum = new Map();
  for (const item of items) {
    const stratum = task.stratumOf(item);
    if (!byStratum.has(stratum)) byStratum.set(stratum, []);
    byStratum.get(stratum).push(item);
  }
  const strata = [...byStratum.keys()].sort();
  for (const stratum of strata) {
    byStratum.get(stratum).sort((a, b) => {
      const ha = sha256(`${SEED}:${task.taskId}:${a.reviewId}`);
      const hb = sha256(`${SEED}:${task.taskId}:${b.reviewId}`);
      return ha < hb ? -1 : ha > hb ? 1 : a.reviewId.localeCompare(b.reviewId);
    });
  }
  const picked = [];
  const cursor = new Map(strata.map(stratum => [stratum, 0]));
  while (picked.length < Math.min(SAMPLE_SIZE, items.length)) {
    let advanced = false;
    for (const stratum of strata) {
      if (picked.length >= Math.min(SAMPLE_SIZE, items.length)) break;
      const rows = byStratum.get(stratum);
      const position = cursor.get(stratum);
      if (position < rows.length) {
        picked.push({ item: rows[position], stratum });
        cursor.set(stratum, position + 1);
        advanced = true;
      }
    }
    if (!advanced) break;
  }
  const sampledByStratum = {};
  for (const { stratum } of picked) sampledByStratum[stratum] = (sampledByStratum[stratum] || 0) + 1;
  const manifestRows = picked.map(({ item, stratum }) => {
    const pooled = poolIndex.get(item.reviewId);
    const keys = countKeys(item, poolIndex);
    return {
      reviewId: item.reviewId,
      stratum,
      reviewStatus: pooled?.status ?? item.reviewStatus,
      existingKeys: keys,
      goldEligible: false
    };
  });
  const strataSummary = strata.map(stratum => ({
    stratum,
    population: byStratum.get(stratum).length,
    sampled: sampledByStratum[stratum] ?? 0
  })).sort((a, b) => (b.population - a.population) || a.stratum.localeCompare(b.stratum));
  return { rows: manifestRows, strataSummary };
}

function goldBlockers(task, sampleRows, manifestRows, poolIndex, explicitGold) {
  const byId = new Map(sampleRows.map(item => [item.reviewId, item]));
  const singleKey = manifestRows.filter(row => row.existingKeys === 1);
  const unkeyed = manifestRows.filter(row => row.existingKeys === 0);
  const gold = manifestRows.filter(row => row.goldEligible);
  const targetGold = Math.ceil(GOLD_COVERAGE_TARGET * manifestRows.length);
  let remaining = Math.max(0, targetGold - gold.length);
  const secondKeysOnSingle = Math.min(remaining, singleKey.length);
  remaining -= secondKeysOnSingle;
  const additionalKeys = secondKeysOnSingle + remaining * 2;
  const blocking = [...unkeyed, ...singleKey].slice(0, 10).map(row => ({
    reviewId: row.reviewId,
    reason: row.existingKeys === 0 ? "no-independent-key" : "single-key-only",
    reviewStatus: row.reviewStatus
  }));
  return {
    targetGoldRows: targetGold,
    goldRows: gold.length,
    coverage: manifestRows.length ? round(gold.length / manifestRows.length) : 0,
    coverageMet: manifestRows.length > 0 && gold.length / manifestRows.length >= GOLD_COVERAGE_TARGET,
    rowsSingleKey: singleKey.length,
    rowsUnkeyed: unkeyed.length,
    additionalKeysNeeded: additionalKeys,
    recruitmentNeed: additionalKeys > 0
      ? `Recruit ${Math.ceil(additionalKeys / 2)}–${additionalKeys} independent keyings (${additionalKeys} keys) to reach ${targetGold} double-keyed rows for this task.`
      : "Gold target met; no additional keying needed.",
    blockingRows: blocking,
    note: "A review by the same session or agent that produced the machine value is not an independent key and never counts as gold."
  };
}

function buildSplitManifest(taskSamples) {
  return {
    schemaVersion: "2.0.0",
    ...licenseFields(),
    generatedBy: "npm run build-benchmark-report",
    seed: SEED,
    sampling: "Stratified by the task's declared stratum, rows ordered inside each stratum by sha256(seed:taskId:reviewId); one row drawn per stratum round-robin until the sample size is reached. Recomputable from this file and the committed queues.",
    trainingPolicy: "No model is trained in this repository. train rows = 0 for every task; held-out rows are never used for fitting any baseline. The rule baseline is fixed in scripts/build-benchmark-report.mjs and the trivial baseline is fit on gold only.",
    sampleSize: SAMPLE_SIZE,
    goldDefinition: "Gold = two independent keys on the same row (data/review/pool_merge/*.json, >=2 distinct pool-aNN annotators) or an explicit expert row in src/data/benchmark/gold.json. Single-key reviews, agent reviews, and self-reviewed machine verdicts are not gold.",
    tasks: taskSamples.map(sample => ({
      taskId: sample.taskId,
      title: sample.title,
      source: sample.source,
      populationSize: sample.populationSize,
      heldOutRows: sample.rows.length,
      trainRows: 0,
      strata: sample.strataSummary,
      rows: sample.rows
    }))
  };
}

function buildTaskReport(task, sampleRows, manifestRows, poolIndex, explicitGold) {
  const sampleIds = new Set(manifestRows.map(row => row.reviewId));
  const rows = sampleRows.filter(item => sampleIds.has(item.reviewId));
  const goldPairs = [];
  for (const row of manifestRows) {
    const item = rows.find(entry => entry.reviewId === row.reviewId);
    const label = goldLabelFor(task, item, poolIndex, explicitGold);
    if (label != null && task.labels.includes(label)) {
      row.goldEligible = true;
      goldPairs.push({ reviewId: row.reviewId, label, prediction: task.rule(item) });
    }
  }
  const hasGold = goldPairs.length > 0;
  const majorityLabel = hasGold
    ? [...goldPairs.reduce((counts, pair) => counts.set(pair.label, (counts.get(pair.label) || 0) + 1), new Map())]
      .sort((a, b) => (b[1] - a[1]) || a[0].localeCompare(b[0]))[0][0]
    : null;
  const trivialMetrics = hasGold
    ? evaluatePredictions(goldPairs.map(() => majorityLabel), goldPairs.map(pair => pair.label), task.labels, { seed: SEED })
    : null;
  const evaluation = hasGold
    ? {
        status: "evaluated",
        classification: "HELD-OUT GOLD — interpretable as a benchmark",
        metrics: evaluatePredictions(goldPairs.map(pair => pair.prediction), goldPairs.map(pair => pair.label), task.labels, { seed: SEED })
      }
    : {
        status: "not_evaluable",
        classification: "INSUFFICIENT GOLD — every score below is null by design",
        reason: `0 of ${manifestRows.length} held-out rows have two independent keys; no task metric can be computed from review rows graded by the same session that produced the machine value.`,
        metrics: {
          n: 0,
          precision: null,
          recall: null,
          f1: null,
          accuracy: null,
          cohenKappa: null,
          krippendorffAlpha: null,
          bootstrapCI95: { macroF1: null, krippendorffAlpha: null },
          perLabel: {}
        }
      };
  return {
    taskId: task.taskId,
    title: task.title,
    question: task.question,
    source: task.source,
    labels: task.labels,
    split: {
      populationSize: sampleRows.length,
      heldOutRows: manifestRows.length,
      trainRows: 0,
      manifest: "src/data/benchmark/split-manifest.json",
      strata: manifestRows.length,
      stratumCount: new Set(manifestRows.map(row => row.stratum)).size
    },
    gold: goldBlockers(task, rows, manifestRows, poolIndex, explicitGold),
    baselines: {
      rule: {
        description: task.ruleDescription,
        status: hasGold ? "evaluated" : "not_evaluable_insufficient_gold",
        metrics: hasGold ? evaluation.metrics : null
      },
      trivial: {
        description: task.trivialDescription,
        status: hasGold ? "evaluated" : "not_evaluable_insufficient_gold",
        majorityLabel,
        metrics: trivialMetrics
      },
      negativeControl: {
        description: "Inverted-oracle control on a 40-row synthetic canary; it must fail. Its real-data scores are null because there is no gold.",
        status: "canary",
        onRealData: "not_evaluable_insufficient_gold",
        canary: negativeControlCanary({ seed: SEED })
      }
    },
    evaluation
  };
}

function renderTaskCards(report) {
  const lines = [
    "# Atlas benchmark v2 — task cards",
    "",
    `_Generated: ${report.generatedAt} · generated by \`npm run build-benchmark-report\`._`,
    "",
    "These cards describe the three frozen held-out tasks. Read the [datasheet](./BENCHMARK_DATASHEET.md)",
    "and the [licence](./BENCHMARK_LICENCE.md) before citing a number. A task with",
    "`INSUFFICIENT GOLD` has no score, and no score may be inferred from the review overlay.",
    ""
  ];
  for (const task of report.tasks) {
    lines.push(`## ${task.title}`, "");
    lines.push(`- **Task id:** \`${task.taskId}\``);
    lines.push(`- **Question:** ${task.question}`);
    lines.push(`- **Source queue:** \`${task.source}\``);
    lines.push(`- **Labels:** ${task.labels.map(label => `\`${label}\``).join(", ")}`);
    lines.push(`- **Frozen split:** ${task.split.heldOutRows} held-out rows, ${task.split.trainRows} train rows, ${task.split.stratumCount} strata`);
    lines.push(`- **Rule baseline:** ${task.baselines.rule.description}`);
    lines.push(`- **Trivial baseline:** ${task.baselines.trivial.description}`);
    lines.push(`- **Gold:** ${task.gold.goldRows}/${task.split.heldOutRows} rows (${(task.gold.coverage * 100).toFixed(1)}%; target ${(GOLD_COVERAGE_TARGET * 100).toFixed(0)}%)`);
    lines.push(`- **Status:** ${task.evaluation.status === "evaluated" ? "evaluated" : `INSUFFICIENT GOLD — ${task.evaluation.reason}`}`);
    lines.push("");
    lines.push("### Why this task matters", "");
    lines.push(task.question, "");
    lines.push("### Blocker", "");
    lines.push(task.gold.recruitmentNeed);
    if (task.gold.blockingRows.length) {
      lines.push("");
      lines.push("First blocking rows:");
      lines.push("");
      lines.push("| reviewId | reason | reviewStatus |");
      lines.push("|---|---|---|");
      for (const row of task.gold.blockingRows) {
        lines.push(`| \`${row.reviewId}\` | ${row.reason} | ${row.reviewStatus} |`);
      }
    }
    lines.push("");
  }
  return `${lines.join("\n").trim()}\n`;
}

function renderDatasheet(report) {
  const summary = report.summary;
  return `# Atlas benchmark v2 — datasheet

_Generated: ${report.generatedAt} · generated by \`npm run build-benchmark-report\`._

## Motivation

Provide an honest evaluation surface for the atlas's three review-driven tasks:
encoding/OCR anomaly triage, cross-dictionary gender conflict adjudication, and
citation-link target verification. Benchmark v1 reported a self-graded
\`overallPrecision\` of 1.0; v2 removes that number and treats two independent
keys as the minimum gold standard.

## Composition

- Tasks: ${summary.taskCount}
- Frozen held-out rows: ${summary.totalHeldOut}
- Training rows: ${summary.totalTrain}
- Double-keyed gold rows: ${summary.totalGold}
- Gold coverage: ${(summary.goldCoverage * 100).toFixed(1)}% (target ${(summary.goldCoverageTarget * 100).toFixed(0)}%)
- Coverage met: ${summary.goldCoverageMet ? "yes" : "no"}
- Honest status: ${summary.status}

Each task's rows are frozen in \`src/data/benchmark/split-manifest.json\` with
the sampling algorithm, seed, and per-stratum counts. No model is trained on
those rows.

## Collection

Rows come from committed review queues under \`src/data/review/\`. Machine values
were produced by the atlas builders; human or pool reviews are overlays keyed by
\`reviewId\`. The pool merge reports under \`data/review/pool_merge/\` are the only
doubly-keyed layer in the repository today.

## Preprocessing

No tokenisation or label remapping is applied to the source rows. Gold labels are
taken verbatim from the pool merge record (or an explicit expert file) and then
checked against the task's closed label vocabulary. Rows whose label is outside
that vocabulary are refused rather than coerced.

## Uses

- Evaluate a rule/parser baseline and a trivial majority baseline on held-out gold.
- Report macro precision/recall/F1, Cohen's kappa, Krippendorff's alpha, and
  bootstrap 95% confidence intervals.
- Track the cost of missing gold explicitly: every task names the keys still needed.

## Not for

- Reporting a score while coverage is below 10\%.
- Calling single-key or agent-reviewed rows "precision".
- Training on the held-out split.
- Treating the negative-control canary as evidence about the data.

## Distribution and maintenance

- Split manifest: \`src/data/benchmark/split-manifest.json\`
- Report: \`src/data/benchmark-report.json\`
- Scoring script: \`scripts/build-benchmark-report.mjs\` (and \`npm run score-benchmark\`)
- Regenerate: \`npm run build-benchmark-report\`
- The manifest is frozen by seed; changing the sample requires a new benchmark
  version and a note in the changelog.

## Licence

${report.license}. See [BENCHMARK_LICENCE.md](./BENCHMARK_LICENCE.md).
`;
}

function renderLicence(report) {
  return `# Atlas benchmark v2 — licence and attribution

_Generated: ${report.generatedAt} · generated by \`npm run build-benchmark-report\`._

- **Dataset licence:** ${report.license} (${report.licenseUrl})
- **Source:** Cologne Digital Sanskrit Lexicon data and the atlas review
  overlays in \`src/data/review/\`.
- **Attribution:** Atlas of the Cologne Digital Sanskrit Lexicons,
  https://sanskrit-lexicon.github.io/csl-atlas/
- **Reviewer attribution:** pool reviewers appear only under pseudonymous keys
  (\`pool-aNN\`). The roster stays off-repo; do not attempt to re-identify it.
- **No csl-orig writes:** the benchmark reads committed derived data and never
  writes to \`csl-orig\`.
- **Share-alike:** redistributions of these derived artifacts must keep
  ${report.license}.
`;
}

function main() {
  const poolIndex = loadPoolIndex();
  const explicitGold = loadExplicitGold();
  const taskSamples = [];
  for (const task of TASKS) {
    const doc = readJson(path.resolve(ROOT, task.source));
    const items = doc.items ?? [];
    const sample = freezeSample(task, items, poolIndex);
    taskSamples.push({ ...task, sampleRows: items, populationSize: items.length, ...sample });
  }

  const manifest = buildSplitManifest(taskSamples);
  const previousManifest = readJsonIfExists(MANIFEST, fs);
  manifest.generatedAt = generatedAtForPayload(previousManifest, manifest);

  const tasks = taskSamples.map(sample => buildTaskReport(
    sample, sample.sampleRows, sample.rows, poolIndex, explicitGold
  ));

  const goldRows = tasks.reduce((sum, task) => sum + task.gold.goldRows, 0);
  const heldOut = tasks.reduce((sum, task) => sum + task.split.heldOutRows, 0);
  const goldCoverage = heldOut ? round(goldRows / heldOut) : 0;
  const negativeControl = negativeControlCanary({ seed: SEED });

  const modelBenchmarks = {};
  if (fs.existsSync(LANGDETECT_METRICS)) {
    const metrics = readJson(LANGDETECT_METRICS);
    modelBenchmarks.langdetectGerman = {
      task: "PWG Sanskrit-vs-German classification (held-out)",
      baselineAccuracy: metrics.baseline_eng_vs_skt?.accuracy ?? null,
      germanAwareAccuracy: metrics.germanAware_san_vs_deu?.accuracy ?? null,
      accuracyLift: metrics.accuracyLift ?? null,
      source: "src/data/external/langdetect-german-metrics.json (#115)",
      caveat: "Trained on PWG's own markup; this evaluates markup consistency, not an external gold standard. Not one of the three v2 tasks."
    };
  }

  const payload = {
    schemaVersion: "2.0.0",
    ...licenseFields(),
    generatedBy: "npm run build-benchmark-report",
    benchmarkVersion: "v2",
    method: "Frozen stratified held-out samples; gold = two independent keys (pool-aNN) or explicit expert labels. No model is trained on the held-out rows. Metrics are macro precision/recall/F1, Cohen's kappa, Krippendorff's alpha (nominal), and seeded bootstrap 95% CIs. Tasks below 10% gold coverage report null scores.",
    scoringScript: "scripts/build-benchmark-report.mjs",
    splitManifest: "src/data/benchmark/split-manifest.json",
    summary: {
      taskCount: tasks.length,
      totalHeldOut: heldOut,
      totalTrain: 0,
      totalGold: goldRows,
      goldCoverage,
      goldCoverageTarget: GOLD_COVERAGE_TARGET,
      goldCoverageMet: goldCoverage >= GOLD_COVERAGE_TARGET,
      noSelfGradedPrecision: true,
      status: goldCoverage >= GOLD_COVERAGE_TARGET
        ? "gold-sufficient"
        : "gold-insufficient-honest-report",
      blockingReason: goldCoverage >= GOLD_COVERAGE_TARGET
        ? null
        : `Only ${goldRows} of ${heldOut} held-out rows are double-keyed (${(goldCoverage * 100).toFixed(1)}%, target ${(GOLD_COVERAGE_TARGET * 100).toFixed(0)}%). The honest result is no task score.`
    },
    tasks,
    negativeControl: {
      description: "A deliberately inverted predictor on a synthetic canary must fail. Pass = the scorer reports macroF1 < 0.5 and chance-corrected agreement <= 0.",
      ...negativeControl,
      realDataStatus: "not_evaluable_insufficient_gold"
    },
    reviewOverlayCounts: {
      note: "Counts only. These rows are not gold and no precision is computed from them.",
      reviewedRowsWithoutSecondKey: tasks.reduce((sum, task) => sum + task.gold.rowsSingleKey, 0),
      unkeyedRows: tasks.reduce((sum, task) => sum + task.gold.rowsUnkeyed, 0)
    },
    modelBenchmarks,
    limitations: [
      "No task score is reported today: zero of the three frozen samples contain a double-keyed gold row.",
      "A review by the session or agent that produced the machine value is not an independent key; v1's 147 self-reviewed rows are excluded by construction.",
      "The negative control is machinery verification on synthetic rows, not benchmark evidence about the data.",
      "Pool reviewers are pseudonymous; agreement cannot be corrected for a shared prior if both keys saw the public repo.",
      "The frozen sample is drawn now; adding gold later must not change the sample without a new benchmark version."
    ]
  };

  payload.generatedAt = generatedAtForPayload(readJsonIfExists(OUTPUT, fs), payload);
  fs.mkdirSync(MANIFEST_DIR, { recursive: true });
  fs.writeFileSync(MANIFEST, `${JSON.stringify(manifest, null, 2)}\n`);
  fs.writeFileSync(OUTPUT, `${JSON.stringify(payload, null, 2)}\n`);
  fs.writeFileSync(TASK_CARDS, renderTaskCards(payload));
  fs.writeFileSync(DATASHEET, renderDatasheet(payload));
  fs.writeFileSync(LICENCE, renderLicence(payload));

  console.log(`Benchmark v2: ${payload.summary.taskCount} tasks, ${heldOut} held-out rows, ${goldRows} double-keyed gold (${(goldCoverage * 100).toFixed(1)}%).`);
  for (const task of payload.tasks) {
    console.log(`  ${task.taskId.padEnd(22)} held-out ${String(task.split.heldOutRows).padStart(3)} · gold ${String(task.gold.goldRows).padStart(3)} · ${task.evaluation.status}`);
  }
  console.log(`  negative control (synthetic canary): ${payload.negativeControl.passes ? "fails as expected" : "FAILED — SCORER BUG"}`);
  console.log(`  status: ${payload.summary.status}`);
  console.log(`Wrote ${path.relative(ROOT, OUTPUT)} and ${path.relative(ROOT, MANIFEST)}`);
}

export { TASKS, loadPoolIndex, loadExplicitGold, goldLabelFor, readJson };

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
