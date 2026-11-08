// H7101 — score candidate-lane outputs against the frozen 500-row sample.
//
// Abstention is first-class: an abstained row is not a prediction. It lowers
// coverage but never silently becomes a false positive. The report therefore
// carries both all-row accuracy (abstain = wrong) and selective accuracy
// (abstain = excluded), plus per-class precision/recall/F1 over the five labels.
//
// Usage: node scripts/score-llm-candidate-lane.mjs [--out PATH]

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { generatedAtNow, licenseFields, readJsonIfExists } from "./lib/dataset-meta.mjs";

export const LANE_DIR = path.join("data", "llm-candidate-lane");
export const SAMPLE_PATH = path.join(LANE_DIR, "sample-500.jsonl");
export const RULE_OUTPUT_PATH = path.join(LANE_DIR, "outputs", "rule-baseline.jsonl");
export const LLM_OUTPUT_PATH = path.join(LANE_DIR, "outputs", "llm-abstain.jsonl");
export const SCORES_PATH = path.join(LANE_DIR, "scores.json");

export const EDIT_TYPES = Object.freeze([
  "ocr-error",
  "sense-split",
  "source-mismatch",
  "markup-normalization",
  "no-correction"
]);

export const TARGET_ERROR_TYPES = Object.freeze(["ocr-error", "sense-split", "source-mismatch"]);

export function readJsonl(filePath) {
  return fs.readFileSync(filePath, "utf8").split(/\r?\n/).filter(Boolean).map(line => JSON.parse(line));
}

