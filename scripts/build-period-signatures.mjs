// Build the period-signatures packet (PH3 FREQ-STRAT, H1576; agenda backlog
// #5): join the SanskritLexicography union headword backbone (per-dict
// provenance) against the frozen kosha lemma-frequency release (per-DCS-period
// count vectors) on the normalized SLP1 key, and ask which era of Sanskrit
// each dictionary records.
//
// Per dictionary: a TYPE-WEIGHTED period-share profile (each matched lemma's
// own normalized 10-period vector, averaged — so ubiquitous high-frequency
// lemmas don't drown the signal), a modal-period chi-square against the
// whole-union baseline (with Cramer's V and total-variation distance as
// effect sizes, since n makes p trivially small), and a dated-periods
// chronological centre-of-mass with a seeded-bootstrap 95% CI. Family
// separation is Kruskal-Wallis on the per-dictionary chronological scores —
// honest label: descriptive (n=14 dictionaries in 4 multi-member families).
//
// Boundary-clean: the kosha release is the frozen public export
// (kosha/data/frequency/lemma_frequency.tsv, consumed read-only from the
// sibling checkout) — no VisualDCS/DCS ingestion here. The committed
// data/lexico/period_signatures.json is the CI-safe artifact.
//
// Usage: npm run build-period-signatures   (then npm run validate-period-signatures)

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { parseTsv } from "./build-heritage-witness.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { loadDictionaryInventory } from "./lib/dict-scope.mjs";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";
import { mulberry32 } from "./build-heap-sat.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-period-signatures";
const SIBLING_LEX = path.resolve(process.cwd(), "..", "SanskritLexicography");
const SIBLING_KOSHA = path.resolve(process.cwd(), "..", "kosha");
const UNION_PATH = path.join(SIBLING_LEX, "HeadwordLists", "union", "union_headwords.tsv");
const FREQ_PATH = path.join(SIBLING_KOSHA, "data", "frequency", "lemma_frequency.tsv");
const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const JSON_OUT = path.join(OUT_DIR, "period_signatures.json");
const SOURCE_OUT = path.join(OUT_DIR, "period_signatures.source.json");

const BOOTSTRAP_B = 1000;
const BOOTSTRAP_SEED = 15760802;

// Canonical DCS period vocabulary, exactly as kosha's
// lemma_frequency.meta.json `period_order` spells it (labels are opaque
// strings there — "3200" is the raw form of period 3 / 200 CE). `chron` is
// the conventional bucket midpoint used for the chronological centre-of-mass;
// Epic and Classic are undated DCS layers and stay OUT of the dated score.
export const PERIODS = [
  { key: "9 Vedic", label: "Vedic", chron: -1000 },
  { key: "1 -800", label: "-800", chron: -800 },
  { key: "2 -300", label: "-300", chron: -300 },
  { key: "3200", label: "200", chron: 200 },
  { key: "4700", label: "700", chron: 700 },
  { key: "5 1200", label: "1200", chron: 1200 },
  { key: "6 1700", label: "1700", chron: 1700 },
  { key: "7 1900", label: "1900", chron: 1900 },
  { key: "11 Epic", label: "Epic", chron: null },
  { key: "12 Classic", label: "Classic", chron: null }
];
const PERIOD_INDEX = new Map(PERIODS.map((p, i) => [p.key, i]));

const UNION_TO_INVENTORY_CODE = { PWK: "pw" };

function round(value, digits = 4) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

/** Parse one kosha `periods` cell ("9 Vedic=8283|1 -800=2897|...") to counts. */
export function parsePeriodsField(cell) {
  const counts = new Array(PERIODS.length).fill(0);
  if (!cell) return counts;
  for (const token of cell.split("|")) {
    const eq = token.lastIndexOf("=");
    if (eq < 0) throw new Error(`periods token without '=': "${token}"`);
    const key = token.slice(0, eq).trim();
    const count = Number(token.slice(eq + 1));
    const idx = PERIOD_INDEX.get(key);
    if (idx === undefined) throw new Error(`unknown DCS period label "${key}" (not in kosha period_order)`);
    if (!Number.isFinite(count) || count < 0) throw new Error(`bad period count in token "${token}"`);
    counts[idx] += count;
  }
  return counts;
}

