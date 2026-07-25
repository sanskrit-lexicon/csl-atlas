// Build the Heaps-saturation packet (PH8 HEAP-SAT, H1576; agenda backlog #5):
// accumulate the SanskritLexicography union headword backbone dictionary by
// dictionary in publication order (dates from dictionary_inventory.csv) and
// test whether union growth follows a saturating Heaps-type law, with
// specialised lexica (inventory family `Specialized`: INM, VEI, BHS) arriving
// as breaks above the fitted curve.
//
// Method: every union lemma's dictionary set is folded to a 15-bit mask, so
// cumulative-novelty curves under ANY dictionary ordering are exact
// mask-arithmetic (no per-lemma rescan per permutation). Heaps K*n^beta is an
// OLS fit on log V vs log n (n = cumulative headword tokens scanned, V =
// cumulative distinct lemmas). The specialised-break claim gets two nulls:
// an order-permutation null (seeded, refit per permutation) and an exhaustive
// same-size label-permutation null (all C(15,3) subsets, observed order kept).
//
// The union backbone is OWNED by SanskritLexicography and consumed read-only
// from the sibling checkout; the committed data/lexico/heap_sat.json is the
// CI-safe artifact. No corpus data is touched — this is dictionary-only
// evidence (csl-atlas boundary).
//
// Usage: npm run build-heap-sat   (then npm run validate-heap-sat)

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { parseTsv } from "./build-heritage-witness.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { loadDictionaryInventory } from "./lib/dict-scope.mjs";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-heap-sat";
const SIBLING_ROOT = path.resolve(process.cwd(), "..", "SanskritLexicography");
const UNION_PATH = path.join(SIBLING_ROOT, "HeadwordLists", "union", "union_headwords.tsv");
const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const JSON_OUT = path.join(OUT_DIR, "heap_sat.json");
const SOURCE_OUT = path.join(OUT_DIR, "heap_sat.source.json");

const N_PERMUTATIONS = 5000;
const PERMUTATION_SEED = 15760801; // fixed: H1576 + arbitrary suffix, never wall-clock

// Union sigla whose inventory row lives under a different code. Union "PWK"
// is Boehtlingk's kuerzere Fassung = inventory "PW" (1879) — same convention
// as build-ghost-stock.mjs.
const UNION_TO_INVENTORY_CODE = { PWK: "pw" };

function round(value, digits = 4) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

/** Deterministic 32-bit PRNG (mulberry32); Math.random is banned in builders. */
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Publication-ordered dictionary roster from the inventory (tie-break: siglum). */
export function orderedDictionaries(unionCodes, inventoryRows) {
  const byCode = new Map(inventoryRows.map((row) => [String(row.code ?? "").trim().toLowerCase(), row]));
  const dicts = unionCodes.map((code) => {
    const invCode = UNION_TO_INVENTORY_CODE[code] ?? code.toLowerCase();
    const row = byCode.get(invCode);
    if (!row) throw new Error(`union dictionary code ${code} has no row in dictionary_inventory.csv`);
    const year = Number(row.year);
    if (!Number.isFinite(year)) throw new Error(`union dictionary code ${code} (inventory ${invCode}) has no numeric year`);
    return { code, inventoryCode: invCode, year, family: row.family || "" };
  });
  dicts.sort((a, b) => a.year - b.year || (a.code < b.code ? -1 : 1));
  return dicts;
}

/**
 * Fold union rows to a mask census: Map(bitmask -> lemma count), where bit i
 * marks presence in dictionary i of `codes` (any fixed code order works; the
 * caller aligns positions). Lemmas are deduplicated on the normalized SLP1 key.
 */
export function maskCensus(unionRows, codes) {
  const bitByCode = new Map(codes.map((code, i) => [code, i]));
  const census = new Map();
  const seen = new Set();
  for (const row of unionRows) {
    const { normalized } = normalizeLemma(row.slp1);
    if (!normalized || seen.has(normalized)) continue;
    seen.add(normalized);
    const dicts = row.dicts.split(" ").filter(Boolean);
    const nDicts = Number(row.n_dicts);
    if (!(nDicts > 0) || dicts.length !== nDicts) {
      throw new Error(`union row ${row.slp1}: n_dicts ${row.n_dicts} disagrees with dicts list "${row.dicts}"`);
    }
    let mask = 0;
    for (const code of dicts) {
      const bit = bitByCode.get(code);
      if (bit === undefined) throw new Error(`union row ${row.slp1}: unknown dictionary code ${code}`);
      mask |= 1 << bit;
    }
    census.set(mask, (census.get(mask) ?? 0) + 1);
  }
  return census;
}

