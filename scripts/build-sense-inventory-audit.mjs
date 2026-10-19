// Build the H7098 cross-dictionary sense-inventory audit.
//
// The audit upgrades the /tools/sense-divergence entry-count proxy to a
// sense-unit comparison. It joins three committed layers:
//   1. data/lexico/microstructure_profile.csv — the 7 core dictionaries'
//      entries per normalized lemma (the sampling frame);
//   2. src/data/dicts/sense-depth.json — validated sense-unit counts for the
//      disparity-enriched stratum (MW/AP/PWG/PWK + broad parseable dicts);
//   3. data/lexico/senses_*.jsonl and r2_align_*.json — the R2 sense-splitter
//      output and anchor-sense alignments.
//
// A 500-lemma stratified sample is drawn deterministically: 200
// disparity-enriched lemmas (the committed sense-depth gaps) plus 300 lemmas
// sampled by hash within nCoreDicts strata. MW sense units are recomputed from
// the local csl-orig source with two independent segmenters, which gives the
// automated double-key and Cohen's kappa reported for the sample.
//
// This is NOT a WSD model and does not duplicate the Uprava B3/H6843 lane.
//
// Usage:
//   npm run build-sense-inventory-audit
//   CSL_ATLAS_GENERATED_AT=... npm run build-sense-inventory-audit

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { senseUnitsForDict } from "./lib/dict-feature-adapters.mjs";
import { licenseFields } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const OUT_DIR = path.resolve("data", "sense");
const OUT_JSON = path.join(OUT_DIR, "inventory_audit.json");
const OUT_CSV = path.join(OUT_DIR, "inventory_audit.csv");
const OUT_TSV = path.join(OUT_DIR, "inventory_audit_sample.tsv");
const OUT_SOURCE = path.join(OUT_DIR, "inventory_audit.source.json");
const PROFILE = path.resolve("data", "lexico", "microstructure_profile.csv");
const SENSE_DEPTH = path.resolve("src", "data", "dicts", "sense-depth.json");
const SAMPLE_SIZE = 500;
const DISPARITY_SIZE = 200;
const SEED = "H7098";
const SENSE_DICTS = ["mw", "ap", "pwg", "pw"];
const CORE_DICTS = ["mw", "ap", "pwg", "pw", "wil", "vcp", "skd"];
const LABEL_TO_CODE = {
  MW: "mw", AP: "ap", PWG: "pwg", PWK: "pw", BEN: "ben", GST: "gst",
  LAN: "lan", INM: "inm", VEI: "vei", PE: "pe", IEG: "ieg", SNP: "snp",
  MCI: "mci", PGN: "pgn"
};
const DICT_LABELS = {
  mw: "MW 1899", ap: "AP 1957", pwg: "PWG 1855", pw: "PWK 1879",
  wil: "WIL 1832", vcp: "VCP 1873", skd: "SKD 1822",
  ben: "BEN 1866", gst: "GST", lan: "LAN", inm: "INM", vei: "VEI",
  pe: "PE", ieg: "IEG", snp: "SNP", mci: "MCI", pgn: "PGN"
};

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function hashKey(value) {
  return crypto.createHash("sha256").update(`${SEED}:${value}`).digest("hex");
}

function parseCsv(text) {
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

function csvEscape(value) {
  if (value == null) return "";
  const s = typeof value === "object" ? JSON.stringify(value) : String(value);
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function wilson(k, n, z = 1.959963984540054) {
  if (!n) return { p: null, lo: null, hi: null, n: 0 };
  const p = k / n;
  const denom = 1 + (z * z) / n;
  const centre = (p + (z * z) / (2 * n)) / denom;
  const half = (z * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n))) / denom;
  return { p: Number(p.toFixed(4)), lo: Number(Math.max(0, centre - half).toFixed(4)), hi: Number(Math.min(1, centre + half).toFixed(4)), n };
}

