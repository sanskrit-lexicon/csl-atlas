// Build the ghost-stock packet (PH4 GHOST-STOCK + PH6 HERITAGE-WIT, H1575;
// agenda backlog #3): joins the SanskritLexicography union headword backbone
// (n_dicts multiplicity per lemma) against the in-repo VisualDCS corpus
// summary (attested flags) and, for MW lemmas, the MW<->Heritage crosswalk —
// three independent witnesses on one normalized SLP1 key.
//
// PH4: attestation rate by n_dicts stratum (Wilson CIs), per-dict
// unique-and-attested share, and a descriptive logistic model
// attested ~ n_dicts + family-presence indicators.
//
// PH6: the 2x2x2 witness cube (MW-unique x Heritage-covered x DCS-attested)
// with Woolf-CI odds ratios, and the ranked triple-filter ghost-candidate
// queue (MW-unique AND Heritage-uncovered AND DCS-unattested), evidence grade
// `inferred` until human review — routed toward the H5-style QA queue, never
// asserted as fact.
//
// Inputs are consumed read-only: the union backbone and crosswalk are OWNED
// by SanskritLexicography (sibling checkout); the DCS summary is the frozen
// VisualDCS export already committed in-repo (VISUALDCS_CONSUMPTION_CONTRACT
// — no DCS ingestion here). H346's heritage-witness packet is a *sibling*
// deliverable (MW entry-level coverage page); this builder extends it with
// the union/DCS triangulation rather than re-deriving the crosswalk.
//
// Usage: npm run build-ghost-stock   (then npm run validate-ghost-stock)

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { parseTsv } from "./build-heritage-witness.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { parseDcsSummaryFile } from "./lib/dcs-summary.mjs";
import { loadDictionaryInventory } from "./lib/dict-scope.mjs";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-ghost-stock";
const SIBLING_ROOT = path.resolve(process.cwd(), "..", "SanskritLexicography");
const UNION_PATH = path.join(SIBLING_ROOT, "HeadwordLists", "union", "union_headwords.tsv");
const CROSSWALK_PATH = path.join(SIBLING_ROOT, "HeadwordLists", "mw_heritage_crosswalk.tsv");
const DCS_SUMMARY_PATH = path.resolve(process.cwd(), "data", "dcs", "dcs_lemma_summary.json");
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "ghost-stock");
const JSON_OUT = path.join(OUT_DIR, "ghost_stock.json");
const SOURCE_OUT = path.join(OUT_DIR, "ghost_stock.source.json");

function round(value, digits = 4) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

function compareLemma(a, b) {
  return a < b ? -1 : a > b ? 1 : 0;
}

/** Wilson 95% score interval for k successes in n trials. */
export function wilson(k, n, z = 1.96) {
  if (!(n > 0)) return { lo: null, hi: null };
  const p = k / n;
  const z2 = z * z;
  const denom = 1 + z2 / n;
  const center = (p + z2 / (2 * n)) / denom;
  const half = (z * Math.sqrt((p * (1 - p)) / n + z2 / (4 * n * n))) / denom;
  return { lo: Math.max(0, center - half), hi: Math.min(1, center + half) };
}

function solveLinear(A, b) {
  // Gaussian elimination with partial pivoting; A is modified in place.
  const p = b.length;
  const M = A.map((row, i) => [...row, b[i]]);
  for (let col = 0; col < p; col++) {
    let pivot = col;
    for (let r = col + 1; r < p; r++) {
      if (Math.abs(M[r][col]) > Math.abs(M[pivot][col])) pivot = r;
    }
    if (Math.abs(M[pivot][col]) < 1e-12) throw new Error("singular information matrix in logistic fit");
    [M[col], M[pivot]] = [M[pivot], M[col]];
    for (let r = 0; r < p; r++) {
      if (r === col) continue;
      const f = M[r][col] / M[col][col];
      for (let c = col; c <= p; c++) M[r][c] -= f * M[col][c];
    }
  }
  return M.map((row, i) => row[p] / row[i]);
}