/** Per-dictionary union lemma counts (dictionary "size" on the token axis). */
export function dictSizes(census, nDicts) {
  const sizes = new Array(nDicts).fill(0);
  for (const [mask, count] of census) {
    for (let i = 0; i < nDicts; i++) if (mask & (1 << i)) sizes[i] += count;
  }
  return sizes;
}

/**
 * Novelty per position for an ordering (array of dictionary indices): how many
 * lemmas each dictionary contributes that no earlier dictionary in the
 * ordering already listed. Exact, via min-position over each mask's set bits.
 */
export function noveltyForOrder(census, order) {
  const posOfDict = new Array(order.length);
  order.forEach((dictIndex, pos) => (posOfDict[dictIndex] = pos));
  const novelty = new Array(order.length).fill(0);
  for (const [mask, count] of census) {
    let minPos = Infinity;
    let m = mask;
    while (m) {
      const bit = 31 - Math.clz32(m & -m);
      const pos = posOfDict[bit];
      if (pos < minPos) minPos = pos;
      m &= m - 1;
    }
    novelty[minPos] += count;
  }
  return novelty;
}

/** OLS fit of log V = log K + beta * log n over the cumulative steps. */
export function heapsFit(cumulativeTokens, cumulativeDistinct) {
  const n = cumulativeTokens.length;
  const xs = cumulativeTokens.map(Math.log);
  const ys = cumulativeDistinct.map(Math.log);
  const xBar = xs.reduce((a, v) => a + v, 0) / n;
  const yBar = ys.reduce((a, v) => a + v, 0) / n;
  let sxx = 0;
  let sxy = 0;
  let syy = 0;
  for (let i = 0; i < n; i++) {
    sxx += (xs[i] - xBar) ** 2;
    sxy += (xs[i] - xBar) * (ys[i] - yBar);
    syy += (ys[i] - yBar) ** 2;
  }
  const beta = sxy / sxx;
  const logK = yBar - beta * xBar;
  const r2 = syy > 0 ? (sxy * sxy) / (sxx * syy) : null;
  return { K: Math.exp(logK), beta, logK, r2 };
}

/**
 * Full curve + fit + per-position relative residuals for one ordering.
 * Relative residual = (observed novelty - Heaps-predicted increment) /
 * predicted increment, so a break above the curve is positive.
 */
export function curveForOrder(census, sizes, order) {
  const novelty = noveltyForOrder(census, order);
  const cumTokens = [];
  const cumDistinct = [];
  let nTok = 0;
  let vDist = 0;
  for (let pos = 0; pos < order.length; pos++) {
    nTok += sizes[order[pos]];
    vDist += novelty[pos];
    cumTokens.push(nTok);
    cumDistinct.push(vDist);
  }
  const fit = heapsFit(cumTokens, cumDistinct);
  const predict = (tok) => (tok > 0 ? fit.K * tok ** fit.beta : 0);
  const residuals = [];
  for (let pos = 0; pos < order.length; pos++) {
    const predicted = predict(cumTokens[pos]) - predict(pos > 0 ? cumTokens[pos - 1] : 0);
    residuals.push(predicted > 0 ? (novelty[pos] - predicted) / predicted : null);
  }
  return { novelty, cumTokens, cumDistinct, fit, residuals };
}

function meanResidualOf(order, residuals, targetDictIndices) {
  const target = new Set(targetDictIndices);
  let sum = 0;
  let n = 0;
  for (let pos = 0; pos < order.length; pos++) {
    if (target.has(order[pos]) && residuals[pos] !== null) {
      sum += residuals[pos];
      n += 1;
    }
  }
  return n > 0 ? sum / n : null;
}

/** All k-subsets of [0, n) as arrays, lexicographic — exhaustive label null. */
export function kSubsets(n, k) {
  const out = [];
  const pick = (start, acc) => {
    if (acc.length === k) {
      out.push([...acc]);
      return;
    }
    for (let i = start; i <= n - (k - acc.length); i++) {
      acc.push(i);
      pick(i + 1, acc);
      acc.pop();
    }
  };
  pick(0, []);
  return out;
}

