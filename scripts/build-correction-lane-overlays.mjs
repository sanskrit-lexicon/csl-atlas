// Build the three H271/DH-memo correction-lane overlays that H306 left open
// (H1579 remainders):
//
//   1. shared-error Sankey / pair edges  → src/data/corrections/shared_error_overlay.json
//   2. correction-front strip           → src/data/corrections/correction_front.json
//   3. QA pressure per maker-QA lemma   → src/data/corrections/qa_pressure.json
//
// Feeds (read-only; never re-derive):
//   - data/forensic/shared_corrections.csv + f4b_report.json  (atlas-owned)
//   - sibling csl-observatory OBS-T correction_events_release.csv (for front)
//   - sibling csl-corrections correction_loci.tsv + H5 maker-QA packet (for pressure)
//
// Committed JSON is the CI-safe artifact. Sibling paths are rebuild-time only.
//
// Usage: npm run build-correction-lane-overlays

import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { parseTsv } from "./build-correction-feed.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-correction-lane-overlays";
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "corrections");

const SHARED_CSV = path.resolve(process.cwd(), "data", "forensic", "shared_corrections.csv");
const F4B_JSON = path.resolve(process.cwd(), "data", "forensic", "f4b_report.json");
const EVENTS_CSV = path.resolve(
  process.cwd(),
  "..",
  "csl-observatory",
  "observatory",
  "site",
  "src",
  "data",
  "correction_events_release.csv"
);
const LOCI_TSV = path.resolve(process.cwd(), "..", "csl-corrections", "data", "derived", "correction_loci.tsv");
const H5_QA_JSON = path.resolve(process.cwd(), "data", "lexico", "h5_maker_qa_candidates.json");

const FRONT_TOP_DICTS = 12;
const ERA_SPLIT = "2019-01-01";
const RECENT_SINCE = "2020-01-01";

function round(value, digits = 4) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

function parseCsv(text) {
  const lines = text.replace(/\r\n/g, "\n").split("\n").filter((l) => l.length > 0);
  if (lines.length === 0) return [];
  const header = splitCsvLine(lines[0]);
  return lines.slice(1).map((line) => {
    const cells = splitCsvLine(line);
    const row = {};
    header.forEach((h, i) => (row[h] = cells[i] ?? ""));
    return row;
  });
}

// Minimal CSV splitter that honours quoted fields with commas/newlines stripped
// to single lines (shared_corrections rows are single-line).
function splitCsvLine(line) {
  const out = [];
  let cur = "";
  let inQ = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQ) {
      if (ch === '"' && line[i + 1] === '"') {
        cur += '"';
        i += 1;
      } else if (ch === '"') {
        inQ = false;
      } else {
        cur += ch;
      }
    } else if (ch === '"') {
      inQ = true;
    } else if (ch === ",") {
      out.push(cur);
      cur = "";
    } else {
      cur += ch;
    }
  }
  out.push(cur);
  return out;
}

function gitHead(cwd = process.cwd()) {
  try {
    return execSync("git rev-parse HEAD", { cwd, encoding: "utf8" }).trim();
  } catch {
    return "unknown";
  }
}

// ---------------------------------------------------------------------------
// 1. Shared-error overlay (forensic F4 / F4b → lineage Sankey edges)
// ---------------------------------------------------------------------------

