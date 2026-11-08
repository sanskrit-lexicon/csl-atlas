// Scoring primitives for the Atlas benchmark v2 (H7099).
//
// Deliberately small and dependency-free so the scoring path can be read and
// tested without the review builders. Every statistic takes explicit labels;
// nothing here reads a review file, and nothing here treats a self-reviewed
// row as gold.

export const BOOTSTRAP_RESAMPLES = 2000;
export const DEFAULT_SEED = 20261019;

export function mulberry32(seed) {
  let a = seed >>> 0;
  return function next() {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function macroScores(predictions, golds, labels) {
  if (predictions.length !== golds.length) {
    throw new Error("predictions and gold labels must be the same length");
  }
  const perLabel = {};
  const present = [];
  for (const label of labels) {
    let tp = 0;
    let fp = 0;
    let fn = 0;
    for (let i = 0; i < golds.length; i += 1) {
      const gold = golds[i];
      const pred = predictions[i];
      if (gold === label && pred === label) tp += 1;
      else if (gold !== label && pred === label) fp += 1;
      else if (gold === label && pred !== label) fn += 1;
    }
    const precision = tp + fp === 0 ? null : tp / (tp + fp);
    const recall = tp + fn === 0 ? null : tp / (tp + fn);
    const f1 = precision == null || recall == null || precision + recall === 0
      ? (precision == null || recall == null ? null : 0)
      : (2 * precision * recall) / (precision + recall);
    perLabel[label] = { tp, fp, fn, precision, recall, f1 };
    if (tp + fp + fn > 0) present.push(label);
  }
  const mean = values => {
    const usable = values.filter(value => value != null);
    return usable.length ? usable.reduce((sum, value) => sum + value, 0) / usable.length : null;
  };
  return {
    n: golds.length,
    perLabel,
    macroPrecision: mean(present.map(label => perLabel[label].precision)),
    macroRecall: mean(present.map(label => perLabel[label].recall)),
    macroF1: mean(present.map(label => perLabel[label].f1)),
    accuracy: golds.length
      ? predictions.filter((pred, i) => pred === golds[i]).length / golds.length
      : null
  };
}

export function cohenKappa(pairs) {
  const n = pairs.length;
  if (!n) return null;
  const observed = pairs.filter(([a, b]) => a === b).length / n;
  const countsA = new Map();
  const countsB = new Map();
  for (const [a, b] of pairs) {
    countsA.set(a, (countsA.get(a) || 0) + 1);
    countsB.set(b, (countsB.get(b) || 0) + 1);
  }
  const categories = new Set([...countsA.keys(), ...countsB.keys()]);
  let expected = 0;
  for (const category of categories) {
    expected += ((countsA.get(category) || 0) / n) * ((countsB.get(category) || 0) / n);
  }
  if (Math.abs(1 - expected) < 1e-12) return null;
  return (observed - expected) / (1 - expected);
}

export function krippendorffAlphaNominal(units) {
  const coincidence = new Map();
  let total = 0;
  const add = (a, b, value) => {
    const key = `${a}\u0000${b}`;
    coincidence.set(key, (coincidence.get(key) || 0) + value);
  };
  for (const labels of units) {
    const m = labels.length;
    if (m < 2) continue;
    const counts = new Map();
    for (const label of labels) counts.set(label, (counts.get(label) || 0) + 1);
    const denominator = m - 1;
    for (const [a, countA] of counts) {
      for (const [b, countB] of counts) {
        add(a, b, a === b ? (countA * (countA - 1)) / denominator : (countA * countB) / denominator);
      }
    }
    total += m;
  }
  if (total < 2) return null;
  const categories = new Set();
  for (const key of coincidence.keys()) {
    const [a, b] = key.split("\u0000");
    categories.add(a);
    categories.add(b);
  }
  const marginals = new Map();
  for (const category of categories) {
    let sum = 0;
    for (const other of categories) sum += coincidence.get(`${category}\u0000${other}`) || 0;
    marginals.set(category, sum);
  }
  let diagonal = 0;
  for (const category of categories) diagonal += coincidence.get(`${category}\u0000${category}`) || 0;
  const observed = (total - diagonal) / total;
  const expectedNumerator = total * (total - 1) -
    [...marginals.values()].reduce((sum, value) => sum + value * (value - 1), 0);
  const expected = expectedNumerator / (total * (total - 1));
  if (expected === 0) return null;
  return 1 - observed / expected;
}

function percentile(sorted, fraction) {
  return sorted[Math.min(sorted.length - 1, Math.floor(fraction * sorted.length))];
}

export function bootstrapCI(rows, statistic, { seed = DEFAULT_SEED, resamples = BOOTSTRAP_RESAMPLES } = {}) {
  if (rows.length < 2) return null;
  const random = mulberry32(seed);
  const samples = [];
  for (let r = 0; r < resamples; r += 1) {
    const draw = [];
    for (let i = 0; i < rows.length; i += 1) draw.push(rows[Math.floor(random() * rows.length)]);
    const value = statistic(draw);
    if (value != null && Number.isFinite(value)) samples.push(value);
  }
  if (samples.length < resamples / 2) return null;
  samples.sort((a, b) => a - b);
  return [round(percentile(samples, 0.025)), round(percentile(samples, 0.975))];
}

export function round(value, digits = 4) {
  return value == null ? null : Number(value.toFixed(digits));
}

export function evaluatePredictions(predictions, golds, labels, { seed = DEFAULT_SEED } = {}) {
  const rows = golds.map((gold, i) => ({ prediction: predictions[i], gold }));
  const base = macroScores(predictions, golds, labels);
  const pairs = rows.map(row => [row.prediction, row.gold]);
  const alphaUnits = rows.map(row => [row.prediction, row.gold]);
  return {
    n: rows.length,
    precision: round(base.macroPrecision),
    recall: round(base.macroRecall),
    f1: round(base.macroF1),
    accuracy: round(base.accuracy),
    cohenKappa: round(cohenKappa(pairs)),
    krippendorffAlpha: round(krippendorffAlphaNominal(alphaUnits)),
    bootstrapCI95: {
      macroF1: bootstrapCI(rows, draw => macroScores(
        draw.map(row => row.prediction), draw.map(row => row.gold), labels
      ).macroF1, { seed }),
      krippendorffAlpha: bootstrapCI(
        rows,
        draw => krippendorffAlphaNominal(draw.map(row => [row.prediction, row.gold])),
        { seed }
      )
    },
    perLabel: Object.fromEntries(Object.entries(base.perLabel).map(([label, value]) => [
      label,
      {
        support: value.tp + value.fn,
        precision: round(value.precision),
        recall: round(value.recall),
        f1: round(value.f1)
      }
    ]))
  };
}

// Inverted-oracle canary: 40 synthetic binary rows where every prediction is
// deliberately wrong. A scorer that reports anything but a failing score here
// is broken. This is machinery verification, never benchmark evidence.
export function negativeControlCanary({ seed = DEFAULT_SEED } = {}) {
  const labels = ["positive", "negative"];
  const predictions = [];
  const golds = [];
  for (let i = 0; i < 40; i += 1) {
    const gold = i % 2 === 0 ? "positive" : "negative";
    golds.push(gold);
    predictions.push(gold === "positive" ? "negative" : "positive");
  }
  const scores = evaluatePredictions(predictions, golds, labels, { seed });
  return {
    kind: "inverted-oracle synthetic canary",
    rows: 40,
    expected: "macroF1 < 0.5 and chance-corrected agreement <= 0",
    observed: { macroF1: scores.f1, cohenKappa: scores.cohenKappa, krippendorffAlpha: scores.krippendorffAlpha },
    passes: scores.f1 != null && scores.f1 < 0.5 &&
      (scores.cohenKappa == null || scores.cohenKappa <= 0) &&
      (scores.krippendorffAlpha == null || scores.krippendorffAlpha <= 0)
  };
}