export function buildPayload(unionRows, inventoryRows, { generatedAt, nPermutations = N_PERMUTATIONS } = {}) {
  const codes = [...new Set(unionRows.flatMap((row) => row.dicts.split(" ").filter(Boolean)))].sort();
  const dicts = orderedDictionaries(codes, inventoryRows);
  const codeOrder = dicts.map((d) => d.code); // publication order
  const census = maskCensus(unionRows, codeOrder);
  const sizes = dictSizes(census, codeOrder.length);
  const identity = codeOrder.map((_, i) => i);
  const observed = curveForOrder(census, sizes, identity);

  const specialisedIdx = dicts.map((d, i) => (d.family === "Specialized" ? i : -1)).filter((i) => i >= 0);
  const observedStat = meanResidualOf(identity, observed.residuals, specialisedIdx);

  // Order-permutation null: shuffle arrival order, refit, recompute the
  // specialised-set mean relative residual at the permuted positions.
  const rand = mulberry32(PERMUTATION_SEED);
  let orderExceed = 0;
  let orderValid = 0;
  for (let p = 0; p < nPermutations; p++) {
    const perm = [...identity];
    for (let i = perm.length - 1; i > 0; i--) {
      const j = Math.floor(rand() * (i + 1));
      [perm[i], perm[j]] = [perm[j], perm[i]];
    }
    const c = curveForOrder(census, sizes, perm);
    const stat = meanResidualOf(perm, c.residuals, specialisedIdx);
    if (stat === null) continue;
    orderValid += 1;
    if (stat >= observedStat) orderExceed += 1;
  }
  const orderP = (orderExceed + 1) / (orderValid + 1);

  // Exhaustive label-permutation null: observed order and fit kept fixed; the
  // specialised trio's mean residual is ranked among ALL same-size subsets.
  const subsets = kSubsets(codeOrder.length, specialisedIdx.length);
  let labelExceed = 0;
  for (const subset of subsets) {
    const stat = meanResidualOf(identity, observed.residuals, subset);
    if (stat !== null && stat >= observedStat) labelExceed += 1;
  }
  const labelP = labelExceed / subsets.length;

  const unionLemmas = [...census.values()].reduce((a, v) => a + v, 0);
  const steps = dicts.map((d, pos) => ({
    code: d.code,
    inventoryCode: d.inventoryCode,
    year: d.year,
    family: d.family,
    specialised: d.family === "Specialized",
    lemmas: sizes[pos],
    novelty: observed.novelty[pos],
    noveltyShare: round(observed.novelty[pos] / sizes[pos]),
    cumulativeTokens: observed.cumTokens[pos],
    cumulativeDistinct: observed.cumDistinct[pos],
    predictedNovelty: round(
      observed.fit.K * observed.cumTokens[pos] ** observed.fit.beta -
        (pos > 0 ? observed.fit.K * observed.cumTokens[pos - 1] ** observed.fit.beta : 0),
      1
    ),
    relativeResidual: round(observed.residuals[pos])
  }));

  // The agenda's concrete sub-claim: each new GENERAL dictionary after ~1890
  // adds <5% novel lemmas.
  const post1890General = steps
    .filter((s) => !s.specialised && s.year >= 1890)
    .map((s) => ({ code: s.code, year: s.year, noveltyShare: s.noveltyShare }));

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "SanskritLexicography/HeadwordLists/union/union_headwords.tsv",
      "data/dictionary_inventory.csv",
      "scripts/build-heap-sat.mjs"
    ],
    method:
      "Normalize each union_headwords.tsv slp1 key with the canonical sanskrit-util slp1_norm and deduplicate; fold every lemma's dictionary list to a 15-bit mask so cumulative novelty under any dictionary ordering is exact mask arithmetic. Order dictionaries by dictionary_inventory.csv publication year (siglum tie-break; union PWK = inventory pw, 1879). Fit Heaps K*n^beta by OLS on log cumulative-distinct vs log cumulative-tokens over the 15 accumulation steps (n = cumulative union lemma listings scanned). Per-dictionary relative residual = (observed novelty - fitted increment) / fitted increment. Specialised-break statistic = mean relative residual of the inventory-family-Specialized dictionaries (INM, VEI, BHS). Null 1 (order-permutation): shuffle arrival order with a fixed-seed mulberry32, refit per permutation, recompute the statistic at permuted positions; one-sided p = (exceed+1)/(valid+1). Null 2 (label-permutation, exhaustive): keep the observed order and fit, rank the specialised trio's mean residual among all C(15,3)=455 same-size subsets.",
    totals: {
      unionLemmas,
      dictionaries: codeOrder.length,
      totalLemmaListings: sizes.reduce((a, v) => a + v, 0),
      specialised: specialisedIdx.map((i) => dicts[i].code)
    },
    heapsFit: {
      K: round(observed.fit.K, 2),
      beta: round(observed.fit.beta, 5),
      r2LogLog: round(observed.fit.r2, 5),
      fitPoints: codeOrder.length,
      model: "V(n) = K * n^beta, OLS on log-log over the 15 publication-order accumulation steps"
    },
    steps,
    specialisedBreak: {
      statistic: round(observedStat),
      statisticDefinition:
        "mean relative residual (observed vs Heaps-fitted marginal novelty) over the Specialized-family dictionaries INM, VEI, BHS",
      orderPermutation: {
        permutations: nPermutations,
        valid: orderValid,
        seed: PERMUTATION_SEED,
        pOneSided: round(orderP, 5)
      },
      labelPermutation: {
        subsets: subsets.length,
        exceeding: labelExceed,
        pOneSided: round(labelP, 5),
        note: "exhaustive over all same-size dictionary subsets; observed order and fit held fixed"
      }
    },
    post1890General,
    limitations: [
      "The token axis counts union lemma LISTINGS (one per dictionary that lists the lemma), not corpus tokens; Heaps' law is borrowed as a saturation model for the recording process, not asserted as the linguistic original.",
      "Union lemmas key on normalized SLP1 (accents and homonym digits stripped), so homonyms collapse; a dictionary's novelty is novelty of normalized keys.",
      "Publication years are single inventory dates; multi-volume spans (PWG 1855-1875, PW 1879-1889) are collapsed to their inventory year, so within-span arrival order is conventional.",
      "15 dictionaries give 15 fit points; the Heaps fit is descriptive and the order-permutation null is the inferential guard, not the OLS standard errors.",
      "The specialised set is the inventory family `Specialized` restricted to union members (INM, VEI, BHS); IEG and technical kosas named in the agenda are not in the union backbone and are untested here.",
      "The union backbone covers 15 of the 44+ CDSL dictionaries (the deduplicated multi-dictionary export); saturation claims are relative to this roster, not all of Sanskrit lexicography."
    ],
    boundary: [
      "union_headwords.tsv is owned by SanskritLexicography and consumed read-only from the sibling checkout; dictionary_inventory.csv is the in-repo roster. Dictionary-only evidence — no DCS/corpus data touched. Rendering owner repo: csl-atlas."
    ]
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
  return payload;
}