/** Regularized upper incomplete gamma Q(a, x) — chi-square upper tail. */
export function gammaQ(a, x) {
  if (x < 0 || a <= 0) return NaN;
  if (x === 0) return 1;
  const gln = lgamma(a);
  if (x < a + 1) {
    // series for P(a,x), return 1-P
    let ap = a;
    let sum = 1 / a;
    let del = sum;
    for (let i = 0; i < 500; i++) {
      ap += 1;
      del *= x / ap;
      sum += del;
      if (Math.abs(del) < Math.abs(sum) * 1e-14) break;
    }
    return Math.max(0, 1 - sum * Math.exp(-x + a * Math.log(x) - gln));
  }
  // continued fraction for Q(a,x) (modified Lentz)
  let b = x + 1 - a;
  let c = 1 / 1e-300;
  let d = 1 / b;
  let h = d;
  for (let i = 1; i < 500; i++) {
    const an = -i * (i - a);
    b += 2;
    d = an * d + b;
    if (Math.abs(d) < 1e-300) d = 1e-300;
    c = b + an / c;
    if (Math.abs(c) < 1e-300) c = 1e-300;
    d = 1 / d;
    const del = d * c;
    h *= del;
    if (Math.abs(del - 1) < 1e-14) break;
  }
  return Math.exp(-x + a * Math.log(x) - gln) * h;
}

function lgamma(z) {
  // Lanczos approximation, g=7, n=9.
  const g = 7;
  const c = [
    0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313,
    -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6,
    1.5056327351493116e-7
  ];
  if (z < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * z)) - lgamma(1 - z);
  z -= 1;
  let x = c[0];
  for (let i = 1; i < g + 2; i++) x += c[i] / (z + i);
  const t = z + g + 0.5;
  return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x);
}

/** Kruskal-Wallis H (tie-corrected) + chi-square-approximate p. */
export function kruskalWallis(groups) {
  const all = [];
  groups.forEach((values, gi) => values.forEach((v) => all.push({ v, gi })));
  all.sort((a, b) => a.v - b.v);
  const n = all.length;
  // mid-ranks with tie correction
  let tieSum = 0;
  let i = 0;
  while (i < n) {
    let j = i;
    while (j + 1 < n && all[j + 1].v === all[i].v) j += 1;
    const rank = (i + j + 2) / 2;
    for (let k = i; k <= j; k++) all[k].rank = rank;
    const t = j - i + 1;
    if (t > 1) tieSum += t * t * t - t;
    i = j + 1;
  }
  const rankSums = groups.map(() => 0);
  for (const item of all) rankSums[item.gi] += item.rank;
  let h = 0;
  groups.forEach((values, gi) => {
    if (values.length > 0) h += (rankSums[gi] * rankSums[gi]) / values.length;
  });
  h = (12 / (n * (n + 1))) * h - 3 * (n + 1);
  const correction = 1 - tieSum / (n * n * n - n);
  if (correction > 0) h /= correction;
  const df = groups.length - 1;
  return { h, df, p: gammaQ(df / 2, h / 2) };
}

function familyOfUnionCode(inventoryRows) {
  const byCode = new Map(inventoryRows.map((row) => [String(row.code ?? "").trim().toLowerCase(), row]));
  return (code) => {
    const invCode = UNION_TO_INVENTORY_CODE[code] ?? code.toLowerCase();
    const row = byCode.get(invCode);
    if (!row || !row.family) throw new Error(`union dictionary code ${code} has no family in dictionary_inventory.csv`);
    return { family: row.family, year: Number(row.year) };
  };
}

/** Fold kosha rows to Map(normalizedLemma -> summed period-count vector). */
export function koshaPeriodMap(freqRows) {
  const map = new Map();
  for (const row of freqRows) {
    const { normalized } = normalizeLemma(row.lemma_slp1);
    if (!normalized) continue;
    const counts = parsePeriodsField(row.periods);
    if (counts.every((c) => c === 0)) continue;
    const prev = map.get(normalized);
    if (prev) {
      for (let i = 0; i < counts.length; i++) prev[i] += counts[i];
    } else {
      map.set(normalized, counts);
    }
  }
  return map;
}

