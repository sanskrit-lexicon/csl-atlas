// Validate the four-axis citation independence packet (PH2 / CITE-4AXIS).
//
// Recomputes the payload from the committed inputs via the builder's exported
// buildPayload (pinning generatedAt to the committed value) and fails (exit 1)
// when:
// - the canonical or site JSON is missing/unparseable;
// - the recomputed payload differs from either committed copy (any drift
//   between inputs and outputs, or between the two copies);
// - structural invariants break: n edges + excluded edges != documented edges,
//   a correlation row lacks its exact permutation p, the 4x4 matrix is not
//   symmetric with a unit diagonal, or a cosine leaves [0,1].
//
// Usage: npm run validate-four-axis-independence   (run after build-four-axis-independence)

import fs from "node:fs";
import path from "node:path";
import { buildPayload } from "./build-four-axis-independence.mjs";

const COMPARISON_PATH = path.resolve(process.cwd(), "data", "lexico", "three_axis_comparison.json");
const APPARATUS_PATH = path.resolve(process.cwd(), "src", "data", "dicts", "citation-apparatus.json");
const GRAPH_EDGES_PATH = path.resolve(process.cwd(), "data", "citations", "ls_citation_edges.tsv");
const JSON_OUT = path.resolve(process.cwd(), "data", "lexico", "four_axis_citation_independence.json");
const SITE_OUT = path.resolve(process.cwd(), "src", "data", "lexico", "four_axis_citation_independence.json");

const errors = [];

function readJson(file) {
  if (!fs.existsSync(file)) {
    errors.push(`Missing required output: ${path.relative(process.cwd(), file)}`);
    return null;
  }
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (e) {
    errors.push(`Unparseable JSON: ${path.relative(process.cwd(), file)} (${e.message})`);
    return null;
  }
}

const committed = readJson(JSON_OUT);
const siteCopy = readJson(SITE_OUT);

if (committed && siteCopy) {
  if (JSON.stringify(committed) !== JSON.stringify(siteCopy)) {
    errors.push("Canonical data/lexico copy and site src/data/lexico copy differ — re-run the builder.");
  }

  const comparison = JSON.parse(fs.readFileSync(COMPARISON_PATH, "utf8"));
  const apparatus = JSON.parse(fs.readFileSync(APPARATUS_PATH, "utf8"));
  const graphEdgesTsv = fs.readFileSync(GRAPH_EDGES_PATH, "utf8");
  const recomputed = buildPayload(comparison, apparatus, graphEdgesTsv, committed.generatedAt);
  if (JSON.stringify(recomputed) !== JSON.stringify(committed)) {
    errors.push("Committed packet does not match a recomputation from its inputs — inputs changed or the file was hand-edited; re-run the builder.");
  }

  if (committed.n + committed.edgeShrinkage.excludedEdges.length !== committed.nDocumentedEdges) {
    errors.push(`Edge accounting broken: n=${committed.n} + excluded=${committed.edgeShrinkage.excludedEdges.length} != documented=${committed.nDocumentedEdges}.`);
  }
  for (const c of committed.citationCorrelations) {
    if (!Number.isFinite(c.permutationP) || !Number.isFinite(c.nPermutations)) {
      errors.push(`Correlation row ${c.pair} lacks its exact permutation p.`);
    }
  }
  const byPair = new Map(committed.correlationMatrix.map((m) => [`${m.a}|${m.b}`, m]));
  for (const m of committed.correlationMatrix) {
    if (m.a === m.b && m.pearson !== 1) errors.push(`4x4 matrix diagonal not 1 at ${m.a}.`);
    const mirror = byPair.get(`${m.b}|${m.a}`);
    if (!mirror || mirror.pearson !== m.pearson) errors.push(`4x4 matrix not symmetric at ${m.a}~${m.b}.`);
  }
  for (const e of committed.edges) {
    if (!(e.citationAxis >= 0 && e.citationAxis <= 1)) errors.push(`Citation cosine out of [0,1] on ${e.parent}→${e.child}.`);
  }
}

if (errors.length > 0) {
  console.error(`validate-four-axis-independence: ${errors.length} error(s)`);
  for (const e of errors) console.error(`- ${e}`);
  process.exit(1);
}
console.log(`validate-four-axis-independence: OK (n=${committed.n} testable edges of ${committed.nDocumentedEdges}; max |citation~axis r| = ${committed.findings.maxAbsCitationPearson})`);