export function buildSharedErrorOverlay(sharedRows, f4b, { generatedAt } = {}) {
  const byPet = new Map(); // pet_dict -> { count, inPwgissues, examples }
  for (const row of sharedRows) {
    const pet = String(row.pet_dict || "").toLowerCase();
    if (!pet) continue;
    let d = byPet.get(pet);
    if (!d) {
      d = { pet, count: 0, inPwgissues: 0, examples: [] };
      byPet.set(pet, d);
    }
    d.count += 1;
    if (String(row.in_pwgissues).toLowerCase() === "true") d.inPwgissues += 1;
    if (d.examples.length < 8 && row.headword) d.examples.push(row.headword);
  }

  // Edges for a simple three-node Sankey: pet dict → MW shared-corrected headwords.
  // Evidence grade is inferred until a confusion-aware null is reviewed (memo C3).
  const edges = [...byPet.values()]
    .sort((a, b) => b.count - a.count || a.pet.localeCompare(b.pet))
    .map((d) => ({
      source: d.pet.toUpperCase(),
      target: "MW",
      sharedCorrectedHeadwords: d.count,
      inPwgissuesBundle: d.inPwgissues,
      independentOfBundle: d.count - d.inPwgissues,
      examples: d.examples,
      evidenceLabel: "inferred"
    }));

  const ahlborn = f4b
    ? {
        total: f4b.ahlborn_total ?? null,
        sharesError: f4b.ahlborn_shares_error ?? null,
        sharesErrorPct: f4b.ahlborn_shares_error_pct ?? null,
        mwCorrect: f4b.ahlborn_status?.mw_correct ?? null,
        mwAbsent: f4b.ahlborn_status?.mw_absent ?? null
      }
    : null;

  const nullModel = f4b
    ? {
        observedCoCorrected: f4b.null_observed ?? null,
        expected: f4b.null_expected ?? null,
        lift: f4b.null_lift ?? null,
        p: f4b.null_p ?? null,
        verdict: f4b.null_verdict ?? null
      }
    : null;

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedBy: GENERATED_BY,
    dataset: "shared_error_overlay",
    sourceFiles: [
      "data/forensic/shared_corrections.csv",
      "data/forensic/f4b_report.json",
      "scripts/build-correction-lane-overlays.mjs"
    ],
    method:
      "Aggregate atlas forensic shared_corrections.csv by pet dictionary (PW/PWG/SCH headwords also corrected on the MW side). Attach F4b Ahlborn direct-test + co-correction null-model stats already computed by scripts/forensic/f4b_ahlborn_nulltest.py. Edge weight = shared-corrected headword count; the direct test (not the edge weight) is the copy-detection verdict.",
    claim:
      "Shared-corrected headwords concentrate on the PWG/PW→MW lineage edge, but the Ahlborn direct test shows MW does not inherit PWG's mechanical headword errors (2/123 shares error) — the co-correction lift is convergence + editorial coupling, not copied mistakes (APPARATUS-NOT-ERRORS).",
    evidenceLabel: "inferred",
    reviewStatus: "machine-reviewed",
    ownerRepo: "csl-atlas",
    hypothesisId: "APPARATUS-NOT-ERRORS",
    totals: {
      sharedCorrectionRows: sharedRows.length,
      petDicts: edges.length,
      edges: edges.length
    },
    edges,
    ahlbornDirectTest: ahlborn,
    nullModel,
    limitations: [
      "shared_corrections.csv is a forensic sample of co-corrected headwords (n≈290), not a full form-keyed join over correction_loci.tsv (memo C3 rank-4 full build).",
      "Edge weight is raw shared-corrected count, not yet residual above a confusion-aware null; F4b supplies the null on co-correction, not on identical old→new strings.",
      "in_pwgissues=True rows are multi-dict fix bundles by design and inflate co-correction without proving inheritance.",
      "Evidence grade remains inferred until a reviewer promotes the null model."
    ],
    boundary: [
      "Cladistics / APPARATUS-NOT-ERRORS owner stays csl-atlas (HYPOTHESIS_INDEX). Correction feed owner is csl-corrections; this packet only aggregates already-committed forensic artifacts."
    ]
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(path.join(OUT_DIR, "shared_error_overlay.json"), fs), payload);
  return payload;
}

// ---------------------------------------------------------------------------
// 2. Correction-front strip (OBS-T events → month × dict × component)
// ---------------------------------------------------------------------------