export function buildPayload(unionRows, freqRows, inventoryRows, { generatedAt, bootstrapB = BOOTSTRAP_B } = {}) {
  const familyOf = familyOfUnionCode(inventoryRows);
  const periodMap = koshaPeriodMap(freqRows);
  const nP = PERIODS.length;

  const perDict = new Map(); // code -> accumulators
  const baseline = { matched: 0, sumShare: new Array(nP).fill(0), modalCounts: new Array(nP).fill(0) };
  let unionLemmas = 0;
  let matchedLemmas = 0;
  const seen = new Set();

  for (const row of unionRows) {
    const { normalized } = normalizeLemma(row.slp1);
    if (!normalized || seen.has(normalized)) continue;
    seen.add(normalized);
    unionLemmas += 1;
    const dicts = row.dicts.split(" ").filter(Boolean);
    const counts = periodMap.get(normalized);

    let share = null;
    let modal = -1;
    let chron = null;
    if (counts) {
      matchedLemmas += 1;
      const total = counts.reduce((a, v) => a + v, 0);
      share = counts.map((v) => v / total);
      let best = -1;
      for (let i = 0; i < nP; i++) {
        if (best < 0 || counts[i] > counts[best]) best = i;
      }
      modal = best;
      let datedSum = 0;
      let datedWeighted = 0;
      for (let i = 0; i < nP; i++) {
        if (PERIODS[i].chron !== null && counts[i] > 0) {
          datedSum += counts[i];
          datedWeighted += counts[i] * PERIODS[i].chron;
        }
      }
      chron = datedSum > 0 ? datedWeighted / datedSum : null;
      baseline.matched += 1;
      for (let i = 0; i < nP; i++) baseline.sumShare[i] += share[i];
      baseline.modalCounts[modal] += 1;
    }

    for (const code of dicts) {
      let d = perDict.get(code);
      if (!d) {
        const meta = familyOf(code);
        perDict.set(
          code,
          (d = {
            code,
            family: meta.family,
            year: meta.year,
            lemmas: 0,
            matched: 0,
            sumShare: new Array(nP).fill(0),
            modalCounts: new Array(nP).fill(0),
            chronScores: []
          })
        );
      }
      d.lemmas += 1;
      if (counts) {
        d.matched += 1;
        for (let i = 0; i < nP; i++) d.sumShare[i] += share[i];
        d.modalCounts[modal] += 1;
        if (chron !== null) d.chronScores.push(chron);
      }
    }
  }

  const baselineShare = baseline.sumShare.map((v) => v / baseline.matched);
  const baselineModalShare = baseline.modalCounts.map((v) => v / baseline.matched);

  const dictRows = [...perDict.values()].sort((a, b) => a.year - b.year || (a.code < b.code ? -1 : 1));
  const rand = mulberry32(BOOTSTRAP_SEED);
  const perDictOut = dictRows.map((d) => {
    const typeShare = d.sumShare.map((v) => v / d.matched);
    // chi-square: modal-period counts vs whole-union expected
    let chi2 = 0;
    for (let i = 0; i < nP; i++) {
      const expected = d.matched * baselineModalShare[i];
      if (expected > 0) chi2 += (d.modalCounts[i] - expected) ** 2 / expected;
    }
    const df = nP - 1;
    const cramersV = Math.sqrt(chi2 / (d.matched * df));
    const tvd = 0.5 * typeShare.reduce((a, v, i) => a + Math.abs(v - baselineShare[i]), 0);

    // seeded bootstrap over the dict's matched-lemma chron scores
    const scores = d.chronScores;
    const meanChron = scores.length > 0 ? scores.reduce((a, v) => a + v, 0) / scores.length : null;
    let ciLo = null;
    let ciHi = null;
    if (scores.length > 1) {
      const means = new Array(bootstrapB);
      for (let b = 0; b < bootstrapB; b++) {
        let sum = 0;
        for (let k = 0; k < scores.length; k++) sum += scores[Math.floor(rand() * scores.length)];
        means[b] = sum / scores.length;
      }
      means.sort((a, b2) => a - b2);
      ciLo = means[Math.floor(0.025 * bootstrapB)];
      ciHi = means[Math.min(bootstrapB - 1, Math.floor(0.975 * bootstrapB))];
    }

    return {
      code: d.code,
      family: d.family,
      year: d.year,
      lemmas: d.lemmas,
      matched: d.matched,
      matchRate: round(d.matched / d.lemmas),
      typeShare: typeShare.map((v) => round(v, 5)),
      modalCounts: d.modalCounts,
      chi2VsUnion: round(chi2, 1),
      chi2Df: df,
      chi2P: round(gammaQ(df / 2, chi2 / 2), 6),
      cramersV: round(cramersV),
      tvdVsUnion: round(tvd),
      meanChron: round(meanChron, 1),
      chronCiLo: round(ciLo, 1),
      chronCiHi: round(ciHi, 1),
      chronN: scores.length
    };
  });

  // Kruskal-Wallis across families with >=2 union dictionaries, on the
  // per-dictionary mean chronological scores.
  const byFamily = new Map();
  for (const row of perDictOut) {
    if (row.meanChron === null) continue;
    if (!byFamily.has(row.family)) byFamily.set(row.family, []);
    byFamily.get(row.family).push(row.meanChron);
  }
  const kwFamilies = [...byFamily.entries()].filter(([, v]) => v.length >= 2).sort((a, b) => (a[0] < b[0] ? -1 : 1));
  const excluded = [...byFamily.entries()].filter(([, v]) => v.length < 2).map(([f]) => f);
  const kw = kruskalWallis(kwFamilies.map(([, v]) => v));
  const kruskal = {
    variable: "per-dictionary mean chronological score (dated periods only)",
    families: kwFamilies.map(([family, values]) => ({ family, dictionaries: values.length, means: values })),
    excludedSingletons: excluded,
    h: round(kw.h, 3),
    df: kw.df,
    pChiSqApprox: round(kw.p, 4),
    evidenceGrade: "descriptive",
    note:
      "Descriptive, not confirmatory: the units are 14 dictionaries in 4 multi-member families, the chi-square approximation to the H distribution is unreliable at these group sizes, and dictionaries share most of their lemma stock so the group samples are not independent. Read the ordering of family medians, not the p-value."
  };

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "SanskritLexicography/HeadwordLists/union/union_headwords.tsv",
      "kosha/data/frequency/lemma_frequency.tsv",
      "data/dictionary_inventory.csv",
      "scripts/build-period-signatures.mjs"
    ],
    method:
      "Normalize both the union_headwords.tsv slp1 keys and the kosha lemma_frequency.tsv lemma_slp1 keys with the canonical sanskrit-util slp1_norm; homonym rows folding onto one normalized key have their period vectors summed. Each matched lemma contributes its own normalized 10-period share vector (kosha `periods`, period vocabulary exactly kosha's period_order). Per dictionary: the TYPE-WEIGHTED mean share vector (each lemma counts once, so ubiquitous lemmas don't dominate); a modal-period (argmax, earlier period on tie) chi-square goodness-of-fit against the whole-union modal distribution with Cramer's V and total-variation distance as effect sizes; and a chronological centre-of-mass over the 8 dated periods (conventional midpoints, Vedic=-1000; Epic/Classic are undated DCS layers and excluded from the score) with a fixed-seed bootstrap (B=" +
      String(bootstrapB) +
      ") 95% percentile CI. Family separation: tie-corrected Kruskal-Wallis on the per-dictionary mean chronological scores across families with >=2 union dictionaries.",
    periods: PERIODS,
    totals: {
      unionLemmas,
      matchedLemmas,
      matchRate: round(matchedLemmas / unionLemmas),
      koshaLemmas: periodMap.size,
      dictionaries: perDictOut.length
    },
    baseline: {
      scope: "all matched union lemmas, each counted once",
      matched: baseline.matched,
      typeShare: baselineShare.map((v) => round(v, 5)),
      modalCounts: baseline.modalCounts
    },
    perDict: perDictOut,
    kruskalWallis: kruskal,
    limitations: [
      "DCS period counts are corpus-relative and heavily uneven across periods; a dictionary's period signature reflects which attested-in-DCS lemmas it lists, not the dictionary's own citations.",
      "Only " +
        String(round((matchedLemmas / unionLemmas) * 100, 1)) +
        "% of union lemmas match a kosha frequency row — the unmatched majority is exactly the corpus-invisible stock the ghost-stock packet (PH4) characterises, so signatures describe each dictionary's CORPUS-VISIBLE slice.",
      "Homonyms collapse on the normalized SLP1 key on both sides of the join; period vectors of collapsed homonyms are summed.",
      "Chronological midpoints are conventions (Vedic=-1000; period labels 3200/4700 are kosha's raw forms of 200/700 CE); Epic and Classic are undated DCS layers excluded from the chronological score but kept in the share vectors.",
      "The chi-square p-values are trivially small at these n — read Cramer's V and the total-variation distance instead.",
      "Kruskal-Wallis is descriptive at n=14 dictionaries; see the kruskalWallis.note."
    ],
    boundary: [
      "union_headwords.tsv is owned by SanskritLexicography and lemma_frequency.tsv by kosha (the frozen public release derived from VisualDCS under its consumption contract); both are consumed read-only from sibling checkouts — no DCS/VisualDCS ingestion in csl-atlas. Rendering owner repo: csl-atlas."
    ]
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(JSON_OUT, fs), payload);
  return payload;
}