function sha256File(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function ratio(numerator, denominator) {
  return denominator ? Number((numerator / denominator).toFixed(4)) : null;
}

// ---------------------------------------------------------------------------
// Agreement and uncertainty
//
// The frozen sample carries ONE gold label per row, so inter-human kappa /
// Krippendorff alpha cannot be computed here: alpha needs two independent
// rater columns. What can be computed is the agreement between a lane and the
// gold label (Cohen's kappa on non-abstained rows). The human-key gap is
// reported as a named null, never silently filled (see report §Limitations).
//
// CIs are percentile bootstrap over the 500 rows, seeded so that re-running
// the scorer on the same committed outputs produces byte-identical numbers.
// The same seed and the same row order give both lanes the same resample
// indices, i.e. a paired bootstrap.
// ---------------------------------------------------------------------------

export const BOOTSTRAP_ITERATIONS = 2000;
export const BOOTSTRAP_SEED = "H7101-2026-10-19";

function seedFromString(value) {
  let hash = 2166136261;
  for (let i = 0; i < value.length; i += 1) {
    hash = Math.imul(hash ^ value.charCodeAt(i), 16777619);
  }
  return hash >>> 0;
}

function mulberry32(seed) {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = Math.imul(state ^ (state >>> 15), 1 | state);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function f1Of(tp, fp, fn) {
  return tp + fp + fn ? (2 * tp) / (2 * tp + fp + fn) : null;
}

/**
 * Compute the comparison metrics from `{gold, predicted}` pairs, where
 * `predicted === null` means abstain (or missing, which scores the same way).
 * This is the resampling kernel for the bootstrap; `scoreOutputs` remains the
 * authoritative point estimate and the test suite locks the two together.
 */
export function metricsFromPairs(pairs) {
  const n = pairs.length;
  const tp = emptyCounts();
  const fp = emptyCounts();
  const fn = emptyCounts();
  let correct = 0;
  let selectiveN = 0;
  let targetTP = 0;
  let targetFP = 0;
  let targetFN = 0;
  let anyTP = 0;
  let anyFP = 0;
  let anyFN = 0;
  for (const { gold, predicted } of pairs) {
    if (predicted !== null) {
      selectiveN += 1;
      if (predicted === gold) correct += 1;
    }
    for (const type of EDIT_TYPES) {
      if (predicted !== null && predicted === type) {
        if (gold === type) tp[type] += 1;
        else fp[type] += 1;
      }
      if (gold === type && predicted !== type) fn[type] += 1;
    }
    const goldTarget = TARGET_ERROR_TYPES.includes(gold);
    const predTarget = predicted !== null && TARGET_ERROR_TYPES.includes(predicted);
    if (goldTarget && predTarget) targetTP += 1;
    else if (!goldTarget && predTarget) targetFP += 1;
    else if (goldTarget && !predTarget) targetFN += 1;
    const goldAny = gold !== "no-correction";
    const predAny = predicted !== null && predicted !== "no-correction";
    if (goldAny && predAny) anyTP += 1;
    else if (!goldAny && predAny) anyFP += 1;
    else if (goldAny && !predAny) anyFN += 1;
  }
  const macroF1AbstainZero = EDIT_TYPES.reduce(
    (sum, type) => sum + (f1Of(tp[type], fp[type], fn[type]) ?? 0),
    0
  ) / EDIT_TYPES.length;
  return {
    n,
    coverage: n ? selectiveN / n : null,
    selectiveAccuracy: selectiveN ? correct / selectiveN : null,
    accuracyAll: n ? correct / n : null,
    macroF1AbstainZero: Number(macroF1AbstainZero.toFixed(4)),
    targetErrorF1: f1Of(targetTP, targetFP, targetFN),
    anyCorrectionF1: f1Of(anyTP, anyFP, anyFN)
  };
}

function percentile(values, p) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const position = (sorted.length - 1) * p;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  if (lower === upper) return sorted[lower];
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (position - lower);
}

const CI_METRICS = Object.freeze([
  "coverage",
  "selectiveAccuracy",
  "accuracyAll",
  "macroF1AbstainZero",
  "targetErrorF1",
  "anyCorrectionF1"
]);

/**
 * Paired percentile-bootstrap 95 % confidence intervals over the sampled rows.
 * Null point estimates stay null; resamples in which a metric is undefined are
 * skipped rather than imputed.
 */
export function bootstrapCI(pairs, { iterations = BOOTSTRAP_ITERATIONS, seed = BOOTSTRAP_SEED } = {}) {
  if (!pairs.length) return null;
  const random = mulberry32(seedFromString(seed));
  const draws = Object.fromEntries(CI_METRICS.map(metric => [metric, []]));
  const resample = new Array(pairs.length);
  for (let iteration = 0; iteration < iterations; iteration += 1) {
    for (let i = 0; i < pairs.length; i += 1) {
      resample[i] = pairs[Math.floor(random() * pairs.length)];
    }
    const metrics = metricsFromPairs(resample);
    for (const metric of CI_METRICS) {
      if (metrics[metric] !== null) draws[metric].push(metrics[metric]);
    }
  }
  const intervals = {};
  for (const metric of CI_METRICS) {
    const values = draws[metric];
    intervals[metric] = values.length
      ? {
        level: 0.95,
        low: Number(percentile(values, 0.025).toFixed(4)),
        high: Number(percentile(values, 0.975).toFixed(4)),
        n: values.length
      }
      : null;
  }
  return {
    method: "paired percentile bootstrap over evaluated rows",
    iterations,
    seed,
    intervals
  };
}

/**
 * Cohen's kappa between a lane's non-abstained predictions and the gold label.
 * Abstained rows are excluded (they are not predictions); `n` is reported.
 */
export function cohenKappa(pairs) {
  const valid = pairs.filter(pair => pair.predicted !== null);
  if (!valid.length) return { kappa: null, n: 0, observed: null, expected: null };
  const goldCounts = new Map();
  const predCounts = new Map();
  let observed = 0;
  for (const { gold, predicted } of valid) {
    goldCounts.set(gold, (goldCounts.get(gold) ?? 0) + 1);
    predCounts.set(predicted, (predCounts.get(predicted) ?? 0) + 1);
    if (gold === predicted) observed += 1;
  }
  const total = valid.length;
  let expected = 0;
  for (const label of new Set([...goldCounts.keys(), ...predCounts.keys()])) {
    expected += ((goldCounts.get(label) ?? 0) / total) * ((predCounts.get(label) ?? 0) / total);
  }
  const kappa = expected === 1 ? null : (observed / total - expected) / (1 - expected);
  return {
    kappa: kappa === null ? null : Number(kappa.toFixed(4)),
    n: total,
    observed: Number((observed / total).toFixed(4)),
    expected: Number(expected.toFixed(4))
  };
}

/** Build `{gold, predicted}` pairs for a frozen sample and one output file. */
export function pairsFrom(sample, records) {
  const byId = new Map(records.map(record => [record.id, record]));
  return sample.map(row => {
    const record = byId.get(row.id);
    const prediction = record?.prediction ?? {};
    const abstain = !record || prediction.abstain !== false || prediction.editType === null;
    return { gold: row.gold.editType, predicted: abstain ? null : prediction.editType };
  });
}

/**
 * Paired bootstrap CI of `llm - baseline` for one metric. Both lanes are
 * resampled with the same indices, so the delta distribution accounts for the
 * fact that they were scored on the same rows.
 */
export function pairedBootstrapDelta(baselinePairs, llmPairs, metric = "macroF1AbstainZero", {
  iterations = BOOTSTRAP_ITERATIONS,
  seed = BOOTSTRAP_SEED
} = {}) {
  if (baselinePairs.length !== llmPairs.length || !baselinePairs.length) return null;
  const random = mulberry32(seedFromString(seed));
  const draws = [];
  const resampleBaseline = new Array(baselinePairs.length);
  const resampleLlm = new Array(llmPairs.length);
  for (let iteration = 0; iteration < iterations; iteration += 1) {
    for (let i = 0; i < baselinePairs.length; i += 1) {
      const index = Math.floor(random() * baselinePairs.length);
      resampleBaseline[i] = baselinePairs[index];
      resampleLlm[i] = llmPairs[index];
    }
    const baselineValue = metricsFromPairs(resampleBaseline)[metric];
    const llmValue = metricsFromPairs(resampleLlm)[metric];
    if (baselineValue !== null && llmValue !== null) draws.push(llmValue - baselineValue);
  }
  if (!draws.length) return null;
  const baselinePoint = metricsFromPairs(baselinePairs)[metric];
  const llmPoint = metricsFromPairs(llmPairs)[metric];
  const low = Number(percentile(draws, 0.025).toFixed(4));
  const high = Number(percentile(draws, 0.975).toFixed(4));
  return {
    metric,
    delta: baselinePoint !== null && llmPoint !== null
      ? Number((llmPoint - baselinePoint).toFixed(4))
      : null,
    level: 0.95,
    low,
    high,
    excludesZero: low > 0 || high < 0,
    positive: low > 0,
    iterations,
    seed
  };
}

export const ALPHA_REASON =
  "not computable: Krippendorff alpha needs two independent human rater columns; " +
  "the frozen sample carries one gold label per row (see report §Limitations).";

function emptyCounts() {
  return Object.fromEntries(EDIT_TYPES.map(type => [type, 0]));
}

/**
 * Score one output file against the sample.
 *
 * `predictions` is a Map or array of records with `id` and
 * `prediction.{editType, abstain, confidence}`.
 */
export function scoreOutputs(sample, records) {
  const byId = new Map(records.map(record => [record.id, record]));
  const confusion = {};
  for (const gold of EDIT_TYPES) {
    confusion[gold] = emptyCounts();
    confusion[gold].__abstain = 0;
  }
  const predictedCounts = emptyCounts();
  let abstained = 0;
  let correct = 0;
  let selectiveN = 0;
  let selectiveCorrect = 0;
  let targetTP = 0;
  let targetFP = 0;
  let targetFN = 0;
  let anyTP = 0;
  let anyFP = 0;
  let anyFN = 0;
  const confidenceBins = new Map();
  const abstentionByGold = emptyCounts();
  const missing = [];
  const pairs = [];

  for (const row of sample) {
    const gold = row.gold.editType;
    const record = byId.get(row.id);
    if (!record) {
      missing.push(row.id);
      pairs.push({ gold, predicted: null });
      continue;
    }
    const prediction = record.prediction ?? {};
    const isAbstain = prediction.abstain !== false || prediction.editType === null;
    if (isAbstain) {
      abstained += 1;
      confusion[gold].__abstain += 1;
      abstentionByGold[gold] += 1;
      pairs.push({ gold, predicted: null });
      continue;
    }
    const predicted = prediction.editType;
    pairs.push({ gold, predicted });
    if (predictedCounts[predicted] === undefined) {
      confusion[gold][String(predicted)] = (confusion[gold][String(predicted)] || 0) + 1;
    } else {
      predictedCounts[predicted] += 1;
    }
    confusion[gold][predicted] = (confusion[gold][predicted] || 0) + 1;
    selectiveN += 1;
    if (predicted === gold) {
      selectiveCorrect += 1;
      correct += 1;
    }

    const goldTarget = TARGET_ERROR_TYPES.includes(gold);
    const predTarget = TARGET_ERROR_TYPES.includes(predicted);
    if (goldTarget && predTarget) targetTP += 1;
    else if (!goldTarget && predTarget) targetFP += 1;
    else if (goldTarget && !predTarget) targetFN += 1;

    const goldAny = gold !== "no-correction";
    const predAny = predicted !== "no-correction";
    if (goldAny && predAny) anyTP += 1;
    else if (!goldAny && predAny) anyFP += 1;
    else if (goldAny && !predAny) anyFN += 1;

    const confidence = Number(prediction.confidence ?? 0);
    const lower = Math.min(0.9, Math.max(0.5, Math.floor(confidence * 10) / 10));
    const key = `${lower.toFixed(1)}-${(lower + 0.1).toFixed(1)}`;
    const bin = confidenceBins.get(key) ?? { bin: key, n: 0, correct: 0 };
    bin.n += 1;
    if (predicted === gold) bin.correct += 1;
    confidenceBins.set(key, bin);
  }

  const perClass = {};
  for (const type of EDIT_TYPES) {
    const tp = confusion[type]?.[type] ?? 0;
    const fp = EDIT_TYPES.reduce((sum, gold) => sum + (gold === type ? 0 : confusion[gold]?.[type] ?? 0), 0);
    const fn = EDIT_TYPES.reduce((sum, pred) => sum + (pred === type ? 0 : confusion[type]?.[pred] ?? 0), 0);
    perClass[type] = {
      support: sample.filter(row => row.gold.editType === type).length,
      precision: ratio(tp, tp + fp),
      recall: ratio(tp, tp + fn),
      f1: tp + fp + fn ? Number(((2 * tp) / (2 * tp + fp + fn)).toFixed(4)) : null,
      predicted: predictedCounts[type]
    };
  }

  const definedF1 = Object.values(perClass).map(item => item.f1).filter(value => value !== null);
  const macroF1 = definedF1.length
    ? Number((definedF1.reduce((sum, value) => sum + value, 0) / definedF1.length).toFixed(4))
    : null;
  const allMacroF1 = Object.values(perClass).reduce((sum, item) => sum + (item.f1 ?? 0), 0) / EDIT_TYPES.length;

  const total = sample.length;
  const agreement = cohenKappa(pairs);
  return {
    total,
    coverage: ratio(selectiveN, total),
    abstentionRate: ratio(abstained, total),
    abstained,
    missing,
    accuracyAll: ratio(correct, total),
    selectiveAccuracy: ratio(selectiveCorrect, selectiveN),
    macroF1,
    macroF1AbstainZero: Number(allMacroF1.toFixed(4)),
    perClass,
    confusion,
    abstentionByGold,
    binaryTargetError: {
      precision: ratio(targetTP, targetTP + targetFP),
      recall: ratio(targetTP, targetTP + targetFN),
      f1: targetTP + targetFP + targetFN
        ? Number(((2 * targetTP) / (2 * targetTP + targetFP + targetFN)).toFixed(4))
        : null,
      tp: targetTP,
      fp: targetFP,
      fn: targetFN
    },
    binaryAnyCorrection: {
      precision: ratio(anyTP, anyTP + anyFP),
      recall: ratio(anyTP, anyTP + anyFN),
      f1: anyTP + anyFP + anyFN
        ? Number(((2 * anyTP) / (2 * anyTP + anyFP + anyFN)).toFixed(4))
        : null,
      tp: anyTP,
      fp: anyFP,
      fn: anyFN
    },
    confidenceBins: [...confidenceBins.values()]
      .map(bin => ({ ...bin, accuracy: ratio(bin.correct, bin.n) }))
      .sort((a, b) => a.bin.localeCompare(b.bin)),
    agreement: {
      modelVsGoldKappa: agreement.kappa,
      modelVsGoldN: agreement.n,
      observedAgreement: agreement.observed,
      expectedAgreement: agreement.expected,
      alpha: null,
      alphaReason: ALPHA_REASON,
      humanInterRater: {
        available: false,
        reason: "one gold label per row; the second independent human label required by H7101 is not in the frozen sample"
      }
    },
    bootstrap: bootstrapCI(pairs)
  };
}

function readMetadata(outputPath, records) {
  const raw = fs.readFileSync(outputPath, "utf8").split(/\r?\n/).filter(Boolean);
  const first = raw[0] ? JSON.parse(raw[0]) : null;
  return {
    path: outputPath.split(path.sep).join("/"),
    sha256: sha256File(outputPath),
    recordCount: records.length,
    prompt: first?.prompt ?? null,
    model: first?.model ?? null,
    runStatus: records.some(record => record.prediction?.abstain) ? "has-abstentions" : "complete"
  };
}

function verdictFor(baseline, llm) {
  if (llm.coverage === 0) {
    return {
      verdict: "NO-GO",
      status: "not-run",
      reason: "The LLM lane produced no predictions (coverage 0); no evidence of gain over the rule baseline. Do not expand or promote."
    };
  }
  const gain = llm.macroF1AbstainZero - baseline.macroF1AbstainZero;
  if (gain <= 0) {
    return {
      verdict: "NO-GO",
      status: "scored",
      reason: `LLM macro-F1 ${llm.macroF1AbstainZero} does not beat the rule baseline ${baseline.macroF1AbstainZero} (delta ${gain.toFixed(4)}). Publish the null.`
    };
  }
  return {
    verdict: "CONDITIONAL-GO",
    status: "scored",
    reason: `LLM macro-F1 ${llm.macroF1AbstainZero} beats the rule baseline ${baseline.macroF1AbstainZero} (delta ${gain.toFixed(4)}). Human adjudication of candidate rows is still required before any promotion.`
  };
}

function main() {
  const args = process.argv.slice(2);
  const outIndex = args.indexOf("--out");
  const outPath = outIndex >= 0 ? args[outIndex + 1] : SCORES_PATH;
  const llmIndex = args.indexOf("--llm");
  const llmPath = llmIndex >= 0 ? args[llmIndex + 1] : LLM_OUTPUT_PATH;

  const sample = readJsonl(SAMPLE_PATH);
  const rule = readJsonl(RULE_OUTPUT_PATH);
  const llm = readJsonl(llmPath);

  const baselineScores = scoreOutputs(sample, rule);
  const llmScores = scoreOutputs(sample, llm);
  const baselineMeta = readMetadata(RULE_OUTPUT_PATH, rule);
  const llmMeta = readMetadata(llmPath, llm);
  const bySource = {};
  for (const source of ["correction-loci", "review-queue"]) {
    const subset = sample.filter(row => row.source === source);
    const subsetIds = new Set(subset.map(row => row.id));
    bySource[source] = {
      rows: subset.length,
      baseline: scoreOutputs(subset, rule.filter(record => subsetIds.has(record.id))),
      llm: scoreOutputs(subset, llm.filter(record => subsetIds.has(record.id)))
    };
  }

  const previous = readJsonIfExists(outPath, fs);
  const comparison = verdictFor(baselineScores, llmScores);
  comparison.pairedBootstrap = pairedBootstrapDelta(
    pairsFrom(sample, rule),
    pairsFrom(sample, llm),
    "macroF1AbstainZero"
  );
  const payload = {
    schemaVersion: "1.0.0",
    ...licenseFields(),
    dataset: "h7101_llm_candidate_scores",
    generatedAt: generatedAtNow(),
    sample: {
      path: SAMPLE_PATH.split(path.sep).join("/"),
      sha256: sha256File(SAMPLE_PATH),
      rows: sample.length
    },
    labels: {
      types: EDIT_TYPES,
      targetErrorTypes: TARGET_ERROR_TYPES,
      goldProvenance: {
        "correction-loci": "weak-diff-label (human correction event, type derived from the old/new diff)",
        "review-queue": "human-reviewed (H5 reviewedValue)"
      }
    },
    baseline: { ...baselineScores, ...baselineMeta },
    llm: { ...llmScores, ...llmMeta },
    bySource,
    comparison,
    stoppingRule: {
      maxPromptTries: 6,
      stopIf: "no gain over the rule baseline on this 500-row eval",
      maxFullCorpusRuns: 0,
      promotion: "none; candidates remain machine-candidate until human review"
    }
  };
  if (previous?.generatedAt && previous.sample?.sha256 === payload.sample.sha256 &&
      previous.baseline?.sha256 === payload.baseline.sha256 && previous.llm?.sha256 === payload.llm.sha256) {
    payload.generatedAt = previous.generatedAt;
  }
  fs.writeFileSync(outPath, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(JSON.stringify({
    baselineMacroF1: payload.baseline.macroF1AbstainZero,
    llmMacroF1: payload.llm.macroF1AbstainZero,
    llmCoverage: payload.llm.coverage,
    verdict: payload.comparison.verdict,
    reason: payload.comparison.reason
  }, null, 2));
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