function invertMatrix(A) {
  const p = A.length;
  const cols = [];
  for (let j = 0; j < p; j++) {
    const e = new Array(p).fill(0);
    e[j] = 1;
    cols.push(solveLinear(A.map((row) => [...row]), e));
  }
  // cols[j] is column j of the inverse.
  return Array.from({ length: p }, (_, i) => cols.map((col) => col[i]));
}

/**
 * Deterministic logistic regression via IRLS (no dependencies).
 * @param {number[][]} X design matrix rows (include the intercept column)
 * @param {number[]} y 0/1 outcomes
 * @returns {{beta:number[], se:number[], logLik:number, nullLogLik:number, mcFaddenR2:number, iterations:number, converged:boolean}}
 */
export function fitLogistic(X, y, { maxIter = 50, tol = 1e-10 } = {}) {
  const n = X.length;
  const p = X[0].length;
  let ones = 0;
  for (const v of y) ones += v;
  const pBar = ones / n;
  // Start at the intercept-only MLE; Newton steps from beta=0 can overshoot
  // into a flat region (mu saturates, the information matrix degenerates)
  // on data this unbalanced.
  let beta = new Array(p).fill(0);
  beta[0] = Math.log(pBar / (1 - pBar));
  let converged = false;
  let iterations = 0;

  const statsAt = (betaNow) => {
    const A = Array.from({ length: p }, () => new Array(p).fill(0));
    const g = new Array(p).fill(0);
    let logLik = 0;
    for (let i = 0; i < n; i++) {
      const xi = X[i];
      let eta = 0;
      for (let j = 0; j < p; j++) eta += xi[j] * betaNow[j];
      const mu = 1 / (1 + Math.exp(-eta));
      const w = Math.max(mu * (1 - mu), 1e-12);
      logLik += y[i] ? Math.log(Math.max(mu, 1e-300)) : Math.log(Math.max(1 - mu, 1e-300));
      const resid = y[i] - mu;
      for (let j = 0; j < p; j++) {
        g[j] += resid * xi[j];
        for (let k = j; k < p; k++) A[j][k] += w * xi[j] * xi[k];
      }
    }
    for (let j = 0; j < p; j++) for (let k = 0; k < j; k++) A[j][k] = A[k][j];
    return { A, g, logLik };
  };

  const logLikAt = (betaNow) => {
    let logLik = 0;
    for (let i = 0; i < n; i++) {
      const xi = X[i];
      let eta = 0;
      for (let j = 0; j < p; j++) eta += xi[j] * betaNow[j];
      const mu = 1 / (1 + Math.exp(-eta));
      logLik += y[i] ? Math.log(Math.max(mu, 1e-300)) : Math.log(Math.max(1 - mu, 1e-300));
    }
    return logLik;
  };

  for (iterations = 1; iterations <= maxIter; iterations++) {
    const s = statsAt(beta);
    const step = solveLinear(s.A.map((row) => [...row]), s.g);
    // Step-halving: never accept a Newton step that lowers the likelihood.
    let scale = 1;
    let candidate = beta.map((b, j) => b + scale * step[j]);
    let candLik = logLikAt(candidate);
    let halvings = 0;
    while ((!Number.isFinite(candLik) || candLik < s.logLik) && halvings < 30) {
      scale /= 2;
      candidate = beta.map((b, j) => b + scale * step[j]);
      candLik = logLikAt(candidate);
      halvings += 1;
    }
    beta = candidate;
    if (Number.isFinite(candLik) && Math.abs(candLik - s.logLik) < tol * (Math.abs(candLik) + 1)) {
      converged = true;
      break;
    }
  }

  const finalStats = statsAt(beta);
  const cov = invertMatrix(finalStats.A);
  const se = cov.map((row, j) => Math.sqrt(Math.max(row[j], 0)));
  const nullLogLik = n * (pBar * Math.log(pBar) + (1 - pBar) * Math.log(1 - pBar));
  return {
    beta,
    se,
    logLik: finalStats.logLik,
    nullLogLik,
    mcFaddenR2: 1 - finalStats.logLik / nullLogLik,
    iterations,
    converged
  };
}