export function buildCorrectionFront(eventRows, { generatedAt, topDicts = FRONT_TOP_DICTS } = {}) {
  const dictTotals = new Map();
  const monthly = new Map(); // month|dict|component
  const era = new Map(); // era|dict|component
  const components = new Map();
  let n = 0;
  let dated = 0;

  for (const row of eventRows) {
    const dict = String(row.dict || "").toLowerCase();
    if (!dict) continue;
    n += 1;
    dictTotals.set(dict, (dictTotals.get(dict) ?? 0) + 1);
    const component = row.error_component || "unattributed";
    components.set(component, (components.get(component) ?? 0) + 1);

    const date = row.date || "";
    if (!/^\d{4}-\d{2}-\d{2}/.test(date)) continue;
    dated += 1;
    const month = date.slice(0, 7);
    const eraKey = date < ERA_SPLIT ? "2014-2018" : "2019-2026";

    const mKey = `${month}|${dict}|${component}`;
    monthly.set(mKey, (monthly.get(mKey) ?? 0) + 1);
    const eKey = `${eraKey}|${dict}|${component}`;
    era.set(eKey, (era.get(eKey) ?? 0) + 1);
  }

  const rankedDicts = [...dictTotals.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([dict, count]) => ({ dict, count }));
  const keep = new Set(rankedDicts.slice(0, topDicts).map((d) => d.dict));

  const monthlyRows = [...monthly.entries()]
    .map(([key, count]) => {
      const [month, dict, component] = key.split("|");
      return { month, dict, component, count };
    })
    .filter((r) => keep.has(r.dict))
    .sort(
      (a, b) =>
        a.month.localeCompare(b.month) ||
        a.dict.localeCompare(b.dict) ||
        a.component.localeCompare(b.component)
    );

  const eraRows = [...era.entries()]
    .map(([key, count]) => {
      const [eraLabel, dict, component] = key.split("|");
      return { era: eraLabel, dict, component, count };
    })
    .filter((r) => keep.has(r.dict))
    .sort(
      (a, b) =>
        a.era.localeCompare(b.era) ||
        a.dict.localeCompare(b.dict) ||
        a.component.localeCompare(b.component)
    );

  // Per-dict era totals (all components) for the strip overview.
  const eraTotals = new Map();
  for (const r of eraRows) {
    const k = `${r.era}|${r.dict}`;
    eraTotals.set(k, (eraTotals.get(k) ?? 0) + r.count);
  }
  const eraOverview = [...eraTotals.entries()]
    .map(([key, count]) => {
      const [eraLabel, dict] = key.split("|");
      return { era: eraLabel, dict, count };
    })
    .sort((a, b) => a.era.localeCompare(b.era) || b.count - a.count);

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedBy: GENERATED_BY,
    dataset: "correction_front",
    sourceFiles: [
      "csl-observatory/observatory/site/src/data/correction_events_release.csv",
      "scripts/build-correction-lane-overlays.mjs"
    ],
    method:
      "Aggregate OBS-T correction_events_release.csv (owner: csl-observatory) into month×dict×error_component cells and an era split at 2019-01-01 (2014–2018 vs 2019–2026). Restrict the committed strip to the top " +
      `${topDicts} dictionaries by event count so the page stays readable; full dict ranking is retained in dictRanking.`,
    claim:
      "The correction front — where editorial attention lands over time and by microstructure component — is a ready-made diachronic lesson; atlas renders, observatory owns the event typology (MW-ATTENTION / OBS-T boundary).",
    evidenceLabel: "derived",
    reviewStatus: "machine-reviewed",
    ownerRepo: "csl-atlas",
    dataOwnerRepo: "csl-observatory",
    eraSplit: ERA_SPLIT,
    topDicts: [...keep],
    totals: {
      events: n,
      dated,
      dicts: dictTotals.size,
      components: components.size,
      stripDicts: keep.size,
      monthlyCells: monthlyRows.length,
      eraCells: eraRows.length
    },
    components: Object.fromEntries([...components.entries()].sort((a, b) => b[1] - a[1])),
    dictRanking: rankedDicts,
    monthly: monthlyRows,
    era: eraRows,
    eraOverview,
    limitations: [
      "OBS-T events are a different grain from csl-corrections change-file loci (normalized IAST edits vs full-line markup diffs); counts are not 1:1 with correction_loci.tsv.",
      "error_component=unattributed is the plurality class — component shares understate true typology resolution.",
      "Corrector identity is deliberately omitted (personal data); /publish-safety-check gate for any corrector-level view.",
      "Strip shows top dicts only; rarer dictionaries are in dictRanking but not monthly cells."
    ],
    boundary: [
      "Data owner: csl-observatory (OBS-T / correction_events_release.csv). Rendering owner: csl-atlas. Never recompute the 9-label component typology here."
    ]
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(path.join(OUT_DIR, "correction_front.json"), fs), payload);
  return payload;
}

// ---------------------------------------------------------------------------
// 3. QA pressure column (human correction density near a maker-QA lemma)
// ---------------------------------------------------------------------------

