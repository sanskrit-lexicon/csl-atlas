// Build the M6 cross-reference hub review artifact.
//
// The xref lineage chart measures pair overlap. This companion artifact turns
// top targets and the MW/PWG shared-core sample into review prompts with stable
// labels, without changing the canonical review-report schema.
//
// Usage: npm run build-xref-hub-review

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const SCHEMA_VERSION = "1.0.0";
const BY_DICT_PATH = path.resolve(process.cwd(), "data", "lexico", "xref_by_dict.json");
const SHARED_EDGES_PATH = path.resolve(process.cwd(), "data", "lexico", "xref_shared_edges.csv");
const CHART_PATH = path.resolve(process.cwd(), "src", "data", "dicts", "xref-lineage.json");
const OUT = path.resolve(process.cwd(), "data", "lexico", "xref_hub_review.json");
const TOP_TARGET_LIMIT = 25;
const SHARED_CORE_LIMIT = 40;

const LABELS = {
  ap: "AP",
  ap90: "AP90",
  cae: "CAE",
  mw: "MW",
  pwg: "PWG"
};

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

function label(code) {
  return LABELS[code] ?? code.toUpperCase();
}

function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) {
    const key = keyFn(row);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

export function classifyHubTarget(target) {
  const value = String(target || "");
  if (!value) return "normalization-risk";
  if (/[\u02da\u00b0-]$/.test(value) || /\/-$/.test(value)) return "prefix-convention";
  if (/\s/.test(value) || /[;:]/.test(value) || value.length > 28) return "normalization-risk";
  if (/^[a-zA-Z][a-zA-Z~/'^.]*$/.test(value)) return "lexical-target";
  return "normalization-risk";
}

function interpretationForHubClass(hubClass) {
  if (hubClass === "prefix-convention") return "Likely compound or prefix reference convention; do not read as rare lexical inheritance without review.";
  if (hubClass === "lexical-target") return "Potential lexical target; useful for shared-core or edition-continuity review.";
  return "Target normalization may create or hide an edge; inspect raw source before using as evidence.";
}

function reviewLabelForPair(pair) {
  if (pair.reading === "positive-control") return "edition-continuity";
  if (pair.reading === "headline-shared-core") return "lexical-shared-core";
  if (pair.reading === "too-few-shared-sources" || pair.sharedSources <= 2) return "too-sparse";
  return "normalization-risk";
}

function buildHubProfiles(byDict) {
  return Object.entries(byDict.dicts || {})
    .filter(([, stats]) => stats.xref_edges > 0)
    .map(([code, stats]) => {
      const topTargets = Object.entries(stats.top_referenced_targets || {})
        .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
        .slice(0, TOP_TARGET_LIMIT)
        .map(([target, count]) => {
          const hubClass = classifyHubTarget(target);
          return {
            target,
            count,
            hubClass,
            interpretation: interpretationForHubClass(hubClass)
          };
        });
      return {
        code,
        label: label(code),
        entriesScanned: stats.entries_scanned,
        entriesWithXref: stats.entries_with_xref,
        xrefEdges: stats.xref_edges,
        distinctTargets: stats.distinct_targets,
        cfQuotes: stats.cf_quotes || 0,
        kindCounts: stats.by_kind || {},
        topTargets,
        hubClassCounts: countBy(topTargets, row => row.hubClass)
      };
    })
    .sort((a, b) => b.xrefEdges - a.xrefEdges || a.label.localeCompare(b.label));
}

function buildPairReview(pairs) {
  return pairs.map(pair => ({
    pair: pair.pair,
    label: pair.label,
    reading: pair.reading,
    sharedSources: pair.sharedSources,
    overlappingEdges: pair.overlappingEdges,
    jaccardOnSharedSources: pair.jaccardOnSharedSources,
    aInheritanceRate: pair.aInheritanceRate,
    bInheritanceRate: pair.bInheritanceRate,
    reviewLabel: reviewLabelForPair(pair),
    interpretation: pair.reading === "headline-shared-core"
      ? "Review shared lexical targets separately from prefix or normalization artifacts."
      : pair.reading === "positive-control"
        ? "Use as edition-continuity calibration."
        : pair.sharedSources <= 2
          ? "Too sparse for lineage interpretation."
          : "Compare cautiously; overlap can reflect target normalization or convention."
  }));
}

function buildSharedCoreSample(sharedEdges) {
  return sharedEdges.slice(0, SHARED_CORE_LIMIT).map((row, index) => {
    const targetClass = classifyHubTarget(row.target);
    return {
      sampleId: `mw-pwg-shared:${String(index + 1).padStart(2, "0")}`,
      sourceLemma: row.src,
      target: row.target,
      hubClass: targetClass,
      reviewLabel: targetClass === "prefix-convention" ? "prefix-convention" : "lexical-shared-core",
      interpretation: targetClass === "prefix-convention"
        ? "Shared edge may reflect prefix/compound convention."
        : "Shared source-target edge is a candidate lexical shared-core item."
    };
  });
}

function validate(payload) {
  const errors = [];
  if (payload.ownerRepo !== "csl-atlas") errors.push("ownerRepo must be csl-atlas");
  if (!payload.hubProfiles.length) errors.push("no hub profiles");
  if (payload.sharedCoreSample.length !== Math.min(SHARED_CORE_LIMIT, payload.counts.sourceSharedEdges)) {
    errors.push("shared core sample count mismatch");
  }
  for (const profile of payload.hubProfiles) {
    if (!profile.topTargets.length) errors.push(`${profile.code}: no top targets`);
    for (const row of profile.topTargets) {
      if (!row.hubClass) errors.push(`${profile.code}/${row.target}: missing hub class`);
    }
  }
  if (errors.length) {
    console.error(`Xref hub review build failed with ${errors.length} error(s):`);
    for (const error of errors.slice(0, 25)) console.error(`  - ${error}`);
    process.exit(1);
  }
}

export function buildPayload(byDict, chart, sharedEdges) {
  const hubProfiles = buildHubProfiles(byDict);
  const pairReview = buildPairReview(chart.pairs || []);
  const sharedCoreSample = buildSharedCoreSample(sharedEdges);
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "xref-hub-review-artifact",
    claim: "M6 xref hubs need separate review labels for prefix conventions, lexical shared cores, sparse pairs, and edition continuity.",
    evidenceLabel: "derived",
    reviewStatus: "machine-reviewed",
    ownerRepo: "csl-atlas",
    generatedBy: "npm run build-xref-hub-review",
    sourceGeneratedAt: chart.generatedAt,
    sourceFiles: [
      "data/lexico/xref_by_dict.json",
      "data/lexico/xref_shared_edges.csv",
      "src/data/dicts/xref-lineage.json",
      "scripts/lexico/m3_xrefs.py",
      "scripts/lexico/m6_xref_lineage.py",
      "scripts/build-xref-lineage.mjs",
      "scripts/build-xref-hub-review.mjs"
    ],
    counts: {
      dictionaryProfiles: hubProfiles.length,
      pairReviewRows: pairReview.length,
      sourceSharedEdges: sharedEdges.length,
      sharedCoreSample: sharedCoreSample.length,
      topTargetLimit: TOP_TARGET_LIMIT
    },
    method: [
      "Classify top referenced targets per dictionary as prefix-convention, lexical-target, or normalization-risk.",
      "Carry xref-lineage pair readings into review labels: edition-continuity, lexical-shared-core, too-sparse, or normalization-risk.",
      "Emit a deterministic 40-edge MW/PWG shared-core sample for scholar review.",
      "Treat labels as review prompts, not automatic lineage claims."
    ],
    hubProfiles,
    pairReview,
    sharedCoreSample,
    limitations: [
      "Top target counts are normalized xref targets, not full citation or sense evidence.",
      "Prefix/convention hubs can dominate counts and must not be treated like rare lexical targets.",
      "The MW/PWG sample is deterministic and source-facing, but still machine-labeled.",
      "Sparse pair rows remain visible but should not drive lineage interpretation."
    ],
    boundary: [
      "This artifact uses dictionary-internal cross-reference evidence only.",
      "No DCS, corpus, TEI/OntoLex, FrAC, GitHub, or organization-process evidence is used."
    ]
  };
  validate(payload);
  return payload;
}

function main() {
  const byDict = JSON.parse(fs.readFileSync(BY_DICT_PATH, "utf8"));
  const chart = JSON.parse(fs.readFileSync(CHART_PATH, "utf8"));
  const sharedEdges = parseCsv(fs.readFileSync(SHARED_EDGES_PATH, "utf8"));
  const payload = buildPayload(byDict, chart, sharedEdges);
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote ${path.relative(process.cwd(), OUT)} (${payload.counts.dictionaryProfiles} hub profiles).`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