// Fold crosswalk rows onto one coverage verdict per normalized SLP1 key —
// same rank semantics as build-heritage-witness.mjs (anchor beats
// covered-no-anchor beats absent), so a homonym split never downgrades a
// covered key.
export function foldCrosswalkCoverage(crosswalkRows) {
  const rank = { anchored: 2, "covered-no-anchor": 1, absent: 0 };
  const byKey = new Map();
  for (const row of crosswalkRows) {
    const { normalized } = normalizeLemma(row.mw_key1);
    if (!normalized) continue;
    const covered = row.covered_flag === "1";
    const tier = covered ? ((row.heritage_entry_anchor ?? "").trim() ? "anchored" : "covered-no-anchor") : "absent";
    const prev = byKey.get(normalized);
    if (prev === undefined || rank[tier] > rank[prev]) byKey.set(normalized, tier);
  }
  return byKey;
}

function woolfOddsRatio(contrast, a, b, c, d) {
  // a/b = outcome/non-outcome in the exposed group, c/d in the unexposed.
  const or = (a / b) / (c / d);
  const seLog = Math.sqrt(1 / a + 1 / b + 1 / c + 1 / d);
  const logOr = Math.log(or);
  return {
    contrast,
    cells: { a, b, c, d },
    oddsRatio: round(or, 3),
    ciLo: round(Math.exp(logOr - 1.96 * seLog), 3),
    ciHi: round(Math.exp(logOr + 1.96 * seLog), 3),
    method: "Woolf log-OR 95% CI"
  };
}

const UNION_TO_INVENTORY_CODE = { PWK: "pw" };

export function familyByUnionCode(inventoryRows) {
  const familyByInventoryCode = new Map(
    inventoryRows.map((row) => [String(row.code ?? "").trim().toLowerCase(), row.family || ""])
  );
  return (unionCode) => {
    const invCode = UNION_TO_INVENTORY_CODE[unionCode] ?? unionCode.toLowerCase();
    const family = familyByInventoryCode.get(invCode);
    if (!family) throw new Error(`union dictionary code ${unionCode} has no family in dictionary_inventory.csv`);
    return family;
  };
}

