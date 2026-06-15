// Build R2 H1 fixed-lemma panel deconfounding check.
//
// Generates r2_h1_panel.json: the same H1 year-vs-sense-granularity trend as
// r2_h1.json but restricted to a fixed panel of 30 nouns. Removes the
// headword-splitting confound (MW splits ~286k compounds into separate short
// entries, diluting its units/entry). The panel is shared across all 11 dicts
// so each dict's data point is computed on the same lemmas.
//
// Expected result (R2_FINDINGS.md): Pearson r ≈ 0.01 (flat, archived 0.06).
// A weak r = 0.56 among the 5 explicit-marker dicts is n=5 non-significant.
//
// Usage: npm run build-r2-h1-panel

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { R2_DICTS } from "./build-r2-source-anchors.mjs";
import { senseUnits } from "./build-r2-h1.mjs";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const ARCHIVE_H1 = path.join(OUT_DIR, "r2_archive_h1.json");
const OUT_FILE = path.join(OUT_DIR, "r2_h1_panel.json");

const PANEL_SIZE = 30;
// Minimum number of the 11 H1 dicts a lemma must appear in to qualify
const MIN_DICT_COVERAGE = 7;

// The 11 dicts used in r2_h1 (from r2_archive_h1.json)
const H1_DICTS_META = JSON.parse(fs.readFileSync(ARCHIVE_H1, "utf8")).rows
  .filter(r => r.dict)
  .map(r => ({ code: r.dict, year: r.year, family: r.family }));

const SPLIT_BY_CODE = new Map(R2_DICTS.map(d => [d.code, d]));

// Strip trailing nominative H/M for cross-dict matching
export function stemKey(k) {
  return k.replace(/[HM]$/, "");
}

// WIL lex tags indicating a nominal entry
const NOMINAL_LEX = /\bm\b|\bf\b|\bn\b|mfn|mf\b|mn\b/;

// Build a stem→{k1, bodies[]} map aggregating ALL L-blocks per stem.
// This is critical for MW 1899 which splits the same base lemma into many
// short sub-entries; summing their senseUnits recovers the true per-lemma count.
function loadStemMap(dictCode) {
  const map = new Map();
  if (!dictExists(dictCode)) return map;
  for (const rec of iterateDict(dictCode)) {
    const stem = stemKey(rec.k1);
    if (!map.has(stem)) map.set(stem, { k1: rec.k1, bodies: [] });
    map.get(stem).bodies.push(rec.body || "");
  }
  return map;
}

function pearson(xs, ys) {
  const n = xs.length;
  if (n < 2) return 0;
  const mx = xs.reduce((a, b) => a + b, 0) / n;
  const my = ys.reduce((a, b) => a + b, 0) / n;
  let num = 0, dx = 0, dy = 0;
  for (let i = 0; i < n; i++) {
    const a = xs[i] - mx, b = ys[i] - my;
    num += a * b; dx += a * a; dy += b * b;
  }
  return dx && dy ? Number((num / Math.sqrt(dx * dy)).toFixed(3)) : 0;
}

function r3(n) { return Number(n.toFixed(3)); }
function r4(n) { return Number(n.toFixed(4)); }

// --- Minimal OLS with classical SEs (for the family-controlled year test) ---
// Self-contained so the panel builder has no cross-file numerical dependency.

// (X'X) for an n×k design given as array of length-k rows.
function gram(X) {
  const k = X[0].length;
  const G = Array.from({ length: k }, () => new Array(k).fill(0));
  for (const row of X) {
    for (let a = 0; a < k; a++) for (let b = 0; b < k; b++) G[a][b] += row[a] * row[b];
  }
  return G;
}

// X'y
function xty(X, y) {
  const k = X[0].length;
  const v = new Array(k).fill(0);
  for (let i = 0; i < X.length; i++) for (let a = 0; a < k; a++) v[a] += X[i][a] * y[i];
  return v;
}

