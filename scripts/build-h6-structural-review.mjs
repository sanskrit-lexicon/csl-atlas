// Build the H6 structural-register review summary.
//
// H6 is already charted in /tools/structural-register. This artifact compares
// the chart's structural coordinates with L0 known-edge support and emits
// family centroids/outliers as scholar review prompts.
//
// Usage: npm run build-h6-structural-review

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const SCHEMA_VERSION = "1.0.0";
const STRUCTURAL_PATH = path.resolve(process.cwd(), "src", "data", "dicts", "structural-register.json");
const BOOTSTRAP_PATH = path.resolve(process.cwd(), "src", "data", "lexicographic-structure", "L0", "bootstrap_support.csv");
const OUT = path.resolve(process.cwd(), "data", "lexico", "structural_register_h6_review.json");
const OUTLIER_LIMIT = 12;

export function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (ch === '"') {
        quoted = false;
      } else {
        field += ch;
      }
      continue;
    }
    if (ch === '"') quoted = true;
    else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else if (ch !== "\r") {
      field += ch;
    }
  }
  if (field.length || row.length) {
    row.push(field);
    rows.push(row);
  }
  if (!rows.length) return [];
  const header = rows[0];
  return rows.slice(1)
    .filter(values => values.some(value => value !== ""))
    .map(values => Object.fromEntries(header.map((key, index) => [key, values[index] ?? ""])));
}

function mean(values) {
  const finite = values.filter(value => Number.isFinite(value));
  return finite.length ? finite.reduce((sum, value) => sum + value, 0) / finite.length : 0;
}

function round(value, digits = 4) {
  return Number(value.toFixed(digits));
}

function groupBy(rows, keyFn) {
  const map = new Map();
  for (const row of rows) {
    const key = keyFn(row);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(row);
  }
  return map;
}

