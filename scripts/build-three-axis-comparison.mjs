// Build a machine-readable three-axis comparison packet for known dictionary families.
//
// The packet keeps content, convention, and microstructure/register evidence
// separate. It records no human decisions and does not update public pages.
//
// Usage: npm run build-three-axis-comparison

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { parseCsv, structuralDistance } from "./build-h6-structural-review.mjs";

const SCHEMA_VERSION = "1.0.0";
const GENERATED_BY = "npm run build-three-axis-comparison";
const BOOTSTRAP_PATH = path.resolve(process.cwd(), "src", "data", "lexicographic-structure", "L0", "bootstrap_support.csv");
const JACCARD_PATH = path.resolve(process.cwd(), "src", "data", "lexicographic-structure", "sanhw1_jaccard.csv");
const CONVENTION_SCATTER_PATH = path.resolve(process.cwd(), "src", "data", "lexicographic-structure", "L0", "content_convention_scatter.csv");
const STRUCTURAL_PATH = path.resolve(process.cwd(), "src", "data", "dicts", "structural-register.json");
const MICROSTRUCTURE_PATH = path.resolve(process.cwd(), "data", "lexico", "microstructure_fingerprint.json");
const JSON_OUT = path.resolve(process.cwd(), "data", "lexico", "three_axis_comparison.json");
const MARKDOWN_OUT = path.resolve(process.cwd(), "docs", "THREE_AXIS_COMPARISON.md");

export const EXPECTED_EDGE_IDS = Object.freeze([
  "three-axis:WIL:YAT",
  "three-axis:WIL:SHS",
  "three-axis:YAT:SHS",
  "three-axis:PWG:PW",
  "three-axis:PW:CCS",
  "three-axis:CCS:CAE",
  "three-axis:MW72:MW",
  "three-axis:AP90:AP",
  "three-axis:PWG:MW72",
  "three-axis:PWG:MW",
  "three-axis:PWG:SCH",
  "three-axis:BOP:MW",
  "three-axis:BEN:MW"
]);

const FOCUS_EDGE_IDS = Object.freeze([
  "three-axis:PWG:MW",
  "three-axis:CCS:CAE",
  "three-axis:WIL:SHS",
  "three-axis:PWG:SCH"
]);

function round(value, digits = 4) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

function pairKey(a, b) {
  return `${String(a).toUpperCase()}|${String(b).toUpperCase()}`;
}

function unorderedPairKey(a, b) {
  return [String(a).toUpperCase(), String(b).toUpperCase()].sort().join("|");
}