export function buildQaPressure(h5Packet, lociRows, { generatedAt, recentSince = RECENT_SINCE } = {}) {
  // Index human corrections by normalized k1.
  const byKey = new Map(); // normK1 -> { human, recent, byDict: Map, lastDate }
  for (const row of lociRows) {
    if (row.process === "bulk") continue;
    const k = normalizeLemma(row.k1 || "").normalized;
    if (!k) continue;
    let e = byKey.get(k);
    if (!e) {
      e = { human: 0, recent: 0, byDict: new Map(), lastDate: null };
      byKey.set(k, e);
    }
    e.human += 1;
    const dict = String(row.dict || "").toLowerCase();
    e.byDict.set(dict, (e.byDict.get(dict) ?? 0) + 1);
    const date = row.batch_date || "";
    if (date && (!e.lastDate || date > e.lastDate)) e.lastDate = date;
    if (date >= recentSince) e.recent += 1;
  }

  function pressureFor(lemma, pairDicts = []) {
    const k = normalizeLemma(lemma || "").normalized;
    const e = byKey.get(k);
    if (!e) {
      return {
        lemma,
        formKey: k,
        humanCorrections: 0,
        recentHumanCorrections: 0,
        samePairHumanCorrections: 0,
        lastCorrectionDate: null,
        pressure: "none",
        byDict: {}
      };
    }
    const pairSet = new Set(pairDicts.map((d) => String(d).toLowerCase()));
    let samePair = 0;
    for (const [dict, n] of e.byDict) {
      if (pairSet.has(dict)) samePair += n;
    }
    // Discrete pressure for prioritization: high if recent same-pair activity,
    // medium if any human corrections on the lemma, else none.
    let pressure = "none";
    if (samePair > 0 && e.recent > 0) pressure = "high";
    else if (e.human >= 2 || samePair > 0) pressure = "medium";
    else if (e.human > 0) pressure = "low";
    return {
      lemma,
      formKey: k,
      humanCorrections: e.human,
      recentHumanCorrections: e.recent,
      samePairHumanCorrections: samePair,
      lastCorrectionDate: e.lastDate,
      pressure,
      byDict: Object.fromEntries([...e.byDict.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])))
    };
  }

  const candidates = h5Packet?.qaCandidateRows ?? h5Packet?.candidates ?? [];
  // H5 packet shape: qaCandidates or nested under rows — support both.
  const qaRows =
    h5Packet?.qaCandidates ??
    h5Packet?.qaCandidateRows ??
    (Array.isArray(h5Packet?.rows) ? h5Packet.rows.filter((r) => r.role === "qa") : null) ??
    [];

  // Preferred path: read structured candidate rows from the committed packet.
  let sourceRows = [];
  if (Array.isArray(h5Packet?.qaCandidates) && h5Packet.qaCandidates.length) {
    sourceRows = h5Packet.qaCandidates;
  } else if (Array.isArray(h5Packet?.candidates)) {
    sourceRows = h5Packet.candidates;
  } else {
    // Fall back to walking known top-level arrays used by the H5 builder.
    for (const key of ["qaCandidateRows", "sourceCheckedRows", "rows"]) {
      if (Array.isArray(h5Packet?.[key])) {
        sourceRows = h5Packet[key];
        break;
      }
    }
  }

  // The live H5 packet stores candidates under a nested structure; also accept
  // a flattened list of { lemma, pair, reviewId, ... } if present.
  if (!sourceRows.length && Array.isArray(h5Packet?.calibrationRows)) {
    // Build from reviewId / lemma fields that the markdown generator uses.
    // Actual keys are inspected below in enrichFromPacket.
  }

  const enriched = enrichFromPacket(h5Packet, pressureFor);

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedBy: GENERATED_BY,
    dataset: "qa_pressure",
    sourceFiles: [
      "data/lexico/h5_maker_qa_candidates.json",
      "csl-corrections/data/derived/correction_loci.tsv",
      "scripts/build-correction-lane-overlays.mjs"
    ],
    method:
      "Join each H5 maker-QA candidate lemma AND its nearestReal neighbour (plus calibration controls) to human-process rows of correction_loci.tsv via sanskrit-util slp1_norm form key. Ghost/typo candidates themselves are rarely already corrected; the neighbour form is the usual attention locus. correctionPressure takes the stronger of the two: high = recent human fixes on the form in a pair dictionary; medium = multi-hit or same-pair human fix; low = a single human fix elsewhere; none = no human correction on either form key. Bulk machine batches are excluded.",
    claim:
      "Recent human corrections near a maker-QA locus raise prioritization without creating a new queue page (DH_IMPROVEMENT_MEMO §3.5).",
    evidenceLabel: "derived",
    reviewStatus: "machine-reviewed",
    ownerRepo: "csl-atlas",
    recentSince,
    totals: {
      indexedHumanKeys: byKey.size,
      candidateRows: enriched.candidates.length,
      calibrationRows: enriched.calibration.length,
      high: enriched.candidates.filter((r) => r.pressure === "high").length,
      medium: enriched.candidates.filter((r) => r.pressure === "medium").length,
      low: enriched.candidates.filter((r) => r.pressure === "low").length,
      none: enriched.candidates.filter((r) => r.pressure === "none").length
    },
    candidates: enriched.candidates,
    calibration: enriched.calibration,
    limitations: [
      "Pressure is a form-key co-occurrence count, not a page-neighbourhood density; two lemmas can share a key fold and inflate the signal.",
      "Bulk (BOR/LRV) batches are excluded by design — they dominate volume without meaning 'recent editorial attention'.",
      "Does not prove the candidate is wrong; it only ranks where humans have already been looking.",
      "H5 packet is a fixed 10-row source-check worksheet; pressure is an overlay, not a rewrite of review decisions."
    ],
    boundary: [
      "Maker-QA owner remains the H5 review lane. Correction loci owner is csl-corrections. This packet only joins them."
    ]
  };
  payload.generatedAt = generatedAt ?? generatedAtForPayload(readJsonIfExists(path.join(OUT_DIR, "qa_pressure.json"), fs), payload);
  return payload;
}