function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) {
    const key = keyFn(row) || "none";
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

export function structuralDistance(a, b) {
  const citationDeltaPct = Math.abs(a.citationRegisterPct - b.citationRegisterPct);
  const grammarDeltaPct = Math.abs(a.grammarPct - b.grammarPct);
  const distance01 = Math.sqrt(citationDeltaPct ** 2 + grammarDeltaPct ** 2) / Math.sqrt(100 ** 2 + 100 ** 2);
  return {
    citationDeltaPct: round(citationDeltaPct, 2),
    grammarDeltaPct: round(grammarDeltaPct, 2),
    structuralDistance01: round(distance01)
  };
}

export function edgeReviewClass(edge, distance, sameFamily, sameCitationMode) {
  const support = Number(edge.consensus_support ?? 0);
  if (!Number.isFinite(distance.structuralDistance01)) return "blocked-missing-h6-row";
  if (support >= 0.55 && distance.structuralDistance01 <= 0.25 && sameFamily) return "positive-control";
  if (support >= 0.6 && distance.structuralDistance01 > 0.25) return "genealogy-structure-tension";
  if (support < 0.2 && distance.structuralDistance01 <= 0.15 && (sameFamily || sameCitationMode)) return "structural-convergence";
  if (support < 0.2 && distance.structuralDistance01 > 0.35) return "expected-separation";
  return "review";
}

function familyProfiles(rows) {
  const profiles = [];
  for (const [family, familyRows] of groupBy(rows, row => row.familyLabel)) {
    const centroid = {
      citationRegisterPct: mean(familyRows.map(row => row.citationRegisterPct)),
      grammarPct: mean(familyRows.map(row => row.grammarPct))
    };
    const outliers = familyRows
      .map(row => ({
        code: row.code,
        sourceCode: row.sourceCode,
        title: row.title,
        citationRegisterPct: round(row.citationRegisterPct, 2),
        grammarPct: round(row.grammarPct, 2),
        citationRegisterMode: row.citationRegisterMode,
        dominantLayer: row.dominantLayer || "none",
        distanceFromFamilyCentroid01: structuralDistance(row, centroid).structuralDistance01,
        warnings: row.warnings
      }))
      .sort((a, b) => b.distanceFromFamilyCentroid01 - a.distanceFromFamilyCentroid01 || a.code.localeCompare(b.code))
      .slice(0, OUTLIER_LIMIT);
    profiles.push({
      family,
      dictionaryCount: familyRows.length,
      meanCitationRegisterPct: round(centroid.citationRegisterPct, 2),
      meanGrammarPct: round(centroid.grammarPct, 2),
      citationModeCounts: countBy(familyRows, row => row.citationRegisterMode),
      dominantLayerCounts: countBy(familyRows, row => row.dominantLayer),
      warningCount: familyRows.reduce((sum, row) => sum + row.warnings.length, 0),
      outliers
    });
  }
  return profiles.sort((a, b) => b.dictionaryCount - a.dictionaryCount || a.family.localeCompare(b.family));
}

function edgeComparisons(structuralRows, bootstrapRows) {
  const byCode = new Map();
  for (const row of structuralRows) {
    byCode.set(row.code.toUpperCase(), row);
    byCode.set(row.sourceCode.toUpperCase(), row);
  }
  return bootstrapRows.map(edge => {
    const parent = byCode.get(String(edge.parent).toUpperCase());
    const child = byCode.get(String(edge.child).toUpperCase());
    const missing = [!parent ? edge.parent : null, !child ? edge.child : null].filter(Boolean);
    const distance = parent && child
      ? structuralDistance(parent, child)
      : { citationDeltaPct: null, grammarDeltaPct: null, structuralDistance01: Number.NaN };
    const sameFamily = Boolean(parent && child && parent.familyLabel === child.familyLabel);
    const sameCitationMode = Boolean(parent && child && parent.citationRegisterMode === child.citationRegisterMode);
    const row = {
      parent: edge.parent,
      child: edge.child,
      tier: edge.tier,
      consensusSupport: round(Number(edge.consensus_support || 0)),
      nnKnnSupport: round(Number(edge.nn_knn_support || 0)),
      parentFamily: parent?.familyLabel ?? null,
      childFamily: child?.familyLabel ?? null,
      sameFamily,
      parentCitationMode: parent?.citationRegisterMode ?? null,
      childCitationMode: child?.citationRegisterMode ?? null,
      sameCitationMode,
      citationDeltaPct: distance.citationDeltaPct,
      grammarDeltaPct: distance.grammarDeltaPct,
      structuralDistance01: Number.isFinite(distance.structuralDistance01) ? distance.structuralDistance01 : null,
      reviewClass: edgeReviewClass(edge, distance, sameFamily, sameCitationMode),
      missingStructuralRows: missing
    };
    return row;
  });
}

function validate(payload) {
  const errors = [];
  if (payload.ownerRepo !== "csl-atlas") errors.push("ownerRepo must be csl-atlas");
  for (const edge of payload.edgeComparisons) {
    if (edge.structuralDistance01 !== null && (edge.structuralDistance01 < 0 || edge.structuralDistance01 > 1)) {
      errors.push(`${edge.parent}->${edge.child}: distance out of range`);
    }
    if (!edge.reviewClass) errors.push(`${edge.parent}->${edge.child}: missing review class`);
  }
  if (errors.length) {
    console.error(`H6 structural review build failed with ${errors.length} error(s):`);
    for (const error of errors.slice(0, 25)) console.error(`  - ${error}`);
    process.exit(1);
  }
}

export function buildPayload(structural, bootstrapRows) {
  const rows = structural.rows ?? [];
  const profiles = familyProfiles(rows);
  const comparisons = edgeComparisons(rows, bootstrapRows);
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "structural-register-review-artifact",
    claim: "H6: structural register predicts dictionary family, with L0 edge comparison as a review prompt.",
    evidenceLabel: "derived",
    reviewStatus: "machine-reviewed",
    ownerRepo: "csl-atlas",
    generatedBy: "npm run build-h6-structural-review",
    sourceGeneratedAt: structural.generatedAt,
    sourceFiles: [
      "src/data/dicts/structural-register.json",
      "src/data/lexicographic-structure/L0/bootstrap_support.csv",
      "data/dictionary-coverage.json",
      "data/lexico/microstructure_fingerprint.json",
      "scripts/build-structural-register.mjs",
      "scripts/build-h6-structural-review.mjs"
    ],
    counts: {
      dictionaryRows: rows.length,
      familyProfiles: profiles.length,
      l0KnownEdges: comparisons.length,
      positiveControls: comparisons.filter(row => row.reviewClass === "positive-control").length,
      genealogyStructureTensions: comparisons.filter(row => row.reviewClass === "genealogy-structure-tension").length,
      structuralConvergences: comparisons.filter(row => row.reviewClass === "structural-convergence").length
    },
    method: [
      "Use the existing H6 chart coordinates: citation-register share and grammar-marking share.",
      "Summarize family centroids and within-family outliers as interpretation review prompts.",
      "Compare L0 bootstrap known edges against H6 coordinate distance and family/citation-mode agreement.",
      "Treat tensions and convergences as review classes, not as descent claims."
    ],
    familyProfiles: profiles,
    edgeComparisons: comparisons,
    limitations: [
      "H6 coordinates are structural-register signals, not direct genealogy.",
      "A close H6 distance may be genre convergence rather than inheritance.",
      "A distant H6 edge may reflect reformatting, edition policy, or detector blindness.",
      "L0 edge support is used only as atlas-owned dictionary evidence; no external repo data is used."
    ],
    boundary: [
      "This artifact uses dictionary structure, microstructure fingerprints, and L0 atlas genealogy evidence only.",
      "No DCS, corpus, TEI/OntoLex, FrAC, GitHub, or organization-process evidence is used."
    ]
  };
  validate(payload);
  return payload;
}

function main() {
  const structural = JSON.parse(fs.readFileSync(STRUCTURAL_PATH, "utf8"));
  const bootstrapRows = parseCsv(fs.readFileSync(BOOTSTRAP_PATH, "utf8"));
  const payload = buildPayload(structural, bootstrapRows);
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote ${path.relative(process.cwd(), OUT)} (${payload.counts.l0KnownEdges} L0 edge comparisons).`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