function cohenKappa(pairs) {
  const n = pairs.length;
  if (!n) return { kappa: null, po: null, pe: null, n: 0 };
  let both1 = 0, both0 = 0, a1 = 0, b1 = 0;
  for (const [a, b] of pairs) {
    if (a && b) both1++;
    if (!a && !b) both0++;
    if (a) a1++;
    if (b) b1++;
  }
  const po = (both1 + both0) / n;
  const pe = ((a1 / n) * (b1 / n)) + (((n - a1) / n) * ((n - b1) / n));
  const kappa = pe === 1 ? 0 : (po - pe) / (1 - pe);
  return { kappa: Number(kappa.toFixed(4)), po: Number(po.toFixed(4)), pe: Number(pe.toFixed(4)), n };
}

function bootstrapKappaCi(pairs, iterations = 1000) {
  if (!pairs.length) return { lo: null, hi: null, iterations };
  const out = [];
  let state = 0x7098;
  const rand = () => {
    state = (1103515245 * state + 12345) % 2147483648;
    return state / 2147483648;
  };
  for (let i = 0; i < iterations; i++) {
    const sample = [];
    for (let j = 0; j < pairs.length; j++) sample.push(pairs[Math.floor(rand() * pairs.length)]);
    const k = cohenKappa(sample).kappa;
    if (Number.isFinite(k)) out.push(k);
  }
  out.sort((a, b) => a - b);
  return {
    lo: Number(out[Math.floor(out.length * 0.025)].toFixed(4)),
    hi: Number(out[Math.floor(out.length * 0.975)].toFixed(4)),
    iterations
  };
}

function largestRemainder(counts, total) {
  const sum = Object.values(counts).reduce((a, b) => a + b, 0);
  const raw = Object.fromEntries(Object.entries(counts).map(([k, v]) => [k, (v / sum) * total]));
  const alloc = Object.fromEntries(Object.entries(raw).map(([k, v]) => [k, Math.floor(v)]));
  let left = total - Object.values(alloc).reduce((a, b) => a + b, 0);
  const order = Object.entries(raw).sort((a, b) => (b[1] - Math.floor(b[1])) - (a[1] - Math.floor(a[1])) || a[0].localeCompare(b[0]));
  for (const [k] of order) {
    if (left <= 0) break;
    alloc[k]++; left--;
  }
  return alloc;
}

function sampleUniverse(universe, quotaByStratum) {
  const picked = [];
  for (const [stratum, quota] of Object.entries(quotaByStratum)) {
    const rows = universe.filter(r => String(r.nDicts) === stratum)
      .sort((a, b) => hashKey(a.k1).localeCompare(hashKey(b.k1)) || a.k1.localeCompare(b.k1));
    picked.push(...rows.slice(0, quota));
  }
  return picked;
}

function mwGlossClauseUnits(body) {
  const text = (body || "")
    .replace(/<[^>]+>/g, " ")
    .replace(/\{[^}]*\}/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  const semicolons = (text.match(/;/g) || []).length;
  return Math.max(1, semicolons);
}

function mwIndex(sampleSet) {
  const index = new Map();
  let records = 0;
  let matched = 0;
  for (const rec of iterateDict("mw")) {
    if (!rec.k1) continue;
    records++;
    const normalized = normalizeLemma(rec.k1).normalized;
    if (!sampleSet.has(normalized)) continue;
    matched++;
    const adapterUnits = senseUnitsForDict("mw", rec.body || "") ?? 1;
    const boundaryUnits = mwGlossClauseUnits(rec.body || "");
    const current = index.get(normalized);
    const entry = {
      adapterUnits,
      boundaryUnits,
      line: rec.startLine,
      href: rec.href
    };
    if (!current) {
      index.set(normalized, { entryCount: 1, richest: entry, entries: [entry] });
    } else {
      current.entryCount++;
      current.entries.push(entry);
      if (entry.adapterUnits > current.richest.adapterUnits ||
          (entry.adapterUnits === current.richest.adapterUnits && entry.line < current.richest.line)) {
        current.richest = entry;
      }
    }
  }
  return { index, records, matched };
}