function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) {
    const key = keyFn(row);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

function indexJaccard(rows) {
  const index = new Map();
  for (const row of rows) {
    index.set(unorderedPairKey(row.dict_a, row.dict_b), row);
  }
  return index;
}

function indexConvention(rows) {
  const index = new Map();
  for (const row of rows) {
    index.set(unorderedPairKey(row.a, row.b), row);
  }
  return index;
}

function indexStructural(rows) {
  const index = new Map();
  for (const row of rows) {
    index.set(String(row.code).toUpperCase(), row);
    index.set(String(row.sourceCode).toUpperCase(), row);
  }
  return index;
}

function indexMicrostructure(data) {
  const index = new Map();
  for (const [code, row] of Object.entries(data.dicts || {})) {
    index.set(code.toUpperCase(), row);
  }
  return index;
}

function contentForPair(jaccardIndex, parent, child) {
  const row = jaccardIndex.get(unorderedPairKey(parent, child));
  if (!row) return null;
  const a = String(row.dict_a).toUpperCase();
  const b = String(row.dict_b).toUpperCase();
  const parentCode = String(parent).toUpperCase();
  const childCode = String(child).toUpperCase();
  if (a === parentCode && b === childCode) {
    return {
      intersection: Number(row.intersection),
      jaccard: round(Number(row.jaccard)),
      parentInChild: round(Number(row.a_in_b)),
      childInParent: round(Number(row.b_in_a)),
      parentSize: Number(row.size_a),
      childSize: Number(row.size_b)
    };
  }
  if (b === parentCode && a === childCode) {
    return {
      intersection: Number(row.intersection),
      jaccard: round(Number(row.jaccard)),
      parentInChild: round(Number(row.b_in_a)),
      childInParent: round(Number(row.a_in_b)),
      parentSize: Number(row.size_b),
      childSize: Number(row.size_a)
    };
  }
  return null;
}

function conventionForPair(conventionIndex, parent, child) {
  const row = conventionIndex.get(unorderedPairKey(parent, child));
  if (!row) return null;
  const similarity = Number(row.convention_similarity);
  return {
    conventionSimilarity: round(similarity),
    conventionDistance: round(1 - similarity)
  };
}

function layerJaccard(parent, child) {
  const parentLayers = new Set(parent?.layers_present || []);
  const childLayers = new Set(child?.layers_present || []);
  if (!parentLayers.size && !childLayers.size) return 1;
  const union = new Set([...parentLayers, ...childLayers]);
  const intersection = [...parentLayers].filter(layer => childLayers.has(layer));
  return round(intersection.length / union.size);
}

function contentBand(parentInChild) {
  if (parentInChild >= 0.85) return "high-content-overlap";
  if (parentInChild >= 0.5) return "medium-content-overlap";
  return "low-content-overlap";
}

function conventionBand(similarity) {
  if (similarity >= 0.7) return "high-convention-overlap";
  if (similarity >= 0.45) return "medium-convention-overlap";
  return "low-convention-overlap";
}

function microstructureBand(similarity, layerOverlap) {
  if (similarity >= 0.8 && layerOverlap >= 0.5) return "close-register-and-layers";
  if (similarity >= 0.6 || layerOverlap >= 0.5) return "partial-register-or-layer-overlap";
  return "divergent-register-and-layers";
}

export function axisReadingForScores({ parentInChild, conventionSimilarity, microstructureSimilarity }) {
  const highContent = parentInChild >= 0.85;
  const lowContent = parentInChild < 0.5;
  const highConvention = conventionSimilarity >= 0.7;
  const lowConvention = conventionSimilarity < 0.45;
  const closeMicrostructure = microstructureSimilarity >= 0.75;

  if (highContent && highConvention && closeMicrostructure) return "aligned-content-convention-register";
  if (highContent && lowConvention && !closeMicrostructure) return "content-carried-with-convention-and-register-recoding";
  if (highContent && lowConvention) return "content-carried-with-convention-recoding";
  if (highContent && highConvention && !closeMicrostructure) return "content-and-convention-aligned-register-shift";
  if (lowContent && highConvention) return "shared-convention-with-narrow-content-overlap";
  if (lowContent && closeMicrostructure) return "register-convergence-with-narrow-content-overlap";
  if (highContent) return "content-overlap-needs-axis-review";
  return "mixed-axis-review";
}

function interpretationForReading(reading) {
  const interpretations = {
    "aligned-content-convention-register": "All three axes point in the same direction; use as a faithful-format/register comparison prompt.",
    "content-carried-with-convention-and-register-recoding": "High lexical containment is paired with recoded convention and shifted register; do not collapse this into a simple descent score.",
    "content-carried-with-convention-recoding": "The content axis is high while house style diverges; this is a reformatting prompt.",
    "content-and-convention-aligned-register-shift": "Content and convention align, but register/microstructure changed enough to need a separate reading.",
    "shared-convention-with-narrow-content-overlap": "The house style is close even though exposed lemma overlap is narrow; this can happen for supplements or convention-family members.",
    "register-convergence-with-narrow-content-overlap": "Structural register is close despite narrow content overlap; treat as convergence until source-read.",
    "content-overlap-needs-axis-review": "Content overlap is high, but the other axes do not form a single stable reading.",
    "mixed-axis-review": "The three axes disagree or remain weak; keep as a review/control row."
  };
  return interpretations[reading] || interpretations["mixed-axis-review"];
}

function buildComparisonRow(edge, indexes) {
  const parent = String(edge.parent).toUpperCase();
  const child = String(edge.child).toUpperCase();
  const content = contentForPair(indexes.jaccard, parent, child);
  const convention = conventionForPair(indexes.convention, parent, child);
  const parentStructural = indexes.structural.get(parent);
  const childStructural = indexes.structural.get(child);
  const parentMicro = indexes.microstructure.get(parent);
  const childMicro = indexes.microstructure.get(child);
  const distance = parentStructural && childStructural ? structuralDistance(parentStructural, childStructural) : null;
  const layers = layerJaccard(parentMicro, childMicro);
  const structuralSimilarity = distance ? round(1 - distance.structuralDistance01) : null;
  const microSimilarity = structuralSimilarity === null ? null : round((structuralSimilarity + layers) / 2);
  const reading = axisReadingForScores({
    parentInChild: content?.parentInChild ?? 0,
    conventionSimilarity: convention?.conventionSimilarity ?? 0,
    microstructureSimilarity: microSimilarity ?? 0
  });

  return {
    rowId: `three-axis:${parent}:${child}`,
    parent,
    child,
    tier: edge.tier,
    conventionBootstrapSupport: round(Number(edge.consensus_support || 0)),
    nnKnnSupport: round(Number(edge.nn_knn_support || 0)),
    contentAxis: {
      parentInChild: content?.parentInChild ?? null,
      childInParent: content?.childInParent ?? null,
      jaccard: content?.jaccard ?? null,
      intersection: content?.intersection ?? null,
      parentSize: content?.parentSize ?? null,
      childSize: content?.childSize ?? null,
      band: content ? contentBand(content.parentInChild) : "missing-content-axis"
    },
    conventionAxis: {
      conventionSimilarity: convention?.conventionSimilarity ?? null,
      conventionDistance: convention?.conventionDistance ?? null,
      bootstrapSupport: round(Number(edge.consensus_support || 0)),
      band: convention ? conventionBand(convention.conventionSimilarity) : "missing-convention-axis"
    },
    microstructureAxis: {
      parentFamily: parentStructural?.familyLabel ?? null,
      childFamily: childStructural?.familyLabel ?? null,
      sameFamily: Boolean(parentStructural && childStructural && parentStructural.familyLabel === childStructural.familyLabel),
      parentCitationMode: parentStructural?.citationRegisterMode ?? null,
      childCitationMode: childStructural?.citationRegisterMode ?? null,
      citationDeltaPct: distance?.citationDeltaPct ?? null,
      grammarDeltaPct: distance?.grammarDeltaPct ?? null,
      structuralDistance01: distance?.structuralDistance01 ?? null,
      structuralRegisterSimilarity01: structuralSimilarity,
      parentDominantLayer: parentMicro?.dominant_layer || "none",
      childDominantLayer: childMicro?.dominant_layer || "none",
      sameDominantLayer: Boolean(parentMicro && childMicro && (parentMicro.dominant_layer || "none") === (childMicro.dominant_layer || "none")),
      layerJaccard: layers,
      microstructureSimilarity01: microSimilarity,
      band: microSimilarity === null ? "missing-microstructure-axis" : microstructureBand(microSimilarity, layers)
    },
    axisReading: reading,
    interpretation: interpretationForReading(reading),
    sourceKeys: {
      contentPairKey: unorderedPairKey(parent, child),
      conventionPairKey: unorderedPairKey(parent, child),
      bootstrapPairKey: pairKey(parent, child)
    }
  };
}

function validatePayload(payload) {
  const errors = [];
  if (payload.ownerRepo !== "csl-atlas") errors.push("ownerRepo must be csl-atlas");
  if (payload.comparisonRows.length !== EXPECTED_EDGE_IDS.length) {
    errors.push(`expected ${EXPECTED_EDGE_IDS.length} comparison rows, got ${payload.comparisonRows.length}`);
  }
  const ids = payload.comparisonRows.map(row => row.rowId);
  if (ids.join("|") !== EXPECTED_EDGE_IDS.join("|")) {
    errors.push(`comparison row order changed: ${ids.join(", ")}`);
  }
  for (const row of payload.comparisonRows) {
    if (row.contentAxis.parentInChild === null) errors.push(`${row.rowId}: missing content axis`);
    if (row.conventionAxis.conventionSimilarity === null) errors.push(`${row.rowId}: missing convention axis`);
    if (row.microstructureAxis.microstructureSimilarity01 === null) errors.push(`${row.rowId}: missing microstructure axis`);
    for (const [label, value] of [
      ["content parentInChild", row.contentAxis.parentInChild],
      ["content jaccard", row.contentAxis.jaccard],
      ["convention similarity", row.conventionAxis.conventionSimilarity],
      ["microstructure similarity", row.microstructureAxis.microstructureSimilarity01]
    ]) {
      if (value !== null && (value < 0 || value > 1)) errors.push(`${row.rowId}: ${label} out of range`);
    }
    if (!row.axisReading) errors.push(`${row.rowId}: missing axis reading`);
    if (!row.interpretation) errors.push(`${row.rowId}: missing interpretation`);
  }
  for (const focusId of FOCUS_EDGE_IDS) {
    if (!payload.focusRows.some(row => row.rowId === focusId)) errors.push(`${focusId}: missing focus row`);
  }
  if (errors.length) {
    const error = new Error(`Three-axis comparison build failed with ${errors.length} error(s):\n${errors.map(errorLine => `  - ${errorLine}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

export function buildPayload({ bootstrapRows, jaccardRows, conventionRows, structural, microstructure }, generatedAt = new Date().toISOString()) {
  const indexes = {
    jaccard: indexJaccard(jaccardRows),
    convention: indexConvention(conventionRows),
    structural: indexStructural(structural.rows || []),
    microstructure: indexMicrostructure(microstructure)
  };
  const comparisonRows = bootstrapRows.map(row => buildComparisonRow(row, indexes));
  const focusRows = FOCUS_EDGE_IDS.map(rowId => comparisonRows.find(row => row.rowId === rowId)).filter(Boolean);
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "three-axis-comparison-packet",
    claim: "THREE-AXES: content, convention, and microstructure inheritance must be compared as separate atlas evidence axes.",
    evidenceLabel: "derived",
    reviewStatus: "machine-reviewed",
    ownerRepo: "csl-atlas",
    generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: [
      "src/data/lexicographic-structure/L0/bootstrap_support.csv",
      "src/data/lexicographic-structure/sanhw1_jaccard.csv",
      "src/data/lexicographic-structure/L0/content_convention_scatter.csv",
      "src/data/dicts/structural-register.json",
      "data/lexico/microstructure_fingerprint.json",
      "scripts/build-three-axis-comparison.mjs"
    ],
    sourceGeneratedAt: {
      structuralRegister: structural.generatedAt ?? null
    },
    counts: {
      comparisonRows: comparisonRows.length,
      focusRows: focusRows.length,
      byAxisReading: countBy(comparisonRows, row => row.axisReading),
      byContentBand: countBy(comparisonRows, row => row.contentAxis.band),
      byConventionBand: countBy(comparisonRows, row => row.conventionAxis.band),
      byMicrostructureBand: countBy(comparisonRows, row => row.microstructureAxis.band),
      highContentLowConventionRows: comparisonRows.filter(row =>
        row.contentAxis.band === "high-content-overlap" && row.conventionAxis.band === "low-convention-overlap"
      ).length
    },
    axisDefinitions: [
      "Content axis: directed sanhw1 parent-in-child headword containment, with pairwise Jaccard retained as a size-aware caveat signal.",
      "Convention axis: L0 convention-fingerprint similarity and bootstrap support over known dictionary edges.",
      "Microstructure axis: H6 citation/grammar register distance plus M1-M5 layer overlap from the microstructure fingerprint.",
      "Axis readings are machine interpretation prompts, not human-reviewed lineage decisions."
    ],
    comparisonRows,
    focusRows,
    limitations: [
      "Raw headword containment is size-confounded; use it as content presence, not proof of content copying.",
      "Convention similarity measures documented house style, not lexical content.",
      "Microstructure similarity can reflect genre, source format, or detector coverage rather than descent.",
      "Rows remain review prompts; the packet records no human decisions and promotes no public claim."
    ],
    boundary: [
      "Atlas dictionary evidence only.",
      "No R2 parser behavior, public page, source-anchor generation, H5 review row, backend/runtime LLM, DCS/corpus, standards, or GitHub-process work is changed.",
      "DCS/corpus frequency and external maker decisions remain outside this artifact."
    ]
  };
  validatePayload(payload);
  return payload;
}

function markdownCell(value) {
  return String(value ?? "").replace(/\\/g, "\\\\").replace(/\|/g, "\\|");
}

function rowEdge(row) {
  return `${row.parent} -> ${row.child}`;
}

function axisSummary(row) {
  return [
    `content ${row.contentAxis.parentInChild}`,
    `convention ${row.conventionAxis.conventionSimilarity}`,
    `micro ${row.microstructureAxis.microstructureSimilarity01}`
  ].join("; ");
}

function comparisonTable(rows) {
  return [
    "| Edge | Content axis | Convention axis | Microstructure axis | Reading |",
    "|---|---:|---:|---:|---|",
    ...rows.map(row => [
      `\`${rowEdge(row)}\``,
      row.contentAxis.parentInChild,
      row.conventionAxis.conventionSimilarity,
      row.microstructureAxis.microstructureSimilarity01,
      `\`${markdownCell(row.axisReading)}\``
    ].join(" | ")).map(line => `| ${line} |`),
    ""
  ].join("\n");
}

function focusTable(rows) {
  return [
    "| Edge | Axis summary | Interpretation |",
    "|---|---|---|",
    ...rows.map(row => `| \`${rowEdge(row)}\` | ${markdownCell(axisSummary(row))} | ${markdownCell(row.interpretation)} |`),
    ""
  ].join("\n");
}

export function buildMarkdown(payload) {
  const lines = [
    "# Three-Axis Comparison Packet",
    "",
    "Date: 2026-06-07",
    "",
    "Status: generated machine-reviewed comparison packet; no human decisions or public claims are promoted.",
    "",
    "## Trust Block",
    "",
    `- Claim: ${payload.claim}`,
    `- Evidence label: \`${payload.evidenceLabel}\`.`,
    `- Review status: \`${payload.reviewStatus}\`.`,
    `- Generated by: \`${payload.generatedBy}\`.`,
    `- Source files: ${payload.sourceFiles.map(file => `\`${file}\``).join(", ")}.`,
    `- Counts: ${payload.counts.comparisonRows} known-edge rows; ${payload.counts.highContentLowConventionRows} high-content / low-convention rows.`,
    "- Boundary note: atlas dictionary evidence only; corpus/DCS, standards, public-page, parser, and external maker work are out of scope.",
    "",
    "## Axis Definitions",
    "",
    ...payload.axisDefinitions.map(item => `- ${item}`),
    "",
    "## Known-Edge Comparison",
    "",
    comparisonTable(payload.comparisonRows),
    "## Focus Rows",
    "",
    focusTable(payload.focusRows),
    "## Limitations",
    "",
    ...payload.limitations.map(item => `- ${item}`),
    "",
    "## Boundary",
    "",
    ...payload.boundary.map(item => `- ${item}`),
    ""
  ];
  return `${lines.join("\n")}\n`;
}

function main() {
  try {
    const payload = buildPayload({
      bootstrapRows: parseCsv(fs.readFileSync(BOOTSTRAP_PATH, "utf8")),
      jaccardRows: parseCsv(fs.readFileSync(JACCARD_PATH, "utf8")),
      conventionRows: parseCsv(fs.readFileSync(CONVENTION_SCATTER_PATH, "utf8")),
      structural: JSON.parse(fs.readFileSync(STRUCTURAL_PATH, "utf8")),
      microstructure: JSON.parse(fs.readFileSync(MICROSTRUCTURE_PATH, "utf8"))
    });
    fs.mkdirSync(path.dirname(JSON_OUT), { recursive: true });
    fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
    fs.writeFileSync(MARKDOWN_OUT, buildMarkdown(payload));
    console.log(`Wrote ${payload.counts.comparisonRows} three-axis comparison rows to:`);
    console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
    console.log(`- ${path.relative(process.cwd(), MARKDOWN_OUT)}`);
    console.log(`Counts: ${JSON.stringify(payload.counts)}`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