function pairDictsFromPair(pair) {
  if (!pair) return [];
  return String(pair)
    .split(/[\/|,]/)
    .map((s) => s.trim())
    .filter(Boolean);
}

const PRESSURE_RANK = { none: 0, low: 1, medium: 2, high: 3 };

function mergePressure(lemmaP, neighbourP) {
  // Prioritize the stronger of (candidate lemma, nearest-real neighbour).
  // Ghost/typo candidates themselves are often uncorrected; the neighbour
  // (the form humans fix toward) is the honest attention signal.
  const rankL = PRESSURE_RANK[lemmaP.pressure] ?? 0;
  const rankN = PRESSURE_RANK[neighbourP?.pressure] ?? 0;
  const winner = rankN > rankL ? neighbourP : lemmaP;
  return {
    ...winner,
    lemma: lemmaP.lemma,
    formKey: lemmaP.formKey,
    humanCorrections: lemmaP.humanCorrections,
    recentHumanCorrections: lemmaP.recentHumanCorrections,
    samePairHumanCorrections: lemmaP.samePairHumanCorrections,
    lastCorrectionDate: lemmaP.lastCorrectionDate ?? neighbourP?.lastCorrectionDate ?? null,
    byDict: lemmaP.byDict,
    nearestReal: neighbourP?.lemma ?? null,
    nearestRealHumanCorrections: neighbourP?.humanCorrections ?? 0,
    nearestRealRecentHumanCorrections: neighbourP?.recentHumanCorrections ?? 0,
    nearestRealSamePairHumanCorrections: neighbourP?.samePairHumanCorrections ?? 0,
    pressure: winner.pressure,
    pressureSource: rankN > rankL ? "nearestReal" : lemmaP.humanCorrections > 0 ? "lemma" : "none"
  };
}

function enrichFromPacket(h5Packet, pressureFor) {
  const candidates = [];
  const calibration = [];

  const calRows = h5Packet?.calibrationRows ?? [];
  for (const row of calRows) {
    const lemma = row.lemma ?? row.subject?.lemma ?? "";
    const pair = row.pair ?? row.subject?.pair ?? "";
    const p = pressureFor(lemma, pairDictsFromPair(pair));
    calibration.push({
      reviewId: row.reviewId ?? null,
      lemma,
      pair,
      ...p
    });
  }

  const qaList = Array.isArray(h5Packet?.qaCandidateRows)
    ? h5Packet.qaCandidateRows
    : Array.isArray(h5Packet?.qaCandidates)
      ? h5Packet.qaCandidates
      : [];

  const seen = new Set();
  for (const row of qaList) {
    const reviewId = row.reviewId ?? row.qaCandidateId ?? null;
    if (reviewId && seen.has(reviewId)) continue;
    if (reviewId) seen.add(reviewId);
    const lemma = row.lemma ?? row.subject?.lemma ?? row.candidateLemma ?? "";
    const nearestReal = row.nearestReal ?? row.machineValue?.nearestReal ?? "";
    const pair = row.pair ?? row.subject?.pair ?? row.machineValue?.pair ?? "";
    const dicts = pairDictsFromPair(pair).concat(row.dictionaries ?? []);
    const lemmaP = pressureFor(lemma, dicts);
    const neighbourP = nearestReal ? pressureFor(nearestReal, dicts) : null;
    const merged = mergePressure(lemmaP, neighbourP);
    candidates.push({
      reviewId,
      lemma,
      pair,
      sampleClass: row.sampleClass ?? row.machineValue?.sampleClass ?? null,
      sourceCheckStatus:
        row.sourceCheckStatus ??
        row.source_check_status ??
        row.sourceCheck?.status ??
        row.sourceCheckDisposition ??
        null,
      ...merged
    });
  }

  return { candidates, calibration };
}