function writeSourceEnvelope(payload) {
  let commit = "unknown";
  let lexCommit = "unknown";
  let koshaCommit = "unknown";
  try {
    commit = execSync("git rev-parse HEAD", { encoding: "utf8" }).trim();
  } catch {}
  try {
    lexCommit = execSync(`git -C "${SIBLING_LEX}" rev-parse HEAD`, { encoding: "utf8" }).trim();
  } catch {}
  try {
    koshaCommit = execSync(`git -C "${SIBLING_KOSHA}" rev-parse HEAD`, { encoding: "utf8" }).trim();
  } catch {}
  const envelope = {
    dataset: "period_signatures",
    commit,
    unionRepo: "https://github.com/gasyoun/SanskritLexicography",
    unionPath: "HeadwordLists/union/union_headwords.tsv",
    unionCommit: lexCommit,
    koshaRepo: "https://github.com/gasyoun/kosha",
    koshaPath: "data/frequency/lemma_frequency.tsv",
    koshaCommit,
    generatedAt: payload.generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: payload.sourceFiles,
    schemaVersion: SCHEMA_VERSION
  };
  fs.writeFileSync(SOURCE_OUT, `${JSON.stringify(envelope, null, 2)}\n`);
}

function main() {
  const missing = [UNION_PATH, FREQ_PATH].filter((p) => !fs.existsSync(p));
  if (missing.length > 0) {
    console.error(
      `Required inputs missing:\n${missing.map((m) => `- ${m}`).join("\n")}\n` +
        "This builder needs sibling SanskritLexicography and kosha checkouts (the committed data/lexico/period_signatures.json is the CI-safe artifact)."
    );
    process.exit(1);
  }
  const unionRows = parseTsv(fs.readFileSync(UNION_PATH, "utf8"));
  const freqRows = parseTsv(fs.readFileSync(FREQ_PATH, "utf8"));
  const inventoryRows = loadDictionaryInventory();
  const payload = buildPayload(unionRows, freqRows, inventoryRows);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  writeSourceEnvelope(payload);
  console.log(`Wrote period-signatures packet (${payload.totals.matchedLemmas}/${payload.totals.unionLemmas} union lemmas matched):`);
  console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), SOURCE_OUT)}`);
  console.log(
    `  KW H=${payload.kruskalWallis.h} (df=${payload.kruskalWallis.df}, p~${payload.kruskalWallis.pChiSqApprox}, descriptive)`
  );
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