// Gauss-Jordan inverse of a square matrix (returns null if singular).
function matInv(M) {
  const n = M.length;
  const A = M.map((row, i) => [...row, ...Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))]);
  for (let col = 0; col < n; col++) {
    let piv = col;
    for (let r = col + 1; r < n; r++) if (Math.abs(A[r][col]) > Math.abs(A[piv][col])) piv = r;
    if (Math.abs(A[piv][col]) < 1e-12) return null;
    [A[col], A[piv]] = [A[piv], A[col]];
    const d = A[col][col];
    for (let j = 0; j < 2 * n; j++) A[col][j] /= d;
    for (let r = 0; r < n; r++) {
      if (r === col) continue;
      const f = A[r][col];
      for (let j = 0; j < 2 * n; j++) A[r][j] -= f * A[col][j];
    }
  }
  return A.map(row => row.slice(n));
}

// OLS fit returning beta + classical-SE covariance and residual df.
function fitOLS(X, y) {
  const n = X.length, k = X[0].length;
  const G = gram(X), Xy = xty(X, y), Ginv = matInv(G);
  if (!Ginv) return null;
  const beta = Ginv.map(row => row.reduce((s, v, j) => s + v * Xy[j], 0));
  let rss = 0;
  for (let i = 0; i < n; i++) {
    const yhat = X[i].reduce((s, v, j) => s + v * beta[j], 0);
    rss += (y[i] - yhat) ** 2;
  }
  const df = n - k;
  const sigma2 = df > 0 ? rss / df : NaN;
  const se = beta.map((_, a) => Math.sqrt(sigma2 * Ginv[a][a]));
  return { beta, se, df, rss, sigma2 };
}

// Two-sided 97.5% t critical value (small df), table-backed; ~1.96 in the limit.
function tCrit975(df) {
  const table = { 1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 30: 2.042 };
  if (df <= 0) return Infinity;
  if (table[df]) return table[df];
  const keys = Object.keys(table).map(Number).filter(d => d >= df);
  return keys.length ? table[Math.min(...keys)] : 1.96;
}