function writeSourceEnvelope(payload) {
  let commit = "unknown";
  let siblingCommit = "unknown";
  try {
    commit = execSync("git rev-parse HEAD", { encoding: "utf8" }).trim();
  } catch {}
  try {
    siblingCommit = execSync(`git -C "${SIBLING_ROOT}" rev-parse HEAD`, { encoding: "utf8" }).trim();
  } catch {}
  const envelope = {
    dataset: "heap_sat",
    commit,
    unionRepo: "https://github.com/gasyoun/SanskritLexicography",
    unionPath: "HeadwordLists/union/union_headwords.tsv",
    siblingCommit,
    generatedAt: payload.generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: payload.sourceFiles,
    schemaVersion: SCHEMA_VERSION
  };
  fs.writeFileSync(SOURCE_OUT, `${JSON.stringify(envelope, null, 2)}\n`);
}

function main() {
  if (!fs.existsSync(UNION_PATH)) {
    console.error(
      `Required input missing: ${UNION_PATH}\n` +
        "This builder needs a sibling SanskritLexicography checkout (the committed data/lexico/heap_sat.json is the CI-safe artifact)."
    );
    process.exit(1);
  }
  const unionRows = parseTsv(fs.readFileSync(UNION_PATH, "utf8"));
  const inventoryRows = loadDictionaryInventory();
  const payload = buildPayload(unionRows, inventoryRows);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  writeSourceEnvelope(payload);
  console.log(`Wrote heap-sat packet (${payload.totals.unionLemmas} union lemmas, ${payload.totals.dictionaries} dictionaries):`);
  console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), SOURCE_OUT)}`);
  console.log(
    `  Heaps beta ${payload.heapsFit.beta} (R2 ${payload.heapsFit.r2LogLog}); ` +
      `specialised-break stat ${payload.specialisedBreak.statistic}, order-perm p ${payload.specialisedBreak.orderPermutation.pOneSided}, ` +
      `label-perm p ${payload.specialisedBreak.labelPermutation.pOneSided}`
  );
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