// ---------------------------------------------------------------------------
// Write + main
// ---------------------------------------------------------------------------

function writeJson(file, payload) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
}

function writeSourceEnvelope(dataset, payload, extra = {}) {
  const envelope = {
    dataset,
    commit: gitHead(),
    generatedAt: payload.generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: payload.sourceFiles,
    schemaVersion: SCHEMA_VERSION,
    ...extra
  };
  const out = path.join(OUT_DIR, `${dataset}.source.json`);
  fs.writeFileSync(out, `${JSON.stringify(envelope, null, 2)}\n`);
  return out;
}

export function buildAll(inputs, opts = {}) {
  return {
    sharedError: buildSharedErrorOverlay(inputs.sharedRows, inputs.f4b, opts),
    correctionFront: inputs.eventRows ? buildCorrectionFront(inputs.eventRows, opts) : null,
    qaPressure: inputs.h5Packet && inputs.lociRows ? buildQaPressure(inputs.h5Packet, inputs.lociRows, opts) : null
  };
}

function main() {
  if (!fs.existsSync(SHARED_CSV) || !fs.existsSync(F4B_JSON)) {
    console.error("Missing forensic inputs (shared_corrections.csv / f4b_report.json).");
    process.exit(1);
  }
  const sharedRows = parseCsv(fs.readFileSync(SHARED_CSV, "utf8"));
  const f4b = JSON.parse(fs.readFileSync(F4B_JSON, "utf8"));
  const sharedError = buildSharedErrorOverlay(sharedRows, f4b);
  writeJson(path.join(OUT_DIR, "shared_error_overlay.json"), sharedError);
  writeSourceEnvelope("shared_error_overlay", sharedError);
  console.log(
    `shared_error_overlay: ${sharedError.totals.sharedCorrectionRows} rows → ${sharedError.edges.length} edges`
  );

  if (!fs.existsSync(EVENTS_CSV)) {
    console.error(
      `OBS-T feed not found: ${EVENTS_CSV}\n` +
        "Need a sibling csl-observatory checkout to rebuild correction_front.json."
    );
    process.exit(1);
  }
  const eventRows = parseCsv(fs.readFileSync(EVENTS_CSV, "utf8"));
  const correctionFront = buildCorrectionFront(eventRows);
  writeJson(path.join(OUT_DIR, "correction_front.json"), correctionFront);
  writeSourceEnvelope("correction_front", correctionFront, {
    feedRepo: "https://github.com/sanskrit-lexicon/csl-observatory",
    feedCommit: gitHead(path.resolve(process.cwd(), "..", "csl-observatory"))
  });
  console.log(
    `correction_front: ${correctionFront.totals.events} events → ${correctionFront.totals.monthlyCells} monthly cells (${correctionFront.topDicts.join(", ")})`
  );

  if (!fs.existsSync(LOCI_TSV) || !fs.existsSync(H5_QA_JSON)) {
    console.error("Need sibling csl-corrections correction_loci.tsv and data/lexico/h5_maker_qa_candidates.json for qa_pressure.");
    process.exit(1);
  }
  const lociRows = parseTsv(fs.readFileSync(LOCI_TSV, "utf8"));
  const h5Packet = JSON.parse(fs.readFileSync(H5_QA_JSON, "utf8"));
  const qaPressure = buildQaPressure(h5Packet, lociRows);
  writeJson(path.join(OUT_DIR, "qa_pressure.json"), qaPressure);
  writeSourceEnvelope("qa_pressure", qaPressure, {
    feedRepo: "https://github.com/sanskrit-lexicon/csl-corrections",
    feedCommit: gitHead(path.resolve(process.cwd(), "..", "csl-corrections"))
  });
  console.log(
    `qa_pressure: ${qaPressure.totals.candidateRows} candidates (high ${qaPressure.totals.high} / medium ${qaPressure.totals.medium} / low ${qaPressure.totals.low} / none ${qaPressure.totals.none})`
  );
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