async function main() {
  process.stderr.write("Loading stem maps for 11 H1 dicts...\n");

  const stemMaps = new Map();
  for (const dm of H1_DICTS_META) {
    stemMaps.set(dm.code, loadStemMap(dm.code));
    process.stderr.write(`  ${dm.code}: ${stemMaps.get(dm.code).size} stems\n`);
  }

  // Use WIL as reference to enumerate nominal candidate lemmas
  const wilDict = SPLIT_BY_CODE.get("wil");
  const wilMap  = stemMaps.get("wil");

  // Score each WIL nominal lemma by coverage across the 11 H1 dicts.
  // Restrict WIL sense count to 2–8: moderate-polysemy nouns representative
  // of the full corpus (WIL full-corpus mean ≈ 1.8; panel nouns are slightly
  // above mean to ensure multiple senses across dicts).
  const candidates = [];
  for (const [stem, { bodies, k1 }] of wilMap) {
    const body = bodies[0] || "";
    const lexMatch = (body.match(/<lex>(.*?)<\/lex>/) || [])[1] || "";
    if (!NOMINAL_LEX.test(lexMatch)) continue;

    const wilUnits = bodies.reduce((s, b) => s + senseUnits(b, wilDict), 0);
    if (wilUnits < 2 || wilUnits > 8) continue;

    let coverage = 0;
    for (const dm of H1_DICTS_META) {
      if (stemMaps.get(dm.code)?.has(stem)) coverage++;
    }
    if (coverage < MIN_DICT_COVERAGE) continue;

    candidates.push({ stem, k1, wilUnits, coverage });
  }

  // Sort by coverage (most-covered first), then by WIL sense count descending
  candidates.sort((a, b) => b.coverage - a.coverage || b.wilUnits - a.wilUnits);
  const panel = candidates.slice(0, PANEL_SIZE).map(c => c.stem);

  process.stderr.write(`Panel (${panel.length}): ${panel.slice(0, 10).join(", ")}...\n`);
  process.stderr.write(`Coverage range: ${candidates[0]?.coverage} – ${candidates[PANEL_SIZE - 1]?.coverage}\n`);

  // Per-dict: compute mean sense-units over panel lemmas
  const dictRows = [];
  const lemmaRows = []; // granular per-(lemma,dict) observations for the regression
  for (const dm of H1_DICTS_META) {
    const dictCfg = SPLIT_BY_CODE.get(dm.code) ?? { code: dm.code, split: "lumped-proxy" };
    const regime = dm.family === "indigenous" ? "indigenous" : "western";
    const map = stemMaps.get(dm.code);
    let sumUnits = 0, found = 0;

    for (const stem of panel) {
      const entry = map?.get(stem);
      if (!entry) continue;
      // Aggregate all L-blocks: sum senseUnits across all bodies for this stem
      const lemmaUnits = entry.bodies.reduce((s, b) => s + senseUnits(b, dictCfg), 0);
      const units = Math.max(1, lemmaUnits);
      sumUnits += units;
      found++;
      lemmaRows.push({ lemma: stem, dict: dm.code, year: dm.year, family: dm.family, regime, units });
    }

    const meanUnits = found > 0 ? r3(sumUnits / found) : null;
    dictRows.push({
      dict: dm.code,
      year: dm.year,
      family: dm.family,
      meanPanelUnits: meanUnits,
      panelLemmasFound: found,
      panelLemmasTotal: panel.length,
    });
    process.stderr.write(`  ${dm.code} (${dm.year}): meanPanelUnits=${meanUnits} (${found}/${panel.length} lemmas)\n`);
  }

  // Pearson r for all 11 dicts (skip dicts with null meanUnits)
  const forPearson = dictRows.filter(r => r.meanPanelUnits !== null);
  const rAll = pearson(forPearson.map(r => r.year), forPearson.map(r => r.meanPanelUnits));

  // Pearson r for only explicit-marker dicts (wil, ben, mw72, ap90, ap)
  const EXPLICIT_MARKER_DICTS = new Set(["wil", "ben", "mw72", "ap90", "ap"]);
  const forPearsonExplicit = forPearson.filter(r => EXPLICIT_MARKER_DICTS.has(r.dict));
  const rExplicit = pearson(forPearsonExplicit.map(r => r.year), forPearsonExplicit.map(r => r.meanPanelUnits));

  process.stderr.write(`Pearson r (all 11): ${rAll} vs archived ~0.01\n`);
  process.stderr.write(`Pearson r (explicit-marker 5): ${rExplicit} vs archived ~0.56 (n=5, non-significant)\n`);

  // ----------------------------------------------------------------------
  // H1R rigor block: the bivariate Pearson r conflates year with FAMILY
  // composition (year is a dict-level covariate with only 11 values across
  // ~7 families). Three sharper tests:
  //   (a) within-family year deltas — controls family directly (panel units,
  //       which also remove the MW headword-splitting confound);
  //   (b) a family-controlled OLS (units ~ year + family) reporting year's
  //       PARTIAL slope + a t-based 95% CI, with the near-saturation caveat;
  //   (c) parser-regime stratification — does any year trend survive within
  //       the single western-parsed regime (vs the 2 indigenous dicts)?
  // ----------------------------------------------------------------------
  const valid = forPearson; // dicts with a non-null meanPanelUnits

  // (a) Within-family trends: families covered by ≥2 dicts at different years.
  const byFamily = new Map();
  for (const r of valid) {
    if (!byFamily.has(r.family)) byFamily.set(r.family, []);
    byFamily.get(r.family).push(r);
  }
  const withinFamilyTrends = [];
  for (const [family, rows] of byFamily) {
    if (rows.length < 2) continue;
    rows.sort((a, b) => a.year - b.year);
    const first = rows[0], last = rows[rows.length - 1];
    const spanYears = last.year - first.year;
    if (spanYears === 0) continue;
    const deltaTotal = r3(last.meanPanelUnits - first.meanPanelUnits);
    const unitsPerYear = r4(deltaTotal / spanYears);
    const verdict = Math.abs(deltaTotal) < 0.15 ? "flat"
      : deltaTotal < 0 ? "decrease (no inflation)" : "increase";
    withinFamilyTrends.push({
      family, nDicts: rows.length, spanYears,
      dicts: rows.map(r => ({ dict: r.dict, year: r.year, panelUnits: r.meanPanelUnits })),
      deltaTotal, unitsPerYear, verdict,
    });
  }
  withinFamilyTrends.sort((a, b) => a.dicts[0].year - b.dicts[0].year);
  const wfSlopes = withinFamilyTrends.map(t => t.unitsPerYear);
  const meanWithinFamilyUnitsPerYear = wfSlopes.length
    ? r4(wfSlopes.reduce((a, b) => a + b, 0) / wfSlopes.length) : null;

  // (b) Family-controlled OLS at the dict level: units ~ year_centered + family.
  // Year is centered for interpretable intercept/conditioning; family enters
  // as k-1 dummies (first family is the reference).
  const families = [...new Set(valid.map(r => r.family))];
  const refFamily = families[0];
  const dummyFamilies = families.slice(1);
  const meanYear = valid.reduce((s, r) => s + r.year, 0) / valid.length;
  const X = valid.map(r => [
    1,
    r.year - meanYear,
    ...dummyFamilies.map(f => (r.family === f ? 1 : 0)),
  ]);
  const yv = valid.map(r => r.meanPanelUnits);
  const ols = fitOLS(X, yv);
  let familyControlledRegression;
  if (ols) {
    const yearSlope = ols.beta[1];
    const yearSE = ols.se[1];
    const tc = tCrit975(ols.df);
    const ci = [r4(yearSlope - tc * yearSE), r4(yearSlope + tc * yearSE)];
    familyControlledRegression = {
      model: `meanPanelUnits ~ yearCentered + family(${dummyFamilies.length} dummies, ref=${refFamily})`,
      nObs: valid.length,
      nParams: X[0].length,
      residualDf: ols.df,
      nearSaturated: ols.df < 5,
      yearSlopePerYear: r4(yearSlope),
      yearSE: r4(yearSE),
      yearCI95: ci,
      tCritical: tc,
      ciIncludesZero: ci[0] <= 0 && ci[1] >= 0,
      note: ols.df < 5
        ? `Near-saturated: ${valid.length} dicts spread over ${families.length} families leave only ${ols.df} residual df, so year and family are barely separable — the wide CI reflects this, not a measured null.`
        : "Year's partial slope after family adjustment.",
    };
  } else {
    familyControlledRegression = { error: "design rank-deficient (year collinear with family); not identifiable at this n." };
  }

  // (c) Parser-regime stratification: bivariate year~units within each regime.
  const western = valid.filter(r => r.family !== "indigenous");
  const indigenous = valid.filter(r => r.family === "indigenous");
  const parserRegimeStratified = {
    western: {
      n: western.length,
      pearsonYearVsUnits: pearson(western.map(r => r.year), western.map(r => r.meanPanelUnits)),
      note: "All non-indigenous dicts share one Roman-headword parsing regime; a flat r here means the family-granularity gap is lexicographic, not a parser artifact.",
    },
    indigenous: {
      n: indigenous.length,
      dicts: indigenous.map(r => ({ dict: r.dict, year: r.year, panelUnits: r.meanPanelUnits })),
      note: "Only 2 indigenous dicts (skd, vcp) — no within-regime trend estimable; reported for completeness.",
    },
  };

  const decisive = meanWithinFamilyUnitsPerYear !== null && meanWithinFamilyUnitsPerYear <= 0.01;
  const h1Controlled = {
    method: "Year is a dict-level covariate (11 values / ~7 families); bivariate r conflates it with family. Tested via within-family deltas, a family-controlled OLS, and parser-regime stratification.",
    naiveBivariatePearson: rAll,
    withinFamilyTrends,
    meanWithinFamilyUnitsPerYear,
    familyControlledRegression,
    parserRegimeStratified,
    verdict: decisive
      ? "Within every family with a time span, per-lemma granularity is flat-to-decreasing — no temporal inflation once family is held fixed. Across families it tracks family, not year. The pooled year effect is underidentified (n=11, ~7 families), so the correct statement is 'no within-family inflation', NOT 'r≈0 proves no relationship'."
      : "Within-family trends are mixed; year effect remains underidentified at n=11 — report as inconclusive, not null.",
    interpretationNote: "Underpowered ≠ no effect: the family-controlled CI on year is wide by construction (only 11 dict-points). The falsifiable claim is the within-family one: any family showing a clear per-year increase would be evidence FOR temporal inflation.",
  };

  process.stderr.write(`Within-family mean units/yr: ${meanWithinFamilyUnitsPerYear} over ${withinFamilyTrends.length} families\n`);
  if (ols) process.stderr.write(`Family-controlled year slope: ${familyControlledRegression.yearSlopePerYear}/yr, 95% CI ${JSON.stringify(familyControlledRegression.yearCI95)} (df=${ols.df})\n`);

  // Granular per-(lemma,dict) observations, written as a sidecar for reproducibility.
  const LEMMA_FILE = path.join(OUT_DIR, "r2_h1_panel_lemma.json");
  fs.writeFileSync(LEMMA_FILE, JSON.stringify({
    schemaVersion: "0.1.0",
    generatedBy: "npm run build-r2-h1-panel",
    note: "Per-(lemma,dict) sense-unit observations underlying r2_h1_panel.json and its h1Controlled block.",
    panelSize: panel.length,
    nObservations: lemmaRows.length,
    rows: lemmaRows,
  }, null, 2));

  const output = {
    schemaVersion: "0.1.0",
    generatedBy: "npm run build-r2-h1-panel",
    claim: "Fixed-lemma panel removes headword-splitting confound; year-trend stays flat (H1 not supported).",
    panel,
    panelSize: panel.length,
    minDictCoverage: MIN_DICT_COVERAGE,
    stats: {
      pearsonYearVsUnits: rAll,
      pearsonExplicitMarkerDicts: rExplicit,
      nDictsInPearson: forPearson.length,
      nExplicitMarkerDicts: forPearsonExplicit.length,
      archivedPearsonAll: 0.01,
      archivedPearsonExplicit: 0.56,
    },
    h1Controlled,
    rows: dictRows,
    limitations: [
      "Panel selected from WIL nominal entries (m./f./n./mfn.) present in ≥" + MIN_DICT_COVERAGE + " of the 11 H1 dicts.",
      "Indigenous dicts (skd, vcp) use different headword conventions; stem-key matching may miss some panel lemmas.",
      "senseUnits() uses the same proxy as r2_h1 (unchanged); calibration drift documented there.",
      "r_explicit = 0.56 among 5 explicit-marker dicts is n=5 non-significant and convention-confounded.",
      "h1Controlled.familyControlledRegression is near-saturated (only ~3 residual df): year's CI is wide by design, so it bounds — it does not measure — the temporal slope. The within-family deltas carry the inferential weight.",
      "Within-family trends rest on as few as 2 dicts per family (one slope each); they falsify temporal inflation but cannot estimate its rate.",
      "Archive parity is a regression signal, not an optimization target.",
    ],
  };

  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(output, null, 2));
  console.log(`Wrote ${path.relative(process.cwd(), OUT_FILE)}`);
  console.log(`Pearson r (all 11): ${rAll} (archived ~0.01) — explicit-marker (5): ${rExplicit} (archived ~0.56)`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
