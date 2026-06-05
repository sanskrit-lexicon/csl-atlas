// Build the M6 cross-reference lineage chart input.
//
// M6 asks whether dictionary-internal cross-reference graphs preserve lineage
// signals. This generator keeps the Observable payload compact and
// dictionary-first.
//
// Usage: npm run build-xref-lineage. No backend, no corpus data.

import fs from "node:fs";
import path from "node:path";

const SCHEMA_VERSION = "1.0.0";
const REPORT_PATH = path.resolve(process.cwd(), "data", "lexico", "xref_lineage.json");
const SHARED_EDGES_PATH = path.resolve(process.cwd(), "data", "lexico", "xref_shared_edges.csv");
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "dicts");
const OUT_PATH = path.join(OUT_DIR, "xref-lineage.json");

const LABELS = {
  ap: "AP",
  ap90: "AP90",
  cae: "CAE",
  mw: "MW",
  pwg: "PWG"
};

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function parseCsv(text) {
  const lines = text.trimEnd().split(/\r?\n/);
  const header = lines.shift().split(",");
  return lines.filter(Boolean).map(line => {
    const cells = line.split(",");
    return Object.fromEntries(header.map((h, i) => [h, cells[i] ?? ""]));
  });
}

function label(code) {
  return LABELS[code] ?? code.toUpperCase();
}

function readingFor(pair, stats) {
  if (pair === "ap-ap90") return "positive-control";
  if (pair === "mw-pwg") return "headline-shared-core";
  if (stats.shared_sources <= 2) return "too-few-shared-sources";
  return "comparison";
}

function validate(payload) {
  const errors = [];
  if (!payload.pairs.length) errors.push("no pair rows");
  for (const row of payload.pairs) {
    for (const field of ["jaccardOnSharedSources", "aInheritanceRate", "bInheritanceRate"]) {
      if (row[field] < 0 || row[field] > 1) errors.push(`${row.pair}: ${field} out of range`);
    }
    if (row.overlappingEdges > row.aEdgesOnSharedSources) {
      errors.push(`${row.pair}: overlap exceeds a-side shared-source edges`);
    }
    if (row.overlappingEdges > row.bEdgesOnSharedSources) {
      errors.push(`${row.pair}: overlap exceeds b-side shared-source edges`);
    }
  }
  if (payload.counts.sharedEdges !== payload.sharedEdges.length) {
    errors.push(`sharedEdges count mismatch`);
  }
  if (errors.length) {
    console.error(`Xref-lineage chart build failed with ${errors.length} error(s):`);
    for (const error of errors.slice(0, 25)) console.error(`  - ${error}`);
    process.exit(1);
  }
}

function main() {
  const report = readJson(REPORT_PATH);
  const sharedEdges = parseCsv(fs.readFileSync(SHARED_EDGES_PATH, "utf8"));
  const pairs = Object.entries(report.pairs)
    .map(([pair, stats]) => {
      const [a, b] = pair.split("-");
      return {
        pair,
        a,
        b,
        aLabel: label(a),
        bLabel: label(b),
        label: `${label(a)} x ${label(b)}`,
        reading: readingFor(pair, stats),
        aEdges: stats.a_edges,
        bEdges: stats.b_edges,
        aSources: stats.a_sources,
        bSources: stats.b_sources,
        sharedSources: stats.shared_sources,
        aEdgesOnSharedSources: stats.a_edges_on_shared_sources,
        bEdgesOnSharedSources: stats.b_edges_on_shared_sources,
        overlappingEdges: stats.overlapping_edges,
        jaccardOnSharedSources: stats.jaccard_on_shared_sources,
        aInheritanceRate: stats.a_inheritance_rate,
        bInheritanceRate: stats.b_inheritance_rate,
        sharedSourcesWithSharedTarget: stats.shared_sources_with_shared_target
      };
    })
    .sort((a, b) =>
      b.overlappingEdges - a.overlappingEdges ||
      b.jaccardOnSharedSources - a.jaccardOnSharedSources ||
      a.label.localeCompare(b.label)
    );

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    claim: "M6: cross-reference graphs preserve lineage signals as a shared core, not wholesale descent.",
    evidenceLabel: "derived",
    reviewStatus: "machine-reviewed",
    sourceFiles: [
      "data/lexico/xref_lineage.json",
      "data/lexico/xref_shared_edges.csv",
      "scripts/lexico/m6_xref_lineage.py",
      "scripts/build-xref-lineage.mjs"
    ],
    question: report.question,
    method: report.method,
    verdictMwPwg: report.verdict_mw_pwg,
    counts: {
      pairRows: pairs.length,
      sharedEdges: sharedEdges.length
    },
    pairs,
    sharedEdges,
    assumptions: [
      "Edges are dictionary-internal cross-reference links from M3.",
      "M6 compares normalized source-target edge sets only where both dictionaries cross-reference the same source lemma.",
      "Overlap is a floor because messy multi-part targets fail to match.",
      "No DCS, corpus, standards/export, GitHub, or organization metrics are inputs."
    ],
    warnings: [
      "A shared edge is a lineage signal, not proof of direct copying by itself.",
      "Pairs with very few shared source lemmas are not interpretable as lineage evidence.",
      "MW x PWG shows a shared core plus independent expansion, not wholesale inheritance."
    ]
  };

  validate(payload);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(OUT_PATH, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote ${path.relative(process.cwd(), OUT_PATH)} (${pairs.length} pair rows).`);
}

main();