function normalizeMwsAlignments() {
  const files = fs.readdirSync(path.resolve("data", "lexico"))
    .filter(name => /^r2_align_.+\.json$/.test(name));
  const relations = { "=": 0, related: 0, unrelated: 0 };
  const perLemma = [];
  const pairs = [];
  for (const file of files) {
    const payload = readJson(path.resolve("data", "lexico", file));
    const lemma = payload.lemma ?? file.replace(/^r2_align_|\.json$/g, "");
    for (const row of payload.alignments ?? []) {
      const j = Number(row.j);
      const relation = j >= 0.999 ? "=" : j > 0 ? "related" : "unrelated";
      relations[relation]++;
      pairs.push({ lemma, a: row.a, b: row.b, j, relation, cross: Boolean(row.cross) });
    }
    perLemma.push({
      lemma,
      alignmentRows: (payload.alignments ?? []).length,
      crossAlignmentRows: (payload.alignments ?? []).filter(r => r.cross).length
    });
  }
  return { status: "measured-internal-anchor-alignment", files: files.length, relations, perLemma, pairs };
}

function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const warnings = [];

  // ── 1. Sampling frame from the committed microstructure profile ────────────
  const entries = parseCsv(fs.readFileSync(PROFILE, "utf8"));
  const byLemma = new Map();
  for (const row of entries) {
    const dict = row.dict;
    if (!CORE_DICTS.includes(dict)) continue;
    const k1 = (row.k1 ?? "").trim();
    if (!k1) continue;
    if (!byLemma.has(k1)) byLemma.set(k1, {});
    byLemma.get(k1)[dict] = (byLemma.get(k1)[dict] ?? 0) + 1;
  }
  const universe = [...byLemma.entries()]
    .filter(([, counts]) => Object.keys(counts).length >= 2)
    .map(([k1, counts]) => ({ k1, counts, nDicts: Object.keys(counts).length }));
  const universeByStratum = {};
  for (const row of universe) universeByStratum[row.nDicts] = (universeByStratum[row.nDicts] ?? 0) + 1;

  // ── 2. Disparity stratum from committed validated sense adapters ───────────
  const senseDepth = readJson(SENSE_DEPTH);
  const disparityRows = (senseDepth.topDisparities ?? []).map(row => ({
    k1: row.lemma,
    stratum: "disparity",
    coreEntryCounts: byLemma.get(row.lemma) ?? {},
    byDict: row.byDict,
    gap: row.gap,
    deepest: row.deepest,
    examples: row.examples ?? []
  }));
  const disparityLemmas = new Set(disparityRows.map(r => r.k1));

  const targetCoverage = SAMPLE_SIZE - disparityRows.length;
  const coverageUniverse = universe.filter(r => !disparityLemmas.has(r.k1));
  const coverageCounts = {};
  for (const row of coverageUniverse) coverageCounts[row.nDicts] = (coverageCounts[row.nDicts] ?? 0) + 1;
  const quota = largestRemainder(coverageCounts, targetCoverage);
  const coverageRows = sampleUniverse(coverageUniverse, quota).map(row => ({
    k1: row.k1,
    stratum: "coverage",
    coreEntryCounts: row.counts,
    byDict: {},
    gap: null,
    deepest: null,
    examples: []
  }));
  const sample = [...disparityRows, ...coverageRows];
  if (sample.length !== SAMPLE_SIZE) {
    warnings.push(`Sample size ${sample.length} differs from target ${SAMPLE_SIZE}.`);
  }
  const sampleSet = new Set(sample.map(r => r.k1));

  // ── 3. MW live sense units + automated double key ──────────────────────────
  let mw = { index: new Map(), records: 0, matched: 0 };
  if (dictExists("mw")) {
    mw = mwIndex(sampleSet);
  } else {
    warnings.push("Local csl-orig MW source missing; MW double-key is unavailable.");
  }

  const doubleKeyPairs = [];
  const rows = sample.map(row => {
    const mwHit = mw.index.get(row.k1);
    const senseUnits = {};
    for (const [label, units] of Object.entries(row.byDict ?? {})) {
      const code = LABEL_TO_CODE[label] ?? label.toLowerCase();
      const example = (row.examples ?? []).find(e => e.dict === label);
      senseUnits[code] = {
        units,
        method: senseDepth.perDict?.find(d => d.code === code)?.methodId ?? null,
        scope: SENSE_DICTS.includes(code) ? "core" : "broad",
        href: example?.href ?? null,
        line: example?.line ?? null
      };
    }
    let mwDouble = null;
    if (mwHit) {
      mwDouble = {
        adapterUnits: mwHit.richest.adapterUnits,
        boundaryUnits: mwHit.richest.boundaryUnits,
        agreeMultiSense: (mwHit.richest.adapterUnits >= 2) === (mwHit.richest.boundaryUnits >= 2),
        agreeExact: mwHit.richest.adapterUnits === mwHit.richest.boundaryUnits,
        line: mwHit.richest.line,
        href: mwHit.richest.href
      };
      doubleKeyPairs.push([
        mwHit.richest.adapterUnits >= 2,
        mwHit.richest.boundaryUnits >= 2
      ]);
      if (!senseUnits.mw) {
        senseUnits.mw = {
          units: mwHit.richest.adapterUnits,
          method: "mw-sense-section-div",
          scope: "core",
          href: mwHit.richest.href,
          line: mwHit.richest.line,
          provenance: "live-csl-orig"
        };
      }
      if (!row.coreEntryCounts.mw) row.coreEntryCounts.mw = mwHit.entryCount;
    }
    return {
      k1: row.k1,
      stratum: row.stratum,
      nCoreDicts: Object.keys(row.coreEntryCounts).length,
      coreEntryCounts: row.coreEntryCounts,
      senseUnits,
      mwDoubleKey: mwDouble
    };
  });

  // ── 4. Cross-dictionary sense-unit metrics on the disparity stratum ────────
  const senseRows = rows.filter(r => r.stratum === "disparity");
  const senseDictsPresent = [...new Set(senseRows.flatMap(r => Object.keys(r.senseUnits)))]
    .filter(code => senseRows.some(r => r.senseUnits[code]))
    .sort();
  const sensesPerEntry = {};
  for (const code of senseDictsPresent) {
    const vals = senseRows.filter(r => r.senseUnits[code]).map(r => r.senseUnits[code].units);
    const entryVals = senseRows.filter(r => r.senseUnits[code]).map(r => r.coreEntryCounts[code] ?? null).filter(v => v != null);
    sensesPerEntry[code] = {
      dict: DICT_LABELS[code] ?? code.toUpperCase(),
      scope: senseRows.some(r => r.senseUnits[code]?.scope === "core") ? "core" : "broad",
      lemmas: vals.length,
      totalSenses: vals.reduce((a, b) => a + b, 0),
      meanSensesPerEntry: vals.length ? Number((vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(3)) : null,
      multiSenseLemmas: vals.filter(v => v >= 2).length,
      multiSensePct: vals.length ? Number(((100 * vals.filter(v => v >= 2).length) / vals.length).toFixed(1)) : null,
      meanCoreEntries: entryVals.length ? Number((entryVals.reduce((a, b) => a + b, 0) / entryVals.length).toFixed(3)) : null
    };
  }

  const corePresent = SENSE_DICTS.filter(code => senseRows.some(r => r.senseUnits[code]));
  const survival = [];
  for (const from of corePresent) {
    const fromRows = senseRows.filter(r => r.senseUnits[from]);
    for (const to of corePresent) {
      if (from === to) continue;
      const both = fromRows.filter(r => r.senseUnits[to]).length;
      survival.push({
        from,
        to,
        fromLemmas: fromRows.length,
        both,
        rate: fromRows.length ? Number((both / fromRows.length).toFixed(4)) : null,
        ci95: wilson(both, fromRows.length)
      });
    }
  }

  let withTwo = 0, strictDominant = 0, secondaryAtLeast2 = 0, notAllEqual = 0;
  const dominantCounts = {};
  for (const row of senseRows) {
    const vals = corePresent.map(code => [code, row.senseUnits[code]?.units ?? 0])
      .filter(([, units]) => units > 0);
    if (vals.length < 2) continue;
    withTwo++;
    vals.sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
    if (vals[0][1] > vals[1][1]) strictDominant++;
    if (vals[1][1] >= 2) secondaryAtLeast2++;
    if (vals.some(([, units]) => units !== vals[0][1])) notAllEqual++;
    const key = `${vals[0][0]}>${vals[1][0]}`;
    dominantCounts[key] = (dominantCounts[key] ?? 0) + 1;
  }
  const dominantSecondary = {
    lemmasWithAtLeastTwoCoreSenseDicts: withTwo,
    strictDominantLemmas: strictDominant,
    strictDominantRate: withTwo ? Number((strictDominant / withTwo).toFixed(4)) : null,
    secondaryAtLeastTwoSenses: secondaryAtLeast2,
    secondaryAtLeastTwoSensesRate: withTwo ? Number((secondaryAtLeast2 / withTwo).toFixed(4)) : null,
    dominantPairTop: Object.entries(dominantCounts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 10)
      .map(([pair, n]) => ({ pair, lemmas: n })),
    definition: "Dominant = dictionary with the most sense units for a lemma; secondary = second most. Rates use lemmas present in >=2 core sense-segmented dictionaries."
  };
  const disagreement = {
    lemmasWithAtLeastTwoCoreSenseDicts: withTwo,
    lemmasWithAnyCountDifference: notAllEqual,
    rate: withTwo ? Number((notAllEqual / withTwo).toFixed(4)) : null,
    ci95: wilson(notAllEqual, withTwo),
    definition: "Disagreement = the core dictionaries do not all report the same sense-unit count for the lemma. This is structural, not semantic, disagreement."
  };

  // ── 5. Automated double-key kappa ──────────────────────────────────────────
  const kappa = cohenKappa(doubleKeyPairs);
  const kappaCi = bootstrapKappaCi(doubleKeyPairs);
  const exactAgreement = rows.filter(r => r.mwDoubleKey?.agreeExact).length;
  const doubleKey = {
    status: "automated-double-key",
    keyA: "validated MW sense-section <div> adapter (senseUnitsForDict)",
    keyB: "independent gloss-clause splitter (semicolon boundaries in MW body text)",
    unit: "lemma",
    metric: "binary multi-sense (>=2 units)",
    n: kappa.n,
    kappa: kappa.kappa,
    kappaBootstrapCi95: kappaCi,
    observedAgreement: kappa.po,
    expectedAgreement: kappa.pe,
    exactCountAgreement: rows.filter(r => r.mwDoubleKey).length ? Number((exactAgreement / rows.filter(r => r.mwDoubleKey).length).toFixed(4)) : null,
    note: "Automated coding agreement, not human inter-annotator kappa. The two keys read the same source text with independently implemented segmenters; they are not independent human annotators."
  };

  const mws = normalizeMwsAlignments();
  const mwsRelationAlignment = {
    vocabulary: ["=", "superset", "subset", "related"],
    status: "partial",
    measured: {
      "=": mws.relations["="],
      related: mws.relations.related,
      unrelated: mws.relations.unrelated
    },
    notMeasurable: {
      superset: "R2 anchor alignments expose a Jaccard score and shared anchors, not full MWSA sense sets; superset/subset cannot be asserted without the MWSA inventory.",
      subset: "R2 anchor alignments expose a Jaccard score and shared anchors, not full MWSA sense sets; superset/subset cannot be asserted without the MWSA inventory."
    },
    internalAnchorAlignmentFiles: mws.files,
    internalAnchorAlignmentRows: mws.pairs.length,
    perLemma: mws.perLemma,
    source: "data/lexico/r2_align_*.json (R2 anchor sense alignments)"
  };
  const externalInventories = {
    elexisMwsa: {
      status: "unavailable",
      reason: "No ELEXIS MWSA relation inventory is checked into csl-atlas or present in the local workspace; external evaluation is therefore an honest null, not a fabricated match."
    },
    isclsWsd: { citation: "2026.iscls-1.2", status: "cited-not-reimplemented", reason: "Cited for the WSD task framing; this audit does not build or evaluate a WSD model." },
    isclsMwSenseInventory: { citation: "2026.iscls-1.3", status: "cited-not-duplicated", reason: "Cited as external MW sense-inventory prior art; no MW-specific sense inventory is duplicated here." }
  };

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedAt: process.env.CSL_ATLAS_GENERATED_AT || new Date().toISOString(),
    generatedBy: "scripts/build-sense-inventory-audit.mjs",
    goal: "H7098 cross-dictionary sense-inventory audit",
    purpose: "Upgrade entry-count divergence to sense-unit comparison and publish an honest, source-traceable inventory audit.",
    sampleDesign: {
      target: SAMPLE_SIZE,
      achieved: rows.length,
      strata: {
        disparity: disparityRows.length,
        coverage: coverageRows.length
      },
      disparityDefinition: "The committed sense-depth top-200 gaps (largest max-min sense-unit spread); disparity-enriched, not a random population sample.",
      coverageDefinition: "Deterministic SHA-256 sample within nCoreDicts strata from the microstructure-profile universe (lemmas in >=2 of MW, AP, PWG, PWK, WIL, VCP, SKD), excluding disparity lemmas.",
      universeLemmas: universe.length,
      universeByCoreDictCount: universeByStratum,
      coverageQuotaByCoreDictCount: quota,
      seed: SEED
    },
    rows,
    humanGold: {
      status: "blocked",
      reason: "This unattended unit cannot run two blind human keys and adjudication. The published 500-lemma sample carries two automated keys (MW validated section adapter and MW gloss-clause splitter) and an explicit unadjudicated label; no human κ is claimed.",
      sampleFile: "data/sense/inventory_audit_sample.tsv",
      requiredForFullAcceptance: "Two blind human keys plus source-line adjudication on the 500-lemma sample."
    },
    reconciliation: {
      h5950: { lane: "Uprava B3 / ISCLS sense-inventory sweep", reused: "External task framing and the instruction not to rebuild the B3 inventory.", newHere: "Cross-dictionary sense-unit evidence from csl-atlas dictionaries." },
      h6843: { lane: "Uprava B3 MW-Sense-Inventory / Sembank camera-ready", reused: "External MW sense-inventory prior art; no MW inventory duplicated.", newHere: "Cross-dictionary audit and structural disagreement metrics." },
      boundary: "No WSD model, classifier, DCS ingestion, or B3 inventory rebuild in this unit."
    },
    senseDictionaries: sensesPerEntry,
    coreSenseDicts: corePresent,
    crossDictSurvival: survival,
    dominantSecondary,
    disagreement,
    doubleKey,
    mwsRelationAlignment,
    externalInventories,
    references: [
      { id: "2026.iscls-1.2", author: "Hellwig et al.", year: 2026, topic: "ISCLS WSD", use: "task framing and WSD non-duplication" },
      { id: "2026.iscls-1.3", author: "Pradeep et al.", year: 2026, topic: "MW-Sense-Inventory", use: "external MW sense-inventory prior art" }
    ],
    limitations: [
      "The disparity stratum is the committed top-200 sense-depth gap list, not a random sample; population inference is limited to the stated strata.",
      "Cross-dictionary sense units exist only where validated adapters exist (MW, AP, PWG, PWK core; broad adapters where committed). WIL, VCP and SKD have no sense adapter, so they contribute entry coverage but not sense units.",
      "Sense units are structural section/marker counts, not curated semantic senses; labels such as 'dominant' mean 'most sense sections', not 'most meanings'.",
      "MW live recomputation requires a local csl-orig checkout; when it is absent the MW double-key is reported as unavailable.",
      "The reported kappa is automated coding agreement between two segmenter implementations on MW, not human inter-annotator agreement.",
      "No ELEXIS MWSA inventory is available locally, so external MWSA (=, superset, subset, related) evaluation is an honest null; only = and related are measured on internal R2 anchor alignments.",
      "Sense counts may be inflated by dictionary-specific subsection markers (e.g. PWG/PWK <div> blocks); method IDs are recorded per dictionary."
    ],
    warnings
  };

  const previous = fs.existsSync(OUT_JSON) ? readJson(OUT_JSON) : null;
  const canonical = value => JSON.stringify(value, (key, v) => (key === "generatedAt" ? undefined : v));
  if (previous && canonical(previous) === canonical(payload)) payload.generatedAt = previous.generatedAt;

  fs.writeFileSync(OUT_JSON, `${JSON.stringify(payload, null, 2)}\n`);

  const csvRows = rows.map(row => ({
    lemma: row.k1,
    stratum: row.stratum,
    n_core_dicts: row.nCoreDicts,
    core_entry_counts: row.coreEntryCounts,
    sense_units: Object.fromEntries(Object.entries(row.senseUnits).map(([k, v]) => [k, v.units])),
    mw_adapter_units: row.mwDoubleKey?.adapterUnits ?? "",
    mw_gloss_clause_units: row.mwDoubleKey?.boundaryUnits ?? "",
    mw_double_key_agree: row.mwDoubleKey?.agreeMultiSense ?? "",
    mw_source: row.mwDoubleKey?.href ?? ""
  }));
  const columns = ["lemma", "stratum", "n_core_dicts", "core_entry_counts", "sense_units", "mw_adapter_units", "mw_gloss_clause_units", "mw_double_key_agree", "mw_source"];
  fs.writeFileSync(OUT_CSV, `${columns.join(",")}\n${csvRows.map(r => columns.map(c => csvEscape(r[c])).join(",")).join("\n")}\n`);

  const tsvColumns = ["lemma", "stratum", "n_core_dicts", "key_a_mw_adapter_units", "key_b_mw_gloss_units", "key_a_binary_multi", "key_b_binary_multi", "adjudicated_label", "mw_source"];
  const tsvRows = rows.map(row => ({
    lemma: row.k1,
    stratum: row.stratum,
    n_core_dicts: row.nCoreDicts,
    key_a_mw_adapter_units: row.mwDoubleKey?.adapterUnits ?? "",
    key_b_mw_gloss_units: row.mwDoubleKey?.boundaryUnits ?? "",
    key_a_binary_multi: row.mwDoubleKey ? (row.mwDoubleKey.adapterUnits >= 2) : "",
    key_b_binary_multi: row.mwDoubleKey ? (row.mwDoubleKey.boundaryUnits >= 2) : "",
    adjudicated_label: row.mwDoubleKey ? "unadjudicated-automated" : "no-mw-row",
    mw_source: row.mwDoubleKey?.href ?? ""
  }));
  fs.writeFileSync(OUT_TSV, `${tsvColumns.join("\t")}\n${tsvRows.map(r => tsvColumns.map(c => String(r[c] ?? "").replace(/\t/g, " ")).join("\t")).join("\n")}\n`);

  const source = {
    stage: 0,
    createdUtc: payload.generatedAt,
    script: "scripts/build-sense-inventory-audit.mjs",
    goal: "H7098",
    command: "npm run build-sense-inventory-audit",
    inputs: [
      { path: "data/lexico/microstructure_profile.csv", sha256: sha256(PROFILE) },
      { path: "src/data/dicts/sense-depth.json", sha256: sha256(SENSE_DEPTH) },
      ...fs.readdirSync(path.resolve("data", "lexico"))
        .filter(name => /^senses_.+\.jsonl$/.test(name))
        .map(name => ({ path: `data/lexico/${name}`, sha256: sha256(path.resolve("data", "lexico", name)) })),
      ...fs.readdirSync(path.resolve("data", "lexico"))
        .filter(name => /^r2_align_.+\.json$/.test(name))
        .map(name => ({ path: `data/lexico/${name}`, sha256: sha256(path.resolve("data", "lexico", name)) }))
    ],
    liveSources: dictExists("mw")
      ? [{ path: "../csl-orig/v02/mw/mw.txt", records: mw.records, sampleMatches: mw.matched, sha256: sha256("../csl-orig/v02/mw/mw.txt") }]
      : [],
    outputs: [
      { path: "data/sense/inventory_audit.json", sha256: sha256(OUT_JSON) },
      { path: "data/sense/inventory_audit.csv", sha256: sha256(OUT_CSV) },
      { path: "data/sense/inventory_audit_sample.tsv", sha256: sha256(OUT_TSV) }
    ],
    notes: [
      "The 200-lemma disparity stratum comes from committed sense-depth adapters, not from a new parser promotion.",
      "The MW double-key recomputes sense units live from csl-orig when available.",
      "No ELEXIS MWSA inventory was present; external evaluation is null."
    ]
  };
  fs.writeFileSync(OUT_SOURCE, `${JSON.stringify(source, null, 2)}\n`);

  console.log(`Wrote ${OUT_JSON}: ${rows.length} lemmas (${disparityRows.length} disparity + ${coverageRows.length} coverage)`);
  console.log(`Sense dictionaries: ${corePresent.join(", ")}; kappa ${kappa.kappa} (n=${kappa.n}, CI ${kappaCi.lo}..${kappaCi.hi})`);
  console.log(`Wrote ${OUT_CSV}, ${OUT_TSV} and ${OUT_SOURCE}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();

export { cohenKappa, mwGlossClauseUnits, wilson, largestRemainder };