export function buildPayload(unionRows, dcsLemmas, crosswalkRows, inventoryRows, { generatedAt } = {}) {
  const familyOf = familyByUnionCode(inventoryRows);
  const crosswalk = foldCrosswalkCoverage(crosswalkRows);

  // Per-lemma pass: strata, per-dict tallies, cube cells, logistic rows.
  const strata = new Map(); // nDicts -> { lemmas, attested }
  const perDict = new Map(); // code -> { lemmas, unique, uniqueAttested }
  const familySet = new Set();
  const lemmaRows = []; // { nDicts, families:Set, attested } for the model
  const cube = new Map(); // "u|h|a" -> count
  const tripleExplicit = [];
  const tripleMissing = [];
  let unionLemmas = 0;
  let unionAttested = 0;
  let mwLemmas = 0;
  let mwUnique = 0;
  let mwHeritageCovered = 0;
  let mwCrosswalkMissing = 0;
  const seen = new Set();

  for (const row of unionRows) {
    const { normalized } = normalizeLemma(row.slp1);
    if (!normalized || seen.has(normalized)) continue;
    seen.add(normalized);
    const nDicts = Number(row.n_dicts);
    const dicts = row.dicts.split(" ").filter(Boolean);
    if (!(nDicts > 0) || dicts.length !== nDicts) {
      throw new Error(`union row ${row.slp1}: n_dicts ${row.n_dicts} disagrees with dicts list "${row.dicts}"`);
    }
    const attested = dcsLemmas[normalized]?.attested === true;
    unionLemmas += 1;
    if (attested) unionAttested += 1;

    let s = strata.get(nDicts);
    if (!s) strata.set(nDicts, (s = { lemmas: 0, attested: 0 }));
    s.lemmas += 1;
    if (attested) s.attested += 1;

    const families = new Set();
    for (const code of dicts) {
      const family = familyOf(code);
      families.add(family);
      familySet.add(family);
      let d = perDict.get(code);
      if (!d) perDict.set(code, (d = { code, family, lemmas: 0, unique: 0, uniqueAttested: 0 }));
      d.lemmas += 1;
      if (nDicts === 1) {
        d.unique += 1;
        if (attested) d.uniqueAttested += 1;
      }
    }
    lemmaRows.push({ nDicts, families, attested });

    if (dicts.includes("MW")) {
      mwLemmas += 1;
      const isUnique = nDicts === 1;
      if (isUnique) mwUnique += 1;
      const tier = crosswalk.get(normalized);
      const heritageCovered = tier === "anchored" || tier === "covered-no-anchor";
      if (heritageCovered) mwHeritageCovered += 1;
      if (tier === undefined) mwCrosswalkMissing += 1;
      const key = `${isUnique ? 1 : 0}|${heritageCovered ? 1 : 0}|${attested ? 1 : 0}`;
      cube.set(key, (cube.get(key) ?? 0) + 1);
      if (isUnique && !heritageCovered && !attested) {
        (tier === "absent" ? tripleExplicit : tripleMissing).push(normalized);
      }
    }
  }

  const byMultiplicity = [...strata.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([nDicts, s]) => {
      const ci = wilson(s.attested, s.lemmas);
      return {
        nDicts,
        lemmas: s.lemmas,
        attested: s.attested,
        rate: round(s.attested / s.lemmas),
        ciLo: round(ci.lo),
        ciHi: round(ci.hi)
      };
    });

  const perDictRows = [...perDict.values()]
    .sort((a, b) => compareLemma(a.code, b.code))
    .map((d) => {
      const ci = d.unique > 0 ? wilson(d.uniqueAttested, d.unique) : { lo: null, hi: null };
      return {
        code: d.code,
        family: d.family,
        lemmas: d.lemmas,
        unique: d.unique,
        uniqueAttested: d.uniqueAttested,
        uniqueAttestedShare: d.unique > 0 ? round(d.uniqueAttested / d.unique) : null,
        ciLo: round(ci.lo),
        ciHi: round(ci.hi)
      };
    });

  // Logistic model: attested ~ n_dicts + family-presence indicators.
  const familyTerms = [...familySet].sort(compareLemma);
  const X = lemmaRows.map((r) => [1, r.nDicts, ...familyTerms.map((f) => (r.families.has(f) ? 1 : 0))]);
  const yVec = lemmaRows.map((r) => (r.attested ? 1 : 0));
  const termNames = ["(intercept)", "n_dicts", ...familyTerms.map((f) => `family:${f}`)];
  // A degenerate input (tiny fixture, separated stratum) can make the
  // information matrix singular; keep the payload buildable and let
  // validate-ghost-stock enforce convergence on the production packet.
  let fit;
  let fitError = null;
  try {
    fit = fitLogistic(X, yVec);
  } catch (e) {
    fit = null;
    fitError = e.message;
  }
  const logistic = {
    model: "attested ~ n_dicts + family-presence indicators (one 0/1 term per family: lemma appears in >=1 dictionary of that family)",
    n: lemmaRows.length,
    converged: fit?.converged ?? false,
    iterations: fit?.iterations ?? 0,
    ...(fitError ? { error: fitError } : {}),
    mcFaddenR2: fit ? round(fit.mcFaddenR2) : null,
    logLik: fit ? round(fit.logLik, 1) : null,
    nullLogLik: fit ? round(fit.nullLogLik, 1) : null,
    terms: fit
      ? termNames.map((term, j) => ({
          term,
          estimate: round(fit.beta[j]),
          se: round(fit.se[j]),
          z: round(fit.beta[j] / fit.se[j], 2)
        }))
      : [],
    note:
      "Descriptive, not confirmatory: family presence overlaps n_dicts by construction (more dictionaries usually means more families), so coefficients partition shared variance; read signs and magnitudes, not p-values."
  };

  const cell = (u, h, a) => cube.get(`${u}|${h}|${a}`) ?? 0;
  const cells = [];
  for (const u of [1, 0]) {
    for (const h of [1, 0]) {
      for (const a of [1, 0]) {
        cells.push({ mwUnique: u === 1, heritageCovered: h === 1, dcsAttested: a === 1, lemmas: cell(u, h, a) });
      }
    }
  }
  const heritageCube = {
    scope: "union lemmas whose dictionary list includes MW",
    mwLemmas,
    cells,
    oddsRatios: [
      woolfOddsRatio(
        "Heritage-uncovered -> DCS-unattested (all MW lemmas)",
        cell(1, 0, 0) + cell(0, 0, 0),
        cell(1, 0, 1) + cell(0, 0, 1),
        cell(1, 1, 0) + cell(0, 1, 0),
        cell(1, 1, 1) + cell(0, 1, 1)
      ),
      woolfOddsRatio(
        "MW-unique -> DCS-unattested (all MW lemmas)",
        cell(1, 0, 0) + cell(1, 1, 0),
        cell(1, 0, 1) + cell(1, 1, 1),
        cell(0, 0, 0) + cell(0, 1, 0),
        cell(0, 0, 1) + cell(0, 1, 1)
      ),
      woolfOddsRatio(
        "Heritage-uncovered -> DCS-unattested (within MW-unique lemmas)",
        cell(1, 0, 0),
        cell(1, 0, 1),
        cell(1, 1, 0),
        cell(1, 1, 1)
      )
    ]
  };

  tripleExplicit.sort(compareLemma);
  tripleMissing.sort(compareLemma);
  const tripleFilter = {
    evidenceGrade: "inferred",
    total: tripleExplicit.length + tripleMissing.length,
    ranking:
      "Two evidence tiers, stronger first: explicitUncovered (crosswalk covered_flag=0 — Heritage's own MW<->DICO alignment saw the key and did not cover it) ranks above crosswalkMissing (key absent from the crosswalk entirely — weaker, could be a key-normalization artifact). Alphabetical within tier; no per-row score is asserted.",
    routing:
      "Ghost CANDIDATES for the H5-style review queue (H5_GHOST_ANOMALY_SCOPE.md discipline): each row needs a source read before any 'ghost word' claim — absence from two modern witnesses is evidence of rarity, not proof of non-existence.",
    explicitUncovered: tripleExplicit,
    crosswalkMissing: tripleMissing
  };

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "SanskritLexicography/HeadwordLists/union/union_headwords.tsv",
      "SanskritLexicography/HeadwordLists/mw_heritage_crosswalk.tsv",
      "data/dcs/dcs_lemma_summary.json",
      "src/data/lexicographic-structure/dictionary_inventory.csv",
      "scripts/build-ghost-stock.mjs"
    ],
    method:
      "Normalize each union_headwords.tsv slp1 key with the canonical sanskrit-util slp1_norm (scripts/lib/dict-normalize.mjs), then look it up in the VisualDCS dcs_lemma_summary.json lemma map (attested flag; same normalized keyspace). PH4: per-n_dicts attestation rates with Wilson 95% score intervals; per-dictionary unique-lemma attested share; deterministic IRLS logistic regression of attested on n_dicts plus family-presence indicators (families from dictionary_inventory.csv). PH6: for lemmas listing MW, fold mw_heritage_crosswalk.tsv onto the same normalized key (anchor beats covered-no-anchor beats absent, as in build-heritage-witness.mjs) and cross-tabulate MW-uniqueness x Heritage coverage x DCS attestation; odds ratios carry Woolf log-OR 95% CIs. The triple filter (MW-unique AND Heritage-uncovered AND DCS-unattested) is emitted as a two-tier ranked candidate queue, evidence grade inferred.",
    totals: {
      unionLemmas,
      unionAttested,
      attestedPct: round(unionAttested / unionLemmas),
      dcsLemmas: Object.keys(dcsLemmas).length,
      mwLemmas,
      mwUnique,
      mwHeritageCovered,
      mwCrosswalkMissing,
      tripleFilter: tripleFilter.total
    },
    byMultiplicity,
    perDict: perDictRows,
    logistic,
    heritageCube,
    tripleFilter,
    limitations: [
      "DCS attestation is corpus-relative: the Digital Corpus of Sanskrit samples the transmitted literature — 'unattested' means absent from that corpus release, not absent from Sanskrit; specialised vocabulary (Buddhist, epigraphic, scientific) is under-sampled by construction.",
      "The union backbone and the DCS summary key on normalized SLP1 (accents and homonym digits stripped); homonyms collapse onto one row, so a lemma is 'attested' if ANY homonym is.",
      "Heritage coverage joins only MW lemmas (the crosswalk is MW-keyed); crosswalkMissing rows (MW union keys absent from the crosswalk) are kept as a separate, weaker tier because absence may be a key-mismatch artifact rather than a Heritage verdict.",
      "The logistic model is descriptive: n_dicts and family presence are collinear by construction, sampling is the whole population (no sampling error in the usual sense), and no causal reading is licensed.",
      "The triple-filter queue is graded inferred — candidates for review, not asserted ghost words; a source read (H5 discipline) decides each row."
    ],
    boundary: [
      "union_headwords.tsv and mw_heritage_crosswalk.tsv are owned by SanskritLexicography and consumed read-only from the sibling checkout; dcs_lemma_summary.json is the frozen VisualDCS export per docs/VISUALDCS_CONSUMPTION_CONTRACT.md (no DCS ingestion in csl-atlas). Heritage is cited/joined, never cloned (LGPLLR). Rendering owner repo: csl-atlas."
    ]
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
  return payload;
}

