// Shared helpers for the H7104 cross-dictionary defgen evaluation.

import crypto from "node:crypto";
import fs from "node:fs";

export function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

export function readJsonl(file) {
  return fs.readFileSync(file, "utf8").split(/\r?\n/).filter(Boolean).map(line => JSON.parse(line));
}

export function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

export function hashKey(seed, value) {
  return crypto.createHash("sha256").update(`${seed}:${value}`).digest("hex");
}

export function round(value, digits = 4) {
  return value == null || !Number.isFinite(value) ? null : Number(value.toFixed(digits));
}

export function mean(values) {
  const xs = values.filter(v => Number.isFinite(v));
  return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null;
}

export function csvEscape(value) {
  if (value == null) return "";
  const s = String(value);
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

export function parseCsv(text) {
  const lines = text.replace(/^\uFEFF/, "").split(/\r?\n/).filter(line => line.length);
  if (!lines.length) return [];
  const parseLine = line => {
    const out = [];
    let cell = "";
    let quoted = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        if (quoted && line[i + 1] === '"') { cell += '"'; i++; }
        else quoted = !quoted;
      } else if (ch === "," && !quoted) {
        out.push(cell); cell = "";
      } else cell += ch;
    }
    out.push(cell);
    return out;
  };
  const header = parseLine(lines[0]);
  return lines.slice(1).map(line => Object.fromEntries(header.map((k, i) => [k, parseLine(line)[i] ?? ""])));
}

export function parseTsv(text) {
  const lines = text.replace(/^\uFEFF/, "").split(/\r?\n/).filter(line => line.length);
  const header = lines[0].split("\t");
  return lines.slice(1).map(line => Object.fromEntries(header.map((k, i) => [k, line.split("\t")[i] ?? ""])));
}

export function glossSegments(gloss) {
  return (gloss || "")
    .split(/\s*[|;]\s*/)
    .map(s => s.trim())
    .filter(Boolean);
}

export function quadraticWeightedKappa(pairs) {
  const n = pairs.length;
  if (!n) return { kappa: null, n: 0 };
  const observed = Array.from({ length: 6 }, () => Array(6).fill(0));
  const expected = Array.from({ length: 6 }, () => Array(6).fill(0));
  const aCounts = Array(6).fill(0);
  const bCounts = Array(6).fill(0);
  for (const [a, b] of pairs) {
    observed[a][b]++;
    aCounts[a]++;
    bCounts[b]++;
  }
  let observedDisagree = 0;
  let expectedDisagree = 0;
  for (let i = 0; i <= 5; i++) {
    for (let j = 0; j <= 5; j++) {
      expected[i][j] = (aCounts[i] * bCounts[j]) / n;
      const w = ((i - j) * (i - j)) / 25;
      observedDisagree += w * observed[i][j];
      expectedDisagree += w * expected[i][j];
    }
  }
  const kappa = expectedDisagree === 0 ? null : 1 - observedDisagree / expectedDisagree;
  return { kappa: round(kappa), n };
}

export function pearson(pairs) {
  const n = pairs.length;
  if (n < 2) return null;
  const ma = mean(pairs.map(p => p[0]));
  const mb = mean(pairs.map(p => p[1]));
  let num = 0, da = 0, db = 0;
  for (const [a, b] of pairs) {
    num += (a - ma) * (b - mb);
    da += (a - ma) ** 2;
    db += (b - mb) ** 2;
  }
  return da && db ? round(num / Math.sqrt(da * db)) : null;
}

export function ranks(values) {
  const order = values.map((v, i) => [v, i]).sort((a, b) => a[0] - b[0]);
  const out = Array(values.length);
  for (let i = 0; i < order.length;) {
    let j = i;
    while (j + 1 < order.length && order[j + 1][0] === order[i][0]) j++;
    const rank = (i + j) / 2 + 1;
    for (let k = i; k <= j; k++) out[order[k][1]] = rank;
    i = j + 1;
  }
  return out;
}

export function spearman(pairs) {
  if (pairs.length < 2) return null;
  const ra = ranks(pairs.map(p => p[0]));
  const rb = ranks(pairs.map(p => p[1]));
  return pearson(ra.map((v, i) => [v, rb[i]]));
}

export function decideVerdict(byArm, calibration) {
  const best = Object.entries(byArm)
    .filter(([arm]) => arm !== "A0_random_floor")
    .sort((a, b) => (b[1].distinction_preserved_adequate_rate ?? 0) - (a[1].distinction_preserved_adequate_rate ?? 0))[0];
  const preservation = best?.[1]?.distinction_preserved_adequate_rate ?? 0;
  const kappa = calibration.quadratic_weighted_kappa;
  const floor = byArm.A0_random_floor?.distinction_preserved_adequate_rate ?? 0;
  const bestF1 = best?.[1]?.mean_count_f1 ?? 0;
  const floorF1 = byArm.A0_random_floor?.mean_count_f1 ?? 0;
  const reasons = [];
  if (preservation <= floor) reasons.push(`best arm ${best?.[0]} does not beat the random-floor adequacy-gated preservation rate (${preservation} vs ${floor})`);
  if (preservation < 0.5) reasons.push(`adequacy-gated sense-distinction preservation is below the pre-registered 0.5 bar (${preservation})`);
  if (bestF1 <= floorF1) reasons.push(`best arm ${best?.[0]} does not beat the random-floor sense-count F1 (${bestF1} vs ${floorF1})`);
  if (kappa == null) reasons.push("no human judge calibration available, so judge adequacy cannot be trusted");
  else if (kappa < 0.4) reasons.push(`judge-vs-human quadratic weighted kappa is below 0.4 (${kappa})`);
  const go = reasons.length === 0;
  return {
    decision: go ? "GO" : "NO-GO",
    bestArm: best?.[0] ?? null,
    bestPreservationRate: preservation,
    randomFloorPreservationRate: floor,
    bestCountF1: bestF1,
    randomFloorCountF1: floorF1,
    judgeHumanKappa: kappa,
    reasons: go ? ["best arm clears the random floor on adequacy-gated preservation and count F1, clears the 0.5 preservation bar, and judge calibration clears kappa 0.4"] : reasons,
    stoppingRule: "Stop after 6 tries and publish the null if the best arm does not clear the floor/0.5 bar or judge-human kappa stays below 0.4. No generated definition is promoted into dictionary content by this lane."
  };
}