function writeSourceEnvelope(payload, dcsMeta) {
  let commit = "unknown";
  let siblingCommit = "unknown";
  try {
    commit = execSync("git rev-parse HEAD", { encoding: "utf8" }).trim();
  } catch {}
  try {
    siblingCommit = execSync(`git -C "${SIBLING_ROOT}" rev-parse HEAD`, { encoding: "utf8" }).trim();
  } catch {}
  const envelope = {
    dataset: "ghost_stock",
    commit,
    unionRepo: "https://github.com/gasyoun/SanskritLexicography",
    unionPath: "HeadwordLists/union/union_headwords.tsv",
    crosswalkPath: "HeadwordLists/mw_heritage_crosswalk.tsv",
    siblingCommit,
    dcsCorpusRelease: dcsMeta?.corpusRelease ?? null,
    generatedAt: payload.generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: payload.sourceFiles,
    schemaVersion: SCHEMA_VERSION
  };
  fs.writeFileSync(SOURCE_OUT, `${JSON.stringify(envelope, null, 2)}\n`);
}

function main() {
  const missing = [UNION_PATH, CROSSWALK_PATH, DCS_SUMMARY_PATH].filter((p) => !fs.existsSync(p));
  if (missing.length > 0) {
    console.error(
      `Required inputs missing:\n${missing.map((m) => `- ${m}`).join("\n")}\n` +
        "This builder needs a sibling SanskritLexicography checkout and the committed DCS summary (the committed src/data/ghost-stock/ghost_stock.json is the CI-safe artifact)."
    );
    process.exit(1);
  }
  const unionRows = parseTsv(fs.readFileSync(UNION_PATH, "utf8"));
  const crosswalkRows = parseTsv(fs.readFileSync(CROSSWALK_PATH, "utf8"));
  const dcsLemmas = parseDcsSummaryFile(DCS_SUMMARY_PATH);
  const dcsMeta = readJsonIfExists(DCS_SUMMARY_PATH, fs);
  const inventoryRows = loadDictionaryInventory();
  const payload = buildPayload(unionRows, dcsLemmas, crosswalkRows, inventoryRows);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  writeSourceEnvelope(payload, dcsMeta);
  console.log(`Wrote ghost-stock packet (${payload.totals.unionLemmas} union lemmas):`);
  console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), SOURCE_OUT)}`);
  console.log(
    `  attested ${payload.totals.unionAttested} (${(payload.totals.attestedPct * 100).toFixed(1)}%); ` +
      `MW lemmas ${payload.totals.mwLemmas}, triple-filter candidates ${payload.totals.tripleFilter}`
  );
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
